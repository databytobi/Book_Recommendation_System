import time
import logging
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
# pyrefly: ignore [missing-import]
# pyrefly: ignore [missing-import]
from sqlalchemy import text
# pyrefly: ignore [missing-import]
from sqlalchemy.exc import SQLAlchemyError
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from redis import RedisError
from app.core.database import get_db
from app.core.redis import redis_client
from app.schemas.base import BaseAPIResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Health"]
)

@router.get("/")
async def health_check(db: Session = Depends(get_db)):
    start_time = time.time()
    
    # Check database connection
    db_status = "connected"
    db_response_time = None
    db_error = None
    try:
        db_start = time.time()
        db.execute(text("SELECT 1"))
        db_response_time = round((time.time() - db_start) * 1000, 2)
        logger.debug("Database connection successful")
    except SQLAlchemyError as error:
        db_status = "disconnected"
        db_error = str(error)
        logger.error(f"Database connection failed: {db_error}")
    
    # Check Redis connection
    redis_status = "connected"
    redis_response_time = None
    redis_error = None
    try:
        redis_start = time.time()
        redis_client.ping()
        redis_response_time = round((time.time() - redis_start) * 1000, 2)
        logger.debug("Redis connection successful")
    except RedisError as error:
        redis_status = "disconnected"
        redis_error = str(error)
        logger.error(f"Redis connection failed: {redis_error}")
    
    # Determine overall status and HTTP status code
    overall_status = "healthy" if db_status == "connected" and redis_status == "connected" else "degraded"
    total_response_time = round((time.time() - start_time) * 1000, 2)
    
    response = {
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
    
    # Include error details if in debug mode
    from app.core.config import settings
    if settings.DEBUG:
        if db_error:
            response["services"]["database"]["error"] = db_error
        if redis_error:
            response["services"]["redis"]["error"] = redis_error
    
    return response