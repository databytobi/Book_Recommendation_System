"""
Onboarding Preference Models

Pydantic models for user preference collection during onboarding.
Supports weighted preferences for authors, books, and genres.

Phase: Schemas / Onboarding
"""

from typing import Dict, List, Optional, Set, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic import ConfigDict


class PreferenceType(str, Enum):
    """Types of preferences that can be collected."""
    GENRE = "genre"
    AUTHOR = "author"
    BOOK = "book"


class WeightedAuthor(BaseModel):
    """
    Author selected by the user during onboarding with preference weight.
    
    Attributes:
    -----------
    id : int
        Author ID from the database
    name : str
        Author name (optional, for display)
    weight : float
        Preference weight between 0.0 and 1.0
        - 1.0: Strong preference
        - 0.5: Moderate preference
        - 0.0: No preference
    """
    
    id: int = Field(..., description="Author ID", gt=0)
    name: Optional[str] = Field(None, description="Author name", max_length=255)
    weight: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Preference weight (0.0 to 1.0)"
    )
    
    @field_validator('id')
    @classmethod
    def validate_author_id(cls, v: int) -> int:
        """Validate author ID is positive."""
        if v <= 0:
            raise ValueError("Author ID must be positive")
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean author name."""
        if v is not None:
            cleaned = v.strip()
            if cleaned and len(cleaned) > 255:
                raise ValueError("Author name cannot exceed 255 characters")
            return cleaned
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "id": self.id,
            "name": self.name,
            "weight": self.weight
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WeightedAuthor":
        """Create WeightedAuthor from dictionary."""
        return cls(
            id=data.get("id", 0),
            name=data.get("name"),
            weight=data.get("weight", 1.0)
        )


class WeightedBook(BaseModel):
    """
    Book selected by the user during onboarding with preference weight.
    
    Attributes:
    -----------
    isbn : str
        Book ISBN (10 or 13 digits)
    title : str
        Book title (optional, for display)
    weight : float
        Preference weight between 0.0 and 1.0
    """
    
    isbn: str = Field(..., description="Book ISBN", min_length=10, max_length=13)
    title: Optional[str] = Field(None, description="Book title", max_length=500)
    weight: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Preference weight (0.0 to 1.0)"
    )
    
    @field_validator('isbn')
    @classmethod
    def validate_isbn(cls, v: str) -> str:
        """Validate ISBN format (10 or 13 digits, with optional hyphens)."""
        cleaned = v.replace('-', '').replace(' ', '')
        
        if len(cleaned) not in [10, 13]:
            raise ValueError("ISBN must be 10 or 13 digits")
        
        if not cleaned.isdigit():
            raise ValueError("ISBN must contain only digits and hyphens")
        
        return cleaned
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean book title."""
        if v is not None:
            cleaned = v.strip()
            if cleaned and len(cleaned) > 500:
                raise ValueError("Book title cannot exceed 500 characters")
            return cleaned
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "isbn": self.isbn,
            "title": self.title,
            "weight": self.weight
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WeightedBook":
        """Create WeightedBook from dictionary."""
        return cls(
            isbn=data.get("isbn", ""),
            title=data.get("title"),
            weight=data.get("weight", 1.0)
        )


class PreferenceValidationResult(BaseModel):
    """Result of preference validation."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class RecommendationPreference(BaseModel):
    """
    Complete recommendation profile for a user.
    
    Stores user preferences collected during onboarding.
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "genres": {
                    "fiction": 0.9,
                    "science_fiction": 0.8,
                    "fantasy": 0.7
                },
                "authors": [
                    {"id": 1, "weight": 1.0},
                    {"id": 2, "weight": 0.8}
                ],
                "favorite_books": [
                    {"isbn": "9780439139601", "weight": 1.0},
                    {"isbn": "9780141439518", "weight": 0.9}
                ],
                "version": 1,
                "created_at": "2026-06-26T10:00:00.000Z"
            }
        }
    )
    
    # User preferences
    genres: Dict[str, float] = Field(
        default_factory=dict,
        description="Genre preferences with weights (0.0 to 1.0)"
    )
    
    authors: List[WeightedAuthor] = Field(
        default_factory=list,
        description="Author preferences with weights",
        max_length=100
    )
    
    favorite_books: List[WeightedBook] = Field(
        default_factory=list,
        description="Book preferences with weights",
        max_length=50
    )
    
    # Metadata
    version: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Preference version"
    )
    
    created_at: Optional[datetime] = Field(
        None,
        description="When the preferences were created"
    )
    
    updated_at: Optional[datetime] = Field(
        None,
        description="When the preferences were last updated"
    )
    
    # Validation
    @field_validator('genres')
    @classmethod
    def validate_genres(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validate genre weights are within bounds and genre names are valid."""
        if not v:
            return v
        
        for genre, weight in v.items():
            # Validate genre name
            if not genre or not genre.strip():
                raise ValueError("Genre name cannot be empty")
            if len(genre) > 50:
                raise ValueError(f"Genre name '{genre[:20]}...' exceeds 50 characters")
            # Validate weight
            if not 0.0 <= weight <= 1.0:
                raise ValueError(f"Weight for genre '{genre}' must be between 0.0 and 1.0")
        
        return {k.strip(): v for k, v in v.items()}
    
    @model_validator(mode='after')
    def validate_preferences(self) -> 'RecommendationPreference':
        """Validate the overall preference state."""
        # Ensure at least one preference type is set
        if not self.genres and not self.authors and not self.favorite_books:
            raise ValueError("At least one preference type must be provided")
        
        # Validate author count
        if len(self.authors) > 100:
            raise ValueError("Maximum 100 authors allowed")
        
        # Validate book count
        if len(self.favorite_books) > 50:
            raise ValueError("Maximum 50 books allowed")
        
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "genres": self.genres,
            "authors": [author.to_dict() for author in self.authors],
            "favorite_books": [book.to_dict() for book in self.favorite_books],
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecommendationPreference':
        """Create RecommendationPreference from dictionary."""
        return cls(
            genres=data.get("genres", {}),
            authors=[
                WeightedAuthor.from_dict(a) 
                for a in data.get("authors", [])
            ],
            favorite_books=[
                WeightedBook.from_dict(b) 
                for b in data.get("favorite_books", [])
            ],
            version=data.get("version", 1),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def get_top_genres(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top genres by weight."""
        if not self.genres:
            return []
        
        sorted_genres = sorted(
            self.genres.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {"genre": genre, "weight": weight}
            for genre, weight in sorted_genres[:limit]
        ]
    
    def get_top_authors(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top authors by weight."""
        sorted_authors = sorted(
            self.authors,
            key=lambda x: x.weight,
            reverse=True
        )
        
        return [
            {"id": author.id, "name": author.name, "weight": author.weight}
            for author in sorted_authors[:limit]
        ]
    
    def get_top_books(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top books by weight."""
        sorted_books = sorted(
            self.favorite_books,
            key=lambda x: x.weight,
            reverse=True
        )
        
        return [
            {"isbn": book.isbn, "title": book.title, "weight": book.weight}
            for book in sorted_books[:limit]
        ]
    
    def add_genre(self, genre: str, weight: float = 1.0) -> None:
        """Add or update a genre preference."""
        if not genre or not genre.strip():
            raise ValueError("Genre cannot be empty")
        
        if not 0.0 <= weight <= 1.0:
            raise ValueError("Weight must be between 0.0 and 1.0")
        
        self.genres[genre.strip()] = weight
        self.updated_at = datetime.now()
    
    def remove_genre(self, genre: str) -> None:
        """Remove a genre preference."""
        if genre in self.genres:
            del self.genres[genre]
            self.updated_at = datetime.now()
    
    def add_author(self, author_id: int, weight: float = 1.0) -> None:
        """Add or update an author preference."""
        # Check if author already exists
        for existing in self.authors:
            if existing.id == author_id:
                existing.weight = weight
                self.updated_at = datetime.now()
                return
        
        # Add new author
        self.authors.append(WeightedAuthor(id=author_id, weight=weight))
        self.updated_at = datetime.now()
    
    def remove_author(self, author_id: int) -> None:
        """Remove an author preference."""
        self.authors = [a for a in self.authors if a.id != author_id]
        self.updated_at = datetime.now()
    
    def add_book(self, isbn: str, weight: float = 1.0) -> None:
        """Add or update a book preference."""
        # Clean ISBN
        cleaned_isbn = isbn.replace('-', '').replace(' ', '')
        
        # Check if book already exists
        for existing in self.favorite_books:
            if existing.isbn == cleaned_isbn:
                existing.weight = weight
                self.updated_at = datetime.now()
                return
        
        # Add new book
        self.favorite_books.append(WeightedBook(isbn=cleaned_isbn, weight=weight))
        self.updated_at = datetime.now()
    
    def remove_book(self, isbn: str) -> None:
        """Remove a book preference."""
        cleaned_isbn = isbn.replace('-', '').replace(' ', '')
        self.favorite_books = [b for b in self.favorite_books if b.isbn != cleaned_isbn]
        self.updated_at = datetime.now()
    
    def get_preference_summary(self) -> Dict[str, Any]:
        """Get a summary of the user's preferences."""
        return {
            "total_genres": len(self.genres),
            "total_authors": len(self.authors),
            "total_books": len(self.favorite_books),
            "top_genres": self.get_top_genres(3),
            "top_authors": self.get_top_authors(3),
            "top_books": self.get_top_books(3),
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def validate_complete(self) -> PreferenceValidationResult:
        """Validate all preferences and return a detailed result."""
        errors = []
        warnings = []
        
        # Check if there are any preferences
        if not self.genres and not self.authors and not self.favorite_books:
            errors.append("At least one preference type must be provided")
        
        # Validate genre weights
        for genre, weight in self.genres.items():
            if not 0.0 <= weight <= 1.0:
                errors.append(f"Genre '{genre}' has invalid weight: {weight}")
        
        # Validate author weights
        for author in self.authors:
            if not 0.0 <= author.weight <= 1.0:
                errors.append(f"Author {author.id} has invalid weight: {author.weight}")
        
        # Validate book weights
        for book in self.favorite_books:
            if not 0.0 <= book.weight <= 1.0:
                errors.append(f"Book {book.isbn} has invalid weight: {book.weight}")
        
        # Warnings for preferences with low weights
        if len(self.authors) < 3:
            warnings.append("Few authors selected, recommendations may be limited")
        
        if len(self.favorite_books) < 3:
            warnings.append("Few books selected, recommendations may be limited")
        
        if not self.genres and len(self.authors) < 5:
            warnings.append("No genres selected, consider adding some for better recommendations")
        
        return PreferenceValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


# ============================================================
# ONBOARDING PREFERENCE SCHEMAS
# ============================================================

class OnboardingStep(str, Enum):
    """Steps in the onboarding process."""
    WELCOME = "welcome"
    GENRE_SELECTION = "genres"
    AUTHOR_SELECTION = "authors"
    BOOK_SELECTION = "books"
    COMPLETE = "complete"


class OnboardingProgress(BaseModel):
    """Track user progress through onboarding."""
    
    step: OnboardingStep = Field(
        default=OnboardingStep.WELCOME,
        description="Current onboarding step"
    )
    completed_steps: List[OnboardingStep] = Field(
        default_factory=list,
        description="Steps that have been completed"
    )
    preferences: RecommendationPreference = Field(
        default_factory=RecommendationPreference,
        description="User preferences collected so far"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Last update timestamp"
    )
    
    @field_validator('completed_steps')
    @classmethod
    def validate_steps(cls, v: List[OnboardingStep]) -> List[OnboardingStep]:
        """Validate that steps are in order."""
        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("Steps must not contain duplicates")
        return v
    
    def complete_step(self, step: OnboardingStep) -> None:
        """Mark a step as completed."""
        if step not in self.completed_steps:
            self.completed_steps.append(step)
            self.step = self._get_next_step()
            self.updated_at = datetime.now()
    
    def _get_next_step(self) -> OnboardingStep:
        """Get the next onboarding step."""
        step_order = [s for s in OnboardingStep]
        
        for s in step_order:
            if s not in self.completed_steps and s != OnboardingStep.COMPLETE:
                return s
        
        return OnboardingStep.COMPLETE
    
    @property
    def is_complete(self) -> bool:
        """Check if onboarding is complete."""
        return OnboardingStep.COMPLETE in self.completed_steps
    
    @property
    def progress_percentage(self) -> float:
        """Calculate onboarding progress percentage."""
        total_steps = len(OnboardingStep) - 1  # Exclude COMPLETE
        completed = len(self.completed_steps)
        return min(100.0, (completed / total_steps) * 100)