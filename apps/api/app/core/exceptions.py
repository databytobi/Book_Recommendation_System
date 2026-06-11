from typing import Optional, List


class APIException(Exception):
    """Base exception for API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        errors: Optional[List[str]] = None,
        error_code: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.errors = errors
        self.error_code = error_code
        super().__init__(message)


class NotFoundException(APIException):
    """Exception for 404 Not Found errors."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404, error_code="NOT_FOUND")


class ValidationException(APIException):
    """Exception for validation errors."""

    def __init__(
        self, message: str = "Validation error", errors: Optional[List[str]] = None
    ):
        super().__init__(
            message, status_code=422, errors=errors, error_code="VALIDATION_ERROR"
        )


class UnauthorizedException(APIException):
    """Exception for 401 Unauthorized errors."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401, error_code="UNAUTHORIZED")


class ForbiddenException(APIException):
    """Exception for 403 Forbidden errors."""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403, error_code="FORBIDDEN")
