from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Query

from .schemas import (
    BookSearchResponse,
    BookSearchResult,
    BookResponse,
    BookListResponse,
)
from .service import BookService
from app.core.images import normalize_cover_url


router = APIRouter(
    prefix="/books",
    tags=["Books"],
)


@router.get(
    "",
    response_model=BookListResponse,
)
def browse_books(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
):
    books_df, total = BookService.browse_books(page, limit)

    books = []

    for _, row in books_df.iterrows():
        authors = str(row.get("authors") or "")

        books.append(
            BookResponse(
                isbn=str(row["isbn"]),
                title=str(row["title"]),
                authors=[
                    a.strip()
                    for a in authors.split(",")
                    if a.strip()
                ],
                genre=(
                    str(row["genre"])
                    if pd.notna(row.get("genre"))
                    else None
                ),
                publisher=(
                    str(row["publisher"])
                    if pd.notna(row.get("publisher"))
                    else None
                ),
                publication_year=(
                    int(row["publication_year"])
                    if pd.notna(row.get("publication_year"))
                    else None
                ),
                image_url=normalize_cover_url(
                    str(row["image_url_m"])
                    if pd.notna(row.get("image_url_m"))
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
            )
        )

    return BookListResponse(
        books=books,
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/search",
    response_model=BookSearchResponse,
)
def search_books(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=50),
) -> BookSearchResponse:

    df = BookService.search_books(q, limit)

    query = q.strip().lower()

    matches = df[
        df["title_key"].str.contains(query, na=False)
        | df["author_key"].str.contains(query, na=False)
    ].copy()

    matches = matches.sort_values(
        by=["ratings_count", "average_rating"],
        ascending=False,
        na_position="last",
    ).head(limit)

    results = []

    for _, row in matches.iterrows():
        authors = str(row.get("authors") or "")

        results.append(
            BookSearchResult(
                isbn=str(row["isbn"]),
                title=str(row["title"]),
                authors=[
                    author.strip()
                    for author in authors.split(",")
                    if author.strip()
                ],
                genre=(
                    str(row["genre"])
                    if pd.notna(row.get("genre"))
                    else None
                ),
                publisher=(
                    str(row["publisher"])
                    if pd.notna(row.get("publisher"))
                    else None
                ),
                publication_year=(
                    int(row["publication_year"])
                    if pd.notna(row.get("publication_year"))
                    else None
                ),
                image_url=normalize_cover_url(
                    str(row["image_url_m"])
                    if pd.notna(row.get("image_url_m"))
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
            )
        )

    return BookSearchResponse(
        results=results,
        total=len(results),
    )