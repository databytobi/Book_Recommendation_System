from pathlib import Path

# Get the base directory (project root)
# This file is at: project/scripts/data/scripts_cleaning/config.py
# Go up 4 levels to reach project root
BASE_DIR = Path(__file__).resolve().parents[3]  # Changed from 4 to 3

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Use the exact folder names from your system
BOOK_CROSSING_DIR = RAW_DATA_DIR / "Book-Crossing dataset"  # Note the space
GOODREADS_DIR = RAW_DATA_DIR / "Goodreads dataset"          # Note the space

# File paths
BOOKS_FILE = BOOK_CROSSING_DIR / "Books.csv"
RATINGS_FILE = BOOK_CROSSING_DIR / "Ratings.csv"
USERS_FILE = BOOK_CROSSING_DIR / "Users.csv"
GOODREADS_BOOKS_FILE = GOODREADS_DIR / "books.csv"

# Debug: Print paths to verify
if __name__ == "__main__":
    print(f"Current file: {Path(__file__).resolve()}")
    print(f"Base Directory: {BASE_DIR}")
    print(f"Raw Data Directory: {RAW_DATA_DIR}")
    print(f"Books file: {BOOKS_FILE}")
    print(f"Books file exists: {BOOKS_FILE.exists()}")