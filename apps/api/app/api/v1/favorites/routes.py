import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


from app.core.database import get_db
from app.core.images import normalize_cover_url
from app.models.user import User
from app.models.user_favorite_book import UserFavoriteBook
from app.dependencies.auth import get_current_user
from app.api.v1.books.service import BookService

from .schemas import (
    FavoriteBook,
    FavoriteListResponse,
    FavoriteResponse,
)


router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"],
)

# ---------------------------------------------------------------------------
# Data sources
# ---------------------------------------------------------------------------
#
# User favourites live in Postgres, but book metadata does NOT: the `books`
# table is empty in this deployment and the catalog is read from parquet
# (see app/api/v1/books/service.py). The previous version of these routes
# validated the ISBN against `Book` and joined `Book` for display data, so
# every favourite action failed with 404 "Book not found" and the list was
# always empty. Both now consult the parquet catalog instead.


def _catalog_lookup(isbn: str):
    """Return the catalog row for one ISBN, or None if it is unknown."""
    catalog = BookService.load_books()

    match = catalog[catalog["isbn"] == isbn]

    if match.empty:
        return None

    return match.iloc[0]


@router.get("", response_model=FavoriteListResponse)
def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    favorites = (
        db.query(UserFavoriteBook)
        .filter(
            UserFavoriteBook.user_id == current_user.id,
            UserFavoriteBook.is_deleted == False,
        )
        .order_by(UserFavoriteBook.added_at.desc())
        .all()
    )

    if not favorites:
        return FavoriteListResponse(success=True, total=0, favorites=[])

    # One catalog filter for the whole batch; preserves the favourite order.
    isbns = [fav.isbn for fav in favorites]
    catalog = BookService.load_books()
    rows = catalog[catalog["isbn"].isin(isbns)].set_index("isbn")

    items = []

    for fav in favorites:
        if fav.isbn not in rows.index:
            # Book disappeared from the catalog; keep the row count honest
            # by skipping it rather than crashing the whole list.
            continue

        row = rows.loc[fav.isbn]

        image_url_m = row.get("image_url_m")

        items.append(
            FavoriteBook(
                isbn=fav.isbn,
                title=str(row["title"]),
                authors=str(row.get("authors") or ""),
                image_url=normalize_cover_url(
                    str(image_url_m)
                    if pd.notna(image_url_m)
                    else None
                ),
                average_rating=(
                    float(row["average_rating"])
                    if pd.notna(row.get("average_rating"))
                    else None
                ),
                ratings_count=(
                    int(row["ratings_count"])
                    if pd.notna(row.get("ratings_count"))
                    else None
                ),
                added_at=fav.added_at,
            )
        )

    return FavoriteListResponse(
        success=True,
        total=len(items),
        favorites=items,
    )


@router.post("/{isbn}", response_model=FavoriteResponse)
def add_favorite(
    isbn: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # The `books` table is empty (catalog data lives in parquet), so a DB
    # lookup here always failed with 404 and the UI's favourite button
    # silently did nothing. Validate against the parquet catalog instead.
    if _catalog_lookup(isbn) is None:
        raise HTTPException(status_code=404, detail="Book not found")

    exists = (
        db.query(UserFavoriteBook)
        .filter(
            UserFavoriteBook.user_id == current_user.id,
            UserFavoriteBook.isbn == isbn,
            UserFavoriteBook.is_deleted == False,
        )
        .first()
    )

    if exists:
        return FavoriteResponse(
            success=True,
            message="Already in favorites",
        )

    favorite = UserFavoriteBook.create(
        user_id=current_user.id,
        isbn=isbn,
    )

    db.add(favorite)
    db.commit()

    return FavoriteResponse(
        success=True,
        message="Book added to favorites",
    )


@router.delete("/{isbn}", response_model=FavoriteResponse)
def remove_favorite(
    isbn: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    favorite = (
        db.query(UserFavoriteBook)
        .filter(
            UserFavoriteBook.user_id == current_user.id,
            UserFavoriteBook.isbn == isbn,
            UserFavoriteBook.is_deleted == False,
        )
        .first()
    )

    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    favorite.soft_delete()
    db.commit()

    return FavoriteResponse(
        success=True,
        message="Removed from favorites",
    )
