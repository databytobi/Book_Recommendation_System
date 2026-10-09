"""
Recommendation Service

Generates personalized book recommendations using
content-based ranking and popularity scoring.

Phase: Recommendation Engine
"""

from typing import List, Dict
from functools import lru_cache
from math import isnan
from pathlib import Path
from types import SimpleNamespace
import faiss
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.genres import add_genre_column
from app.core.images import normalize_cover_url
from app.models.book import Book
from app.models.user_profile import UserProfile
from app.models.user_favorite_book import UserFavoriteBook
from app.models.user_book_interaction import UserBookInteraction
from app.api.v1.recommendations.schemas import (
    RecommendedBook,
    RecommendationResponse,
)
from ml.artifacts.cache import get_artifacts
from app.api.v1.books.service import BookService


def _num_or(value, default):
    """
    Coerce a possibly-missing catalog value to a clean number.

    Pandas represents absent numeric data as NaN (a float). NaN is TRUTHY, so
    the intuitive `value or 0` returns NaN — and `int(NaN)` raises
    `ValueError: cannot convert float NaN to integer`, which the route maps
    to a misleading HTTP 404. Most of the catalog has no rating data at all
    (only ~3.3k of 248k books carry a ratings_count), so any code path that
    can reach an unrated book MUST go through this helper. The same trap is
    documented in app/core/genres.py::_as_text.
    """
    if value is None:
        return default
    try:
        if isinstance(value, float) and isnan(value):
            return default
    except (TypeError, ValueError):
        return default
    return value


class RecommendationService:
    """
    Service responsible for generating personalized recommendations.
    """

    def __init__(self, db: Session):
        self.db = db

        # Load FAISS index and embeddings using cache
        artifacts = get_artifacts()

        self.faiss_index = artifacts["index"]
        self.embeddings = artifacts["embeddings"]
        self.semantic_books = artifacts["books"]

    def _get_profile(self, user_id: int) -> UserProfile:
        """
        Get the user's profile from the database.

        Args:
            user_id: The ID of the user

        Returns:
            UserProfile: The user's profile

        Raises:
            ValueError: If the user profile is not found
        """
        profile = (
            self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        )

        if profile is None:
            raise ValueError("User profile not found")

        return profile

    def _get_favorite_isbns(self, user_id: int) -> List[str]:
        """
        Get the ISBNs of the user's favorite books.

        Args:
            user_id: The ID of the user

        Returns:
            List[str]: A list of ISBNs of the user's favorite books
        """
        books = (
            self.db.query(UserFavoriteBook)
            .filter(UserFavoriteBook.user_id == user_id)
            .all()
        )

        return [book.isbn for book in books]

    # NOTE ON GENRE SCORING
    # ---------------------
    # A `_genre_score()` helper previously contributed 30% of the final score
    # by matching `Book.genre` against the user's favourite genres. The
    # ingested catalog (Book-Crossing + Goodreads) has NO genre column — see
    # docs/PROJECT_DOCUMENTATION.md §11 — so `book.genre` is always NULL and
    # the term was a constant 0.0 for every candidate. It consumed 30% of the
    # weight budget while contributing nothing, and it produced a misleading
    # "Matches your favorite genres" reason that could never actually fire.
    #
    # The signal has been removed and its weight redistributed
    # proportionally across the remaining signals, preserving their original
    # ratios (0.25 : 0.15 : 0.20 relative to their 0.60 total).

    def _author_score(
        self,
        book: Book,
        favorite_authors: List[str],
    ) -> float:
        """
        Score a book based on favorite author overlap.

        Args:
            book: The book to score
            favorite_authors: List of the user's favorite authors

        Returns:
            float: A score between 0.0 and 1.0 representing author match
        """
        if not favorite_authors:
            return 0.0

        if not book.authors:
            return 0.0

        book_authors = {a.strip().lower() for a in book.authors.split(",")}

        favorites = {a.lower() for a in favorite_authors}

        matches = len(book_authors.intersection(favorites))

        return matches / max(len(book_authors), 1)

    def _popularity_score(self, book: Book) -> float:
        """
        Compute a normalized popularity score.

        Uses both average rating and ratings count.
        Returns a value between 0.0 and 1.0.
        """
        rating = min((book.average_rating or 0) / 5.0, 1.0)
        count = min((book.ratings_count or 0) / 10000, 1.0)

        return (rating * 0.7) + (count * 0.3)

    def _reading_style_bonus(
        self,
        book: Book,
        reading_style: str,
    ) -> float:
        """
        Small bonus based on the user's reading style.
        """
        pages = book.num_pages or 300

        if reading_style == "quick":
            return 1.0 if pages <= 250 else 0.2

        if reading_style == "deep":
            return 1.0 if pages >= 450 else 0.3

        if reading_style == "explorer":
            return 1.0 if (book.ratings_count or 0) < 500 else 0.4

        # balanced
        return 0.6

    def _semantic_candidates(
        self,
        favorite_isbns: List[str],
        top_k: int = 200,
    ) -> List[str]:
        """
        Retrieve semantically similar books from FAISS.
        """
        if not favorite_isbns:
            return []

        indices = []

        for isbn in favorite_isbns:
            match = self.semantic_books.index[self.semantic_books["isbn"] == isbn]

            if len(match):
                indices.append(match[0])

        if not indices:
            return []

        query = np.mean(
            self.embeddings[indices],
            axis=0,
        ).astype("float32")

        distances, neighbors = self.faiss_index.search(
            query.reshape(1, -1),
            top_k,
        )

        results = self.semantic_books.iloc[neighbors[0]]["isbn"].tolist()

        return results

    def _collaborative_scores(self, user_id: int) -> Dict[str, float]:
        """
        Compute collaborative scores once for all candidate books.
        Returns: {isbn: score}
        """
        # Books the current user interacted with
        my_books = [
            row[0]
            for row in self.db.query(UserBookInteraction.isbn)
            .filter(UserBookInteraction.user_id == str(user_id))
            .all()
        ]

        if not my_books:
            return {}

        # Similar users
        similar_users = [
            row[0]
            for row in self.db.query(UserBookInteraction.user_id)
            .filter(
                UserBookInteraction.isbn.in_(my_books),
                UserBookInteraction.user_id != str(user_id),
            )
            .distinct()
            .all()
        ]

        if not similar_users:
            return {}

        # All books read by similar users (ONE query)
        interactions = (
            self.db.query(UserBookInteraction.isbn)
            .filter(UserBookInteraction.user_id.in_(similar_users))
            .all()
        )

        counts: Dict[str, int] = {}

        for row in interactions:
            isbn = row[0]
            counts[isbn] = counts.get(isbn, 0) + 1

        return {isbn: min(count / 10, 1.0) for isbn, count in counts.items()}

    def _catalog(self) -> pd.DataFrame:
        """
        The browsable book catalog.

        This deliberately reuses `BookService`, which reads
        `ml/artifacts/semantic_books.parquet` (248,176 rows) and is the same
        source the browse and search endpoints serve. The `books` DB table is
        empty in this deployment -- all catalog data lives in parquet -- so
        querying `Book` here produced zero candidates and the endpoint always
        answered `total: 0`. Reusing the one loaded/cached dataframe also keeps
        browse, search and recommendations consistent.
        """
        return BookService.load_books()

    @staticmethod
    def _row_authors(row) -> str:
        """Catalog authors are a comma-joined string; normalise to that form."""
        authors = row.get("authors")
        if authors is None or (isinstance(authors, float) and pd.isna(authors)):
            return ""
        if isinstance(authors, (list, tuple)):
            return ", ".join(str(a) for a in authors)
        return str(authors)

    def _author_score_row(self, row, favorite_authors: List[str]) -> float:
        """Author-overlap score for a catalog row (parquet, not ORM)."""
        if not favorite_authors:
            return 0.0

        authors = self._row_authors(row)
        if not authors:
            return 0.0

        book_authors = {a.strip().lower() for a in authors.split(",") if a.strip()}
        favorites = {a.lower() for a in favorite_authors}

        matches = len(book_authors.intersection(favorites))

        return matches / max(len(book_authors), 1)

    @staticmethod
    def _popularity_score_values(average_rating, ratings_count) -> float:
        rating = min(float(_num_or(average_rating, 0)) / 5.0, 1.0)
        count = min(float(_num_or(ratings_count, 0)) / 10000, 1.0)

        return (rating * 0.7) + (count * 0.3)

    @staticmethod
    def _reading_style_bonus_values(reading_style: str) -> float:
        """
        Reading-style bonus.

        The ORM version also looked at `book.num_pages`, but the catalog has no
        page-count column at all, so the previous `book.num_pages or 300`
        always evaluated to the 300 default -- meaning every book scored
        identically and the signal was effectively a constant. Rather than
        preserve a fake per-book comparison, the bonus is now honestly a
        per-style constant and the docstring says so.
        """
        if reading_style == "quick":
            return 0.5
        if reading_style == "deep":
            return 0.5
        if reading_style == "explorer":
            return 0.6

        # balanced
        return 0.6

    def get_recommendations(
        self,
        user_id: int,
        limit: int = 20,
    ) -> RecommendationResponse:
        """
        Generate personalized recommendations using hybrid scoring.

        Candidates come from the parquet catalog. When the user has favorites
        we restrict to FAISS semantic neighbours of those favorites; otherwise
        (for example a brand-new account that has just registered) we fall back
        to the strongest catalog books by rating volume, so the page is never
        empty. Previously an empty candidate set returned `total: 0` and the
        UI showed "No recommendations yet".
        """
        profile = self._get_profile(user_id)

        collaborative_scores = self._collaborative_scores(user_id)

        # `favorite_genres` is intentionally not read: genre is derived
        # heuristically and is unknown for ~75% of the catalog, so scoring on
        # it would re-introduce the always-zero term documented above.
        favorite_authors = profile.get_favorite_authors()
        favorite_isbns = self._get_favorite_isbns(user_id)

        catalog = self._catalog()

        candidate_isbns = self._semantic_candidates(
            favorite_isbns,
            top_k=250,
        )

        if candidate_isbns:
            candidates = catalog[catalog["isbn"].isin(candidate_isbns)]
            excluded = set(favorite_isbns)
        else:
            # No favorites (or no semantic match): fall back to the most-rated
            # catalog books so a cold-start user still gets recommendations.
            candidates = catalog
            excluded = set(favorite_isbns)

        if excluded:
            candidates = candidates[~candidates["isbn"].isin(excluded)]

        candidates = candidates.sort_values(
            by=["ratings_count", "average_rating"],
            ascending=False,
            na_position="last",
        ).head(500)

        recommendations = []

        for row in candidates.to_dict("records"):
            author_score = self._author_score_row(row, favorite_authors)

            popularity_score = self._popularity_score_values(
                row.get("average_rating"),
                row.get("ratings_count"),
            )

            style_bonus = self._reading_style_bonus_values(
                profile.reading_style,
            )

            collaborative_score = collaborative_scores.get(row["isbn"], 0.0)

            # Weights renormalised after removing the always-zero genre term.
            # The previous ratios were author 0.25 : popularity 0.15 :
            # style 0.10 : collaborative 0.20 (total 0.60). Each is scaled by
            # 1/0.60 so the four remaining signals sum to exactly 1.0.
            final_score = (
                (author_score * 0.4167)
                + (popularity_score * 0.2500)
                + (style_bonus * 0.1667)
                + (collaborative_score * 0.1666)
            )

            # Reason selection no longer references genre, which could never
            # contribute. Ordered by the strength of evidence behind the score.
            if collaborative_score >= 0.6:
                reason = "Readers with similar taste enjoyed this"
            elif author_score > 0:
                reason = "From one of your favorite authors"
            elif not favorite_isbns:
                reason = "Popular among readers"
            elif style_bonus >= 1:
                reason = "Fits your reading style"
            else:
                reason = "Similar to books you enjoyed"

            publication_year = row.get("publication_year")

            recommendations.append(
                RecommendedBook(
                    isbn=str(row["isbn"]),
                    title=str(row["title"]),
                    # `authors` is typed as Optional[str] in the schema and the
                    # frontend consumes it as a string (dashboard.service.ts
                    # assigns it straight to author.name). Pass the catalog's
                    # comma-joined form unchanged rather than a list.
                    authors=self._row_authors(row),
                    genre=(
                        str(row["genre"])
                        if row.get("genre") is not None
                        and not (isinstance(row.get("genre"), float) and pd.isna(row["genre"]))
                        else None
                    ),
                    publisher=(
                        str(row["publisher"])
                        if row.get("publisher") is not None
                        and not (isinstance(row.get("publisher"), float) and pd.isna(row["publisher"]))
                        else None
                    ),
                    publication_year=(
                        int(publication_year)
                        if publication_year is not None
                        and not (isinstance(publication_year, float) and pd.isna(publication_year))
                        else None
                    ),
                    average_rating=float(_num_or(row.get("average_rating"), 0)),
                    ratings_count=int(_num_or(row.get("ratings_count"), 0)),
                    image_url=normalize_cover_url(
                        str(row["image_url_l"])
                        if row.get("image_url_l") is not None
                        and not (isinstance(row.get("image_url_l"), float) and pd.isna(row["image_url_l"]))
                        else (
                            str(row["image_url_m"])
                            if row.get("image_url_m") is not None
                            and not (isinstance(row.get("image_url_m"), float) and pd.isna(row["image_url_m"]))
                            else None
                        )
                    ),
                    recommendation_score=round(final_score, 3),
                    recommendation_reason=reason,
                )
            )

        recommendations.sort(
            key=lambda x: x.recommendation_score,
            reverse=True,
        )

        return RecommendationResponse(
            success=True,
            total=min(limit, len(recommendations)),
            recommendations=recommendations[:limit],
            generated_from="hybrid",
        )
