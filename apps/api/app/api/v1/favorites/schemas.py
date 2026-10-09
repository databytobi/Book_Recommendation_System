from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class FavoriteBook(BaseModel):
    isbn: str
    title: str
    authors: str
    image_url: Optional[str] = None
    average_rating: Optional[float] = None
    ratings_count: Optional[int] = None
    added_at: datetime


class FavoriteListResponse(BaseModel):
    success: bool
    total: int
    favorites: List[FavoriteBook]


class FavoriteResponse(BaseModel):
    success: bool
    message: str