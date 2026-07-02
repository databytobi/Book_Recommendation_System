"""
Author Schemas

Pydantic models for author-related API requests and responses.

Phase: Schemas
"""

from enum import Enum
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from pydantic import BaseModel, Field, HttpUrl, validator


# ============================================================
# BASE SCHEMAS
# ============================================================

class AuthorBase(BaseModel):
    """Base author schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Author's full name")
    bio: Optional[str] = Field(None, description="Author's biography")
    image_url: Optional[HttpUrl] = Field(None, description="URL to author's profile image")
    birth_date: Optional[date] = Field(None, description="Author's birth date")
    death_date: Optional[date] = Field(None, description="Author's death date (if deceased)")
    nationality: Optional[str] = Field(None, max_length=100, description="Author's nationality")
    website: Optional[HttpUrl] = Field(None, description="Author's official website")
    wikipedia_url: Optional[HttpUrl] = Field(None, description="URL to author's Wikipedia page")
    popularity_score: Optional[float] = Field(0.0, ge=0.0, le=1.0, description="Popularity score (0-1)")
    is_active: bool = Field(True, description="Whether the author is active")


class AuthorCreate(AuthorBase):
    """Schema for creating a new author."""
    
    pass


class AuthorUpdate(BaseModel):
    """Schema for updating an existing author."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Author's full name")
    bio: Optional[str] = Field(None, description="Author's biography")
    image_url: Optional[HttpUrl] = Field(None, description="URL to author's profile image")
    birth_date: Optional[date] = Field(None, description="Author's birth date")
    death_date: Optional[date] = Field(None, description="Author's death date (if deceased)")
    nationality: Optional[str] = Field(None, max_length=100, description="Author's nationality")
    website: Optional[HttpUrl] = Field(None, description="Author's official website")
    wikipedia_url: Optional[HttpUrl] = Field(None, description="URL to author's Wikipedia page")
    popularity_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Popularity score (0-1)")
    is_active: Optional[bool] = Field(None, description="Whether the author is active")


# ============================================================
# RESPONSE SCHEMAS
# ============================================================

class AuthorResponse(AuthorBase):
    """Schema for author response."""
    
    id: int = Field(..., description="Author's unique identifier")
    total_books: int = Field(0, description="Total number of books by this author")
    average_rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Average rating of author's books")
    rating_status: Optional[str] = Field(None, description="Rating status (e.g., 'highly_rated', 'rated')")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class AuthorDetailResponse(AuthorResponse):
    """Schema for detailed author response including follow info."""
    
    followers_count: int = Field(0, description="Number of followers")
    is_following: bool = Field(False, description="Whether the current user follows this author")
    books: Optional[List[Any]] = Field(None, description="Author's books (if requested)")
    
    @classmethod
    def from_author_with_follow(
        cls,
        author,
        followers_count: int = 0,
        is_following: bool = False,
    ):
        """Create an AuthorDetailResponse from an author model with follow info."""
        author_dict = {
            col.name: getattr(author, col.name)
            for col in author.__table__.columns
        } if hasattr(author, '__table__') else author.__dict__
        author_dict["followers_count"] = followers_count
        author_dict["is_following"] = is_following
        return cls(**author_dict)


class AuthorListResponse(BaseModel):
    """Schema for paginated author list response."""
    
    items: List[AuthorResponse] = Field(..., description="List of authors")
    total: int = Field(..., description="Total number of authors")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum records returned")


# ============================================================
# SORT ENUMS
# ============================================================

class AuthorSortField(str, Enum):
    """Enum for author sort fields."""
    
    NAME = "name"
    POPULARITY = "popularity_score"
    RATING = "average_rating"
    CREATED = "created_at"
    BOOKS = "total_books"


class AuthorSortOrder(str, Enum):
    """Enum for sort order."""
    
    ASC = "asc"
    DESC = "desc"


# ============================================================
# SEARCH AND AUTOCOMPLETE SCHEMAS
# ============================================================

class AuthorSearchParams(BaseModel):
    """Schema for author search parameters."""
    
    query: Optional[str] = Field(None, max_length=100, description="Search query")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(20, ge=1, le=100, description="Maximum results")
    sort_by: Optional[AuthorSortField] = Field(None, description="Field to sort by")
    sort_order: Optional[AuthorSortOrder] = Field(None, description="Sort direction")
    include_inactive: bool = Field(False, description="Include inactive authors")
    min_popularity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum popularity score")
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Minimum rating")
    nationality: Optional[str] = Field(None, description="Filter by nationality")


class AuthorSuggestion(BaseModel):
    """Schema for author autocomplete suggestion."""
    
    id: int = Field(..., description="Author's unique identifier")
    name: str = Field(..., description="Author's full name")
    popularity_score: float = Field(..., description="Popularity score")
    total_books: int = Field(..., description="Total number of books")
    is_following: Optional[bool] = Field(False, description="Whether the current user follows this author")


# ============================================================
# FOLLOW SCHEMAS
# ============================================================

class FollowAuthorRequest(BaseModel):
    """Schema for following an author."""
    
    author_id: int = Field(..., description="Author's unique identifier")
    notification_preference: Optional[str] = Field(None, description="Notification preference")
    follow_source: str = Field("manual", description="Source of the follow")
    notes: Optional[str] = Field(None, description="User notes")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class UnfollowAuthorRequest(BaseModel):
    """Schema for unfollowing an author."""
    
    author_id: int = Field(..., description="Author's unique identifier")
    hard_delete: bool = Field(True, description="Permanently delete the follow relationship")


class AuthorFollowResponse(BaseModel):
    """Schema for author follow response."""
    
    author_id: int = Field(..., description="Author's unique identifier")
    author_name: str = Field(..., description="Author's full name")
    is_following: bool = Field(..., description="Whether the user is following this author")
    followers_count: int = Field(..., description="Total followers count")
    followed_at: Optional[datetime] = Field(None, description="When the user followed this author")


class FollowAuthorResponse(BaseModel):
    """Schema for follow author action response."""
    
    success: bool = Field(..., description="Whether the follow was successful")
    message: str = Field(..., description="Response message")
    author_id: int = Field(..., description="Author's unique identifier")
    author_name: str = Field(..., description="Author's full name")
    followed_at: Optional[datetime] = Field(None, description="When the user followed this author")


class UnfollowAuthorResponse(BaseModel):
    """Schema for unfollow author action response."""
    
    success: bool = Field(..., description="Whether the unfollow was successful")
    message: str = Field(..., description="Response message")
    author_id: int = Field(..., description="Author's unique identifier")
    author_name: Optional[str] = Field(None, description="Author's full name")


class FollowStatsResponse(BaseModel):
    """Schema for follow statistics response."""
    
    author_id: int = Field(..., description="Author's unique identifier")
    total_followers: int = Field(..., description="Total number of followers")
    recent_follows: int = Field(..., description="Number of follows in the last 7 days")
    follow_trend: float = Field(..., description="Follow trend percentage")
    timestamp: datetime = Field(..., description="Statistics timestamp")


class AuthorFollowStatsResponse(BaseModel):
    """Schema for detailed author follow statistics response."""
    
    author_id: int = Field(..., description="Author's unique identifier")
    author_name: str = Field(..., description="Author's full name")
    total_followers: int = Field(0, description="Total number of followers")
    recent_follows_30d: int = Field(0, description="Number of follows in the last 30 days")
    follow_sources: Dict[str, int] = Field(default_factory=dict, description="Follow sources breakdown")


# ============================================================
# DISCOVERY SCHEMAS
# ============================================================

class AuthorDiscoverySection(BaseModel):
    """Schema for a discovery section containing authors."""
    
    title: str = Field(..., description="Section title (e.g., 'Popular Authors', 'Trending Now')")
    type: str = Field(..., description="Section type (e.g., 'popular', 'trending', 'recommended', 'new')")
    authors: List[AuthorResponse] = Field(..., description="List of authors in this section")


class AuthorDiscoveryResponse(BaseModel):
    """Schema for author discovery response containing multiple sections."""
    
    sections: List[AuthorDiscoverySection] = Field(..., description="List of discovery sections")


# ============================================================
# STATISTICS SCHEMAS
# ============================================================

class AuthorStatsResponse(BaseModel):
    """Schema for author statistics response."""
    
    author_id: Optional[int] = Field(None, description="Author's unique identifier")
    name: Optional[str] = Field(None, description="Author's full name")
    total_books: Optional[int] = Field(0, description="Total number of books")
    average_rating: Optional[float] = Field(None, description="Average rating")
    popularity_score: Optional[float] = Field(None, description="Popularity score")
    followers_count: Optional[int] = Field(0, description="Total followers count")
    rating_status: Optional[str] = Field(None, description="Rating status")
    is_active: Optional[bool] = Field(None, description="Whether the author is active")
    
    # Global stats fields
    total_authors: Optional[int] = Field(None, description="Total number of authors")
    active_authors: Optional[int] = Field(None, description="Number of active authors")
    total_follows: Optional[int] = Field(None, description="Total follow relationships")
    average_popularity: Optional[float] = Field(None, description="Average popularity score")
    popularity_distribution: Optional[Dict[str, int]] = Field(None, description="Popularity score distribution")
    timestamp: Optional[datetime] = Field(None, description="Statistics timestamp")


class AuthorPopularityDistribution(BaseModel):
    """Schema for popularity distribution."""
    
    low: int = Field(..., description="Number of authors with low popularity (0-0.3)")
    medium: int = Field(..., description="Number of authors with medium popularity (0.3-0.7)")
    high: int = Field(..., description="Number of authors with high popularity (0.7-1.0)")


# ============================================================
# BULK OPERATION SCHEMAS
# ============================================================

class BulkFollowRequest(BaseModel):
    """Schema for bulk follow request."""
    
    author_ids: List[int] = Field(..., min_items=1, max_items=100, description="List of author IDs to follow")
    follow_source: str = Field("bulk", description="Source of the follows")


class BulkOperationResponse(BaseModel):
    """Schema for bulk operation response."""
    
    successful: int = Field(..., description="Number of successful operations")
    failed: int = Field(..., description="Number of failed operations")
    total: int = Field(..., description="Total number of operations")
    errors: Optional[List[str]] = Field(None, description="Error messages for failed operations")
    timestamp: datetime = Field(..., description="Operation timestamp")


class BulkFollowResponse(BaseModel):
    """Schema for bulk follow response."""
    
    successful: int = Field(..., description="Number of successful follows")
    failed: int = Field(..., description="Number of failed follows")
    total: int = Field(..., description="Total number of follow attempts")


# ============================================================
# RECOMMENDATION SCHEMAS
# ============================================================

class AuthorRecommendationResponse(BaseModel):
    """Schema for author recommendation response."""
    
    author: AuthorResponse = Field(..., description="Recommended author")
    match_score: float = Field(..., ge=0.0, le=1.0, description="Recommendation match score")
    reason: Optional[str] = Field(None, description="Reason for recommendation")
    is_following: bool = Field(False, description="Whether the user is already following this author")
    followers_count: int = Field(0, description="Total followers count")


# ============================================================
# VALIDATORS
# ============================================================

class AuthorValidators:
    """Collection of validators for author schemas."""
    
    @staticmethod
    def validate_dates(v: dict) -> dict:
        """Validate that birth_date is before death_date."""
        birth = v.get('birth_date')
        death = v.get('death_date')
        if birth and death and death < birth:
            raise ValueError('Death date must be after birth date')
        return v
    
    @staticmethod
    def validate_name(v: str) -> str:
        """Validate author name."""
        if not v or not v.strip():
            raise ValueError('Author name cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Author name must be at least 2 characters')
        return v.strip()