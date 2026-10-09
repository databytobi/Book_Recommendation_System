"""
Onboarding Routes

API endpoints for user onboarding flow.
Handles preference collection, progress tracking, and onboarding completion.

Phase: API Routes
"""

from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.api.v1.onboarding.schemas import (
    OnboardingRequest,
    OnboardingResponse,
    OnboardingProgressResponse,
    OnboardingStepUpdateRequest,
    OnboardingPreferenceSummary,
)
# pyrefly: ignore [missing-import]
from app.api.v1.onboarding.service import OnboardingService
# pyrefly: ignore [missing-import]
from app.dependencies.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


# ============================================================
# ONBOARDING ENDPOINTS
# ============================================================

@router.post(
    "/complete",
    response_model=OnboardingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Complete user onboarding",
    description="Submit all onboarding preferences and complete the onboarding process."
)
def complete_onboarding(
    request: OnboardingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OnboardingResponse:
    """
    Complete user onboarding with provided preferences.
    
    Parameters:
    -----------
    request : OnboardingRequest
        Onboarding preferences
    db : Session
        Database session
    current_user : User
        Authenticated user
    
    Returns:
    --------
    OnboardingResponse: Onboarding completion status
    
    Raises:
    -------
    HTTPException: If onboarding fails
    """
    try:
        logger.info(f"Completing onboarding for user: {current_user.id}")
        
        # Validate request has selections
        if not request.has_selections():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one preference must be selected"
            )
        
        service = OnboardingService(db)
        
        # Complete onboarding
        result = service.complete_onboarding(
            user_id=current_user.id,
            request=request
        )
        
        # FIX: Added log for onboarding_completed
        logger.info(
            f"onboarding_completed saved = {result.get('onboarding_completed', False)}"
        )
        
        logger.info(f"Onboarding completed for user: {current_user.id}")
        
        # Generate preference summary
        summary = OnboardingPreferenceSummary.from_preferences(
            genres=request.preferred_genres,
            authors=request.favorite_authors,
            books=request.favorite_books,
            reading_goal=(
                request.reading_goal.value
                if hasattr(request.reading_goal, "value")
                else request.reading_goal or "moderate"
            ),
            reading_style=(
                request.reading_style.value
                if hasattr(request.reading_style, "value")
                else request.reading_style or "balanced"
            ),
            language=(
                request.preferred_language.value
                if hasattr(request.preferred_language, "value")
                else request.preferred_language or "en"
            ),
            theme=(
                request.theme.value
                if hasattr(request.theme, "value")
                else request.theme or "dark"
            ),
        )
        
        return OnboardingResponse.success_response(
            message="Onboarding completed successfully",
            completed_steps=[
                "welcome",
                "genres",
                "authors",
                "books",
                "reading_goal",
                "complete"
            ],
            recommendations_ready=True,
            preference_summary=summary.model_dump()
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error during onboarding: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during onboarding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete onboarding"
        )


@router.post(
    "/progress",
    response_model=OnboardingResponse,
    summary="Save onboarding progress",
    description="Save partial onboarding progress for a user."
)
def save_onboarding_progress(
    request: OnboardingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OnboardingResponse:
    """
    Save onboarding progress without completing.
    
    Parameters:
    -----------
    request : OnboardingRequest
        Onboarding preferences to save
    db : Session
        Database session
    current_user : User
        Authenticated user
    
    Returns:
    --------
    OnboardingResponse: Progress save status
    """
    try:
        logger.info(f"Saving onboarding progress for user: {current_user.id}")
        
        service = OnboardingService(db)
        
        # Save progress
        service.save_progress(
            user_id=current_user.id,
            request=request
        )
        
        logger.info(f"Onboarding progress saved for user: {current_user.id}")
        
        return OnboardingResponse.success_response(
            message="Progress saved successfully",
            completed_steps=service.get_completed_steps(current_user.id),
            recommendations_ready=False
        )
        
    except Exception as e:
        logger.error(f"Failed to save onboarding progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save progress"
        )


@router.get(
    "/status",
    response_model=OnboardingProgressResponse,
    summary="Get onboarding status",
    description="Get the current onboarding status for a user."
)
def get_onboarding_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OnboardingProgressResponse:
    """
    Get onboarding status for the current user.
    
    Parameters:
    -----------
    db : Session
        Database session
    current_user : User
        Authenticated user
    
    Returns:
    --------
    OnboardingProgressResponse: Onboarding progress status
    """
    try:
        service = OnboardingService(db)
        
        # NOTE: this variable must NOT be named `status`, because that would
        # shadow the `fastapi.status` module imported at the top of this file.
        # Doing so made the `except` block below raise
        # AttributeError: 'NoneType' object has no attribute
        # 'HTTP_500_INTERNAL_SERVER_ERROR', which replaced the real error and
        # left the frontend unable to read onboarding state.
        onboarding_state = service.get_status(current_user.id)
        
        # FIX: Added log for onboarding status
        logger.info(
            f"Onboarding status → completed={onboarding_state.get('completed_steps', []) if onboarding_state else []} "
            f"current={onboarding_state.get('current_step', 'welcome') if onboarding_state else 'welcome'}"
        )
        
        if not onboarding_state:
            # User hasn't started onboarding
            return OnboardingProgressResponse(
                user_id=current_user.id,
                current_step="welcome",
                completed_steps=[],
                progress_percentage=0.0,
                is_complete=False,
                next_step="welcome",
                total_steps=5
            )
        
        return OnboardingProgressResponse.from_onboarding_state(
            user_id=current_user.id,
            current_step=onboarding_state.get("current_step", "welcome"),
            completed_steps=onboarding_state.get("completed_steps", []),
            total_steps=onboarding_state.get("total_steps", 5)
        )
        
    except Exception as e:
        logger.error(f"Failed to get onboarding status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get onboarding status"
        )


@router.post(
    "/skip",
    response_model=Dict[str, Any],
    summary="Skip onboarding",
    description="Skip the onboarding process for a user."
)
def skip_onboarding(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Skip onboarding for the current user.
    
    Parameters:
    -----------
    db : Session
        Database session
    current_user : User
        Authenticated user
    
    Returns:
    --------
    Dict[str, Any]: Skip status
    """
    try:
        logger.info(f"Skipping onboarding for user: {current_user.id}")
        
        service = OnboardingService(db)
        
        result = service.skip(current_user.id)
        
        logger.info(f"Onboarding skipped for user: {current_user.id}")
        
        return {
            "success": True,
            "message": "Onboarding skipped successfully",
            "skipped_at": result.get("skipped_at") if result else None
        }
        
    except Exception as e:
        logger.error(f"Failed to skip onboarding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to skip onboarding"
        )


@router.post(
    "/step/{step}",
    response_model=OnboardingProgressResponse,
    summary="Complete a step",
    description="Mark a specific onboarding step as completed."
)
def complete_onboarding_step(
    step: str,
    request: OnboardingStepUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OnboardingProgressResponse:
    """
    Complete a specific onboarding step.
    
    Parameters:
    -----------
    step : str
        Step to complete
    request : OnboardingStepUpdateRequest
        Step completion data
    db : Session
        Database session
    current_user : User
        Authenticated user
    
    Returns:
    --------
    OnboardingProgressResponse: Updated progress status
    """
    try:
        logger.info(f"Completing step {step} for user: {current_user.id}")
        
        service = OnboardingService(db)
        
        # Mark step as complete
        service.complete_step(
            user_id=current_user.id,
            step=step,
            data=request.data
        )
        
        # Get updated status.
        # Named `onboarding_state`, not `status`: a local `status` would shadow
        # the fastapi.status module used by the handlers below.
        onboarding_state = service.get_status(current_user.id)
        
        if not onboarding_state:
            onboarding_state = {}
        
        return OnboardingProgressResponse.from_onboarding_state(
            user_id=current_user.id,
            current_step=onboarding_state.get("current_step", "welcome"),
            completed_steps=onboarding_state.get("completed_steps", []),
            total_steps=onboarding_state.get("total_steps", 5)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to complete step: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete step"
        )


@router.get(
    "/preferences",
    response_model=OnboardingRequest,
    summary="Get onboarding preferences",
    description="Get the user's editable onboarding preferences."
)
def get_onboarding_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OnboardingRequest:
    """
    Get the user's editable onboarding preferences.
    """
    try:
        service = OnboardingService(db)

        preferences = service.get_preferences(current_user.id)

        if not preferences:
            return OnboardingRequest(
                preferred_genres=[],
                favorite_authors=[],
                favorite_books=[],
                reading_goal="moderate",
                reading_style="balanced",
                preferred_language="en",
                theme="dark",
            )

        return OnboardingRequest(
            preferred_genres=preferences.get("preferred_genres", []),
            favorite_authors=preferences.get("favorite_authors", []),
            favorite_books=preferences.get("favorite_books", []),
            reading_goal=preferences.get("reading_goal", "moderate"),
            reading_style=preferences.get("reading_style", "balanced"),
            preferred_language=preferences.get("preferred_language", "en"),
            theme=preferences.get("theme", "dark"),
        )

    except Exception as e:
        logger.error(f"Failed to get preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get preferences",
        )
        
@router.post(
    "/reset",
    response_model=Dict[str, Any],
    summary="Reset onboarding",
    description="Reset onboarding progress for a user."
)
def reset_onboarding(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Reset onboarding progress for the current user.
    
    Parameters:
    -----------
    db : Session
        Database session
    current_user : User
        Authenticated user
    
    Returns:
    --------
    Dict[str, Any]: Reset status
    """
    try:
        logger.warning(f"Resetting onboarding for user: {current_user.id}")
        
        service = OnboardingService(db)
        
        service.reset(current_user.id)
        
        logger.info(f"Onboarding reset for user: {current_user.id}")
        
        return {
            "success": True,
            "message": "Onboarding reset successfully",
            "reset_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to reset onboarding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset onboarding"
        )


# ============================================================
# HEALTH CHECK
# ============================================================

@router.get(
    "/health",
    summary="Onboarding health check",
    description="Check if the onboarding service is healthy."
)
async def onboarding_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for onboarding service.
    
    Returns:
    --------
    Dict[str, Any]: Health status
    """
    return {
        "status": "healthy",
        "service": "onboarding",
        "timestamp": datetime.now().isoformat()
    }