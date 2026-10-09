from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class HistoryBook(BaseModel):
    isbn: str
    title: str
    authors: str
    image_url: Optional[str] = None
    progress: int
    rating: Optional[int] = None
    last_read_at: datetime


class ReadingHistoryResponse(BaseModel):
    success: bool
    total: int
    history: List[HistoryBook]