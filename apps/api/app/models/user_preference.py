"""
User Preference Model

SQLAlchemy model for storing user preferences including
UI settings, recommendation preferences, and personalization options.

Phase: Database Models
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
import json
import logging
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    Float,
    Index,
    UniqueConstraint,
    JSON,
    CheckConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

logger = logging.getLogger(__name__)


# ============================================================
# ENUMS
# ============================================================

class PreferenceCategory(str, Enum):
    """Categories of user preferences."""
    UI = "ui"                       # UI/display preferences
    RECOMMENDATION = "recommendation"  # Recommendation preferences
    NOTIFICATION = "notification"    # Notification preferences
    PRIVACY = "privacy"              # Privacy settings
    LANGUAGE = "language"            # Language preferences
    ACCESSIBILITY = "accessibility"  # Accessibility settings
    PERSONALIZATION = "personalization"  # Personalization settings
    COMMUNICATION = "communication"  # Communication preferences


class PreferenceDataType(str, Enum):
    """Data types for preference values."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    ARRAY = "array"


class UserPreference(Base):
    """
    Model for storing user preferences.
    
    Attributes:
    -----------
    id : int
        Primary key
    user_id : str
        User identifier (UUID)
    key : str
        Preference key
    value : str
        Preference value (stored as string, parsed based on data_type)
    data_type : str
        Data type of the value (string, integer, float, boolean, json, array)
    category : str
        Preference category
    description : str
        Human-readable description of the preference
    is_public : bool
        Whether this preference is publicly visible
    is_encrypted : bool
        Whether this preference should be encrypted
    default_value : str
        Default value for this preference
    version : int
        Version of the preference schema
    metadata : str
        JSON string with additional metadata
    created_at : datetime
        Record creation timestamp
    updated_at : datetime
        Record last update timestamp
    """
    
    __tablename__ = "user_preferences"
    
    # ============================================================
    # COLUMNS
    # ============================================================
    
    id = Column(
        Integer,
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
    
    key = Column(
        String(100),
        nullable=False,
        index=True,
        doc="Preference key"
    )
    
    value = Column(
        Text,
        nullable=False,
        doc="Preference value (stored as string)"
    )
    
    data_type = Column(
        String(20),
        default=PreferenceDataType.STRING.value,
        doc="Data type of the value"
    )
    
    category = Column(
        String(30),
        nullable=True,
        index=True,
        doc="Preference category"
    )
    
    description = Column(
        Text,
        nullable=True,
        doc="Human-readable description"
    )
    
    is_public = Column(
        Boolean,
        default=False,
        doc="Whether this preference is publicly visible"
    )
    
    is_encrypted = Column(
        Boolean,
        default=False,
        doc="Whether this preference should be encrypted"
    )
    
    default_value = Column(
        Text,
        nullable=True,
        doc="Default value for this preference"
    )
    
    version = Column(
        Integer,
        default=1,
        doc="Version of the preference schema"
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
    # CONSTRAINTS & INDEXES
    # ============================================================
    
    __table_args__ = (
        # Composite indexes for common queries
        Index('ix_user_preferences_user_key', 'user_id', 'key'),
        Index('ix_user_preferences_user_category', 'user_id', 'category'),
        Index('ix_user_preferences_user_public', 'user_id', 'is_public'),
        Index('ix_user_preferences_key_category', 'key', 'category'),
        # Unique constraint for user preference key
        UniqueConstraint(
            'user_id', 'key',
            name='uq_user_preference'
        )
    )
    
    # ============================================================
    # PROPERTIES
    # ============================================================
    
    @property
    def parsed_value(self) -> Any:
        """
        Get the parsed value based on data_type.
        
        Returns:
        --------
        Any: Parsed value
        """
        if self.value is None:
            return None
        
        try:
            if self.data_type == PreferenceDataType.STRING.value:
                return self.value
            elif self.data_type == PreferenceDataType.INTEGER.value:
                return int(self.value)
            elif self.data_type == PreferenceDataType.FLOAT.value:
                return float(self.value)
            elif self.data_type == PreferenceDataType.BOOLEAN.value:
                return self.value.lower() == 'true'
            elif self.data_type == PreferenceDataType.JSON.value:
                return json.loads(self.value)
            elif self.data_type == PreferenceDataType.ARRAY.value:
                return json.loads(self.value) if self.value else []
            else:
                return self.value
        except (ValueError, json.JSONDecodeError) as e:
            logger.warning(f"Error parsing preference {self.key} for user {self.user_id}: {e}")
            return self.value
    
    @property
    def is_ui_preference(self) -> bool:
        """Check if this is a UI preference."""
        return self.category == PreferenceCategory.UI.value
    
    @property
    def is_recommendation_preference(self) -> bool:
        """Check if this is a recommendation preference."""
        return self.category == PreferenceCategory.RECOMMENDATION.value
    
    @property
    def is_notification_preference(self) -> bool:
        """Check if this is a notification preference."""
        return self.category == PreferenceCategory.NOTIFICATION.value
    
    @property
    def key_parts(self) -> List[str]:
        """Get the key parts (for hierarchical keys)."""
        return self.key.split('.')
    
    # ============================================================
    # CLASS METHODS
    # ============================================================
    
    @classmethod
    def create(
        cls,
        user_id: str,
        key: str,
        value: Any,
        data_type: Optional[Union[str, PreferenceDataType]] = None,
        category: Optional[Union[str, PreferenceCategory]] = None,
        description: Optional[str] = None,
        is_public: bool = False,
        is_encrypted: bool = False,
        default_value: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "UserPreference":
        """
        Create a new user preference.
        
        Parameters:
        -----------
        user_id : str
            User identifier
        key : str
            Preference key
        value : Any
            Preference value
        data_type : Optional[str]
            Data type (auto-detected if not provided)
        category : Optional[str]
            Preference category
        description : Optional[str]
            Human-readable description
        is_public : bool
            Whether this preference is publicly visible
        is_encrypted : bool
            Whether this preference should be encrypted
        default_value : Optional[Any]
            Default value
        metadata : Optional[Dict[str, Any]]
            Additional metadata
        
        Returns:
        --------
        UserPreference: New preference record
        """
        # Auto-detect data type if not provided
        if data_type is None:
            data_type = cls._detect_data_type(value)
        
        # Convert enums to strings
        if isinstance(data_type, PreferenceDataType):
            data_type = data_type.value
        if isinstance(category, PreferenceCategory):
            category = category.value
        
        # Serialize value based on data type
        serialized_value = cls._serialize_value(value, data_type)
        serialized_default = cls._serialize_value(default_value, data_type) if default_value is not None else None
        
        return cls(
            user_id=user_id,
            key=key,
            value=serialized_value,
            data_type=data_type,
            category=category,
            description=description,
            is_public=is_public,
            is_encrypted=is_encrypted,
            default_value=serialized_default,
            meta_data=json.dumps(metadata) if metadata else None
        )
    
    @classmethod
    def _detect_data_type(cls, value: Any) -> str:
        """
        Detect the data type of a value.
        
        Parameters:
        -----------
        value : Any
            Value to detect type for
        
        Returns:
        --------
        str: Data type
        """
        if value is None:
            return PreferenceDataType.STRING.value
        if isinstance(value, bool):
            return PreferenceDataType.BOOLEAN.value
        if isinstance(value, int):
            return PreferenceDataType.INTEGER.value
        if isinstance(value, float):
            return PreferenceDataType.FLOAT.value
        if isinstance(value, (list, tuple)):
            return PreferenceDataType.ARRAY.value
        if isinstance(value, dict):
            return PreferenceDataType.JSON.value
        return PreferenceDataType.STRING.value
    
    @classmethod
    def _serialize_value(cls, value: Any, data_type: str) -> str:
        """
        Serialize a value based on data type.
        
        Parameters:
        -----------
        value : Any
            Value to serialize
        data_type : str
            Data type
        
        Returns:
        --------
        str: Serialized value
        """
        if value is None:
            return ""
        
        if data_type == PreferenceDataType.STRING.value:
            return str(value)
        elif data_type == PreferenceDataType.INTEGER.value:
            return str(int(value))
        elif data_type == PreferenceDataType.FLOAT.value:
            return str(float(value))
        elif data_type == PreferenceDataType.BOOLEAN.value:
            return str(value).lower()
        elif data_type in [PreferenceDataType.JSON.value, PreferenceDataType.ARRAY.value]:
            return json.dumps(value)
        else:
            return str(value)
    
    # ============================================================
    # INSTANCE METHODS
    # ============================================================
    
    def update_value(self, new_value: Any) -> None:
        """
        Update the preference value.
        
        Parameters:
        -----------
        new_value : Any
            New value
        """
        self.value = self._serialize_value(new_value, self.data_type)
        self.updated_at = func.now()
        logger.debug(f"Preference {self.key} updated for user {self.user_id}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata as dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Metadata dictionary
        """
        if not self.metad_ata:
            return {}
        try:
            return json.loads(self.meta_data)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in metadata for preference {self.id}")
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
        Convert preference to dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Preference data
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "key": self.key,
            "value": self.parsed_value,
            "data_type": self.data_type,
            "category": self.category,
            "description": self.description,
            "is_public": self.is_public,
            "is_encrypted": self.is_encrypted,
            "default_value": self.parsed_default_value if self.default_value else None,
            "version": self.version,
            "metadata": self.get_metadata(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def parsed_default_value(self) -> Any:
        """
        Get the parsed default value.
        
        Returns:
        --------
        Any: Parsed default value
        """
        if self.default_value is None:
            return None
        try:
            if self.data_type == PreferenceDataType.STRING.value:
                return self.default_value
            elif self.data_type == PreferenceDataType.INTEGER.value:
                return int(self.default_value)
            elif self.data_type == PreferenceDataType.FLOAT.value:
                return float(self.default_value)
            elif self.data_type == PreferenceDataType.BOOLEAN.value:
                return self.default_value.lower() == 'true'
            elif self.data_type == PreferenceDataType.JSON.value:
                return json.loads(self.default_value)
            elif self.data_type == PreferenceDataType.ARRAY.value:
                return json.loads(self.default_value) if self.default_value else []
            else:
                return self.default_value
        except (ValueError, json.JSONDecodeError):
            return self.default_value
    
    # ============================================================
    # VALIDATION HELPERS
    # ============================================================
    
    @staticmethod
    def validate_key(key: str) -> bool:
        """
        Validate preference key.
        
        Parameters:
        -----------
        key : str
            Preference key to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        if not key or not key.strip():
            return False
        if len(key) > 100:
            return False
        # Allow alphanumeric, dots, underscores, and hyphens
        import re
        return bool(re.match(r'^[a-zA-Z0-9._-]+$', key))
    
    @staticmethod
    def validate_category(category: str) -> bool:
        """
        Validate preference category.
        
        Parameters:
        -----------
        category : str
            Category to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        valid_categories = [c.value for c in PreferenceCategory]
        return category in valid_categories
    
    # ============================================================
    # DUNDER METHODS
    # ============================================================
    
    def __repr__(self) -> str:
        """String representation of the preference."""
        return f"<UserPreference(id={self.id}, user={self.user_id}, key='{self.key}', type='{self.data_type}')>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        value_preview = str(self.parsed_value)[:50]
        return f"Preference '{self.key}' for user {self.user_id}: {value_preview}..."


# ============================================================
# PREFERENCE MANAGER UTILITY
# ============================================================

class PreferenceManager:
    """
    Utility class for managing user preferences.
    
    Provides convenience methods for common preference operations.
    """
    
    # Common preference keys
    THEME = "ui.theme"
    LANGUAGE = "ui.language"
    FONT_SIZE = "ui.font_size"
    RECOMMENDATION_COUNT = "recommendation.count"
    RECOMMENDATION_WEIGHTS = "recommendation.weights"
    NOTIFICATION_EMAIL = "notification.email"
    NOTIFICATION_PUSH = "notification.push"
    PRIVACY_PROFILE = "privacy.profile"
    
    def __init__(self, user_id: str, session):
        """
        Initialize the preference manager.
        
        Parameters:
        -----------
        user_id : str
            User identifier
        session : SQLAlchemy session
            Database session
        """
        self.user_id = user_id
        self.session = session
        self._cache = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a preference value.
        
        Parameters:
        -----------
        key : str
            Preference key
        default : Any
            Default value if not found
        
        Returns:
        --------
        Any: Preference value
        """
        # Check cache first
        if key in self._cache:
            return self._cache[key]
        
        # Query database
        pref = self.session.query(UserPreference).filter_by(
            user_id=self.user_id,
            key=key
        ).first()
        
        if pref:
            value = pref.parsed_value
            self._cache[key] = value
            return value
        
        return default
    
    def set(self, key: str, value: Any, **kwargs) -> None:
        """
        Set a preference value.
        
        Parameters:
        -----------
        key : str
            Preference key
        value : Any
            Preference value
        **kwargs : Additional arguments passed to UserPreference.create
        """
        # Check if exists
        pref = self.session.query(UserPreference).filter_by(
            user_id=self.user_id,
            key=key
        ).first()
        
        if pref:
            pref.update_value(value)
        else:
            pref = UserPreference.create(
                user_id=self.user_id,
                key=key,
                value=value,
                **kwargs
            )
            self.session.add(pref)
        
        # Update cache
        self._cache[key] = value
        self.session.commit()
    
    def get_ui_preferences(self) -> Dict[str, Any]:
        """
        Get all UI preferences.
        
        Returns:
        --------
        Dict[str, Any]: UI preferences
        """
        prefs = self.session.query(UserPreference).filter_by(
            user_id=self.user_id,
            category=PreferenceCategory.UI.value
        ).all()
        
        return {p.key: p.parsed_value for p in prefs}
    
    def get_recommendation_preferences(self) -> Dict[str, Any]:
        """
        Get all recommendation preferences.
        
        Returns:
        --------
        Dict[str, Any]: Recommendation preferences
        """
        prefs = self.session.query(UserPreference).filter_by(
            user_id=self.user_id,
            category=PreferenceCategory.RECOMMENDATION.value
        ).all()
        
        return {p.key: p.parsed_value for p in prefs}
    
    def clear_cache(self) -> None:
        """Clear the preference cache."""
        self._cache.clear()
    
    def delete(self, key: str) -> bool:
        """
        Delete a preference.
        
        Parameters:
        -----------
        key : str
            Preference key
        
        Returns:
        --------
        bool: True if deleted, False if not found
        """
        pref = self.session.query(UserPreference).filter_by(
            user_id=self.user_id,
            key=key
        ).first()
        
        if pref:
            self.session.delete(pref)
            self.session.commit()
            if key in self._cache:
                del self._cache[key]
            return True
        
        return False


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    import json
    from datetime import datetime
    
    print("=" * 60)
    print("USER PREFERENCE MODEL TEST")
    print("=" * 60)
    
    # Test 1: Create various preferences
    print("\n📌 Test 1: Create Preferences")
    
    # String preference
    pref1 = UserPreference.create(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        key="ui.theme",
        value="dark",
        category=PreferenceCategory.UI,
        description="UI theme preference",
        is_public=True
    )
    print(f"✅ String preference: {pref1.key} = {pref1.parsed_value}")
    
    # Integer preference
    pref2 = UserPreference.create(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        key="recommendation.count",
        value=20,
        category=PreferenceCategory.RECOMMENDATION,
        data_type=PreferenceDataType.INTEGER
    )
    print(f"✅ Integer preference: {pref2.key} = {pref2.parsed_value}")
    
    # JSON preference
    pref3 = UserPreference.create(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        key="recommendation.weights",
        value={"collaborative": 0.5, "content": 0.3, "popularity": 0.2},
        category=PreferenceCategory.RECOMMENDATION,
        data_type=PreferenceDataType.JSON
    )
    print(f"✅ JSON preference: {pref3.key} = {pref3.parsed_value}")
    
    # Boolean preference
    pref4 = UserPreference.create(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        key="notification.email",
        value=True,
        category=PreferenceCategory.NOTIFICATION,
        data_type=PreferenceDataType.BOOLEAN
    )
    print(f"✅ Boolean preference: {pref4.key} = {pref4.parsed_value}")
    
    # Array preference
    pref5 = UserPreference.create(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        key="ui.categories",
        value=["Fiction", "Science", "History"],
        category=PreferenceCategory.UI,
        data_type=PreferenceDataType.ARRAY
    )
    print(f"✅ Array preference: {pref5.key} = {pref5.parsed_value}")
    
    # Test 2: Update value
    print("\n📌 Test 2: Update Value")
    pref1.update_value("light")
    print(f"  Theme updated to: {pref1.parsed_value}")
    
    # Test 3: Auto-detect data type
    print("\n📌 Test 3: Auto-detect Data Type")
    test_values = [
        ("string value", PreferenceDataType.STRING),
        (42, PreferenceDataType.INTEGER),
        (3.14, PreferenceDataType.FLOAT),
        (True, PreferenceDataType.BOOLEAN),
        ([1, 2, 3], PreferenceDataType.ARRAY),
        ({"key": "value"}, PreferenceDataType.JSON)
    ]
    for value, expected_type in test_values:
        detected = UserPreference._detect_data_type(value)
        print(f"  {value} -> {detected} (expected: {expected_type.value})")
    
    # Test 4: To dict
    print("\n📌 Test 4: To Dict")
    data = pref1.to_dict()
    print(f"  Data: {json.dumps(data, indent=2)}")
    
    # Test 5: Validation
    print("\n📌 Test 5: Validation")
    print(f"  Valid key 'ui.theme': {UserPreference.validate_key('ui.theme')}")
    print(f"  Valid key 'invalid!@#': {UserPreference.validate_key('invalid!@#')}")
    print(f"  Valid category 'ui': {UserPreference.validate_category('ui')}")
    print(f"  Valid category 'invalid': {UserPreference.validate_category('invalid')}")
    
    print("\n✅ All tests completed!")