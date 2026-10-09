from typing import List, Optional

from pydantic import BaseModel


class BookSearchResult(BaseModel):
    isbn: str
    title: str
    authors: List[str]
    genre: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    image_url: Optional[str] = None
    average_rating: Optional[float] = None
    ratings_count: Optional[int] = None


class BookSearchResponse(BaseModel):
    results: List[BookSearchResult]
    total: int



class BookResponse(BaseModel):
    isbn: str
    title: str
    authors: List[str]
    genre: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    image_url: Optional[str] = None
    average_rating: Optional[float] = None
    ratings_count: Optional[int] = None


class BookListResponse(BaseModel):
    books: List[BookResponse]
    total: int
    page: int
    limit: int