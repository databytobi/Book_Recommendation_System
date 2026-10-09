from pathlib import Path
import pickle
import logging
from typing import Optional, Dict, Any, List, Tuple, Union
from datetime import datetime

import pandas as pd
import numpy as np
from scipy.sparse import load_npz, csr_matrix

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data" / "processed"
ARTIFACT_DIR = BASE_DIR / "apps" / "api" / "ml" / "artifacts"


class CollaborativeRecommender:
    """
    Collaborative filtering recommender using ALS (Alternating Least Squares).
    Provides user-based and item-based recommendations.
    """

    def __init__(self, artifact_dir: Optional[Path] = None, load_on_init: bool = True):
        """
        Initialize the collaborative recommender.
        
        Parameters:
        -----------
        artifact_dir : Path, optional
            Directory containing the artifacts. Defaults to ARTIFACT_DIR.
        load_on_init : bool
            Whether to load artifacts immediately on initialization.
        """
        self.artifact_dir = artifact_dir or ARTIFACT_DIR
        
        # Model components
        self.model = None
        self.user_encoder = None
        self.book_encoder = None
        self.matrix = None
        
        # Data
        self.books = None
        self.train_ratings = None
        self.metadata = None
        
        # Cache
        self._cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 3600  # 1 hour cache TTL
        
        # Statistics
        self._load_time = None
        self._is_loaded = False
        self._load_attempts = 0
        
        if load_on_init:
            self.load_artifacts()
        
        logger.info("CollaborativeRecommender initialized")

    # =====================================================
    # LOAD ARTIFACTS
    # =====================================================

    def load_artifacts(self, force_reload: bool = False) -> bool:
        """
        Load all artifacts from disk.
        
        Parameters:
        -----------
        force_reload : bool
            Whether to force reload even if already loaded.
        
        Returns:
        --------
        bool: True if successful, False otherwise.
        """
        if self._is_loaded and not force_reload:
            logger.info("Artifacts already loaded. Use force_reload=True to reload.")
            return True
        
        self._load_attempts += 1
        
        try:
            start_time = datetime.now()
            
            print("=" * 60)
            print("LOADING COLLABORATIVE ARTIFACTS")
            print("=" * 60)
            
            # Load model
            model_path = self.artifact_dir / "als_model.pkl"
            if not model_path.exists():
                raise FileNotFoundError(f"Model not found: {model_path}")
            
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
            print(f"✅ ALS model loaded: {model_path}")
            
            # Load user encoder
            user_encoder_path = self.artifact_dir / "user_encoder.pkl"
            if not user_encoder_path.exists():
                raise FileNotFoundError(f"User encoder not found: {user_encoder_path}")
            
            with open(user_encoder_path, "rb") as f:
                self.user_encoder = pickle.load(f)
            print(f"✅ User encoder loaded: {user_encoder_path}")
            
            # Load book encoder
            book_encoder_path = self.artifact_dir / "book_encoder.pkl"
            if not book_encoder_path.exists():
                raise FileNotFoundError(f"Book encoder not found: {book_encoder_path}")
            
            with open(book_encoder_path, "rb") as f:
                self.book_encoder = pickle.load(f)
            print(f"✅ Book encoder loaded: {book_encoder_path}")
            
            # Load interaction matrix
            matrix_path = self.artifact_dir / "interaction_matrix.npz"
            if not matrix_path.exists():
                raise FileNotFoundError(f"Interaction matrix not found: {matrix_path}")
            
            self.matrix = load_npz(matrix_path)
            print(f"✅ Interaction matrix loaded: {matrix_path}")
            
            # Load train ratings
            train_path = self.artifact_dir / "train_ratings.parquet"
            if not train_path.exists():
                raise FileNotFoundError(f"Train ratings not found: {train_path}")
            
            self.train_ratings = pd.read_parquet(train_path)
            print(f"✅ Train ratings loaded: {len(self.train_ratings):,}")
            
            # Load books
            books_path = DATA_DIR / "integrated" / "master_books_deduplicated.parquet"
            if not books_path.exists():
                books_path = DATA_DIR / "integrated" / "master_books.parquet"
            
            if not books_path.exists():
                raise FileNotFoundError(f"Books data not found: {books_path}")
            
            self.books = pd.read_parquet(books_path)
            print(f"✅ Books loaded: {len(self.books):,}")
            
            # Load metadata
            metadata_path = self.artifact_dir / "collaborative_metadata.pkl"
            if metadata_path.exists():
                with open(metadata_path, "rb") as f:
                    self.metadata = pickle.load(f)
                print(f"✅ Metadata loaded: {metadata_path}")
            
            # Mark as loaded
            self._is_loaded = True
            self._load_time = (datetime.now() - start_time).total_seconds()
            
            print("\n" + "=" * 60)
            print("SUMMARY")
            print("=" * 60)
            print(f"✅ Users: {len(self.user_encoder.classes_):,}")
            print(f"✅ Books: {len(self.book_encoder.classes_):,}")
            print(f"✅ Interactions: {len(self.train_ratings):,}")
            print(f"✅ Matrix shape: {self.matrix.shape}")
            print(f"✅ Load time: {self._load_time:.2f} seconds")
            
            return True
            
        except FileNotFoundError as e:
            logger.error(f"❌ File not found: {e}")
            print("\n💡 Please run the collaborative training first:")
            print("   python apps/api/ml/collaborative/train_collaborative.py")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error loading artifacts: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _ensure_loaded(self) -> bool:
        """Ensure artifacts are loaded before making predictions."""
        if not self._is_loaded:
            return self.load_artifacts()
        return True

    # =====================================================
    # CACHE
    # =====================================================

    def _get_from_cache(self, key: str) -> Optional[pd.DataFrame]:
        """Get cached results if valid."""
        if key in self._cache:
            if self._cache_timestamp is not None:
                age = (datetime.now() - self._cache_timestamp).total_seconds()
                if age < self._cache_ttl:
                    logger.debug(f"Cache hit for: {key}")
                    return self._cache[key]
                else:
                    del self._cache[key]
        return None

    def _cache_results(self, key: str, results: pd.DataFrame) -> None:
        """Cache results."""
        if len(self._cache) > 100:
            self._cache.clear()
        self._cache[key] = results
        self._cache_timestamp = datetime.now()

    def clear_cache(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        self._cache_timestamp = None
        logger.info("Cache cleared")

    # =====================================================
    # USER HISTORY
    # =====================================================

    def get_user_history(
        self,
        user_id: Union[str, int],
        top_k: int = 20,
        include_metadata: bool = True
    ) -> pd.DataFrame:
        """
        Get a user's rating history.
        
        Parameters:
        -----------
        user_id : str or int
            User ID to get history for.
        top_k : int
            Number of top-rated books to return.
        include_metadata : bool
            Whether to include book metadata.
        
        Returns:
        --------
        pd.DataFrame: User's rating history.
        """
        if not self._ensure_loaded():
            return pd.DataFrame()
        
        try:
            # Check cache
            cache_key = f"history_{user_id}_{top_k}"
            cached = self._get_from_cache(cache_key)
            if cached is not None:
                return cached
            
            history = self.train_ratings[
                self.train_ratings["user_id"] == user_id
            ].copy()
            
            if len(history) == 0:
                logger.warning(f"No history found for user: {user_id}")
                return pd.DataFrame()
            
            # Sort by rating
            history = history.sort_values(
                "book_rating",
                ascending=False
            )
            
            # Merge with book metadata
            if include_metadata and self.books is not None:
                history = history.merge(
                    self.books[['isbn', 'title', 'authors', 'publisher', 'publication_year']],
                    on="isbn",
                    how="left"
                )
            
            # Select columns
            columns = ['isbn', 'title', 'authors', 'book_rating']
            available_cols = [col for col in columns if col in history.columns]
            
            result = history.head(top_k)[available_cols]
            
            # Cache results
            self._cache_results(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user history: {e}")
            return pd.DataFrame()

    # =====================================================
    # USER RECOMMENDATIONS
    # =====================================================

    def recommend_for_user(
        self,
        user_id: Union[str, int],
        top_k: int = 10,
        filter_liked: bool = True,
        exclude_authors: Optional[List[str]] = None,
        min_score: float = 0.0,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Generate recommendations for a user.
        """
        if not self._ensure_loaded():
            return pd.DataFrame()
        
        try:
            # Check cache
            cache_key = f"user_{user_id}_{top_k}_{filter_liked}"
            if use_cache:
                cached = self._get_from_cache(cache_key)
                if cached is not None:
                    return cached
            
            # Check if user exists
            if user_id not in self.user_encoder.classes_:
                logger.warning(f"User {user_id} not found in training data")
                return pd.DataFrame()
            
            # Get user index
            user_idx = self.user_encoder.transform([user_id])[0]
            
            # The implicit library's recommend() expects user_items as a CSR matrix
            # with shape (1, n_items) when userid is a scalar — i.e., just the row
            # for this specific user.
            user_items = self.matrix.tocsr()
            user_row = user_items[user_idx]  # single row: shape (1, n_items)
            
            # Verify the matrix has the correct shape
            logger.info(f"Full matrix shape: {user_items.shape}")
            logger.info(f"User row shape: {user_row.shape}, User index: {user_idx}")
            
            # Get recommendations
            ids, scores = self.model.recommend(
                userid=0,  # index into user_row (which has only 1 row)
                user_items=user_row,
                N=top_k * 2,  # Get extra to allow filtering
                filter_already_liked_items=filter_liked
            )
            
            # Build results
            recommendations = []
            for item_idx, score in zip(ids, scores):
                if score < min_score:
                    continue
                
                isbn = self.book_encoder.inverse_transform([item_idx])[0]
                match = self.books[self.books["isbn"] == isbn]
                if len(match) == 0:
                    continue
                
                row = match.iloc[0]
                if exclude_authors and row.get("authors") in exclude_authors:
                    continue
                
                recommendations.append({
                    "isbn": isbn,
                    "title": row.get("title", "Unknown"),
                    "authors": row.get("authors", "Unknown"),
                    "publisher": row.get("publisher", "Unknown"),
                    "publication_year": row.get("publication_year", None),
                    "score": float(score)
                })
                
                if len(recommendations) >= top_k:
                    break
            
            result = pd.DataFrame(recommendations)
            
            # Cache results
            if use_cache:
                self._cache_results(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error recommending for user {user_id}: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    # =====================================================
    # SIMILAR BOOKS
    # =====================================================

    def similar_books(
        self,
        isbn: str,
        top_k: int = 10,
        exclude_self: bool = True,
        min_score: float = 0.0,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Find books similar to a given ISBN.
        
        Parameters:
        -----------
        isbn : str
            ISBN to find similar books for.
        top_k : int
            Number of similar books to return.
        exclude_self : bool
            Whether to exclude the input book from results.
        min_score : float
            Minimum similarity score threshold.
        use_cache : bool
            Whether to use cached results.
        
        Returns:
        --------
        pd.DataFrame: Similar books with scores.
        """
        if not self._ensure_loaded():
            return pd.DataFrame()
        
        try:
            # Check cache
            cache_key = f"similar_{isbn}_{top_k}"
            if use_cache:
                cached = self._get_from_cache(cache_key)
                if cached is not None:
                    return cached
            
            # Check if ISBN exists
            if isbn not in self.book_encoder.classes_:
                logger.warning(f"ISBN {isbn} not found in training data")
                return pd.DataFrame()
            
            # Get item index
            item_idx = self.book_encoder.transform([isbn])[0]
            
            # Get similar items
            ids, scores = self.model.similar_items(
                item_idx,
                N=top_k * 2  # Get extra to allow filtering
            )
            
            # Build results
            similar_books = []
            
            for idx, score in zip(ids, scores):
                # Skip self
                if exclude_self and idx == item_idx:
                    continue
                
                # Check score threshold
                if score < min_score:
                    continue
                
                # Get ISBN
                similar_isbn = self.book_encoder.inverse_transform([idx])[0]
                
                # Get book details
                match = self.books[self.books["isbn"] == similar_isbn]
                if len(match) == 0:
                    continue
                
                row = match.iloc[0]
                
                similar_books.append({
                    "isbn": similar_isbn,
                    "title": row.get("title", "Unknown"),
                    "authors": row.get("authors", "Unknown"),
                    "publisher": row.get("publisher", "Unknown"),
                    "publication_year": row.get("publication_year", None),
                    "similarity": float(score)
                })
                
                if len(similar_books) >= top_k:
                    break
            
            result = pd.DataFrame(similar_books)
            
            # Cache results
            if use_cache:
                self._cache_results(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error finding similar books for {isbn}: {e}")
            return pd.DataFrame()

    # =====================================================
    # BATCH RECOMMENDATIONS
    # =====================================================

    def recommend_for_users(
        self,
        user_ids: List[Union[str, int]],
        top_k: int = 10,
        **kwargs
    ) -> Dict[Union[str, int], pd.DataFrame]:
        """
        Generate recommendations for multiple users.
        
        Parameters:
        -----------
        user_ids : List[str or int]
            List of user IDs to generate recommendations for.
        top_k : int
            Number of recommendations per user.
        **kwargs : Additional arguments passed to recommend_for_user.
        
        Returns:
        --------
        dict: Dictionary mapping user_id to recommendations DataFrame.
        """
        if not self._ensure_loaded():
            return {}
        
        results = {}
        
        for user_id in user_ids:
            try:
                recs = self.recommend_for_user(user_id, top_k, **kwargs)
                if not recs.empty:
                    results[user_id] = recs
            except Exception as e:
                logger.error(f"Error recommending for user {user_id}: {e}")
                results[user_id] = pd.DataFrame()
        
        return results

    # =====================================================
    # MOST ACTIVE USERS
    # =====================================================

    def get_active_users(self, top_k: int = 20) -> pd.Series:
        """
        Get most active users by number of ratings.
        
        Parameters:
        -----------
        top_k : int
            Number of active users to return.
        
        Returns:
        --------
        pd.Series: Top active users with their rating counts.
        """
        if not self._ensure_loaded():
            return pd.Series()
        
        return (
            self.train_ratings
            .groupby("user_id")
            .size()
            .sort_values(ascending=False)
            .head(top_k)
        )

    # =====================================================
    # TOP BOOKS
    # =====================================================

    def get_top_books(
        self,
        top_k: int = 20,
        min_ratings: int = 5
    ) -> pd.DataFrame:
        """
        Get top books by number of ratings.
        
        Parameters:
        -----------
        top_k : int
            Number of top books to return.
        min_ratings : int
            Minimum number of ratings required.
        
        Returns:
        --------
        pd.DataFrame: Top books with their rating counts.
        """
        if not self._ensure_loaded():
            return pd.DataFrame()
        
        top_books = (
            self.train_ratings
            .groupby("isbn")
            .agg(
                rating_count=("book_rating", "count"),
                avg_rating=("book_rating", "mean")
            )
            .reset_index()
        )
        
        # Filter by minimum ratings
        top_books = top_books[top_books["rating_count"] >= min_ratings]
        
        # Sort and get top k
        top_books = top_books.sort_values("rating_count", ascending=False).head(top_k)
        
        # Merge with book metadata
        if self.books is not None:
            top_books = top_books.merge(
                self.books[['isbn', 'title', 'authors', 'publisher']],
                on="isbn",
                how="left"
            )
        
        return top_books

    # =====================================================
    # USER SIMILARITY
    # =====================================================

    def get_user_similarity(
        self,
        user_id1: Union[str, int],
        user_id2: Union[str, int]
    ) -> Optional[float]:
        """
        Calculate similarity between two users.
        
        Parameters:
        -----------
        user_id1 : str or int
            First user ID.
        user_id2 : str or int
            Second user ID.
        
        Returns:
        --------
        float or None: Similarity score.
        """
        if not self._ensure_loaded():
            return None
        
        try:
            if user_id1 not in self.user_encoder.classes_:
                logger.warning(f"User {user_id1} not found")
                return None
            
            if user_id2 not in self.user_encoder.classes_:
                logger.warning(f"User {user_id2} not found")
                return None
            
            idx1 = self.user_encoder.transform([user_id1])[0]
            idx2 = self.user_encoder.transform([user_id2])[0]
            
            # Get user factors
            user_factors1 = self.model.user_factors[idx1]
            user_factors2 = self.model.user_factors[idx2]
            
            # Calculate cosine similarity
            similarity = np.dot(user_factors1, user_factors2) / (
                np.linalg.norm(user_factors1) * np.linalg.norm(user_factors2)
            )
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating user similarity: {e}")
            return None

    # =====================================================
    # STATS
    # =====================================================

    def get_stats(self) -> Dict[str, Any]:
        """
        Get recommender statistics.
        
        Returns:
        --------
        dict: Statistics dictionary.
        """
        if not self._is_loaded:
            return {
                "status": "not_loaded",
                "is_loaded": False,
                "load_attempts": self._load_attempts
            }
        
        stats = {
            "status": "loaded",
            "is_loaded": True,
            "users": len(self.user_encoder.classes_),
            "books": len(self.book_encoder.classes_),
            "interactions": len(self.train_ratings),
            "load_time": self._load_time,
            "load_attempts": self._load_attempts,
            "cache_size": len(self._cache),
            "cache_ttl": self._cache_ttl,
        }
        
        # Add model info
        if self.metadata:
            stats["model"] = {
                "type": "ALS",
                "factors": self.metadata.get("factors", "Unknown"),
                "iterations": self.metadata.get("iterations", "Unknown"),
                "regularization": self.metadata.get("regularization", "Unknown")
            }
        elif self.model:
            stats["model"] = {
                "type": type(self.model).__name__,
                "factors": self.model.factors if hasattr(self.model, 'factors') else "Unknown"
            }
        
        # Add matrix statistics
        if self.matrix is not None:
            total_possible = self.matrix.shape[0] * self.matrix.shape[1]
            stats["matrix"] = {
                "shape": self.matrix.shape,
                "nnz": self.matrix.nnz,
                "sparsity": (1 - (self.matrix.nnz / total_possible)) * 100 if total_possible > 0 else 0
            }
        
        return stats

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the recommender.
        
        Returns:
        --------
        dict: Health status information.
        """
        if not self._is_loaded:
            return {
                "status": "unhealthy",
                "message": "Artifacts not loaded",
                "is_loaded": False
            }
        
        status = {
            "status": "healthy",
            "is_loaded": True,
            "components": {
                "model": self.model is not None,
                "user_encoder": self.user_encoder is not None,
                "book_encoder": self.book_encoder is not None,
                "matrix": self.matrix is not None,
                "books": self.books is not None,
                "train_ratings": self.train_ratings is not None
            }
        }
        
        # Check if all components are loaded
        all_loaded = all(status["components"].values())
        if not all_loaded:
            status["status"] = "degraded"
            status["missing_components"] = [
                key for key, value in status["components"].items() if not value
            ]
        
        return status

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(self) -> bool:
        """
        Refresh the recommender by reloading artifacts.
        
        Returns:
        --------
        bool: True if successful.
        """
        self.clear_cache()
        return self.load_artifacts(force_reload=True)

    # =====================================================
    # USER PRESENCE CHECK
    # =====================================================

    def user_exists(self, user_id: Union[str, int]) -> bool:
        """Check if a user exists in the training data."""
        if not self._is_loaded:
            return False
        try:
            return user_id in self.user_encoder.classes_
        except Exception:
            return False

    def book_exists(self, isbn: str) -> bool:
        """Check if a book exists in the training data."""
        if not self._is_loaded:
            return False
        try:
            return isbn in self.book_encoder.classes_
        except Exception:
            return False

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self) -> str:
        status = "loaded" if self._is_loaded else "not loaded"
        users = len(self.user_encoder.classes_) if self.user_encoder else 0
        books = len(self.book_encoder.classes_) if self.book_encoder else 0
        return f"CollaborativeRecommender(status={status}, users={users:,}, books={books:,})"


# =====================================================
# SINGLETON INSTANCE
# =====================================================

_collaborative_service = None


def get_collaborative_service() -> CollaborativeRecommender:
    """
    Get or create the singleton CollaborativeRecommender instance.
    
    Returns:
    --------
    CollaborativeRecommender: The singleton instance.
    """
    global _collaborative_service
    if _collaborative_service is None:
        _collaborative_service = CollaborativeRecommender()
    return _collaborative_service


# =====================================================
# CONVENIENCE FUNCTIONS
# =====================================================

def get_user_recommendations(
    user_id: Union[str, int],
    top_k: int = 10,
    **kwargs
) -> pd.DataFrame:
    """
    Quick function to get user recommendations.
    
    Parameters:
    -----------
    user_id : str or int
        User ID to generate recommendations for.
    top_k : int
        Number of recommendations to return.
    **kwargs : Additional arguments passed to recommend_for_user.
    
    Returns:
    --------
    pd.DataFrame: Recommendations.
    """
    service = get_collaborative_service()
    return service.recommend_for_user(user_id, top_k, **kwargs)


def get_similar_books(
    isbn: str,
    top_k: int = 10,
    **kwargs
) -> pd.DataFrame:
    """
    Quick function to get similar books.
    
    Parameters:
    -----------
    isbn : str
        ISBN to find similar books for.
    top_k : int
        Number of similar books to return.
    **kwargs : Additional arguments passed to similar_books.
    
    Returns:
    --------
    pd.DataFrame: Similar books.
    """
    service = get_collaborative_service()
    return service.similar_books(isbn, top_k, **kwargs)