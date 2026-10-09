"""
Recommendation API Schemas

This module defines the Pydantic models for all recommendation API endpoints.
Includes request/response validation, examples, and comprehensive documentation.

Phase: API Schemas
"""

import math

from pydantic import BaseModel, Field, validator, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


def _is_null(value: Any) -> bool:
    """True for None, NaN, NaT and the strings pandas produces for them."""
    if value is None:
        return True
    if isinstance(value, float):
        return math.isnan(value)
    if isinstance(value, str):
        return value.strip().lower() in ("", "nan", "none", "<na>", "nat")
    return False


def _clean_optional_str(value: Any) -> Optional[str]:
    """Coerce a possibly-missing value to Optional[str]."""
    return None if _is_null(value) else str(value)


def _clean_optional_int(value: Any) -> Optional[int]:
    """
    Coerce a possibly-missing value to Optional[int].

    Pandas yields NaN for absent numeric columns. Passing NaN straight into a
    Pydantic `Optional[int]` raises "Input should be a finite number", which
    surfaced as a 500 for user IDs with no interaction history. Invalid values
    degrade to None instead of failing the whole response.
    """
    if _is_null(value):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# ============================================================
# ENUMS
# ============================================================

class RecommendationType(str, Enum):
    """Types of recommendation strategies."""
    POPULARITY = "popularity"
    CONTENT = "content"
    COLLABORATIVE = "collaborative"
    HYBRID = "hybrid"
    TRENDING = "trending"


class SortOrder(str, Enum):
    """Sorting order for responses."""
    ASC = "asc"
    DESC = "desc"


# ============================================================
# REQUEST SCHEMAS
# ============================================================

class RecommendationRequest(BaseModel):
    """
    Request schema for getting user recommendations.
    
    Attributes:
    -----------
    user_id : int
        User ID to generate recommendations for
    top_k : int
        Number of recommendations to return (default: 10)
    min_score : float
        Minimum recommendation score threshold (default: 0.0)
    exclude_authors : List[str], optional
        List of authors to exclude from recommendations
    filter_category : str, optional
        Filter recommendations by category
    """
    user_id: int = Field(
        ...,
        description="User ID to generate recommendations for",
        example=11676,
        gt=0
    )
    top_k: int = Field(
        default=10,
        description="Number of recommendations to return",
        example=10,
        ge=1,
        le=100
    )
    min_score: float = Field(
        default=0.0,
        description="Minimum recommendation score threshold (0-1)",
        example=0.1,
        ge=0.0,
        le=1.0
    )
    exclude_authors: Optional[List[str]] = Field(
        default=None,
        description="List of authors to exclude",
        example=["J.K. Rowling", "Stephen King"]
    )
    filter_category: Optional[str] = Field(
        default=None,
        description="Filter recommendations by category",
        example="Fantasy"
    )

    @validator('top_k')
    def validate_top_k(cls, v):
        """Validate top_k is within acceptable range."""
        if v < 1 or v > 100:
            raise ValueError('top_k must be between 1 and 100')
        return v

    @validator('min_score')
    def validate_min_score(cls, v):
        """Validate min_score is between 0 and 1."""
        if v < 0 or v > 1:
            raise ValueError('min_score must be between 0 and 1')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 11676,
                "top_k": 10,
                "min_score": 0.1,
                "exclude_authors": ["J.K. Rowling"],
                "filter_category": "Fantasy"
            }
        }
    )


class SimilarBookRequest(BaseModel):
    """
    Request schema for finding similar books.
    
    Attributes:
    -----------
    isbn : str
        ISBN of the book to find similar books for
    top_k : int
        Number of similar books to return (default: 10)
    exclude_same_author : bool
        Whether to exclude books by the same author (default: False)
    min_similarity : float
        Minimum similarity threshold (default: 0.0)
    """
    isbn: str = Field(
        ...,
        description="ISBN of the book to find similar books for",
        example="0446310786",
        min_length=10,
        max_length=13
    )
    top_k: int = Field(
        default=10,
        description="Number of similar books to return",
        example=10,
        ge=1,
        le=50
    )
    exclude_same_author: bool = Field(
        default=False,
        description="Whether to exclude books by the same author",
        example=False
    )
    min_similarity: float = Field(
        default=0.0,
        description="Minimum similarity threshold (0-1)",
        example=0.1,
        ge=0.0,
        le=1.0
    )

    @validator('isbn')
    def validate_isbn(cls, v):
        """Validate ISBN format."""
        # Remove hyphens and spaces
        v = v.replace('-', '').replace(' ', '')
        if not v.isdigit() and not (v[:-1].isdigit() and v[-1].upper() == 'X'):
            # ISBN-10 can end with X
            if not (len(v) == 10 and v[:-1].isdigit() and v[-1].upper() == 'X'):
                if not v.isdigit():
                    raise ValueError('ISBN must contain only digits (and optional X for ISBN-10)')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "isbn": "0446310786",
                "top_k": 10,
                "exclude_same_author": False,
                "min_similarity": 0.1
            }
        }
    )


class SearchRequest(BaseModel):
    """
    Request schema for semantic search.
    
    Attributes:
    -----------
    query : str
        Search query text
    top_k : int
        Number of search results to return (default: 10)
    min_score : float
        Minimum relevance score threshold (default: 0.0)
    filter_category : str, optional
        Filter results by category
    """
    query: str = Field(
        ...,
        description="Search query text",
        example="science fiction space adventure",
        min_length=1,
        max_length=500
    )
    top_k: int = Field(
        default=10,
        description="Number of search results to return",
        example=10,
        ge=1,
        le=50
    )
    min_score: float = Field(
        default=0.0,
        description="Minimum relevance score threshold (0-1)",
        example=0.1,
        ge=0.0,
        le=1.0
    )
    filter_category: Optional[str] = Field(
        default=None,
        description="Filter results by category",
        example="Science Fiction"
    )

    @validator('query')
    def validate_query(cls, v):
        """Validate query is not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "science fiction space adventure",
                "top_k": 10,
                "min_score": 0.1,
                "filter_category": "Science Fiction"
            }
        }
    )


class TrendingRequest(BaseModel):
    """
    Request schema for getting trending books.
    
    Attributes:
    -----------
    top_k : int
        Number of trending books to return (default: 20)
    days : int
        Number of days to consider for trending (default: 30)
    category : str, optional
        Filter by category
    """
    top_k: int = Field(
        default=20,
        description="Number of trending books to return",
        example=20,
        ge=1,
        le=100
    )
    days: int = Field(
        default=30,
        description="Number of days to consider for trending",
        example=30,
        ge=1
    )
    category: Optional[str] = Field(
        default=None,
        description="Filter by category",
        example="Fantasy"
    )


class WeightsUpdateRequest(BaseModel):
    """
    Request schema for updating recommendation weights.
    
    Attributes:
    -----------
    collaborative_weight : float
        Weight for collaborative recommendations (default: 0.50)
    content_weight : float
        Weight for content-based recommendations (default: 0.30)
    popularity_weight : float
        Weight for popularity-based recommendations (default: 0.20)
    """
    collaborative_weight: float = Field(
        default=0.50,
        description="Weight for collaborative recommendations",
        example=0.60,
        ge=0.0,
        le=1.0
    )
    content_weight: float = Field(
        default=0.30,
        description="Weight for content-based recommendations",
        example=0.30,
        ge=0.0,
        le=1.0
    )
    popularity_weight: float = Field(
        default=0.20,
        description="Weight for popularity-based recommendations",
        example=0.10,
        ge=0.0,
        le=1.0
    )

    @validator('collaborative_weight', 'content_weight', 'popularity_weight')
    def validate_weight(cls, v):
        """Validate each weight is between 0 and 1."""
        if v < 0 or v > 1:
            raise ValueError('Weights must be between 0 and 1')
        return v

    def validate_weights_sum(cls, values):
        """Validate weights sum to approximately 1."""
        total = (
            values.get('collaborative_weight', 0) +
            values.get('content_weight', 0) +
            values.get('popularity_weight', 0)
        )
        if not (0.99 <= total <= 1.01):
            raise ValueError(f'Weights must sum to 1 (current: {total:.2f})')
        return values

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "collaborative_weight": 0.60,
                "content_weight": 0.30,
                "popularity_weight": 0.10
            }
        }
    )


# ============================================================
# RESPONSE SCHEMAS
# ============================================================

class BookRecommendation(BaseModel):
    """
    Individual book recommendation with score.
    
    Attributes:
    -----------
    isbn : str
        Book ISBN
    title : str
        Book title
    author : str, optional
        Book author(s)
    publisher : str, optional
        Publisher name
    publication_year : int, optional
        Year of publication
    category : str, optional
        Book category
    score : float
        Recommendation score
    score_breakdown : Dict[str, float], optional
        Score breakdown by component
    """
    isbn: str = Field(..., description="Book ISBN")
    title: str = Field(..., description="Book title")
    author: Optional[str] = Field(None, description="Book author(s)")
    publisher: Optional[str] = Field(None, description="Publisher name")
    publication_year: Optional[int] = Field(None, description="Year of publication")
    category: Optional[str] = Field(None, description="Book category")
    # Cover art. Normalized to a loadable https URL by app/core/images.py,
    # because the catalog's original Amazon host now returns HTTP 403.
    image_url: Optional[str] = Field(None, description="Cover image URL")
    score: float = Field(..., description="Recommendation score")
    score_breakdown: Optional[Dict[str, float]] = Field(
        None,
        description="Score breakdown by component",
        example={"collaborative": 0.50, "content": 0.15, "popularity": 0.10}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "isbn": "0446310786",
                "title": "To Kill a Mockingbird",
                "author": "Harper Lee",
                "publisher": "Harper Perennial",
                "publication_year": 1988,
                "category": "Classic",
                "score": 0.75,
                "score_breakdown": {
                    "collaborative": 0.50,
                    "content": 0.15,
                    "popularity": 0.10
                }
            }
        }
    )


class RecommendationResponse(BaseModel):
    """
    Response schema for recommendation requests.
    
    Attributes:
    -----------
    count : int
        Number of recommendations returned
    recommendations : List[BookRecommendation]
        List of recommendations
    user_id : int, optional
        User ID these recommendations are for
    recommender_type : str, optional
        Type of recommender used
    processing_time_ms : float, optional
        Processing time in milliseconds
    """
    count: int = Field(..., description="Number of recommendations returned")
    recommendations: List[BookRecommendation] = Field(..., description="List of recommendations")
    user_id: Optional[int] = Field(None, description="User ID these recommendations are for")
    recommender_type: Optional[str] = Field(None, description="Type of recommender used")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "count": 10,
                "user_id": 11676,
                "recommender_type": "hybrid",
                "processing_time_ms": 42.5,
                "recommendations": [
                    {
                        "isbn": "0446310786",
                        "title": "To Kill a Mockingbird",
                        "author": "Harper Lee",
                        "category": "Classic",
                        "score": 0.75
                    }
                ]
            }
        }
    )


class SimilarBooksResponse(BaseModel):
    """
    Response schema for similar books requests.
    
    Attributes:
    -----------
    query_isbn : str
        The ISBN that was queried
    query_title : str, optional
        Title of the queried book
    count : int
        Number of similar books returned
    similar_books : List[BookRecommendation]
        List of similar books
    """
    query_isbn: str = Field(..., description="The ISBN that was queried")
    query_title: Optional[str] = Field(None, description="Title of the queried book")
    count: int = Field(..., description="Number of similar books returned")
    similar_books: List[BookRecommendation] = Field(..., description="List of similar books")


class SearchResponse(BaseModel):
    """
    Response schema for search requests.
    
    Attributes:
    -----------
    query : str
        The search query
    count : int
        Number of results returned
    results : List[BookRecommendation]
        Search results
    """
    query: str = Field(..., description="The search query")
    count: int = Field(..., description="Number of results returned")
    results: List[BookRecommendation] = Field(..., description="Search results")


class TrendingResponse(BaseModel):
    """
    Response schema for trending books.
    
    Attributes:
    -----------
    period : str
        Time period for trending
    count : int
        Number of trending books returned
    trending : List[BookRecommendation]
        Trending books
    """
    period: str = Field(..., description="Time period for trending", example="Last 30 days")
    count: int = Field(..., description="Number of trending books returned")
    trending: List[BookRecommendation] = Field(..., description="Trending books")


# ============================================================
# ERROR SCHEMAS
# ============================================================

class ErrorResponse(BaseModel):
    """
    Error response schema.
    
    Attributes:
    -----------
    error : str
        Error message
    error_type : str
        Error type
    status_code : int
        HTTP status code
    timestamp : datetime
        Error timestamp
    details : Dict[str, Any], optional
        Additional error details
    """
    error: str = Field(..., description="Error message", example="User not found")
    error_type: str = Field(..., description="Error type", example="NotFoundError")
    status_code: int = Field(..., description="HTTP status code", example=404)
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "User not found",
                "error_type": "NotFoundError",
                "status_code": 404,
                "timestamp": "2024-01-01T00:00:00",
                "details": {"user_id": 99999}
            }
        }
    )


# ============================================================
# FACTORY FUNCTIONS
# ============================================================

def create_recommendation_response(
    recommendations: List[Dict[str, Any]],
    user_id: Optional[int] = None,
    recommender_type: Optional[str] = None,
    processing_time_ms: Optional[float] = None
) -> RecommendationResponse:
    """
    Create a RecommendationResponse from raw recommendation data.
    
    Parameters:
    -----------
    recommendations : List[Dict]
        List of recommendation dictionaries
    user_id : Optional[int]
        User ID these recommendations are for
    recommender_type : Optional[str]
        Type of recommender used
    processing_time_ms : Optional[float]
        Processing time in milliseconds
    
    Returns:
    --------
    RecommendationResponse: Formatted response
    """
    book_recs = []
    for rec in recommendations:
        book_recs.append(
            BookRecommendation(
                isbn=rec.get("isbn", ""),
                title=rec.get("title", "Unknown"),
                author=rec.get("author") or rec.get("authors"),
                publisher=_clean_optional_str(rec.get("publisher")),
                publication_year=_clean_optional_int(rec.get("publication_year")),
                category=_clean_optional_str(rec.get("category")),
                score=rec.get("score", 0.0) or rec.get("hybrid_score", 0.0) or rec.get("similarity", 0.0),
                score_breakdown={
                    k: v for k, v in rec.items()
                    if k.endswith("_score") and isinstance(v, (int, float))
                    and not (isinstance(v, float) and math.isnan(v))
                }
            )
        )
    
    return RecommendationResponse(
        count=len(book_recs),
        recommendations=book_recs,
        user_id=user_id,
        recommender_type=recommender_type,
        processing_time_ms=processing_time_ms
    )


def create_error_response(
    error: str,
    error_type: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """
    Create an ErrorResponse.
    
    Parameters:
    -----------
    error : str
        Error message
    error_type : str
        Error type
    status_code : int
        HTTP status code
    details : Optional[Dict]
        Additional error details
    
    Returns:
    --------
    ErrorResponse: Formatted error response
    """
    return ErrorResponse(
        error=error,
        error_type=error_type,
        status_code=status_code,
        details=details
    )


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    # Example: Create a recommendation response
    sample_recs = [
        {
            "isbn": "0446310786",
            "title": "To Kill a Mockingbird",
            "authors": "Harper Lee",
            "category": "Classic",
            "score": 0.75,
            "collab_score": 0.50,
            "content_score": 0.15,
            "popularity_score": 0.10
        },
        {
            "isbn": "0439139597",
            "title": "Harry Potter and the Goblet of Fire",
            "authors": "J.K. Rowling",
            "category": "Fantasy",
            "score": 0.72,
        }
    ]
    
    response = create_recommendation_response(
        recommendations=sample_recs,
        user_id=11676,
        recommender_type="hybrid",
        processing_time_ms=42.5
    )
    
    print("Sample Response:")
    print(response.model_dump_json(indent=2))
    
    # Example: Create an error response
    error = create_error_response(
        error="User not found",
        error_type="NotFoundError",
        status_code=404,
        details={"user_id": 99999}
    )
    
    print("\nError Response:")
    print(error.model_dump_json(indent=2))