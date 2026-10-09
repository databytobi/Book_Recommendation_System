"""
Book Model

SQLAlchemy model for the books catalog.
This table stores the searchable book metadata used by the
recommendation engine.

Phase: Book Catalog
"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Text,
    Index,
)
from app.core.database import Base


class Book(Base):
    """
    Master book catalog.
    """

    __tablename__ = "books"

    # ==========================================================
    # PRIMARY KEY
    # ==========================================================

    isbn = Column(
        String(13),
        primary_key=True,
        index=True,
        doc="ISBN-10 or ISBN-13"
    )

    # ==========================================================
    # BOOK METADATA
    # ==========================================================

    title = Column(
        Text,
        nullable=False,
        index=True
    )

    authors = Column(
        Text,
        nullable=True
    )

    genre = Column(
        Text,
        nullable=True,
        index=True
    )

    publisher = Column(
        String(255),
        nullable=True
    )

    publication_year = Column(
        Integer,
        nullable=True
    )

    publication_date = Column(
        String(30),
        nullable=True
    )

    language_code = Column(
        String(10),
        nullable=True,
        index=True
    )

    num_pages = Column(
        Integer,
        nullable=True
    )

    # ==========================================================
    # RATINGS
    # ==========================================================

    average_rating = Column(
        Float,
        default=0.0,
        index=True
    )

    ratings_count = Column(
        Integer,
        default=0,
        index=True
    )

    text_reviews_count = Column(
        Integer,
        default=0
    )

    # ==========================================================
    # IMAGES
    # ==========================================================

    image_url_s = Column(Text)
    image_url_m = Column(Text)
    image_url_l = Column(Text)

    # ==========================================================
    # INDEXES
    # ==========================================================

    __table_args__ = (
        Index("ix_books_title_author", "title"),
        Index("ix_books_rating_popularity", "average_rating", "ratings_count"),
    )

    # ==========================================================
    # SERIALIZER
    # ==========================================================

    def to_dict(self):
        return {
            "isbn": self.isbn,
            "title": self.title,
            "authors": self.authors,
            "genre": self.genre,
            "publisher": self.publisher,
            "publication_year": self.publication_year,
            "language_code": self.language_code,
            "average_rating": self.average_rating,
            "ratings_count": self.ratings_count,
            "image_url_l": self.image_url_l,
        }

    def __repr__(self):
        return f"<Book(isbn='{self.isbn}', title='{self.title[:30]}')>"