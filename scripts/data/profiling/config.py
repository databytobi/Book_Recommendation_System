from pathlib import Path

# Get the project root
BASE_DIR = Path(__file__).resolve().parents[3]

# Raw data directory
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

# Update paths to match your actual folder names
BOOK_CROSSING_DIR = RAW_DATA_DIR / "Book-Crossing dataset"  # Note the space
GOODREADS_DIR = RAW_DATA_DIR / "Goodreads dataset"          # Note the space

# File paths
BOOKS_FILE = BOOK_CROSSING_DIR / "Books.csv"
RATINGS_FILE = BOOK_CROSSING_DIR / "Ratings.csv"
USERS_FILE = BOOK_CROSSING_DIR / "Users.csv"
GOODREADS_BOOKS_FILE = GOODREADS_DIR / "books.csv"

# Reports directory
REPORTS_DIR = BASE_DIR / "reports" / "profiling"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Print configuration for verification
if __name__ == "__main__":
    print("Configuration:")
    print(f"Base Directory: {BASE_DIR}")
    print(f"Raw Data Directory: {RAW_DATA_DIR}")
    print(f"Book Crossing Directory: {BOOK_CROSSING_DIR}")
    print(f"Goodreads Directory: {GOODREADS_DIR}")
    print(f"\nBook Files:")
    print(f"  Books: {BOOKS_FILE} - Exists: {BOOKS_FILE.exists()}")
    print(f"  Ratings: {RATINGS_FILE} - Exists: {RATINGS_FILE.exists()}")
    print(f"  Users: {USERS_FILE} - Exists: {USERS_FILE.exists()}")
    print(f"\nGoodreads File:")
    print(f"  Books: {GOODREADS_BOOKS_FILE} - Exists: {GOODREADS_BOOKS_FILE.exists()}")