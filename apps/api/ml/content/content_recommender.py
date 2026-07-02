from pathlib import Path
import faiss
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Union
import pickle


class ContentRecommender:
    """
    Content-based recommender using FAISS embeddings.
    Provides similar book recommendations based on semantic similarity.
    """

    def __init__(self, books: pd.DataFrame, index: faiss.Index, metadata: Optional[Dict] = None):
        """
        Initialize the content recommender.
        
        Parameters:
        -----------
        books : pd.DataFrame
            DataFrame containing book metadata with 'isbn' column
        index : faiss.Index
            FAISS index containing book embeddings
        metadata : dict, optional
            Additional metadata about the embeddings
        """
        self.books = books.reset_index(drop=True)
        self.index = index
        self.metadata = metadata or {}
        
        # Create ISBN to index mapping
        self.isbn_to_idx = {
            isbn: idx
            for idx, isbn in enumerate(self.books["isbn"])
        }
        
        # Cache for frequently accessed data
        self._cache = {}
        
        # Validate index size matches books
        if len(self.books) != index.ntotal:
            print(f"⚠️ Warning: Books count ({len(self.books)}) doesn't match index size ({index.ntotal})")
    
    @classmethod
    def load(cls, artifact_dir: Union[str, Path]):
        """
        Load a saved ContentRecommender from artifacts directory.
        
        Parameters:
        -----------
        artifact_dir : str or Path
            Path to the artifacts directory containing saved files
        
        Returns:
        --------
        ContentRecommender: Loaded recommender instance
        """
        artifact_dir = Path(artifact_dir)
        
        # Load books
        books_path = artifact_dir / "semantic_books.parquet"
        if not books_path.exists():
            raise FileNotFoundError(f"Books file not found: {books_path}")
        books = pd.read_parquet(books_path)
        
        # Load index
        index_path = artifact_dir / "books_faiss.index"
        if not index_path.exists():
            raise FileNotFoundError(f"FAISS index not found: {index_path}")
        index = faiss.read_index(str(index_path))
        
        # Load metadata if available
        metadata_path = artifact_dir / "embedding_metadata.pkl"
        metadata = None
        if metadata_path.exists():
            with open(metadata_path, "rb") as f:
                metadata = pickle.load(f)
        
        return cls(books, index, metadata)
    
    def save(self, artifact_dir: Union[str, Path]):
        """
        Save the recommender to disk.
        
        Parameters:
        -----------
        artifact_dir : str or Path
            Directory to save the artifacts
        """
        artifact_dir = Path(artifact_dir)
        artifact_dir.mkdir(parents=True, exist_ok=True)
        
        # Save books
        books_path = artifact_dir / "semantic_books.parquet"
        self.books.to_parquet(books_path, index=False)
        
        # Save index
        index_path = artifact_dir / "books_faiss.index"
        faiss.write_index(self.index, str(index_path))
        
        # Save metadata
        if self.metadata:
            metadata_path = artifact_dir / "embedding_metadata.pkl"
            with open(metadata_path, "wb") as f:
                pickle.dump(self.metadata, f)
        
        print(f"✅ ContentRecommender saved to: {artifact_dir}")
    
    def recommend_by_isbn(
        self,
        isbn: str,
        top_k: int = 10,
        exclude_same_author: bool = False,
        min_similarity: float = 0.0
    ) -> pd.DataFrame:
        """
        Recommend books similar to a given ISBN.
        
        Parameters:
        -----------
        isbn : str
            ISBN of the book to find similar books for
        top_k : int
            Number of recommendations to return
        exclude_same_author : bool
            If True, exclude books by the same author
        min_similarity : float
            Minimum similarity score threshold (0-1)
        
        Returns:
        --------
        pd.DataFrame: Top K similar books with similarity scores
        """
        if isbn not in self.isbn_to_idx:
            print(f"❌ ISBN not found: {isbn}")
            return pd.DataFrame()
        
        idx = self.isbn_to_idx[isbn]
        
        # Get the book's vector
        query_vector = self.index.reconstruct(idx).reshape(1, -1)
        
        # Search for similar books (get more to allow filtering)
        search_k = top_k * 2 + 1
        scores, indices = self.index.search(query_vector, search_k)
        
        # Create results DataFrame
        results = self.books.iloc[indices[0]].copy()
        results["similarity"] = scores[0]
        
        # Remove the query book itself
        results = results[results["isbn"] != isbn]
        
        # Filter by minimum similarity
        if min_similarity > 0:
            results = results[results["similarity"] >= min_similarity]
        
        # Exclude same author if requested
        if exclude_same_author:
            query_author = self.books.iloc[idx].get("authors", "")
            if query_author:
                results = results[results["authors"] != query_author]
        
        return results.head(top_k)
    
    def recommend_by_title(
        self,
        title: str,
        top_k: int = 10,
        fuzzy_match: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        Recommend books similar to a title.
        
        Parameters:
        -----------
        title : str
            Title to search for
        top_k : int
            Number of recommendations to return
        fuzzy_match : bool
            If True, use partial matching; if False, use exact match
        **kwargs : Additional arguments passed to recommend_by_isbn
        
        Returns:
        --------
        pd.DataFrame: Top K similar books
        """
        if fuzzy_match:
            matches = self.books[
                self.books["title"].str.contains(
                    title,
                    case=False,
                    na=False,
                    regex=False
                )
            ]
        else:
            matches = self.books[
                self.books["title"].str.lower() == title.lower()
            ]
        
        if len(matches) == 0:
            print(f"❌ No match found for title: '{title}'")
            return pd.DataFrame()
        
        # If multiple matches, use the first one
        matched_book = matches.iloc[0]
        print(f"✅ Matched: '{matched_book['title']}' by {matched_book.get('authors', 'Unknown')}")
        
        return self.recommend_by_isbn(
            matched_book["isbn"],
            top_k=top_k,
            **kwargs
        )
    
    def recommend_by_text(
        self,
        query_text: str,
        top_k: int = 10,
        model=None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Recommend books based on a text query using semantic search.
        
        Parameters:
        -----------
        query_text : str
            Text query to search for
        top_k : int
            Number of recommendations to return
        model : SentenceTransformer, optional
            Model to encode the query text. If None, uses pre-computed embeddings.
        **kwargs : Additional arguments passed to recommend_by_vector
        
        Returns:
        --------
        pd.DataFrame: Top K similar books
        """
        if model is None:
            # Try to load the model
            try:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            except ImportError:
                raise ImportError(
                    "SentenceTransformer not installed. "
                    "Install it with: pip install sentence-transformers"
                )
        
        # Generate embedding for the query
        from sklearn.preprocessing import normalize
        query_embedding = model.encode([query_text], convert_to_numpy=True)
        query_embedding = normalize(query_embedding, norm="l2").astype("float32")
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Create results
        results = self.books.iloc[indices[0]].copy()
        results["similarity"] = scores[0]
        
        return results
    
    def recommend_by_vector(
        self,
        vector: np.ndarray,
        top_k: int = 10,
        **kwargs
    ) -> pd.DataFrame:
        """
        Recommend books based on a query vector.
        
        Parameters:
        -----------
        vector : np.ndarray
            Query vector to search with
        top_k : int
            Number of recommendations to return
        **kwargs : Additional arguments passed to search
        
        Returns:
        --------
        pd.DataFrame: Top K similar books
        """
        if vector.shape[0] != self.index.d:
            raise ValueError(
                f"Vector dimension {vector.shape[0]} doesn't match "
                f"index dimension {self.index.d}"
            )
        
        # Reshape if needed
        if vector.ndim == 1:
            vector = vector.reshape(1, -1)
        
        # Search
        scores, indices = self.index.search(vector, top_k)
        
        # Create results
        results = self.books.iloc[indices[0]].copy()
        results["similarity"] = scores[0]
        
        return results
    
    def explain_book(
        self,
        isbn: str
    ) -> Optional[Dict[str, Any]]:
        """
        Return detailed metadata for a book.
        
        Parameters:
        -----------
        isbn : str
            ISBN of the book to explain
        
        Returns:
        --------
        dict or None: Book metadata dictionary
        """
        if isbn not in self.isbn_to_idx:
            print(f"❌ ISBN not found: {isbn}")
            return None
        
        idx = self.isbn_to_idx[isbn]
        book = self.books.iloc[idx]
        
        return {
            "isbn": str(book.get("isbn", "")),
            "title": str(book.get("title", "Unknown")),
            "authors": str(book.get("authors", "Unknown")),
            "publisher": str(book.get("publisher", "Unknown")),
            "publication_year": int(book.get("publication_year", 0)) if pd.notna(book.get("publication_year")) else None,
            "language": str(book.get("language_code", "Unknown")),
            "average_rating": float(book.get("average_rating", 0)) if pd.notna(book.get("average_rating")) else None,
            "ratings_count": int(book.get("ratings_count", 0)) if pd.notna(book.get("ratings_count")) else 0
        }
    
    def get_similarity(
        self,
        isbn1: str,
        isbn2: str
    ) -> Optional[float]:
        """
        Calculate similarity score between two books.
        
        Parameters:
        -----------
        isbn1 : str
            ISBN of first book
        isbn2 : str
            ISBN of second book
        
        Returns:
        --------
        float or None: Similarity score between 0 and 1
        """
        if isbn1 not in self.isbn_to_idx:
            print(f"❌ ISBN not found: {isbn1}")
            return None
        
        if isbn2 not in self.isbn_to_idx:
            print(f"❌ ISBN not found: {isbn2}")
            return None
        
        idx1 = self.isbn_to_idx[isbn1]
        idx2 = self.isbn_to_idx[isbn2]
        
        vec1 = self.index.reconstruct(idx1)
        vec2 = self.index.reconstruct(idx2)
        
        # Cosine similarity (vectors are normalized)
        similarity = np.dot(vec1, vec2)
        return float(similarity)
    
    def get_most_similar(
        self,
        isbn: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get most similar books with their similarity scores.
        
        Parameters:
        -----------
        isbn : str
            ISBN of the query book
        top_k : int
            Number of similar books to return
        
        Returns:
        --------
        List of dicts with book info and similarity scores
        """
        results = self.recommend_by_isbn(isbn, top_k=top_k)
        
        if results.empty:
            return []
        
        return [
            {
                "isbn": row["isbn"],
                "title": row["title"],
                "authors": row.get("authors", "Unknown"),
                "similarity": float(row["similarity"])
            }
            for _, row in results.iterrows()
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the recommender.
        
        Returns:
        --------
        dict: Statistics dictionary
        """
        stats = {
            "total_books": len(self.books),
            "index_dimension": self.index.d,
            "index_size": self.index.ntotal,
            "model_name": self.metadata.get("embedding_model", "Unknown") if self.metadata else "Unknown",
            "unique_authors": self.books["authors"].nunique() if "authors" in self.books.columns else 0,
            "unique_publishers": self.books["publisher"].nunique() if "publisher" in self.books.columns else 0,
        }
        
        if "category" in self.books.columns:
            stats["unique_categories"] = self.books["category"].nunique()
            stats["top_categories"] = self.books["category"].value_counts().head(5).to_dict()
        
        return stats
    
    def __repr__(self) -> str:
        """String representation of the recommender."""
        return (
            f"ContentRecommender("
            f"books={len(self.books)}, "
            f"index_size={self.index.ntotal}, "
            f"dim={self.index.d})"
        )


# Factory function to load from artifacts
def load_content_recommender(artifact_dir: Union[str, Path]) -> ContentRecommender:
    """
    Convenience function to load a ContentRecommender from artifacts.
    
    Parameters:
    -----------
    artifact_dir : str or Path
        Path to the artifacts directory
    
    Returns:
    --------
    ContentRecommender: Loaded recommender instance
    """
    return ContentRecommender.load(artifact_dir)