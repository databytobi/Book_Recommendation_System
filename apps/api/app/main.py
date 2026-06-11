from contextlib import asynccontextmanager

# pyrefly: ignore [missing-import]
from fastapi import FastAPI

# pyrefly: ignore [missing-import]
from fastapi.exceptions import RequestValidationError

# pyrefly: ignore [missing-import]
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.health.routes import router as health_router
from app.middleware.request_logging import RequestLoggingMiddleware
from app.core.logging import setup_logging
from app.core.exceptions import APIException
from app.core.handlers import (
    api_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=" * 50)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    logger.info("=" * 50)
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Hybrid Book Recommendation Platform API",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Register exception handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])

# Add middleware
app.add_middleware(RequestLoggingMiddleware)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Book Recommendation System API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
