from contextlib import asynccontextmanager
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.health.routes import router as health_router
from app.middleware.request_logging import RequestLoggingMiddleware
from app.core.logging import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application startup starting...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    yield
    # Shutdown
    logger.info("Application shutdown")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Hybrid Book Recommendation Platform API",
    lifespan=lifespan
)

# Include routers
app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])
app.add_middleware(RequestLoggingMiddleware)

@app.get("/")
async def root():
    return {
        "message": "Book Recommendation System API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }