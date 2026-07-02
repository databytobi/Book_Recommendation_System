"""
Recommendation API Dependencies

This module provides dependency injection for FastAPI endpoints.
Includes lazy loading, health monitoring, and reload capabilities
for the hybrid recommender.

Phase: API Dependencies
"""

import logging
import time
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from functools import lru_cache
from contextlib import contextmanager
from fastapi import Depends, HTTPException, status

# Add the parent directory (apps/api) to path so we can import ml
# This file is at: apps/api/app/api/v1/recommendation/dependencies.py
# We need to go up to apps/api/
api_dir = Path(__file__).resolve().parents[4]  # Go up 4 levels: recommendation -> v1 -> api -> app -> api
sys.path.insert(0, str(api_dir))

# Now we can import from ml
from ml.hybrid.hybrid_recommender import HybridRecommender

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# RECOMMENDER MANAGER
# ============================================================

class RecommenderManager:
    """
    Singleton manager for the HybridRecommender instance.
    
    Features:
    - Lazy initialization
    - Health monitoring
    - Reload capabilities
    - Error handling
    - Statistics tracking
    """
    
    def __init__(self):
        """Initialize the manager."""
        self._instance: Optional[HybridRecommender] = None
        self._initialized: bool = False
        self._init_time: Optional[float] = None
        self._init_duration: Optional[float] = None
        self._health_status: str = "not_initialized"
        self._last_health_check: Optional[float] = None
        self._load_attempts: int = 0
        self._reload_count: int = 0
        self._error_count: int = 0
        
    @property
    def is_ready(self) -> bool:
        """Check if the recommender is ready."""
        return self._initialized and self._instance is not None
    
    @property
    def uptime_seconds(self) -> Optional[float]:
        """Get the uptime in seconds."""
        if self._init_time is None:
            return None
        return time.time() - self._init_time
    
    @property
    def health_status(self) -> str:
        """Get the current health status."""
        return self._health_status
    
    def _initialize(self) -> HybridRecommender:
        """
        Initialize the hybrid recommender.
        
        Returns:
        --------
        HybridRecommender: The initialized recommender instance
        
        Raises:
        --------
        RuntimeError: If initialization fails
        """
        self._load_attempts += 1
        
        try:
            logger.info("🔄 Initializing HybridRecommender...")
            start_time = time.time()
            
            self._instance = HybridRecommender()
            self._initialized = True
            self._init_time = time.time()
            self._init_duration = time.time() - start_time
            self._health_status = "healthy"
            self._error_count = 0
            
            logger.info(f"✅ HybridRecommender initialized in {self._init_duration:.2f}s")
            
            # Log recommender stats
            try:
                if hasattr(self._instance, 'get_stats'):
                    stats = self._instance.get_stats()
                    if stats and 'weights' in stats:
                        weights = stats['weights']
                        logger.info(f"   Weights: Collaborative={weights.get('collaborative', 0):.2f}, "
                                   f"Content={weights.get('content', 0):.2f}, "
                                   f"Popularity={weights.get('popularity', 0):.2f}")
            except Exception as e:
                logger.debug(f"Could not get recommender stats: {e}")
            
            return self._instance
            
        except Exception as e:
            self._health_status = "unhealthy"
            self._error_count += 1
            logger.error(f"❌ Failed to initialize HybridRecommender: {e}")
            raise RuntimeError(f"Failed to initialize HybridRecommender: {e}") from e
    
    def get_instance(self) -> HybridRecommender:
        """
        Get the singleton instance of the hybrid recommender.
        
        Returns:
        --------
        HybridRecommender: The recommender instance
        
        Raises:
        --------
        RuntimeError: If initialization fails
        """
        if not self.is_ready:
            self._initialize()
        
        if self._instance is None:
            raise RuntimeError("HybridRecommender instance is None after initialization")
        
        return self._instance
    
    def reload(self, force: bool = False) -> HybridRecommender:
        """
        Reload the hybrid recommender.
        
        Parameters:
        -----------
        force : bool
            Force reload even if healthy
        
        Returns:
        --------
        HybridRecommender: The new recommender instance
        """
        if self.is_ready and not force:
            logger.info("Recommender is already initialized and healthy. Use force=True to force reload.")
            return self._instance
        
        logger.info("🔄 Reloading HybridRecommender...")
        self._reload_count += 1
        
        # Clear the old instance
        if self._instance is not None:
            try:
                if hasattr(self._instance, 'clear_cache'):
                    self._instance.clear_cache()
                    logger.debug("Cache cleared from existing instance")
            except Exception as e:
                logger.warning(f"Error clearing cache: {e}")
        
        # Reset and reinitialize
        self._instance = None
        self._initialized = False
        self._init_time = None
        
        return self._initialize()
    
    def health_check(self, detailed: bool = False) -> Dict[str, Any]:
        """
        Perform a health check on the recommender.
        
        Parameters:
        -----------
        detailed : bool
            Whether to include detailed information
        
        Returns:
        --------
        Dict[str, Any]: Health status information
        """
        self._last_health_check = time.time()
        
        base_status = {
            "status": self._health_status,
            "ready": self.is_ready,
            "uptime_seconds": self.uptime_seconds,
            "last_check": self._last_health_check,
        }
        
        if not self.is_ready:
            return {
                **base_status,
                "message": "Recommender not initialized",
                "load_attempts": self._load_attempts,
                "error_count": self._error_count
            }
        
        try:
            # Perform detailed health check if available
            if detailed and hasattr(self._instance, 'health_check'):
                instance_health = self._instance.health_check()
                self._health_status = instance_health.get("status", "healthy")
                
                return {
                    **base_status,
                    "status": self._health_status,
                    "message": "Recommender is operational",
                    "load_attempts": self._load_attempts,
                    "reload_count": self._reload_count,
                    "error_count": self._error_count,
                    "init_duration": self._init_duration,
                    "details": instance_health
                }
            else:
                # Basic health check
                has_attributes = (
                    hasattr(self._instance, 'popularity_service') and
                    hasattr(self._instance, 'content_service') and
                    hasattr(self._instance, 'collaborative_service')
                )
                self._health_status = "healthy" if has_attributes else "degraded"
                
                return {
                    **base_status,
                    "status": self._health_status,
                    "message": "Recommender is operational" if has_attributes else "Recommender may have degraded functionality",
                    "load_attempts": self._load_attempts,
                    "reload_count": self._reload_count,
                    "error_count": self._error_count,
                    "init_duration": self._init_duration,
                    "has_services": has_attributes
                }
                
        except Exception as e:
            self._health_status = "error"
            return {
                **base_status,
                "status": "error",
                "message": f"Health check failed: {str(e)}",
                "error": str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics from the recommender.
        
        Returns:
        --------
        Dict[str, Any]: Statistics dictionary
        """
        if not self.is_ready:
            return {
                "status": "not_initialized",
                "ready": False,
                "load_attempts": self._load_attempts,
                "error_count": self._error_count
            }
        
        try:
            stats = {
                "status": self._health_status,
                "ready": True,
                "uptime_seconds": self.uptime_seconds,
                "init_duration_seconds": self._init_duration,
                "load_attempts": self._load_attempts,
                "reload_count": self._reload_count,
                "error_count": self._error_count,
                "last_health_check": self._last_health_check,
                "instance_type": type(self._instance).__name__
            }
            
            # Add recommender-specific stats
            if hasattr(self._instance, 'get_stats'):
                recommender_stats = self._instance.get_stats()
                if recommender_stats:
                    stats.update(recommender_stats)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "status": "error",
                "ready": True,
                "error": str(e)
            }
    
    def reset_error_count(self) -> None:
        """Reset the error counter."""
        self._error_count = 0
        logger.info("Error counter reset")


# ============================================================
# SINGLETON INSTANCE
# ============================================================

# Create a single manager instance
_manager = RecommenderManager()


# ============================================================
# DEPENDENCY FUNCTIONS
# ============================================================

def get_hybrid_recommender() -> HybridRecommender:
    """
    Get the singleton HybridRecommender instance.
    
    This function can be used as a FastAPI dependency.
    
    Returns:
    --------
    HybridRecommender: The singleton recommender instance
    
    Raises:
    --------
    HTTPException: If the recommender cannot be initialized
    """
    try:
        return _manager.get_instance()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Recommender service unavailable: {str(e)}"
        )


def get_health_status() -> Dict[str, Any]:
    """
    Get the health status of the recommender.
    
    Returns:
    --------
    Dict[str, Any]: Health status information
    """
    return _manager.health_check(detailed=True)


def get_recommender_stats() -> Dict[str, Any]:
    """
    Get statistics from the recommender.
    
    Returns:
    --------
    Dict[str, Any]: Statistics dictionary
    """
    return _manager.get_stats()


def reload_hybrid_recommender() -> HybridRecommender:
    """
    Reload the hybrid recommender.
    
    Returns:
    --------
    HybridRecommender: The new recommender instance
    
    Raises:
    --------
    HTTPException: If reload fails
    """
    try:
        return _manager.reload(force=True)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload recommender: {str(e)}"
        )


# ============================================================
# FASTAPI DEPENDENCY CLASS
# ============================================================

class RecommenderDependencies:
    """
    Dependency injection class for FastAPI routes.
    """
    
    def __init__(self):
        self._recommender: Optional[HybridRecommender] = None
    
    def get_recommender(self) -> HybridRecommender:
        """Get the recommender instance."""
        if self._recommender is None:
            self._recommender = get_hybrid_recommender()
        return self._recommender
    
    def get_stats(self) -> Dict[str, Any]:
        """Get recommender statistics."""
        return get_recommender_stats()
    
    def health_check(self) -> Dict[str, Any]:
        """Get recommender health status."""
        return get_health_status()


# ============================================================
# CONTEXT MANAGER
# ============================================================

@contextmanager
def recommender_context():
    """
    Context manager for working with the hybrid recommender.
    """
    recommender = get_hybrid_recommender()
    try:
        yield recommender
    except Exception as e:
        logger.error(f"Error in recommender context: {e}")
        raise
    finally:
        # No cleanup needed for singleton
        pass


# ============================================================
# CACHED INSTANCE (Alternative)
# ============================================================

@lru_cache(maxsize=1)
def get_cached_hybrid_recommender() -> HybridRecommender:
    """
    Get a cached HybridRecommender instance using LRU cache.
    
    This is an alternative to the singleton pattern that uses
    Python's built-in lru_cache for thread-safe singleton behavior.
    
    Returns:
    --------
    HybridRecommender: The cached recommender instance
    """
    return HybridRecommender()


# ============================================================
# ADMIN DEPENDENCIES
# ============================================================

def require_admin():
    """
    Dependency to require admin privileges.
    
    Returns:
    --------
    bool: True if user is admin
    
    Raises:
    --------
    HTTPException: If user is not admin
    """
    # In production, implement proper admin authentication
    # This is a placeholder
    return True


def admin_only():
    """
    Admin-only dependency for sensitive endpoints.
    
    Raises:
    --------
    HTTPException: If user is not admin
    """
    if not require_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return True


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("DEPENDENCIES TEST")
    print("=" * 60)
    
    # Test 1: Get recommender
    print("\n📌 Test 1: Get Recommender")
    try:
        recommender = get_hybrid_recommender()
        print(f"✅ Recommender loaded: {type(recommender).__name__}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Health check
    print("\n📌 Test 2: Health Check")
    health = get_health_status()
    for key, value in health.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    # Test 3: Statistics
    print("\n📌 Test 3: Statistics")
    stats = get_recommender_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            if "time" in key or "duration" in key:
                print(f"  {key}: {value:.2f}s")
            else:
                print(f"  {key}: {value:.4f}" if value < 1 else f"  {key}: {value:.2f}")
        elif isinstance(value, int):
            print(f"  {key}: {value:,}")
        else:
            print(f"  {key}: {value}")
    
    # Test 4: Context manager
    print("\n📌 Test 4: Context Manager")
    try:
        with recommender_context() as recommender:
            print(f"✅ Context manager works: {type(recommender).__name__}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✅ All tests completed!")