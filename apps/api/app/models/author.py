"""
Author Model

SQLAlchemy model for authors with relationships to books,
biographical information, and popularity tracking.

Phase: Database Models
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
import re
import logging
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    Boolean,
    Index,
    UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

logger = logging.getLogger(__name__)


class Author(Base):
    """
    Author model for book authors and creators.
    
    Attributes:
    -----------
    id : int
        Primary key
    name : str
        Author's full name (required)
    bio : str
        Biographical information (optional)
    image_url : str
        URL to author's image (optional)
    birth_date : datetime
        Author's birth date (optional)
    death_date : datetime
        Author's death date (optional)
    nationality : str
        Author's nationality (optional)
    website : str
        Author's official website (optional)
    wikipedia_url : str
        Wikipedia page URL (optional)
    popularity_score : float
        Popularity score based on book ratings and sales
    total_books : int
        Number of books by this author
    average_rating : float
        Average rating across all books
    is_active : bool
        Whether the author is still active/publishing
    created_at : datetime
        Record creation timestamp
    updated_at : datetime
        Record last update timestamp
    """
    
    __tablename__ = "authors"
    
    # ============================================================
    # COLUMNS
    # ============================================================
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Primary key"
    )
    
    name = Column(
        String(255),
        nullable=False,
        index=True,
        doc="Author's full name"
    )
    
    bio = Column(
        Text,
        nullable=True,
        doc="Biographical information"
    )
    
    image_url = Column(
        String(512),
        nullable=True,
        doc="URL to author's image"
    )
    
    birth_date = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Author's birth date"
    )
    
    death_date = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Author's death date"
    )
    
    nationality = Column(
        String(100),
        nullable=True,
        index=True,
        doc="Author's nationality"
    )
    
    website = Column(
        String(255),
        nullable=True,
        doc="Author's official website"
    )
    
    wikipedia_url = Column(
        String(255),
        nullable=True,
        doc="Wikipedia page URL"
    )
    
    popularity_score = Column(
        Float,
        default=0.0,
        index=True,
        doc="Popularity score based on book ratings and sales"
    )
    
    total_books = Column(
        Integer,
        default=0,
        index=True,
        doc="Number of books by this author"
    )
    
    average_rating = Column(
        Float,
        default=0.0,
        doc="Average rating across all books"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        doc="Whether the author is still active/publishing"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="Record creation timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        doc="Record last update timestamp"
    )
    
    # ============================================================
    # RELATIONSHIPS
    # ============================================================
    
    # Relationship to books (if you have a Book model)
    #books = relationship("Book", back_populates="author", cascade="all, delete-orphan")
    
    # Relationship to user favorites (if you have a UserFavorites model)
    #favorited_by = relationship("UserFavorite", back_populates="author")
    
    # ============================================================
    # CONSTRAINTS & INDEXES
    # ============================================================
    
    __table_args__ = (
        # Unique constraint on name (case-insensitive)
        UniqueConstraint('name', name='uq_authors_name'),
        # Indexes for common queries
        Index('ix_authors_name_nationality', 'name', 'nationality'),
        Index('ix_authors_popularity_created', 'popularity_score', 'created_at'),
        #Index('ix_authors_total_books', 'total_books'),
        Index('ix_authors_average_rating', 'average_rating'),
    )
    
    # ============================================================
    # PROPERTIES
    # ============================================================
    
    @property
    def display_name(self) -> str:
        """Get the display name."""
        return self.name
    
    @property
    def is_deceased(self) -> bool:
        """Check if the author is deceased."""
        return self.death_date is not None
    
    @property
    def age(self) -> Optional[int]:
        """Calculate author's age (or age at death)."""
        if self.birth_date is None:
            return None
        target_date = self.death_date or datetime.now()
        return target_date.year - self.birth_date.year
    
    @property
    def years_active(self) -> Optional[int]:
        """Calculate years active."""
        if self.birth_date is None:
            return None
        if self.death_date:
            return self.death_date.year - self.birth_date.year
        return datetime.now().year - self.birth_date.year
    
    @property
    def rating_status(self) -> str:
        """Get rating status based on average rating."""
        if self.average_rating >= 4.5:
            return "excellent"
        elif self.average_rating >= 4.0:
            return "good"
        elif self.average_rating >= 3.5:
            return "average"
        elif self.average_rating >= 3.0:
            return "fair"
        else:
            return "poor"
    
    # ============================================================
    # CLASS METHODS
    # ============================================================
    
    @classmethod
    def create(
        cls,
        name: str,
        bio: Optional[str] = None,
        image_url: Optional[str] = None,
        birth_date: Optional[datetime] = None,
        death_date: Optional[datetime] = None,
        nationality: Optional[str] = None,
        website: Optional[str] = None,
        wikipedia_url: Optional[str] = None,
        popularity_score: float = 0.0,
        is_active: bool = True
    ) -> "Author":
        """
        Create a new author instance.
        
        Parameters:
        -----------
        name : str
            Author's full name
        bio : Optional[str]
            Biographical information
        image_url : Optional[str]
            URL to author's image
        birth_date : Optional[datetime]
            Author's birth date
        death_date : Optional[datetime]
            Author's death date
        nationality : Optional[str]
            Author's nationality
        website : Optional[str]
            Official website URL
        wikipedia_url : Optional[str]
            Wikipedia page URL
        popularity_score : float
            Initial popularity score
        is_active : bool
            Whether author is active
        
        Returns:
        --------
        Author: New author instance
        """
        return cls(
            name=name,
            bio=bio,
            image_url=image_url,
            birth_date=birth_date,
            death_date=death_date,
            nationality=nationality,
            website=website,
            wikipedia_url=wikipedia_url,
            popularity_score=popularity_score,
            is_active=is_active,
            total_books=0,
            average_rating=0.0
        )
    
    # ============================================================
    # INSTANCE METHODS
    # ============================================================
    
    def update_popularity(self, rating: float = None) -> None:
        """
        Update author's popularity score.
        
        Parameters:
        -----------
        rating : float, optional
            New rating to incorporate
        """
        # Simple popularity update logic
        if rating is not None:
            # Update average rating
            new_total = self.total_books + 1
            self.average_rating = ((self.average_rating * self.total_books) + rating) / new_total
            self.total_books = new_total
        
        # Update popularity score based on average rating and total books
        self.popularity_score = self.average_rating * (1 + (self.total_books / 100))
        logger.info(f"Updated popularity for {self.name}: {self.popularity_score:.2f}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert author to dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Author data
        """
        return {
            "id": self.id,
            "name": self.name,
            "bio": self.bio,
            "image_url": self.image_url,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "death_date": self.death_date.isoformat() if self.death_date else None,
            "nationality": self.nationality,
            "website": self.website,
            "wikipedia_url": self.wikipedia_url,
            "popularity_score": self.popularity_score,
            "total_books": self.total_books,
            "average_rating": self.average_rating,
            "rating_status": self.rating_status,
            "is_active": self.is_active,
            "age": self.age,
            "years_active": self.years_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_dict_public(self) -> Dict[str, Any]:
        """
        Convert author to public dictionary (limited fields).
        
        Returns:
        --------
        Dict[str, Any]: Public author data
        """
        return {
            "id": self.id,
            "name": self.name,
            "bio": self.bio,
            "image_url": self.image_url,
            "nationality": self.nationality,
            "popularity_score": self.popularity_score,
            "total_books": self.total_books,
            "average_rating": self.average_rating,
            "rating_status": self.rating_status
        }
    
    # ============================================================
    # VALIDATION HELPERS
    # ============================================================
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """
        Validate author name.
        
        Parameters:
        -----------
        name : str
            Author name to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        if not name or len(name.strip()) < 2:
            return False
        if len(name) > 255:
            return False
        return True
    
    @staticmethod
    def validate_url(url: Optional[str]) -> bool:
        """
        Validate URL format.
        
        Parameters:
        -----------
        url : Optional[str]
            URL to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        if url is None:
            return True
        pattern = r'^https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(/\S*)?$'
        return bool(re.match(pattern, url))
    
    # ============================================================
    # DUNDER METHODS
    # ============================================================
    
    def __repr__(self) -> str:
        """String representation of the author."""
        return f"<Author(id={self.id}, name='{self.name}', books={self.total_books}, rating={self.average_rating:.2f})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.name} ({self.total_books} books, {self.average_rating:.2f} avg)"


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("AUTHOR MODEL TEST")
    print("=" * 60)
    
    # Test 1: Create author
    print("\n📌 Test 1: Create Author")
    author = Author.create(
        name="Jane Austen",
        bio="English novelist known for her works of romantic fiction",
        birth_date=datetime(1775, 12, 16),
        death_date=datetime(1817, 7, 18),
        nationality="British",
        popularity_score=92.5
    )
    
    print(f"✅ Created: {author}")
    print(f"  Bio: {author.bio[:50]}...")
    print(f"  Nationality: {author.nationality}")
    print(f"  Age at death: {author.age} years")
    
    # Test 2: Update popularity
    print("\n📌 Test 2: Update Popularity")
    print(f"  Before - Books: {author.total_books}, Rating: {author.average_rating:.2f}")
    author.update_popularity(4.5)
    print(f"  After - Books: {author.total_books}, Rating: {author.average_rating:.2f}")
    print(f"  Popularity Score: {author.popularity_score:.2f}")
    print(f"  Rating Status: {author.rating_status}")
    
    # Test 3: To dict
    print("\n📌 Test 3: To Dict")
    data = author.to_dict()
    print(f"  Name: {data['name']}")
    print(f"  Age: {data['age']}")
    print(f"  Years Active: {data['years_active']}")
    print(f"  Rating Status: {data['rating_status']}")
    
    # Test 4: Validation
    print("\n📌 Test 4: Validation")
    print(f"  Valid name 'Jane Austen': {Author.validate_name('Jane Austen')}")
    print(f"  Valid name 'J': {Author.validate_name('J')}")
    print(f"  Valid URL 'https://example.com': {Author.validate_url('https://example.com')}")
    print(f"  Valid URL 'invalid': {Author.validate_url('invalid')}")
    
    print("\n✅ All tests completed!")