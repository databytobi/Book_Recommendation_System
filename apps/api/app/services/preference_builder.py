"""
Preference Builder

Builds user preference profiles from onboarding selections.
Handles weight generation and preference creation.

Phase: Services / Onboarding
"""

from typing import List, Dict, Optional, Any
import logging
from datetime import datetime

from app.schemas.user_preference import (
    RecommendationPreference,
    WeightedAuthor,
    WeightedBook,
)
from app.repositories.user_preference_repository import (
    UserPreferenceRepository,
)

logger = logging.getLogger(__name__)


class PreferenceBuilder:
    """
    Builds user preference profiles from onboarding selections.
    
    Features:
    - Generate weighted preferences from selections
    - Validate input data
    - Create and save preference profiles
    - Support for incremental updates
    - Batch processing
    """
    
    # Default weight configuration
    DEFAULT_WEIGHT_START = 1.0
    DEFAULT_WEIGHT_STEP = 0.05
    DEFAULT_WEIGHT_MINIMUM = 0.50
    
    # Maximum selections allowed
    MAX_AUTHORS = 100
    MAX_BOOKS = 50
    MAX_GENRES = 30
    
    def __init__(
        self,
        repository: UserPreferenceRepository,
        weight_start: float = DEFAULT_WEIGHT_START,
        weight_step: float = DEFAULT_WEIGHT_STEP,
        weight_minimum: float = DEFAULT_WEIGHT_MINIMUM,
    ):
        """
        Initialize the preference builder.
        
        Parameters:
        -----------
        repository : UserPreferenceRepository
            Repository for storing preferences
        weight_start : float
            Starting weight for the first item
        weight_step : float
            Decrease per item
        weight_minimum : float
            Minimum weight value
        """
        self.repository = repository
        self.weight_start = weight_start
        self.weight_step = weight_step
        self.weight_minimum = weight_minimum
        
        # Validate weight configuration
        self._validate_weight_config()
    
    def _validate_weight_config(self) -> None:
        """Validate weight configuration parameters."""
        if not 0.0 <= self.weight_start <= 1.0:
            raise ValueError("weight_start must be between 0.0 and 1.0")
        
        if not 0.0 <= self.weight_step <= 1.0:
            raise ValueError("weight_step must be between 0.0 and 1.0")
        
        if not 0.0 <= self.weight_minimum <= 1.0:
            raise ValueError("weight_minimum must be between 0.0 and 1.0")
        
        if self.weight_minimum > self.weight_start:
            raise ValueError("weight_minimum cannot be greater than weight_start")
    
    def build(
        self,
        user_id: int,
        genres: Optional[Dict[str, float]] = None,
        authors: Optional[List[WeightedAuthor]] = None,
        books: Optional[List[WeightedBook]] = None,
        version: int = 1,
    ) -> RecommendationPreference:
        """
        Build a recommendation preference profile.
        
        Parameters:
        -----------
        user_id : int
            User ID
        genres : Optional[Dict[str, float]]
            Genre preferences with weights
        authors : Optional[List[WeightedAuthor]]
            Author preferences with weights
        books : Optional[List[WeightedBook]]
            Book preferences with weights
        version : int
            Preference version
        
        Returns:
        --------
        RecommendationPreference: Built preference profile
        
        Raises:
        -------
        ValueError: If input validation fails
        """
        # Validate inputs
        self._validate_inputs(genres, authors, books)
        
        # Use provided values or defaults
        genres = genres or {}
        authors = authors or []
        books = books or []
        
        # Validate weights
        self._validate_weights(genres, authors, books)
        
        # Create preference
        preference = RecommendationPreference(
            genres=genres,
            authors=authors,
            favorite_books=books,
            version=version,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        logger.info(f"Built preference profile for user {user_id}: "
                   f"{len(genres)} genres, {len(authors)} authors, {len(books)} books")
        
        return preference
    
    def build_from_lists(
        self,
        user_id: int,
        genres: Optional[List[str]] = None,
        author_ids: Optional[List[int]] = None,
        book_isbns: Optional[List[str]] = None,
        genre_weights: Optional[Dict[str, float]] = None,
        author_weights: Optional[Dict[int, float]] = None,
        book_weights: Optional[Dict[str, float]] = None,
    ) -> RecommendationPreference:
        """
        Build a preference profile from lists of IDs.
        
        Parameters:
        -----------
        user_id : int
            User ID
        genres : Optional[List[str]]
            List of genre names
        author_ids : Optional[List[int]]
            List of author IDs
        book_isbns : Optional[List[str]]
            List of book ISBNs
        genre_weights : Optional[Dict[str, float]]
            Custom genre weights
        author_weights : Optional[Dict[int, float]]
            Custom author weights
        book_weights : Optional[Dict[str, float]]
            Custom book weights
        
        Returns:
        --------
        RecommendationPreference: Built preference profile
        """
        # Normalize inputs
        genres = genres or []
        author_ids = author_ids or []
        book_isbns = book_isbns or []
        
        # Validate counts
        self._validate_count("genres", len(genres), self.MAX_GENRES)
        self._validate_count("authors", len(author_ids), self.MAX_AUTHORS)
        self._validate_count("books", len(book_isbns), self.MAX_BOOKS)
        
        # Generate weights
        genre_weights_dict = self._build_genre_weights(genres, genre_weights)
        author_weights_list = self._build_author_weights(author_ids, author_weights)
        book_weights_list = self._build_book_weights(book_isbns, book_weights)
        
        # Create preference
        return self.build(
            user_id=user_id,
            genres=genre_weights_dict,
            authors=author_weights_list,
            books=book_weights_list,
        )
    
    def build_and_save(
        self,
        user_id: int,
        genres: Optional[Dict[str, float]] = None,
        authors: Optional[List[WeightedAuthor]] = None,
        books: Optional[List[WeightedBook]] = None,
    ) -> RecommendationPreference:
        """
        Build and save a new preference profile.
        
        Parameters:
        -----------
        user_id : int
            User ID
        genres : Optional[Dict[str, float]]
            Genre preferences
        authors : Optional[List[WeightedAuthor]]
            Author preferences
        books : Optional[List[WeightedBook]]
            Book preferences
        
        Returns:
        --------
        RecommendationPreference: Saved preference profile
        """
        preference = self.build(
            user_id=user_id,
            genres=genres,
            authors=authors,
            books=books,
        )
        
        return self.save(user_id, preference)
    
    def build_and_save_from_lists(
        self,
        user_id: int,
        genres: Optional[List[str]] = None,
        author_ids: Optional[List[int]] = None,
        book_isbns: Optional[List[str]] = None,
    ) -> RecommendationPreference:
        """
        Build and save a preference profile from lists of IDs.
        
        Parameters:
        -----------
        user_id : int
            User ID
        genres : Optional[List[str]]
            List of genre names
        author_ids : Optional[List[int]]
            List of author IDs
        book_isbns : Optional[List[str]]
            List of book ISBNs
        
        Returns:
        --------
        RecommendationPreference: Saved preference profile
        """
        preference = self.build_from_lists(
            user_id=user_id,
            genres=genres,
            author_ids=author_ids,
            book_isbns=book_isbns,
        )
        
        return self.save(user_id, preference)
    
    def save(
        self,
        user_id: int,
        preference: RecommendationPreference,
    ) -> RecommendationPreference:
        """
        Save a preference profile to the repository.
        
        Parameters:
        -----------
        user_id : int
            User ID
        preference : RecommendationPreference
            Preference to save
        
        Returns:
        --------
        RecommendationPreference: Saved preference
        """
        if not user_id or user_id <= 0:
            raise ValueError("Invalid user_id")
        
        try:
            # Check if preferences already exist
            existing = self.repository.get(user_id)
            
            if existing:
                # Update existing preferences
                logger.info(f"Updating existing preferences for user {user_id}")
                return self.repository.update(user_id, preference)
            else:
                # Save new preferences
                logger.info(f"Saving new preferences for user {user_id}")
                self.repository.save(user_id, preference)
                return preference
                
        except Exception as e:
            logger.error(f"Error saving preferences for user {user_id}: {e}")
            raise
    
    def update_from_selections(
        self,
        user_id: int,
        genres: Optional[List[str]] = None,
        author_ids: Optional[List[int]] = None,
        book_isbns: Optional[List[str]] = None,
        merge: bool = True,
    ) -> Optional[RecommendationPreference]:
        """
        Update existing preferences with new selections.
        
        Parameters:
        -----------
        user_id : int
            User ID
        genres : Optional[List[str]]
            New genre selections
        author_ids : Optional[List[int]]
            New author selections
        book_isbns : Optional[List[str]]
            New book selections
        merge : bool
            If True, merge with existing preferences
            If False, replace completely
        
        Returns:
        --------
        Optional[RecommendationPreference]: Updated preference or None
        """
        # Get existing preferences
        existing = self.repository.get(user_id)
        
        if existing is None:
            # Create new preferences if none exist
            return self.build_and_save_from_lists(
                user_id=user_id,
                genres=genres,
                author_ids=author_ids,
                book_isbns=book_isbns,
            )
        
        # Build new preferences from selections
        new_preference = self.build_from_lists(
            user_id=user_id,
            genres=genres,
            author_ids=author_ids,
            book_isbns=book_isbns,
        )
        
        if merge:
            # Merge with existing
            merged = self._merge_preferences(existing, new_preference)
            return self.save(user_id, merged)
        else:
            # Replace completely
            return self.save(user_id, new_preference)
    
    def _build_genre_weights(
        self,
        genres: List[str],
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """Build genre weights dictionary."""
        weights = self._generate_weights(len(genres))
        
        result = {}
        for i, genre in enumerate(genres):
            # Use custom weight if provided, otherwise generated weight
            weight = custom_weights.get(genre, weights[i]) if custom_weights else weights[i]
            result[genre] = max(min(weight, 1.0), 0.0)
        
        return result
    
    def _build_author_weights(
        self,
        author_ids: List[int],
        custom_weights: Optional[Dict[int, float]] = None
    ) -> List[WeightedAuthor]:
        """Build author weights list."""
        weights = self._generate_weights(len(author_ids))
        
        result = []
        for i, author_id in enumerate(author_ids):
            weight = custom_weights.get(author_id, weights[i]) if custom_weights else weights[i]
            result.append(
                WeightedAuthor(
                    id=author_id,
                    weight=max(min(weight, 1.0), 0.0)
                )
            )
        
        return result
    
    def _build_book_weights(
        self,
        book_isbns: List[str],
        custom_weights: Optional[Dict[str, float]] = None
    ) -> List[WeightedBook]:
        """Build book weights list."""
        weights = self._generate_weights(len(book_isbns))
        
        result = []
        for i, isbn in enumerate(book_isbns):
            weight = custom_weights.get(isbn, weights[i]) if custom_weights else weights[i]
            result.append(
                WeightedBook(
                    isbn=isbn,
                    weight=max(min(weight, 1.0), 0.0)
                )
            )
        
        return result
    
    def _generate_weights(
        self,
        count: int,
        start: Optional[float] = None,
        step: Optional[float] = None,
        minimum: Optional[float] = None,
    ) -> List[float]:
        """
        Generate descending weights based on selection order.
        
        Example:
            count=5, start=1.0, step=0.05, minimum=0.50
            Returns: [1.00, 0.95, 0.90, 0.85, 0.80]
        
        Parameters:
        -----------
        count : int
            Number of weights to generate
        start : Optional[float]
            Starting weight (default: self.weight_start)
        step : Optional[float]
            Decrease per item (default: self.weight_step)
        minimum : Optional[float]
            Minimum weight (default: self.weight_minimum)
        
        Returns:
        --------
        List[float]: Generated weights
        """
        if count <= 0:
            return []
        
        start = start if start is not None else self.weight_start
        step = step if step is not None else self.weight_step
        minimum = minimum if minimum is not None else self.weight_minimum
        
        weights = []
        current = start
        
        for _ in range(count):
            weights.append(max(current, minimum))
            current -= step
        
        return weights
    
    def _merge_preferences(
        self,
        existing: RecommendationPreference,
        new: RecommendationPreference,
    ) -> RecommendationPreference:
        """Merge two preference profiles."""
        # Merge genres
        merged_genres = existing.genres.copy()
        merged_genres.update(new.genres)
        
        # Merge authors (deduplicate by ID)
        author_map = {a.id: a for a in existing.authors}
        for author in new.authors:
            if author.id in author_map:
                # Update existing author weight
                author_map[author.id].weight = author.weight
            else:
                author_map[author.id] = author
        merged_authors = list(author_map.values())
        
        # Merge books (deduplicate by ISBN)
        book_map = {b.isbn: b for b in existing.favorite_books}
        for book in new.favorite_books:
            if book.isbn in book_map:
                # Update existing book weight
                book_map[book.isbn].weight = book.weight
            else:
                book_map[book.isbn] = book
        merged_books = list(book_map.values())
        
        return RecommendationPreference(
            genres=merged_genres,
            authors=merged_authors,
            favorite_books=merged_books,
            version=existing.version + 1,
            created_at=existing.created_at,
            updated_at=datetime.now(),
        )
    
    def _validate_inputs(
        self,
        genres: Optional[Dict[str, float]],
        authors: Optional[List[WeightedAuthor]],
        books: Optional[List[WeightedBook]],
    ) -> None:
        """Validate input data."""
        # Validate genres count
        if genres:
            self._validate_count("genres", len(genres), self.MAX_GENRES)
        
        # Validate authors count
        if authors:
            self._validate_count("authors", len(authors), self.MAX_AUTHORS)
            for author in authors:
                if not author.id or author.id <= 0:
                    raise ValueError("Invalid author ID")
        
        # Validate books count
        if books:
            self._validate_count("books", len(books), self.MAX_BOOKS)
            for book in books:
                if not book.isbn or len(book.isbn) < 10:
                    raise ValueError(f"Invalid ISBN: {book.isbn}")
    
    def _validate_weights(
        self,
        genres: Dict[str, float],
        authors: List[WeightedAuthor],
        books: List[WeightedBook],
    ) -> None:
        """Validate weights are within bounds."""
        for genre, weight in genres.items():
            if not 0.0 <= weight <= 1.0:
                raise ValueError(f"Invalid weight {weight} for genre '{genre}'")
        
        for author in authors:
            if not 0.0 <= author.weight <= 1.0:
                raise ValueError(f"Invalid weight {author.weight} for author {author.id}")
        
        for book in books:
            if not 0.0 <= book.weight <= 1.0:
                raise ValueError(f"Invalid weight {book.weight} for book {book.isbn}")
    
    def _validate_count(self, name: str, count: int, max_count: int) -> None:
        """Validate item count doesn't exceed maximum."""
        if count > max_count:
            raise ValueError(f"Too many {name}: {count} (max: {max_count})")
    
    def get_default_preference(self) -> RecommendationPreference:
        """
        Get a default preference profile.
        
        Returns:
        --------
        RecommendationPreference: Default preferences
        """
        return RecommendationPreference(
            genres={},
            authors=[],
            favorite_books=[],
            version=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
    
    def create_empty_preference(self, user_id: int) -> RecommendationPreference:
        """
        Create and save an empty preference profile for a user.
        
        Parameters:
        -----------
        user_id : int
            User ID
        
        Returns:
        --------
        RecommendationPreference: Empty preference profile
        """
        preference = self.get_default_preference()
        return self.save(user_id, preference)