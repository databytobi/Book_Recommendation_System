"""
User Profile Model

SQLAlchemy model for tracking user reading habits, preferences,
and behavioral characteristics for personalization.

Phase: Database Models
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
import json
import logging
from enum import Enum
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    Float,
    Boolean,
    Text,
    JSON,
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

class ReadingPersonality(str, Enum):
    """Reading personality types."""
    COMPLETIONIST = "completionist"        # Reads every book in a series
    DIVERSE = "diverse"                    # Reads across many genres
    SPECIALIST = "specialist"              # Reads deeply in specific genres
    BROWSER = "browser"                    # Reads randomly, follows recommendations
    TRENDY = "trendy"                      # Reads what's popular
    EXPLORER = "explorer"                  # Likes discovering new authors
    CLASSICIST = "classicist"              # Prefers classics and established works


class ReadingSpeed(str, Enum):
    """Reading speed categories."""
    FAST = "fast"                          # > 50 books/year
    AVERAGE = "average"                    # 25-50 books/year
    SLOW = "slow"                          # < 25 books/year
    VARIABLE = "variable"                  # Varies significantly


class DiscoveryPreference(str, Enum):
    """How users prefer to discover books."""
    RECOMMENDATIONS = "recommendations"    # AI recommendations
    FRIENDS = "friends"                    # Social recommendations
    SEARCH = "search"                      # Active search
    CURATED = "curated"                    # Curated lists/collections
    RANDOM = "random"                      # Random discovery
    TRENDING = "trending"                  # Popular/trending books


class GenrePreference(str, Enum):
    """Genre preference levels."""
    LOVES = "loves"
    LIKES = "likes"
    NEUTRAL = "neutral"
    DISLIKES = "dislikes"
    AVOIDS = "avoids"


class UserProfile(Base):
    """
    Model for tracking user reading habits and behavioral characteristics.
    
    Attributes:
    -----------
    user_id : str
        User identifier (UUID)
    display_name : str
        User's display name for the profile
    bio : str
        User's bio/description
    avatar_url : str
        URL to user's avatar image
    reading_personality : str
        Reading personality type
    reading_speed : str
        Reading speed category
    books_per_year : int
        Estimated books read per year
    total_books_read : int
        Total books read
    favorite_genres : str
        JSON array of favorite genres
    favorite_authors : str
        JSON array of favorite authors
    reading_goals : str
        JSON object with reading goals
    discovery_preference : str
        How the user prefers to discover books
    discovery_score : float
        Score indicating user's openness to discovery
    onboarding_completed : bool
        Whether user has completed onboarding
    last_active_at : datetime
        Last time user was active
    reading_streak_days : int
        Current reading streak in days
    longest_streak_days : int
        Longest reading streak achieved
    weekly_reading_hours : float
        Average weekly reading hours
    preferred_book_length : str
        Preferred book length (short, medium, long)
    reading_style : str
        Preferred reading style (quick, balanced, deep, explorer)
    preferred_language : str
        Preferred reading language
    accessibility_needs : str
        JSON array of accessibility needs
    metadata : str
        JSON string with additional metadata
    created_at : datetime
        Record creation timestamp
    updated_at : datetime
        Record last update timestamp
    """
    
    __tablename__ = "user_profiles"
    
    # ============================================================
    # COLUMNS
    # ============================================================
    
    user_id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="User identifier"
    )
    
    display_name = Column(
        String(100),
        nullable=True,
        doc="User's display name for the profile"
    )
    
    bio = Column(
        Text,
        nullable=True,
        doc="User's bio/description"
    )
    
    avatar_url = Column(
        String(512),
        nullable=True,
        doc="URL to user's avatar image"
    )
    
    reading_personality = Column(
        String(20),
        nullable=True,
        index=True,
        doc="Reading personality type"
    )
    
    reading_speed = Column(
        String(10),
        nullable=True,
        doc="Reading speed category"
    )
    
    books_per_year = Column(
        Integer,
        default=0,
        doc="Estimated books read per year"
    )
    
    total_books_read = Column(
        Integer,
        default=0,
        doc="Total books read"
    )
    
    favorite_genres = Column(
        Text,
        nullable=True,
        doc="JSON array of favorite genres"
    )
    
    favorite_authors = Column(
        Text,
        nullable=True,
        doc="JSON array of favorite authors"
    )
    
    reading_goals = Column(
        Text,
        nullable=True,
        doc="JSON object with reading goals"
    )
    
    discovery_preference = Column(
        String(20),
        nullable=True,
        doc="How the user prefers to discover books"
    )
    
    discovery_score = Column(
        Float,
        default=0.5,
        doc="Score indicating user's openness to discovery (0-1)"
    )
    
    onboarding_completed = Column(
        Boolean,
        default=False,
        doc="Whether user has completed onboarding"
    )
    
    last_active_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Last time user was active"
    )
    
    reading_streak_days = Column(
        Integer,
        default=0,
        doc="Current reading streak in days"
    )
    
    longest_streak_days = Column(
        Integer,
        default=0,
        doc="Longest reading streak achieved"
    )
    
    weekly_reading_hours = Column(
        Float,
        default=0.0,
        doc="Average weekly reading hours"
    )
    
    preferred_book_length = Column(
        String(10),
        nullable=True,
        doc="Preferred book length: short, medium, long"
    )
    
    reading_style = Column(
        String(20),
        nullable=False,
        default="balanced",
        index=True,
        doc="Preferred reading style"
    )
    
    preferred_language = Column(
        String(10),
        default="en",
        doc="Preferred reading language"
    )
    
    accessibility_needs = Column(
        Text,
        nullable=True,
        doc="JSON array of accessibility needs"
    )
    
    meta_data = Column(
        "metadata",
        Text,
        nullable=True,
        doc="JSON string with additional metadata"
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
    
    # Relationship to User model
    # user = relationship("User", foreign_keys=[user_id])
    
    # ============================================================
    # CONSTRAINTS & INDEXES
    # ============================================================
    
    __table_args__ = (
        # Indexes for common queries.
        # NOTE: `reading_personality` is declared with index=True on the
        # column itself, which already creates an index named
        # ix_user_profiles_reading_personality. Re-declaring it here produced
        # a duplicate CREATE INDEX statement, so schema creation failed with
        # "index ix_user_profiles_reading_personality already exists".
        Index('ix_user_profiles_books_per_year', 'books_per_year'),
        Index('ix_user_profiles_last_active', 'last_active_at'),
        Index('ix_user_profiles_onboarding', 'onboarding_completed'),
        # Check constraints
        CheckConstraint(
            'books_per_year >= 0',
            name='ck_books_per_year_non_negative'
        ),
        CheckConstraint(
            'total_books_read >= 0',
            name='ck_total_books_read_non_negative'
        ),
        CheckConstraint(
            'discovery_score >= 0 AND discovery_score <= 1',
            name='ck_discovery_score_range'
        ),
        CheckConstraint(
            'reading_streak_days >= 0',
            name='ck_reading_streak_non_negative'
        ),
        CheckConstraint(
            'weekly_reading_hours >= 0',
            name='ck_weekly_reading_hours_non_negative'
        )
    )
    
    # ============================================================
    # PROPERTIES
    # ============================================================
    
    @property
    def is_onboarded(self) -> bool:
        """Check if onboarding is completed."""
        return self.onboarding_completed
    
    @property
    def is_active_reader(self) -> bool:
        """Check if user is an active reader (books_per_year > 0)."""
        return self.books_per_year > 0
    
    @property
    def is_avid_reader(self) -> bool:
        """Check if user is an avid reader (books_per_year > 50)."""
        return self.books_per_year > 50
    
    @property
    def reading_personality_display(self) -> str:
        """Get display name for reading personality."""
        personality_map = {
            ReadingPersonality.COMPLETIONIST.value: "Completionist",
            ReadingPersonality.DIVERSE.value: "Diverse Reader",
            ReadingPersonality.SPECIALIST.value: "Specialist",
            ReadingPersonality.BROWSER.value: "Browser",
            ReadingPersonality.TRENDY.value: "Trendy Reader",
            ReadingPersonality.EXPLORER.value: "Explorer",
            ReadingPersonality.CLASSICIST.value: "Classicist"
        }
        return personality_map.get(self.reading_personality, "Unknown")
    
    @property
    def reading_speed_display(self) -> str:
        """Get display name for reading speed."""
        speed_map = {
            ReadingSpeed.FAST.value: "Fast Reader",
            ReadingSpeed.AVERAGE.value: "Average Reader",
            ReadingSpeed.SLOW.value: "Slow Reader",
            ReadingSpeed.VARIABLE.value: "Variable Reader"
        }
        return speed_map.get(self.reading_speed, "Unknown")
    
    @property
    def discovery_preference_display(self) -> str:
        """Get display name for discovery preference."""
        discovery_map = {
            DiscoveryPreference.RECOMMENDATIONS.value: "AI Recommendations",
            DiscoveryPreference.FRIENDS.value: "Friends' Recommendations",
            DiscoveryPreference.SEARCH.value: "Active Search",
            DiscoveryPreference.CURATED.value: "Curated Lists",
            DiscoveryPreference.RANDOM.value: "Random Discovery",
            DiscoveryPreference.TRENDING.value: "Trending Books"
        }
        return discovery_map.get(self.discovery_preference, "Unknown")
    
    # ============================================================
    # CLASS METHODS
    # ============================================================
    
    @classmethod
    def create(
        cls,
        user_id: str,
        display_name: Optional[str] = None,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None,
        reading_personality: Optional[Union[str, ReadingPersonality]] = None,
        reading_speed: Optional[Union[str, ReadingSpeed]] = None,
        books_per_year: int = 0,
        favorite_genres: Optional[List[str]] = None,
        favorite_authors: Optional[List[str]] = None,
        discovery_preference: Optional[Union[str, DiscoveryPreference]] = None,
        discovery_score: float = 0.5,
        reading_style: str = "balanced",
        preferred_language: str = "en",
        accessibility_needs: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "UserProfile":
        """
        Create a new user profile.
        
        Parameters:
        -----------
        user_id : str
            User identifier
        display_name : Optional[str]
            Display name
        bio : Optional[str]
            Bio description
        avatar_url : Optional[str]
            Avatar URL
        reading_personality : Optional[str]
            Reading personality type
        reading_speed : Optional[str]
            Reading speed category
        books_per_year : int
            Books read per year
        favorite_genres : Optional[List[str]]
            List of favorite genres
        favorite_authors : Optional[List[str]]
            List of favorite authors
        discovery_preference : Optional[str]
            Discovery preference
        discovery_score : float
            Discovery openness score
        reading_style : str
            Preferred reading style
        preferred_language : str
            Preferred language
        accessibility_needs : Optional[List[str]]
            Accessibility needs
        metadata : Optional[Dict[str, Any]]
            Additional metadata
        
        Returns:
        --------
        UserProfile: New profile record
        """
        # Convert enums to strings
        if isinstance(reading_personality, ReadingPersonality):
            reading_personality = reading_personality.value
        if isinstance(reading_speed, ReadingSpeed):
            reading_speed = reading_speed.value
        if isinstance(discovery_preference, DiscoveryPreference):
            discovery_preference = discovery_preference.value
        
        return cls(
            user_id=user_id,
            display_name=display_name,
            bio=bio,
            avatar_url=avatar_url,
            reading_personality=reading_personality,
            reading_speed=reading_speed,
            books_per_year=books_per_year,
            favorite_genres=json.dumps(favorite_genres) if favorite_genres else None,
            favorite_authors=json.dumps(favorite_authors) if favorite_authors else None,
            discovery_preference=discovery_preference,
            discovery_score=discovery_score,
            reading_style=reading_style,
            preferred_language=preferred_language,
            accessibility_needs=json.dumps(accessibility_needs) if accessibility_needs else None,
            meta_data=json.dumps(metadata) if metadata else None,
            last_active_at=datetime.now()
        )
    
    # ============================================================
    # INSTANCE METHODS
    # ============================================================
    
    def update_activity(self) -> None:
        """Update the last active timestamp."""
        self.last_active_at = datetime.now()
        self.updated_at = func.now()
    
    def increment_books_read(self, count: int = 1) -> None:
        """
        Increment the total books read count.
        
        Parameters:
        -----------
        count : int
            Number of books to increment by
        """
        self.total_books_read += count
        self.updated_at = func.now()
        logger.info(f"User {self.user_id} read {count} book(s). Total: {self.total_books_read}")
    
    def update_streak(self, is_active_day: bool = True) -> None:
        """
        Update reading streak.
        
        Parameters:
        -----------
        is_active_day : bool
            Whether the user read today
        """
        if is_active_day:
            self.reading_streak_days += 1
            if self.reading_streak_days > self.longest_streak_days:
                self.longest_streak_days = self.reading_streak_days
            logger.info(f"User {self.user_id} streak: {self.reading_streak_days} days")
        else:
            self.reading_streak_days = 0
        self.updated_at = func.now()
    
    def set_favorite_genres(self, genres: List[str]) -> None:
        """
        Set favorite genres.
        
        Parameters:
        -----------
        genres : List[str]
            List of favorite genres
        """
        self.favorite_genres = json.dumps(genres) if genres else None
        self.updated_at = func.now()
        logger.info(f"Favorite genres updated for user {self.user_id}")
    
    def add_favorite_genre(self, genre: str) -> None:
        """
        Add a genre to favorites.
        
        Parameters:
        -----------
        genre : str
            Genre to add
        """
        current = self.get_favorite_genres()
        if genre not in current:
            current.append(genre)
            self.set_favorite_genres(current)
    
    def remove_favorite_genre(self, genre: str) -> None:
        """
        Remove a genre from favorites.
        
        Parameters:
        -----------
        genre : str
            Genre to remove
        """
        current = self.get_favorite_genres()
        if genre in current:
            current.remove(genre)
            self.set_favorite_genres(current)
    
    def set_favorite_authors(self, authors: List[str]) -> None:
        """
        Set favorite authors.
        
        Parameters:
        -----------
        authors : List[str]
            List of favorite authors
        """
        self.favorite_authors = json.dumps(authors) if authors else None
        self.updated_at = func.now()
        logger.info(f"Favorite authors updated for user {self.user_id}")
    
    def get_favorite_genres(self) -> List[str]:
        """
        Get favorite genres as list.
        
        Returns:
        --------
        List[str]: List of favorite genres
        """
        if not self.favorite_genres:
            return []
        try:
            return json.loads(self.favorite_genres)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in favorite_genres for user {self.user_id}")
            return []
    
    def get_favorite_authors(self) -> List[str]:
        """
        Get favorite authors as list.
        
        Returns:
        --------
        List[str]: List of favorite authors
        """
        if not self.favorite_authors:
            return []
        try:
            return json.loads(self.favorite_authors)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in favorite_authors for user {self.user_id}")
            return []
    
    def get_accessibility_needs(self) -> List[str]:
        """
        Get accessibility needs as list.
        
        Returns:
        --------
        List[str]: List of accessibility needs
        """
        if not self.accessibility_needs:
            return []
        try:
            return json.loads(self.accessibility_needs)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in accessibility_needs for user {self.user_id}")
            return []
    
    def get_reading_goals(self) -> Dict[str, Any]:
        """
        Get reading goals as dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Reading goals
        """
        if not self.reading_goals:
            return {}
        try:
            return json.loads(self.reading_goals)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in reading_goals for user {self.user_id}")
            return {}
    
    def set_reading_goals(self, goals: Dict[str, Any]) -> None:
        """
        Set reading goals.
        
        Parameters:
        -----------
        goals : Dict[str, Any]
            Reading goals dictionary
        """
        self.reading_goals = json.dumps(goals)
        self.updated_at = func.now()
        logger.info(f"Reading goals updated for user {self.user_id}")
    
    def complete_onboarding(self) -> None:
        """Mark onboarding as completed."""
        self.onboarding_completed = True
        self.updated_at = func.now()
        logger.info(f"Onboarding completed for user {self.user_id}")
    
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
            logger.warning(f"Invalid JSON in metadata for user {self.user_id}")
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
        Convert profile to dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Profile data
        """
        return {
            "user_id": self.user_id,
            "display_name": self.display_name,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "reading_personality": self.reading_personality,
            "reading_personality_display": self.reading_personality_display,
            "reading_speed": self.reading_speed,
            "reading_speed_display": self.reading_speed_display,
            "books_per_year": self.books_per_year,
            "total_books_read": self.total_books_read,
            "favorite_genres": self.get_favorite_genres(),
            "favorite_authors": self.get_favorite_authors(),
            "reading_goals": self.get_reading_goals(),
            "discovery_preference": self.discovery_preference,
            "discovery_preference_display": self.discovery_preference_display,
            "discovery_score": self.discovery_score,
            "onboarding_completed": self.onboarding_completed,
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None,
            "reading_streak_days": self.reading_streak_days,
            "longest_streak_days": self.longest_streak_days,
            "weekly_reading_hours": self.weekly_reading_hours,
            "preferred_book_length": self.preferred_book_length,
            "reading_style": self.reading_style,
            "preferred_language": self.preferred_language,
            "accessibility_needs": self.get_accessibility_needs(),
            "metadata": self.get_metadata(),
            "is_active_reader": self.is_active_reader,
            "is_avid_reader": self.is_avid_reader,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_public_dict(self) -> Dict[str, Any]:
        """
        Convert to public-facing dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Public profile data
        """
        return {
            "user_id": self.user_id,
            "display_name": self.display_name,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "reading_personality_display": self.reading_personality_display,
            "reading_style": self.reading_style,
            "favorite_genres": self.get_favorite_genres(),
            "favorite_authors": self.get_favorite_authors(),
            "books_per_year": self.books_per_year,
            "total_books_read": self.total_books_read,
            "reading_streak_days": self.reading_streak_days
        }
    
    # ============================================================
    # DUNDER METHODS
    # ============================================================
    
    def __repr__(self) -> str:
        """String representation of the profile."""
        return f"<UserProfile(user_id='{self.user_id}', personality='{self.reading_personality}', books_per_year={self.books_per_year})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"User {self.user_id}: {self.reading_personality_display} ({self.books_per_year} books/year)"


# ============================================================
# PROFILE ANALYZER UTILITY
# ============================================================

class ProfileAnalyzer:
    """
    Utility class for analyzing user reading behavior and generating recommendations.
    """
    
    def __init__(self, profile: UserProfile):
        """
        Initialize the profile analyzer.
        
        Parameters:
        -----------
        profile : UserProfile
            User profile to analyze
        """
        self.profile = profile
    
    def get_recommendation_weights(self) -> Dict[str, float]:
        """
        Generate recommendation weights based on profile.
        
        Returns:
        --------
        Dict[str, float]: Weighted recommendation preferences
        """
        weights = {
            "collaborative": 0.30,
            "content": 0.30,
            "popularity": 0.20,
            "novelty": 0.10,
            "diversity": 0.10
        }
        
        # Adjust based on reading personality
        personality_adjustments = {
            ReadingPersonality.COMPLETIONIST.value: {"collaborative": 0.40, "novelty": 0.05},
            ReadingPersonality.DIVERSE.value: {"diversity": 0.30, "content": 0.20},
            ReadingPersonality.SPECIALIST.value: {"content": 0.50, "collaborative": 0.10},
            ReadingPersonality.BROWSER.value: {"popularity": 0.30, "novelty": 0.20},
            ReadingPersonality.TRENDY.value: {"popularity": 0.40, "collaborative": 0.10},
            ReadingPersonality.EXPLORER.value: {"novelty": 0.40, "diversity": 0.20},
            ReadingPersonality.CLASSICIST.value: {"content": 0.40, "popularity": 0.10}
        }
        
        if self.profile.reading_personality in personality_adjustments:
            adjustments = personality_adjustments[self.profile.reading_personality]
            for key, value in adjustments.items():
                if key in weights:
                    weights[key] = value
        
        # Adjust discovery score
        if self.profile.discovery_score < 0.3:
            weights["novelty"] = weights.get("novelty", 0.1) * 0.5
        elif self.profile.discovery_score > 0.7:
            weights["novelty"] = weights.get("novelty", 0.1) * 1.5
        
        # Normalize
        total = sum(weights.values())
        for key in weights:
            weights[key] = weights[key] / total
        
        return weights
    
    def get_genre_recommendations(self, genres: List[str]) -> List[str]:
        """
        Recommend genres based on profile.
        
        Parameters:
        -----------
        genres : List[str]
            Available genres
        
        Returns:
        --------
        List[str]: Recommended genres
        """
        favorite_genres = self.profile.get_favorite_genres()
        
        if not favorite_genres:
            # If no favorites, suggest from available
            return genres[:5]
        
        # Prioritize favorite genres
        recommended = [g for g in favorite_genres if g in genres]
        
        # Add some variety
        remaining = [g for g in genres if g not in recommended]
        recommended.extend(remaining[:10 - len(recommended)])
        
        return recommended[:10]
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the user's reading profile.
        
        Returns:
        --------
        Dict[str, Any]: Profile summary
        """
        return {
            "reading_personality": self.profile.reading_personality_display,
            "reading_speed": self.profile.reading_speed_display,
            "books_per_year": self.profile.books_per_year,
            "total_books_read": self.profile.total_books_read,
            "favorite_genres": self.profile.get_favorite_genres(),
            "favorite_authors": self.profile.get_favorite_authors(),
            "discovery_preference": self.profile.discovery_preference_display,
            "reading_streak": self.profile.reading_streak_days,
            "longest_streak": self.profile.longest_streak_days,
            "is_active": self.profile.is_active_reader,
            "is_avid": self.profile.is_avid_reader,
            "recommendation_weights": self.get_recommendation_weights()
        }


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    import json
    from datetime import datetime
    
    print("=" * 60)
    print("USER PROFILE MODEL TEST")
    print("=" * 60)
    
    # Test 1: Create profile
    print("\n📌 Test 1: Create Profile")
    profile = UserProfile.create(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        display_name="Book Lover",
        bio="I love reading fiction and exploring new authors.",
        reading_personality=ReadingPersonality.DIVERSE,
        reading_speed=ReadingSpeed.AVERAGE,
        books_per_year=35,
        favorite_genres=["Fiction", "Science Fiction", "Fantasy", "History"],
        favorite_authors=["J.R.R. Tolkien", "Isaac Asimov", "Harper Lee"],
        discovery_preference=DiscoveryPreference.RECOMMENDATIONS,
        discovery_score=0.7,
        reading_style="balanced",
        preferred_language="en",
        metadata={"source": "onboarding", "version": "1.0"}
    )
    
    print(f"✅ Created profile: {profile}")
    print(f"  Display Name: {profile.display_name}")
    print(f"  Personality: {profile.reading_personality_display}")
    print(f"  Speed: {profile.reading_speed_display}")
    print(f"  Style: {profile.reading_style}")
    print(f"  Books/Year: {profile.books_per_year}")
    print(f"  Favorite Genres: {profile.get_favorite_genres()}")
    
    # Test 2: Update activity
    print("\n📌 Test 2: Update Activity")
    profile.update_activity()
    print(f"  Last active: {profile.last_active_at}")
    
    # Test 3: Increment books read
    print("\n📌 Test 3: Increment Books Read")
    profile.increment_books_read(5)
    print(f"  Total books read: {profile.total_books_read}")
    
    # Test 4: Update streak
    print("\n📌 Test 4: Update Streak")
    profile.update_streak(True)
    print(f"  Current streak: {profile.reading_streak_days} days")
    print(f"  Longest streak: {profile.longest_streak_days} days")
    
    # Test 5: Complete onboarding
    print("\n📌 Test 5: Complete Onboarding")
    profile.complete_onboarding()
    print(f"  Onboarding completed: {profile.onboarding_completed}")
    
    # Test 6: Analyze profile
    print("\n📌 Test 6: Profile Analysis")
    analyzer = ProfileAnalyzer(profile)
    weights = analyzer.get_recommendation_weights()
    print(f"  Recommendation Weights: {json.dumps(weights, indent=2)}")
    
    # Test 7: To dict
    print("\n📌 Test 7: To Dict")
    data = profile.to_dict()
    print(f"  Data: {json.dumps(data, indent=2)}")
    
    # Test 8: Public dict
    print("\n📌 Test 8: Public Dict")
    public = profile.to_public_dict()
    print(f"  Public: {json.dumps(public, indent=2)}")
    
    print("\n✅ All tests completed!")