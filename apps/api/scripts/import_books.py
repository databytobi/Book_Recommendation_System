"""
Import Books into PostgreSQL

Loads the integrated parquet book catalog into the books table.

Phase: Book Catalog
"""
import pandas as pd
from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.book import Book

from pathlib import Path

PARQUET_PATH = (
    Path(__file__)
    .resolve()
    .parents[1]      # apps/api
    / "ml"
    / "artifacts"
    / "semantic_books.parquet"
)


def load_books():
    print("Reading parquet...")
    df = pd.read_parquet(PARQUET_PATH)

    print(f"Loaded {len(df):,} books")

    db: Session = SessionLocal()

    try:
        db.query(Book).delete()
        db.commit()

        books = []

        for _, row in df.iterrows():
            books.append(
    Book(
        isbn=str(row.get("isbn")),
        title=row.get("title"),
        authors=row.get("authors"),
        genre=row.get("genre"),
        publisher=row.get("publisher"),
        publication_year=None if pd.isna(row.get("publication_year")) else int(row.get("publication_year")),
        publication_date=None if pd.isna(row.get("publication_date")) else str(row.get("publication_date")),
        language_code=None if pd.isna(row.get("language_code")) else row.get("language_code"),
        num_pages=None if pd.isna(row.get("num_pages")) else int(row.get("num_pages")),
        average_rating=0.0 if pd.isna(row.get("average_rating")) else float(row.get("average_rating")),
        ratings_count=0 if pd.isna(row.get("ratings_count")) else int(row.get("ratings_count")),
        text_reviews_count=0 if pd.isna(row.get("text_reviews_count")) else int(row.get("text_reviews_count")),
        image_url_s=None if pd.isna(row.get("image_url_s")) else row.get("image_url_s"),
        image_url_m=None if pd.isna(row.get("image_url_m")) else row.get("image_url_m"),
        image_url_l=None if pd.isna(row.get("image_url_l")) else row.get("image_url_l"),
    )
)

        print("Writing to PostgreSQL...")

        db.bulk_save_objects(books)
        db.commit()

        print(f"Imported {len(books):,} books successfully")

    finally:
        db.close()


if __name__ == "__main__":
    load_books()