"""
User Followed Author Model

SQLAlchemy model for tracking which authors users follow with
additional metadata for notification preferences and engagement tracking.

Phase: Database Models
"""

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
    Boolean,
    Text,
    Index,
    UniqueConstraint,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

logger = logging.getLogger(__name__)


# ============================================================
# ENUMS
# ============================================================

class FollowStatus(str, Enum):
    """Status of an author follow."""
    ACTIVE = "active"
    MUTED = "muted"
    UNFOLLOWED = "unfollowed"


class NotificationPreference(str, Enum):
    """Notification preferences for followed authors."""
    ALL = "all"                    # All notifications
    NEW_BOOKS = "new_books"        # Only new book releases
    UPDATES = "updates"            # Only updates (events, interviews)
    NONE = "none"                  # No notifications


class FollowSource(str, Enum):
    """Source of the follow."""
    DIRECT = "direct"              # User directly followed
    RECOMMENDATION = "recommendation"  # From recommendation
    DISCOVER = "discover"          # From discover page
    BOOK = "book"                  # From book page
    SEARCH = "search"              # From search results
    SOCIAL = "social"              # From social sharing


class UserFollowedAuthor(Base):
    """
    Model for tracking authors followed by users.
    
    Attributes:
    -----------
    id : int
        Primary key
    user_id : str
        User identifier (UUID)
    author_id : int
        Author identifier (foreign key to authors table)
    author_name : str
        Denormalized author name for quick display
    status : str
        Follow status (active, muted, unfollowed)
    notification_preference : str
        Notification preference (all, new_books, updates, none)
    followed_at : datetime
        When the user followed the author
    last_notified_at : datetime
        When the user was last notified about this author
    muted_at : datetime
        When the user muted this author
    unfollowed_at : datetime
        When the user unfollowed this author
    notes : str
        User notes about this author
    metadata : str
        JSON string with additional metadata
    follow_source : str
        How the user discovered/followed this author
    is_deleted : bool
        Soft delete flag
    created_at : datetime
        Record creation timestamp
    updated_at : datetime
        Record last update timestamp
    """
    
    __tablename__ = "user_followed_authors"
    
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
    
    author_id = Column(
        Integer,
        nullable=False,
        index=True,
        doc="Author identifier (foreign key to authors table)"
    )
    
    author_name = Column(
        String(255),
        nullable=True,
        doc="Denormalized author name for quick display"
    )
    
    status = Column(
        String(10),
        default=FollowStatus.ACTIVE.value,
        index=True,
        doc="Follow status: active, muted, unfollowed"
    )
    
    notification_preference = Column(
        String(10),
        default=NotificationPreference.ALL.value,
        doc="Notification preference"
    )
    
    followed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="When the user followed the author"
    )
    
    last_notified_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the user was last notified about this author"
    )
    
    muted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the user muted this author"
    )
    
    unfollowed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the user unfollowed this author"
    )
    
    notes = Column(
        Text,
        nullable=True,
        doc="User notes about this author"
    )
    
    meta_data = Column(
        "metadata",
        Text,
        nullable=True,
        doc="JSON string with additional metadata"
    )
    
    follow_source = Column(
        String(20),
        nullable=True,
        index=True,
        doc="How the user discovered/followed this author"
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
    
    # Relationship to Author model
    # author = relationship("Author", foreign_keys=[author_id])
    
    # Relationship to User model
    # user = relationship("User", foreign_keys=[user_id])
    
    # ============================================================
    # CONSTRAINTS & INDEXES
    # ============================================================
    
    __table_args__ = (
        # Composite indexes for common queries
        Index('ix_user_followed_authors_user_status', 'user_id', 'status'),
        Index('ix_user_followed_authors_user_author', 'user_id', 'author_id'),
        Index('ix_user_followed_authors_author_status', 'author_id', 'status'),
        Index('ix_user_followed_authors_followed_at', 'followed_at'),
        Index('ix_user_followed_authors_user_followed', 'user_id', 'followed_at'),
        # Unique constraint to prevent duplicate follows
        UniqueConstraint(
            'user_id', 'author_id',
            name='uq_user_followed_author'
        )
    )
    
    # ============================================================
    # PROPERTIES
    # ============================================================
    
    @property
    def is_active(self) -> bool:
        """Check if the follow is active."""
        return self.status == FollowStatus.ACTIVE
    
    @property
    def is_muted(self) -> bool:
        """Check if the follow is muted."""
        return self.status == FollowStatus.MUTED
    
    @property
    def is_unfollowed(self) -> bool:
        """Check if the user has unfollowed."""
        return self.status == FollowStatus.UNFOLLOWED
    
    @property
    def should_notify(self) -> bool:
        """Check if notifications should be sent."""
        return self.is_active and self.notification_preference != NotificationPreference.NONE
    
    @property
    def should_notify_new_books(self) -> bool:
        """Check if new book notifications are enabled."""
        return self.should_notify and self.notification_preference in [
            NotificationPreference.ALL,
            NotificationPreference.NEW_BOOKS
        ]
    
    @property
    def should_notify_updates(self) -> bool:
        """Check if update notifications are enabled."""
        return self.should_notify and self.notification_preference in [
            NotificationPreference.ALL,
            NotificationPreference.UPDATES
        ]
    
    @property
    def follow_duration_days(self) -> Optional[int]:
        """Get the number of days since following."""
        if not self.followed_at:
            return None
        return (datetime.now(self.followed_at.tzinfo) - self.followed_at).days
    
    @property
    def has_notes(self) -> bool:
        """Check if there are notes."""
        return bool(self.notes and self.notes.strip())
    
    @property
    def week_day(self) -> Optional[str]:
        """Get the day of the week."""
        if not self.followed_at:
            return None
        return self.followed_at.strftime("%A")
    
    # ============================================================
    # CLASS METHODS
    # ============================================================
    
    @classmethod
    def create(
        cls,
        user_id: str,
        author_id: int,
        author_name: Optional[str] = None,
        notification_preference: Optional[Union[str, NotificationPreference]] = None,
        follow_source: Optional[Union[str, FollowSource]] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "UserFollowedAuthor":
        """
        Create a new author follow.
        
        Parameters:
        -----------
        user_id : str
            User identifier
        author_id : int
            Author identifier
        author_name : Optional[str]
            Author name for denormalization
        notification_preference : Optional[str]
            Notification preference
        follow_source : Optional[str]
            How the user discovered this author
        notes : Optional[str]
            User notes
        metadata : Optional[Dict[str, Any]]
            Additional metadata
        
        Returns:
        --------
        UserFollowedAuthor: New follow record
        """
        if isinstance(notification_preference, NotificationPreference):
            notification_preference = notification_preference.value
        if isinstance(follow_source, FollowSource):
            follow_source = follow_source.value
        
        return cls(
            user_id=user_id,
            author_id=author_id,
            author_name=author_name,
            status=FollowStatus.ACTIVE.value,
            notification_preference=notification_preference or NotificationPreference.ALL.value,
            follow_source=follow_source,
            notes=notes,
            meta_data=json.dumps(metadata) if metadata else None,
            followed_at=datetime.now()
        )
    
    # ============================================================
    # INSTANCE METHODS
    # ============================================================
    
    def mute(self) -> None:
        """Mute the author follow."""
        self.status = FollowStatus.MUTED
        self.muted_at = datetime.now()
        self.updated_at = func.now()
        logger.info(f"Author {self.author_id} muted by user {self.user_id}")
    
    def unmute(self) -> None:
        """Unmute the author follow."""
        self.status = FollowStatus.ACTIVE
        self.muted_at = None
        self.updated_at = func.now()
        logger.info(f"Author {self.author_id} unmuted by user {self.user_id}")
    
    def unfollow(self) -> None:
        """Unfollow the author."""
        self.status = FollowStatus.UNFOLLOWED
        self.unfollowed_at = datetime.now()
        self.updated_at = func.now()
        logger.info(f"Author {self.author_id} unfollowed by user {self.user_id}")
    
    def refollow(self) -> None:
        """Refollow a previously unfollowed author."""
        self.status = FollowStatus.ACTIVE
        self.unfollowed_at = None
        self.followed_at = datetime.now()
        self.updated_at = func.now()
        logger.info(f"Author {self.author_id} refollowed by user {self.user_id}")
    
    def update_notification_preference(
        self,
        preference: Union[str, NotificationPreference]
    ) -> None:
        """
        Update notification preference.
        
        Parameters:
        -----------
        preference : str
            New notification preference
        """
        if isinstance(preference, NotificationPreference):
            preference = preference.value
        self.notification_preference = preference
        self.updated_at = func.now()
        logger.info(f"Notification preference updated for user {self.user_id}, author {self.author_id}: {preference}")
    
    def update_notes(self, notes: str) -> None:
        """
        Update notes.
        
        Parameters:
        -----------
        notes : str
            New notes
        """
        self.notes = notes
        self.updated_at = func.now()
        logger.info(f"Notes updated for follow {self.id}")
    
    def mark_notified(self) -> None:
        """Mark that the user was notified about this author."""
        self.last_notified_at = datetime.now()
        self.updated_at = func.now()
    
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
            logger.warning(f"Invalid JSON in metadata for follow {self.id}")
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
    
    def soft_delete(self) -> None:
        """Soft delete the follow."""
        self.is_deleted = True
        self.status = FollowStatus.UNFOLLOWED
        self.unfollowed_at = datetime.now()
        self.updated_at = func.now()
        logger.info(f"Follow {self.id} soft deleted")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert follow to dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Follow data
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "author_id": self.author_id,
            "author_name": self.author_name,
            "status": self.status,
            "notification_preference": self.notification_preference,
            "followed_at": self.followed_at.isoformat() if self.followed_at else None,
            "last_notified_at": self.last_notified_at.isoformat() if self.last_notified_at else None,
            "muted_at": self.muted_at.isoformat() if self.muted_at else None,
            "unfollowed_at": self.unfollowed_at.isoformat() if self.unfollowed_at else None,
            "follow_duration_days": self.follow_duration_days,
            "notes": self.notes,
            "metadata": self.get_metadata(),
            "follow_source": self.follow_source,
            "is_active": self.is_active,
            "is_muted": self.is_muted,
            "should_notify": self.should_notify,
            "should_notify_new_books": self.should_notify_new_books,
            "should_notify_updates": self.should_notify_updates,
            "has_notes": self.has_notes,
            "week_day": self.week_day,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
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
            "author_id": self.author_id,
            "status": self.status,
            "notification_preference": self.notification_preference,
            "follow_source": self.follow_source,
            "follow_duration_days": self.follow_duration_days,
            "followed_at": self.followed_at.isoformat() if self.followed_at else None,
            "week_day": self.week_day
        }
    
    # ============================================================
    # VALIDATION HELPERS
    # ============================================================
    
    @staticmethod
    def validate_notification_preference(preference: str) -> bool:
        """
        Validate notification preference.
        
        Parameters:
        -----------
        preference : str
            Notification preference to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        valid_preferences = [p.value for p in NotificationPreference]
        return preference in valid_preferences
    
    @staticmethod
    def validate_follow_source(source: str) -> bool:
        """
        Validate follow source.
        
        Parameters:
        -----------
        source : str
            Follow source to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        valid_sources = [s.value for s in FollowSource]
        return source in valid_sources
    
    @staticmethod
    def validate_status(status: str) -> bool:
        """
        Validate follow status.
        
        Parameters:
        -----------
        status : str
            Status to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        valid_statuses = [s.value for s in FollowStatus]
        return status in valid_statuses
    
    # ============================================================
    # DUNDER METHODS
    # ============================================================
    
    def __repr__(self) -> str:
        """String representation of the follow."""
        return f"<UserFollowedAuthor(id={self.id}, user={self.user_id}, author_id={self.author_id}, status='{self.status}')>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        status = self.status or "unknown"
        return f"User {self.user_id} follows author {self.author_id} ({status})"


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    import json
    from datetime import datetime
    
    print("=" * 60)
    print("USER FOLLOWED AUTHOR MODEL TEST")
    print("=" * 60)
    
    # Test 1: Create follow
    print("\n📌 Test 1: Create Follow")
    follow = UserFollowedAuthor.create(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        author_id=123,
        author_name="J.R.R. Tolkien",
        notification_preference=NotificationPreference.NEW_BOOKS,
        follow_source=FollowSource.RECOMMENDATION,
        notes="My favorite author of all time!",
        metadata={"source_book": "The Hobbit", "rating": 5}
    )
    
    print(f"✅ Created follow: {follow}")
    print(f"  Author: {follow.author_name} (ID: {follow.author_id})")
    print(f"  Notification Preference: {follow.notification_preference}")
    print(f"  Follow Source: {follow.follow_source}")
    print(f"  Notes: {follow.notes}")
    
    # Test 2: Notification checks
    print("\n📌 Test 2: Notification Checks")
    print(f"  Should notify: {follow.should_notify}")
    print(f"  Should notify new books: {follow.should_notify_new_books}")
    print(f"  Should notify updates: {follow.should_notify_updates}")
    
    # Test 3: Mute and unmute
    print("\n📌 Test 3: Mute and Unmute")
    follow.mute()
    print(f"  Is muted: {follow.is_muted}")
    follow.unmute()
    print(f"  Is active: {follow.is_active}")
    
    # Test 4: Unfollow and refollow
    print("\n📌 Test 4: Unfollow and Refollow")
    follow.unfollow()
    print(f"  Is unfollowed: {follow.is_unfollowed}")
    follow.refollow()
    print(f"  Follow duration days: {follow.follow_duration_days}")
    
    # Test 5: Update preference
    print("\n📌 Test 5: Update Notification Preference")
    follow.update_notification_preference(NotificationPreference.UPDATES)
    print(f"  New preference: {follow.notification_preference}")
    
    # Test 6: To dict
    print("\n📌 Test 6: To Dict")
    data = follow.to_dict()
    print(f"  Data: {json.dumps(data, indent=2)}")
    
    # Test 7: Analytics
    print("\n📌 Test 7: Analytics Data")
    analytics = follow.to_analytics_dict()
    print(f"  Analytics: {json.dumps(analytics, indent=2)}")
    
    # Test 8: Validation
    print("\n📌 Test 8: Validation")
    print(f"  Valid preference 'new_books': {UserFollowedAuthor.validate_notification_preference('new_books')}")
    print(f"  Valid preference 'invalid': {UserFollowedAuthor.validate_notification_preference('invalid')}")
    print(f"  Valid source 'direct': {UserFollowedAuthor.validate_follow_source('direct')}")
    print(f"  Valid status 'active': {UserFollowedAuthor.validate_status('active')}")
    
    print("\n✅ All tests completed!")