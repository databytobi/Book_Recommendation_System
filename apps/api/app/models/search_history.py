"""
Search History Model

SQLAlchemy model for tracking user search queries, filters, and search behavior.

Phase: Database Models
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
import json
import logging
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    Integer,
    Float,
    Boolean,
    Text,
    Index,
    UniqueConstraint,
    CheckConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

logger = logging.getLogger(__name__)


class SearchHistory(Base):
    """
    Model for tracking user search queries and search behavior.
    
    Attributes:
    -----------
    id : int
        Primary key
    user_id : str
        User identifier (UUID)
    session_id : str
        Session identifier
    query : str
        Search query text
    normalized_query : str
        Normalized version of the search query
    search_type : str
        Type of search (semantic, keyword, hybrid, filter)
    filters : str
        JSON string of applied filters (category, author, year, etc.)
    sort_by : str
        Sort order (relevance, popularity, rating, date)
    results_count : int
        Number of search results returned
    page : int
        Page number in results
    page_size : int
        Items per page
    selected_isbn : str
        ISBN of book clicked/selected from results
    selected_rank : int
        Position of selected book in results
    time_to_select : float
        Time from search to selection in seconds
    is_clicked : bool
        Whether the user clicked on a result
    is_saved_search : bool
        Whether the search was saved for later
    ip_address : str
        IP address of the user
    user_agent : str
        User agent string
    referer : str
        Referer URL
    device_type : str
        Device type (web, mobile, tablet)
    browser : str
        Browser information
    os : str
        Operating system
    location : str
        User location (city, country)
    metadata : str
        JSON string with additional metadata
    created_at : datetime
        Search timestamp
    updated_at : datetime
        Last update timestamp
    """
    
    __tablename__ = "search_history"
    
    # ============================================================
    # COLUMNS
    # ============================================================
    
    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        doc="Primary key"
    )
    
    user_id = Column(
        String(36),
        nullable=True,
        index=True,
        doc="User identifier (UUID)"
    )
    
    session_id = Column(
        String(64),
        nullable=True,
        index=True,
        doc="Session identifier"
    )
    
    query = Column(
        String(500),
        nullable=False,
        index=True,
        doc="Search query text"
    )
    
    normalized_query = Column(
        String(500),
        nullable=True,
        index=True,
        doc="Normalized version of the search query"
    )
    
    search_type = Column(
        String(20),
        nullable=True,
        index=True,
        doc="Type of search: semantic, keyword, hybrid, filter"
    )
    
    filters = Column(
        Text,
        nullable=True,
        doc="JSON string of applied filters"
    )
    
    sort_by = Column(
        String(20),
        nullable=True,
        doc="Sort order: relevance, popularity, rating, date"
    )
    
    results_count = Column(
        Integer,
        nullable=True,
        doc="Number of search results returned"
    )
    
    page = Column(
        Integer,
        default=1,
        doc="Page number in results"
    )
    
    page_size = Column(
        Integer,
        default=10,
        doc="Items per page"
    )
    
    selected_isbn = Column(
        String(13),
        nullable=True,
        index=True,
        doc="ISBN of book clicked/selected from results"
    )
    
    selected_rank = Column(
        Integer,
        nullable=True,
        doc="Position of selected book in results"
    )
    
    time_to_select = Column(
        Float,
        nullable=True,
        doc="Time from search to selection in seconds"
    )
    
    is_clicked = Column(
        Boolean,
        default=False,
        doc="Whether the user clicked on a result"
    )
    
    is_saved_search = Column(
        Boolean,
        default=False,
        doc="Whether the search was saved for later"
    )
    
    ip_address = Column(
        String(45),
        nullable=True,
        doc="IP address (IPv4 or IPv6)"
    )
    
    user_agent = Column(
        String(255),
        nullable=True,
        doc="User agent string"
    )
    
    referer = Column(
        String(512),
        nullable=True,
        doc="Referer URL"
    )
    
    device_type = Column(
        String(20),
        nullable=True,
        doc="Device type: web, mobile, tablet"
    )
    
    browser = Column(
        String(50),
        nullable=True,
        doc="Browser information"
    )
    
    os = Column(
        String(50),
        nullable=True,
        doc="Operating system"
    )
    
    location = Column(
        String(100),
        nullable=True,
        doc="User location (city, country)"
    )
    
    meta_data = Column(
        "metadata",
        Text,
        nullable=True,
        doc="JSON string with additional metadata"
    )
    
    searched_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="Search timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        doc="Last update timestamp"
    )
    
    # ============================================================
    # CONSTRAINTS & INDEXES
    # ============================================================
    
    __table_args__ = (
        # Composite indexes for common queries
        Index('ix_search_history_user_query', 'user_id', 'query'),
        Index('ix_search_history_user_type', 'user_id', 'search_type'),
        Index('ix_search_history_searched_at', 'searched_at'),
        Index('ix_search_history_query_normalized', 'normalized_query'),
        Index('ix_search_history_user_selected', 'user_id', 'selected_isbn'),
        # Unique constraint to prevent duplicate searches (optional)
        UniqueConstraint(
            'user_id', 'query', 'searched_at',
            name='uq_search_history'
        )
    )
    
    # ============================================================
    # PROPERTIES
    # ============================================================
    
    @property
    def is_empty_query(self) -> bool:
        """Check if the query is empty or only whitespace."""
        return not self.query or not self.query.strip()
    
    @property
    def query_length(self) -> int:
        """Get the length of the query."""
        return len(self.query) if self.query else 0
    
    @property
    def query_word_count(self) -> int:
        """Get the number of words in the query."""
        if not self.query:
            return 0
        return len(self.query.split())
    
    @property
    def is_clicked_through(self) -> bool:
        """Check if the user clicked through to a result."""
        return self.is_clicked and self.selected_isbn is not None
    
    @property
    def has_filters(self) -> bool:
        """Check if filters were applied to the search."""
        return bool(self.filters and self.filters.strip() and self.filters != '{}')
    
    @property
    def created_at_str(self) -> str:
        """Get formatted created_at string."""
        return self.searched_at.strftime("%Y-%m-%d %H:%M:%S") if self.searched_at else ""
    
    @property
    def week_day(self) -> Optional[str]:
        """Get the day of the week."""
        if not self.searched_at:
            return None
        return self.searched_at.strftime("%A")
    
    @property
    def hour(self) -> Optional[int]:
        """Get the hour of the search."""
        if not self.searched_at:
            return None
        return self.searched_at.hour
    
    # ============================================================
    # CLASS METHODS
    # ============================================================
    
    @classmethod
    def create(
        cls,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        search_type: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        results_count: Optional[int] = None,
        page: int = 1,
        page_size: int = 10,
        device_type: Optional[str] = None,
        browser: Optional[str] = None,
        os: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referer: Optional[str] = None,
        location: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "SearchHistory":
        """
        Create a new search history record.
        
        Parameters:
        -----------
        query : str
            Search query text
        user_id : Optional[str]
            User identifier
        session_id : Optional[str]
            Session identifier
        search_type : Optional[str]
            Type of search
        filters : Optional[Dict[str, Any]]
            Applied filters
        sort_by : Optional[str]
            Sort order
        results_count : Optional[int]
            Number of results returned
        page : int
            Page number
        page_size : int
            Items per page
        device_type : Optional[str]
            Device type
        browser : Optional[str]
            Browser information
        os : Optional[str]
            Operating system
        ip_address : Optional[str]
            IP address
        user_agent : Optional[str]
            User agent string
        referer : Optional[str]
            Referer URL
        location : Optional[str]
            User location
        metadata : Optional[Dict[str, Any]]
            Additional metadata
        
        Returns:
        --------
        SearchHistory: New search record
        """
        normalized_query = cls.normalize_query(query)
        
        return cls(
            user_id=user_id,
            session_id=session_id,
            query=query.strip(),
            normalized_query=normalized_query,
            search_type=search_type,
            filters=json.dumps(filters) if filters else None,
            sort_by=sort_by,
            results_count=results_count,
            page=page,
            page_size=page_size,
            device_type=device_type,
            browser=browser,
            os=os,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
            location=location,
            meta_data=json.dumps(metadata) if metadata else None,
            searched_at=datetime.now()
        )
    
    # ============================================================
    # INSTANCE METHODS
    # ============================================================
    
    def mark_clicked(self, isbn: str, rank: int) -> None:
        """
        Mark that a result was clicked.
        
        Parameters:
        -----------
        isbn : str
            ISBN of the clicked book
        rank : int
            Position of the clicked book in results
        """
        self.is_clicked = True
        self.selected_isbn = isbn
        self.selected_rank = rank
        if self.searched_at:
            self.time_to_select = (datetime.now() - self.searched_at).total_seconds()
        self.updated_at = func.now()
        logger.info(f"Search result clicked: {isbn} at rank {rank} for query '{self.query[:50]}...'")
    
    def save_search(self) -> None:
        """Mark the search as saved for later."""
        self.is_saved_search = True
        self.updated_at = func.now()
        logger.info(f"Search saved: '{self.query[:50]}...' by user {self.user_id}")
    
    def get_filters(self) -> Dict[str, Any]:
        """
        Get filters as dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Filters dictionary
        """
        if not self.filters:
            return {}
        try:
            return json.loads(self.filters)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in filters for search {self.id}")
            return {}
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata as dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Metadata dictionary
        """
        if not self.metadata:
            return {}
        try:
            return json.loads(self.meta_data)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in metadata for search {self.id}")
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
    
    @staticmethod
    def normalize_query(query: str) -> str:
        """
        Normalize a search query.
        
        Parameters:
        -----------
        query : str
            Search query
        
        Returns:
        --------
        str: Normalized query
        """
        if not query:
            return ""
        # Convert to lowercase and remove extra spaces
        normalized = " ".join(query.lower().strip().split())
        # Remove special characters (keep alphanumeric and spaces)
        import re
        normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
        return normalized
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert search record to dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Search data
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "query": self.query,
            "normalized_query": self.normalized_query,
            "search_type": self.search_type,
            "filters": self.get_filters(),
            "sort_by": self.sort_by,
            "results_count": self.results_count,
            "page": self.page,
            "page_size": self.page_size,
            "selected_isbn": self.selected_isbn,
            "selected_rank": self.selected_rank,
            "time_to_select": self.time_to_select,
            "is_clicked": self.is_clicked,
            "is_saved_search": self.is_saved_search,
            "device_type": self.device_type,
            "browser": self.browser,
            "os": self.os,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "referer": self.referer,
            "location": self.location,
            "metadata": self.get_metadata(),
            "searched_at": self.searched_at.isoformat() if self.searched_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "week_day": self.week_day,
            "hour": self.hour,
            "query_length": self.query_length,
            "query_word_count": self.query_word_count
        }
    
    def to_analytics_dict(self) -> Dict[str, Any]:
        """
        Convert to analytics-friendly dictionary.
        
        Returns:
        --------
        Dict[str, Any]: Analytics data
        """
        return {
            "user_id": self.user_id,
            "query": self.query,
            "search_type": self.search_type,
            "filters": self.get_filters(),
            "sort_by": self.sort_by,
            "results_count": self.results_count,
            "clicked": self.is_clicked,
            "selected_isbn": self.selected_isbn,
            "selected_rank": self.selected_rank,
            "time_to_select": self.time_to_select,
            "device": self.device_type,
            "searched_at": self.searched_at.isoformat() if self.searched_at else None,
            "week_day": self.week_day,
            "hour": self.hour,
            "query_word_count": self.query_word_count
        }
    
    # ============================================================
    # VALIDATION HELPERS
    # ============================================================
    
    @staticmethod
    def validate_query(query: str) -> bool:
        """
        Validate search query.
        
        Parameters:
        -----------
        query : str
            Search query to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        if not query or not query.strip():
            return False
        if len(query.strip()) < 2:
            return False
        if len(query.strip()) > 500:
            return False
        return True
    
    @staticmethod
    def validate_search_type(search_type: str) -> bool:
        """
        Validate search type.
        
        Parameters:
        -----------
        search_type : str
            Search type to validate
        
        Returns:
        --------
        bool: True if valid, False otherwise
        """
        valid_types = ['semantic', 'keyword', 'hybrid', 'filter', 'trending']
        return search_type in valid_types
    
    # ============================================================
    # DUNDER METHODS
    # ============================================================
    
    def __repr__(self) -> str:
        """String representation of the search."""
        return f"<SearchHistory(id={self.id}, user={self.user_id}, query='{self.query[:30]}...', clicked={self.is_clicked})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        status = "clicked" if self.is_clicked else "viewed"
        return f"Search '{self.query[:50]}...' by user {self.user_id}: {status}"


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    import json
    from datetime import datetime
    
    print("=" * 60)
    print("SEARCH HISTORY MODEL TEST")
    print("=" * 60)
    
    # Test 1: Create search
    print("\n📌 Test 1: Create Search")
    search = SearchHistory.create(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        session_id="session_12345",
        query="science fiction space adventure",
        search_type="semantic",
        filters={"category": "Science Fiction", "year_range": {"min": 2000, "max": 2024}},
        sort_by="relevance",
        results_count=42,
        page=1,
        page_size=10,
        device_type="web",
        browser="Chrome 120",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0",
        referer="https://example.com",
        location="New York, US",
        metadata={"search_id": "abc123", "experiment": "v2"}
    )
    
    print(f"✅ Created: {search}")
    print(f"  User: {search.user_id}")
    print(f"  Query: {search.query}")
    print(f"  Type: {search.search_type}")
    print(f"  Filters: {search.get_filters()}")
    print(f"  Results: {search.results_count}")
    
    # Test 2: Mark clicked
    print("\n📌 Test 2: Mark Clicked")
    search.mark_clicked(isbn="0446310786", rank=1)
    print(f"  After click: {search}")
    print(f"  Selected ISBN: {search.selected_isbn}")
    print(f"  Selected Rank: {search.selected_rank}")
    print(f"  Time to select: {search.time_to_select:.2f}s")
    
    # Test 3: Query analysis
    print("\n📌 Test 3: Query Analysis")
    print(f"  Query length: {search.query_length}")
    print(f"  Query word count: {search.query_word_count}")
    print(f"  Normalized query: {search.normalized_query}")
    print(f"  Has filters: {search.has_filters}")
    
    # Test 4: Save search
    print("\n📌 Test 4: Save Search")
    search.save_search()
    print(f"  Is saved: {search.is_saved_search}")
    
    # Test 5: Analytics data
    print("\n📌 Test 5: Analytics Data")
    analytics = search.to_analytics_dict()
    print(f"  Analytics: {json.dumps(analytics, indent=2)}")
    
    # Test 6: Validation
    print("\n📌 Test 6: Validation")
    print(f"  Valid query 'science fiction': {SearchHistory.validate_query('science fiction')}")
    print(f"  Valid query 'a': {SearchHistory.validate_query('a')}")
    print(f"  Valid type 'semantic': {SearchHistory.validate_search_type('semantic')}")
    print(f"  Valid type 'invalid': {SearchHistory.validate_search_type('invalid')}")
    print(f"  Normalize query '  Science  FICTION  ': '{SearchHistory.normalize_query('  Science  FICTION  ')}'")
    
    print("\n✅ All tests completed!")