import pandas as pd
from pathlib import Path

# Fix: Use __file__ (double underscores) not **file**
BASE_DIR = Path(__file__).resolve().parents[3]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR = BASE_DIR / "data" / "processed" / "integrated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_datasets():
    print("=" * 60)
    print("LOADING CLEANED DATASETS")
    print("=" * 60)
    
    books = pd.read_parquet(
        PROCESSED_DIR / "books" / "books_cleaned.parquet"
    )
    
    ratings = pd.read_parquet(
        PROCESSED_DIR / "ratings" / "ratings_cleaned.parquet"
    )
    
    users = pd.read_parquet(
        PROCESSED_DIR / "users" / "users_cleaned.parquet"
    )
    
    goodreads = pd.read_parquet(
        PROCESSED_DIR / "goodreads" / "goodreads_cleaned.parquet"
    )
    
    print(f"Books: {len(books):,}")
    print(f"Ratings: {len(ratings):,}")
    print(f"Users: {len(users):,}")
    print(f"Goodreads: {len(goodreads):,}")
    
    # NOTE: `users` is loaded here for a row-count sanity check only. It is NOT
    # joined into master_books, which is a book-level table — joining users (one
    # row per reader) into it would fan out every book per reader and be a
    # category error. The user dimension is validated and carried forward
    # separately by scripts/data/integration/schema_validator.py, and is joined
    # to ratings at database-import time.
    return books, ratings, users, goodreads

def clean_isbn_column(dataframe, column):
    if column not in dataframe.columns:
        print(f"⚠️ Warning: Column '{column}' not found in dataframe")
        return dataframe
    
    dataframe[column] = (
        dataframe[column]
        .astype(str)
        .str.strip()
        .str.replace('"', "")
        .str.replace("'", "")
        .str.replace('-', '')
        .str.upper()
    )
    # Replace 'nan' strings with actual NaN
    dataframe[column] = dataframe[column].replace('nan', None)
    
    return dataframe

def standardize_isbns(books, ratings, goodreads):
    print("\n📚 Standardizing ISBNs...")
    
    books = clean_isbn_column(books, "isbn")
    ratings = clean_isbn_column(ratings, "isbn")
    goodreads = clean_isbn_column(goodreads, "isbn")
    
    return books, ratings, goodreads

def merge_book_metadata(books, goodreads):
    print("\n🔗 Merging book metadata...")
    
    # Ensure ISBN columns are string type for merging
    books['isbn'] = books['isbn'].astype(str)
    goodreads['isbn'] = goodreads['isbn'].astype(str)
    
    # Merge on ISBN
    merged = books.merge(
        goodreads,
        on="isbn",
        how="left",
        suffixes=('_bx', '_gr')
    )
    
    print(f"Merged rows: {len(merged):,}")
    
    goodreads_matches = merged["average_rating"].notna().sum()
    print(f"Books enriched with Goodreads metadata: {goodreads_matches:,}")
    
    return merged

def identify_orphan_ratings(ratings, books):
    print("\n🔍 Identifying orphan ratings...")
    
    # Ensure ISBN columns are string type
    ratings['isbn'] = ratings['isbn'].astype(str)
    books['isbn'] = books['isbn'].astype(str)
    
    valid_isbns = set(books["isbn"].dropna())
    orphan_ratings = ratings[~ratings["isbn"].isin(valid_isbns)]
    
    print(f"Orphan interactions: {len(orphan_ratings):,}")
    
    return orphan_ratings

def create_master_books_dataset(merged):
    print("\n🧠 Creating master books dataset...")
    
    master = pd.DataFrame()
    
    # ISBN
    master["isbn"] = merged["isbn"]
    
    # Title - prefer Goodreads if available
    if "title" in merged.columns:
        master["title"] = merged["title"].fillna(merged.get("book_title", ""))
    else:
        master["title"] = merged.get("book_title", "")
    
    # Authors - prefer Goodreads if available
    if "authors" in merged.columns:
        master["authors"] = merged["authors"].fillna(merged.get("book_author", ""))
    else:
        master["authors"] = merged.get("book_author", "")
    
    # Publisher
    if "publisher_bx" in merged.columns:
        master["publisher"] = merged["publisher_bx"].fillna(merged.get("publisher_gr", ""))
    elif "publisher" in merged.columns:
        master["publisher"] = merged["publisher"]
    else:
        master["publisher"] = None
    
    # Publication year
    master["publication_year"] = merged.get("year_of_publication", None)
    
    # Goodreads metadata
    gr_columns = [
        "average_rating",
        "ratings_count",
        "text_reviews_count",
        "language_code",
        "publication_date"
    ]
    
    for column in gr_columns:
        if column in merged.columns:
            master[column] = merged[column]
    
    # Image URLs
    image_columns = ["image_url_s", "image_url_m", "image_url_l"]
    for image_col in image_columns:
        if image_col in merged.columns:
            master[image_col] = merged[image_col]
    
    # Add useful derived columns
    if "average_rating" in master.columns:
        # Rating category
        master["rating_category"] = pd.cut(
            master["average_rating"],
            bins=[0, 2, 3, 4, 5],
            labels=["Poor", "Fair", "Good", "Excellent"],
            include_lowest=True
        )
    
    if "language_code" in master.columns:
        # Language group
        master["is_english"] = master["language_code"] == "eng"
    
    print(f"Master dataset rows: {len(master):,}")
    
    return master

def export_datasets(master_books, orphan_ratings):
    print("\n💾 Exporting integrated datasets...")
    
    master_path = OUTPUT_DIR / "master_books.parquet"
    orphan_path = OUTPUT_DIR / "orphan_ratings.parquet"
    
    master_books.to_parquet(master_path, index=False)
    print(f"✅ Master books dataset saved: {master_path}")
    
    orphan_ratings.to_parquet(orphan_path, index=False)
    print(f"✅ Orphan ratings dataset saved: {orphan_path}")
    
    # Also export CSV versions for compatibility
    master_csv = OUTPUT_DIR / "master_books.csv"
    orphan_csv = OUTPUT_DIR / "orphan_ratings.csv"
    
    master_books.to_csv(master_csv, index=False)
    print(f"✅ Master books CSV saved: {master_csv}")
    
    if len(orphan_ratings) > 0:
        orphan_ratings.to_csv(orphan_csv, index=False)
        print(f"✅ Orphan ratings CSV saved: {orphan_csv}")

def summarize_integration(master_books, orphan_ratings):
    print("\n" + "=" * 60)
    print("INTEGRATION SUMMARY")
    print("=" * 60)
    
    print(f"Master books dataset: {len(master_books):,}")
    print(f"Books with Goodreads ratings: {master_books['average_rating'].notna().sum():,}")
    
    if "language_code" in master_books.columns:
        print(f"Books with language metadata: {master_books['language_code'].notna().sum():,}")
    
    if "rating_category" in master_books.columns:
        print(f"\nRating distribution:")
        rating_dist = master_books['rating_category'].value_counts()
        for category, count in rating_dist.items():
            pct = (count / len(master_books)) * 100
            print(f"  {category}: {count:,} ({pct:.1f}%)")
    
    print(f"\nOrphan ratings: {len(orphan_ratings):,}")
    
    total_ratings = 1_149_780  # From earlier reports
    coverage = (1 - (len(orphan_ratings) / total_ratings)) * 100
    print(f"Interaction coverage: {coverage:.2f}%")

def main():
    # Load datasets
    books, ratings, users, goodreads = load_datasets()
    
    # `users` is intentionally not merged into the book-level master table.
    # See the note in load_datasets().
    _ = users
    
    # Standardize ISBNs
    books, ratings, goodreads = standardize_isbns(books, ratings, goodreads)
    
    # Merge book metadata
    merged = merge_book_metadata(books, goodreads)
    
    # Identify orphan ratings
    orphan_ratings = identify_orphan_ratings(ratings, books)
    
    # Create master books dataset
    master_books = create_master_books_dataset(merged)
    
    # Summarize integration
    summarize_integration(master_books, orphan_ratings)
    
    # Export datasets
    export_datasets(master_books, orphan_ratings)
    
    print("\n✅ Dataset integration completed successfully!")

if __name__ == "__main__":
    main()