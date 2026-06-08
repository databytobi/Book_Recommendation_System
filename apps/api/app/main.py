# pyrefly: ignore [missing-import]
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.health.routes import router as health_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Hybrid Book Recommendation Platform API"
)

# Include routers
app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])

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