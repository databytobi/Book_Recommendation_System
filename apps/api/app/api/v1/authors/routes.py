"""
Author Routes

API endpoints for author operations including CRUD, search,
following, and recommendations.

Phase: API Routes
"""

from datetime import datetime
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.api.v1.authors.schemas import (
    AuthorCreate,
    AuthorUpdate,
    AuthorResponse,
    AuthorDetailResponse,
    AuthorListResponse,
    AuthorDiscoveryResponse,
    AuthorSortField,
    AuthorSortOrder,
    FollowAuthorRequest,
    FollowAuthorResponse,
    UnfollowAuthorResponse,
    BulkFollowRequest,
    BulkFollowResponse,
    AuthorStatsResponse,
    AuthorFollowStatsResponse,
)
from app.api.v1.authors.dependencies import get_author_service
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.author_service import AuthorService
from app.services.author_discovery_service import AuthorDiscoveryService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/authors", tags=["Authors"])


# ============================================================
# 1. HEALTH CHECK (no auth, must be first)
# ============================================================

@router.get(
    "/health",
    summary="Authors health check",
    description="Check if the authors service is healthy."
)
async def authors_health_check():
    """
    Health check endpoint for authors service.
    """
    return {
        "status": "healthy",
        "service": "authors",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================
# 2. LIST & SEARCH (static paths with query params)
# ============================================================

@router.get(
    "/",
    response_model=AuthorListResponse,
    summary="List authors",
    description="Get paginated list of authors with sorting and filtering."
)
def list_authors(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    sort_by: AuthorSortField = Query(AuthorSortField.NAME, description="Field to sort by"),
    sort_order: AuthorSortOrder = Query(AuthorSortOrder.ASC, description="Sort direction"),
    include_inactive: bool = Query(False, description="Include inactive authors"),
    min_popularity: float = Query(None, ge=0.0, le=100.0, description="Minimum popularity"),
    min_rating: float = Query(None, ge=0.0, le=5.0, description="Minimum rating"),
    nationality: str = Query(None, description="Filter by nationality"),
    service: AuthorService = Depends(get_author_service),
):
    """
    List authors with pagination and filters.
    """
    try:
        result = service.list_authors(
            skip=skip,
            limit=limit,
            include_inactive=include_inactive,
            order_by=sort_by.value if sort_by else "name",
            order_direction=sort_order.value if sort_order else "asc"
        )
        return result
        
    except Exception as e:
        logger.error(f"Failed to list authors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list authors"
        )


@router.get(
    "/search",
    response_model=AuthorListResponse,
    summary="Search authors",
    description="Search authors by name with relevance ranking."
)
def search_authors(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    limit: int = Query(20, ge=1, le=50, description="Maximum number of results"),
    include_inactive: bool = Query(False, description="Include inactive authors"),
    min_popularity: float = Query(None, ge=0.0, le=100.0, description="Minimum popularity"),
    service: AuthorService = Depends(get_author_service),
):
    """
    Search authors by name.
    """
    try:
        authors = service.search_authors(
            query=q,
            limit=limit,
            include_inactive=include_inactive,
            min_popularity=min_popularity
        )
        
        # Convert to response models
        author_responses = [AuthorResponse.model_validate(author) for author in authors]
        
        return AuthorListResponse(
            total=len(author_responses),
            items=author_responses,
            skip=0,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Failed to search authors with query '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search authors"
        )


@router.get(
    "/autocomplete",
    response_model=List[Dict[str, Any]],
    summary="Autocomplete authors",
    description="Get author suggestions for autocomplete."
)
def autocomplete_authors(
    prefix: str = Query(..., min_length=1, max_length=50, description="Name prefix"),
    limit: int = Query(10, ge=1, le=20, description="Maximum number of results"),
    service: AuthorService = Depends(get_author_service),
    current_user: User = Depends(get_current_user),
):
    """
    Get author suggestions for autocomplete.
    """
    try:
        suggestions = service.get_author_suggestions(
            prefix=prefix,
            limit=limit,
            user_id=current_user.id
        )
        return suggestions
        
    except Exception as e:
        logger.error(f"Failed to autocomplete authors with prefix '{prefix}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get autocomplete suggestions"
        )


# ============================================================
# 3. SPECIALIZED QUERIES (all static paths)
# ============================================================

@router.get(
    "/popular",
    response_model=AuthorListResponse,
    summary="Popular authors",
    description="Get most popular authors sorted by popularity score."
)
def get_popular_authors(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    min_popularity: float = Query(None, ge=0.0, le=100.0, description="Minimum popularity"),
    service: AuthorService = Depends(get_author_service),
):
    """
    Get most popular authors.
    """
    try:
        authors = service.get_popular_authors(limit, min_popularity)
        
        # Convert to response models
        author_responses = [AuthorResponse.model_validate(author) for author in authors]
        
        return AuthorListResponse(
            total=len(author_responses),
            items=author_responses,
            skip=0,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Failed to get popular authors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get popular authors"
        )


@router.get(
    "/top-rated",
    response_model=AuthorListResponse,
    summary="Top rated authors",
    description="Get highest rated authors."
)
def get_top_rated_authors(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    min_rating: float = Query(None, ge=0.0, le=5.0, description="Minimum rating"),
    service: AuthorService = Depends(get_author_service),
):
    """
    Get highest rated authors.
    """
    try:
        authors = service.get_top_rated_authors(limit, min_rating)
        
        # Convert to response models
        author_responses = [AuthorResponse.model_validate(author) for author in authors]
        
        return AuthorListResponse(
            total=len(author_responses),
            items=author_responses,
            skip=0,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Failed to get top rated authors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get top rated authors"
        )


@router.get(
    "/prolific",
    response_model=AuthorListResponse,
    summary="Most prolific authors",
    description="Get authors with the most books."
)
def get_most_prolific_authors(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    min_books: int = Query(None, ge=0, description="Minimum number of books"),
    service: AuthorService = Depends(get_author_service),
):
    """
    Get most prolific authors (most books).
    """
    try:
        authors = service.get_most_prolific_authors(limit, min_books)
        
        # Convert to response models
        author_responses = [AuthorResponse.model_validate(author) for author in authors]
        
        return AuthorListResponse(
            total=len(author_responses),
            items=author_responses,
            skip=0,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Failed to get most prolific authors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get most prolific authors"
        )


@router.get(
    "/featured",
    response_model=AuthorListResponse,
    summary="Featured authors",
    description="Get featured authors with high popularity."
)
def get_featured_authors(
    limit: int = Query(10, ge=1, le=20, description="Maximum number of results"),
    min_popularity: float = Query(0.5, ge=0.0, le=100.0, description="Minimum popularity"),
    service: AuthorService = Depends(get_author_service),
):
    """
    Get featured authors.
    """
    try:
        authors = service.get_featured_authors(limit, min_popularity)
        
        # Convert to response models
        author_responses = [AuthorResponse.model_validate(author) for author in authors]
        
        return AuthorListResponse(
            total=len(author_responses),
            items=author_responses,
            skip=0,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Failed to get featured authors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get featured authors"
        )


@router.get(
    "/trending",
    response_model=AuthorListResponse,
    summary="Trending authors",
    description="Get trending authors based on recent popularity."
)
def get_trending_authors(
    limit: int = Query(10, ge=1, le=20, description="Maximum number of results"),
    days: int = Query(30, ge=1, le=90, description="Days to consider for trending"),
    service: AuthorService = Depends(get_author_service),
):
    """
    Get trending authors.
    """
    try:
        authors = service.get_trending_authors(limit, days)
        
        # Convert to response models
        author_responses = [AuthorResponse.model_validate(author) for author in authors]
        
        return AuthorListResponse(
            total=len(author_responses),
            items=author_responses,
            skip=0,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Failed to get trending authors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trending authors"
        )


@router.get(
    "/random",
    response_model=AuthorListResponse,
    summary="Random authors",
    description="Get random authors for discovery."
)
def get_random_authors(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    seed: int = Query(None, description="Random seed for reproducibility"),
    service: AuthorService = Depends(get_author_service),
):
    """
    Get random authors.
    """
    try:
        authors = service.get_random_authors(limit=limit, seed=seed)
        
        # Convert to response models
        author_responses = [AuthorResponse.model_validate(author) for author in authors]
        
        return AuthorListResponse(
            total=len(author_responses),
            items=author_responses,
            skip=0,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Failed to get random authors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get random authors"
        )


@router.get(
    "/recommendations",
    response_model=List[Dict[str, Any]],
    summary="Author recommendations",
    description="Get personalized author recommendations for the user."
)
def get_author_recommendations(
    limit: int = Query(20, ge=1, le=50, description="Maximum number of recommendations"),
    min_popularity: float = Query(0.3, ge=0.0, le=100.0, description="Minimum popularity"),
    service: AuthorService = Depends(get_author_service),
    current_user: User = Depends(get_current_user),
):
    """
    Get personalized author recommendations.
    """
    try:
        recommendations = service.get_author_recommendations(
            user_id=current_user.id,
            limit=limit,
            min_popularity=min_popularity
        )
        return recommendations
        
    except Exception as e:
        logger.error(f"Failed to get author recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommendations"
        )


# ============================================================
# 4. FOLLOW ENDPOINTS (static paths)
# ============================================================

@router.post(
    "/follow",
    response_model=FollowAuthorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Follow author",
)
def follow_author(
    request: FollowAuthorRequest,
    service: AuthorService = Depends(get_author_service),
    current_user: User = Depends(get_current_user),
) -> FollowAuthorResponse:
    """
    Follow an author.
    """
    try:
        # Verify author exists
        author = service.get_author(request.author_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Author with ID {request.author_id} not found"
            )
        
        # Check if already following
        if service.is_following(current_user.id, request.author_id):
            return FollowAuthorResponse(
                success=True,
                message=f"Already following {author.name}",
                author_id=request.author_id,
                author_name=author.name,
                followed_at=datetime.now()
            )
        
        # Create follow relationship
        service.follow_author(
            user_id=current_user.id,
            author_id=request.author_id,
            notification_preference=request.notification_preference,
            follow_source="api",
            notes=request.notes
        )
        
        logger.info(f"User {current_user.id} followed author {request.author_id}")
        
        return FollowAuthorResponse(
            success=True,
            message=f"Successfully followed {author.name}",
            author_id=request.author_id,
            author_name=author.name,
            followed_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to follow author {request.author_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/follow/{author_id}",
    response_model=UnfollowAuthorResponse,
    summary="Unfollow author",
)
def unfollow_author(
    author_id: int,
    service: AuthorService = Depends(get_author_service),
    current_user: User = Depends(get_current_user),
) -> UnfollowAuthorResponse:
    """
    Unfollow an author.
    """
    try:
        # Check if following first
        if not service.is_following(current_user.id, author_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not following this author"
            )
        
        # Get author name for response
        author = service.get_author(author_id)
        author_name = author.name if author else None
        
        # Unfollow
        success = service.unfollow_author(
            user_id=current_user.id,
            author_id=author_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to unfollow author"
            )
        
        logger.info(f"User {current_user.id} unfollowed author {author_id}")
        
        return UnfollowAuthorResponse(
            success=True,
            message=f"Successfully unfollowed {author_name or 'author'}",
            author_id=author_id,
            author_name=author_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unfollow author {author_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/follow/bulk",
    response_model=BulkFollowResponse,
    summary="Bulk follow authors",
    description="Follow multiple authors at once."
)
def bulk_follow_authors(
    request: BulkFollowRequest,
    service: AuthorService = Depends(get_author_service),
    current_user: User = Depends(get_current_user),
):
    """
    Bulk follow authors.
    """
    try:
        result = service.bulk_follow_authors(
            user_id=current_user.id,
            author_ids=request.author_ids,
            follow_source=request.follow_source or "bulk"
        )
        
        logger.info(f"User {current_user.id} bulk followed {result['successful']} authors")
        
        return BulkFollowResponse(
            successful=result["successful"],
            failed=result["failed"],
            total=result["total"]
        )
        
    except Exception as e:
        logger.error(f"Failed to bulk follow authors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk follow authors"
        )


@router.get(
    "/following",
    response_model=AuthorListResponse,
    summary="Followed authors",
    description="Get all authors followed by the current user."
)
def get_followed_authors(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    service: AuthorService = Depends(get_author_service),
    current_user: User = Depends(get_current_user),
):
    """
    Get authors followed by the current user.
    """
    try:
        authors = service.get_followed_authors(
            user_id=current_user.id,
            limit=limit,
            offset=skip
        )
        
        # Convert to response models
        author_responses = [AuthorResponse.model_validate(author) for author in authors]
        
        # Get total count
        total = service.follow_repo.count_following(current_user.id)
        
        return AuthorListResponse(
            total=total,
            items=author_responses,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Failed to get followed authors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get followed authors"
        )


# ============================================================
# 5. DISCOVERY ENDPOINTS (static paths)
# ============================================================

def get_author_discovery_service(db: Session = Depends(get_db)):
    """Dependency that provides an AuthorDiscoveryService instance."""
    return AuthorDiscoveryService(db)


@router.get(
    "/discovery/onboarding",
    response_model=AuthorListResponse,
    summary="Get authors for onboarding",
    description="Returns a balanced mix of authors for user onboarding.",
)
def onboarding_discovery(
    limit: int = Query(
        30,
        ge=10,
        le=100,
        description="Number of authors to return for onboarding"
    ),
    service: AuthorDiscoveryService = Depends(get_author_discovery_service),
):
    """
    Get curated authors for new user onboarding.
    """
    authors = service.onboarding_authors(limit)
    
    author_responses = [AuthorResponse.model_validate(author) for author in authors]
    
    return AuthorListResponse(
        total=len(author_responses),
        items=author_responses,
        skip=0,
        limit=limit,
    )


@router.get(
    "/discovery",
    response_model=AuthorDiscoveryResponse,
    summary="Author discovery collections",
    description="Return curated author collections for onboarding and homepage.",
)
def discovery(
    service: AuthorDiscoveryService = Depends(get_author_discovery_service),
):
    """
    Get curated author discovery collections.
    """
    sections_config = [
        {"type": "trending", "title": "Trending Now", "limit": 20, "kwargs": {"days": 7}},
        {"type": "top_rated", "title": "Highest Rated", "limit": 20, "kwargs": {"min_rating": 4.0}},
        {"type": "emerging", "title": "Hidden Gems", "limit": 20, "kwargs": {"max_books": 3}},
        {"type": "random", "title": "Discover Someone New", "limit": 20, "kwargs": {"seed": 42}},
    ]
    
    return service.build_discovery_response(sections_config)


# ============================================================
# 6. STATISTICS (static paths)
# ============================================================

@router.get(
    "/stats",
    response_model=AuthorStatsResponse,
    summary="Author statistics",
    description="Get global author statistics."
)
def get_author_stats(
    service: AuthorService = Depends(get_author_service),
):
    """
    Get global author statistics.
    """
    try:
        stats = service.get_author_stats()
        return AuthorStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Failed to get author stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get author stats"
        )


# ============================================================
# 7. CRUD ENDPOINTS — DYNAMIC /{author_id} MUST BE LAST
# ============================================================

@router.post(
    "/",
    response_model=AuthorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create author",
    description="Create a new author in the system."
)
def create_author(
    author_data: AuthorCreate,
    service: AuthorService = Depends(get_author_service),
):
    """
    Create a new author.
    """
    try:
        author = service.create_author(author_data)
        logger.info(f"Created author: {author.name} (ID: {author.id})")
        return AuthorResponse.from_author(author)
        
    except ValueError as e:
        logger.warning(f"Validation error creating author: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create author: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create author"
        )


@router.get(
    "/{author_id}",
    response_model=AuthorDetailResponse,
    summary="Get author",
    description="Get an author by ID with detailed information."
)
def get_author(
    author_id: int,
    include_books: bool = Query(False, description="Include books in response"),
    service: AuthorService = Depends(get_author_service),
    current_user: User = Depends(get_current_user),
):
    """
    Get an author by ID.
    """
    try:
        author = service.get_author(author_id, include_books)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Author with ID {author_id} not found"
            )
        
        followers_count = service.count_followers(author_id)
        is_following = service.is_following(current_user.id, author_id)
        
        return AuthorDetailResponse.from_author_with_follow(
            author=author,
            followers_count=followers_count,
            is_following=is_following
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get author {author_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get author"
        )


@router.put(
    "/{author_id}",
    response_model=AuthorResponse,
    summary="Update author",
    description="Update an existing author."
)
def update_author(
    author_id: int,
    author_data: AuthorUpdate,
    service: AuthorService = Depends(get_author_service),
):
    """
    Update an existing author.
    """
    try:
        author = service.update_author(author_id, author_data)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Author with ID {author_id} not found"
            )
        
        logger.info(f"Updated author: {author.name} (ID: {author.id})")
        return AuthorResponse.from_author(author)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update author {author_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update author"
        )


@router.delete(
    "/{author_id}",
    response_model=Dict[str, Any],
    summary="Delete author",
    description="Delete or deactivate an author."
)
def delete_author(
    author_id: int,
    hard_delete: bool = Query(False, description="Permanently delete"),
    service: AuthorService = Depends(get_author_service),
):
    """
    Delete or deactivate an author.
    """
    try:
        success = service.delete_author(author_id, hard_delete)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Author with ID {author_id} not found"
            )
        
        logger.info(f"{'Hard' if hard_delete else 'Soft'} deleted author {author_id}")
        return {
            "success": True,
            "message": f"Author {'permanently deleted' if hard_delete else 'deactivated'} successfully",
            "author_id": author_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete author {author_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete author"
        )


@router.get(
    "/{author_id}/stats/follow",
    response_model=AuthorFollowStatsResponse,
    summary="Author follow statistics",
    description="Get follow statistics for an author."
)
def get_author_follow_stats(
    author_id: int,
    service: AuthorService = Depends(get_author_service),
):
    """
    Get follow statistics for an author.
    """
    try:
        author = service.get_author(author_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Author with ID {author_id} not found"
            )
        
        stats = service.get_follow_stats(author_id)
        
        return AuthorFollowStatsResponse(
            author_id=author_id,
            author_name=author.name,
            total_followers=stats.get("total_followers", 0),
            recent_follows_30d=stats.get("recent_follows_30d", 0),
            follow_sources=stats.get("follow_sources", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get follow stats for author {author_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get follow statistics"
        )