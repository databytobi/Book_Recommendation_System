"""
Recommendation Schemas

Pydantic models for personalized book recommendations.

Phase: Recommendation Engine
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# REQUEST
# ============================================================

class RecommendationRequest(BaseModel):
    """
    Request parameters for recommendation generation.
    """

    limit: int = Field(
        default=20,
        ge=5,
        le=100,
        description="Number of books to return"
    )

    include_read_books: bool = Field(
        default=False,
        description="Whether to include books the user already selected"
    )

    genre_filter: Optional[str] = Field(
        default=None,
        description="Optional genre filter"
    )


# ============================================================
# BOOK CARD
# ============================================================

class RecommendedBook(BaseModel):
    """
    Individual recommended book.
    """

    isbn: str
    title: str
    authors: Optional[str] = None
    genre: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None

    average_rating: float = 0.0
    ratings_count: int = 0

    image_url: Optional[str] = None

    recommendation_score: float = Field(
        ...,
        description="Final hybrid recommendation score"
    )

    recommendation_reason: str = Field(
        ...,
        description="Human-readable explanation"
    )


# ============================================================
# RESPONSE
# ============================================================

class RecommendationResponse(BaseModel):
    """
    API response containing personalized books.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "total": 20,
                "recommendations": []
            }
        }
    )

    success: bool
    total: int

    recommendations: List[RecommendedBook]

    generated_from: str = Field(
        default="hybrid",
        description="Recommendation strategy used"
    )