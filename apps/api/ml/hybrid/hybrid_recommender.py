from pathlib import Path
import logging
from typing import Optional, Dict, Any, List, Tuple, Union
from datetime import datetime

import numpy as np
import pandas as pd

from ..popularity.popularity_service import get_popularity_service
from ..content.content_service import get_content_service
from ..collaborative.collaborative_service import get_collaborative_service

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HybridRecommender:
    """
    Hybrid recommender that combines collaborative, content-based, and popularity-based recommendations.
    Uses weighted scoring to generate diverse and personalized recommendations.
    """

    def __init__(
        self,
        collaborative_weight: float = 0.50,
        content_weight: float = 0.30,
        popularity_weight: float = 0.20,
        load_on_init: bool = True,
        use_caching: bool = True,
        cache_ttl: int = 3600
    ):
        """
        Initialize the hybrid recommender.
        
        Parameters:
        -----------
        collaborative_weight : float
            Weight for collaborative filtering recommendations
        content_weight : float
            Weight for content-based recommendations
        popularity_weight : float
            Weight for popularity-based recommendations
        load_on_init : bool
            Whether to load services immediately on initialization
        use_caching : bool
            Whether to use caching for recommendations
        cache_ttl : int
            Cache TTL in seconds
        """
        self.collaborative_weight = collaborative_weight
        self.content_weight = content_weight
        self.popularity_weight = popularity_weight
        self.use_caching = use_caching
        self.cache_ttl = cache_ttl
        
        # Validate weights sum to 1
        total_weight = collaborative_weight + content_weight + popularity_weight
        if not np.isclose(total_weight, 1.0, rtol=1e-3):
            logger.warning(f"Total weight {total_weight:.2f} doesn't sum to 1. Normalizing...")
            self.collaborative_weight = collaborative_weight / total_weight
            self.content_weight = content_weight / total_weight
            self.popularity_weight = popularity_weight / total_weight
            logger.info(f"Normalized weights: {self.collaborative_weight:.2f}, {self.content_weight:.2f}, {self.popularity_weight:.2f}")
        
        # Cache
        self._cache = {}
        self._cache_timestamp = None
        self._last_request_time = None
        self._request_count = 0
        
        # Services
        self.popularity_service = None
        self.content_service = None
        self.collaborative_service = None
        
        if load_on_init:
            self._initialize_services()
        
        logger.info("HybridRecommender initialized")

    def _initialize_services(self) -> None:
        """Initialize all underlying services."""
        print("=" * 60)
        print("INITIALIZING HYBRID RECOMMENDER")
        print("=" * 60)
        
        try:
            # Load services
            self.popularity_service = get_popularity_service()
            print("✅ Popularity service loaded")
            
            self.content_service = get_content_service()
            print("✅ Content service loaded")
            
            self.collaborative_service = get_collaborative_service()
            print("✅ Collaborative service loaded")
            
            # Get service stats - handle different service structures
            self._service_stats = {
                "popularity": hasattr(self.popularity_service, 'recommender') and 
                             hasattr(self.popularity_service.recommender, 'is_fitted') and 
                             self.popularity_service.recommender.is_fitted,
                "content": self.content_service.recommender is not None if hasattr(self.content_service, 'recommender') else False,
                "collaborative": hasattr(self.collaborative_service, 'model') and 
                                self.collaborative_service.model is not None
            }
            
            print("✅ Hybrid recommender ready")
            print(f"   Weights: Collaborative={self.collaborative_weight:.2f}, Content={self.content_weight:.2f}, Popularity={self.popularity_weight:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Error initializing services: {e}")
            raise

    def _ensure_services(self) -> bool:
        """Ensure all services are initialized."""
        if self.popularity_service is None or self.content_service is None or self.collaborative_service is None:
            self._initialize_services()
        return all([self.popularity_service, self.content_service, self.collaborative_service])

    # ----------------------------------------------------
    # CACHE
    # ----------------------------------------------------

    def _get_from_cache(self, key: str) -> Optional[pd.DataFrame]:
        """Get cached results if valid."""
        if not self.use_caching:
            return None
        
        if key in self._cache:
            if self._cache_timestamp is not None:
                age = (datetime.now() - self._cache_timestamp).total_seconds()
                if age < self.cache_ttl:
                    logger.debug(f"Cache hit for: {key}")
                    return self._cache[key]
                else:
                    del self._cache[key]
        return None

    def _cache_results(self, key: str, results: pd.DataFrame) -> None:
        """Cache results."""
        if not self.use_caching:
            return
        
        if len(self._cache) > 100:
            self._cache.clear()
        self._cache[key] = results
        self._cache_timestamp = datetime.now()

    def clear_cache(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        self._cache_timestamp = None
        logger.info("Cache cleared")

    # ----------------------------------------------------
    # UTILITY
    # ----------------------------------------------------

    def normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        """
        Normalize scores to [0, 1] range using min-max normalization.
        
        Parameters:
        -----------
        scores : np.ndarray
            Array of scores to normalize
        
        Returns:
        --------
        np.ndarray: Normalized scores
        """
        scores = np.array(scores)
        
        if len(scores) == 0:
            return scores
        
        min_score = scores.min()
        max_score = scores.max()
        
        if max_score == min_score:
            return np.ones_like(scores)
        
        return (scores - min_score) / (max_score - min_score)

    def _get_book_metadata(self, isbns: List[str]) -> pd.DataFrame:
        """
        Get metadata for a list of ISBNs.
        
        Parameters:
        -----------
        isbns : List[str]
            List of ISBNs
        
        Returns:
        --------
        pd.DataFrame: Book metadata
        """
        if not isbns:
            return pd.DataFrame()
        
        try:
            # Try to get from content service
            books = self.content_service.recommender.books.copy()
            return books[books["isbn"].isin(isbns)]
        except Exception:
            return pd.DataFrame()

    # ----------------------------------------------------
    # PERSONALIZED RECOMMENDATION
    # ----------------------------------------------------

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
        Generate hybrid recommendations for a user.
        
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
            Whether to fallback to popularity recommendations if collaborative fails
        
        Returns:
        --------
        pd.DataFrame: Hybrid recommendations with scores
        """
        if not self._ensure_services():
            logger.error("Services not initialized")
            return pd.DataFrame()
        
        self._request_count += 1
        self._last_request_time = datetime.now()
        
        try:
            # Check cache
            cache_key = f"user_{user_id}_{top_k}"
            if use_cache:
                cached = self._get_from_cache(cache_key)
                if cached is not None:
                    return cached
            
            logger.info(f"Generating hybrid recommendations for user {user_id}")
            
            # Get collaborative recommendations
            try:
                collab = self.collaborative_service.recommend_for_user(
                    user_id=user_id,
                    top_k=top_k * 3,  # Get extra for normalization
                    filter_liked=True
                )
            except TypeError:
                # If filter_liked is not accepted, try without it
                collab = self.collaborative_service.recommend_for_user(
                    user_id=user_id,
                    top_k=top_k * 3
                )
            except Exception as e:
                logger.warning(f"Collaborative recommendations failed: {e}")
                collab = pd.DataFrame()
            
            # If collaborative is empty, fallback to popularity
            if collab.empty:
                logger.warning(f"User {user_id} not found in collaborative model")
                if fallback_to_popularity:
                    result = self.popularity_service.homepage(top_k=top_k)
                    if use_cache:
                        self._cache_results(cache_key, result)
                    return result
                return pd.DataFrame()
            
            # Get content-based recommendations
            # Get content-based recommendations
            try:  
                # Get user's reading history to find a representative book
                history = self.collaborative_service.get_user_history(user_id, top_k=5)
                if not history.empty:
                    # Use the highest-rated book as query
                    query_book = history.iloc[0].get("title")
                    # Check if query_book is valid (not NaN, not None, and is a string)
                    if query_book and isinstance(query_book, str) and pd.notna(query_book):
                        content = self.content_service.recommend_by_book(
                            title=query_book,
                            top_k=top_k * 2
                        )
                    else:
                        logger.info(f"Skipping content recommendations for user {user_id} - invalid query book")
                        content = pd.DataFrame()
                else:
                    content = pd.DataFrame()
            except Exception as e:
                logger.warning(f"Content recommendations failed: {e}")
                content = pd.DataFrame()
            
            # Prepare collaborative results
            collab = collab.copy()
            collab["collab_score"] = self.normalize_scores(collab["score"].values)
            collab["content_score"] = 0.0
            collab["popularity_score"] = 0.0
            
            # Add content scores
            if not content.empty and "isbn" in content.columns:
                content_score_map = dict(zip(content["isbn"], content.get("similarity", 1.0)))
                collab["content_score"] = collab["isbn"].map(
                    lambda x: content_score_map.get(x, 0.0)
                )
                if collab["content_score"].max() > 0:
                    collab["content_score"] = self.normalize_scores(collab["content_score"].values)
            
            # Add popularity scores (based on adjusted_score or ratings_count)
            if "adjusted_score" in collab.columns:
                collab["popularity_score"] = self.normalize_scores(collab["adjusted_score"].values)
            elif "ratings_count" in collab.columns:
                # Use ratings count as popularity proxy
                collab["popularity_score"] = self.normalize_scores(
                    np.log1p(collab["ratings_count"].fillna(0).values)
                )
            
            # Calculate hybrid score
            collab["hybrid_score"] = (
                self.collaborative_weight * collab["collab_score"] +
                self.content_weight * collab["content_score"] +
                self.popularity_weight * collab["popularity_score"]
            )
            
            # Filter by min score
            if min_score > 0:
                collab = collab[collab["hybrid_score"] >= min_score]
            
            # Exclude authors if specified
            if exclude_authors and "authors" in collab.columns:
                collab = collab[~collab["authors"].isin(exclude_authors)]
            
            # Sort and limit
            collab = collab.sort_values("hybrid_score", ascending=False).head(top_k)
            
            # Add rank
            if "rank" in collab.columns:
                collab = collab.drop(columns=["rank"])
                collab.insert(0, "rank", range(1, len(collab) + 1))
            
            # Cache results
            if use_cache:
                self._cache_results(cache_key, collab)
            
            return collab
            
        except Exception as e:
            logger.error(f"Error generating hybrid recommendations: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

    # ----------------------------------------------------
    # SIMILAR BOOKS
    # ----------------------------------------------------

    def recommend_similar_books(
        self,
        isbn: str,
        top_k: int = 20,
        use_cache: bool = True,
        min_score: float = 0.0
    ) -> pd.DataFrame:
        """
        Recommend books similar to a given ISBN using hybrid approach.
        
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
        if not self._ensure_services():
            logger.error("Services not initialized")
            return pd.DataFrame()
        
        try:
            # Check cache
            cache_key = f"similar_{isbn}_{top_k}"
            if use_cache:
                cached = self._get_from_cache(cache_key)
                if cached is not None:
                    return cached
            
            logger.info(f"Generating similar books for ISBN: {isbn}")
            
            # Get content-based similar books
            content = self.content_service.similar_books(
                isbn=isbn,
                top_k=top_k * 2
            )
            
            if content.empty:
                logger.warning(f"No similar books found for ISBN: {isbn}")
                return pd.DataFrame()
            
            content = content.copy()
            
            # Get popularity scores
            if "adjusted_score" in content.columns:
                content["popularity_score"] = self.normalize_scores(content["adjusted_score"].values)
            else:
                content["popularity_score"] = 0.0
            
            # Normalize content scores
            if "similarity" in content.columns:
                content["content_score"] = self.normalize_scores(content["similarity"].values)
            else:
                content["content_score"] = 1.0
            
            # Calculate hybrid score
            content["hybrid_score"] = (
                self.content_weight * content["content_score"] +
                self.popularity_weight * content["popularity_score"]
            )
            
            # Filter by min score
            if min_score > 0:
                content = content[content["hybrid_score"] >= min_score]
            
            # Sort and limit
            content = content.sort_values("hybrid_score", ascending=False).head(top_k)
            
            # Add rank
            content.insert(0, "rank", range(1, len(content) + 1))
            
            # Cache results
            if use_cache:
                self._cache_results(cache_key, content)
            
            return content
            
        except Exception as e:
            logger.error(f"Error finding similar books: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

    # ----------------------------------------------------
    # SEARCH + RANKING
    # ----------------------------------------------------

    def search_and_recommend(
        self,
        query: str,
        top_k: int = 20,
        use_cache: bool = True,
        min_score: float = 0.0
    ) -> pd.DataFrame:
        """
        Perform semantic search and rank results using hybrid scoring.
        
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
        if not self._ensure_services():
            logger.error("Services not initialized")
            return pd.DataFrame()
        
        try:
            # Check cache
            cache_key = f"search_{query[:50]}_{top_k}"
            if use_cache:
                cached = self._get_from_cache(cache_key)
                if cached is not None:
                    return cached
            
            logger.info(f"Searching and ranking: '{query}'")
            
            # Get semantic search results
            results = self.content_service.recommend_by_description(
                query=query,
                top_k=top_k * 2
            )
            
            if results.empty:
                logger.warning(f"No results found for query: '{query}'")
                return pd.DataFrame()
            
            results = results.copy()
            
            # Normalize scores
            if "similarity" in results.columns:
                results["content_score"] = self.normalize_scores(results["similarity"].values)
            else:
                results["content_score"] = 1.0
            
            # Add popularity scores if available
            if "adjusted_score" in results.columns:
                results["popularity_score"] = self.normalize_scores(results["adjusted_score"].values)
            else:
                results["popularity_score"] = 0.0
            
            # Calculate hybrid score
            results["hybrid_score"] = (
                self.content_weight * results["content_score"] +
                self.popularity_weight * results["popularity_score"]
            )
            
            # Filter by min score
            if min_score > 0:
                results = results[results["hybrid_score"] >= min_score]
            
            # Sort and limit
            results = results.sort_values("hybrid_score", ascending=False).head(top_k)
            
            # Add rank
            results.insert(0, "rank", range(1, len(results) + 1))
            
            # Cache results
            if use_cache:
                self._cache_results(cache_key, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in search and recommend: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

    # ----------------------------------------------------
    # COLD START
    # ----------------------------------------------------

    def cold_start_recommendations(
        self,
        top_k: int = 20,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Get recommendations for new users (cold start).
        
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
        if not self._ensure_services():
            logger.error("Services not initialized")
            return pd.DataFrame()
        
        try:
            cache_key = f"cold_start_{top_k}"
            if use_cache:
                cached = self._get_from_cache(cache_key)
                if cached is not None:
                    return cached
            
            logger.info("Generating cold start recommendations")
            
            result = self.popularity_service.homepage(top_k=top_k)
            
            if use_cache:
                self._cache_results(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating cold start recommendations: {e}")
            return pd.DataFrame()

    # ----------------------------------------------------
    # EXPLAIN RECOMMENDATION
    # ----------------------------------------------------

    def explain_recommendation(self, row: pd.Series) -> Dict[str, Any]:
        """
        Generate explanation for a recommendation.
        
        Parameters:
        -----------
        row : pd.Series
            Row from recommendations DataFrame
        
        Returns:
        --------
        dict: Explanation with scores and weights
        """
        return {
            "title": row.get("title", ""),
            "hybrid_score": float(row.get("hybrid_score", 0)),
            "collaborative_weight": self.collaborative_weight,
            "content_weight": self.content_weight,
            "popularity_weight": self.popularity_weight,
            "score_breakdown": {
                "collaborative": float(row.get("collab_score", 0) * self.collaborative_weight),
                "content": float(row.get("content_score", 0) * self.content_weight),
                "popularity": float(row.get("popularity_score", 0) * self.popularity_weight)
            } if "collab_score" in row else None
        }

    # ----------------------------------------------------
    # STATS
    # ----------------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        """
        Get service statistics.
        
        Returns:
        --------
        dict: Statistics dictionary
        """
        return {
            "weights": {
                "collaborative": self.collaborative_weight,
                "content": self.content_weight,
                "popularity": self.popularity_weight
            },
            "cache": {
                "size": len(self._cache),
                "ttl": self.cache_ttl,
                "enabled": self.use_caching
            },
            "requests": {
                "count": self._request_count,
                "last_request": self._last_request_time.isoformat() if self._last_request_time else None
            },
            "services": getattr(self, "_service_stats", {}),
            "status": "ready" if self._ensure_services() else "not_ready"
        }

    # ----------------------------------------------------
    # HEALTH CHECK
    # ----------------------------------------------------

    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the hybrid recommender.
        
        Returns:
        --------
        dict: Health status information
        """
        status = {
            "status": "healthy",
            "services": {
                "popularity": self.popularity_service is not None,
                "content": self.content_service is not None,
                "collaborative": self.collaborative_service is not None
            }
        }
        
        # Check each service if available
        if self.popularity_service:
            try:
                if hasattr(self.popularity_service, 'get_health_status'):
                    health = self.popularity_service.get_health_status()
                    status["services"]["popularity_health"] = health.get("status", "unknown")
                else:
                    status["services"]["popularity_health"] = "healthy"
            except:
                status["services"]["popularity_health"] = "error"
        
        if self.content_service:
            try:
                if hasattr(self.content_service, 'get_health_status'):
                    health = self.content_service.get_health_status()
                    status["services"]["content_health"] = health.get("status", "unknown")
                else:
                    status["services"]["content_health"] = "healthy"
            except:
                status["services"]["content_health"] = "error"
        
        if self.collaborative_service:
            try:
                if hasattr(self.collaborative_service, 'health_check'):
                    health = self.collaborative_service.health_check()
                    status["services"]["collaborative_health"] = health.get("status", "unknown")
                else:
                    status["services"]["collaborative_health"] = "healthy"
            except:
                status["services"]["collaborative_health"] = "error"
        
        all_healthy = all([
            status["services"]["popularity"],
            status["services"]["content"],
            status["services"]["collaborative"]
        ])
        
        if not all_healthy:
            status["status"] = "degraded"
            status["missing_services"] = [
                service for service, loaded in status["services"].items() 
                if not loaded and not service.endswith("_health")
            ]
        
        return status

    # ----------------------------------------------------
    # REFRESH
    # ----------------------------------------------------

    def refresh(self) -> bool:
        """
        Refresh all underlying services.
        
        Returns:
        --------
        bool: True if successful
        """
        self.clear_cache()
        self._request_count = 0
        
        try:
            if self.popularity_service:
                self.popularity_service.refresh_model()
            if self.content_service:
                self.content_service.refresh()
            if self.collaborative_service:
                self.collaborative_service.refresh()
            
            self._service_stats = {
                "popularity": self.popularity_service.recommender.is_fitted if self.popularity_service else False,
                "content": self.content_service.recommender is not None if self.content_service else False,
                "collaborative": self.collaborative_service._is_loaded if self.collaborative_service else False
            }
            
            logger.info("Hybrid recommender refreshed")
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing hybrid recommender: {e}")
            return False

    # ----------------------------------------------------
    # REPRESENTATION
    # ----------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"HybridRecommender("
            f"collab={self.collaborative_weight:.2f}, "
            f"content={self.content_weight:.2f}, "
            f"pop={self.popularity_weight:.2f})"
        )


# =====================================================
# SINGLETON INSTANCE
# =====================================================

_hybrid_recommender = None


def get_hybrid_recommender() -> HybridRecommender:
    """
    Get or create the singleton HybridRecommender instance.
    
    Returns:
    --------
    HybridRecommender: The singleton instance
    """
    global _hybrid_recommender
    if _hybrid_recommender is None:
        _hybrid_recommender = HybridRecommender()
    return _hybrid_recommender


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
    hybrid = get_hybrid_recommender()
    return hybrid.recommend_for_user(user_id, top_k, **kwargs)


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
    hybrid = get_hybrid_recommender()
    return hybrid.recommend_similar_books(isbn, top_k, **kwargs)