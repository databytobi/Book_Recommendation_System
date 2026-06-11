import logging
import time
import uuid
from typing import Callable

# pyrefly: ignore [missing-import]
from starlette.middleware.base import BaseHTTPMiddleware

# pyrefly: ignore [missing-import]
from starlette.requests import Request

# pyrefly: ignore [missing-import]
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request details with unique request ID."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]

        # Add request ID to request state
        request.state.request_id = request_id

        start_time = time.time()

        # Log request start
        logger.info(f"[{request_id}] START {request.method} {request.url.path}")

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log request completion
            logger.info(
                f"[{request_id}] END {request.method} {request.url.path} "
                f"status={response.status_code} "
                f"duration={duration:.4f}s"
            )

            # Add request ID to response headers for debugging
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"[{request_id}] ERROR {request.method} {request.url.path} "
                f"duration={duration:.4f}s "
                f"error={str(e)}"
            )
            raise
