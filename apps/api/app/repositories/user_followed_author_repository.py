from __future__ import annotations

"""
User Followed Author Repository

Repository for managing user-author follow relationships.
Handles following, unfollowing, and querying followed authors.

Phase: Data Access Layer
"""

from datetime import timedelta
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import logging
from sqlalchemy import func, select, and_, desc, asc
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.models.author import Author
from app.models.user_followed_author import UserFollowedAuthor

logger = logging.getLogger(__name__)


class UserFollowedAuthorRepository:
    """
    Repository for managing user-author follow relationships.
    
    Handles:
    - Follow/unfollow authors
    - Query followed authors
    - Follower counts
    - Notification preferences
    - Bulk operations
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
    # CRUD Operations
    # ============================================================
    
    def get_follow(
        self,
        user_id: int,
        author_id: int,
        include_inactive: bool = False
    ) -> Optional[UserFollowedAuthor]:
        """
        Get a specific follow relationship.
        
        Parameters:
        -----------
        user_id : int
            User ID
        author_id : int
            Author ID
        include_inactive : bool
            Whether to include inactive follows
        
        Returns:
        --------
        Optional[UserFollowedAuthor]: Follow relationship or None
        """
        try:
            stmt = select(UserFollowedAuthor).where(
                UserFollowedAuthor.user_id == user_id,
                UserFollowedAuthor.author_id == author_id,
            )
            
            if not include_inactive:
                stmt = stmt.where(UserFollowedAuthor.is_active.is_(True))
            
            return self.db.scalar(stmt)
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get follow for user {user_id}, author {author_id}: {e}")
            return None
    
    def get_follow_with_author(
        self,
        user_id: int,
        author_id: int
    ) -> Optional[UserFollowedAuthor]:
        """
        Get a follow relationship with author data loaded.
        
        Parameters:
        -----------
        user_id : int
            User ID
        author_id : int
            Author ID
        
        Returns:
        --------
        Optional[UserFollowedAuthor]: Follow relationship with author
        """
        try:
            stmt = (
                select(UserFollowedAuthor)
                .where(
                    UserFollowedAuthor.user_id == user_id,
                    UserFollowedAuthor.author_id == author_id,
                )
                .options(selectinload(UserFollowedAuthor.author))
            )
            return self.db.scalar(stmt)
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get follow with author for user {user_id}, author {author_id}: {e}")
            return None
    
    def follow_author(
        self,
        user_id: int,
        author_id: int,
        author_name: Optional[str] = None,
        notification_preference: Optional[str] = None,
        follow_source: Optional[str] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        allow_duplicate: bool = False
    ) -> UserFollowedAuthor:
        """
        Follow an author.
        
        Parameters:
        -----------
        user_id : int
            User ID
        author_id : int
            Author ID
        author_name : Optional[str]
            Author name (for denormalization)
        notification_preference : Optional[str]
            Notification preference (email, push, none)
        follow_source : Optional[str]
            Source of the follow (onboarding, search, recommendation)
        notes : Optional[str]
            User notes about the author
        metadata : Optional[Dict[str, Any]]
            Additional metadata
        allow_duplicate : bool
            Whether to allow duplicate follows
        
        Returns:
        --------
        UserFollowedAuthor: Created follow relationship
        
        Raises:
        -------
        ValueError: If user_id or author_id is invalid
        SQLAlchemyError: If database operation fails
        """
        if not user_id or user_id <= 0:
            raise ValueError("Invalid user_id")
        if not author_id or author_id <= 0:
            raise ValueError("Invalid author_id")
        
        try:
            # Check if already following
            existing = self.get_follow(user_id, author_id)
            
            if existing:
                if allow_duplicate:
                    # Create a new follow (if duplicates are allowed)
                    pass
                else:
                    logger.debug(f"User {user_id} already follows author {author_id}")
                    return existing
            
            # Create follow relationship
            follow = UserFollowedAuthor(
                user_id=user_id,
                author_id=author_id,
                author_name=author_name,
                notification_preference=notification_preference or "email",
                follow_source=follow_source or "manual",
                notes=notes,
                metadata=metadata or {},
                is_active=True,
            )
            
            self.db.add(follow)
            self.db.commit()
            self.db.refresh(follow)
            
            logger.info(f"User {user_id} followed author {author_id}")
            return follow
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to follow author {author_id} for user {user_id}: {e}")
            raise
    
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
            If False, soft delete (mark as inactive)
        
        Returns:
        --------
        bool: True if unfollowed, False if not found
        """
        follow = self.get_follow(user_id, author_id)
        
        if not follow:
            logger.warning(f"Follow not found for user {user_id}, author {author_id}")
            return False
        
        try:
            if hard_delete:
                self.db.delete(follow)
                logger.info(f"User {user_id} unfollowed author {author_id}")
            else:
                follow.is_active = False
                follow.unfollowed_at = datetime.now()
                logger.info(f"User {user_id} soft unfollowed author {author_id}")
            
            self.db.commit()
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to unfollow author {author_id} for user {user_id}: {e}")
            raise
    
    def update_follow(
        self,
        user_id: int,
        author_id: int,
        **kwargs
    ) -> Optional[UserFollowedAuthor]:
        """
        Update a follow relationship.
        
        Parameters:
        -----------
        user_id : int
            User ID
        author_id : int
            Author ID
        **kwargs : dict
            Fields to update
        
        Returns:
        --------
        Optional[UserFollowedAuthor]: Updated follow or None
        """
        follow = self.get_follow(user_id, author_id)
        
        if not follow:
            logger.warning(f"Follow not found for user {user_id}, author {author_id}")
            return None
        
        try:
            # Update allowed fields
            allowed_fields = [
                'notification_preference', 'notes', 'metadata', 'follow_source'
            ]
            
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(follow, field):
                    setattr(follow, field, value)
            
            follow.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(follow)
            
            logger.debug(f"Updated follow for user {user_id}, author {author_id}")
            return follow
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to update follow for user {user_id}, author {author_id}: {e}")
            raise
    
    # ============================================================
    # Query Operations
    # ============================================================
    
    def get_followed_authors(
        self,
        user_id: int,
        include_inactive: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: str = "followed_at",
        order_direction: str = "desc"
    ) -> List[Author]:
        """
        Get all authors followed by a user.
        
        Parameters:
        -----------
        user_id : int
            User ID
        include_inactive : bool
            Whether to include inactive follows
        limit : Optional[int]
            Maximum number of results
        offset : Optional[int]
            Number of records to skip
        order_by : str
            Field to order by (followed_at, author_name, popularity_score)
        order_direction : str
            Sort direction (asc, desc)
        
        Returns:
        --------
        List[Author]: List of followed authors
        """
        try:
            query = (
                self.db.query(Author)
                .join(
                    UserFollowedAuthor,
                    UserFollowedAuthor.author_id == Author.id
                )
                .filter(UserFollowedAuthor.user_id == user_id)
            )
            
            if not include_inactive:
                query = query.filter(
                    UserFollowedAuthor.is_active.is_(True),
                    Author.is_active.is_(True)
                )
            
            # Apply ordering
            if order_by == "followed_at":
                order_col = UserFollowedAuthor.followed_at
            elif order_by == "author_name":
                order_col = Author.name
            else:
                order_col = getattr(Author, order_by, Author.popularity_score)
            
            if order_direction.lower() == "desc":
                query = query.order_by(desc(order_col))
            else:
                query = query.order_by(asc(order_col))
            
            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)
            
            return query.all()
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get followed authors for user {user_id}: {e}")
            return []
    
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
        try:
            follows = (
                self.db.query(UserFollowedAuthor)
                .filter(
                    UserFollowedAuthor.user_id == user_id,
                    UserFollowedAuthor.is_active.is_(True)
                )
                .options(selectinload(UserFollowedAuthor.author))
                .order_by(desc(UserFollowedAuthor.followed_at))
                .all()
            )
            
            result = []
            for follow in follows:
                if follow.author and follow.author.is_active:
                    result.append({
                        "author": follow.author.to_dict(),
                        "followed_at": follow.followed_at,
                        "notification_preference": follow.notification_preference,
                        "follow_source": follow.follow_source,
                        "notes": follow.notes,
                    })
            
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get followed authors with details for user {user_id}: {e}")
            return []
    
    def get_follow_relationships(
        self,
        user_id: int,
        include_inactive: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[UserFollowedAuthor]:
        """
        Get follow relationships for a user.
        
        Parameters:
        -----------
        user_id : int
            User ID
        include_inactive : bool
            Whether to include inactive follows
        limit : Optional[int]
            Maximum number of results
        offset : Optional[int]
            Number of records to skip
        
        Returns:
        --------
        List[UserFollowedAuthor]: List of follow relationships
        """
        try:
            stmt = select(UserFollowedAuthor).where(
                UserFollowedAuthor.user_id == user_id
            )
            
            if not include_inactive:
                stmt = stmt.where(UserFollowedAuthor.is_active.is_(True))
            
            if offset is not None:
                stmt = stmt.offset(offset)
            if limit is not None:
                stmt = stmt.limit(limit)
            
            return list(self.db.scalars(stmt))
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get follow relationships for user {user_id}: {e}")
            return []
    
    def get_followers(
        self,
        author_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get users who follow an author.
        
        Parameters:
        -----------
        author_id : int
            Author ID
        limit : Optional[int]
            Maximum number of results
        offset : Optional[int]
            Number of records to skip
        
        Returns:
        --------
        List[Dict[str, Any]]: List of followers with details
        """
        try:
            query = (
                self.db.query(UserFollowedAuthor)
                .filter(
                    UserFollowedAuthor.author_id == author_id,
                    UserFollowedAuthor.is_active.is_(True)
                )
                .order_by(desc(UserFollowedAuthor.followed_at))
            )
            
            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)
            
            follows = query.all()
            
            result = []
            for follow in follows:
                result.append({
                    "user_id": follow.user_id,
                    "followed_at": follow.followed_at,
                    "notification_preference": follow.notification_preference,
                    "follow_source": follow.follow_source,
                })
            
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get followers for author {author_id}: {e}")
            return []
    
    # ============================================================
    # Count Operations
    # ============================================================
    
    def count_followers(
        self,
        author_id: int,
        include_inactive: bool = False
    ) -> int:
        """
        Count followers of an author.
        
        Parameters:
        -----------
        author_id : int
            Author ID
        include_inactive : bool
            Whether to include inactive followers
        
        Returns:
        --------
        int: Number of followers
        """
        try:
            stmt = select(func.count()).select_from(UserFollowedAuthor).where(
                UserFollowedAuthor.author_id == author_id
            )
            
            if not include_inactive:
                stmt = stmt.where(UserFollowedAuthor.is_active.is_(True))
            
            return self.db.scalar(stmt) or 0
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to count followers for author {author_id}: {e}")
            return 0
    
    def count_following(
        self,
        user_id: int,
        include_inactive: bool = False
    ) -> int:
        """
        Count authors followed by a user.
        
        Parameters:
        -----------
        user_id : int
            User ID
        include_inactive : bool
            Whether to include inactive follows
        
        Returns:
        --------
        int: Number of followed authors
        """
        try:
            stmt = select(func.count()).select_from(UserFollowedAuthor).where(
                UserFollowedAuthor.user_id == user_id
            )
            
            if not include_inactive:
                stmt = stmt.where(UserFollowedAuthor.is_active.is_(True))
            
            return self.db.scalar(stmt) or 0
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to count following for user {user_id}: {e}")
            return 0
    
    # ============================================================
    # Check Operations
    # ============================================================
    
    def is_following(
        self,
        user_id: int,
        author_id: int,
        include_inactive: bool = False
    ) -> bool:
        """
        Check if a user is following an author.
        
        Parameters:
        -----------
        user_id : int
            User ID
        author_id : int
            Author ID
        include_inactive : bool
            Whether to include inactive follows
        
        Returns:
        --------
        bool: True if following
        """
        return self.get_follow(user_id, author_id, include_inactive) is not None
    
    def are_following(
        self,
        user_ids: List[int],
        author_id: int
    ) -> Dict[int, bool]:
        """
        Check multiple users' follow status for an author.
        
        Parameters:
        -----------
        user_ids : List[int]
            List of user IDs
        author_id : int
            Author ID
        
        Returns:
        --------
        Dict[int, bool]: Mapping of user_id to follow status
        """
        if not user_ids:
            return {}
        
        try:
            stmt = (
                select(UserFollowedAuthor.user_id)
                .where(
                    UserFollowedAuthor.author_id == author_id,
                    UserFollowedAuthor.user_id.in_(user_ids),
                    UserFollowedAuthor.is_active.is_(True)
                )
            )
            
            following_ids = {row[0] for row in self.db.execute(stmt).all()}
            
            return {user_id: user_id in following_ids for user_id in user_ids}
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to check following status for users: {e}")
            return {}
    
    # ============================================================
    # Bulk Operations
    # ============================================================
    
    def bulk_follow(
        self,
        user_id: int,
        author_ids: List[int],
        follow_source: str = "bulk"
    ) -> Tuple[int, int]:
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
        Tuple[int, int]: (successful, failed)
        """
        if not author_ids:
            return (0, 0)
        
        successful = 0
        failed = 0
        
        for author_id in author_ids:
            try:
                self.follow_author(
                    user_id=user_id,
                    author_id=author_id,
                    follow_source=follow_source
                )
                successful += 1
            except Exception:
                failed += 1
        
        logger.info(f"Bulk follow: {successful} successful, {failed} failed for user {user_id}")
        return (successful, failed)
    
    def bulk_unfollow(
        self,
        user_id: int,
        author_ids: List[int]
    ) -> Tuple[int, int]:
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
        Tuple[int, int]: (successful, failed)
        """
        if not author_ids:
            return (0, 0)
        
        successful = 0
        failed = 0
        
        for author_id in author_ids:
            try:
                if self.unfollow_author(user_id, author_id):
                    successful += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
        
        logger.info(f"Bulk unfollow: {successful} successful, {failed} failed for user {user_id}")
        return (successful, failed)
    
    def remove_all_follows(
        self,
        user_id: int,
        hard_delete: bool = True
    ) -> int:
        """
        Remove all follows for a user.
        
        Parameters:
        -----------
        user_id : int
            User ID
        hard_delete : bool
            If True, permanently delete
            If False, soft delete
        
        Returns:
        --------
        int: Number of follows removed
        """
        follows = self.get_follow_relationships(user_id)
        count = len(follows)
        
        if count == 0:
            return 0
        
        try:
            if hard_delete:
                for follow in follows:
                    self.db.delete(follow)
            else:
                for follow in follows:
                    follow.is_active = False
                    follow.unfollowed_at = datetime.now()
            
            self.db.commit()
            logger.info(f"Removed {count} follows for user {user_id}")
            return count
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to remove follows for user {user_id}: {e}")
            raise
    
    # ============================================================
    # Statistics and Utility Methods
    # ============================================================
    
    def get_stats(
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
        Dict[str, Any]: Statistics dictionary
        """
        try:
            total = self.count_followers(author_id)
            
            # Get recent follows (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent = (
                self.db.query(UserFollowedAuthor)
                .filter(
                    UserFollowedAuthor.author_id == author_id,
                    UserFollowedAuthor.is_active.is_(True),
                    UserFollowedAuthor.followed_at >= thirty_days_ago
                )
                .count()
            )
            
            # Get follow sources
            sources = (
                self.db.query(
                    UserFollowedAuthor.follow_source,
                    func.count().label("count")
                )
                .filter(
                    UserFollowedAuthor.author_id == author_id,
                    UserFollowedAuthor.is_active.is_(True)
                )
                .group_by(UserFollowedAuthor.follow_source)
                .all()
            )
            
            return {
                "total_followers": total,
                "recent_follows_30d": recent,
                "follow_sources": {s[0] or "unknown": s[1] for s in sources},
                "timestamp": datetime.now().isoformat()
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get stats for author {author_id}: {e}")
            return {}
    
    def get_popular_authors_by_follows(
        self,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get most followed authors.
        
        Parameters:
        -----------
        limit : int
            Maximum number of results
        
        Returns:
        --------
        List[Dict[str, Any]]: List of authors with follow counts
        """
        try:
            result = (
                self.db.query(
                    Author.id,
                    Author.name,
                    func.count(UserFollowedAuthor.id).label("follow_count")
                )
                .join(
                    UserFollowedAuthor,
                    UserFollowedAuthor.author_id == Author.id
                )
                .filter(
                    Author.is_active.is_(True),
                    UserFollowedAuthor.is_active.is_(True)
                )
                .group_by(Author.id)
                .order_by(desc("follow_count"))
                .limit(limit)
                .all()
            )
            
            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "follow_count": r[2]
                }
                for r in result
            ]
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get popular authors by follows: {e}")
            return []