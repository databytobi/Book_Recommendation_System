"""
Author Service

Business logic layer for author operations including CRUD, search,
recommendations, and popularity management.

Phase: Services
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.author import Author
from app.models.user_followed_author import UserFollowedAuthor
from app.repositories.author_repository import AuthorRepository
from app.repositories.user_followed_author_repository import UserFollowedAuthorRepository
# pyrefly: ignore [missing-import]
from app.api.v1.authors.schemas import (
    AuthorCreate,
    AuthorUpdate,
    AuthorResponse,
    AuthorSearchParams,
    AuthorListResponse
)

logger = logging.getLogger(__name__)


class AuthorService:
    """
    Service for author operations.
    
    Handles:
    - CRUD operations
    - Search and autocomplete
    - Popularity management
    - Follow/unfollow authors
    - Author recommendations
    - Statistics and analytics
    """
    
    def __init__(self, db: Session):
        """
        Initialize the author service.
        
        Parameters:
        -----------
        db : Session
            SQLAlchemy database session
        """
        self.db = db
        self.author_repo = AuthorRepository(db)
        self.follow_repo = UserFollowedAuthorRepository(db)
    
    # ============================================================
    # CRUD Operations
    # ============================================================
    
    def create_author(
        self,
        author_data: AuthorCreate,
        refresh_popularity: bool = True
    ) -> Author:
        """
        Create a new author.
        
        Parameters:
        -----------
        author_data : AuthorCreate
            Author creation data
        refresh_popularity : bool
            Whether to refresh popularity score
        
        Returns:
        --------
        Author: Created author
        
        Raises:
        -------
        ValueError: If author already exists or data is invalid
        """
        # Check if author already exists
        existing = self.author_repo.get_by_name(author_data.name)
        if existing:
            raise ValueError(f"Author '{author_data.name}' already exists")
        
        # Create author instance
        author = Author(
            name=author_data.name,
            bio=author_data.bio,
            image_url=author_data.image_url,
            birth_date=author_data.birth_date,
            death_date=author_data.death_date,
            nationality=author_data.nationality,
            website=author_data.website,
            wikipedia_url=author_data.wikipedia_url,
            popularity_score=author_data.popularity_score or 0.0,
            is_active=author_data.is_active if author_data.is_active is not None else True
        )
        
        # Save to database
        created = self.author_repo.create(author)
        
        # Refresh popularity if needed
        if refresh_popularity:
            created = self.author_repo.refresh_popularity(created)
        
        logger.info(f"Created author: {created.name} (ID: {created.id})")
        return created
    
    def get_author(
        self,
        author_id: int,
        include_books: bool = False
    ) -> Optional[Author]:
        """
        Get an author by ID.
        
        Parameters:
        -----------
        author_id : int
            Author ID
        include_books : bool
            Whether to load books relationship
        
        Returns:
        --------
        Optional[Author]: Author instance or None
        """
        if include_books:
            return self.author_repo.get_by_id_with_books(author_id)
        return self.author_repo.get_by_id(author_id)
    
    def get_author_by_name(
        self,
        name: str,
        case_sensitive: bool = False
    ) -> Optional[Author]:
        """
        Get an author by name.
        
        Parameters:
        -----------
        name : str
            Author name
        case_sensitive : bool
            Whether to match case sensitively
        
        Returns:
        --------
        Optional[Author]: Author instance or None
        """
        return self.author_repo.get_by_name(name, case_sensitive)
    
    def update_author(
        self,
        author_id: int,
        author_data: AuthorUpdate,
        refresh_popularity: bool = True
    ) -> Author:
        """
        Update an author.
        
        Parameters:
        -----------
        author_id : int
            Author ID
        author_data : AuthorUpdate
            Author update data
        refresh_popularity : bool
            Whether to refresh popularity score
        
        Returns:
        --------
        Author: Updated author
        
        Raises:
        -------
        ValueError: If author not found or update data is invalid
        """
        author = self.author_repo.get_by_id(author_id)
        if not author:
            raise ValueError(f"Author with ID {author_id} not found")
        
        # Update fields
        update_data = author_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(author, field) and value is not None:
                setattr(author, field, value)
        
        # Save updates
        updated = self.author_repo.update(author)
        
        # Refresh popularity if needed
        if refresh_popularity:
            updated = self.author_repo.refresh_popularity(updated)
        
        logger.info(f"Updated author: {updated.name} (ID: {updated.id})")
        return updated
    
    def delete_author(
        self,
        author_id: int,
        hard_delete: bool = False
    ) -> bool:
        """
        Delete an author.
        
        Parameters:
        -----------
        author_id : int
            Author ID
        hard_delete : bool
            If True, permanently delete
            If False, soft delete (deactivate)
        
        Returns:
        --------
        bool: True if deleted, False if not found
        """
        return self.author_repo.delete(author_id, hard_delete)
    
    # ============================================================
    # Listing and Search Operations
    # ============================================================
    
    def list_authors(
        self,
        skip: int = 0,
        limit: int = 50,
        include_inactive: bool = False,
        order_by: str = "name",
        order_direction: str = "asc"
    ) -> AuthorListResponse:
        """
        List authors with pagination.
        
        Parameters:
        -----------
        skip : int
            Number of records to skip
        limit : int
            Maximum number of records to return
        include_inactive : bool
            Whether to include inactive authors
        order_by : str
            Field to order by
        order_direction : str
            Sort direction
        
        Returns:
        --------
        AuthorListResponse: Paginated author list
        """
        authors = self.author_repo.list(
            skip=skip,
            limit=limit,
            include_inactive=include_inactive,
            order_by=order_by,
            order_direction=order_direction
        )
        
        total = self.author_repo.count(include_inactive=include_inactive)
        
        return AuthorListResponse(
            items=authors,
            total=total,
            skip=skip,
            limit=limit
        )
    
    def search_authors(
        self,
        query: str,
        limit: int = 20,
        include_inactive: bool = False,
        min_popularity: Optional[float] = None
    ) -> List[Author]:
        """
        Search authors by name.
        
        Parameters:
        -----------
        query : str
            Search query
        limit : int
            Maximum number of results
        include_inactive : bool
            Whether to include inactive authors
        min_popularity : Optional[float]
            Minimum popularity score filter
        
        Returns:
        --------
        List[Author]: List of matching authors
        """
        return self.author_repo.search(
            query=query,
            limit=limit,
            include_inactive=include_inactive,
            min_popularity=min_popularity
        )
    
    def autocomplete_authors(
        self,
        prefix: str,
        limit: int = 10,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Autocomplete author names.
        
        Parameters:
        -----------
        prefix : str
            Name prefix
        limit : int
            Maximum number of results
        include_inactive : bool
            Whether to include inactive authors
        
        Returns:
        --------
        List[Dict[str, Any]]: List of author suggestions
        """
        authors = self.author_repo.autocomplete(
            prefix=prefix,
            limit=limit,
            include_inactive=include_inactive
        )
        
        return [
            {
                "id": author.id,
                "name": author.name,
                "popularity_score": author.popularity_score,
                "total_books": author.total_books,
            }
            for author in authors
        ]
    
    # ============================================================
    # Specialized Queries
    # ============================================================
    
    def get_popular_authors(
        self,
        limit: int = 50,
        min_popularity: Optional[float] = None
    ) -> List[Author]:
        """
        Get most popular authors.
        
        Parameters:
        -----------
        limit : int
            Maximum number of results
        min_popularity : Optional[float]
            Minimum popularity score filter
        
        Returns:
        --------
        List[Author]: List of popular authors
        """
        return self.author_repo.get_popular(limit, min_popularity)
    
    def get_top_rated_authors(
        self,
        limit: int = 50,
        min_rating: Optional[float] = None
    ) -> List[Author]:
        """
        Get highest rated authors.
        
        Parameters:
        -----------
        limit : int
            Maximum number of results
        min_rating : Optional[float]
            Minimum rating filter
        
        Returns:
        --------
        List[Author]: List of top rated authors
        """
        return self.author_repo.get_top_rated(limit, min_rating)
    
    def get_most_prolific_authors(
        self,
        limit: int = 50,
        min_books: Optional[int] = None
    ) -> List[Author]:
        """
        Get most prolific authors (most books).
        
        Parameters:
        -----------
        limit : int
            Maximum number of results
        min_books : Optional[int]
            Minimum book count filter
        
        Returns:
        --------
        List[Author]: List of prolific authors
        """
        return self.author_repo.get_most_prolific(limit, min_books)
    
    def get_featured_authors(
        self,
        limit: int = 10,
        min_popularity: float = 0.5
    ) -> List[Author]:
        """
        Get featured authors.
        
        Parameters:
        -----------
        limit : int
            Maximum number of results
        min_popularity : float
            Minimum popularity score
        
        Returns:
        --------
        List[Author]: List of featured authors
        """
        return self.author_repo.get_featured(limit, min_popularity)
    
    def get_trending_authors(
        self,
        limit: int = 10,
        days: int = 30
    ) -> List[Author]:
        """
        Get trending authors.
        
        Parameters:
        -----------
        limit : int
            Maximum number of results
        days : int
            Number of days to consider
        
        Returns:
        --------
        List[Author]: List of trending authors
        """
        return self.author_repo.get_trending(limit, days)
    
    def get_random_authors(
        self,
        limit: int = 20,
        include_inactive: bool = False,
        seed: Optional[int] = None
    ) -> List[Author]:
        """
        Get random authors.
        
        Parameters:
        -----------
        limit : int
            Maximum number of results
        include_inactive : bool
            Whether to include inactive authors
        seed : Optional[int]
            Random seed for reproducibility
        
        Returns:
        --------
        List[Author]: List of random authors
        """
        return self.author_repo.get_random(limit, include_inactive, seed)
    
    def get_recommendation_candidates(
        self,
        limit: int = 200,
        user_id: Optional[int] = None,
        min_popularity: float = 0.3
    ) -> List[Author]:
        """
        Get authors suitable for recommendations.
        
        Parameters:
        -----------
        limit : int
            Maximum number of results
        user_id : Optional[int]
            User ID to exclude already followed authors
        min_popularity : float
            Minimum popularity score
        
        Returns:
        --------
        List[Author]: List of recommendation candidates
        """
        exclude_ids = []
        
        if user_id:
            # Get authors the user already follows
            followed = self.follow_repo.get_followed_authors(user_id)
            exclude_ids = [author.id for author in followed]
        
        return self.author_repo.get_recommendation_candidates(
            limit=limit,
            exclude_ids=exclude_ids if exclude_ids else None,
            min_popularity=min_popularity
        )
    
    # ============================================================
    # Follow Operations
    # ============================================================
    
    def follow_author(
        self,
        user_id: int,
        author_id: int,
        notification_preference: Optional[str] = None,
        follow_source: str = "manual",
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Author:
        """
        Follow an author.
        
        Parameters:
        -----------
        user_id : int
            User ID
        author_id : int
            Author ID
        notification_preference : Optional[str]
            Notification preference
        follow_source : str
            Source of the follow
        notes : Optional[str]
            User notes
        metadata : Optional[Dict[str, Any]]
            Additional metadata
        
        Returns:
        --------
        Author: The author that was followed
        
        Raises:
        -------
        ValueError: If author not found
        """
        # Verify author exists
        authors = self.author_repo.get_by_ids([author_id])
        if not authors:
            raise ValueError(f"Author with ID {author_id} not found")
        
        author = authors[0]
        
        # Create follow relationship
        self.follow_repo.follow_author(
            user_id=user_id,
            author_id=author_id,
            author_name=author.name,
            notification_preference=notification_preference,
            follow_source=follow_source,
            notes=notes,
            metadata=metadata
        )
        
        logger.info(f"User {user_id} followed author {author.name} (ID: {author_id})")
        return author
    
    def unfollow_author(
        self,
        user_id: int,
        author_id: int,
        hard_delete: bool = True
    ) -> bool:
        """
        Unfollow an author.
        
        Parameters:
        -----------
        user_id : int
            User ID
        author_id : int
            Author ID
        hard_delete : bool
            If True, permanently delete
            If False, soft delete
        
        Returns:
        --------
        bool: True if unfollowed, False if not found
        """
        try:
            # Get the follow relationship directly from the repository
            follow = self.follow_repo.get_follow(user_id, author_id)
            
            if not follow:
                logger.warning(f"Follow not found for user {user_id}, author {author_id}")
                return False
            
            if hard_delete:
                self.db.delete(follow)
                logger.info(f"User {user_id} unfollowed author {author_id}")
            else:
                # Use direct attribute access instead of property
                follow.is_active = False
                follow.unfollowed_at = datetime.now()
                logger.info(f"User {user_id} soft unfollowed author {author_id}")
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to unfollow author {author_id} for user {user_id}: {e}")
            raise
    
    def get_followed_authors(
        self,
        user_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Author]:
        """
        Get authors followed by a user.
        
        Parameters:
        -----------
        user_id : int
            User ID
        limit : Optional[int]
            Maximum number of results
        offset : Optional[int]
            Number of records to skip
        
        Returns:
        --------
        List[Author]: List of followed authors
        """
        return self.follow_repo.get_followed_authors(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
    
    def get_followed_authors_with_details(
        self,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get followed authors with follow details.
        
        Parameters:
        -----------
        user_id : int
            User ID
        
        Returns:
        --------
        List[Dict[str, Any]]: List of authors with follow details
        """
        return self.follow_repo.get_followed_authors_with_details(user_id)
    
    def is_following(
        self,
        user_id: int,
        author_id: int
    ) -> bool:
        """
        Check if a user is following an author.
        
        Parameters:
        -----------
        user_id : int
            User ID
        author_id : int
            Author ID
        
        Returns:
        --------
        bool: True if following
        """
        return self.follow_repo.is_following(user_id, author_id)
    
    def count_followers(
        self,
        author_id: int
    ) -> int:
        """
        Count followers of an author.
        
        Parameters:
        -----------
        author_id : int
            Author ID
        
        Returns:
        --------
        int: Number of followers
        """
        return self.follow_repo.count_followers(author_id)
    
    # ============================================================
    # Popularity Management
    # ============================================================
    
    def refresh_popularity(
        self,
        author_id: int
    ) -> Author:
        """
        Refresh an author's popularity score.
        
        Parameters:
        -----------
        author_id : int
            Author ID
        
        Returns:
        --------
        Author: Updated author
        
        Raises:
        -------
        ValueError: If author not found
        """
        author = self.author_repo.get_by_id(author_id)
        if not author:
            raise ValueError(f"Author with ID {author_id} not found")
        
        return self.author_repo.refresh_popularity(author)
    
    def refresh_all_popularity(
        self,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Refresh popularity scores for all authors.
        
        Parameters:
        -----------
        batch_size : int
            Number of authors to process per batch
        
        Returns:
        --------
        Dict[str, Any]: Result statistics
        """
        offset = 0
        updated = 0
        errors = 0
        
        while True:
            authors = self.author_repo.list(
                skip=offset,
                limit=batch_size,
                include_inactive=True
            )
            
            if not authors:
                break
            
            for author in authors:
                try:
                    self.author_repo.refresh_popularity(author)
                    updated += 1
                except Exception:
                    errors += 1
            
            offset += batch_size
            logger.info(f"Refreshed popularity for {updated} authors, {errors} errors")
        
        return {
            "total_updated": updated,
            "total_errors": errors,
            "timestamp": datetime.now().isoformat()
        }
    
    # ============================================================
    # Statistics and Analytics
    # ============================================================
    
    def get_author_stats(
        self,
        author_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get author statistics.
        
        Parameters:
        -----------
        author_id : Optional[int]
            Author ID (if None, returns global stats)
        
        Returns:
        --------
        Dict[str, Any]: Statistics dictionary
        """
        if author_id:
            # Get stats for a specific author
            author = self.author_repo.get_by_id(author_id)
            if not author:
                return {}
            
            return {
                "author_id": author.id,
                "name": author.name,
                "total_books": author.total_books,
                "average_rating": author.average_rating,
                "popularity_score": author.popularity_score,
                "followers_count": self.count_followers(author_id),
                "rating_status": author.rating_status,
                "is_active": author.is_active,
            }
        
        # Get global stats
        repo_stats = self.author_repo.get_stats()
        distribution = self.author_repo.get_popularity_distribution()
        
        return {
            **repo_stats,
            "popularity_distribution": distribution,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_follow_stats(
        self,
        author_id: int
    ) -> Dict[str, Any]:
        """
        Get follow statistics for an author.
        
        Parameters:
        -----------
        author_id : int
            Author ID
        
        Returns:
        --------
        Dict[str, Any]: Follow statistics
        """
        return self.follow_repo.get_stats(author_id)
    
    # ============================================================
    # Bulk Operations
    # ============================================================
    
    def bulk_follow_authors(
        self,
        user_id: int,
        author_ids: List[int],
        follow_source: str = "bulk"
    ) -> Dict[str, Any]:
        """
        Follow multiple authors at once.
        
        Parameters:
        -----------
        user_id : int
            User ID
        author_ids : List[int]
            List of author IDs to follow
        follow_source : str
            Source of the follows
        
        Returns:
        --------
        Dict[str, Any]: Result statistics
        """
        successful, failed = self.follow_repo.bulk_follow(
            user_id=user_id,
            author_ids=author_ids,
            follow_source=follow_source
        )
        
        return {
            "successful": successful,
            "failed": failed,
            "total": len(author_ids),
            "timestamp": datetime.now().isoformat()
        }
    
    def bulk_unfollow_authors(
        self,
        user_id: int,
        author_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Unfollow multiple authors at once.
        
        Parameters:
        -----------
        user_id : int
            User ID
        author_ids : List[int]
            List of author IDs to unfollow
        
        Returns:
        --------
        Dict[str, Any]: Result statistics
        """
        successful, failed = self.follow_repo.bulk_unfollow(
            user_id=user_id,
            author_ids=author_ids
        )
        
        return {
            "successful": successful,
            "failed": failed,
            "total": len(author_ids),
            "timestamp": datetime.now().isoformat()
        }
    
    def bulk_create_authors(
        self,
        authors_data: List[AuthorCreate]
    ) -> List[Author]:
        """
        Bulk create authors.
        
        Parameters:
        -----------
        authors_data : List[AuthorCreate]
            List of author creation data
        
        Returns:
        --------
        List[Author]: Created authors
        """
        authors = []
        
        for data in authors_data:
            try:
                author = self.create_author(data, refresh_popularity=False)
                authors.append(author)
            except Exception as e:
                logger.error(f"Failed to create author '{data.name}': {e}")
        
        logger.info(f"Bulk created {len(authors)} authors")
        return authors
    
    # ============================================================
    # Validation and Helpers
    # ============================================================
    
    def validate_author_exists(
        self,
        author_id: int
    ) -> bool:
        """
        Validate that an author exists.
        
        Parameters:
        -----------
        author_id : int
            Author ID
        
        Returns:
        --------
        bool: True if author exists
        """
        return self.author_repo.exists(author_id)
    
    def validate_author_name_available(
        self,
        name: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Validate that an author name is available.
        
        Parameters:
        -----------
        name : str
            Author name
        exclude_id : Optional[int]
            Author ID to exclude (for updates)
        
        Returns:
        --------
        bool: True if name is available
        """
        return not self.author_repo.exists_by_name(name, exclude_id)
    
    def get_author_suggestions(
        self,
        prefix: str,
        limit: int = 10,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get author suggestions with follow status.
        
        Parameters:
        -----------
        prefix : str
            Name prefix
        limit : int
            Maximum number of results
        user_id : Optional[int]
            User ID to check follow status
        
        Returns:
        --------
        List[Dict[str, Any]]: Author suggestions with follow status
        """
        authors = self.autocomplete_authors(prefix, limit)
        
        if not user_id:
            return authors
        
        # Add follow status
        for author in authors:
            author["is_following"] = self.is_following(user_id, author["id"])
        
        return authors
    
    def get_author_with_follow_status(
        self,
        author_id: int,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get an author with follow status for a user.
        
        Parameters:
        -----------
        author_id : int
            Author ID
        user_id : Optional[int]
            User ID to check follow status
        
        Returns:
        --------
        Dict[str, Any]: Author data with follow status
        """
        author = self.get_author(author_id)
        if not author:
            return {}
        
        result = author.to_dict()
        
        if user_id:
            result["is_following"] = self.is_following(user_id, author_id)
            result["followers_count"] = self.count_followers(author_id)
        
        return result
    
    def get_author_recommendations(
        self,
        user_id: int,
        limit: int = 20,
        min_popularity: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Get personalized author recommendations for a user.
        
        Parameters:
        -----------
        user_id : int
            User ID
        limit : int
            Maximum number of recommendations
        min_popularity : float
            Minimum popularity score
        
        Returns:
        --------
        List[Dict[str, Any]]: List of recommended authors with follow status
        """
        # Get recommendation candidates
        candidates = self.get_recommendation_candidates(
            limit=limit,
            user_id=user_id,
            min_popularity=min_popularity
        )
        
        # Format response with follow status
        result = []
        for author in candidates:
            author_data = author.to_dict()
            author_data["is_following"] = False  # Already excluded followed authors
            author_data["followers_count"] = self.count_followers(author.id)
            result.append(author_data)
        
        return result


def update_notification_preference(
    self,
    user_id: str,
    author_id: int,
    preference,
) -> UserFollowedAuthor | None:

    follow = self.get_follow(user_id, author_id)

    if follow is None:
        return None

    follow.notification_preference = preference

    self.db.commit()
    self.db.refresh(follow)

    return follow