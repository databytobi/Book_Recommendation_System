"""
User Favorite Book Model

SQLAlchemy model for tracking user's favorite books with additional
metadata like notes, tags, and collection management.

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
    Text,
    Boolean,
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

class FavoriteStatus(str, Enum):
    """Status of a favorite book."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    REMOVED = "removed"


class FavoritePriority(str, Enum):
    """Priority level of a favorite."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FavoriteCollection(str, Enum):
    """Predefined collections for organizing favorites."""
    READING_LIST = "reading_list"
    WISHLIST = "wishlist"
    FAVORITES = "favorites"
    RECOMMENDED = "recommended"
    OWNED = "owned"
    READ = "read"
    WANT_TO_READ = "want_to_read"
    CURRENTLY_READING = "currently_reading"
    TO_REVIEW = "to_review"


class UserFavoriteBook(Base):
    """
    Model for tracking user's favorite books with collections and notes.
    
    Attributes:
    -----------
    id : int
        Primary key
    user_id : str
        User identifier (UUID)
    isbn : str
        Book ISBN
    collection : str
        Collection name (reading_list, wishlist, favorites, etc.)
    priority : str
        Priority level (high, medium, low)
    status : str
        Status of the favorite (active, archived, removed)
    notes : str
        User notes about the book
    tags : str
        JSON array of tags
    rating_value : int
        User's rating for this book (1-5)
    added_at : datetime
        When the book was added to favorites
    last_accessed_at : datetime
        When the user last accessed this favorite
    times_accessed : int
        Number of times this favorite was accessed
    metadata : str
        JSON string with additional metadata
    is_deleted : bool
        Soft delete flag
    created_at : datetime
        Record creation timestamp
    updated_at : datetime
        Record last update timestamp
    """
    
    __tablename__ = "user_favorite_books"
    
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
        Integer,
        nullable=False,
        index=True,
        doc="User identifier"
    )
    
    isbn = Column(
        String(13),
        nullable=False,
        index=True,
        doc="Book ISBN"
    )
    
    collection = Column(
        String(30),
        default=FavoriteCollection.FAVORITES.value,
        index=True,
        doc="Collection name"
    )
    
    priority = Column(
        String(10),
        default=FavoritePriority.MEDIUM.value,
        index=True,
        doc="Priority level: high, medium, low"
    )
    
    status = Column(
        String(10),
        default=FavoriteStatus.ACTIVE.value,
        index=True,
        doc="Status: active, archived, removed"
    )
    
    notes = Column(
        Text,
        nullable=True,
        doc="User notes about the book"
    )
    
    tags = Column(
        Text,
        nullable=True,
        doc="JSON array of tags"
    )
    
    rating_value = Column(
        Integer,
        nullable=True,
        doc="User's rating for this book (1-5)"
    )
    
    added_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="When the book was added to favorites"
    )
    
    last_accessed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the user last accessed this favorite"
    )
    
    times_accessed = Column(
        Integer,
        default=0,
        doc="Number of times this favorite was accessed"
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
    
    # If you have a Book model:
    # book = relationship("Book", foreign_keys=[isbn])
    
    # If you have a User model:
    # user = relationship("User", foreign_keys=[user_id])
    
    # ============================================================
    # CONSTRAINTS & INDEXES
    # ============================================================
    
    __table_args__ = (
        # Composite indexes for common queries
        Index('ix_user_favorite_books_user_collection', 'user_id', 'collection'),
        Index('ix_user_favorite_books_user_status', 'user_id', 'status'),
        Index('ix_user_favorite_books_user_priority', 'user_id', 'priority'),
        Index('ix_user_favorite_books_added_at', 'added_at'),
        Index('ix_user_favorite_books_user_added', 'user_id', 'added_at'),
        # Unique constraint to prevent duplicate favorites
        UniqueConstraint(
            'user_id', 'isbn',
            name='uq_user_favorite_book'
        ),
        # Check constraint for rating range
        CheckConstraint(
            'rating_value IS NULL OR (rating_value >= 1 AND rating_value <= 5)',
            name='ck_favorite_rating_range'
        )
    )
    
    # ============================================================
    # PROPERTIES
    # ============================================================
    
    @property
    def is_active(self) -> bool:
        """Check if the favorite is active."""
        return self.status == FavoriteStatus.ACTIVE
    
    @property
    def is_archived(self) -> bool:
        """Check if the favorite is archived."""
        return self.status == FavoriteStatus.ARCHIVED
    
    @property
    def is_high_priority(self) -> bool:
        """Check if the favorite has high priority."""
        return self.priority == FavoritePriority.HIGH
    
    @property
    def is_low_priority(self) -> bool:
        """Check if the favorite has low priority."""
        return self.priority == FavoritePriority.LOW
    
    @property
    def has_notes(self) -> bool:
        """Check if there are notes."""
        return bool(self.notes and self.notes.strip())
    
    @property
    def has_rating(self) -> bool:
        """Check if there is a rating."""
        return self.rating_value is not None
    
    @property
    def has_tags(self) -> bool:
        """Check if there are tags."""
        return bool(self.tags and self.tags.strip())
    
    @property
    def added_at_str(self) -> str:
        """Get formatted added_at string."""
        return self.added_at.strftime("%Y-%m-%d %H:%M:%S") if self.added_at else ""
    
    @property
    def days_since_added(self) -> Optional[int]:
        """Get days since added."""
        if not self.added_at:
            return None
        return (datetime.now(self.added_at.tzinfo) - self.added_at).days
    
    @property
    def week_day(self) -> Optional[str]:
        """Get the day of the week."""
        if not self.added_at:
            return None
        return self.added_at.strftime("%A")
    
    # ============================================================
    # CLASS METHODS
    # ============================================================
    
    @classmethod
    def create(
        cls,
        user_id: str,
        isbn: str,
        collection: Optional[Union[str, FavoriteCollection]] = None,
        priority: Optional[Union[str, FavoritePriority]] = None,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None,
        rating_value: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "UserFavoriteBook":
        """
        Create a new favorite book.
        
        Parameters:
        -----------
        user_id : str
            User identifier
        isbn : str
            Book ISBN
        collection : Optional[str]
            Collection name
        priority : Optional[str]
            Priority level
        notes : Optional[str]
            User notes
        tags : Optional[List[str]]
            List of tags
        rating_value : Optional[int]
            Rating value (1-5)
        metadata : Optional[Dict[str, Any]]
            Additional metadata
        
        Returns:
        --------
        UserFavoriteBook: New favorite record
        
        Raises:
        -------
        ValueError: If validation fails
        """
        # Validate rating
        if rating_value is not None and not (1 <= rating_value <= 5):
            raise ValueError("Rating must be between 1 and 5")
        
        # Convert enums to strings
        if isinstance(collection, FavoriteCollection):
            collection = collection.value
        if isinstance(priority, FavoritePriority):
            priority = priority.value
        
        return cls(
            user_id=user_id,
            isbn=isbn,
            collection=collection or FavoriteCollection.FAVORITES.value,
            priority=priority or FavoritePriority.MEDIUM.value,
            status=FavoriteStatus.ACTIVE.value,
            notes=notes,
            tags=json.dumps(tags) if tags else None,
            rating_value=rating_value,
            meta_data=json.dumps(metadata) if metadata else None,
            added_at=datetime.now()
        )
    
    # ============================================================
    # INSTANCE METHODS
    # ============================================================
    
    def add_tags(self, tags: List[str]) -> None:
        """
        Add tags to the favorite.
        
        Parameters:
        -----------
        tags : List[str]
            Tags to add
        """
        current_tags = self.get_tags()
        current_tags.extend(tags)
        # Remove duplicates while preserving order
        self.tags = json.dumps(list(dict.fromkeys(current_tags)))
        self.updated_at = func.now()
        logger.info(f"Tags added to favorite {self.id}: {tags}")
    
    def remove_tags(self, tags: List[str]) -> None:
        """
        Remove tags from the favorite.
        
        Parameters:
        -----------
        tags : List[str]
            Tags to remove
        """
        current_tags = self.get_tags()
        updated_tags = [t for t in current_tags if t not in tags]
        self.tags = json.dumps(updated_tags) if updated_tags else None
        self.updated_at = func.now()
        logger.info(f"Tags removed from favorite {self.id}: {tags}")
    
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
        logger.info(f"Notes updated for favorite {self.id}")
    
    def update_rating(self, rating_value: int) -> None:
        """
        Update rating.
        
        Parameters:
        -----------
        rating_value : int
            Rating value (1-5)
        """
        if not (1 <= rating_value <= 5):
            raise ValueError("Rating must be between 1 and 5")
        self.rating_value = rating_value
        self.updated_at = func.now()
        logger.info(f"Rating updated for favorite {self.id}: {rating_value}/5")
    
    def set_collection(self, collection: Union[str, FavoriteCollection]) -> None:
        """
        Set the collection.
        
        Parameters:
        -----------
        collection : str
            Collection name
        """
        if isinstance(collection, FavoriteCollection):
            collection = collection.value
        self.collection = collection
        self.updated_at = func.now()
        logger.info(f"Collection updated for favorite {self.id}: {collection}")
    
    def set_priority(self, priority: Union[str, FavoritePriority]) -> None:
        """
        Set the priority.
        
        Parameters:
        -----------
        priority : str
            Priority level
        """
        if isinstance(priority, FavoritePriority):
            priority = priority.value
        self.priority = priority
        self.updated_at = func.now()
        logger.info(f"Priority updated for favorite {self.id}: {priority}")
    
    def archive(self) -> None:
        """Archive the favorite."""
        self.status = FavoriteStatus.ARCHIVED
        self.updated_at = func.now()
        logger.info(f"Favorite {self.id} archived")
    
    def restore(self) -> None:
        """Restore an archived favorite."""
        self.status = FavoriteStatus.ACTIVE
        self.updated_at = func.now()
        logger.info(f"Favorite {self.id} restored")
    
    def access(self) -> None:
        """Record an access to this favorite."""
        self.times_accessed += 1
        self.last_accessed_at = datetime.now()
        self.updated_at = func.now()
    
    def get_tags(self) -> List[str]:
        """
        Get tags as list.
        
        Returns:
        --------
        List[str]: List of tags
        """
        if not self.tags:
            return []
        try:
            return json.loads(self.tags)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in tags for favorite {self.id}")
            return []
    
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
            logger.warning(f"Invalid JSON in metadata for favorite {self.id}")
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
        """Soft delete the favorite."""
        self.is_deleted = True
        self.status = FavoriteStatus.REMOVED
        self.updated_at = func.now()
        logger.info(f"Favorite {self.id} soft deleted")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert favorite to dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Favorite data
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "isbn": self.isbn,
            "collection": self.collection,
            "priority": self.priority,
            "status": self.status,
            "notes": self.notes,
            "tags": self.get_tags(),
            "rating_value": self.rating_value,
            "added_at": self.added_at.isoformat() if self.added_at else None,
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "times_accessed": self.times_accessed,
            "metadata": self.get_metadata(),
            "is_active": self.is_active,
            "is_archived": self.is_archived,
            "has_notes": self.has_notes,
            "has_rating": self.has_rating,
            "has_tags": self.has_tags,
            "days_since_added": self.days_since_added,
            "week_day": self.week_day,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
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
    def validate_collection(collection: str) -> bool:
        """
        Validate collection name.
        
        Parameters:
        -----------
        collection : str
            Collection name to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        valid_collections = [c.value for c in FavoriteCollection]
        return collection in valid_collections
    
    @staticmethod
    def validate_priority(priority: str) -> bool:
        """
        Validate priority.
        
        Parameters:
        -----------
        priority : str
            Priority to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        valid_priorities = [p.value for p in FavoritePriority]
        return priority in valid_priorities
    
    # ============================================================
    # DUNDER METHODS
    # ============================================================
    
    def __repr__(self) -> str:
        """String representation of the favorite."""
        return f"<UserFavoriteBook(id={self.id}, user={self.user_id}, isbn='{self.isbn}', collection='{self.collection}')>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Favorite: {self.isbn} by user {self.user_id} ({self.collection})"


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    import json
    from datetime import datetime
    
    print("=" * 60)
    print("USER FAVORITE BOOK MODEL TEST")
    print("=" * 60)
    
    # Test 1: Create favorite
    print("\n📌 Test 1: Create Favorite")
    favorite = UserFavoriteBook.create(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        isbn="0446310786",
        collection=FavoriteCollection.WISHLIST,
        priority=FavoritePriority.HIGH,
        notes="Really want to read this classic!",
        tags=["classic", "to-read", "fiction"],
        rating_value=5,
        metadata={"source": "recommendation", "recommended_by": "friend"}
    )
    
    print(f"✅ Created favorite: {favorite}")
    print(f"  ISBN: {favorite.isbn}")
    print(f"  Collection: {favorite.collection}")
    print(f"  Priority: {favorite.priority}")
    print(f"  Tags: {favorite.get_tags()}")
    print(f"  Notes: {favorite.notes}")
    print(f"  Rating: {favorite.rating_value}/5")
    
    # Test 2: Add tags
    print("\n📌 Test 2: Add Tags")
    favorite.add_tags(["favorite", "must-read"])
    print(f"  Tags after add: {favorite.get_tags()}")
    
    # Test 3: Update notes
    print("\n📌 Test 3: Update Notes")
    favorite.update_notes("Classic American literature, highly recommended by many readers.")
    print(f"  Notes updated: {favorite.notes}")
    
    # Test 4: Access tracking
    print("\n📌 Test 4: Access Tracking")
    favorite.access()
    favorite.access()
    favorite.access()
    print(f"  Times accessed: {favorite.times_accessed}")
    print(f"  Last accessed: {favorite.last_accessed_at}")
    
    # Test 5: Archive and restore
    print("\n📌 Test 5: Archive and Restore")
    favorite.archive()
    print(f"  Is archived: {favorite.is_archived}")
    favorite.restore()
    print(f"  Is active: {favorite.is_active}")
    
    # Test 6: To dict
    print("\n📌 Test 6: To Dict")
    data = favorite.to_dict()
    print(f"  Data: {json.dumps(data, indent=2)}")
    
    # Test 7: Validation
    print("\n📌 Test 7: Validation")
    print(f"  Valid ISBN '0446310786': {UserFavoriteBook.validate_isbn('0446310786')}")
    print(f"  Valid collection 'wishlist': {UserFavoriteBook.validate_collection('wishlist')}")
    print(f"  Valid priority 'high': {UserFavoriteBook.validate_priority('high')}")
    
    print("\n✅ All tests completed!")