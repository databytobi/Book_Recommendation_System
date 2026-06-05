# pyrefly: ignore [missing-import]
from fastapi import FastAPI
from apps.api.app.v1.health.routes import router as health_router

app = FastAPI(
    title="Book Recommendation System API",
    version="1.0.0",
    description="Hybrid Book Recommendation Platform API"
)

@app.get("/")
async def root():
    return {
        "message": "Book Recommendation System API"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }