"""
ML Service Registry

Central registry for all machine learning services in the recommendation system.
Provides lazy loading, health monitoring, statistics, and service management.

Phase: Service Registry
"""
import sys
from pathlib import Path

# Add the current directory to path for imports
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

import logging
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from contextlib import contextmanager

# FIXED: Import directly from the ml package (no app prefix)
# pyrefly: ignore [missing-import]
from ml.popularity.popularity_service import PopularityService
# pyrefly: ignore [missing-import]
from ml.content.content_service import ContentService
# pyrefly: ignore [missing-import]
from ml.collaborative.collaborative_service import CollaborativeService
# pyrefly: ignore [missing-import]
from ml.hybrid.hybrid_recommender import HybridRecommender

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ServiceStatus:
    """Status information for a service."""
    name: str
    loaded: bool
    load_time: Optional[float] = None
    error: Optional[str] = None
    health_status: str = "unknown"


class MLServiceRegistry:
    """
    Central registry for all ML services.
    
    Features:
    - Lazy loading (services load on first access)
    - Health monitoring
    - Service statistics
    - Reload capabilities
    - Error handling
    - Singleton pattern
    """
    
    def __init__(self, load_on_init: bool = False):
        """
        Initialize the service registry.
        
        Parameters:
        -----------
        load_on_init : bool
            Whether to load all services immediately on initialization
        """
        self._popularity: Optional[PopularityService] = None
        self._content: Optional[ContentService] = None
        self._collaborative: Optional[CollaborativeService] = None
        self._hybrid: Optional[HybridRecommender] = None
        
        self._loaded: bool = False
        self._load_start_time: Optional[float] = None
        self._load_end_time: Optional[float] = None
        self._load_attempts: int = 0
        self._reload_count: int = 0
        self._errors: List[str] = []
        
        # Service status tracking
        self._service_status: Dict[str, ServiceStatus] = {
            "popularity": ServiceStatus(name="popularity", loaded=False),
            "content": ServiceStatus(name="content", loaded=False),
            "collaborative": ServiceStatus(name="collaborative", loaded=False),
            "hybrid": ServiceStatus(name="hybrid", loaded=False),
        }
        
        if load_on_init:
            self.load_all()
        
        logger.info("MLServiceRegistry initialized")
    
    @property
    def is_loaded(self) -> bool:
        """Check if all services are loaded."""
        return self._loaded
    
    @property
    def load_duration(self) -> Optional[float]:
        """Get the duration of the last load operation in seconds."""
        if self._load_start_time is None or self._load_end_time is None:
            return None
        return self._load_end_time - self._load_start_time
    
    @property
    def popularity(self) -> Optional[PopularityService]:
        """Get the popularity service (lazy loaded)."""
        if self._popularity is None and not self._loaded:
            self.load_all()
        return self._popularity
    
    @property
    def content(self) -> Optional[ContentService]:
        """Get the content service (lazy loaded)."""
        if self._content is None and not self._loaded:
            self.load_all()
        return self._content
    
    @property
    def collaborative(self) -> Optional[CollaborativeService]:
        """Get the collaborative service (lazy loaded)."""
        if self._collaborative is None and not self._loaded:
            self.load_all()
        return self._collaborative
    
    @property
    def hybrid(self) -> Optional[HybridRecommender]:
        """Get the hybrid recommender (lazy loaded)."""
        if self._hybrid is None and not self._loaded:
            self.load_all()
        return self._hybrid
    
    def load_all(self, force_reload: bool = False) -> bool:
        """
        Load all ML services.
        
        Parameters:
        -----------
        force_reload : bool
            Whether to force reload even if already loaded
        
        Returns:
        --------
        bool: True if all services loaded successfully, False otherwise
        """
        if self._loaded and not force_reload:
            logger.info("Services already loaded. Use force_reload=True to reload.")
            return True
        
        self._load_attempts += 1
        self._errors = []
        self._load_start_time = time.time()
        
        logger.info("=" * 60)
        logger.info("LOADING ML SERVICES")
        logger.info("=" * 60)
        
        success = True
        
        # Load each service individually with error handling
        services = [
            ("popularity", self._load_popularity),
            ("content", self._load_content),
            ("collaborative", self._load_collaborative),
            ("hybrid", self._load_hybrid),
        ]
        
        for service_name, load_func in services:
            try:
                load_func()
                self._service_status[service_name].loaded = True
                self._service_status[service_name].health_status = "healthy"
                logger.info(f"✅ {service_name.capitalize()} service loaded")
            except Exception as e:
                success = False
                error_msg = f"Failed to load {service_name}: {str(e)}"
                self._errors.append(error_msg)
                self._service_status[service_name].loaded = False
                self._service_status[service_name].error = str(e)
                self._service_status[service_name].health_status = "unhealthy"
                logger.error(f"❌ {error_msg}")
        
        self._loaded = success
        self._load_end_time = time.time()
        
        if success:
            logger.info("=" * 60)
            logger.info("ALL ML SERVICES READY")
            logger.info(f"✅ Load time: {self.load_duration:.2f}s")
            logger.info("=" * 60)
        else:
            logger.warning("=" * 60)
            logger.warning("⚠️ SOME SERVICES FAILED TO LOAD")
            logger.warning(f"   Errors: {len(self._errors)}")
            logger.warning("=" * 60)
        
        return success
    
    def _load_popularity(self) -> None:
        """Load the popularity service."""
        self._popularity = PopularityService()
        self._service_status["popularity"].load_time = time.time()
    
    def _load_content(self) -> None:
        """Load the content service."""
        self._content = ContentService()
        self._service_status["content"].load_time = time.time()
    
    def _load_collaborative(self) -> None:
        """Load the collaborative service."""
        self._collaborative = CollaborativeService()
        self._service_status["collaborative"].load_time = time.time()
    
    def _load_hybrid(self) -> None:
        """Load the hybrid recommender."""
        self._hybrid = HybridRecommender()
        self._service_status["hybrid"].load_time = time.time()
    
    def reload(self) -> bool:
        """
        Reload all services.
        
        Returns:
        --------
        bool: True if reload successful
        """
        self._reload_count += 1
        logger.info(f"🔄 Reloading services (attempt {self._reload_count})")
        
        # Clear existing instances
        self._popularity = None
        self._content = None
        self._collaborative = None
        self._hybrid = None
        self._loaded = False
        
        return self.load_all(force_reload=True)
    
    def reload_service(self, service_name: str) -> bool:
        """
        Reload a specific service.
        
        Parameters:
        -----------
        service_name : str
            Name of the service to reload ('popularity', 'content', 'collaborative', 'hybrid')
        
        Returns:
        --------
        bool: True if reload successful
        """
        service_map = {
            "popularity": ("_popularity", self._load_popularity),
            "content": ("_content", self._load_content),
            "collaborative": ("_collaborative", self._load_collaborative),
            "hybrid": ("_hybrid", self._load_hybrid),
        }
        
        if service_name not in service_map:
            logger.error(f"Unknown service: {service_name}")
            return False
        
        attr_name, load_func = service_map[service_name]
        
        try:
            logger.info(f"🔄 Reloading {service_name} service...")
            
            # Clear existing instance
            setattr(self, attr_name, None)
            self._service_status[service_name].loaded = False
            
            # Reload
            load_func()
            self._service_status[service_name].loaded = True
            self._service_status[service_name].error = None
            self._service_status[service_name].health_status = "healthy"
            self._service_status[service_name].load_time = time.time()
            
            logger.info(f"✅ {service_name.capitalize()} service reloaded")
            return True
            
        except Exception as e:
            error_msg = f"Failed to reload {service_name}: {str(e)}"
            self._errors.append(error_msg)
            self._service_status[service_name].loaded = False
            self._service_status[service_name].error = str(e)
            self._service_status[service_name].health_status = "unhealthy"
            logger.error(f"❌ {error_msg}")
            return False
    
    def get_service(self, service_name: str):
        """
        Get a specific service by name.
        
        Parameters:
        -----------
        service_name : str
            Name of the service ('popularity', 'content', 'collaborative', 'hybrid')
        
        Returns:
        --------
        The requested service instance or None if not loaded
        """
        service_map = {
            "popularity": self.popularity,
            "content": self.content,
            "collaborative": self.collaborative,
            "hybrid": self.hybrid,
        }
        
        return service_map.get(service_name)
    
    def health(self) -> Dict[str, Any]:
        """
        Get health status of all services.
        
        Returns:
        --------
        Dict[str, Any]: Health information
        """
        return {
            "loaded": self._loaded,
            "load_duration": self.load_duration,
            "load_attempts": self._load_attempts,
            "reload_count": self._reload_count,
            "errors": self._errors,
            "services": {
                name: {
                    "loaded": status.loaded,
                    "health": status.health_status,
                    "error": status.error,
                    "load_time": status.load_time,
                }
                for name, status in self._service_status.items()
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get detailed statistics about all services.
        
        Returns:
        --------
        Dict[str, Any]: Statistics information
        """
        stats = {
            "registry": {
                "loaded": self._loaded,
                "load_duration": self.load_duration,
                "load_attempts": self._load_attempts,
                "reload_count": self._reload_count,
                "error_count": len(self._errors),
            },
            "services": {}
        }
        
        # Get service-specific stats
        service_stats = {
            "popularity": self._get_popularity_stats(),
            "content": self._get_content_stats(),
            "collaborative": self._get_collaborative_stats(),
            "hybrid": self._get_hybrid_stats(),
        }
        
        for name, service_stats in service_stats.items():
            stats["services"][name] = {
                "loaded": self._service_status[name].loaded,
                "health": self._service_status[name].health_status,
                "stats": service_stats
            }
        
        return stats
    
    def _get_popularity_stats(self) -> Dict[str, Any]:
        """Get popularity service statistics."""
        if self._popularity is None:
            return {"status": "not_loaded"}
        
        try:
            if hasattr(self._popularity, 'get_stats'):
                return self._popularity.get_stats()
            elif hasattr(self._popularity, 'stats'):
                return self._popularity.stats()
            return {"status": "available"}
        except Exception as e:
            return {"error": str(e)}
    
    def _get_content_stats(self) -> Dict[str, Any]:
        """Get content service statistics."""
        if self._content is None:
            return {"status": "not_loaded"}
        
        try:
            if hasattr(self._content, 'get_statistics'):
                return self._content.get_statistics()
            elif hasattr(self._content, 'stats'):
                return self._content.stats()
            return {"status": "available"}
        except Exception as e:
            return {"error": str(e)}
    
    def _get_collaborative_stats(self) -> Dict[str, Any]:
        """Get collaborative service statistics."""
        if self._collaborative is None:
            return {"status": "not_loaded"}
        
        try:
            if hasattr(self._collaborative, 'get_stats'):
                return self._collaborative.get_stats()
            return {"status": "available"}
        except Exception as e:
            return {"error": str(e)}
    
    def _get_hybrid_stats(self) -> Dict[str, Any]:
        """Get hybrid recommender statistics."""
        if self._hybrid is None:
            return {"status": "not_loaded"}
        
        try:
            if hasattr(self._hybrid, 'get_stats'):
                return self._hybrid.get_stats()
            return {"status": "available"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_service_health(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Get health status for a specific service.
        
        Parameters:
        -----------
        service_name : str
            Name of the service
        
        Returns:
        --------
        Optional[Dict[str, Any]]: Health information or None if service not found
        """
        if service_name not in self._service_status:
            return None
        
        status = self._service_status[service_name]
        
        return {
            "name": status.name,
            "loaded": status.loaded,
            "health": status.health_status,
            "error": status.error,
            "load_time": status.load_time,
        }
    
    def reset(self) -> None:
        """
        Reset the registry (clear all services and statistics).
        """
        logger.info("🔄 Resetting service registry...")
        
        self._popularity = None
        self._content = None
        self._collaborative = None
        self._hybrid = None
        self._loaded = False
        self._load_start_time = None
        self._load_end_time = None
        self._errors = []
        
        for status in self._service_status.values():
            status.loaded = False
            status.error = None
            status.health_status = "unknown"
        
        logger.info("✅ Registry reset")
    
    def __repr__(self) -> str:
        """String representation of the registry."""
        loaded_count = sum(1 for s in self._service_status.values() if s.loaded)
        total_count = len(self._service_status)
        return f"MLServiceRegistry(loaded={self._loaded}, services={loaded_count}/{total_count})"


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_registry: Optional[MLServiceRegistry] = None


def get_service_registry(load_on_init: bool = True) -> MLServiceRegistry:
    """
    Get or create the singleton MLServiceRegistry instance.
    
    Parameters:
    -----------
    load_on_init : bool
        Whether to load services immediately on initialization
    
    Returns:
    --------
    MLServiceRegistry: The singleton registry instance
    """
    global _registry
    if _registry is None:
        _registry = MLServiceRegistry(load_on_init=load_on_init)
    return _registry


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def get_hybrid_recommender() -> HybridRecommender:
    """
    Get the hybrid recommender from the registry.
    
    Returns:
    --------
    HybridRecommender: The hybrid recommender instance
    
    Raises:
    --------
    RuntimeError: If hybrid recommender is not available
    """
    registry = get_service_registry()
    recommender = registry.hybrid
    if recommender is None:
        raise RuntimeError("Hybrid recommender not available")
    return recommender


def get_popularity_service() -> PopularityService:
    """
    Get the popularity service from the registry.
    
    Returns:
    --------
    PopularityService: The popularity service instance
    
    Raises:
    --------
    RuntimeError: If popularity service is not available
    """
    registry = get_service_registry()
    service = registry.popularity
    if service is None:
        raise RuntimeError("Popularity service not available")
    return service


def get_content_service() -> ContentService:
    """
    Get the content service from the registry.
    
    Returns:
    --------
    ContentService: The content service instance
    
    Raises:
    --------
    RuntimeError: If content service is not available
    """
    registry = get_service_registry()
    service = registry.content
    if service is None:
        raise RuntimeError("Content service not available")
    return service


def get_collaborative_service() -> CollaborativeService:
    """
    Get the collaborative service from the registry.
    
    Returns:
    --------
    CollaborativeService: The collaborative service instance
    
    Raises:
    --------
    RuntimeError: If collaborative service is not available
    """
    registry = get_service_registry()
    service = registry.collaborative
    if service is None:
        raise RuntimeError("Collaborative service not available")
    return service


# ============================================================
# CONTEXT MANAGER
# ============================================================

@contextmanager
def service_context(service_name: str):
    """
    Context manager for using a specific service.
    
    Parameters:
    -----------
    service_name : str
        Name of the service to use
    
    Yields:
    --------
    The requested service instance
    
    Raises:
    --------
    ValueError: If service name is invalid
    """
    registry = get_service_registry()
    service = registry.get_service(service_name)
    
    if service is None:
        raise ValueError(f"Service '{service_name}' not available")
    
    try:
        yield service
    except Exception as e:
        logger.error(f"Error in service context ({service_name}): {e}")
        raise


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SERVICE REGISTRY TEST")
    print("=" * 60)
    
    # Get registry
    registry = get_service_registry()
    print(f"\n📋 Registry: {registry}")
    
    # Health check
    print("\n📊 Health Check:")
    health = registry.health()
    print(f"  Loaded: {health['loaded']}")
    print(f"  Load attempts: {health['load_attempts']}")
    print(f"  Errors: {len(health['errors'])}")
    print("\n  Services:")
    for name, status in health['services'].items():
        print(f"    {name}: loaded={status['loaded']}, health={status['health']}")
    
    # Statistics
    print("\n📊 Statistics:")
    stats = registry.get_stats()
    print(f"  Registry: {stats['registry']}")
    print("  Services:", len(stats['services']))
    
    print("\n✅ All tests completed!")