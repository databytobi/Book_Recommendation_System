from __future__ import annotations

"""
Author Repository

Repository for Author database operations including CRUD, search,
and specialized queries for recommendations.

Phase: Data Access Layer
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import logging
from sqlalchemy import select, func, desc, and_, or_, case
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.models.author import Author

logger = logging.getLogger(__name__)


class AuthorRepository:
    """
    Repository for Author operations.
    
    Handles:
    - CRUD operations
    - Search and autocomplete
    - Featured authors
    - Trending authors
    - Popular authors
    - Recommendation candidates
    - Random selection
    - Batch operations
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
    
    def create(self, author: Author) -> Author:
        """
        Create a new author.
        
        Parameters:
        -----------
        author : Author
            Author instance to create
        
        Returns:
        --------
        Author: Created author
        
        Raises:
        -------
        ValueError: If author is invalid
        SQLAlchemyError: If database operation fails
        """
        if not author:
            raise ValueError("Author cannot be None")
        
        if not author.name or not author.name.strip():
            raise ValueError("Author name is required")
        
        try:
            self.db.add(author)
            self.db.commit()
            self.db.refresh(author)
            
            logger.debug(f"Created author: {author.name} (ID: {author.id})")
            return author
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to create author: {e}")
            raise
    
    def get_by_id(self, author_id: int) -> Optional[Author]:
        """
        Get an author by ID.
        
        Parameters:
        -----------
        author_id : int
            Author ID
        
        Returns:
        --------
        Optional[Author]: Author instance or None
        """
        if not author_id or author_id <= 0:
            return None
        
        try:
            return self.db.get(Author, author_id)
        except SQLAlchemyError as e:
            logger.error(f"Failed to get author by ID {author_id}: {e}")
            return None
    
    def get_by_ids(
        self,
        author_ids: list[int],
    ) -> list[Author]:
        """
        Get multiple authors by their IDs.
        
        Parameters:
        -----------
        author_ids : list[int]
            List of author IDs to fetch
        
        Returns:
        --------
        list[Author]: List of active authors matching the provided IDs
        """
        if not author_ids:
            return []

        unique_ids = list(set(author_ids))

        stmt = (
            select(Author)
            .where(
                Author.id.in_(unique_ids),
                Author.is_active.is_(True),
            )
         )

        return list(self.db.scalars(stmt))

    def get_by_id_with_books(self, author_id: int) -> Optional[Author]:
        """
        Get an author by ID with their books loaded.
        
        Parameters:
        -----------
        author_id : int
            Author ID
        
        Returns:
        --------
        Optional[Author]: Author instance with books or None
        """
        if not author_id or author_id <= 0:
            return None
        
        try:
            stmt = (
                select(Author)
                .where(Author.id == author_id)
                .options(selectinload(Author.books))
            )
            return self.db.scalar(stmt)
        except SQLAlchemyError as e:
            logger.error(f"Failed to get author with books by ID {author_id}: {e}")
            return None
    
    def get_by_name(self, name: str, case_sensitive: bool = False) -> Optional[Author]:
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
        if not name or not name.strip():
            return None
        
        try:
            if case_sensitive:
                stmt = select(Author).where(Author.name == name)
            else:
                stmt = select(Author).where(func.lower(Author.name) == name.lower())
            
            return self.db.scalar(stmt)
        except SQLAlchemyError as e:
            logger.error(f"Failed to get author by name '{name}': {e}")
            return None
    
    def update(self, author: Author) -> Author:
        """
        Update an existing author.
        
        Parameters:
        -----------
        author : Author
            Author instance to update
        
        Returns:
        --------
        Author: Updated author
        
        Raises:
        -------
        ValueError: If author is None
        SQLAlchemyError: If database operation fails
        """
        if not author:
            raise ValueError("Author cannot be None")
        
        try:
            # Update timestamp if available
            if hasattr(author, 'updated_at'):
                author.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(author)
            
            logger.debug(f"Updated author: {author.name} (ID: {author.id})")
            return author
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to update author: {e}")
            raise
    
    def delete(self, author_id: int, hard_delete: bool = False) -> bool:
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
        author = self.get_by_id(author_id)
        if not author:
            logger.warning(f"Author {author_id} not found for deletion")
            return False
        
        try:
            if hard_delete:
                self.db.delete(author)
                logger.info(f"Hard deleted author: {author.name} (ID: {author_id})")
            else:
                author.is_active = False
                if hasattr(author, 'deleted_at'):
                    author.deleted_at = datetime.now()
                logger.info(f"Soft deleted author: {author.name} (ID: {author_id})")
            
            self.db.commit()
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to delete author {author_id}: {e}")
            raise
    
    # ============================================================
    # Listing Operations
    # ============================================================
    
    def list(
        self,
        skip: int = 0,
        limit: int = 50,
        include_inactive: bool = False,
        order_by: str = "name",
        order_direction: str = "asc"
    ) -> List[Author]:
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
            Field to order by (name, popularity_score, total_books, average_rating)
        order_direction : str
            Sort direction (asc, desc)
        
        Returns:
        --------
        List[Author]: List of authors
        """
        try:
            stmt = select(Author)
            
            if not include_inactive:
                stmt = stmt.where(Author.is_active.is_(True))
            
            # Apply ordering
            order_column = getattr(Author, order_by, Author.name)
            if order_direction.lower() == "desc":
                stmt = stmt.order_by(desc(order_column))
            else:
                stmt = stmt.order_by(order_column)
            
            stmt = stmt.offset(skip).limit(limit)
            
            return list(self.db.scalars(stmt))
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to list authors: {e}")
            return []
    
    def list_by_ids(
        self,
        author_ids: List[int],
        include_inactive: bool = False
    ) -> List[Author]:
        """
        List authors by IDs.
        
        Parameters:
        -----------
        author_ids : List[int]
            List of author IDs
        include_inactive : bool
            Whether to include inactive authors
        
        Returns:
        --------
        List[Author]: List of authors
        """
        if not author_ids:
            return []
        
        try:
            stmt = select(Author).where(Author.id.in_(author_ids))
            
            if not include_inactive:
                stmt = stmt.where(Author.is_active.is_(True))
            
            return list(self.db.scalars(stmt))
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to list authors by IDs: {e}")
            return []
    
    # ============================================================
    # Search Operations
    # ============================================================
    
    def search(
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
        if not query or not query.strip():
            return []
        
        try:
            search_term = f"%{query.strip()}%"
            
            conditions = [Author.name.ilike(search_term)]
            
            if not include_inactive:
                conditions.append(Author.is_active.is_(True))
            
            if min_popularity is not None:
                conditions.append(Author.popularity_score >= min_popularity)
            
            stmt = (
                select(Author)
                .where(and_(*conditions))
                .order_by(
                    desc(Author.popularity_score),
                    Author.name
                )
                .limit(limit)
            )
            
            return list(self.db.scalars(stmt))
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to search authors with query '{query}': {e}")
            return []
    
    def autocomplete(
        self,
        prefix: str,
        limit: int = 10,
        include_inactive: bool = False
    ) -> List[Author]:
        """
        Autocomplete authors by name prefix.
        
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
        List[Author]: List of matching authors
        """
        if not prefix or not prefix.strip():
            return []
        
        try:
            search_term = f"{prefix.strip()}%"
            
            conditions = [
                Author.name.ilike(search_term),
                Author.is_active.is_(True)
            ] if not include_inactive else [Author.name.ilike(search_term)]
            
            stmt = (
                select(Author)
                .where(and_(*conditions))
                .order_by(
                    desc(Author.popularity_score),
                    Author.name
                )
                .limit(limit)
            )
            
            return list(self.db.scalars(stmt))
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to autocomplete authors with prefix '{prefix}': {e}")
            return []
    
    def search_by_names(
        self,
        names: List[str],
        limit: int = 50
    ) -> List[Author]:
        """
        Search authors by multiple names.
        
        Parameters:
        -----------
        names : List[str]
            List of author names
        limit : int
            Maximum number of results
        
        Returns:
        --------
        List[Author]: List of matching authors
        """
        if not names:
            return []
        
        try:
            # Clean names and create search patterns
            patterns = [f"%{name.strip()}%" for name in names if name and name.strip()]
            
            if not patterns:
                return []
            
            # Build OR conditions
            conditions = [
                Author.name.ilike(pattern) for pattern in patterns
            ]
            
            stmt = (
                select(Author)
                .where(Author.is_active.is_(True))
                .where(or_(*conditions))
                .order_by(desc(Author.popularity_score))
                .limit(limit)
            )
            
            return list(self.db.scalars(stmt))
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to search authors by names: {e}")
            return []
    
    # ============================================================
    # Specialized Queries
    # ============================================================
    
    def get_popular(
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
        try:
            conditions = [Author.is_active.is_(True)]
            
            if min_popularity is not None:
                conditions.append(Author.popularity_score >= min_popularity)
            
            stmt = (
                select(Author)
                .where(and_(*conditions))
                .order_by(desc(Author.popularity_score))
                .limit(limit)
            )
            
            return list(self.db.scalars(stmt))
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get popular authors: {e}")
            return []
    
    def get_top_rated(
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
        try:
            conditions = [Author.is_active.is_(True)]
            
            if min_rating is not None:
                conditions.append(Author.average_rating >= min_rating)
            
            stmt = (
                select(Author)
                .where(and_(*conditions))
                .order_by(desc(Author.average_rating))
                .limit(limit)
            )
            
            return list(self.db.scalars(stmt))
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get top rated authors: {e}")
            return []
    
    def get_most_prolific(
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
        try:
            conditions = [Author.is_active.is_(True)]
            
            if min_books is not None:
                conditions.append(Author.total_books >= min_books)
            
            stmt = (
                select(Author)
                .where(and_(*conditions))
                .order_by(desc(Author.total_books))
                .limit(limit)
            )
            
            return list(self.db.scalars(stmt))
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get most prolific authors: {e}")
            return []
    
    def get_featured(
        self,
        limit: int = 10,
        min_popularity: float = 0.5
    ) -> List[Author]:
        """
        Get featured authors (high popularity, recent updates).
        
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
        try:
            stmt = (
                select(Author)
                .where(
                    Author.is_active.is_(True),
                    Author.popularity_score >= min_popularity
                )
                .order_by(
                    desc(Author.popularity_score),
                    desc(Author.total_books)
                )
                .limit(limit)
            )
            
            return list(self.db.scalars(stmt))
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get featured authors: {e}")
            return []
    
    def get_trending(
        self,
        limit: int = 10,
        days: int = 30
    ) -> List[Author]:
        """
        Get trending authors based on recent popularity changes.
        
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
        # This is a simplified version - in production, you'd track
        # popularity changes over time
        try:
            stmt = (
                select(Author)
                .where(
                    Author.is_active.is_(True),
                    Author.popularity_score > 0.5
                )
                .order_by(
                    desc(Author.popularity_score),
                    desc(Author.total_books)
                )
                .limit(limit)
            )
            
            return list(self.db.scalars(stmt))
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get trending authors: {e}")
            return []
    
    def get_recommendation_candidates(
        self,
        limit: int = 200,
        exclude_ids: Optional[List[int]] = None,
        min_popularity: float = 0.3
    ) -> List[Author]:
        """
        Get authors suitable for recommendations.
        
        Parameters:
        -----------
        limit : int
            Maximum number of results
        exclude_ids : Optional[List[int]]
            Author IDs to exclude
        min_popularity : float
            Minimum popularity score
        
        Returns:
        --------
        List[Author]: List of recommendation candidates
        """
        try:
            conditions = [
                Author.is_active.is_(True),
                Author.popularity_score >= min_popularity
            ]
            
            if exclude_ids:
                conditions.append(Author.id.notin_(exclude_ids))
            
            stmt = (
                select(Author)
                .where(and_(*conditions))
                .order_by(
                    desc(Author.popularity_score),
                    desc(Author.average_rating),
                    desc(Author.total_books)
                )
                .limit(limit)
            )
            
            return list(self.db.scalars(stmt))
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get recommendation candidates: {e}")
            return []
    
    def get_random(
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
        try:
            stmt = select(Author)
            
            if not include_inactive:
                stmt = stmt.where(Author.is_active.is_(True))
            
            stmt = stmt.order_by(func.random()).limit(limit)
            
            return list(self.db.scalars(stmt))
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get random authors: {e}")
            return []
    
    def get_emerging(
        self,
        limit: int = 20,
        min_books: int = 1,
        max_books: int = 5,
    ) -> List[Author]:
        """
        Get emerging authors (new or with few books).
        
        Parameters:
        -----------
        limit : int
            Maximum number of authors to return
        min_books : int
            Minimum number of books
        max_books : int
            Maximum number of books
        
        Returns:
        --------
        List[Author]: List of emerging authors
        """
        try:
            stmt = (
                select(Author)
                .where(
                    Author.is_active.is_(True),
                    Author.total_books >= min_books,
                    Author.total_books <= max_books,
                    Author.average_rating >= 4.0,
                )
                .order_by(
                    desc(Author.average_rating),
                    desc(Author.popularity_score),
                )
                .limit(limit)
            )

            return list(self.db.scalars(stmt))
        except SQLAlchemyError as e:
            logger.error(f"Failed to get emerging authors: {e}")
            return []
    
    # ============================================================
    # Bulk Operations
    # ============================================================
    
    def bulk_create(self, authors: List[Author]) -> List[Author]:
        """
        Bulk create authors.
        
        Parameters:
        -----------
        authors : List[Author]
            List of authors to create
        
        Returns:
        --------
        List[Author]: Created authors
        """
        if not authors:
            return []
        
        try:
            self.db.add_all(authors)
            self.db.commit()
            
            for author in authors:
                self.db.refresh(author)
            
            logger.info(f"Bulk created {len(authors)} authors")
            return authors
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to bulk create authors: {e}")
            raise
    
    def bulk_update_popularity(
        self,
        author_ids: List[int],
        popularity_score: float
    ) -> int:
        """
        Bulk update popularity scores.
        
        Parameters:
        -----------
        author_ids : List[int]
            Author IDs to update
        popularity_score : float
            New popularity score
        
        Returns:
        --------
        int: Number of authors updated
        """
        if not author_ids:
            return 0
        
        try:
            result = (
                self.db.query(Author)
                .filter(Author.id.in_(author_ids))
                .update(
                    {"popularity_score": popularity_score},
                    synchronize_session=False
                )
            )
            self.db.commit()
            
            logger.info(f"Bulk updated popularity for {result} authors")
            return result
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to bulk update popularity: {e}")
            raise
    
    # ============================================================
    # Statistics and Utility Methods
    # ============================================================
    
    def count(
        self,
        include_inactive: bool = False,
        min_popularity: Optional[float] = None
    ) -> int:
        """
        Count authors.
        
        Parameters:
        -----------
        include_inactive : bool
            Whether to include inactive authors
        min_popularity : Optional[float]
            Minimum popularity score filter
        
        Returns:
        --------
        int: Number of authors
        """
        try:
            stmt = select(func.count()).select_from(Author)
            
            if not include_inactive:
                stmt = stmt.where(Author.is_active.is_(True))
            
            if min_popularity is not None:
                stmt = stmt.where(Author.popularity_score >= min_popularity)
            
            return self.db.scalar(stmt) or 0
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to count authors: {e}")
            return 0
    
    def exists(self, author_id: int) -> bool:
        """
        Check if an author exists.
        
        Parameters:
        -----------
        author_id : int
            Author ID
        
        Returns:
        --------
        bool: True if author exists
        """
        return self.get_by_id(author_id) is not None
    
    def exists_by_name(
        self,
        name: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Check if an author with the given name exists.
        
        Parameters:
        -----------
        name : str
            Author name
        exclude_id : Optional[int]
            Author ID to exclude (for updates)
        
        Returns:
        --------
        bool: True if author exists
        """
        if not name or not name.strip():
            return False
        
        try:
            stmt = select(Author).where(func.lower(Author.name) == name.lower())
            
            if exclude_id:
                stmt = stmt.where(Author.id != exclude_id)
            
            return self.db.scalar(stmt) is not None
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to check author existence by name '{name}': {e}")
            return False
    
    def refresh_popularity(self, author: Author) -> Author:
        """
        Refresh an author's popularity score.
        
        Parameters:
        -----------
        author : Author
            Author instance
        
        Returns:
        --------
        Author: Updated author
        """
        if not author:
            raise ValueError("Author cannot be None")
        
        try:
            author.update_popularity()
            self.db.commit()
            self.db.refresh(author)
            
            logger.debug(f"Refreshed popularity for author: {author.name}")
            return author
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to refresh popularity: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get author statistics.
        
        Returns:
        --------
        Dict[str, Any]: Statistics dictionary
        """
        try:
            total = self.count()
            active = self.count(include_inactive=False)
            
            # Get average stats
            stmt = select(
                func.avg(Author.popularity_score),
                func.avg(Author.average_rating),
                func.sum(Author.total_books)
            ).where(Author.is_active.is_(True))
            
            result = self.db.execute(stmt).first()
            
            return {
                "total_authors": total,
                "active_authors": active,
                "inactive_authors": total - active,
                "avg_popularity": float(result[0] or 0),
                "avg_rating": float(result[1] or 0),
                "total_books": int(result[2] or 0),
                "timestamp": datetime.now().isoformat()
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get author stats: {e}")
            return {}
    
    def get_popularity_distribution(self) -> Dict[str, int]:
        """
        Get popularity score distribution.
        
        Returns:
        --------
        Dict[str, int]: Distribution counts
        """
        try:
            # Using SQLAlchemy 2.0 case syntax
            stmt = (
                select(
                    case(
                        (Author.popularity_score >= 0.8, "high"),
                        (Author.popularity_score >= 0.5, "medium"),
                        else_="low"
                    ).label("tier"),
                    func.count().label("count")
                )
                .where(Author.is_active.is_(True))
                .group_by("tier")
            )
            
            results = self.db.execute(stmt).all()
            
            distribution = {"high": 0, "medium": 0, "low": 0}
            for tier, count in results:
                distribution[tier] = count
            
            return distribution
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get popularity distribution: {e}")
            return {"high": 0, "medium": 0, "low": 0}