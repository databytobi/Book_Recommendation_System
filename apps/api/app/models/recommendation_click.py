"""
Recommendation Click Model

SQLAlchemy model for tracking user interactions with recommendations.
Supports click tracking, feedback collection, and interaction analysis.

Phase: Database Models
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
import logging
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    Integer,
    Float,
    Boolean,
    Text,
    ForeignKey,
    Index,
    UniqueConstraint,
    CheckConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

logger = logging.getLogger(__name__)


class RecommendationClick(Base):
    """
    Model for tracking user clicks and interactions with recommendations.
    
    Attributes:
    -----------
    id : int
        Primary key
    user_id : str
        User identifier (UUID)
    isbn : str
        Book ISBN
    session_id : str
        Session identifier for tracking user sessions
    recommendation_type : str
        Type of recommendation (user, similar, search, trending, hybrid)
    rank : int
        Position of the book in the recommendation list (1-based)
    score : float
        Recommendation score at the time of click
    is_clicked : bool
        Whether the user clicked on the recommendation
    is_saved : bool
        Whether the user saved the recommendation
    is_rated : bool
        Whether the user rated the book
    rating_value : int
        Rating value if rated (1-5)
    feedback : str
        User feedback text
    metadata : str
        JSON string with additional metadata
    device_type : str
        Type of device (web, mobile, tablet)
    browser : str
        Browser information
    ip_address : str
        IP address of the user
    created_at : datetime
        Click timestamp
    updated_at : datetime
        Last update timestamp
    """
    
    __tablename__ = "recommendation_clicks"
    
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
        nullable=True,
        index=True,
        doc="User identifier (UUID)"
    )
    
    isbn = Column(
        String(13),
        nullable=False,
        index=True,
        doc="Book ISBN"
    )
    
    session_id = Column(
        String(64),
        nullable=True,
        index=True,
        doc="Session identifier"
    )
    
    recommendation_type = Column(
        String(20),
        nullable=True,
        index=True,
        doc="Type of recommendation: user, similar, search, trending, hybrid"
    )
    
    rank = Column(
        Integer,
        nullable=True,
        doc="Position in recommendation list (1-based)"
    )
    
    score = Column(
        Float,
        nullable=True,
        doc="Recommendation score at time of click"
    )
    
    is_clicked = Column(
        Boolean,
        default=True,
        doc="Whether the user clicked on the recommendation"
    )
    
    is_saved = Column(
        Boolean,
        default=False,
        doc="Whether the user saved the recommendation"
    )
    
    is_rated = Column(
        Boolean,
        default=False,
        doc="Whether the user rated the book"
    )
    
    rating_value = Column(
        Integer,
        nullable=True,
        doc="Rating value (1-5)"
    )
    
    feedback = Column(
        Text,
        nullable=True,
        doc="User feedback text"
    )
    
    meta_data = Column(
        "metadata",
        Text,
        nullable=True,
        doc="JSON string with additional metadata"
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
    
    referer_url = Column(
        String(512),
        nullable=True,
        doc="Referer URL"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="Click timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        doc="Last update timestamp"
    )
    
    # ============================================================
    # RELATIONSHIPS
    # ============================================================
    
    # Relationship to books (if you have a Book model)
    # book = relationship("Book", back_populates="recommendation_clicks")
    
    # ============================================================
    # CONSTRAINTS & INDEXES
    # ============================================================
    
    __table_args__ = (
        # Composite indexes for common queries
        Index('ix_recommendation_clicks_user_type', 'user_id', 'recommendation_type'),
        Index('ix_recommendation_clicks_isbn_type', 'isbn', 'recommendation_type'),
        Index('ix_recommendation_clicks_user_created', 'user_id', 'created_at'),
        Index('ix_recommendation_clicks_session_created', 'session_id', 'created_at'),
        Index('ix_recommendation_clicks_created_at', 'created_at'),
        # Unique constraint to prevent duplicate clicks (optional)
        # UniqueConstraint('user_id', 'isbn', 'session_id', name='uq_recommendation_click')
    )
    
    # ============================================================
    # PROPERTIES
    # ============================================================
    
    @property
    def has_rating(self) -> bool:
        """Check if the click has a rating."""
        return self.is_rated and self.rating_value is not None
    
    @property
    def has_feedback(self) -> bool:
        """Check if the click has feedback."""
        return bool(self.feedback and self.feedback.strip())
    
    @property
    def is_positive_feedback(self) -> Optional[bool]:
        """Check if the rating is positive (4 or 5)."""
        if not self.has_rating:
            return None
        return self.rating_value >= 4
    
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
        """Get the hour of the click."""
        if not self.created_at:
            return None
        return self.created_at.hour
    
    # ============================================================
    # CLASS METHODS
    # ============================================================
    
    @classmethod
    def create(
        cls,
        user_id: Optional[str],
        isbn: str,
        session_id: Optional[str] = None,
        recommendation_type: Optional[str] = None,
        rank: Optional[int] = None,
        score: Optional[float] = None,
        device_type: Optional[str] = None,
        browser: Optional[str] = None,
        ip_address: Optional[str] = None,
        referer_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "RecommendationClick":
        """
        Create a new recommendation click record.
        
        Parameters:
        -----------
        user_id : Optional[str]
            User identifier
        isbn : str
            Book ISBN
        session_id : Optional[str]
            Session identifier
        recommendation_type : Optional[str]
            Type of recommendation
        rank : Optional[int]
            Position in recommendation list
        score : Optional[float]
            Recommendation score
        device_type : Optional[str]
            Device type
        browser : Optional[str]
            Browser information
        ip_address : Optional[str]
            IP address
        referer_url : Optional[str]
            Referer URL
        metadata : Optional[Dict[str, Any]]
            Additional metadata
        
        Returns:
        --------
        RecommendationClick: New click record
        """
        import json
        
        return cls(
            user_id=user_id,
            isbn=isbn,
            session_id=session_id,
            recommendation_type=recommendation_type,
            rank=rank,
            score=score,
            is_clicked=True,
            device_type=device_type,
            browser=browser,
            ip_address=ip_address,
            referer_url=referer_url,
            meta_data=json.dumps(metadata) if metadata else None
        )
    
    # ============================================================
    # INSTANCE METHODS
    # ============================================================
    
    def record_rating(self, rating_value: int) -> None:
        """
        Record a rating for the recommendation.
        
        Parameters:
        -----------
        rating_value : int
            Rating value (1-5)
        
        Raises:
        -------
        ValueError: If rating is not between 1 and 5
        """
        if not 1 <= rating_value <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        self.is_rated = True
        self.rating_value = rating_value
        self.updated_at = func.now()
        logger.info(f"Rating recorded for ISBN {self.isbn}: {rating_value}/5")
    
    def record_feedback(self, feedback: str) -> None:
        """
        Record user feedback.
        
        Parameters:
        -----------
        feedback : str
            User feedback text
        """
        self.feedback = feedback
        self.updated_at = func.now()
        logger.info(f"Feedback recorded for ISBN {self.isbn}")
    
    def mark_saved(self) -> None:
        """Mark the recommendation as saved."""
        self.is_saved = True
        self.updated_at = func.now()
        logger.info(f"Book {self.isbn} saved by user {self.user_id}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata as dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Metadata dictionary
        """
        import json
        if not self.meta_data:
            return {}
        try:
            return json.loads(self.meta_data)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in metadata for click {self.id}")
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
        import json
        self.meta_data = json.dumps(current)
        self.updated_at = func.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert click to dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Click data
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "isbn": self.isbn,
            "session_id": self.session_id,
            "recommendation_type": self.recommendation_type,
            "rank": self.rank,
            "score": self.score,
            "is_clicked": self.is_clicked,
            "is_saved": self.is_saved,
            "is_rated": self.is_rated,
            "rating_value": self.rating_value,
            "feedback": self.feedback,
            "metadata": self.get_metadata(),
            "device_type": self.device_type,
            "browser": self.browser,
            "ip_address": self.ip_address,
            "referer_url": self.referer_url,
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
            "type": self.recommendation_type,
            "rank": self.rank,
            "score": self.score,
            "clicked": self.is_clicked,
            "saved": self.is_saved,
            "rated": self.is_rated,
            "rating": self.rating_value,
            "device": self.device_type,
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
        # Remove hyphens and spaces
        isbn = isbn.replace('-', '').replace(' ', '')
        if len(isbn) not in [10, 13]:
            return False
        if not isbn.isdigit() and not (len(isbn) == 10 and isbn[:-1].isdigit() and isbn[-1].upper() == 'X'):
            return False
        return True
    
    @staticmethod
    def validate_rating(rating: int) -> bool:
        """
        Validate rating value.
        
        Parameters:
        -----------
        rating : int
            Rating to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        return 1 <= rating <= 5
    
    # ============================================================
    # DUNDER METHODS
    # ============================================================
    
    def __repr__(self) -> str:
        """String representation of the click."""
        return f"<RecommendationClick(id={self.id}, user={self.user_id}, isbn='{self.isbn}', type='{self.recommendation_type}')>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        status = []
        if self.is_clicked:
            status.append("clicked")
        if self.is_saved:
            status.append("saved")
        if self.is_rated:
            status.append(f"rated {self.rating_value}/5")
        status_str = ", ".join(status) if status else "viewed"
        return f"Recommendation {self.isbn} by user {self.user_id}: {status_str}"


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    import json
    from datetime import datetime
    
    print("=" * 60)
    print("RECOMMENDATION CLICK MODEL TEST")
    print("=" * 60)
    
    # Test 1: Create click
    print("\n📌 Test 1: Create Click")
    click = RecommendationClick.create(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        isbn="0446310786",
        session_id="session_12345",
        recommendation_type="hybrid",
        rank=1,
        score=0.85,
        device_type="web",
        browser="Chrome 120",
        ip_address="192.168.1.1",
        referer_url="https://example.com/books",
        metadata={"page": "homepage", "section": "featured"}
    )
    
    print(f"✅ Created: {click}")
    print(f"  User: {click.user_id}")
    print(f"  ISBN: {click.isbn}")
    print(f"  Type: {click.recommendation_type}")
    print(f"  Rank: {click.rank}")
    print(f"  Score: {click.score}")
    print(f"  Metadata: {click.get_metadata()}")
    
    # Test 2: Record interactions
    print("\n📌 Test 2: Record Interactions")
    click.record_rating(5)
    print(f"  After rating: {click}")
    print(f"  Is positive: {click.is_positive_feedback}")
    
    click.mark_saved()
    print(f"  After save: {click}")
    
    click.record_feedback("Great recommendation! Exactly what I was looking for.")
    print(f"  Has feedback: {click.has_feedback}")
    
    # Test 3: Analytics data
    print("\n📌 Test 3: Analytics Data")
    analytics = click.to_analytics_dict()
    print(f"  Analytics: {json.dumps(analytics, indent=2)}")
    
    # Test 4: To dict
    print("\n📌 Test 4: To Dict")
    data = click.to_dict()
    print(f"  Created at: {data['created_at']}")
    print(f"  Week day: {data['week_day']}")
    print(f"  Hour: {data['hour']}")
    print(f"  Has rating: {click.has_rating}")
    print(f"  Is positive: {click.is_positive_feedback}")
    
    # Test 5: Validation
    print("\n📌 Test 5: Validation")
    print(f"  Valid ISBN '0446310786': {RecommendationClick.validate_isbn('0446310786')}")
    print(f"  Valid ISBN 'invalid': {RecommendationClick.validate_isbn('invalid')}")
    print(f"  Valid rating 5: {RecommendationClick.validate_rating(5)}")
    print(f"  Valid rating 0: {RecommendationClick.validate_rating(0)}")
    
    print("\n✅ All tests completed!")