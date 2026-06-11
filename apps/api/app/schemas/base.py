from typing import Any, Optional, Generic, TypeVar

# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseAPIResponse(BaseModel):
    """Base response model for all API endpoints."""

    success: bool = Field(..., description="Indicates if the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(default=None, description="Response data payload")


class GenericAPIResponse(BaseModel, Generic[T]):
    """Generic response model with type-safe data field."""

    success: bool
    message: str
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    """Response model for error cases."""

    success: bool = Field(default=False, description="Always False for errors")
    message: str = Field(..., description="Error message")
    errors: Optional[list[str]] = Field(
        default=None, description="List of specific errors"
    )
    error_code: Optional[str] = Field(
        default=None, description="Error code for client handling"
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Response model for paginated data."""

    success: bool = True
    message: str = "Success"
    data: list[T]
    page: int
    page_size: int
    total_pages: int
    total_items: int


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str
    timestamp: float
    response_time_ms: float
    services: dict[str, Any]


class ValidationErrorResponse(ErrorResponse):
    """Response model for validation errors."""

    errors: list[str]
    validation_details: Optional[dict[str, list[str]]] = None
