"""
Onboarding Schemas

Pydantic models for user onboarding requests and responses.
Handles preference collection, validation, and progress tracking.

Phase: Schemas / Onboarding
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


class Theme(str, Enum):
    """Available UI themes."""
    DARK = "dark"
    LIGHT = "light"
    SYSTEM = "system"


class ReadingGoal(str, Enum):
    """Reading goal options."""
    LIGHT = "light"  # 1-5 books/year
    MODERATE = "moderate"  # 6-12 books/year
    AVID = "avid"  # 13-24 books/year
    INTENSE = "intense"  # 25+ books/year
    
    @classmethod
    def get_book_count(cls, goal: str) -> int:
        """Get the approximate number of books for a goal."""
        goal_map = {
            cls.LIGHT: 5,
            cls.MODERATE: 12,
            cls.AVID: 24,
            cls.INTENSE: 40,
        }
        return goal_map.get(goal, 12)


class Language(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    DUTCH = "nl"
    RUSSIAN = "ru"
    JAPANESE = "ja"
    CHINESE = "zh"
    ARABIC = "ar"
    HINDI = "hi"
    
    @classmethod
    def get_language_name(cls, code: str) -> str:
        """Get the full language name."""
        language_map = {
            cls.ENGLISH: "English",
            cls.SPANISH: "Spanish",
            cls.FRENCH: "French",
            cls.GERMAN: "German",
            cls.ITALIAN: "Italian",
            cls.PORTUGUESE: "Portuguese",
            cls.DUTCH: "Dutch",
            cls.RUSSIAN: "Russian",
            cls.JAPANESE: "Japanese",
            cls.CHINESE: "Chinese",
            cls.ARABIC: "Arabic",
            cls.HINDI: "Hindi",
        }
        return language_map.get(code, code)


class OnboardingStep(str, Enum):
    """Onboarding flow steps."""
    WELCOME = "welcome"
    GENRE_SELECTION = "genres"
    AUTHOR_SELECTION = "authors"
    BOOK_SELECTION = "books"
    READING_GOAL = "reading_goal"
    COMPLETE = "complete"


class OnboardingRequest(BaseModel):
    """
    User onboarding preference request.
    
    Collects user preferences during the onboarding process.
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "favorite_authors": ["Jane Austen", "J.K. Rowling"],
                "favorite_books": ["9780439139601", "9780141439518"],
                "reading_goal": "moderate",
                "preferred_genres": ["fiction", "fantasy", "romance"],
                "preferred_language": "en",
                "recommendation_count": 20,
                "theme": "dark"
            }
        }
    )
    
    # User preferences
    favorite_authors: List[str] = Field(
        default_factory=list,
        max_length=100,
        description="List of favorite author names or IDs",
        examples=[["Jane Austen", "J.K. Rowling"]]
    )
    
    favorite_books: List[str] = Field(
        default_factory=list,
        max_length=50,
        description="List of favorite book ISBNs",
        examples=[["9780439139601", "9780141439518"]]
    )
    
    preferred_genres: List[str] = Field(
        default_factory=list,
        max_length=30,
        description="List of preferred genres",
        examples=[["fiction", "fantasy", "romance"]]
    )
    
    # User preferences
    reading_goal: Optional[ReadingGoal] = Field(
        default=ReadingGoal.MODERATE,
        description="Reading goal for the year"
    )
    
    preferred_language: Optional[Language] = Field(
        default=Language.ENGLISH,
        description="Preferred language for recommendations"
    )
    
    # App preferences
    recommendation_count: Optional[int] = Field(
        default=20,
        ge=5,
        le=100,
        description="Number of recommendations to show",
        examples=[20]
    )
    
    theme: Optional[Theme] = Field(
        default=Theme.DARK,
        description="UI theme preference"
    )
    
    # Optional additional data
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata for the onboarding"
    )
    
    # Validators
    @field_validator('favorite_authors')
    @classmethod
    def validate_favorite_authors(cls, v: List[str]) -> List[str]:
        """Validate author list and clean entries."""
        if v is None:
            return []
        
        # Clean and deduplicate
        cleaned = [author.strip() for author in v if author and author.strip()]
        
        if len(cleaned) != len(v):
            raise ValueError("Invalid author names provided (empty or whitespace)")
        
        if len(cleaned) > 100:
            raise ValueError("Cannot select more than 100 authors")
        
        return cleaned
    
    @field_validator('favorite_books')
    @classmethod
    def validate_favorite_books(cls, v: List[str]) -> List[str]:
        """Validate book ISBNs."""
        if v is None:
            return []
        
        # Clean ISBNs
        cleaned = []
        for isbn in v:
            # Remove hyphens and spaces
            cleaned_isbn = isbn.replace('-', '').replace(' ', '').strip()
            if not cleaned_isbn:
                continue
            
            # Validate ISBN format (10 or 13 digits)
            if not (len(cleaned_isbn) in [10, 13] and cleaned_isbn.isdigit()):
                raise ValueError(f"Invalid ISBN format: {isbn}")
            
            cleaned.append(cleaned_isbn)
        
        if len(cleaned) > 50:
            raise ValueError("Cannot select more than 50 books")
        
        return cleaned
    
    @field_validator('preferred_genres')
    @classmethod
    def validate_genres(cls, v: List[str]) -> List[str]:
        """Validate and clean genre list."""
        if v is None:
            return []
        
        # Clean and deduplicate
        cleaned = [genre.strip().lower() for genre in v if genre and genre.strip()]
        
        if len(cleaned) != len(v):
            raise ValueError("Invalid genres provided (empty or whitespace)")
        
        if len(cleaned) > 30:
            raise ValueError("Cannot select more than 30 genres")
        
        return cleaned
    
    @field_validator('preferred_language')
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        """Validate language code."""
        if v is None:
            return None
        
        # If it's a Language enum member
        if isinstance(v, Language):
            return v.value
        
        # If it's a string, validate against enum
        if isinstance(v, str):
            try:
                return Language(v.lower()).value
            except ValueError:
                valid_languages = ", ".join([l.value for l in Language])
                raise ValueError(f"Invalid language: {v}. Valid options: {valid_languages}")
        
        return v
    
    @field_validator('theme')
    @classmethod
    def validate_theme(cls, v: Optional[str]) -> Optional[str]:
        """Validate theme option."""
        if v is None:
            return None
        
        if isinstance(v, Theme):
            return v.value
        
        try:
            return Theme(v.lower()).value
        except ValueError:
            raise ValueError(f"Invalid theme: {v}. Valid options: dark, light, system")
    
    def get_book_count_goal(self) -> int:
        """Get the estimated number of books for the reading goal."""
        if isinstance(self.reading_goal, ReadingGoal):
            return ReadingGoal.get_book_count(self.reading_goal.value)
        elif isinstance(self.reading_goal, str):
            return ReadingGoal.get_book_count(self.reading_goal)
        return 12
    
    def has_selections(self) -> bool:
        """Check if the user has made any selections."""
        return (
            bool(self.favorite_authors) or
            bool(self.favorite_books) or
            bool(self.preferred_genres)
        )


class OnboardingResponse(BaseModel):
    """
    Onboarding response model.
    
    Returns the status and results of the onboarding process.
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Onboarding completed successfully",
                "completed_steps": ["welcome", "genres", "authors", "books", "reading_goal", "complete"],
                "recommendations_ready": True,
                "preference_summary": {
                    "total_genres": 3,
                    "total_authors": 2,
                    "total_books": 2,
                    "reading_goal": "moderate",
                    "reading_goal_books": 12,
                    "language": "English"
                }
            }
        }
    )
    
    success: bool = Field(
        ...,
        description="Whether the onboarding was successful"
    )
    
    message: str = Field(
        ...,
        description="Status message",
        examples=["Onboarding completed successfully"]
    )
    
    completed_steps: List[str] = Field(
        default_factory=list,
        description="List of completed onboarding steps",
        examples=[["welcome", "genres", "authors", "books", "reading_goal", "complete"]]
    )
    
    recommendations_ready: bool = Field(
        default=False,
        description="Whether recommendations are ready"
    )
    
    # Optional additional fields
    preference_summary: Optional[Dict[str, Any]] = Field(
        None,
        description="Summary of collected preferences"
    )
    
    next_step: Optional[str] = Field(
        None,
        description="Next onboarding step if not complete"
    )
    
    progress_percentage: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Onboarding progress percentage"
    )
    
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Response timestamp"
    )
    
    @classmethod
    def success_response(
        cls,
        message: str = "Onboarding completed successfully",
        completed_steps: Optional[List[str]] = None,
        recommendations_ready: bool = True,
        preference_summary: Optional[Dict[str, Any]] = None,
    ) -> "OnboardingResponse":
        """
        Create a successful onboarding response.
        
        Parameters:
        -----------
        message : str
            Success message
        completed_steps : Optional[List[str]]
            List of completed steps
        recommendations_ready : bool
            Whether recommendations are ready
        preference_summary : Optional[Dict[str, Any]]
            Summary of preferences
        
        Returns:
        --------
        OnboardingResponse: Success response
        """
        return cls(
            success=True,
            message=message,
            completed_steps=completed_steps or [],
            recommendations_ready=recommendations_ready,
            preference_summary=preference_summary,
        )
    
    @classmethod
    def error_response(
        cls,
        message: str = "Onboarding failed",
        completed_steps: Optional[List[str]] = None,
    ) -> "OnboardingResponse":
        """
        Create an error onboarding response.
        
        Parameters:
        -----------
        message : str
            Error message
        completed_steps : Optional[List[str]]
            Steps completed so far
        
        Returns:
        --------
        OnboardingResponse: Error response
        """
        return cls(
            success=False,
            message=message,
            completed_steps=completed_steps or [],
            recommendations_ready=False,
        )


class OnboardingProgressResponse(BaseModel):
    """
    Response model for onboarding progress tracking.
    """
    
    user_id: int = Field(..., description="User ID")
    current_step: str = Field(..., description="Current onboarding step")
    completed_steps: List[str] = Field(..., description="Completed steps")
    progress_percentage: float = Field(..., description="Progress percentage", ge=0, le=100)
    is_complete: bool = Field(..., description="Whether onboarding is complete")
    next_step: Optional[str] = Field(None, description="Next step to complete")
    total_steps: int = Field(..., description="Total number of steps")
    
    @classmethod
    def from_onboarding_state(
        cls,
        user_id: int,
        current_step: str,
        completed_steps: List[str],
        total_steps: int,
    ) -> "OnboardingProgressResponse":
        """Create from onboarding state data."""
        progress = (len(completed_steps) / total_steps) * 100 if total_steps > 0 else 0
        is_complete = len(completed_steps) == total_steps
        
        # Find next step
        all_steps = [step.value for step in OnboardingStep]
        next_step = None
        for step in all_steps:
            if step not in completed_steps and step != OnboardingStep.COMPLETE.value:
                next_step = step
                break
        
        return cls(
            user_id=user_id,
            current_step=current_step,
            completed_steps=completed_steps,
            progress_percentage=min(100.0, progress),
            is_complete=is_complete,
            next_step=next_step if not is_complete else None,
            total_steps=total_steps,
        )


class OnboardingStepUpdateRequest(BaseModel):
    """
    Request model for updating onboarding step progress.
    """
    
    step: OnboardingStep = Field(..., description="Step to mark as completed")
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional data for the step"
    )
    
    @field_validator('step')
    @classmethod
    def validate_step(cls, v: OnboardingStep) -> OnboardingStep:
        """Validate the step is valid."""
        if v == OnboardingStep.COMPLETE:
            raise ValueError("Cannot manually mark COMPLETE step")
        return v


class OnboardingPreferenceSummary(BaseModel):
    """
    Summary of onboarding preferences for display.
    """
    
    total_genres: int = Field(..., description="Number of selected genres")
    total_authors: int = Field(..., description="Number of selected authors")
    total_books: int = Field(..., description="Number of selected books")
    reading_goal: str = Field(..., description="Reading goal")
    reading_goal_books: int = Field(..., description="Estimated books per year")
    language: str = Field(..., description="Preferred language")
    theme: str = Field(..., description="UI theme")
    top_genres: List[str] = Field(default_factory=list, description="Top 3 genres")
    top_authors: List[str] = Field(default_factory=list, description="Top 3 authors")
    top_books: List[str] = Field(default_factory=list, description="Top 3 books")
    
    @classmethod
    def from_preferences(
        cls,
        genres: List[str],
        authors: List[str],
        books: List[str],
        reading_goal: str,
        language: str,
        theme: str,
    ) -> "OnboardingPreferenceSummary":
        """
        Create a summary from preference data.
        
        Parameters:
        -----------
        genres : List[str]
            Selected genres
        authors : List[str]
            Selected authors
        books : List[str]
            Selected books
        reading_goal : str
            Reading goal
        language : str
            Preferred language
        theme : str
            UI theme
        
        Returns:
        --------
        OnboardingPreferenceSummary: Summary instance
        """
        return cls(
            total_genres=len(genres),
            total_authors=len(authors),
            total_books=len(books),
            reading_goal=reading_goal,
            reading_goal_books=ReadingGoal.get_book_count(reading_goal),
            language=Language.get_language_name(language),
            theme=theme,
            top_genres=genres[:3],
            top_authors=authors[:3],
            top_books=books[:3],
        )