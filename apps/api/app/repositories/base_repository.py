
from typing import Optional, List, TypeVar, Generic
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseRepository(Generic[T]):

    def __init__(self, db: Session):
        self.db = db
        self.model = None

    def create(self, obj: T) -> T:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_id(self, id: int) -> Optional[T]:
        if self.model is None:
            raise ValueError("Model not set")
        return self.db.query(self.model).filter(self.model.id == id).first()

    def update(self, obj: T) -> T:
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: int, hard_delete: bool = False) -> bool:
        obj = self.get_by_id(id)
        if not obj:
            return False

        if hard_delete:
            self.db.delete(obj)
        else:
            if hasattr(obj, 'is_active'):
                obj.is_active = False

        self.db.commit()
        return True

    def list(
        self,
        skip: int = 0,
        limit: int = 50,
        include_inactive: bool = False,
        **filters
    ) -> List[T]:

        if self.model is None:
            raise ValueError("Model not set")

        query = self.db.query(self.model)

        if not include_inactive and hasattr(self.model, 'is_active'):
            query = query.filter(self.model.is_active.is_(True))

        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)

        return query.offset(skip).limit(limit).all()

    def count(self, include_inactive: bool = False, **filters) -> int:
        if self.model is None:
            raise ValueError("Model not set")

        query = self.db.query(self.model)

        if not include_inactive and hasattr(self.model, 'is_active'):
            query = query.filter(self.model.is_active.is_(True))

        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)

        return query.count()

    def exists(self, id: int) -> bool:
        return self.get_by_id(id) is not None
