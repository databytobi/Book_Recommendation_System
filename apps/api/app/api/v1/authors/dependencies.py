"""
Author Dependencies

Dependency injection for author-related services and components.
Provides reusable dependencies for author operations.

Phase: API Dependencies
"""

from typing import Optional, List
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.services.author_service import AuthorService
from app.services.author_discovery_service import AuthorDiscoveryService
from app.models.user import User
# pyrefly: ignore [missing-import]
from app.dependencies.auth import get_current_user

logger = logging.getLogger(__name__)


def get_author_service(
    db: Session = Depends(get_db),
) -> AuthorService:
    """Get an AuthorService instance."""
    return AuthorService(db)


def get_author_discovery_service(
    db: Session = Depends(get_db),
) -> AuthorDiscoveryService:
    """Get an AuthorDiscoveryService instance."""
    return AuthorDiscoveryService(db)


async def get_author_or_404(
    author_id: int,
    service: AuthorService = Depends(get_author_service),
):
    """Get an author by ID or raise 404 if not found."""
    author = service.get_author(author_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with ID {author_id} not found"
        )
    return author


async def get_active_author_or_404(
    author_id: int,
    service: AuthorService = Depends(get_author_service),
):
    """Get an active author by ID or raise 404 if not found or inactive."""
    author = service.get_author(author_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with ID {author_id} not found"
        )
    
    if not author.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with ID {author_id} is not active"
        )
    
    return author


async def get_authors_or_404(
    author_ids: str,
    service: AuthorService = Depends(get_author_service),
) -> List:
    """Get multiple authors by comma-separated IDs or raise 404 if any not found."""
    try:
        ids = [int(id.strip()) for id in author_ids.split(",") if id.strip()]
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid author IDs format. Use comma-separated integers."
        )
    
    if not ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one author ID is required"
        )
    
    authors = service.get_by_ids(ids)
    found_ids = {author.id for author in authors}
    missing_ids = set(ids) - found_ids
    
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Authors not found: {', '.join(map(str, missing_ids))}"
        )
    
    return authors


async def get_author_with_follow_permission(
    author_id: int,
    current_user: User = Depends(get_current_user),
    service: AuthorService = Depends(get_author_service),
):
    """Get an author and validate that the current user has permission to follow/unfollow."""
    return await get_active_author_or_404(author_id, service)


class PaginationParams:
    """Pagination parameters for list endpoints."""
    
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(50, ge=1, le=200, description="Maximum records to return"),
    ):
        self.skip = skip
        self.limit = limit


def get_pagination_params(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum records to return"),
) -> PaginationParams:
    """Get pagination parameters."""
    return PaginationParams(skip=skip, limit=limit)


class AuthorFilters:
    """Filter parameters for author listing endpoints."""
    
    def __init__(
        self,
        include_inactive: bool = Query(False, description="Include inactive authors"),
        min_popularity: Optional[float] = Query(None, ge=0, le=1, description="Minimum popularity score"),
        nationality: Optional[str] = Query(None, description="Filter by nationality"),
    ):
        self.include_inactive = include_inactive
        self.min_popularity = min_popularity
        self.nationality = nationality


def get_author_filters(
    include_inactive: bool = Query(False, description="Include inactive authors"),
    min_popularity: Optional[float] = Query(None, ge=0, le=1, description="Minimum popularity score"),
    nationality: Optional[str] = Query(None, description="Filter by nationality"),
) -> AuthorFilters:
    """Get author filter parameters."""
    return AuthorFilters(
        include_inactive=include_inactive,
        min_popularity=min_popularity,
        nationality=nationality,
    )


class SearchParams:
    """Search parameters for author search endpoints."""
    
    def __init__(
        self,
        q: str = Query(..., min_length=1, max_length=100, description="Search query"),
        limit: int = Query(20, ge=1, le=100, description="Maximum results"),
        include_inactive: bool = Query(False, description="Include inactive authors"),
    ):
        self.q = q
        self.limit = limit
        self.include_inactive = include_inactive


def get_search_params(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    include_inactive: bool = Query(False, description="Include inactive authors"),
) -> SearchParams:
    """Get search parameters."""
    return SearchParams(q=q, limit=limit, include_inactive=include_inactive)


class SortParams:
    """Sort parameters for author listing endpoints."""
    
    ALLOWED_FIELDS = {"name", "popularity_score", "total_books", "average_rating", "created_at"}
    ALLOWED_DIRECTIONS = {"asc", "desc"}
    
    def __init__(
        self,
        order_by: str = Query("name", description="Field to order by"),
        order_direction: str = Query("asc", description="Sort direction"),
    ):
        self.order_by = order_by
        self.order_direction = order_direction


def get_sort_params(
    order_by: str = Query("name", description="Field to order by"),
    order_direction: str = Query("asc", description="Sort direction"),
) -> SortParams:
    """Get sort parameters."""
    if order_by not in SortParams.ALLOWED_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid order_by field. Allowed: {', '.join(SortParams.ALLOWED_FIELDS)}"
        )
    
    if order_direction not in SortParams.ALLOWED_DIRECTIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid order_direction. Allowed: {', '.join(SortParams.ALLOWED_DIRECTIONS)}"
        )
    
    return SortParams(order_by=order_by, order_direction=order_direction)


async def get_author_service_with_context(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
) -> dict:
    """Get author service with user context."""
    return {
        "service": AuthorService(db),
        "current_user": current_user,
    }


def get_recommendation_limit(
    limit: int = Query(20, ge=1, le=100, description="Number of recommendations"),
) -> int:
    """Get recommendation limit parameter."""
    return limit


def get_popularity_threshold(
    min_popularity: float = Query(0.3, ge=0, le=1, description="Minimum popularity score"),
) -> float:
    """Get popularity threshold parameter."""
    return min_popularity


__all__ = [
    "get_author_service",
    "get_author_discovery_service",
    "get_author_or_404",
    "get_active_author_or_404",
    "get_authors_or_404",
    "get_author_with_follow_permission",
    "PaginationParams",
    "get_pagination_params",
    "AuthorFilters",
    "get_author_filters",
    "SearchParams",
    "get_search_params",
    "SortParams",
    "get_sort_params",
    "get_author_service_with_context",
    "get_recommendation_limit",
    "get_popularity_threshold",
]

