"""
Health Check Routes

Provides health check endpoints for the API, including liveness, readiness,
and detailed health checks for all services.

Phase: API Health Endpoints

"""
"""
Health Check Routes

Provides health check endpoints for the API, including liveness, readiness,
and detailed health checks for all services.

Phase: API Health Endpoints
"""

import sys
from pathlib import Path

# Add the parent directory to path for imports
api_dir = Path(__file__).resolve().parents[4]  # Go up to apps/api
sys.path.insert(0, str(api_dir))

import time
import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import JSONResponse
from datetime import datetime

# Import service registry for ML service health
from ml.service_registry import get_service_registry

logger = logging.getLogger(__name__)

# Create router with prefix
health_router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

# ... rest of the file remains the same ...

import logging
from fastapi import APIRouter

# Import service registry for ML service health
import sys
from pathlib import Path

# Add the parent directory to path for imports
api_dir = Path(__file__).resolve().parents[4]  # Go up to apps/api
sys.path.insert(0, str(api_dir))


logger = logging.getLogger(__name__)

# Create router with prefix
health_router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


# ============================================================
# HEALTH CHECK FUNCTIONS
# ============================================================

def check_database() -> Dict[str, Any]:
    """
    Check database connection health.
    
    Returns:
    --------
    Dict[str, Any]: Database health status
    """
    db_status = "connected"
    db_response_time = None
    db_error = None
    
    try:
        # Try to import database modules
        from app.core.database import SessionLocal
        from sqlalchemy import text
        from sqlalchemy.exc import SQLAlchemyError
        
        db_start = time.time()
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        db_response_time = round((time.time() - db_start) * 1000, 2)
        if db_response_time == 0.0:
            db_response_time = 0.01
        logger.debug("Database connection successful")
    except ImportError:
        # Database not configured - return unknown status
        db_status = "unknown"
        logger.warning("Database not configured")
    except Exception as e:
        db_status = "disconnected"
        db_error = str(e)
        logger.error(f"Database connection failed: {db_error}")
    
    return {
        "status": db_status,
        "response_time_ms": db_response_time,
        "error": db_error
    }


def check_redis() -> Dict[str, Any]:
    """
    Check Redis connection health.
    
    Returns:
    --------
    Dict[str, Any]: Redis health status
    """
    redis_status = "connected"
    redis_response_time = None
    redis_error = None
    
    try:
        # Try to import redis modules
        from app.core.redis import redis_client
        from redis import RedisError
        
        redis_start = time.time()
        redis_client.ping()
        redis_response_time = round((time.time() - redis_start) * 1000, 2)
        if redis_response_time == 0.0:
            redis_response_time = 0.01
        logger.debug("Redis connection successful")
    except ImportError:
        # Redis not configured - return unknown status
        redis_status = "unknown"
        logger.warning("Redis not configured")
    except Exception as e:
        redis_status = "disconnected"
        redis_error = str(e)
        logger.error(f"Redis connection failed: {redis_error}")
    
    return {
        "status": redis_status,
        "response_time_ms": redis_response_time,
        "error": redis_error
    }


def check_ml_services() -> Dict[str, Any]:
    """
    Check ML services health.
    
    Returns:
    --------
    Dict[str, Any]: ML services health status
    """
    try:
        registry = get_service_registry(load_on_init=False)
        health = registry.health()
        
        return {
            "status": "healthy" if health['loaded'] else "degraded",
            "loaded": health['loaded'],
            "services": health['services'],
            "errors": health['errors'] if health['errors'] else None
        }
    except Exception as e:
        logger.error(f"ML services health check failed: {e}")
        return {
            "status": "unknown",
            "error": str(e)
        }


# ============================================================
# HEALTH ENDPOINTS
# ============================================================

@health_router.get(
    "/liveness",
    summary="Liveness probe",
    description="Check if the API is running and responsive"
)
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness probe endpoint.
    
    Returns:
    --------
    Dict[str, Any]: Liveness status
    """
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "service": "book-recommendation-api"
    }


@health_router.get(
    "/readiness",
    summary="Readiness probe",
    description="Check if the API is ready to serve requests"
)
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness probe endpoint.
    
    Returns:
    --------
    Dict[str, Any]: Readiness status
    """
    # Check database and redis health
    db_health = check_database()
    redis_health = check_redis()
    ml_health = check_ml_services()
    
    # Determine overall readiness
    is_ready = (
        db_health.get("status") in ["connected", "unknown"] and
        redis_health.get("status") in ["connected", "unknown"]
    )
    
    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not_ready",
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "database": db_health,
                "redis": redis_health,
                "ml_services": ml_health
            }
        }
    )


@health_router.get(
    "/details",
    summary="Detailed health",
    description="Get detailed health information including response times"
)
async def detailed_health_check(request: Request) -> Dict[str, Any]:
    """
    Detailed health check endpoint.
    
    Returns:
    --------
    Dict[str, Any]: Detailed health status
    """
    start_time = time.time()
    
    # Check all services
    db_health = check_database()
    redis_health = check_redis()
    ml_health = check_ml_services()
    
    # Determine overall status
    all_healthy = (
        db_health.get("status") in ["connected", "unknown"] and
        redis_health.get("status") in ["connected", "unknown"]
    )
    
    overall_status = "healthy" if all_healthy else "degraded"
    total_response_time = round((time.time() - start_time) * 1000, 2)
    if total_response_time == 0.0:
        total_response_time = 0.01
    
    return {
        "status": overall_status,
        "timestamp": time.time(),
        "response_time_ms": total_response_time,
        "services": {
            "database": {
                "status": db_health.get("status"),
                "response_time_ms": db_health.get("response_time_ms"),
                "error": db_health.get("error")
            },
            "redis": {
                "status": redis_health.get("status"),
                "response_time_ms": redis_health.get("response_time_ms"),
                "error": redis_health.get("error")
            },
            "ml_services": {
                "status": ml_health.get("status"),
                "loaded": ml_health.get("loaded", False),
                "services": ml_health.get("services", {}),
                "errors": ml_health.get("errors")
            }
        },
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }


@health_router.get(
    "/ml",
    summary="ML Services health",
    description="Check the health of all ML services"
)
async def ml_services_health() -> Dict[str, Any]:
    """
    ML services health check endpoint.
    
    Returns:
    --------
    Dict[str, Any]: ML services health status
    """
    try:
        registry = get_service_registry(load_on_init=False)
        health = registry.health()
        
        return {
            "status": "healthy" if health['loaded'] else "degraded",
            "loaded": health['loaded'],
            "load_duration": health.get('load_duration'),
            "load_attempts": health.get('load_attempts', 0),
            "services": {
                name: {
                    "loaded": status.get('loaded', False),
                    "health": status.get('health', 'unknown'),
                    "error": status.get('error')
                }
                for name, status in health.get('services', {}).items()
            },
            "errors": health.get('errors', []),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"ML services health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# ============================================================
# LEGACY SUPPORT (for backward compatibility)
# ============================================================

# Alias for backward compatibility
router = health_router

# Keep the original health_check function for compatibility
async def health_check(request: Request):
    """
    Legacy health check endpoint.
    """
    return await detailed_health_check(request)


# Add the legacy route
health_router.get("/")(health_check)


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("HEALTH ROUTES TEST")
    print("=" * 60)
    
    # Test database check
    print("\n📊 Database Check:")
    db = check_database()
    for key, value in db.items():
        print(f"  {key}: {value}")
    
    # Test Redis check
    print("\n📊 Redis Check:")
    redis = check_redis()
    for key, value in redis.items():
        print(f"  {key}: {value}")
    
    # Test ML services check
    print("\n📊 ML Services Check:")
    ml = check_ml_services()
    for key, value in ml.items():
        if key == "services" and isinstance(value, dict):
            print(f"  {key}:")
            for name, status in value.items():
                print(f"    {name}: {status}")
        else:
            print(f"  {key}: {value}")
    
    print("\n✅ All tests completed!")