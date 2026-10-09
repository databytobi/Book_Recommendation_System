"""
Deduplicate books in the master_books dataset.
Removes duplicate ISBN entries while preserving the best quality record.
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from scripts.data.scripts_cleaning.config import PROCESSED_DATA_DIR

def load_master_books():
    """Load the master books dataset."""
    print("=" * 60)
    print("LOADING MASTER BOOKS DATASET")
    print("=" * 60)
    
    books_path = PROCESSED_DATA_DIR / "integrated" / "master_books.parquet"
    
    if not books_path.exists():
        print(f"❌ File not found: {books_path}")
        return None
    
    books = pd.read_parquet(books_path)
    print(f"✅ Loaded {len(books):,} books")
    print(f"   Columns: {list(books.columns)}")
    
    return books

def identify_duplicates(books):
    """Identify duplicate ISBN entries."""
    print("\n" + "=" * 60)
    print("IDENTIFYING DUPLICATES")
    print("=" * 60)
    
    # Check for duplicate ISBNs
    duplicate_mask = books['isbn'].duplicated(keep=False)
    duplicate_count = duplicate_mask.sum()
    
    print(f"Total books: {len(books):,}")
    print(f"Unique ISBNs: {books['isbn'].nunique():,}")
    print(f"Duplicate entries: {duplicate_count:,}")
    
    if duplicate_count > 0:
        # Show examples of duplicates
        duplicates = books[duplicate_mask].sort_values('isbn')
        print(f"\n📋 Duplicate Examples (first 10):")
        
        for isbn in duplicates['isbn'].unique()[:5]:
            dup_rows = duplicates[duplicates['isbn'] == isbn]
            print(f"\n  ISBN: {isbn}")
            for idx, row in dup_rows.iterrows():
                title = row.get('title', 'Unknown')[:50]
                source = "Goodreads" if pd.notna(row.get('average_rating')) else "Book-Crossing"
                rating = row.get('average_rating', 'N/A')
                print(f"    - {title}... (Source: {source}, Rating: {rating})")
    
    return duplicate_mask

def deduplicate_books(books):
    """
    Deduplicate books keeping the best record for each ISBN.
    Priority: Goodreads metadata > Book-Crossing data
    """
    print("\n" + "=" * 60)
    print("DEDUPLICATING BOOKS")
    print("=" * 60)
    
    # Create quality score for each record
    def calculate_quality_score(row):
        """Calculate a quality score for each record."""
        score = 0
        
        # Prefer records with Goodreads metadata
        if pd.notna(row.get('average_rating')):
            score += 100
        
        # Prefer records with more complete information
        if pd.notna(row.get('title')):
            score += 10
        if pd.notna(row.get('authors')):
            score += 10
        if pd.notna(row.get('publisher')):
            score += 5
        if pd.notna(row.get('language_code')):
            score += 5
        if pd.notna(row.get('publication_year')):
            score += 5
        
        # Prefer records with image URLs
        if pd.notna(row.get('image_url_l')):
            score += 10
        elif pd.notna(row.get('image_url_m')):
            score += 5
        
        # Prefer higher rating counts
        if pd.notna(row.get('ratings_count')):
            score += min(row['ratings_count'] / 10000, 20)
        
        return score
    
    # Calculate quality scores
    books['_quality_score'] = books.apply(calculate_quality_score, axis=1)
    
    # Sort by quality score and drop duplicates keeping the best
    books_sorted = books.sort_values('_quality_score', ascending=False)
    books_deduplicated = books_sorted.drop_duplicates(subset=['isbn'], keep='first')
    
    # Remove temporary column
    books_deduplicated = books_deduplicated.drop(columns=['_quality_score'])
    
    removed = len(books) - len(books_deduplicated)
    print(f"✅ Removed {removed:,} duplicate entries")
    print(f"✅ Final unique books: {len(books_deduplicated):,}")
    
    return books_deduplicated

def merge_duplicate_info(books):
    """
    Merge information from duplicate entries to create enriched records.
    Combines ratings, reviews, and metadata from both sources.
    """
    print("\n" + "=" * 60)
    print("MERGING DUPLICATE INFORMATION")
    print("=" * 60)
    
    # Group by ISBN and aggregate information
    merged = books.groupby('isbn').agg({
        'title': lambda x: x.iloc[0] if len(x) > 0 else None,
        'authors': lambda x: x.iloc[0] if len(x) > 0 else None,
        'publisher': lambda x: x.iloc[0] if len(x) > 0 else None,
        'publication_year': lambda x: x.min() if len(x) > 0 else None,
        'average_rating': lambda x: x.max() if len(x) > 0 else None,  # Take highest rating
        'ratings_count': lambda x: x.sum() if len(x) > 0 else 0,  # Sum ratings from all sources
        'language_code': lambda x: x.iloc[0] if len(x) > 0 else None,
        'image_url_l': lambda x: x.iloc[0] if len(x) > 0 else None,
        'image_url_m': lambda x: x.iloc[0] if len(x) > 0 else None,
        'image_url_s': lambda x: x.iloc[0] if len(x) > 0 else None,
    }).reset_index()
    
    print(f"✅ Merged information from duplicate entries")
    print(f"   Final books: {len(merged):,}")
    
    return merged

def export_cleaned_books(books):
    """Export the deduplicated books dataset."""
    print("\n" + "=" * 60)
    print("EXPORTING CLEANED DATASET")
    print("=" * 60)

    # IMPORTANT: this script and scripts/data/integration/deduplicate_catalog.py
    # are ALTERNATIVE strategies — an ISBN-based quality-score dedup here, and a
    # normalized title+author dedup there. Both previously wrote
    # master_books_deduplicated.parquet, so whichever ran last silently won and
    # downstream training read a different dataset depending on execution order.
    #
    # deduplicate_catalog.py owns the canonical output (it also removes
    # title/author duplicates that an ISBN-only pass cannot catch). This script
    # now writes to a clearly-named alternative path so the two cannot collide.
    output_path = PROCESSED_DATA_DIR / "integrated" / "master_books_deduplicated_by_isbn.parquet"
    books.to_parquet(output_path, index=False)
    print(f"✅ Saved to: {output_path}")

    # Also save CSV for inspection
    csv_path = PROCESSED_DATA_DIR / "integrated" / "master_books_deduplicated_by_isbn.csv"
    books.to_csv(csv_path, index=False)
    print(f"✅ CSV saved to: {csv_path}")

    print()
    print("ℹ️  For the canonical training input, run instead:")
    print("     python scripts/data/integration/deduplicate_catalog.py")

    return output_path

def main():
    # Load data
    books = load_master_books()
    if books is None:
        return
    
    # Identify duplicates
    duplicate_mask = identify_duplicates(books)
    
    if duplicate_mask.sum() > 0:
        # Option 1: Simple deduplication (keep best record)
        books_cleaned = deduplicate_books(books)
        
        # Option 2: Merge information from duplicates
        # books_merged = merge_duplicate_info(books)
        
        # Export
        export_cleaned_books(books_cleaned)
        
        print("\n" + "=" * 60)
        print("✅ DEDUPLICATION COMPLETE!")
        print("=" * 60)
        print("\n💡 Next steps:")
        print("   1. For the canonical dataset, run scripts/data/integration/deduplicate_catalog.py")
        print("      (it writes master_books_deduplicated.parquet, which training reads)")
        print("   2. Retrain the popularity recommender with clean data")
    else:
        print("\n✅ No duplicates found! Dataset is clean.")

if __name__ == "__main__":
    main()