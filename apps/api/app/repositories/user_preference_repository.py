"""
User Preference Repository

Repository for managing user preferences with CRUD operations,
bulk operations, and preference management.

Phase: Data Access Layer
"""

from typing import Any, Dict, List, Optional, Union, TypeVar, Generic
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.user_preference import (
    UserPreference,
    PreferenceCategory,
    PreferenceDataType,
)

logger = logging.getLogger(__name__)
T = TypeVar('T')


class UserPreferenceRepository:
    """
    Repository for managing user preferences.
    
    Provides comprehensive CRUD operations for user preferences with
    support for JSON storage, categories, and bulk operations.
    
    Features:
    - Basic CRUD operations
    - Key-value preference management
    - Category-based organization
    - Bulk operations
    - Transaction support
    - Audit logging
    """
    
    def __init__(self, db: Session):
        """
        Initialize the repository.
        
        Parameters:
        -----------
        db : Session
            SQLAlchemy database session
        """
        self.db = db
    
    # ============================================================
    # Basic CRUD Operations
    # ============================================================
    
    def create(self, preference: UserPreference) -> UserPreference:
        """
        Create a new preference record.
        
        Parameters:
        -----------
        preference : UserPreference
            Preference record to create
        
        Returns:
        --------
        UserPreference: Created preference record
        
        Raises:
        -------
        ValueError: If preference is invalid
        SQLAlchemyError: If database operation fails
        """
        if not preference:
            raise ValueError("Preference cannot be None")
        
        try:
            self.db.add(preference)
            self.db.commit()
            self.db.refresh(preference)
            
            logger.debug(f"Created preference {preference.key} for user {preference.user_id}")
            return preference
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to create preference: {e}")
            raise
    
    def update(self, preference: UserPreference) -> UserPreference:
        """
        Update an existing preference record.
        
        Parameters:
        -----------
        preference : UserPreference
            Preference record to update
        
        Returns:
        --------
        UserPreference: Updated preference record
        
        Raises:
        -------
        ValueError: If preference is None
        SQLAlchemyError: If database operation fails
        """
        if not preference:
            raise ValueError("Preference cannot be None")
        
        try:
            self.db.commit()
            self.db.refresh(preference)
            
            logger.debug(f"Updated preference {preference.key} for user {preference.user_id}")
            return preference
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to update preference: {e}")
            raise
    
    def delete(self, preference: UserPreference) -> bool:
        """
        Delete a preference record.
        
        Parameters:
        -----------
        preference : UserPreference
            Preference record to delete
        
        Returns:
        --------
        bool: True if deleted successfully
        
        Raises:
        -------
        ValueError: If preference is None
        SQLAlchemyError: If database operation fails
        """
        if not preference:
            raise ValueError("Preference cannot be None")
        
        try:
            self.db.delete(preference)
            self.db.commit()
            
            logger.debug(f"Deleted preference {preference.key} for user {preference.user_id}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to delete preference: {e}")
            raise
    
    # ============================================================
    # Lookup Operations
    # ============================================================
    
    def get_by_id(self, preference_id: int) -> Optional[UserPreference]:
        """
        Get a preference by its ID.
        
        Parameters:
        -----------
        preference_id : int
            Preference record ID
        
        Returns:
        --------
        Optional[UserPreference]: Preference record or None
        """
        try:
            return (
                self.db.query(UserPreference)
                .filter(UserPreference.id == preference_id)
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(f"Failed to get preference by ID {preference_id}: {e}")
            return None
    
    def get_by_user(
        self,
        user_id: int,
        include_deleted: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[UserPreference]:
        """
        Get all preferences for a user.
        
        Parameters:
        -----------
        user_id : int
            User ID
        include_deleted : bool
            Whether to include soft-deleted preferences
        limit : Optional[int]
            Maximum number of records to return
        offset : Optional[int]
            Number of records to skip
        
        Returns:
        --------
        List[UserPreference]: List of preference records
        """
        try:
            query = self.db.query(UserPreference).filter(
                UserPreference.user_id == user_id
            )
            
            if not include_deleted:
                query = query.filter(UserPreference.is_deleted == False)
            
            if limit is not None:
                query = query.limit(limit)
            if offset is not None:
                query = query.offset(offset)
            
            return query.all()
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get preferences for user {user_id}: {e}")
            return []
    
    def get_by_key(
        self,
        user_id: int,
        key: str,
        include_deleted: bool = False,
    ) -> Optional[UserPreference]:
        """
        Get a preference by its key.
        
        Parameters:
        -----------
        user_id : int
            User ID
        key : str
            Preference key
        include_deleted : bool
            Whether to include soft-deleted preferences
        
        Returns:
        --------
        Optional[UserPreference]: Preference record or None
        """
        try:
            query = self.db.query(UserPreference).filter(
                UserPreference.user_id == user_id,
                UserPreference.key == key,
            )
            
            if not include_deleted:
                query = query.filter(UserPreference.is_deleted == False)
            
            return query.first()
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get preference {key} for user {user_id}: {e}")
            return None
    
    def get_by_category(
        self,
        user_id: int,
        category: PreferenceCategory,
        include_deleted: bool = False,
    ) -> List[UserPreference]:
        """
        Get preferences by category.
        
        Parameters:
        -----------
        user_id : int
            User ID
        category : PreferenceCategory
            Preference category
        include_deleted : bool
            Whether to include soft-deleted preferences
        
        Returns:
        --------
        List[UserPreference]: List of preference records
        """
        try:
            query = self.db.query(UserPreference).filter(
                UserPreference.user_id == user_id,
                UserPreference.category == category,
            )
            
            if not include_deleted:
                query = query.filter(UserPreference.is_deleted == False)
            
            return query.all()
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get preferences by category {category} for user {user_id}: {e}")
            return []
    
    def get_by_data_type(
        self,
        user_id: int,
        data_type: PreferenceDataType,
    ) -> List[UserPreference]:
        """
        Get preferences by data type.
        
        Parameters:
        -----------
        user_id : int
            User ID
        data_type : PreferenceDataType
            Preference data type
        
        Returns:
        --------
        List[UserPreference]: List of preference records
        """
        try:
            return (
                self.db.query(UserPreference)
                .filter(
                    UserPreference.user_id == user_id,
                    UserPreference.data_type == data_type,
                )
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Failed to get preferences by data type {data_type} for user {user_id}: {e}")
            return []
    
    def get_all_by_user_ids(
        self,
        user_ids: List[int],
        include_deleted: bool = False,
    ) -> Dict[int, List[UserPreference]]:
        """
        Get preferences for multiple users.
        
        Parameters:
        -----------
        user_ids : List[int]
            List of user IDs
        include_deleted : bool
            Whether to include soft-deleted preferences
        
        Returns:
        --------
        Dict[int, List[UserPreference]]: Mapping of user_id to preferences
        """
        if not user_ids:
            return {}
        
        try:
            query = self.db.query(UserPreference).filter(
                UserPreference.user_id.in_(user_ids)
            )
            
            if not include_deleted:
                query = query.filter(UserPreference.is_deleted == False)
            
            records = query.all()
            
            result = {}
            for record in records:
                if record.user_id not in result:
                    result[record.user_id] = []
                result[record.user_id].append(record)
            
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get preferences for multiple users: {e}")
            return {}
    
    # ============================================================
    # Dictionary Helpers
    # ============================================================
    
    def get_preferences_dict(
        self,
        user_id: int,
        include_metadata: bool = False,
    ) -> Dict[str, Any]:
        """
        Get preferences as a dictionary.
        
        Parameters:
        -----------
        user_id : int
            User ID
        include_metadata : bool
            Whether to include metadata in the dictionary
        
        Returns:
        --------
        Dict[str, Any]: Dictionary of preferences
        """
        prefs = self.get_by_user(user_id)
        
        result = {}
        for p in prefs:
            if include_metadata:
                result[p.key] = {
                    "value": p.value,
                    "category": p.category,
                    "data_type": p.data_type,
                    "description": p.description,
                    "is_public": p.is_public,
                    "metadata": p.metadata,
                }
            else:
                result[p.key] = p.value
        
        return result
    
    def get_preferences_by_category_dict(
        self,
        user_id: int,
    ) -> Dict[PreferenceCategory, Dict[str, Any]]:
        """
        Get preferences organized by category.
        
        Parameters:
        -----------
        user_id : int
            User ID
        
        Returns:
        --------
        Dict[PreferenceCategory, Dict[str, Any]]: Category-organized preferences
        """
        prefs = self.get_by_user(user_id)
        
        result = {}
        for p in prefs:
            if p.category not in result:
                result[p.category] = {}
            result[p.category][p.key] = p.value
        
        return result
    
    # ============================================================
    # Upsert Operations
    # ============================================================
    
    def set_preference(
        self,
        user_id: int,
        key: str,
        value: Any,
        category: Optional[PreferenceCategory] = None,
        data_type: Optional[PreferenceDataType] = None,
        description: Optional[str] = None,
        is_public: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UserPreference:
        """
        Set a preference (create or update).
        
        Parameters:
        -----------
        user_id : int
            User ID
        key : str
            Preference key
        value : Any
            Preference value
        category : Optional[PreferenceCategory]
            Preference category
        data_type : Optional[PreferenceDataType]
            Preference data type
        description : Optional[str]
            Preference description
        is_public : bool
            Whether the preference is public
        metadata : Optional[Dict[str, Any]]
            Additional metadata
        
        Returns:
        --------
        UserPreference: Created or updated preference record
        """
        try:
            # Try to get existing preference
            pref = self.get_by_key(user_id, key)
            
            if pref:
                # Update existing
                pref.value = value
                if category is not None:
                    pref.category = category
                if data_type is not None:
                    pref.data_type = data_type
                if description is not None:
                    pref.description = description
                pref.is_public = is_public
                if metadata is not None:
                    pref.metadata = metadata
                
                # Update timestamp
                if hasattr(pref, 'updated_at'):
                    pref.updated_at = datetime.now()
                
                self.db.commit()
                self.db.refresh(pref)
                
                logger.debug(f"Updated preference {key} for user {user_id}")
                return pref
            
            # Create new preference
            pref = UserPreference.create(
                user_id=user_id,
                key=key,
                value=value,
                category=category or PreferenceCategory.GENERAL,
                data_type=data_type or self._infer_data_type(value),
                description=description or key,
                is_public=is_public,
                metadata=metadata or {},
            )
            
            self.db.add(pref)
            self.db.commit()
            self.db.refresh(pref)
            
            logger.debug(f"Created preference {key} for user {user_id}")
            return pref
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to set preference {key} for user {user_id}: {e}")
            raise
    
    def set_preferences(
        self,
        user_id: int,
        preferences: Dict[str, Any],
        category: Optional[PreferenceCategory] = None,
        data_type: Optional[PreferenceDataType] = None,
        description_prefix: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[UserPreference]:
        """
        Set multiple preferences at once.
        
        Parameters:
        -----------
        user_id : int
            User ID
        preferences : Dict[str, Any]
            Dictionary of preferences
        category : Optional[PreferenceCategory]
            Default category for all preferences
        data_type : Optional[PreferenceDataType]
            Default data type for all preferences
        description_prefix : Optional[str]
            Prefix for descriptions
        metadata : Optional[Dict[str, Any]]
            Metadata to merge with each preference
        
        Returns:
        --------
        List[UserPreference]: Created or updated preference records
        """
        results = []
        
        try:
            for key, value in preferences.items():
                pref = self.set_preference(
                    user_id=user_id,
                    key=key,
                    value=value,
                    category=category,
                    data_type=data_type,
                    description=f"{description_prefix or ''} {key}".strip() if description_prefix else key,
                    is_public=False,
                    metadata=metadata,
                )
                results.append(pref)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to set preferences for user {user_id}: {e}")
            raise
    
    # ============================================================
    # Delete Operations
    # ============================================================
    
    def delete_key(
        self,
        user_id: int,
        key: str,
    ) -> bool:
        """
        Delete a preference by key.
        
        Parameters:
        -----------
        user_id : int
            User ID
        key : str
            Preference key
        
        Returns:
        --------
        bool: True if deleted, False if not found
        """
        pref = self.get_by_key(user_id, key)
        
        if not pref:
            logger.warning(f"Preference {key} not found for user {user_id}")
            return False
        
        return self.delete(pref)
    
    def delete_category(
        self,
        user_id: int,
        category: PreferenceCategory,
        hard_delete: bool = True,
    ) -> int:
        """
        Delete all preferences in a category.
        
        Parameters:
        -----------
        user_id : int
            User ID
        category : PreferenceCategory
            Category to delete
        hard_delete : bool
            If True, permanently delete
            If False, soft delete (mark as deleted)
        
        Returns:
        --------
        int: Number of preferences deleted
        """
        try:
            prefs = self.get_by_category(user_id, category)
            count = len(prefs)
            
            if hard_delete:
                for pref in prefs:
                    self.db.delete(pref)
            else:
                for pref in prefs:
                    if hasattr(pref, 'is_deleted'):
                        pref.is_deleted = True
                    if hasattr(pref, 'deleted_at'):
                        pref.deleted_at = datetime.now()
            
            self.db.commit()
            logger.info(f"Deleted {count} preferences in category {category} for user {user_id}")
            return count
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to delete category {category} for user {user_id}: {e}")
            raise
    
    def delete_all_for_user(
        self,
        user_id: int,
        hard_delete: bool = True,
    ) -> int:
        """
        Delete all preferences for a user.
        
        Parameters:
        -----------
        user_id : int
            User ID
        hard_delete : bool
            If True, permanently delete
            If False, soft delete
        
        Returns:
        --------
        int: Number of preferences deleted
        """
        try:
            prefs = self.get_by_user(user_id)
            count = len(prefs)
            
            if hard_delete:
                for pref in prefs:
                    self.db.delete(pref)
            else:
                for pref in prefs:
                    if hasattr(pref, 'is_deleted'):
                        pref.is_deleted = True
                    if hasattr(pref, 'deleted_at'):
                        pref.deleted_at = datetime.now()
            
            self.db.commit()
            logger.info(f"Deleted {count} preferences for user {user_id}")
            return count
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to delete preferences for user {user_id}: {e}")
            raise
    
    # ============================================================
    # Batch Operations
    # ============================================================
    
    def bulk_create(
        self,
        preferences: List[UserPreference],
    ) -> List[UserPreference]:
        """
        Bulk create preference records.
        
        Parameters:
        -----------
        preferences : List[UserPreference]
            List of preferences to create
        
        Returns:
        --------
        List[UserPreference]: Created preference records
        """
        if not preferences:
            return []
        
        try:
            self.db.add_all(preferences)
            self.db.commit()
            
            for pref in preferences:
                self.db.refresh(pref)
            
            logger.info(f"Bulk created {len(preferences)} preferences")
            return preferences
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to bulk create preferences: {e}")
            raise
    
    def bulk_delete(
        self,
        preferences: List[UserPreference],
    ) -> int:
        """
        Bulk delete preference records.
        
        Parameters:
        -----------
        preferences : List[UserPreference]
            List of preferences to delete
        
        Returns:
        --------
        int: Number of preferences deleted
        """
        if not preferences:
            return 0
        
        try:
            count = len(preferences)
            for pref in preferences:
                self.db.delete(pref)
            
            self.db.commit()
            logger.info(f"Bulk deleted {count} preferences")
            return count
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to bulk delete preferences: {e}")
            raise
    
    # ============================================================
    # Utility Methods
    # ============================================================
    
    def exists(
        self,
        user_id: int,
        key: str,
    ) -> bool:
        """
        Check if a preference exists.
        
        Parameters:
        -----------
        user_id : int
            User ID
        key : str
            Preference key
        
        Returns:
        --------
        bool: True if preference exists
        """
        return self.get_by_key(user_id, key) is not None
    
    def count_by_user(self, user_id: int) -> int:
        """
        Count preferences for a user.
        
        Parameters:
        -----------
        user_id : int
            User ID
        
        Returns:
        --------
        int: Number of preferences
        """
        try:
            return (
                self.db.query(UserPreference)
                .filter(UserPreference.user_id == user_id)
                .count()
            )
        except SQLAlchemyError as e:
            logger.error(f"Failed to count preferences for user {user_id}: {e}")
            return 0
    
    def count_by_category(
        self,
        user_id: int,
        category: PreferenceCategory,
    ) -> int:
        """
        Count preferences in a category.
        
        Parameters:
        -----------
        user_id : int
            User ID
        category : PreferenceCategory
            Preference category
        
        Returns:
        --------
        int: Number of preferences
        """
        try:
            return (
                self.db.query(UserPreference)
                .filter(
                    UserPreference.user_id == user_id,
                    UserPreference.category == category,
                )
                .count()
            )
        except SQLAlchemyError as e:
            logger.error(f"Failed to count preferences in category {category} for user {user_id}: {e}")
            return 0
    
    def get_categories_for_user(
        self,
        user_id: int,
    ) -> List[PreferenceCategory]:
        """
        Get all preference categories for a user.
        
        Parameters:
        -----------
        user_id : int
            User ID
        
        Returns:
        --------
        List[PreferenceCategory]: List of categories
        """
        try:
            results = (
                self.db.query(UserPreference.category)
                .filter(UserPreference.user_id == user_id)
                .distinct()
                .all()
            )
            return [r[0] for r in results]
        except SQLAlchemyError as e:
            logger.error(f"Failed to get categories for user {user_id}: {e}")
            return []
    
    def get_keys_for_user(
        self,
        user_id: int,
        category: Optional[PreferenceCategory] = None,
    ) -> List[str]:
        """
        Get all preference keys for a user.
        
        Parameters:
        -----------
        user_id : int
            User ID
        category : Optional[PreferenceCategory]
            Filter by category
        
        Returns:
        --------
        List[str]: List of preference keys
        """
        try:
            query = self.db.query(UserPreference.key).filter(
                UserPreference.user_id == user_id
            )
            
            if category is not None:
                query = query.filter(UserPreference.category == category)
            
            results = query.distinct().all()
            return [r[0] for r in results]
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get keys for user {user_id}: {e}")
            return []
    
    def get_public_preferences(
        self,
        user_id: int,
    ) -> List[UserPreference]:
        """
        Get public preferences for a user.
        
        Parameters:
        -----------
        user_id : int
            User ID
        
        Returns:
        --------
        List[UserPreference]: List of public preferences
        """
        try:
            return (
                self.db.query(UserPreference)
                .filter(
                    UserPreference.user_id == user_id,
                    UserPreference.is_public == True,
                )
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Failed to get public preferences for user {user_id}: {e}")
            return []
    
    # ============================================================
    # Helper Methods
    # ============================================================
    
    @staticmethod
    def _infer_data_type(value: Any) -> PreferenceDataType:
        """
        Infer the preference data type from the value.
        
        Parameters:
        -----------
        value : Any
            Preference value
        
        Returns:
        --------
        PreferenceDataType: Inferred data type
        """
        if isinstance(value, dict):
            return PreferenceDataType.JSON
        elif isinstance(value, list):
            return PreferenceDataType.JSON
        elif isinstance(value, bool):
            return PreferenceDataType.BOOLEAN
        elif isinstance(value, int):
            return PreferenceDataType.INTEGER
        elif isinstance(value, float):
            return PreferenceDataType.FLOAT
        else:
            return PreferenceDataType.STRING
    
    # ============================================================
    # Context Manager Support
    # ============================================================
    
    def __enter__(self):
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if exc_type is not None:
            self.db.rollback()
        else:
            self.db.commit()