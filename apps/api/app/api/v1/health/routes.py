# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from app.core.redis import redis_client
from app.core.database import get_db

router = APIRouter()

@router.get("/")
async def health_check(db: Session = Depends(get_db)):
    # Check Redis status
    redis_status = "connected"
    try:
        redis_client.ping()
    except Exception:
        redis_status = "disconnected"
    
    # Check Database status
    db_status = "connected"
    try:
        # Try to execute a simple query
        db.execute("SELECT 1")
    except Exception:
        db_status = "disconnected"
    
    # Overall status
    overall_status = "healthy" if redis_status == "connected" and db_status == "connected" else "degraded"
    
    return {
        "status": overall_status,
        "services": {
            "redis": redis_status,
            "database": db_status
        },
        "timestamp": "2026-06-07T00:00:00Z"  # You can add actual timestamp here
    }