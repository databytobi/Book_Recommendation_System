from pathlib import Path
import logging
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import pandas as pd

# pyrefly: ignore [missing-import]
from apps.api.ml.hybrid.hybrid_recommender import (
    HybridRecommender, get_hybrid_recommender
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HybridService:
    """
    Production service for hybrid recommendations.
    Wraps the HybridRecommender with caching, error handling, and convenient methods.
    """

    def __init__(self, load_on_init: bool = True):
        """
        Initialize the hybrid service.
        
        Parameters:
        -----------
        load_on_init : bool
            Whether to load the recommender immediately on initialization.
        """
        self.recommender = None
        self._cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 3600  # 1 hour cache TTL
        self._request_count = 0
        self._last_request_time = None
        self._is_initialized = False
        
        if load_on_init:
            self._initialize()
        
        logger.info("HybridService initialized")

    def _initialize(self) -> None:
        """Initialize the hybrid recommender."""
        try:
            print("=" * 60)
            print("INITIALIZING HYBRID SERVICE")
            print("=" * 60)
            
            self.recommender = get_hybrid_recommender()
            self._is_initialized = True
            
            # Log weights
            weights = self.recommender.get_stats()["weights"]
            print(f"✅ Hybrid service initialized with weights:")
            print(f"   Collaborative: {weights['collaborative']:.2f}")
            print(f"   Content: {weights['content']:.2f}")
            print(f"   Popularity: {weights['popularity']:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Error initializing hybrid service: {e}")
            self._is_initialized = False
            raise

    def _ensure_initialized(self) -> bool:
        """Ensure the service is initialized."""
        if not self._is_initialized or self.recommender is None:
            self._initialize()
        return self._is_initialized

    # --------------------------------------------------
    # CACHE
    # --------------------------------------------------

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

    # --------------------------------------------------
    # PERSONALIZED RECOMMENDATIONS
    # --------------------------------------------------

    def recommend_for_user(
        self,
        user_id: Union[str, int],
        top_k: int = 20,
        use_cache: bool = True,
        min_score: float = 0.0,
        exclude_authors: Optional[List[str]] = None,
        fallback_to_popularity: bool = True
    ) -> pd.DataFrame:
        """
        Generate personalized hybrid recommendations for a user.
        
        Parameters:
        -----------
        user_id : str or int
            User ID to generate recommendations for
        top_k : int
            Number of recommendations to return
        use_cache : bool
            Whether to use cached results
        min_score : float
            Minimum hybrid score threshold
        exclude_authors : List[str], optional
            List of authors to exclude
        fallback_to_popularity : bool
            Whether to fallback to popularity if collaborative fails
        
        Returns:
        --------
        pd.DataFrame: Hybrid recommendations with scores
        """
        if not self._ensure_initialized():
            return pd.DataFrame()
        
        self._request_count += 1
        self._last_request_time = datetime.now()
        
        try:
            # Check cache
            cache_key = f"user_{user_id}_{top_k}_{min_score}"
            if use_cache:
                cached = self._get_from_cache(cache_key)
                if cached is not None:
                    return cached
            
            logger.info(f"Generating hybrid recommendations for user: {user_id}")
            
            # Get recommendations
            results = self.recommender.recommend_for_user(
                user_id=user_id,
                top_k=top_k,
                min_score=min_score,
                exclude_authors=exclude_authors,
                fallback_to_popularity=fallback_to_popularity
            )
            
            # Cache results
            if use_cache and not results.empty:
                self._cache_results(cache_key, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error recommending for user {user_id}: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

    # --------------------------------------------------
    # SIMILAR BOOKS
    # --------------------------------------------------

    def recommend_similar_books(
        self,
        isbn: str,
        top_k: int = 20,
        use_cache: bool = True,
        min_score: float = 0.0
    ) -> pd.DataFrame:
        """
        Recommend books similar to a given ISBN.
        
        Parameters:
        -----------
        isbn : str
            ISBN to find similar books for
        top_k : int
            Number of recommendations to return
        use_cache : bool
            Whether to use cached results
        min_score : float
            Minimum hybrid score threshold
        
        Returns:
        --------
        pd.DataFrame: Similar books with hybrid scores
        """
        if not self._ensure_initialized():
            return pd.DataFrame()
        
        try:
            # Check cache
            cache_key = f"similar_{isbn}_{top_k}_{min_score}"
            if use_cache:
                cached = self._get_from_cache(cache_key)
                if cached is not None:
                    return cached
            
            logger.info(f"Finding similar books for ISBN: {isbn}")
            
            # Get recommendations
            results = self.recommender.recommend_similar_books(
                isbn=isbn,
                top_k=top_k,
                min_score=min_score
            )
            
            # Cache results
            if use_cache and not results.empty:
                self._cache_results(cache_key, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar books for {isbn}: {e}")
            return pd.DataFrame()

    # --------------------------------------------------
    # SEMANTIC SEARCH
    # --------------------------------------------------

    def search_books(
        self,
        query: str,
        top_k: int = 20,
        use_cache: bool = True,
        min_score: float = 0.0
    ) -> pd.DataFrame:
        """
        Perform semantic search and rank results.
        
        Parameters:
        -----------
        query : str
            Search query
        top_k : int
            Number of results to return
        use_cache : bool
            Whether to use cached results
        min_score : float
            Minimum hybrid score threshold
        
        Returns:
        --------
        pd.DataFrame: Search results with hybrid scores
        """
        if not self._ensure_initialized():
            return pd.DataFrame()
        
        try:
            # Check cache
            cache_key = f"search_{query[:50]}_{top_k}_{min_score}"
            if use_cache:
                cached = self._get_from_cache(cache_key)
                if cached is not None:
                    return cached
            
            logger.info(f"Searching for: '{query}'")
            
            # Get results
            results = self.recommender.search_and_recommend(
                query=query,
                top_k=top_k,
                min_score=min_score
            )
            
            # Cache results
            if use_cache and not results.empty:
                self._cache_results(cache_key, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching for '{query}': {e}")
            return pd.DataFrame()

    # --------------------------------------------------
    # COLD START / TRENDING
    # --------------------------------------------------

    def trending_books(
        self,
        top_k: int = 20,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Get trending/popular books (cold start recommendations).
        
        Parameters:
        -----------
        top_k : int
            Number of recommendations to return
        use_cache : bool
            Whether to use cached results
        
        Returns:
        --------
        pd.DataFrame: Popularity-based recommendations
        """
        if not self._ensure_initialized():
            return pd.DataFrame()
        
        try:
            # Check cache
            cache_key = f"trending_{top_k}"
            if use_cache:
                cached = self._get_from_cache(cache_key)
                if cached is not None:
                    return cached
            
            logger.info(f"Getting trending books (top {top_k})")
            
            # Get recommendations
            results = self.recommender.cold_start_recommendations(top_k=top_k)
            
            # Cache results
            if use_cache and not results.empty:
                self._cache_results(cache_key, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting trending books: {e}")
            return pd.DataFrame()

    # --------------------------------------------------
    # RECOMMENDATION EXPLANATION
    # --------------------------------------------------

    def explain(
        self,
        recommendation_row: pd.Series
    ) -> Dict[str, Any]:
        """
        Generate explanation for a recommendation.
        
        Parameters:
        -----------
        recommendation_row : pd.Series
            Row from recommendations DataFrame
        
        Returns:
        --------
        dict: Explanation with scores and weights
        """
        if not self._ensure_initialized():
            return {"error": "Service not initialized"}
        
        try:
            return self.recommender.explain_recommendation(recommendation_row)
        except Exception as e:
            logger.error(f"Error explaining recommendation: {e}")
            return {
                "error": str(e),
                "title": recommendation_row.get("title", "Unknown")
            }

    # --------------------------------------------------
    # BATCH RECOMMENDATIONS
    # --------------------------------------------------

    def recommend_for_users(
        self,
        user_ids: List[Union[str, int]],
        top_k: int = 20,
        **kwargs
    ) -> Dict[Union[str, int], pd.DataFrame]:
        """
        Generate recommendations for multiple users.
        
        Parameters:
        -----------
        user_ids : List[str or int]
            List of user IDs
        top_k : int
            Number of recommendations per user
        **kwargs : Additional arguments passed to recommend_for_user
        
        Returns:
        --------
        dict: Dictionary mapping user_id to recommendations DataFrame
        """
        if not self._ensure_initialized():
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

    # --------------------------------------------------
    # HEALTH CHECK
    # --------------------------------------------------

    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the hybrid service.
        
        Returns:
        --------
        dict: Health status information
        """
        if not self._is_initialized or self.recommender is None:
            return {
                "status": "unhealthy",
                "message": "Service not initialized",
                "is_initialized": False
            }
        
        try:
            # Get health from recommender
            health = self.recommender.health_check()
            
            # Add service-specific info
            health.update({
                "cache_size": len(self._cache),
                "cache_ttl": self._cache_ttl,
                "request_count": self._request_count,
                "last_request": self._last_request_time.isoformat() if self._last_request_time else None,
                "service_initialized": True
            })
            
            return health
            
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {
                "status": "error",
                "message": str(e),
                "is_initialized": self._is_initialized
            }

    # --------------------------------------------------
    # STATS
    # --------------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        """
        Get service statistics.
        
        Returns:
        --------
        dict: Statistics dictionary
        """
        if not self._is_initialized or self.recommender is None:
            return {
                "status": "not_initialized",
                "is_initialized": False
            }
        
        try:
            recommender_stats = self.recommender.get_stats()
            
            stats = {
                "status": "ready",
                "is_initialized": True,
                "request_count": self._request_count,
                "last_request": self._last_request_time.isoformat() if self._last_request_time else None,
                "cache_size": len(self._cache),
                "cache_ttl": self._cache_ttl,
                "recommender": recommender_stats
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    # --------------------------------------------------
    # REFRESH
    # --------------------------------------------------

    def refresh(self) -> bool:
        """
        Refresh the service by reloading the recommender.
        
        Returns:
        --------
        bool: True if successful
        """
        try:
            self.clear_cache()
            self._request_count = 0
            self._last_request_time = None
            
            if self.recommender:
                self.recommender.refresh()
            else:
                self._initialize()
            
            logger.info("Hybrid service refreshed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing hybrid service: {e}")
            return False

    # --------------------------------------------------
    # WEIGHT CONFIGURATION
    # --------------------------------------------------

    def update_weights(
        self,
        collaborative_weight: Optional[float] = None,
        content_weight: Optional[float] = None,
        popularity_weight: Optional[float] = None
    ) -> bool:
        """
        Update the recommendation weights.
        
        Parameters:
        -----------
        collaborative_weight : float, optional
            New collaborative weight
        content_weight : float, optional
            New content weight
        popularity_weight : float, optional
            New popularity weight
        
        Returns:
        --------
        bool: True if successful
        """
        if not self._ensure_initialized():
            return False
        
        try:
            # Create new recommender with updated weights
            # pyrefly: ignore [missing-import]
            from apps.api.ml.hybrid.hybrid_recommender import HybridRecommender
            
            new_collab = collaborative_weight or self.recommender.collaborative_weight
            new_content = content_weight or self.recommender.content_weight
            new_pop = popularity_weight or self.recommender.popularity_weight
            
            # Validate weights
            total = new_collab + new_content + new_pop
            if not 0.9 <= total <= 1.1:
                raise ValueError(f"Weights must sum to 1. Got: {total}")
            
            # Create new recommender instance
            new_recommender = HybridRecommender(
                collaborative_weight=new_collab,
                content_weight=new_content,
                popularity_weight=new_pop,
                load_on_init=True
            )
            
            self.recommender = new_recommender
            self.clear_cache()
            
            logger.info(f"Weights updated: Collaborative={new_collab:.2f}, Content={new_content:.2f}, Popularity={new_pop:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating weights: {e}")
            return False

    # --------------------------------------------------
    # REPRESENTATION
    # --------------------------------------------------

    def __repr__(self) -> str:
        status = "ready" if self._is_initialized else "not initialized"
        return f"HybridService(status={status}, cache_size={len(self._cache)})"


# =====================================================
# SINGLETON INSTANCE
# =====================================================

_hybrid_service = None


def get_hybrid_service() -> HybridService:
    """
    Get or create the singleton HybridService instance.
    
    Returns:
    --------
    HybridService: The singleton instance
    """
    global _hybrid_service
    if _hybrid_service is None:
        _hybrid_service = HybridService()
    return _hybrid_service


# =====================================================
# CONVENIENCE FUNCTIONS
# =====================================================

def get_hybrid_recommendations(
    user_id: Union[str, int],
    top_k: int = 20,
    **kwargs
) -> pd.DataFrame:
    """
    Quick function to get hybrid recommendations for a user.
    
    Parameters:
    -----------
    user_id : str or int
        User ID
    top_k : int
        Number of recommendations
    **kwargs : Additional arguments passed to recommend_for_user
    
    Returns:
    --------
    pd.DataFrame: Hybrid recommendations
    """
    service = get_hybrid_service()
    return service.recommend_for_user(user_id, top_k, **kwargs)


def get_hybrid_similar_books(
    isbn: str,
    top_k: int = 20,
    **kwargs
) -> pd.DataFrame:
    """
    Quick function to get similar books using hybrid approach.
    
    Parameters:
    -----------
    isbn : str
        ISBN to find similar books for
    top_k : int
        Number of similar books
    **kwargs : Additional arguments passed to recommend_similar_books
    
    Returns:
    --------
    pd.DataFrame: Similar books
    """
    service = get_hybrid_service()
    return service.recommend_similar_books(isbn, top_k, **kwargs)


def get_hybrid_trending(top_k: int = 20) -> pd.DataFrame:
    """
    Quick function to get trending books.
    
    Parameters:
    -----------
    top_k : int
        Number of trending books to return
    
    Returns:
    --------
    pd.DataFrame: Trending books
    """
    service = get_hybrid_service()
    return service.trending_books(top_k=top_k)