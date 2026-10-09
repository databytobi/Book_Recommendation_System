"""
Recommendation Routes

API endpoints for personalized book recommendations.

Phase: Recommendation Engine
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.api.v1.recommendations.schemas import (
    RecommendationRequest,
    RecommendationResponse,
)

from app.api.v1.recommendations.service import RecommendationService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


@router.get(
    "",
    response_model=RecommendationResponse,
    summary="Get personalized book recommendations",
)
def get_recommendations(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return personalized recommendations for the authenticated user.
    """

    try:
        service = RecommendationService(db)

        return service.get_recommendations(
            user_id=current_user.id,
            limit=limit,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except Exception as e:
        logger.exception("Recommendation generation failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations",
        )