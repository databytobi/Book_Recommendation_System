from pathlib import Path
import sys
import pandas as pd
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# pyrefly: ignore [missing-import]
from content_recommender import ContentRecommender


BASE_DIR = Path(__file__).resolve().parents[4]

ARTIFACT_DIR = (
    BASE_DIR
    / "apps"
    / "api"
    / "ml"
    / "artifacts"
)


class ContentService:
    """
    Production wrapper around ContentRecommender.
    Provides caching, error handling, and logging for the content-based recommender.
    """

    def __init__(self, artifact_dir: Optional[Path] = None, load_on_init: bool = True):
        """
        Initialize the content service.
        
        Parameters:
        -----------
        artifact_dir : Path, optional
            Directory containing the artifacts. Defaults to ARTIFACT_DIR.
        load_on_init : bool
            Whether to load artifacts immediately on initialization.
        """
        self.artifact_dir = artifact_dir or ARTIFACT_DIR
        self.recommender = None
        self._cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 3600  # 1 hour cache TTL
        
        if load_on_init:
            self.load_artifacts()
        
        logger.info(f"ContentService initialized with artifact_dir: {self.artifact_dir}")
    
    def load_artifacts(self, force_reload: bool = False) -> bool:
        """
        Load content artifacts from disk.
        
        Parameters:
        -----------
        force_reload : bool
            Whether to force reload even if already loaded.
        
        Returns:
        --------
        bool: True if successful, False otherwise.
        """
        # Check if already loaded and not forcing reload
        if self.recommender is not None and not force_reload:
            logger.info("Artifacts already loaded. Use force_reload=True to reload.")
            return True
        
        try:
            logger.info("Loading content artifacts...")
            
            # Load using the class method
            self.recommender = ContentRecommender.load(self.artifact_dir)
            
            # Update cache timestamp
            self._cache_timestamp = datetime.now()
            
            logger.info(f"✅ Content artifacts loaded successfully")
            logger.info(f"   Books: {len(self.recommender.books):,}")
            logger.info(f"   Vectors: {self.recommender.index.ntotal:,}")
            
            return True
            
        except FileNotFoundError as e:
            logger.error(f"❌ Artifacts not found: {e}")
            logger.info("Please run the embedding pipeline first:")
            logger.info("  python apps/api/ml/features/embedding_pipeline.py")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error loading artifacts: {e}")
            return False
    
    def _ensure_loaded(self) -> bool:
        """
        Ensure artifacts are loaded before making recommendations.
        
        Returns:
        --------
        bool: True if loaded, False otherwise.
        """
        if self.recommender is None:
            return self.load_artifacts()
        return True
    
    def _get_from_cache(self, key: str) -> Optional[pd.DataFrame]:
        """
        Get recommendations from cache if valid.
        
        Parameters:
        -----------
        key : str
            Cache key.
        
        Returns:
        --------
        pd.DataFrame or None: Cached recommendations if valid.
        """
        if key in self._cache:
            # Check if cache is still valid
            if self._cache_timestamp is not None:
                age = (datetime.now() - self._cache_timestamp).total_seconds()
                if age < self._cache_ttl:
                    logger.debug(f"Cache hit for key: {key}")
                    return self._cache[key]
                else:
                    logger.debug(f"Cache expired for key: {key}")
                    del self._cache[key]
        return None
    
    def _cache_results(self, key: str, results: pd.DataFrame) -> None:
        """
        Cache recommendation results.
        
        Parameters:
        -----------
        key : str
            Cache key.
        results : pd.DataFrame
            Results to cache.
        """
        if len(self._cache) > 100:
            # Limit cache size
            self._cache.clear()
        self._cache[key] = results
        self._cache_timestamp = datetime.now()
    
    def recommend_by_book(
        self,
        title: str,
        top_k: int = 10,
        fuzzy_match: bool = True,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Recommend books similar to a title.
        
        Parameters:
        -----------
        title : str
            Book title to find similar books for.
        top_k : int
            Number of recommendations to return.
        fuzzy_match : bool
            Whether to use fuzzy matching for the title.
        use_cache : bool
            Whether to use cached results.
        
        Returns:
        --------
        pd.DataFrame: Recommendations with similarity scores.
        """
        if not self._ensure_loaded():
            return pd.DataFrame()
        
        # Check cache
        cache_key = f"by_book_{title}_{top_k}_{fuzzy_match}"
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached is not None:
                return cached
        
        try:
            logger.info(f"Recommending books similar to: {title}")
            
            results = self.recommender.recommend_by_title(
                title=title,
                top_k=top_k,
                fuzzy_match=fuzzy_match
            )
            
            # Cache results
            if use_cache and not results.empty:
                self._cache_results(cache_key, results)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error recommending by book: {e}")
            return pd.DataFrame()
    
    def recommend_by_isbn(
        self,
        isbn: str,
        top_k: int = 10,
        exclude_same_author: bool = False,
        min_similarity: float = 0.0,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Recommend books similar to an ISBN.
        
        Parameters:
        -----------
        isbn : str
            ISBN to find similar books for.
        top_k : int
            Number of recommendations to return.
        exclude_same_author : bool
            Whether to exclude books by the same author.
        min_similarity : float
            Minimum similarity threshold.
        use_cache : bool
            Whether to use cached results.
        
        Returns:
        --------
        pd.DataFrame: Recommendations with similarity scores.
        """
        if not self._ensure_loaded():
            return pd.DataFrame()
        
        # Check cache
        cache_key = f"by_isbn_{isbn}_{top_k}_{exclude_same_author}_{min_similarity}"
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached is not None:
                return cached
        
        try:
            logger.info(f"Recommending books similar to ISBN: {isbn}")
            
            results = self.recommender.recommend_by_isbn(
                isbn=isbn,
                top_k=top_k,
                exclude_same_author=exclude_same_author,
                min_similarity=min_similarity
            )
            
            # Cache results
            if use_cache and not results.empty:
                self._cache_results(cache_key, results)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error recommending by ISBN: {e}")
            return pd.DataFrame()
    
    def recommend_by_description(
        self,
        query: str,
        top_k: int = 10,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Semantic recommendation from text query.
        
        Parameters:
        -----------
        query : str
            Text query to search for.
        top_k : int
            Number of recommendations to return.
        use_cache : bool
            Whether to use cached results.
        
        Returns:
        --------
        pd.DataFrame: Recommendations with similarity scores.
        """
        if not self._ensure_loaded():
            return pd.DataFrame()
        
        # Check cache (shorter TTL for text queries)
        cache_key = f"by_desc_{query[:50]}_{top_k}"
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached is not None:
                return cached
        
        try:
            logger.info(f"Semantic search for: {query[:50]}...")
            
            results = self.recommender.recommend_by_text(
                query_text=query,
                top_k=top_k
            )
            
            # Cache results (shorter TTL for text queries)
            if use_cache and not results.empty:
                # Set shorter TTL for text queries
                self._cache_results(cache_key, results)
            
            return results
            
        except ImportError as e:
            logger.error(f"❌ SentenceTransformer not installed: {e}")
            logger.info("Please install: pip install sentence-transformers")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"❌ Error in semantic search: {e}")
            return pd.DataFrame()
    
    def similar_books(
        self,
        isbn: str,
        top_k: int = 10
    ) -> pd.DataFrame:
        """
        Get similar books for a given ISBN.
        
        Parameters:
        -----------
        isbn : str
            ISBN to find similar books for
        top_k : int
            Number of similar books to return
        
        Returns:
        --------
        pd.DataFrame: Similar books with similarity scores
        """
        return self.recommend_by_isbn(isbn, top_k)
    
    def explain(
        self,
        title: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Explain why recommendations appear for a given title.
        
        Parameters:
        -----------
        title : str
            Book title to explain recommendations for.
        top_k : int
            Number of recommendations to include in explanation.
        
        Returns:
        --------
        dict: Explanation with query book and recommendations.
        """
        if not self._ensure_loaded():
            return {
                "query_book": title,
                "recommendations": pd.DataFrame(),
                "error": "Artifacts not loaded"
            }
        
        try:
            logger.info(f"Explaining recommendations for: {title}")
            
            recommendations = self.recommender.recommend_by_title(
                title=title,
                top_k=top_k,
                fuzzy_match=True
            )
            
            # Get the matched book if available
            matched_book = None
            if not recommendations.empty:
                # Try to find the original book
                matches = self.recommender.books[
                    self.recommender.books["title"].str.contains(
                        title,
                        case=False,
                        na=False,
                        regex=False
                    )
                ]
                if not matches.empty:
                    matched_book = {
                        "title": matches.iloc[0]["title"],
                        "authors": matches.iloc[0].get("authors", "Unknown"),
                        "isbn": matches.iloc[0]["isbn"]
                    }
            
            return {
                "query_book": title,
                "matched_book": matched_book,
                "recommendations": recommendations,
                "total_recommendations": len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"❌ Error explaining recommendations: {e}")
            return {
                "query_book": title,
                "recommendations": pd.DataFrame(),
                "error": str(e)
            }
    
    def explain_by_isbn(
        self,
        isbn: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Explain why recommendations appear for a given ISBN.
        
        Parameters:
        -----------
        isbn : str
            ISBN to explain recommendations for.
        top_k : int
            Number of recommendations to include in explanation.
        
        Returns:
        --------
        dict: Explanation with query book and recommendations.
        """
        if not self._ensure_loaded():
            return {
                "query_isbn": isbn,
                "recommendations": pd.DataFrame(),
                "error": "Artifacts not loaded"
            }
        
        try:
            logger.info(f"Explaining recommendations for ISBN: {isbn}")
            
            # Get the book info
            book_info = self.recommender.explain_book(isbn)
            
            recommendations = self.recommender.recommend_by_isbn(
                isbn=isbn,
                top_k=top_k
            )
            
            return {
                "query_isbn": isbn,
                "query_book": book_info,
                "recommendations": recommendations,
                "total_recommendations": len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"❌ Error explaining recommendations: {e}")
            return {
                "query_isbn": isbn,
                "recommendations": pd.DataFrame(),
                "error": str(e)
            }
    
    def get_book_info(
        self,
        isbn: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a book.
        
        Parameters:
        -----------
        isbn : str
            ISBN of the book.
        
        Returns:
        --------
        dict or None: Book information.
        """
        if not self._ensure_loaded():
            return None
        
        try:
            return self.recommender.explain_book(isbn)
        except Exception as e:
            logger.error(f"❌ Error getting book info: {e}")
            return None
    
    def get_similarity(
        self,
        isbn1: str,
        isbn2: str
    ) -> Optional[float]:
        """
        Get similarity score between two books.
        
        Parameters:
        -----------
        isbn1 : str
            ISBN of first book.
        isbn2 : str
            ISBN of second book.
        
        Returns:
        --------
        float or None: Similarity score.
        """
        if not self._ensure_loaded():
            return None
        
        try:
            return self.recommender.get_similarity(isbn1, isbn2)
        except Exception as e:
            logger.error(f"❌ Error calculating similarity: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get service statistics.
        
        Returns:
        --------
        dict: Statistics dictionary.
        """
        if not self._ensure_loaded():
            return {"status": "not_loaded"}
        
        try:
            stats = self.recommender.get_statistics()
            stats.update({
                "cache_size": len(self._cache),
                "cache_ttl": self._cache_ttl,
                "artifact_dir": str(self.artifact_dir)
            })
            return stats
        except Exception as e:
            logger.error(f"❌ Error getting statistics: {e}")
            return {"error": str(e)}
    
    def clear_cache(self) -> None:
        """
        Clear the recommendation cache.
        """
        self._cache.clear()
        self._cache_timestamp = None
        logger.info("Cache cleared")
    
    def refresh(self) -> bool:
        """
        Refresh the service by reloading artifacts and clearing cache.
        
        Returns:
        --------
        bool: True if successful.
        """
        self.clear_cache()
        return self.load_artifacts(force_reload=True)
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the service.
        
        Returns:
        --------
        dict: Health status information.
        """
        status = {
            "status": "healthy",
            "artifacts_loaded": self.recommender is not None,
            "cache_size": len(self._cache),
        }
        
        if self.recommender is not None:
            try:
                status.update({
                    "total_books": len(self.recommender.books),
                    "vector_count": self.recommender.index.ntotal,
                    "vector_dimension": self.recommender.index.d,
                })
            except Exception:
                status["status"] = "degraded"
        else:
            status["status"] = "unhealthy"
            status["error"] = "Artifacts not loaded"
        
        return status


# Singleton instance
_content_service = None


def get_content_service() -> ContentService:
    """
    Get or create the singleton ContentService instance.
    
    Returns:
    --------
    ContentService: The singleton instance.
    """
    global _content_service
    if _content_service is None:
        _content_service = ContentService()
    return _content_service


# Convenience function for quick access
def get_content_recommendations(
    query: str,
    top_k: int = 10,
    by: str = "title"
) -> pd.DataFrame:
    """
    Quick function to get content recommendations.
    
    Parameters:
    -----------
    query : str
        Search query (title or text).
    top_k : int
        Number of recommendations.
    by : str
        Type of search: 'title', 'isbn', or 'text'.
    
    Returns:
    --------
    pd.DataFrame: Recommendations.
    """
    service = get_content_service()
    
    if by == "isbn":
        return service.recommend_by_isbn(query, top_k)
    elif by == "text":
        return service.recommend_by_description(query, top_k)
    else:
        return service.recommend_by_book(query, top_k)