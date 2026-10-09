from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "integrated"
    / "master_books.parquet"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "integrated"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "master_books_deduplicated.parquet"
)


def load_books():

    print("=" * 60)
    print("LOADING MASTER BOOKS")
    print("=" * 60)

    books = pd.read_parquet(INPUT_FILE)

    print(f"Loaded: {len(books):,} books")

    return books


def normalize_text(text):

    if pd.isna(text):
        return ""

    return (
        str(text)
        .lower()
        .strip()
    )


def create_dedupe_keys(books):

    print("\nCreating deduplication keys...")

    books["title_key"] = (
        books["title"]
        .fillna("")
        .map(normalize_text)
    )

    books["author_key"] = (
        books["authors"]
        .fillna("")
        .map(normalize_text)
    )

    books["dedupe_key"] = (
        books["title_key"]
        + "|"
        + books["author_key"]
    )

    return books


def remove_duplicate_isbns(books):

    before = len(books)

    books = books.drop_duplicates(
        subset=["isbn"],
        keep="first"
    )

    removed = before - len(books)

    print(
        f"Duplicate ISBNs removed: "
        f"{removed:,}"
    )

    return books


def remove_duplicate_books(books):

    before = len(books)

    books = books.drop_duplicates(
        subset=["dedupe_key"],
        keep="first"
    )

    removed = before - len(books)

    print(
        f"Duplicate title-author pairs removed: "
        f"{removed:,}"
    )

    return books


def export_dataset(books):

    books.to_parquet(
        OUTPUT_FILE,
        index=False
    )

    csv_file = (
        OUTPUT_DIR
        / "master_books_deduplicated.csv"
    )

    books.to_csv(
        csv_file,
        index=False
    )

    print("\nExport completed.")
    print(f"Parquet: {OUTPUT_FILE}")
    print(f"CSV: {csv_file}")


def summary(before, after):

    print("\n" + "=" * 60)
    print("DEDUPLICATION SUMMARY")
    print("=" * 60)

    print(f"Original books: {before:,}")
    print(f"Final books:    {after:,}")
    print(
        f"Removed:        "
        f"{before-after:,}"
    )

    reduction = (
        (before-after)
        / before
    ) * 100

    print(
        f"Reduction:      "
        f"{reduction:.2f}%"
    )


def main():

    books = load_books()

    original_count = len(books)

    books = create_dedupe_keys(
        books
    )

    books = remove_duplicate_isbns(
        books
    )

    books = remove_duplicate_books(
        books
    )

    final_count = len(books)

    export_dataset(books)

    summary(
        original_count,
        final_count
    )


if __name__ == "__main__":
    main()