# pyrefly: ignore [missing-import]
from fastapi import APIRouter
# pyrefly: ignore [missing-import]
from sqlalchemy import text
# pyrefly: ignore [missing-import]
from sqlalchemy.exc import SQLAlchemyError
import time
# pyrefly: ignore [missing-import]
from app.core.database import SessionLocal
from app.core.redis import redis_client
# pyrefly: ignore [missing-import]
from redis import RedisError

router = APIRouter()

@router.get("/")
async def health_check():
    start_time = time.time()
    
    # Check database connection
    db_status = "connected"
    db_response_time = None
    try:
        db_start = time.time()
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        db_response_time = round((time.time() - db_start) * 1000, 2)
    except SQLAlchemyError:
        db_status = "disconnected"
    
    # Check Redis connection
    redis_status = "connected"
    redis_response_time = None
    try:
        redis_start = time.time()
        redis_client.ping()
        redis_response_time = round((time.time() - redis_start) * 1000, 2)
    except RedisError:
        redis_status = "disconnected"
    
    # Determine overall status
    overall_status = "healthy" if db_status == "connected" and redis_status == "connected" else "degraded"
    total_response_time = round((time.time() - start_time) * 1000, 2)
    
    return {
        "status": overall_status,
        "timestamp": time.time(),
        "response_time_ms": total_response_time,
        "services": {
            "database": {
                "status": db_status,
                "response_time_ms": db_response_time
            },
            "redis": {
                "status": redis_status,
                "response_time_ms": redis_response_time
            }
        }
    }