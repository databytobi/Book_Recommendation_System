"""
Recommendation Event Model

SQLAlchemy model for tracking recommendation impressions, displays,
and user interactions with recommendations.

Phase: Database Models
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
import json
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
    Index,
    UniqueConstraint,
    CheckConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

logger = logging.getLogger(__name__)


class RecommendationEvent(Base):
    """
    Model for tracking recommendation impression and display events.
    
    Attributes:
    -----------
    id : int
        Primary key
    user_id : str
        User identifier (UUID)
    isbn : str
        Book ISBN
    session_id : str
        Session identifier
    recommendation_type : str
        Type of recommendation (user, similar, search, trending, hybrid, popularity, content, collaborative)
    rank : int
        Position in recommendation list (1-based)
    score : float
        Recommendation score
    click_through_rate : float
        Estimated click-through rate
    displayed_at : datetime
        When the recommendation was displayed
    viewed_at : datetime
        When the user viewed the recommendation
    click_at : datetime
        When the user clicked on the recommendation
    time_to_click : float
        Time from display to click in seconds
    is_seen : bool
        Whether the recommendation was seen (scrolled into view)
    is_clicked : bool
        Whether the user clicked on the recommendation
    is_saved : bool
        Whether the user saved the recommendation
    is_dismissed : bool
        Whether the user dismissed the recommendation
    context : str
        Where the recommendation was displayed (homepage, category, search, etc.)
    position : int
        Position in the UI layout
    page_number : int
        Page number in paginated results
    recommendations_count : int
        Total number of recommendations in the set
    metadata : str
        JSON string with additional metadata
    request_id : str
        Unique request identifier for tracking
    device_type : str
        Device type (web, mobile, tablet)
    browser : str
        Browser information
    ip_address : str
        IP address of the user
    created_at : datetime
        Record creation timestamp
    updated_at : datetime
        Record last update timestamp
    """
    
    __tablename__ = "recommendation_events"
    
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
        nullable=False,
        index=True,
        doc="Type of recommendation: user, similar, search, trending, hybrid, popularity, content, collaborative"
    )
    
    rank = Column(
        Integer,
        nullable=True,
        doc="Position in recommendation list (1-based)"
    )
    
    score = Column(
        Float,
        nullable=True,
        doc="Recommendation score"
    )
    
    click_through_rate = Column(
        Float,
        nullable=True,
        doc="Estimated click-through rate"
    )
    
    displayed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="When the recommendation was displayed"
    )
    
    viewed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the user viewed the recommendation"
    )
    
    click_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the user clicked on the recommendation"
    )
    
    time_to_click = Column(
        Float,
        nullable=True,
        doc="Time from display to click in seconds"
    )
    
    is_seen = Column(
        Boolean,
        default=False,
        doc="Whether the recommendation was seen"
    )
    
    is_clicked = Column(
        Boolean,
        default=False,
        index=True,
        doc="Whether the user clicked on the recommendation"
    )
    
    is_saved = Column(
        Boolean,
        default=False,
        doc="Whether the user saved the recommendation"
    )
    
    is_dismissed = Column(
        Boolean,
        default=False,
        doc="Whether the user dismissed the recommendation"
    )
    
    context = Column(
        String(50),
        nullable=True,
        index=True,
        doc="Where the recommendation was displayed"
    )
    
    position = Column(
        Integer,
        nullable=True,
        doc="Position in the UI layout"
    )
    
    page_number = Column(
        Integer,
        nullable=True,
        doc="Page number in paginated results"
    )
    
    recommendations_count = Column(
        Integer,
        nullable=True,
        doc="Total number of recommendations in the set"
    )
    
    meta_data = Column(
        "metadata",
        Text,
        nullable=True,
        doc="JSON string with additional metadata"
    )
    
    request_id = Column(
        String(64),
        nullable=True,
        index=True,
        doc="Unique request identifier"
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
        doc="Record creation timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        doc="Record last update timestamp"
    )
    
    # ============================================================
    # CONSTRAINTS & INDEXES
    # ============================================================
    
    __table_args__ = (
        # Composite indexes for common queries
        Index('ix_recommendation_events_user_type', 'user_id', 'recommendation_type'),
        Index('ix_recommendation_events_isbn_type', 'isbn', 'recommendation_type'),
        Index('ix_recommendation_events_user_clicked', 'user_id', 'is_clicked'),
        Index('ix_recommendation_events_displayed_at', 'displayed_at'),
        Index('ix_recommendation_events_clicked_at', 'click_at'),
        #Index('ix_recommendation_events_context', 'context'),
        #Index('ix_recommendation_events_request_id', 'request_id'),
        # Unique constraint to prevent duplicate events
        UniqueConstraint(
            'user_id', 'isbn', 'session_id', 'displayed_at',
            name='uq_recommendation_event'
        )
    )
    
    # ============================================================
    # PROPERTIES
    # ============================================================
    
    @property
    def is_interacted(self) -> bool:
        """Check if the user interacted with the recommendation."""
        return self.is_clicked or self.is_saved or self.is_dismissed
    
    @property
    def engagement_score(self) -> float:
        """
        Calculate engagement score based on interactions.
        
        Returns:
        --------
        float: Engagement score (0-1)
        """
        if not self.is_interacted:
            return 0.0
        
        score = 0.0
        if self.is_clicked:
            score += 0.6
        if self.is_saved:
            score += 0.3
        if self.is_seen and not self.is_clicked:
            score += 0.1
        
        return min(score, 1.0)
    
    @property
    def is_positive_interaction(self) -> bool:
        """Check if the interaction was positive."""
        return self.is_clicked or self.is_saved
    
    @property
    def display_age_seconds(self) -> Optional[float]:
        """Get age of the display in seconds."""
        if not self.displayed_at:
            return None
        now = datetime.now(self.displayed_at.tzinfo)
        return (now - self.displayed_at).total_seconds()
    
    @property
    def display_age_hours(self) -> Optional[float]:
        """Get age of the display in hours."""
        seconds = self.display_age_seconds
        return seconds / 3600 if seconds is not None else None
    
    @property
    def week_day(self) -> Optional[str]:
        """Get the day of the week."""
        if not self.displayed_at:
            return None
        return self.displayed_at.strftime("%A")
    
    @property
    def hour(self) -> Optional[int]:
        """Get the hour of the display."""
        if not self.displayed_at:
            return None
        return self.displayed_at.hour
    
    # ============================================================
    # CLASS METHODS
    # ============================================================
    
    @classmethod
    def create(
        cls,
        isbn: str,
        recommendation_type: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        rank: Optional[int] = None,
        score: Optional[float] = None,
        context: Optional[str] = None,
        position: Optional[int] = None,
        page_number: Optional[int] = None,
        recommendations_count: Optional[int] = None,
        request_id: Optional[str] = None,
        device_type: Optional[str] = None,
        browser: Optional[str] = None,
        ip_address: Optional[str] = None,
        referer_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "RecommendationEvent":
        """
        Create a new recommendation event.
        
        Parameters:
        -----------
        isbn : str
            Book ISBN
        recommendation_type : str
            Type of recommendation
        user_id : Optional[str]
            User identifier
        session_id : Optional[str]
            Session identifier
        rank : Optional[int]
            Position in recommendation list
        score : Optional[float]
            Recommendation score
        context : Optional[str]
            Display context
        position : Optional[int]
            UI position
        page_number : Optional[int]
            Page number
        recommendations_count : Optional[int]
            Total recommendations count
        request_id : Optional[str]
            Request identifier
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
        RecommendationEvent: New event record
        """
        return cls(
            user_id=user_id,
            isbn=isbn,
            session_id=session_id,
            recommendation_type=recommendation_type,
            rank=rank,
            score=score,
            context=context,
            position=position,
            page_number=page_number,
            recommendations_count=recommendations_count,
            request_id=request_id,
            device_type=device_type,
            browser=browser,
            ip_address=ip_address,
            referer_url=referer_url,
            meta_data=json.dumps(metadata) if metadata else None,
            displayed_at=datetime.now()
        )
    
    @classmethod
    def from_recommendations(
        cls,
        recommendations: List[Dict[str, Any]],
        **kwargs
    ) -> List["RecommendationEvent"]:
        """
        Create recommendation events from a list of recommendations.
        
        Parameters:
        -----------
        recommendations : List[Dict[str, Any]]
            List of recommendation dictionaries
        **kwargs : Additional arguments passed to create
        
        Returns:
        --------
        List[RecommendationEvent]: List of events
        """
        events = []
        total_count = len(recommendations)
        
        for idx, rec in enumerate(recommendations, start=1):
            event = cls.create(
                isbn=rec.get('isbn', ''),
                recommendation_type=kwargs.get('recommendation_type', 'hybrid'),
                rank=idx,
                score=rec.get('score', 0.0),
                recommendations_count=total_count,
                user_id=kwargs.get('user_id'),
                session_id=kwargs.get('session_id'),
                context=kwargs.get('context', 'recommendations'),
                request_id=kwargs.get('request_id'),
                device_type=kwargs.get('device_type'),
                browser=kwargs.get('browser'),
                ip_address=kwargs.get('ip_address'),
                referer_url=kwargs.get('referer_url'),
                metadata=kwargs.get('metadata')
            )
            events.append(event)
        
        return events
    
    # ============================================================
    # INSTANCE METHODS
    # ============================================================
    
    def mark_seen(self) -> None:
        """Mark the recommendation as seen."""
        self.is_seen = True
        self.viewed_at = datetime.now()
        self.updated_at = func.now()
        logger.debug(f"Recommendation {self.isbn} marked as seen")
    
    def mark_clicked(self) -> None:
        """Mark the recommendation as clicked."""
        self.is_clicked = True
        self.click_at = datetime.now()
        if self.displayed_at:
            self.time_to_click = (self.click_at - self.displayed_at).total_seconds()
        self.updated_at = func.now()
        logger.info(f"Recommendation {self.isbn} clicked by user {self.user_id}")
    
    def mark_saved(self) -> None:
        """Mark the recommendation as saved."""
        self.is_saved = True
        self.updated_at = func.now()
        logger.info(f"Recommendation {self.isbn} saved by user {self.user_id}")
    
    def mark_dismissed(self) -> None:
        """Mark the recommendation as dismissed."""
        self.is_dismissed = True
        self.updated_at = func.now()
        logger.info(f"Recommendation {self.isbn} dismissed by user {self.user_id}")
    
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
            logger.warning(f"Invalid JSON in metadata for event {self.id}")
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
        self.meta_data = json.dumps(current)
        self.updated_at = func.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Event data
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "isbn": self.isbn,
            "session_id": self.session_id,
            "recommendation_type": self.recommendation_type,
            "rank": self.rank,
            "score": self.score,
            "click_through_rate": self.click_through_rate,
            "displayed_at": self.displayed_at.isoformat() if self.displayed_at else None,
            "viewed_at": self.viewed_at.isoformat() if self.viewed_at else None,
            "click_at": self.click_at.isoformat() if self.click_at else None,
            "time_to_click": self.time_to_click,
            "is_seen": self.is_seen,
            "is_clicked": self.is_clicked,
            "is_saved": self.is_saved,
            "is_dismissed": self.is_dismissed,
            "is_interacted": self.is_interacted,
            "engagement_score": self.engagement_score,
            "context": self.context,
            "position": self.position,
            "page_number": self.page_number,
            "recommendations_count": self.recommendations_count,
            "metadata": self.get_metadata(),
            "request_id": self.request_id,
            "device_type": self.device_type,
            "browser": self.browser,
            "ip_address": self.ip_address,
            "referer_url": self.referer_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "week_day": self.week_day,
            "hour": self.hour,
            "display_age_hours": self.display_age_hours
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
            "context": self.context,
            "seen": self.is_seen,
            "clicked": self.is_clicked,
            "saved": self.is_saved,
            "dismissed": self.is_dismissed,
            "time_to_click": self.time_to_click,
            "device": self.device_type,
            "displayed_at": self.displayed_at.isoformat() if self.displayed_at else None,
            "week_day": self.week_day,
            "hour": self.hour,
            "engagement_score": self.engagement_score
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
    def validate_recommendation_type(rec_type: str) -> bool:
        """
        Validate recommendation type.
        
        Parameters:
        -----------
        rec_type : str
            Recommendation type to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        valid_types = [
            'user', 'similar', 'search', 'trending', 'hybrid',
            'popularity', 'content', 'collaborative'
        ]
        return rec_type in valid_types
    
    # ============================================================
    # DUNDER METHODS
    # ============================================================
    
    def __repr__(self) -> str:
        """String representation of the event."""
        return f"<RecommendationEvent(id={self.id}, user={self.user_id}, isbn='{self.isbn}', type='{self.recommendation_type}', clicked={self.is_clicked})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        status = []
        if self.is_seen:
            status.append("seen")
        if self.is_clicked:
            status.append("clicked")
        if self.is_saved:
            status.append("saved")
        if self.is_dismissed:
            status.append("dismissed")
        status_str = ", ".join(status) if status else "displayed"
        return f"Recommendation {self.isbn} ({self.recommendation_type}): {status_str}"


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    import json
    from datetime import datetime
    
    print("=" * 60)
    print("RECOMMENDATION EVENT MODEL TEST")
    print("=" * 60)
    
    # Test 1: Create event
    print("\n📌 Test 1: Create Event")
    event = RecommendationEvent.create(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        isbn="0446310786",
        session_id="session_12345",
        recommendation_type="hybrid",
        rank=1,
        score=0.85,
        context="homepage",
        position=1,
        page_number=1,
        recommendations_count=10,
        device_type="web",
        browser="Chrome 120",
        ip_address="192.168.1.1",
        referer_url="https://example.com",
        metadata={"section": "featured", "carousel": "popular"}
    )
    
    print(f"✅ Created: {event}")
    print(f"  User: {event.user_id}")
    print(f"  ISBN: {event.isbn}")
    print(f"  Type: {event.recommendation_type}")
    print(f"  Rank: {event.rank}")
    print(f"  Score: {event.score}")
    print(f"  Context: {event.context}")
    
    # Test 2: Track interactions
    print("\n📌 Test 2: Track Interactions")
    event.mark_seen()
    print(f"  After seen: {event}")
    
    event.mark_clicked()
    print(f"  After click: {event}")
    print(f"  Time to click: {event.time_to_click:.2f}s")
    
    event.mark_saved()
    print(f"  After save: {event}")
    
    # Test 3: Engagement score
    print("\n📌 Test 3: Engagement Score")
    print(f"  Engagement Score: {event.engagement_score:.2f}")
    print(f"  Is positive interaction: {event.is_positive_interaction}")
    
    # Test 4: From recommendations
    print("\n📌 Test 4: From Recommendations")
    recs = [
        {"isbn": "0446310786", "score": 0.85},
        {"isbn": "0439139597", "score": 0.82},
        {"isbn": "0142001740", "score": 0.78}
    ]
    events = RecommendationEvent.from_recommendations(
        recommendations=recs,
        user_id="user123",
        recommendation_type="hybrid",
        context="homepage"
    )
    print(f"  Created {len(events)} events")
    for e in events:
        print(f"    {e.isbn}: rank {e.rank}, score {e.score}")
    
    # Test 5: Analytics data
    print("\n📌 Test 5: Analytics Data")
    analytics = event.to_analytics_dict()
    print(f"  Analytics: {json.dumps(analytics, indent=2)}")
    
    # Test 6: Validation
    print("\n📌 Test 6: Validation")
    print(f"  Valid ISBN '0446310786': {RecommendationEvent.validate_isbn('0446310786')}")
    print(f"  Valid type 'hybrid': {RecommendationEvent.validate_recommendation_type('hybrid')}")
    print(f"  Valid type 'invalid': {RecommendationEvent.validate_recommendation_type('invalid')}")
    
    print("\n✅ All tests completed!")