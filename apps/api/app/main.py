"""
Book Recommendation System API

A FastAPI application for book recommendations using hybrid recommender system.
Supports personalized recommendations, similar books, semantic search, and trending books.

Phase: API Entry Point
"""

import sys
from pathlib import Path

# Add the parent directory (apps/api) to Python path
# This allows importing from the ml folder
api_dir = Path(__file__).resolve().parents[1]  # Go up 1 level from app to api
sys.path.insert(0, str(api_dir))

from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import logging
import time
from datetime import datetime
from typing import Dict, Any

# Import routes - Recommendation routes
from app.api.v1.recommendation.routes import router as recommendation_router

# Import health routes
from app.api.v1.health.routes import health_router

# Import auth routes
from app.api.v1.auth.routes import router as auth_router
#import author router
from app.api.v1.authors.routes import router as author_router

from app.api.v1.onboarding.routes import router as onboarding_router

# Import service registry - now working because we added api_dir to path
from ml.service_registry import get_service_registry

# Import monitoring services
from app.services.monitoring import (
    MonitoringService,
    MonitoringMiddleware,
    get_monitoring_service,
    log_recommendation,
    log_api_request,
    get_metrics as get_monitoring_metrics
)
from app.services.recommendation_metrics import (
    get_metrics as get_prometheus_metrics,
    record_recommendation,
    record_request,
    update_service_status,
    track_request,
    track_recommendation
)
from app.services.recommendation_monitor import (
    RecommendationMonitor,
    get_monitor,
    get_monitor_dependency
)

# Import artifact validator
from app.core.artifact_validator import (
    ArtifactValidator,
    ValidationResult,
    validate_artifacts,
    get_artifact_status
    
)

# Import settings
from app.core.config import settings

# Set up logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================
# LIFESPAN CONTEXT MANAGER
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    This replaces the deprecated on_event handlers with the new lifespan API.
    """
    # --- STARTUP ---
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)
    logger.info(f"📖 Environment: {settings.ENVIRONMENT}")
    logger.info(f"📚 Docs: http://localhost:8000/docs")
    logger.info(f"📖 Redoc: http://localhost:8000/redoc")
    logger.info("=" * 60)
    
    # Initialize monitoring
    logger.info("📊 Initializing monitoring services...")
    try:
        # Initialize monitoring service
        monitoring_service = get_monitoring_service()
        app.state.monitoring_service = monitoring_service
        
        # Initialize recommendation monitor
        monitor = get_monitor()
        app.state.recommendation_monitor = monitor
        
        # Update service status
        update_service_status("healthy")
        
        logger.info("✅ Monitoring services initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize monitoring: {e}")
    
    # Validate artifacts
    # Validate artifacts
# Validate artifacts
    try:
        logger.info("🔍 Validating ML artifacts...")
        validation_result = validate_artifacts(raise_on_missing=False)
        
        if validation_result.all_present:
            logger.info("✅ All ML artifacts are present!")
            # Log artifact details
            artifacts = validation_result.artifacts
            if artifacts:
                logger.info(f"   Found {len(artifacts)} artifacts")
                for name, path in list(artifacts.items())[:5]:  # Show first 5
                    logger.debug(f"   📁 {name}: {path}")
                if len(artifacts) > 5:
                    logger.debug(f"   ... and {len(artifacts) - 5} more")
        else:
            missing = validation_result.missing_files
            if missing:
                logger.warning(f"⚠️ Missing {len(missing)} ML artifacts:")
                for artifact in missing[:10]:  # Show first 10 missing
                    logger.warning(f"   ❌ {artifact}")
                if len(missing) > 10:
                    logger.warning(f"   ... and {len(missing) - 10} more")

            logger.info("💡 Generate missing artifacts by running:")
            logger.info("   python apps/api/ml/collaborative/train_collaborative.py")
            logger.info("   python apps/api/ml/features/embedding_pipeline.py")
            logger.info("   python apps/api/ml/train_popularity.py")
        
        errors = validation_result.errors
        if errors:
            for error in errors:
                logger.error(f"   ❌ Error: {error}")
                
        warnings = validation_result.warnings
        if warnings:
            for warning in warnings[:5]:
                logger.warning(f"   ⚠️ Warning: {warning}")
                
    except Exception as e:
            logger.error(f"❌ Artifact validation error: {e}")
            logger.info("💡 Continuing with lazy loading - services will load when needed")
    
    # Initialize service registry with lazy loading
    try:
        logger.info("🔄 Initializing ML Service Registry...")
        start_time = time.time()
        
        # Get registry (loads on first access)
        registry = get_service_registry(load_on_init=False)
        
        elapsed = time.time() - start_time
        logger.info(f"✅ ML Service Registry initialized in {elapsed:.2f}s")
        
        # Store registry in app state for easy access
        app.state.registry = registry
        
        # Log service availability
        health = registry.health()
        logger.info("📊 Service Status:")
        for service_name, status in health['services'].items():
            logger.info(f"   {service_name}: {'✅ Available' if status['loaded'] else '⏳ Lazy Load'}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize service registry: {e}")
        # Don't crash the app - services will load on first request
    
    # Update service status
    update_service_status("healthy")
    
    logger.info("=" * 60)
    logger.info("✅ API READY")
    logger.info("=" * 60)
    
    # --- YIELD (App runs here) ---
    yield
    
    # --- SHUTDOWN ---
    logger.info("=" * 60)
    logger.info(f"🛑 Shutting down {settings.APP_NAME}")
    logger.info("=" * 60)
    
    # Update service status
    update_service_status("unhealthy")
    
    # Cleanup resources if needed
    try:
        if hasattr(app.state, 'registry'):
            logger.info("Cleaning up service registry...")
            logger.info("✅ Cleanup complete")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")
    
    # Flush monitoring logs
    try:
        if hasattr(app.state, 'monitoring_service'):
            app.state.monitoring_service.flush_logs()
            logger.info("✅ Monitoring logs flushed")
    except Exception as e:
        logger.error(f"❌ Error flushing monitoring logs: {e}")


# ============================================================
# CREATE FASTAPI APP WITH LIFESPAN
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    description="""
    A comprehensive book recommendation API powered by a hybrid recommender system.
    
    ## Features
    
    - **User Authentication**: Register, login, token refresh, password reset
    - **Personalized Recommendations**: Get book recommendations tailored to users
    - **Similar Books**: Find books similar to a given ISBN
    - **Semantic Search**: Search books using natural language queries
    - **Trending Books**: Get popular and trending books
    - **Hybrid Recommendations**: Combines collaborative, content-based, and popularity signals
    - **Health Monitoring**: Check API and service health status
    - **Performance Metrics**: Real-time monitoring of system performance
    
    ## Authentication
    
    - **Register**: Create a new user account
    - **Login**: Authenticate and get access token
    - **Refresh**: Refresh access token
    - **Password Reset**: Request and confirm password reset
    - **Email Verification**: Verify email address
    
    ## Recommender Types
    
    - **Hybrid**: Combines collaborative, content, and popularity (recommended)
    - **Popularity**: Most popular books
    - **Content**: Books with similar content
    - **Collaborative**: User-based collaborative filtering
    
    ## Monitoring Endpoints
    
    - **/metrics**: Prometheus metrics
    - **/monitor/metrics**: Real-time performance metrics
    - **/monitor/summary**: Human-readable status summary
    
    ## Health Endpoints
    
    - **Liveness**: Check if the API is running
    - **Readiness**: Check if all services are ready
    - **Detailed Health**: Get detailed service health information
    
    ## Response Formats
    
    All endpoints return JSON responses with consistent structure including:
    - Success responses with requested data
    - Error responses with status codes and messages
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Store settings in app state
app.state.settings = settings


# ============================================================
# MIDDLEWARE
# ============================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# Monitoring Middleware - Auto tracks all requests
app.add_middleware(MonitoringMiddleware)

# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all incoming requests and their processing time.
    """
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    duration_ms = process_time * 1000
    
    logger.info(
        f"Response: {response.status_code} - "
        f"Duration: {process_time:.4f}s - "
        f"Path: {request.url.path}"
    )
    
    # Record metrics
    try:
        record_request(
            endpoint=request.url.path,
            method=request.method,
            duration=process_time,
            status_code=response.status_code
        )
        
        # Log to monitoring service
        log_api_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
    except Exception as e:
        logger.error(f"Error recording metrics: {e}")
    
    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if app.debug else "An unexpected error occurred",
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================
# ROUTES
# ============================================================

# Include authentication routes
app.include_router(
    auth_router,
    prefix=settings.API_V1_PREFIX,
    tags=["Authentication"]
)

# Include recommendation routes with version prefix
app.include_router(
    recommendation_router,
    prefix=settings.API_V1_PREFIX,
    tags=["Recommendations"]
)

# Include health routes with version prefix
app.include_router(
    health_router,
    prefix=settings.API_V1_PREFIX,
    tags=["Health"]
)

app.include_router(
    onboarding_router,
    prefix="/api/v1/onboarding",
    tags=["Onboarding"],
)

app.include_router(
    author_router,
    prefix="/api/v1",
    tags=["Authors"]
)


# ============================================================
# VERSION ENDPOINT
# ============================================================

@app.get(
    "/version",
    tags=["Info"],
    summary="Get API version",
    description="Get the current version of the API"
)
async def get_version() -> Dict[str, Any]:
    """
    Get the current version of the API.
    
    Returns:
    --------
    Dict[str, Any]: Version information
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "timestamp": datetime.now().isoformat()
    }


@app.get(
    "/artifacts",
    tags=["Info"],
    summary="Get artifact status",
    description="Get the status of all ML artifacts"
)
async def get_artifacts_status() -> Dict[str, Any]:
    """
    Get the status of all ML artifacts.
    
    Returns:
    --------
    Dict[str, Any]: Artifact status information
    """
    validator = ArtifactValidator()
    return validator.get_status()


# ============================================================
# ROOT ENDPOINTS
# ============================================================

@app.get(
    "/",
    tags=["Root"],
    summary="Root endpoint",
    description="Welcome endpoint for the Book Recommendation System API"
)
async def root() -> Dict[str, Any]:
    """
    Root endpoint providing API information.
    
    Returns:
    --------
    Dict[str, Any]: API information and links
    """
    # Get registry status if available
    registry_status = "unknown"
    if hasattr(app.state, 'registry'):
        health = app.state.registry.health()
        registry_status = "ready" if health['loaded'] else "initializing"
    
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": registry_status,
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "health": f"{settings.API_V1_PREFIX}/health",
            "version": "/version",
            "artifacts": "/artifacts",
            "metrics": "/metrics",
            "monitor": {
                "metrics": "/monitor/metrics",
                "summary": "/monitor/summary"
            },
            "auth": {
                "register": f"{settings.API_V1_PREFIX}/auth/register",
                "login": f"{settings.API_V1_PREFIX}/auth/login",
                "refresh": f"{settings.API_V1_PREFIX}/auth/refresh",
                "me": f"{settings.API_V1_PREFIX}/auth/me",
                "logout": f"{settings.API_V1_PREFIX}/auth/logout",
                "password-reset": f"{settings.API_V1_PREFIX}/auth/password-reset",
                "verify-email": f"{settings.API_V1_PREFIX}/auth/verify-email"
            },
            "recommendations": {
                "user": f"{settings.API_V1_PREFIX}/recommendation/user",
                "similar": f"{settings.API_V1_PREFIX}/recommendation/similar",
                "search": f"{settings.API_V1_PREFIX}/recommendation/search",
                "trending": f"{settings.API_V1_PREFIX}/recommendation/trending",
                "stats": f"{settings.API_V1_PREFIX}/recommendation/stats",
                "health": f"{settings.API_V1_PREFIX}/recommendation/health"
            },
            "health": {
                "liveness": f"{settings.API_V1_PREFIX}/health/liveness",
                "readiness": f"{settings.API_V1_PREFIX}/health/readiness",
                "details": f"{settings.API_V1_PREFIX}/health/details"
            }
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Check if the API is running and healthy"
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the API.
    
    Returns:
    --------
    Dict[str, Any]: Health status information
    """
    service_status = {}
    
    # Check registry status
    if hasattr(app.state, 'registry'):
        health = app.state.registry.health()
        service_status = {
            "registry": {
                "loaded": health['loaded'],
                "services": {
                    name: {
                        "loaded": status['loaded'],
                        "health": status['health']
                    }
                    for name, status in health['services'].items()
                }
            }
        }
    
    # Check monitoring status
    monitoring_status = {}
    if hasattr(app.state, 'monitoring_service'):
        monitoring_status = app.state.monitoring_service.get_health_status()
    
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "service": "book-recommendation-api",
        "services": service_status,
        "monitoring": monitoring_status
    }


@app.get(
    "/info",
    tags=["Info"],
    summary="API information",
    description="Get detailed information about the API"
)
async def get_info() -> Dict[str, Any]:
    """
    Get detailed information about the API including available routes.
    
    Returns:
    --------
    Dict[str, Any]: API information
    """
    routes = []
    for route in app.routes:
        if hasattr(route, "methods"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": route.name,
            })
    
    # Get registry stats
    registry_stats = {}
    if hasattr(app.state, 'registry'):
        try:
            registry_stats = app.state.registry.get_stats()
        except Exception as e:
            registry_stats = {"error": str(e)}
    
    # Get monitoring metrics
    monitor_metrics = {}
    if hasattr(app.state, 'recommendation_monitor'):
        try:
            monitor_metrics = app.state.recommendation_monitor.get_metrics()
        except Exception as e:
            monitor_metrics = {"error": str(e)}
    
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "description": "Hybrid book recommendation system",
        "routes": routes,
        "total_routes": len(routes),
        "registry": registry_stats,
        "monitoring": monitor_metrics,
        "timestamp": datetime.now().isoformat()
    }


# ============================================================
# MONITORING ENDPOINTS
# ============================================================

@app.get(
    "/metrics",
    tags=["Monitoring"],
    summary="Prometheus metrics",
    description="Get Prometheus-formatted metrics for scraping"
)
async def prometheus_metrics():
    """
    Get Prometheus metrics.
    
    Returns:
    --------
    Response: Prometheus metrics in text format
    """
    return Response(
        content=get_prometheus_metrics(),
        media_type="text/plain"
    )


@app.get(
    "/monitor/metrics",
    tags=["Monitoring"],
    summary="Real-time metrics",
    description="Get real-time performance metrics"
)
async def get_monitor_metrics(
    monitor: RecommendationMonitor = Depends(get_monitor_dependency)
) -> Dict[str, Any]:
    """
    Get real-time recommendation metrics.
    
    Returns:
    --------
    Dict[str, Any]: Real-time metrics
    """
    return monitor.get_metrics()


@app.get(
    "/monitor/summary",
    tags=["Monitoring"],
    summary="Monitor summary",
    description="Get human-readable monitor summary"
)
async def get_monitor_summary(
    monitor: RecommendationMonitor = Depends(get_monitor_dependency)
) -> Dict[str, Any]:
    """
    Get human-readable monitor summary.
    
    Returns:
    --------
    Dict[str, Any]: Monitor summary
    """
    return {
        "summary": monitor.get_summary(),
        "timestamp": datetime.now().isoformat()
    }


@app.get(
    "/monitor/alerts",
    tags=["Monitoring"],
    summary="Get alerts",
    description="Get recent alerts from the monitor"
)
async def get_monitor_alerts(
    monitor: RecommendationMonitor = Depends(get_monitor_dependency)
) -> Dict[str, Any]:
    """
    Get recent alerts from the monitor.
    
    Returns:
    --------
    Dict[str, Any]: Recent alerts
    """
    return {
        "alerts": monitor.get_alerts(),
        "count": len(monitor.get_alerts()),
        "timestamp": datetime.now().isoformat()
    }


@app.delete(
    "/monitor/alerts",
    tags=["Monitoring"],
    summary="Clear alerts",
    description="Clear all alerts"
)
async def clear_monitor_alerts(
    monitor: RecommendationMonitor = Depends(get_monitor_dependency)
) -> Dict[str, Any]:
    """
    Clear all alerts.
    
    Returns:
    --------
    Dict[str, Any]: Clear status
    """
    monitor.clear_alerts()
    return {
        "status": "success",
        "message": "Alerts cleared",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================
# ADMIN ENDPOINTS
# ============================================================

@app.post(
    "/admin/reload",
    tags=["Admin"],
    summary="Reload all services",
    description="Reload all ML services (admin only)"
)
async def reload_services() -> Dict[str, Any]:
    """
    Reload all ML services.
    
    Returns:
    --------
    Dict[str, Any]: Reload status
    """
    if not hasattr(app.state, 'registry'):
        return {
            "status": "error",
            "message": "Registry not available"
        }
    
    try:
        success = app.state.registry.reload()
        return {
            "status": "success" if success else "partial",
            "message": "Services reloaded" if success else "Some services failed to reload",
            "health": app.state.registry.health()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.get(
    "/admin/registry",
    tags=["Admin"],
    summary="Registry status",
    description="Get detailed registry status (admin only)"
)
async def get_registry_status() -> Dict[str, Any]:
    """
    Get detailed registry status.
    
    Returns:
    --------
    Dict[str, Any]: Registry status
    """
    if not hasattr(app.state, 'registry'):
        return {
            "status": "error",
            "message": "Registry not available"
        }
    
    return {
        "status": "success",
        "registry": app.state.registry.health()
    }


# ============================================================
# CUSTOM OPENAPI
# ============================================================

def custom_openapi():
    """
    Custom OpenAPI schema generation.
    Adds additional metadata and examples.
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom metadata
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    # Add contact information
    openapi_schema["info"]["contact"] = {
        "name": "Book Recommendation System Team",
        "email": "support@bookrec.com",
        "url": "https://github.com/book-recommendation-system"
    }
    
    # Add license
    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    # Add tags
    openapi_schema["tags"] = [
        {
            "name": "Authentication",
            "description": "User authentication and management endpoints"
        },
        {
            "name": "Recommendations",
            "description": "Recommendation endpoints for users and books"
        },
        {
            "name": "Health",
            "description": "Health check and monitoring endpoints"
        },
        {
            "name": "Root",
            "description": "Root and informational endpoints"
        },
        {
            "name": "Info",
            "description": "API information endpoints"
        },
        {
            "name": "Admin",
            "description": "Administrative endpoints for service management"
        },
        {
            "name": "Monitoring",
            "description": "Monitoring and metrics endpoints"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

import logging
logging.basicConfig(level=logging.DEBUG)


# ============================================================
# DEVELOPMENT SERVER (Optional)
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )