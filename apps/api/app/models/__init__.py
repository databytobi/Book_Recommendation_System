"""
Models Package

Database models for the Book Recommendation System.
"""

from app.models.user import User
from app.models.author import Author
from app.models.book import Book
from app.models.recommendation_click import RecommendationClick
from app.models.recommendation_event import RecommendationEvent
from app.models.search_history import SearchHistory
from app.models.user_book_interaction import (
    UserBookInteraction,
    InteractionType,
    ReadingStatus,
    InteractionSource
)
from app.models.user_favorite_book import (
    UserFavoriteBook,
    FavoriteStatus,
    FavoritePriority,
    FavoriteCollection
)
from app.models.user_followed_author import (
    UserFollowedAuthor,
    FollowStatus,
    NotificationPreference,
    FollowSource
)
from app.models.user_preference import (
    UserPreference,
    PreferenceCategory,
    PreferenceDataType,
    PreferenceManager
)
from app.models.user_profile import (
    UserProfile,
    ReadingPersonality,
    ReadingSpeed,
    DiscoveryPreference,
    ProfileAnalyzer
)

__all__ = [
    "User",
    "Author",
    "Book",
    "RecommendationClick",
    "RecommendationEvent",
    "SearchHistory",
    "UserBookInteraction",
    "InteractionType",
    "ReadingStatus",
    "InteractionSource",
    "UserFavoriteBook",
    "FavoriteStatus",
    "FavoritePriority",
    "FavoriteCollection",
    "UserFollowedAuthor",
    "FollowStatus",
    "NotificationPreference",
    "FollowSource",
    "UserPreference",
    "PreferenceCategory",
    "PreferenceDataType",
    "PreferenceManager",
    "UserProfile",
    "ReadingPersonality",
    "ReadingSpeed",
    "DiscoveryPreference",
    "ProfileAnalyzer",
]