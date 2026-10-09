
from pathlib import Path
from functools import lru_cache
import pandas as pd

from app.core.genres import add_genre_column


ARTIFACT_PATH = (
    Path(__file__).resolve().parents[4]
    / "ml"
    / "artifacts"
    / "semantic_books.parquet"
)


class BookService:
    """
    Service layer for book browsing and search.
    Reads the semantic_books.parquet artifact.
    """

    @staticmethod
    @lru_cache(maxsize=1)
    def load_books() -> pd.DataFrame:
        df = pd.read_parquet(ARTIFACT_PATH)

        df["title_key"] = (
            df["title"]
            .fillna("")
            .astype(str)
            .str.lower()
        )

        df["author_key"] = (
            df["authors"]
            .fillna("")
            .astype(str)
            .str.lower()
        )

        # The source parquet has no `genre` column at all, so the API used to
        # return `genre: null` for every book. Derive it from title/author/
        # publisher signals instead (see app/core/genres.py for the heuristic
        # and its coverage limits). Computed once here and cached with the
        # dataframe via lru_cache.
        df = add_genre_column(df)

        return df

    @classmethod
    def browse_books(cls, page: int = 1, limit: int = 20):
        df = cls.load_books()

        start = (page - 1) * limit
        end = start + limit

        books = (
            df.sort_values(
                by=["ratings_count", "average_rating"],
                ascending=False,
                na_position="last",
            )
            .iloc[start:end]
        )

        return books, len(df)

    @classmethod
    def search_books(cls, query: str, limit: int = 20):
        df = cls.load_books()

        q = query.strip().lower()

        matches = df[
            df["title_key"].str.contains(q, na=False)
            | df["author_key"].str.contains(q, na=False)
        ]

        matches = matches.sort_values(
            by=["ratings_count", "average_rating"],
            ascending=False,
            na_position="last",
        ).head(limit)

        return matches