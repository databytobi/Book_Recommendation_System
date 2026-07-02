from __future__ import annotations

import random
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.models.author import Author
from app.repositories.author_repository import AuthorRepository
# pyrefly: ignore [missing-import]
from app.api.v1.authors.schemas import (
    AuthorResponse,
    AuthorDiscoverySection,
    AuthorDiscoveryResponse,
)

logger = logging.getLogger(__name__)


class AuthorDiscoveryService:
    """
    Service for author discovery and recommendations.
    
    Handles:
    - Popular authors
    - Top rated authors
    - Emerging authors
    - Random authors
    - Onboarding author selection
    - Discovery sections building
    """
    
    def __init__(self, db: Session):
        """
        Initialize the author discovery service.
        
        Parameters:
        -----------
        db : Session
            SQLAlchemy database session
        """
        self.db = db
        self.author_repo = AuthorRepository(db)
    
    def popular(
        self,
        limit: int = 20,
        min_popularity: Optional[float] = None,
    ) -> List[Author]:
        """
        Get popular authors.
        
        Parameters:
        -----------
        limit : int
            Maximum number of authors to return
        min_popularity : Optional[float]
            Minimum popularity score filter
        
        Returns:
        --------
        List[Author]: List of popular authors
        """
        return self.author_repo.get_popular(limit, min_popularity)
    
    def top_rated(
        self,
        limit: int = 20,
        min_rating: Optional[float] = None,
    ) -> List[Author]:
        """
        Get top rated authors.
        
        Parameters:
        -----------
        limit : int
            Maximum number of authors to return
        min_rating : Optional[float]
            Minimum rating filter
        
        Returns:
        --------
        List[Author]: List of top rated authors
        """
        return self.author_repo.get_top_rated(limit, min_rating)
    
    def random(
        self,
        limit: int = 20,
        include_inactive: bool = False,
        seed: Optional[int] = None,
    ) -> List[Author]:
        """
        Get random authors.
        
        Parameters:
        -----------
        limit : int
            Maximum number of authors to return
        include_inactive : bool
            Whether to include inactive authors
        seed : Optional[int]
            Random seed for reproducibility
        
        Returns:
        --------
        List[Author]: List of random authors
        """
        return self.author_repo.get_random(limit, include_inactive, seed)
    
    def emerging(
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
        return self.author_repo.get_emerging(limit, min_books, max_books)
    
    def trending(
        self,
        limit: int = 20,
        days: int = 30,
    ) -> List[Author]:
        """
        Get trending authors.
        
        Parameters:
        -----------
        limit : int
            Maximum number of authors to return
        days : int
            Number of days to consider for trending
        
        Returns:
        --------
        List[Author]: List of trending authors
        """
        return self.author_repo.get_trending(limit, days)
    
    def featured(
        self,
        limit: int = 20,
        min_popularity: float = 0.5,
    ) -> List[Author]:
        """
        Get featured authors.
        
        Parameters:
        -----------
        limit : int
            Maximum number of authors to return
        min_popularity : float
            Minimum popularity score
        
        Returns:
        --------
        List[Author]: List of featured authors
        """
        return self.author_repo.get_featured(limit, min_popularity)
    
    def recently_added(
        self,
        limit: int = 20,
        days: int = 30,
    ) -> List[Author]:
        """
        Get recently added authors.
        
        Parameters:
        -----------
        limit : int
            Maximum number of authors to return
        days : int
            Number of days to consider
        
        Returns:
        --------
        List[Author]: List of recently added authors
        """
        return self.author_repo.get_recently_added(limit, days)
    
    def _remove_duplicates(
        self,
        authors: List[Author],
    ) -> List[Author]:
        """
        Remove duplicate authors while preserving order.
        
        Parameters:
        -----------
        authors : List[Author]
            List of authors with potential duplicates
        
        Returns:
        --------
        List[Author]: List with duplicates removed
        """
        seen = set()
        unique = []
        
        for author in authors:
            if author.id in seen:
                continue
            seen.add(author.id)
            unique.append(author)
        
        return unique
    
    def onboarding_authors(
        self,
        limit: int = 30,
    ) -> List[Author]:
        """
        Return a balanced set of authors for onboarding.
        
        Parameters:
        -----------
        limit : int
            Maximum number of authors to return
        
        Returns:
        --------
        List[Author]: Balanced list of authors for onboarding
        """
        # Calculate distribution
        popular_count = int(limit * 0.40)
        rated_count = int(limit * 0.30)
        emerging_count = int(limit * 0.20)
        random_count = limit - popular_count - rated_count - emerging_count
        
        # Fetch authors from different categories
        popular = self.popular(popular_count)
        rated = self.top_rated(rated_count)
        emerging = self.emerging(emerging_count)
        random_authors = self.random(random_count)
        
        # Combine and deduplicate
        authors = popular + rated + emerging + random_authors
        authors = self._remove_duplicates(authors)
        
        # Shuffle for variety
        random.shuffle(authors)
        
        return authors[:limit]
    
    def build_discovery_section(
        self,
        section_type: str,
        title: str,
        limit: int = 20,
        **kwargs,
    ) -> AuthorDiscoverySection:
        """
        Build a discovery section with authors.
        
        Parameters:
        -----------
        section_type : str
            Type of section ('popular', 'top_rated', 'emerging', 'random', 
                         'trending', 'featured', 'recently_added')
        title : str
            Display title for the section
        limit : int
            Number of authors to include
        **kwargs : Additional parameters for specific section types
        
        Returns:
        --------
        AuthorDiscoverySection: Discovery section with authors
        
        Raises:
        -------
        ValueError: If section_type is invalid
        """
        # Map section types to methods
        section_methods = {
            'popular': self.popular,
            'top_rated': self.top_rated,
            'emerging': self.emerging,
            'random': self.random,
            'trending': self.trending,
            'featured': self.featured,
            'recently_added': self.recently_added,
        }
        
        # Get the appropriate method
        method = section_methods.get(section_type)
        if not method:
            raise ValueError(
                f"Invalid section_type: {section_type}. "
                f"Allowed types: {', '.join(section_methods.keys())}"
            )
        
        # Fetch authors
        authors = method(limit=limit, **kwargs)
        
        # Convert to AuthorResponse if needed
        # Assuming Author has a to_dict method or we'll use model_dump
        author_responses = []
        for author in authors:
            if hasattr(author, 'to_response'):
                author_responses.append(author.to_response())
            else:
                # Convert Author model to dict/response
                author_responses.append(AuthorResponse.model_validate(author))
        
        return AuthorDiscoverySection(
            title=title,
            type=section_type,
            authors=author_responses,
        )
    
    def build_discovery_response(
        self,
        sections_config: List[Dict[str, Any]],
    ) -> AuthorDiscoveryResponse:
        """
        Build a complete discovery response with multiple sections.
        
        Parameters:
        -----------
        sections_config : List[Dict[str, Any]]
            List of section configurations.
            Each dict should contain:
            - type: str (section type)
            - title: str (display title)
            - limit: int (number of authors)
            - kwargs: dict (additional parameters)
        
        Returns:
        --------
        AuthorDiscoveryResponse: Complete discovery response
        
        Example:
        ```python
        config = [
            {
                "type": "popular",
                "title": "Popular Authors",
                "limit": 10,
                "kwargs": {"min_popularity": 0.5}
            },
            {
                "type": "trending",
                "title": "Trending Now",
                "limit": 10,
                "kwargs": {"days": 7}
            },
            {
                "type": "emerging",
                "title": "Emerging Voices",
                "limit": 10,
                "kwargs": {"max_books": 3}
            }
        ]
        """
        sections = []

        for config in sections_config:
            try:
                section_type = config.get('type')
                title = config.get('title', section_type.title())
                limit = config.get('limit', 20)
                kwargs = config.get('kwargs', {})

                section = self.build_discovery_section(
                    section_type=section_type,
                    title=title,
                    limit=limit,
                    **kwargs,
                )
                sections.append(section)

            except Exception as e:
                logger.error(f"Failed to build section {config}: {e}")

        # Continue with other sections
        return AuthorDiscoveryResponse(sections=sections)

    def get_onboarding_discovery(
        self,
        limit_per_section: int = 10,
    ) -> AuthorDiscoveryResponse:
        """
        Get discovery sections specifically for onboarding.

        Parameters:

        limit_per_section : int
        Number of authors per section

        Returns:

        AuthorDiscoveryResponse: Onboarding discovery response
        """
        sections_config = [
        {
            "type": "popular",
            "title": "Popular Authors",
            "limit": limit_per_section,
            "kwargs": {"min_popularity": 0.5}
        },
        {
            "type": "top_rated",
            "title": "Top Rated",
            "limit": limit_per_section,
            "kwargs": {"min_rating": 4.0}
        },
        {
            "type": "trending",
            "title": "Trending Now",
            "limit": limit_per_section,
            "kwargs": {"days": 7}
        },
        {
            "type": "emerging",
            "title": "Emerging Voices",
            "limit": limit_per_section,
            "kwargs": {"max_books": 3}
        },
        ]

        return self.build_discovery_response(sections_config)

    def get_homepage_discovery(
        self,
        limit_per_section: int = 20,
    ) -> AuthorDiscoveryResponse:
        """
        Get discovery sections for the homepage.

        Parameters:

        limit_per_section : int
        Number of authors per section

        Returns:

        AuthorDiscoveryResponse: Homepage discovery response
        """
        sections_config = [
        {
            "type": "featured",
            "title": "Featured Authors",
            "limit": limit_per_section,
            "kwargs": {"min_popularity": 0.7}
        },
        {
        "type": "trending",
        "title": "Trending This Week",
        "limit": limit_per_section,
        "kwargs": {"days": 7}
    },
    {
        "type": "popular",
        "title": "Most Popular",
        "limit": limit_per_section,
        "kwargs": {"min_popularity": 0.3}
    },
    {
        "type": "recently_added",
        "title": "New Authors",
        "limit": limit_per_section,
        "kwargs": {"days": 30}
    },
    {
        "type": "top_rated",
        "title": "Highest Rated",
        "limit": limit_per_section,
        "kwargs": {"min_rating": 4.0}
    },
    {
        "type": "emerging",
        "title": "Up and Coming",
        "limit": limit_per_section,
        "kwargs": {"max_books": 5}
    },
    ]

        return self.build_discovery_response(sections_config)

    def get_personalized_discovery(
        self,
        user_id: int,
        limit_per_section: int = 20,
    ) -> AuthorDiscoveryResponse:
        """
        Get personalized discovery sections for a user.

        Parameters:
    
        user_id : int
            User ID for personalization
        limit_per_section : int
            Number of authors per section

        Returns:

        AuthorDiscoveryResponse: Personalized discovery response
        """

        # This would be more sophisticated with actual user data
        sections_config = [
        {
            "type": "recommended",
            "title": "Recommended for You",
            "limit": limit_per_section,
            "kwargs": {"user_id": user_id, "min_popularity": 0.3}
        },
        {
            "type": "trending",
        "title": "Trending in Your Network",
        "limit": limit_per_section,
        "kwargs": {"days": 7}
    },
        {
            "type": "popular",
            "title": "Popular Among Readers Like You",
            "limit": limit_per_section,
            "kwargs": {"min_popularity": 0.3}
        },
        ]

        return self.build_discovery_response(sections_config)