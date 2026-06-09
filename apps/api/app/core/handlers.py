# pyrefly: ignore [missing-import]
from fastapi import Request
# pyrefly: ignore [missing-import]
from fastapi.responses import JSONResponse

from app.core.exceptions import APIException

async def api_exception_handler(
    request: Request,
    exc: APIException
) -> JSONResponse:
    """Handle APIException and return formatted JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "errors": []
        }
    )