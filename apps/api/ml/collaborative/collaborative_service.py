from pathlib import Path
import sys
from typing import Optional, Dict, Any, List, Tuple, Union
import pickle

import numpy as np
import pandas as pd
from scipy.sparse import load_npz, csr_matrix

# Add the parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# pyrefly: ignore [missing-import]
from collaborative_recommender import CollaborativeRecommender

# Central path resolution — see apps/api/ml/paths.py.
# BASE_DIR was previously parents[1] (= apps/api/ml), so the artifact path
# gained a spurious "apps/api/ml" segment and model loading failed with a
# FileNotFoundError for als_model.pkl.
from paths import ARTIFACT_DIR, PROCESSED_DATA_DIR  # noqa: E402

DATA_DIR = PROCESSED_DATA_DIR


class CollaborativeService:
    """
    Production service for collaborative filtering recommendations.
    """

    def __init__(self):
        """
        Initialize the collaborative service by loading all artifacts.
        """
        print("=" * 60)
        print("LOADING COLLABORATIVE MODEL")
        print("=" * 60)

        self.model = pickle.load(open(ARTIFACT_DIR / "als_model.pkl", "rb"))

        self.user_encoder = pickle.load(open(ARTIFACT_DIR / "user_encoder.pkl", "rb"))

        self.book_encoder = pickle.load(open(ARTIFACT_DIR / "book_encoder.pkl", "rb"))

        self.interaction_matrix = load_npz(ARTIFACT_DIR / "interaction_matrix.npz")

        self.metadata = pickle.load(
            open(ARTIFACT_DIR / "collaborative_metadata.pkl", "rb")
        )

        self.books = pd.read_parquet(
            DATA_DIR / "integrated" / "master_books_deduplicated.parquet"
        )

        # Cache train ratings for user history
        train_path = ARTIFACT_DIR / "train_ratings.parquet"
        self.train_ratings = (
            pd.read_parquet(train_path) if train_path.exists() else pd.DataFrame()
        )

        # Add these attributes for compatibility with hybrid recommender
        self._is_loaded = True
        self.is_fitted = True
        self.popularity_df = None

        print(f"✅ Users: {len(self.user_encoder.classes_):,}")
        print(f"✅ Books: {len(self.book_encoder.classes_):,}")
        print("✅ CollaborativeService initialized")

    def recommend_for_user(
        self,
        user_id: Union[str, int],
        top_k: int = 10,
        filter_liked: bool = True,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Generate recommendations for a user.

        Parameters:
        -----------
        user_id : str or int
            User ID to generate recommendations for
        top_k : int
            Number of recommendations to return
        filter_liked : bool
            Whether to filter already liked items
        **kwargs : Additional arguments

        Returns:
        --------
        pd.DataFrame: Recommendations with scores and metadata
        """
        if user_id not in self.user_encoder.classes_:
            print(f"User {user_id} not found")
            return pd.DataFrame()

        user_idx = self.user_encoder.transform([user_id])[0]

        # Extract the user's single row (1 x n_items)
        user_row = self.interaction_matrix[user_idx].tocsr()

        # Ensure CSR format and single row
        if not isinstance(user_row, csr_matrix):
            user_row = csr_matrix(user_row)

        # userid must be 0 because the matrix has only one row
        ids, scores = self.model.recommend(
            userid=0,
            user_items=user_row,
            N=top_k * 2,
            filter_already_liked_items=filter_liked,
        )

        isbn_list = self.book_encoder.inverse_transform(ids)

        recommendations = self.books[self.books["isbn"].isin(isbn_list)].copy()

        score_map = {isbn: float(score) for isbn, score in zip(isbn_list, scores)}

        recommendations["score"] = recommendations["isbn"].map(score_map)

        recommendations = recommendations.sort_values("score", ascending=False)

        # Add rank
        recommendations.insert(0, "rank", range(1, len(recommendations) + 1))

        return recommendations

    def get_user_history(
        self, user_id: Union[str, int], top_k: int = 20
    ) -> pd.DataFrame:
        """
        Get a user's rating history from the training data.
        """
        if self.train_ratings.empty:
            return pd.DataFrame()

        history = self.train_ratings[self.train_ratings["user_id"] == user_id].copy()

        if len(history) == 0:
            return pd.DataFrame()

        history = history.sort_values("book_rating", ascending=False)

        # Merge with book metadata
        history = history.merge(
            self.books[["isbn", "title", "authors", "publisher"]], on="isbn", how="left"
        )

        return history.head(top_k)

    def similar_books(self, isbn: str, top_k: int = 10) -> pd.DataFrame:
        """
        Find books similar to a given ISBN.

        Parameters:
        -----------
        isbn : str
            ISBN to find similar books for
        top_k : int
            Number of similar books to return

        Returns:
        --------
        pd.DataFrame: Similar books with scores and metadata
        """
        if isbn not in self.book_encoder.classes_:
            print(f"Book not found: {isbn}")
            return pd.DataFrame()

        item_id = self.book_encoder.transform([isbn])[0]

        ids, scores = self.model.similar_items(item_id, N=top_k + 1)

        # Remove the input book itself
        ids = ids[1:]
        scores = scores[1:]

        similar_isbns = self.book_encoder.inverse_transform(ids)

        books = self.books[self.books["isbn"].isin(similar_isbns)].copy()

        score_map = {isbn: float(score) for isbn, score in zip(similar_isbns, scores)}

        books["score"] = books["isbn"].map(score_map)

        # Add rank
        books.insert(0, "rank", range(1, len(books) + 1))

        return books.sort_values("score", ascending=False)

    def similar_users(
        self, user_id: Union[str, int], top_k: int = 10
    ) -> List[Tuple[Union[str, int], float]]:
        """
        Find users similar to a given user.

        Parameters:
        -----------
        user_id : str or int
            User ID to find similar users for
        top_k : int
            Number of similar users to return

        Returns:
        --------
        List[Tuple[user_id, score]]: List of similar users with scores
        """
        if user_id not in self.user_encoder.classes_:
            print(f"User {user_id} not found")
            return []

        user_idx = self.user_encoder.transform([user_id])[0]

        ids, scores = self.model.similar_users(user_idx, N=top_k + 1)

        # Remove the input user
        ids = ids[1:]
        scores = scores[1:]

        user_ids = self.user_encoder.inverse_transform(ids)

        return list(zip(user_ids, scores))

    def explain_recommendation(
        self, user_id: Union[str, int], isbn: str
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate and explain the score for a specific user-book pair.

        Parameters:
        -----------
        user_id : str or int
            User ID
        isbn : str
            Book ISBN

        Returns:
        --------
        dict or None: Explanation with score and details
        """
        if user_id not in self.user_encoder.classes_:
            print(f"User {user_id} not found")
            return None

        if isbn not in self.book_encoder.classes_:
            print(f"ISBN {isbn} not found")
            return None

        user_idx = self.user_encoder.transform([user_id])[0]

        item_idx = self.book_encoder.transform([isbn])[0]

        score = np.dot(
            self.model.user_factors[user_idx], self.model.item_factors[item_idx]
        )

        return {"user_id": user_id, "isbn": isbn, "score": float(score)}

    def get_stats(self) -> Dict[str, Any]:
        """
        Get service statistics.

        Returns:
        --------
        dict: Statistics dictionary
        """
        return {
            "users": len(self.user_encoder.classes_),
            "books": len(self.book_encoder.classes_),
            "interactions": self.interaction_matrix.nnz,
            "matrix_shape": self.interaction_matrix.shape,
            "factors": self.metadata.get("factors", "Unknown"),
            "iterations": self.metadata.get("iterations", "Unknown"),
            "is_loaded": getattr(self, "_is_loaded", True),
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the service.

        Returns:
        --------
        dict: Health status information
        """
        return {
            "status": "healthy",
            "users": len(self.user_encoder.classes_),
            "books": len(self.book_encoder.classes_),
            "is_loaded": getattr(self, "_is_loaded", True),
        }

    def refresh(self) -> bool:
        """
        Refresh the service by reloading all artifacts.

        Returns:
        --------
        bool: True if successful
        """
        try:
            # Reload all artifacts
            self.model = pickle.load(open(ARTIFACT_DIR / "als_model.pkl", "rb"))
            self.user_encoder = pickle.load(
                open(ARTIFACT_DIR / "user_encoder.pkl", "rb")
            )
            self.book_encoder = pickle.load(
                open(ARTIFACT_DIR / "book_encoder.pkl", "rb")
            )
            self.interaction_matrix = load_npz(ARTIFACT_DIR / "interaction_matrix.npz")
            self.metadata = pickle.load(
                open(ARTIFACT_DIR / "collaborative_metadata.pkl", "rb")
            )
            self.books = pd.read_parquet(
                DATA_DIR / "integrated" / "master_books_deduplicated.parquet"
            )
            self._is_loaded = True
            print("✅ CollaborativeService refreshed")
            return True
        except Exception as e:
            print(f"❌ Error refreshing service: {e}")
            return False


# =====================================================
# SINGLETON INSTANCE
# =====================================================

_collaborative_service = None


def get_collaborative_service() -> CollaborativeService:
    """
    Get or create the singleton CollaborativeService instance.

    Returns:
    --------
    CollaborativeService: The singleton instance.
    """
    global _collaborative_service
    if _collaborative_service is None:
        _collaborative_service = CollaborativeService()
    return _collaborative_service


# =====================================================
# CONVENIENCE FUNCTIONS
# =====================================================


def get_user_recommendations(
    user_id: Union[str, int], top_k: int = 10, **kwargs
) -> pd.DataFrame:
    """
    Quick function to get user recommendations.

    Parameters:
    -----------
    user_id : str or int
        User ID
    top_k : int
        Number of recommendations
    **kwargs : Additional arguments passed to recommend_for_user

    Returns:
    --------
    pd.DataFrame: Recommendations.
    """
    service = get_collaborative_service()
    return service.recommend_for_user(user_id, top_k, **kwargs)


def get_similar_books(isbn: str, top_k: int = 10, **kwargs) -> pd.DataFrame:
    """
    Quick function to get similar books.

    Parameters:
    -----------
    isbn : str
        ISBN to find similar books for
    top_k : int
        Number of similar books
    **kwargs : Additional arguments passed to similar_books

    Returns:
    --------
    pd.DataFrame: Similar books.
    """
    service = get_collaborative_service()
    return service.similar_books(isbn, top_k, **kwargs)
