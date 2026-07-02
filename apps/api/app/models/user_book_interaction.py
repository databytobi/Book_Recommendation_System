"""
User-Book Interaction Model

SQLAlchemy model for tracking all types of user-book interactions including
views, clicks, ratings, reviews, saves, shares, and reading status.

Phase: Database Models
"""

from ctypes import Union
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
import json
import logging
from enum import Enum
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    Integer,
    Float,
    Boolean,
    Text,
    Index,
    UniqueConstraint,
    CheckConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

logger = logging.getLogger(__name__)


# ============================================================
# ENUMS
# ============================================================

class InteractionType(str, Enum):
    """Types of user-book interactions."""
    VIEW = "view"
    CLICK = "click"
    RATING = "rating"
    REVIEW = "review"
    SAVE = "save"
    SHARE = "share"
    READ = "read"
    WISHLIST = "wishlist"
    PURCHASE = "purchase"
    RECOMMEND = "recommend"
    DISMISS = "dismiss"


class ReadingStatus(str, Enum):
    """Reading status of a book."""
    NOT_STARTED = "not_started"
    READING = "reading"
    FINISHED = "finished"
    ABANDONED = "abandoned"
    WANT_TO_READ = "want_to_read"


class InteractionSource(str, Enum):
    """Source of the interaction."""
    DIRECT = "direct"
    RECOMMENDATION = "recommendation"
    SEARCH = "search"
    CATEGORY = "category"
    TRENDING = "trending"
    SOCIAL = "social"
    EXTERNAL = "external"


class UserBookInteraction(Base):
    """
    Model for tracking all user-book interactions.
    
    Attributes:
    -----------
    id : int
        Primary key
    user_id : str
        User identifier (UUID)
    isbn : str
        Book ISBN
    interaction_type : str
        Type of interaction (view, click, rating, review, save, share, read, wishlist, purchase, recommend, dismiss)
    reading_status : str
        Reading status (not_started, reading, finished, abandoned, want_to_read)
    rating_value : int
        Rating value (1-5) if rating interaction
    review_text : str
        Review text if review interaction
    review_title : str
        Review title
    progress : int
        Reading progress (0-100)
    current_page : int
        Current page number
    started_at : datetime
        When the user started reading
    finished_at : datetime
        When the user finished reading
    time_spent_seconds : int
        Total time spent reading in seconds
    source : str
        Source of interaction (direct, recommendation, search, category, trending, social, external)
    recommendation_type : str
        Type of recommendation that led to this interaction
    recommendation_score : float
        Score of the recommendation
    referer_url : str
        Referer URL
    device_type : str
        Device type (web, mobile, tablet)
    browser : str
        Browser information
    ip_address : str
        IP address of the user
    location : str
        User location
    metadata : str
        JSON string with additional metadata
    is_deleted : bool
        Soft delete flag
    created_at : datetime
        Creation timestamp
    updated_at : datetime
        Last update timestamp
    """
    
    __tablename__ = "user_book_interactions"
    
    # ============================================================
    # COLUMNS
    # ============================================================
    
    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        doc="Primary key"
    )
    
    user_id = Column(
        String(36),
        nullable=False,
        index=True,
        doc="User identifier (UUID)"
    )
    
    isbn = Column(
        String(13),
        nullable=False,
        index=True,
        doc="Book ISBN"
    )
    
    interaction_type = Column(
        String(20),
        nullable=False,
        index=True,
        doc="Type of interaction"
    )
    
    reading_status = Column(
        String(20),
        nullable=True,
        index=True,
        doc="Reading status"
    )
    
    rating_value = Column(
        Integer,
        nullable=True,
        doc="Rating value (1-5)"
    )
    
    review_text = Column(
        Text,
        nullable=True,
        doc="Review text"
    )
    
    review_title = Column(
        String(200),
        nullable=True,
        doc="Review title"
    )
    
    progress = Column(
        Integer,
        nullable=True,
        doc="Reading progress (0-100)"
    )
    
    current_page = Column(
        Integer,
        nullable=True,
        doc="Current page number"
    )
    
    started_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the user started reading"
    )
    
    finished_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the user finished reading"
    )
    
    time_spent_seconds = Column(
        Integer,
        nullable=True,
        doc="Total time spent reading in seconds"
    )
    
    source = Column(
        String(20),
        nullable=True,
        index=True,
        doc="Source of interaction"
    )
    
    recommendation_type = Column(
        String(20),
        nullable=True,
        doc="Type of recommendation that led to this interaction"
    )
    
    recommendation_score = Column(
        Float,
        nullable=True,
        doc="Score of the recommendation"
    )
    
    referer_url = Column(
        String(512),
        nullable=True,
        doc="Referer URL"
    )
    
    device_type = Column(
        String(20),
        nullable=True,
        doc="Device type: web, mobile, tablet"
    )
    
    browser = Column(
        String(50),
        nullable=True,
        doc="Browser information"
    )
    
    ip_address = Column(
        String(45),
        nullable=True,
        doc="IP address (IPv4 or IPv6)"
    )
    
    location = Column(
        String(100),
        nullable=True,
        doc="User location (city, country)"
    )
    
    meta_data = Column(
        "metadata",
        Text,
        nullable=True,
        doc="JSON string with additional metadata"
    )
    
    is_deleted = Column(
        Boolean,
        default=False,
        index=True,
        doc="Soft delete flag"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="Creation timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        doc="Last update timestamp"
    )
    
    # ============================================================
    # CONSTRAINTS & INDEXES
    # ============================================================
    
    __table_args__ = (
        # Composite indexes for common queries
        Index('ix_user_book_interactions_user_isbn', 'user_id', 'isbn'),
        Index('ix_user_book_interactions_user_type', 'user_id', 'interaction_type'),
        Index('ix_user_book_interactions_isbn_type', 'isbn', 'interaction_type'),
        Index('ix_user_book_interactions_status', 'reading_status'),
        Index('ix_user_book_interactions_rating', 'rating_value'),
        Index('ix_user_book_interactions_created_at', 'created_at'),
        Index('ix_user_book_interactions_user_created', 'user_id', 'created_at'),
        #Index('ix_user_book_interactions_source', 'source'),
        # Unique constraint to prevent duplicate interactions (one per type per user per book)
        UniqueConstraint(
            'user_id', 'isbn', 'interaction_type',
            name='uq_user_book_interaction'
        ),
        # Check constraint for rating range
        CheckConstraint(
            'rating_value IS NULL OR (rating_value >= 1 AND rating_value <= 5)',
            name='ck_rating_value_range'
        ),
        # Check constraint for progress range
        CheckConstraint(
            'progress IS NULL OR (progress >= 0 AND progress <= 100)',
            name='ck_progress_range'
        )
    )
    
    # ============================================================
    # PROPERTIES
    # ============================================================
    
    @property
    def is_rating(self) -> bool:
        """Check if this is a rating interaction."""
        return self.interaction_type == InteractionType.RATING
    
    @property
    def is_review(self) -> bool:
        """Check if this is a review interaction."""
        return self.interaction_type == InteractionType.REVIEW
    
    @property
    def is_save(self) -> bool:
        """Check if this is a save interaction."""
        return self.interaction_type == InteractionType.SAVE
    
    @property
    def is_read(self) -> bool:
        """Check if this is a read interaction."""
        return self.interaction_type == InteractionType.READ
    
    @property
    def is_finished(self) -> bool:
        """Check if the book has been finished."""
        return self.reading_status == ReadingStatus.FINISHED
    
    @property
    def is_reading(self) -> bool:
        """Check if the user is currently reading."""
        return self.reading_status == ReadingStatus.READING
    
    @property
    def has_review(self) -> bool:
        """Check if there is a review."""
        return bool(self.review_text and self.review_text.strip())
    
    @property
    def has_rating(self) -> bool:
        """Check if there is a rating."""
        return self.rating_value is not None
    
    @property
    def is_high_rating(self) -> bool:
        """Check if the rating is high (4 or 5)."""
        return self.has_rating and self.rating_value >= 4
    
    @property
    def is_low_rating(self) -> bool:
        """Check if the rating is low (1 or 2)."""
        return self.has_rating and self.rating_value <= 2
    
    @property
    def engagement_score(self) -> float:
        """
        Calculate engagement score based on interactions.
        
        Returns:
        --------
        float: Engagement score (0-1)
        """
        score = 0.0
        
        # Rating contributes
        if self.has_rating:
            score += 0.3
            if self.is_high_rating:
                score += 0.2
        
        # Review contributes
        if self.has_review:
            score += 0.2
        
        # Save contributes
        if self.is_save:
            score += 0.2
        
        # Reading progress contributes
        if self.progress is not None:
            score += (self.progress / 100) * 0.2
        
        return min(score, 1.0)
    
    @property
    def reading_days(self) -> Optional[int]:
        """Get the number of days spent reading."""
        if not self.started_at:
            return None
        end_date = self.finished_at or datetime.now(self.started_at.tzinfo)
        return (end_date - self.started_at).days
    
    @property
    def created_at_str(self) -> str:
        """Get formatted created_at string."""
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
    
    @property
    def week_day(self) -> Optional[str]:
        """Get the day of the week."""
        if not self.created_at:
            return None
        return self.created_at.strftime("%A")
    
    @property
    def hour(self) -> Optional[int]:
        """Get the hour of the interaction."""
        if not self.created_at:
            return None
        return self.created_at.hour
    
    # ============================================================
    # CLASS METHODS
    # ============================================================
    
    @classmethod
    def create(
        cls,
        user_id: str,
        isbn: str,
        interaction_type: Union[str, InteractionType],
        reading_status: Optional[Union[str, ReadingStatus]] = None,
        rating_value: Optional[int] = None,
        review_text: Optional[str] = None,
        review_title: Optional[str] = None,
        progress: Optional[int] = None,
        current_page: Optional[int] = None,
        source: Optional[Union[str, InteractionSource]] = None,
        recommendation_type: Optional[str] = None,
        recommendation_score: Optional[float] = None,
        referer_url: Optional[str] = None,
        device_type: Optional[str] = None,
        browser: Optional[str] = None,
        ip_address: Optional[str] = None,
        location: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "UserBookInteraction":
        """
        Create a new user-book interaction.
        
        Parameters:
        -----------
        user_id : str
            User identifier
        isbn : str
            Book ISBN
        interaction_type : str
            Type of interaction
        reading_status : Optional[str]
            Reading status
        rating_value : Optional[int]
            Rating value (1-5)
        review_text : Optional[str]
            Review text
        review_title : Optional[str]
            Review title
        progress : Optional[int]
            Reading progress (0-100)
        current_page : Optional[int]
            Current page number
        source : Optional[str]
            Source of interaction
        recommendation_type : Optional[str]
            Type of recommendation
        recommendation_score : Optional[float]
            Recommendation score
        referer_url : Optional[str]
            Referer URL
        device_type : Optional[str]
            Device type
        browser : Optional[str]
            Browser information
        ip_address : Optional[str]
            IP address
        location : Optional[str]
            User location
        metadata : Optional[Dict[str, Any]]
            Additional metadata
        
        Returns:
        --------
        UserBookInteraction: New interaction record
        
        Raises:
        -------
        ValueError: If validation fails
        """
        # Validate
        if rating_value is not None and not (1 <= rating_value <= 5):
            raise ValueError("Rating must be between 1 and 5")
        if progress is not None and not (0 <= progress <= 100):
            raise ValueError("Progress must be between 0 and 100")
        
        # Convert enums to strings
        if isinstance(interaction_type, InteractionType):
            interaction_type = interaction_type.value
        if isinstance(reading_status, ReadingStatus):
            reading_status = reading_status.value
        if isinstance(source, InteractionSource):
            source = source.value
        
        return cls(
            user_id=user_id,
            isbn=isbn,
            interaction_type=interaction_type,
            reading_status=reading_status,
            rating_value=rating_value,
            review_text=review_text,
            review_title=review_title,
            progress=progress,
            current_page=current_page,
            source=source,
            recommendation_type=recommendation_type,
            recommendation_score=recommendation_score,
            referer_url=referer_url,
            device_type=device_type,
            browser=browser,
            ip_address=ip_address,
            location=location,
            meta_data=json.dumps(metadata) if metadata else None
        )
    
    @classmethod
    def create_rating(
        cls,
        user_id: str,
        isbn: str,
        rating_value: int,
        **kwargs
    ) -> "UserBookInteraction":
        """Create a rating interaction."""
        return cls.create(
            user_id=user_id,
            isbn=isbn,
            interaction_type=InteractionType.RATING,
            rating_value=rating_value,
            **kwargs
        )
    
    @classmethod
    def create_review(
        cls,
        user_id: str,
        isbn: str,
        review_text: str,
        review_title: Optional[str] = None,
        **kwargs
    ) -> "UserBookInteraction":
        """Create a review interaction."""
        return cls.create(
            user_id=user_id,
            isbn=isbn,
            interaction_type=InteractionType.REVIEW,
            review_text=review_text,
            review_title=review_title,
            **kwargs
        )
    
    @classmethod
    def create_save(
        cls,
        user_id: str,
        isbn: str,
        **kwargs
    ) -> "UserBookInteraction":
        """Create a save interaction."""
        return cls.create(
            user_id=user_id,
            isbn=isbn,
            interaction_type=InteractionType.SAVE,
            **kwargs
        )
    
    @classmethod
    def create_read(
        cls,
        user_id: str,
        isbn: str,
        reading_status: Union[str, ReadingStatus] = ReadingStatus.READING,
        progress: Optional[int] = None,
        **kwargs
    ) -> "UserBookInteraction":
        """Create a read interaction."""
        return cls.create(
            user_id=user_id,
            isbn=isbn,
            interaction_type=InteractionType.READ,
            reading_status=reading_status,
            progress=progress,
            **kwargs
        )
    
    # ============================================================
    # INSTANCE METHODS
    # ============================================================
    
    def update_rating(self, rating_value: int) -> None:
        """
        Update the rating value.
        
        Parameters:
        -----------
        rating_value : int
            New rating value (1-5)
        """
        if not (1 <= rating_value <= 5):
            raise ValueError("Rating must be between 1 and 5")
        self.rating_value = rating_value
        self.updated_at = func.now()
        logger.info(f"Rating updated for user {self.user_id}, book {self.isbn}: {rating_value}/5")
    
    def update_review(self, review_text: str, review_title: Optional[str] = None) -> None:
        """
        Update the review.
        
        Parameters:
        -----------
        review_text : str
            New review text
        review_title : Optional[str]
            New review title
        """
        self.review_text = review_text
        if review_title is not None:
            self.review_title = review_title
        self.updated_at = func.now()
        logger.info(f"Review updated for user {self.user_id}, book {self.isbn}")
    
    def update_reading_progress(self, progress: int, current_page: Optional[int] = None) -> None:
        """
        Update reading progress.
        
        Parameters:
        -----------
        progress : int
            New progress (0-100)
        current_page : Optional[int]
            Current page number
        """
        if not (0 <= progress <= 100):
            raise ValueError("Progress must be between 0 and 100")
        self.progress = progress
        if current_page is not None:
            self.current_page = current_page
        
        # Update reading status based on progress
        if progress == 100:
            self.reading_status = ReadingStatus.FINISHED
            self.finished_at = func.now()
        elif progress > 0:
            self.reading_status = ReadingStatus.READING
            if not self.started_at:
                self.started_at = func.now()
        
        self.updated_at = func.now()
        logger.info(f"Reading progress updated for user {self.user_id}, book {self.isbn}: {progress}%")
    
    def mark_finished(self) -> None:
        """Mark the book as finished."""
        self.reading_status = ReadingStatus.FINISHED
        self.progress = 100
        self.finished_at = func.now()
        self.updated_at = func.now()
        logger.info(f"Book marked as finished for user {self.user_id}, book {self.isbn}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata as dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Metadata dictionary
        """
        if not self.meta_data:
            return {}
        try:
            return json.loads(self.meta_data)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in metadata for interaction {self.id}")
            return {}
    
    def update_metadata(self, updates: Dict[str, Any]) -> None:
        """
        Update metadata fields.
        
        Parameters:
        -----------
        updates : Dict[str, Any]
            Dictionary of metadata updates
        """
        current = self.get_metadata()
        current.update(updates)
        self.metadata = json.dumps(current)
        self.updated_at = func.now()
    
    def soft_delete(self) -> None:
        """Soft delete the interaction."""
        self.is_deleted = True
        self.updated_at = func.now()
        logger.info(f"Interaction {self.id} soft deleted")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert interaction to dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Interaction data
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "isbn": self.isbn,
            "interaction_type": self.interaction_type,
            "reading_status": self.reading_status,
            "rating_value": self.rating_value,
            "review_text": self.review_text,
            "review_title": self.review_title,
            "progress": self.progress,
            "current_page": self.current_page,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "time_spent_seconds": self.time_spent_seconds,
            "reading_days": self.reading_days,
            "source": self.source,
            "recommendation_type": self.recommendation_type,
            "recommendation_score": self.recommendation_score,
            "referer_url": self.referer_url,
            "device_type": self.device_type,
            "browser": self.browser,
            "ip_address": self.ip_address,
            "location": self.location,
            "metadata": self.get_metadata(),
            "engagement_score": self.engagement_score,
            "is_rating": self.is_rating,
            "is_review": self.is_review,
            "is_save": self.is_save,
            "is_read": self.is_read,
            "is_finished": self.is_finished,
            "is_reading": self.is_reading,
            "has_review": self.has_review,
            "has_rating": self.has_rating,
            "is_high_rating": self.is_high_rating,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "week_day": self.week_day,
            "hour": self.hour
        }
    
    def to_analytics_dict(self) -> Dict[str, Any]:
        """
        Convert to analytics-friendly dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Analytics data
        """
        return {
            "user_id": self.user_id,
            "isbn": self.isbn,
            "interaction_type": self.interaction_type,
            "reading_status": self.reading_status,
            "rating_value": self.rating_value,
            "progress": self.progress,
            "source": self.source,
            "recommendation_type": self.recommendation_type,
            "device": self.device_type,
            "engagement_score": self.engagement_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "week_day": self.week_day,
            "hour": self.hour
        }
    
    # ============================================================
    # VALIDATION HELPERS
    # ============================================================
    
    @staticmethod
    def validate_isbn(isbn: str) -> bool:
        """
        Validate ISBN format.
        
        Parameters:
        -----------
        isbn : str
            ISBN to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        isbn = isbn.replace('-', '').replace(' ', '')
        if len(isbn) not in [10, 13]:
            return False
        if not isbn.isdigit() and not (len(isbn) == 10 and isbn[:-1].isdigit() and isbn[-1].upper() == 'X'):
            return False
        return True
    
    @staticmethod
    def validate_interaction_type(interaction_type: str) -> bool:
        """
        Validate interaction type.
        
        Parameters:
        -----------
        interaction_type : str
            Interaction type to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        valid_types = [t.value for t in InteractionType]
        return interaction_type in valid_types
    
    @staticmethod
    def validate_reading_status(reading_status: str) -> bool:
        """
        Validate reading status.
        
        Parameters:
        -----------
        reading_status : str
            Reading status to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        valid_statuses = [s.value for s in ReadingStatus]
        return reading_status in valid_statuses
    
    # ============================================================
    # DUNDER METHODS
    # ============================================================
    
    def __repr__(self) -> str:
        """String representation of the interaction."""
        return f"<UserBookInteraction(id={self.id}, user={self.user_id}, isbn='{self.isbn}', type='{self.interaction_type}')>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        parts = [f"User {self.user_id}", f"book {self.isbn}"]
        if self.interaction_type:
            parts.append(f"type: {self.interaction_type}")
        if self.rating_value:
            parts.append(f"rating: {self.rating_value}/5")
        if self.progress is not None:
            parts.append(f"progress: {self.progress}%")
        return " ".join(parts)


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    import json
    from datetime import datetime
    
    print("=" * 60)
    print("USER-BOOK INTERACTION MODEL TEST")
    print("=" * 60)
    
    # Test 1: Create rating
    print("\n📌 Test 1: Create Rating")
    interaction = UserBookInteraction.create_rating(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        isbn="0446310786",
        rating_value=5,
        source=InteractionSource.RECOMMENDATION,
        recommendation_type="hybrid",
        recommendation_score=0.85,
        device_type="web",
        metadata={"page": "recommendations", "section": "featured"}
    )
    
    print(f"✅ Created rating: {interaction}")
    print(f"  Rating: {interaction.rating_value}/5")
    print(f"  Source: {interaction.source}")
    print(f"  Metadata: {interaction.get_metadata()}")
    
    # Test 2: Create review
    print("\n📌 Test 2: Create Review")
    review = UserBookInteraction.create_review(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        isbn="0439139597",
        review_title="Amazing book!",
        review_text="This is one of the best fantasy books I've ever read. The world-building is incredible.",
        rating_value=5,
        source=InteractionSource.SEARCH
    )
    
    print(f"✅ Created review: {review}")
    print(f"  Review title: {review.review_title}")
    print(f"  Has review: {review.has_review}")
    print(f"  Is high rating: {review.is_high_rating}")
    
    # Test 3: Create read interaction
    print("\n📌 Test 3: Create Read Interaction")
    read = UserBookInteraction.create_read(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        isbn="0142001740",
        reading_status=ReadingStatus.READING,
        progress=45,
        current_page=128
    )
    
    print(f"✅ Created read: {read}")
    print(f"  Progress: {read.progress}%")
    print(f"  Current page: {read.current_page}")
    print(f"  Reading status: {read.reading_status}")
    
    # Test 4: Update progress
    print("\n📌 Test 4: Update Progress")
    read.update_reading_progress(100, current_page=285)
    print(f"  Updated progress: {read.progress}%")
    print(f"  Reading status: {read.reading_status}")
    print(f"  Is finished: {read.is_finished}")
    
    # Test 5: Engagement score
    print("\n📌 Test 5: Engagement Score")
    print(f"  Rating engagement: {interaction.engagement_score:.2f}")
    print(f"  Review engagement: {review.engagement_score:.2f}")
    print(f"  Read engagement: {read.engagement_score:.2f}")
    
    # Test 6: Analytics data
    print("\n📌 Test 6: Analytics Data")
    analytics = interaction.to_analytics_dict()
    print(f"  Analytics: {json.dumps(analytics, indent=2)}")
    
    # Test 7: Validation
    print("\n📌 Test 7: Validation")
    print(f"  Valid ISBN '0446310786': {UserBookInteraction.validate_isbn('0446310786')}")
    print(f"  Valid type 'rating': {UserBookInteraction.validate_interaction_type('rating')}")
    print(f"  Valid type 'invalid': {UserBookInteraction.validate_interaction_type('invalid')}")
    print(f"  Valid status 'reading': {UserBookInteraction.validate_reading_status('reading')}")
    
    print("\n✅ All tests completed!")