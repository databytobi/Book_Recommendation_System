import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.images import normalize_cover_url
from app.models.user import User
from app.models.user_book_interaction import UserBookInteraction
from app.dependencies.auth import get_current_user
from app.api.v1.books.service import BookService

from .schemas import ReadingHistoryResponse, HistoryBook

router = APIRouter(
    prefix="/history",
    tags=["Reading History"],
)


@router.get("", response_model=ReadingHistoryResponse)
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    user_id_str = str(current_user.id)

    # Reading progress lives in Postgres; book metadata does not. The `books`
    # table is empty in this deployment (the catalog is served from parquet),
    # so the previous INNER JOIN on Book silently dropped every interaction
    # and the history list was always empty. Fetch the interactions, then
    # attach metadata from the parquet catalog.
    interactions = (
        db.query(UserBookInteraction)
        .filter(UserBookInteraction.user_id == user_id_str)
        .order_by(UserBookInteraction.updated_at.desc())
        .all()
    )

    if not interactions:
        return ReadingHistoryResponse(
            success=True,
            total=0,
            history=[],
        )

    isbns = [i.isbn for i in interactions]
    catalog = BookService.load_books()
    rows = catalog[catalog["isbn"].isin(isbns)].set_index("isbn")

    history = []

    for interaction in interactions:
        if interaction.isbn not in rows.index:
            # Unknown ISBN in the interaction log; skip it rather than
            # failing the whole response.
            continue

        row = rows.loc[interaction.isbn]
        image_url_m = row.get("image_url_m")

        history.append(
            HistoryBook(
                isbn=interaction.isbn,
                title=str(row["title"]),
                authors=str(row.get("authors") or ""),
                image_url=normalize_cover_url(
                    str(image_url_m)
                    if pd.notna(image_url_m)
                    else None
                ),
                progress=interaction.progress_percentage or 0,
                rating=interaction.rating,
                last_read_at=interaction.last_interaction,
            )
        )

    return ReadingHistoryResponse(
        success=True,
        total=len(history),
        history=history,
    )
