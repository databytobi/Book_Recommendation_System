# pyrefly: ignore [missing-import]
from fastapi import Request

# pyrefly: ignore [missing-import]
from fastapi.responses import JSONResponse
from app.core.exceptions import APIException
import logging

logger = logging.getLogger(__name__)


async def api_exception_handler(request: Request, exc: APIException):
    """Handle custom API exceptions."""
    logger.error(f"API Exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "errors": exc.errors,
            "error_code": exc.error_code,
        },
    )


async def http_exception_handler(request: Request, exc):
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
        },
    )


async def validation_exception_handler(request: Request, exc):
    """Handle validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "errors": exc.errors(),
            "error_code": "VALIDATION_ERROR",
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_SERVER_ERROR",
        },
    )
