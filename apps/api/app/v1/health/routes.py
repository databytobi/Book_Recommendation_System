# pyrefly: ignore [missing-import]
from fastapi import APIRouter


router = APIRouter()

@router.get("/")
async def health_check():
    return {
        "status": "healthy"
    }