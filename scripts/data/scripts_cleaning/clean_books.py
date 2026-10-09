import sys
from pathlib import Path
import pandas as pd

# Add the project root to Python path (go up 4 levels from this file)
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# Now import using absolute paths from project root
from scripts.data.scripts_cleaning.config import (
    BOOKS_FILE,
    PROCESSED_DATA_DIR
)

from scripts.data.scripts_cleaning.utils import (
    normalize_text,
    normalize_author,
    clean_year
)

OUTPUT_DIR = PROCESSED_DATA_DIR / "books"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_books_dataset():
    print("Loading books dataset...")
    print(f"Looking for file: {BOOKS_FILE}")
    
    if not BOOKS_FILE.exists():
        print(f"❌ File not found: {BOOKS_FILE}")
        print(f"\n📁 Project root: {project_root}")
        print(f"📁 Raw data dir: {Path(__file__).resolve().parents[3] / 'data' / 'raw'}")
        return None
    
    try:
        dataframe = pd.read_csv(
            BOOKS_FILE,
            sep=",",
            encoding="latin-1",
            low_memory=False
        )
        
        print(f"✅ Loaded {len(dataframe):,} rows")
        print(f"   Columns: {list(dataframe.columns)}")
        
        return dataframe
        
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return None

def standardize_column_names(dataframe):
    # Convert column names to lowercase and replace spaces/hyphens with underscores
    dataframe.columns = (
        dataframe.columns
        .str.strip()
        .str.lower()
        .str.replace("-", "_")
        .str.replace(" ", "_")
    )
    
    return dataframe

def clean_books(dataframe):
    print("Cleaning books dataset...")
    
    # Check if required columns exist
    required_columns = ['isbn', 'book_title', 'book_author', 'publisher', 'year_of_publication']
    missing_columns = [col for col in required_columns if col not in dataframe.columns]
    
    if missing_columns:
        print(f"⚠️ Missing columns: {missing_columns}")
        print(f"   Available columns: {list(dataframe.columns)}")
    
    # Normalize text columns (if they exist)
    if "book_title" in dataframe.columns:
        print("  Normalizing book titles...")
        dataframe["book_title"] = dataframe["book_title"].apply(normalize_text)
    
    if "book_author" in dataframe.columns:
        print("  Normalizing authors...")
        dataframe["book_author"] = dataframe["book_author"].apply(normalize_author)
    
    if "publisher" in dataframe.columns:
        print("  Normalizing publishers...")
        dataframe["publisher"] = dataframe["publisher"].apply(normalize_text)
    
    # Clean publication years (if column exists)
    if "year_of_publication" in dataframe.columns:
        print("  Cleaning publication years...")
        original_count = dataframe['year_of_publication'].notna().sum()
        dataframe["year_of_publication"] = dataframe["year_of_publication"].apply(clean_year)
        cleaned_count = dataframe['year_of_publication'].notna().sum()
        print(f"    Valid years: {cleaned_count:,} (from {original_count:,})")
    
    # Drop rows missing ISBN (if column exists)
    if "isbn" in dataframe.columns:
        original_len = len(dataframe)
        dataframe = dataframe.dropna(subset=["isbn"])
        print(f"  Dropped {original_len - len(dataframe):,} rows with missing ISBN")
        
        # Remove duplicate ISBNs
        original_len = len(dataframe)
        dataframe = dataframe.drop_duplicates(subset=["isbn"])
        print(f"  Removed {original_len - len(dataframe):,} duplicate ISBNs")
    
    return dataframe

def export_cleaned_books(dataframe):
    csv_output = OUTPUT_DIR / "books_cleaned.csv"
    parquet_output = OUTPUT_DIR / "books_cleaned.parquet"
    
    print("Exporting cleaned books dataset...")
    
    try:
        dataframe.to_csv(csv_output, index=False)
        print(f"✅ CSV saved to: {csv_output}")
        
        # Only save parquet if pyarrow is installed
        try:
            dataframe.to_parquet(parquet_output, index=False)
            print(f"✅ Parquet saved to: {parquet_output}")
        except ImportError:
            print(f"⚠️ Parquet not saved (install pyarrow: pip install pyarrow)")
        
    except Exception as e:
        print(f"❌ Error exporting: {e}")

def summarize_dataset(dataframe):
    print("\n📊 Dataset Summary")
    print("=" * 50)
    print(f"Rows: {len(dataframe):,}")
    print(f"Columns: {len(dataframe.columns)}")
    
    if "year_of_publication" in dataframe.columns:
        print(f"Missing publication years: {dataframe['year_of_publication'].isna().sum():,}")
    
    if "book_author" in dataframe.columns:
        print(f"Unique authors: {dataframe['book_author'].nunique():,}")
    
    if "publisher" in dataframe.columns:
        print(f"Unique publishers: {dataframe['publisher'].nunique():,}")
    
    if "isbn" in dataframe.columns:
        print(f"Unique ISBNs: {dataframe['isbn'].nunique():,}")

def main():
    print("=" * 50)
    print("Books Data Cleaning Pipeline")
    print("=" * 50)
    
    dataframe = load_books_dataset()
    
    if dataframe is None:
        print("\n❌ Failed to load dataset. Exiting.")
        return
    
    print("\n📝 Standardizing column names...")
    dataframe = standardize_column_names(dataframe)
    
    print("\n🧹 Cleaning data...")
    dataframe = clean_books(dataframe)
    
    summarize_dataset(dataframe)
    
    print("\n💾 Exporting cleaned data...")
    export_cleaned_books(dataframe)
    
    print("\n✅ Books cleaning pipeline completed successfully!")

if __name__ == "__main__":
    main()