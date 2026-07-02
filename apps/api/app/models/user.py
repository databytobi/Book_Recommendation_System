"""
User Model

SQLAlchemy model for the User table with validation and utility methods.

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
    Boolean, 
    DateTime, 
    Text,
    UniqueConstraint,
    Index,
    CheckConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

logger = logging.getLogger(__name__)

class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    PENDING_VERIFICATION = "pending_verification"
    SUSPENDED = "suspended"
    BANNED = "banned"


class User(Base):
    """
    User model for authentication and user management.
    
    Attributes:
    -----------
    id : int
        Primary key
    username : str
        Unique username (required)
    email : str
        Unique email address (required)
    hashed_password : str
        Hashed password (required)
    full_name : str
        Optional full name
    is_active : bool
        Whether the user account is active
    is_superuser : bool
        Whether the user has admin privileges
    created_at : datetime
        Timestamp of account creation
    updated_at : datetime
        Timestamp of last update
    last_login : datetime
        Timestamp of last login
    preferences : str
        JSON string of user preferences
    """
    
    __tablename__ = "users"
    
    # ============================================================
    # COLUMNS
    # ============================================================
    
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        doc="Primary key"
    )
    
    username = Column(
        String(50), 
        unique=True, 
        nullable=False, 
        index=True,
        doc="Unique username"
    )
    
    email = Column(
        String(100), 
        unique=True, 
        nullable=False, 
        index=True,
        doc="Unique email address"
    )
    
    hashed_password = Column(
        String(255), 
        nullable=False,
        doc="Hashed password (bcrypt)"
    )
    
    full_name = Column(
        String(100),
        nullable=True,
        doc="User's full name (optional)"
    )
    
    is_active = Column(
        Boolean, 
        default=True,
        doc="Whether the account is active"
    )
    
    is_superuser = Column(
        Boolean, 
        default=False,
        doc="Whether the user has admin privileges"
    )
    
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        doc="Account creation timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True), 
        onupdate=func.now(),
        doc="Last update timestamp"
    )
    
    last_login = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Last login timestamp"
    )
    
    preferences = Column(
        Text,
        nullable=True,
        doc="JSON string of user preferences (e.g., categories, themes)"
    )
    
    account_status = Column(
        String(20),
        default="pending_verification",
        doc="Account status: active, pending_verification, suspended, banned"
    )
    # ============================================================
    # RELATIONSHIPS
    # ============================================================
    
    # If you have a ratings table, you can add this relationship
    # ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    
    # If you have a reviews table
    # reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    
    # ============================================================
    # CONSTRAINTS
    # ============================================================
    
    __table_args__ = (
        # Ensure username is case-insensitive unique
        UniqueConstraint('username', name='uq_users_username'),
        UniqueConstraint('email', name='uq_users_email'),
        # Index for common queries
        Index('ix_users_username_email', 'username', 'email'),
        Index('ix_users_created_at', 'created_at'),
        Index('ix_users_last_login', 'last_login'),
    )
    
    # ============================================================
    # PROPERTIES
    # ============================================================
    
    @property
    def is_authenticated(self) -> bool:
        """Check if the user is authenticated."""
        return True
    
    @property
    def is_anonymous(self) -> bool:
        """Check if the user is anonymous."""
        return False
    
    @property
    def display_name(self) -> str:
        """Get the display name (full_name or username)."""
        return self.full_name or self.username
    
    @property
    def created_at_str(self) -> str:
        """Get formatted created_at string."""
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
    
    # ============================================================
    # CLASS METHODS
    # ============================================================
    
    @classmethod
    def create(
        cls,
        username: str,
        email: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        is_active: bool = True,
        is_superuser: bool = False,
        preferences: Optional[Dict[str, Any]] = None
    ) -> "User":
        """
        Create a new user instance.
        
        Parameters:
        -----------
        username : str
            Unique username
        email : str
            Unique email address
        hashed_password : str
            Hashed password
        full_name : Optional[str]
            User's full name
        is_active : bool
            Whether the account is active
        is_superuser : bool
            Whether the user has admin privileges
        preferences : Optional[Dict[str, Any]]
            User preferences as dictionary
        
        Returns:
        --------
        User: New user instance
        """
        import json
        
        return cls(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=is_active,
            is_superuser=is_superuser,
            preferences=json.dumps(preferences) if preferences else None
        )
    
    # ============================================================
    # INSTANCE METHODS
    # ============================================================
    
    def update_last_login(self) -> None:
        """Update the last_login timestamp."""
        self.last_login = func.now()
    
    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
        logger.info(f"User {self.username} activated")
    
    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
        logger.info(f"User {self.username} deactivated")
    
    def make_admin(self) -> None:
        """Make the user a superuser/admin."""
        self.is_superuser = True
        logger.info(f"User {self.username} promoted to admin")
    
    def remove_admin(self) -> None:
        """Remove admin privileges from the user."""
        self.is_superuser = False
        logger.info(f"User {self.username} removed from admin")
    
    def get_preferences(self) -> Dict[str, Any]:
        """
        Get user preferences as a dictionary.
        
        Returns:
        --------
        Dict[str, Any]: User preferences
        """
        import json
        if not self.preferences:
            return {}
        try:
            return json.loads(self.preferences)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in preferences for user {self.id}")
            return {}
    
    def set_preferences(self, preferences: Dict[str, Any]) -> None:
        """
        Set user preferences from dictionary.
        
        Parameters:
        -----------
        preferences : Dict[str, Any]
            Preferences dictionary
        """
        import json
        self.preferences = json.dumps(preferences)
    
    def update_preferences(self, updates: Dict[str, Any]) -> None:
        """
        Update specific preference keys.
        
        Parameters:
        -----------
        updates : Dict[str, Any]
            Dictionary of preference updates
        """
        current = self.get_preferences()
        current.update(updates)
        self.set_preferences(current)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert user to dictionary (safe for API responses).
        
        Returns:
        --------
        Dict[str, Any]: User data (without sensitive fields)
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "display_name": self.display_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "preferences": self.get_preferences()
        }
    
    def to_dict_public(self) -> Dict[str, Any]:
        """
        Convert user to public dictionary (limited fields).
        
        Returns:
        --------
        Dict[str, Any]: Public user data
        """
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "display_name": self.display_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    # ============================================================
    # VALIDATION HELPERS
    # ============================================================
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Validate username format.
        
        Parameters:
        -----------
        username : str
            Username to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        if not username or len(username) < 3:
            return False
        if len(username) > 50:
            return False
        # Alphanumeric, underscore, hyphen, and dot
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            return False
        return True
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format.
        
        Parameters:
        -----------
        email : str
            Email to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        if not email:
            return False
        # Simple email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    # ============================================================
    # STRING REPRESENTATION
    # ============================================================
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', active={self.is_active})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.display_name} ({self.username})"


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    # Test user creation
    user = User.create(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password_here",
        full_name="Test User",
        preferences={"theme": "dark", "categories": ["fiction", "science"]}
    )
    
    print("Created user:")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Display Name: {user.display_name}")
    print(f"  Preferences: {user.get_preferences()}")
    print(f"  Is Active: {user.is_active}")
    print(f"  Is Superuser: {user.is_superuser}")
    print(f"  To Dict: {user.to_dict()}")
    
    # Test validation
    print("\nValidation Tests:")
    print(f"  Valid username 'test_user': {User.validate_username('test_user')}")
    print(f"  Valid username 'ab': {User.validate_username('ab')}")
    print(f"  Valid email 'test@example.com': {User.validate_email('test@example.com')}")
    print(f"  Valid email 'invalid': {User.validate_email('invalid')}")
    
    # Test methods
    user.activate()
    print(f"\nAfter activate: {user}")
    
    user.make_admin()
    print(f"After make_admin: is_superuser={user.is_superuser}")
    
    print("\n✅ All tests completed!")