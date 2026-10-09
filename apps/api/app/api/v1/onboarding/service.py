"""
Onboarding Service

Handles user onboarding operations including author discovery,
search, and following authors.

Phase: Services
"""

from math import ceil
from typing import Optional, List, Dict, Any, Set
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime

from app.models.author import Author
from app.models.user_followed_author import UserFollowedAuthor
from app.models.user_profile import UserProfile
from app.models.user_preference import UserPreference
from app.models.user_favorite_book import UserFavoriteBook

logger = logging.getLogger(__name__)


class OnboardingService:
    """
    Service for managing user onboarding and author interactions.
    
    Features:
    - Paginated author listing with search
    - Author search with autocomplete support
    - Follow/unfollow authors
    - Get followed authors
    """
    
    def __init__(self, db: Session):
        """
        Initialize the onboarding service.
        
        Parameters:
        -----------
        db : Session
            SQLAlchemy database session
        """
        self.db = db
    
    def get_authors(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        order_by: str = "name",
        order_direction: str = "asc"
    ) -> Dict[str, Any]:
        """
        Get paginated list of authors with optional search.
        
        Parameters:
        -----------
        page : int
            Page number (1-indexed)
        limit : int
            Number of items per page (max 100)
        search : Optional[str]
            Search term for author name
        order_by : str
            Field to order by (name, popularity_score, total_books)
        order_direction : str
            Sort direction (asc, desc)
        
        Returns:
        --------
        Dict[str, Any]: Paginated author list with metadata
        
        Raises:
        -------
        ValueError: If page < 1 or limit is out of range
        """
        # Validate inputs
        if page < 1:
            raise ValueError("Page must be >= 1")
        if limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        try:
            # Build query
            query = self.db.query(Author)
            
            # Apply search filter
            if search and search.strip():
                search_term = f"%{search.strip()}%"
                query = query.filter(Author.name.ilike(search_term))
            
            # Get total count
            total = query.count()
            
            # Calculate pagination metadata
            total_pages = ceil(total / limit) if total > 0 else 0
            offset = (page - 1) * limit
            
            # Apply ordering
            order_column = getattr(Author, order_by, Author.name)
            if order_direction.lower() == "desc":
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
            
            # Execute query with pagination
            authors = query.offset(offset).limit(limit).all()
            
            return {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
                "items": [author.to_dict() for author in authors],
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_authors: {e}")
            raise
    
    def search_authors(
        self,
        query: str,
        limit: int = 20,
        include_metadata: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search authors by name with autocomplete support.
        
        Parameters:
        -----------
        query : str
            Search query string
        limit : int
            Maximum number of results (max 50)
        include_metadata : bool
            Whether to include full author metadata
        
        Returns:
        --------
        List[Dict[str, Any]]: List of matching authors
        """
        # Validate inputs
        if limit < 1 or limit > 50:
            raise ValueError("Limit must be between 1 and 50")
        
        if not query or not query.strip():
            return []
        
        try:
            search_term = f"%{query.strip()}%"
            
            authors = (
                self.db.query(Author)
                .filter(Author.name.ilike(search_term))
                .order_by(Author.popularity_score.desc(), Author.name)
                .limit(limit)
                .all()
            )
            
            if include_metadata:
                return [author.to_dict() for author in authors]
            else:
                return [
                    {
                        "id": author.id,
                        "name": author.name,
                        "total_books": author.total_books,
                        "popularity_score": author.popularity_score,
                    }
                    for author in authors
                ]
                
        except SQLAlchemyError as e:
            logger.error(f"Database error in search_authors: {e}")
            raise
    
    def follow_authors(
        self,
        user_id: int,
        author_ids: List[int],
    ) -> Dict[str, Any]:
        """
        Follow multiple authors for a user.
        
        Parameters:
        -----------
        user_id : int
            ID of the user
        author_ids : List[int]
            List of author IDs to follow
        
        Returns:
        --------
        Dict[str, Any]: Result with follow statistics
        """
        # Validate inputs
        if not author_ids:
            return {"success": True, "followed": 0, "message": "No authors to follow"}
        
        if not all(isinstance(aid, int) and aid > 0 for aid in author_ids):
            raise ValueError("Invalid author IDs provided")
        
        try:
            # Get existing follows to avoid duplicates
            existing = (
                self.db.query(UserFollowedAuthor.author_id)
                .filter(UserFollowedAuthor.user_id == user_id)
                .all()
            )
            existing_ids = {row.author_id for row in existing}
            
            # Find new authors to follow
            new_author_ids = [
                aid for aid in author_ids 
                if aid not in existing_ids
            ]
            
            if not new_author_ids:
                return {
                    "success": True,
                    "followed": 0,
                    "message": "All authors already followed"
                }
            
            # Create follow records
            new_follows = [
                UserFollowedAuthor(
                    user_id=user_id,
                    author_id=author_id,
                )
                for author_id in new_author_ids
            ]
            
            # Batch insert
            self.db.add_all(new_follows)
            self.db.commit()
            
            logger.info(f"User {user_id} followed {len(new_follows)} new authors")
            
            return {
                "success": True,
                "followed": len(new_follows),
                "already_followed": len(author_ids) - len(new_follows),
                "total_following": len(existing_ids) + len(new_follows),
            }
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error in follow_authors: {e}")
            raise
    
    def unfollow_author(
        self,
        user_id: int,
        author_id: int,
    ) -> Dict[str, Any]:
        """
        Unfollow a single author for a user.
        
        Parameters:
        -----------
        user_id : int
            ID of the user
        author_id : int
            ID of the author to unfollow
        
        Returns:
        --------
        Dict[str, Any]: Result with unfollow status
        """
        try:
            # Find the follow relationship
            follow = (
                self.db.query(UserFollowedAuthor)
                .filter(
                    UserFollowedAuthor.user_id == user_id,
                    UserFollowedAuthor.author_id == author_id,
                )
                .first()
            )
            
            if not follow:
                return {
                    "success": False,
                    "message": "Author not followed by this user"
                }
            
            # Delete the follow relationship
            self.db.delete(follow)
            self.db.commit()
            
            logger.info(f"User {user_id} unfollowed author {author_id}")
            
            return {
                "success": True,
                "message": "Author unfollowed successfully"
            }
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error in unfollow_author: {e}")
            raise
    
    def get_followed_authors(
        self,
        user_id: int,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Get paginated list of authors followed by a user.
        
        Parameters:
        -----------
        user_id : int
            ID of the user
        page : int
            Page number
        limit : int
            Items per page
        
        Returns:
        --------
        Dict[str, Any]: Paginated list of followed authors
        """
        if page < 1:
            raise ValueError("Page must be >= 1")
        if limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        try:
            # Query followed authors
            query = (
                self.db.query(Author)
                .join(UserFollowedAuthor, UserFollowedAuthor.author_id == Author.id)
                .filter(UserFollowedAuthor.user_id == user_id)
                .order_by(Author.name)
            )
            
            total = query.count()
            total_pages = ceil(total / limit) if total > 0 else 0
            offset = (page - 1) * limit
            
            authors = query.offset(offset).limit(limit).all()
            
            return {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "items": [author.to_dict() for author in authors],
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_followed_authors: {e}")
            raise
    
    def is_following_author(
        self,
        user_id: int,
        author_id: int,
    ) -> bool:
        """
        Check if a user is following a specific author.
        
        Parameters:
        -----------
        user_id : int
            ID of the user
        author_id : int
            ID of the author
        
        Returns:
        --------
        bool: True if following, False otherwise
        """
        try:
            result = (
                self.db.query(UserFollowedAuthor)
                .filter(
                    UserFollowedAuthor.user_id == user_id,
                    UserFollowedAuthor.author_id == author_id,
                )
                .first()
            )
            return result is not None
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in is_following_author: {e}")
            return False
    
    def get_author_recommendations(
        self,
        user_id: int,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get author recommendations for a user based on their follows.
        
        Parameters:
        -----------
        user_id : int
            ID of the user
        limit : int
            Maximum number of recommendations
        
        Returns:
        --------
        List[Dict[str, Any]]: List of recommended authors
        """
        if limit < 1 or limit > 50:
            raise ValueError("Limit must be between 1 and 50")
        
        try:
            # Get authors the user already follows
            followed_ids = (
                self.db.query(UserFollowedAuthor.author_id)
                .filter(UserFollowedAuthor.user_id == user_id)
                .subquery()
            )
            
            # Recommend popular authors the user doesn't follow
            recommended = (
                self.db.query(Author)
                .filter(Author.id.notin_(followed_ids))
                .order_by(
                    Author.popularity_score.desc(),
                    Author.total_books.desc()
                )
                .limit(limit)
                .all()
            )
            
            return [author.to_dict() for author in recommended]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_author_recommendations: {e}")
            raise

    def complete_onboarding(
        self,
        user_id: str,
        request,
    ):
        """
        Save all onboarding selections and mark onboarding complete.
        """

        profile = (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )

        if profile is None:
            profile = UserProfile.create(user_id=user_id)
            self.db.add(profile)

        # Save profile preferences
        profile.set_favorite_genres(request.preferred_genres)
        profile.set_favorite_authors(request.favorite_authors)

        # Replace previous favorite books
        (
            self.db.query(UserFavoriteBook)
            .filter(UserFavoriteBook.user_id == user_id)
            .delete()
        )

        for isbn in request.favorite_books:
            self.db.add(
                UserFavoriteBook(
                    user_id=user_id,
                    isbn=isbn,
                )
            )

        profile.preferred_language = (
            request.preferred_language.value
            if hasattr(request.preferred_language, "value")
            else request.preferred_language or "en"
        )

        profile.reading_style = (
            request.reading_style.value
            if hasattr(request.reading_style, "value")
            else request.reading_style or "balanced"
        )

        profile.reading_goals = (
            request.reading_goal.value
            if hasattr(request.reading_goal, "value")
            else request.reading_goal or "moderate"
        )

        # FIX: Use the model method to complete onboarding
        # profile.onboarding_completed = True
        # self.db.commit()
        
        # Use the model method
        profile.complete_onboarding()

        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)

        logger.info(
            f"After commit -> onboarding_completed={profile.onboarding_completed}"
        )

        return {
            "success": True
        }

    def save_progress(
        self,
        user_id: str,
        request,
    ):
        """
        Save onboarding progress without marking it complete.
        """

        profile = (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )

        if profile is None:
            profile = UserProfile.create(user_id=user_id)
            self.db.add(profile)

        profile.set_favorite_genres(request.preferred_genres)
        profile.set_favorite_authors(request.favorite_authors)

        # Replace previous favorite books
        (
            self.db.query(UserFavoriteBook)
            .filter(UserFavoriteBook.user_id == user_id)
            .delete()
        )

        for isbn in request.favorite_books:
            self.db.add(
                UserFavoriteBook(
                    user_id=user_id,
                    isbn=isbn,
                )
            )

        profile.preferred_language = (
            request.preferred_language.value
            if request.preferred_language
            else "en"
        )

        profile.reading_style = (
            request.reading_style.value
            if request.reading_style
            else "balanced"
        )

        profile.reading_goals = (
            request.reading_goal.value
            if request.reading_goal
            else "moderate"
        )

        self.db.commit()

    def get_completed_steps(self, user_id: str):

        profile = (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )

        if profile is None:
            return []

        steps = ["welcome"]

        if profile.get_favorite_genres():
            steps.append("genres")

        if profile.get_favorite_authors():
            steps.append("authors")

        favorite_books = (
            self.db.query(UserFavoriteBook)
            .filter(UserFavoriteBook.user_id == user_id)
            .count()
        )

        if favorite_books > 0:
            steps.append("books")

        if profile.reading_goals:
            steps.append("reading_goal")

        if profile.onboarding_completed:
            steps.append("complete")

        return steps

    def get_status(self, user_id: str):

        profile = (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )

        if profile is None:
            return None

        # FIX: If onboarding is complete, return complete status immediately
        if profile.onboarding_completed:
            return {
                "current_step": "complete",
                "completed_steps": [
                    "welcome",
                    "genres",
                    "authors",
                    "books",
                    "reading_goal",
                    "complete",
                ],
                "total_steps": 6,
            }

        completed = self.get_completed_steps(user_id)

        all_steps = [
            "welcome",
            "genres",
            "authors",
            "books",
            "reading_goal",
            "complete",
        ]

        current_step = "welcome"

        for step in all_steps:
            if step not in completed:
                current_step = step
                break

        return {
            "current_step": current_step,
            "completed_steps": completed,
            "total_steps": len(all_steps),
        }

    def skip(self, user_id: str):

        profile = (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )

        if profile is None:
            profile = UserProfile.create(user_id=user_id)
            self.db.add(profile)

        profile.onboarding_completed = True

        self.db.commit()

        return {
            "skipped_at": datetime.utcnow().isoformat()
        }

    def get_preferences(self, user_id: str):

        profile = (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )

        if profile is None:
            return None

        favorite_books = (
            self.db.query(UserFavoriteBook)
            .filter(UserFavoriteBook.user_id == user_id)
            .all()
        )

        favorite_book_isbns = [
            book.isbn
            for book in favorite_books
        ]

        return {
            "preferred_genres": profile.get_favorite_genres(),
            "favorite_authors": profile.get_favorite_authors(),
            "favorite_books": favorite_book_isbns,
            "reading_goal": profile.reading_goals,
            "reading_style": profile.reading_style,
            "preferred_language": profile.preferred_language,
            "theme": "dark",
        }

    def reset(self, user_id: str):

        profile = (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )

        if profile is None:
            return

        profile.set_favorite_genres([])
        profile.set_favorite_authors([])

        profile.reading_goals = None
        profile.reading_style = "balanced"
        profile.onboarding_completed = False

        self.db.commit()