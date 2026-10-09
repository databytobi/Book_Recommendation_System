import sys
from pathlib import Path
import pandas as pd

# Add the project root to Python path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# Now import using absolute paths from project root
from scripts.data.scripts_cleaning.config import (
    RATINGS_FILE,
    PROCESSED_DATA_DIR
)

OUTPUT_DIR = PROCESSED_DATA_DIR / "ratings"
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

def load_ratings_dataset():
    print("Loading ratings dataset...")
    print(f"Looking for file: {RATINGS_FILE}")
    
    if not RATINGS_FILE.exists():
        print(f"❌ File not found: {RATINGS_FILE}")
        return None
    
    try:
        dataframe = pd.read_csv(
            RATINGS_FILE,
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
    dataframe.columns = (
        dataframe.columns
        .str.strip()
        .str.lower()
        .str.replace("-", "_")
        .str.replace(" ", "_")
    )
    
    return dataframe

def clean_ratings(dataframe):
    print("Cleaning ratings dataset...")
    
    # Check if required columns exist
    required_columns = ['user_id', 'isbn', 'book_rating']
    missing_columns = [col for col in required_columns if col not in dataframe.columns]
    
    if missing_columns:
        print(f"⚠️ Missing columns: {missing_columns}")
        print(f"   Available columns: {list(dataframe.columns)}")
        return dataframe
    
    # Remove rows missing user_id or isbn
    before = len(dataframe)
    dataframe = dataframe.dropna(subset=["user_id", "isbn"])
    print(f"  Dropped {before - len(dataframe):,} rows with missing user_id or isbn")
    
    # Remove duplicate interactions
    before = len(dataframe)
    dataframe = dataframe.drop_duplicates(subset=["user_id", "isbn"])
    removed = before - len(dataframe)
    print(f"  Removed {removed:,} duplicate interactions")
    
    return dataframe

def split_explicit_implicit(dataframe):
    print("Splitting explicit and implicit ratings...")
    
    explicit = dataframe[
        dataframe["book_rating"] > 0
    ].copy()
    
    implicit = dataframe[
        dataframe["book_rating"] == 0
    ].copy()
    
    print(f"  Explicit ratings: {len(explicit):,}")
    print(f"  Implicit interactions: {len(implicit):,}")
    
    return explicit, implicit

def export_dataset(dataframe, output_path):
    try:
        dataframe.to_csv(
            output_path.with_suffix(".csv"),
            index=False
        )
        print(f"  ✅ CSV saved to: {output_path.with_suffix('.csv')}")
        
        # Try to save as parquet
        try:
            dataframe.to_parquet(
                output_path.with_suffix(".parquet"),
                index=False
            )
            print(f"  ✅ Parquet saved to: {output_path.with_suffix('.parquet')}")
        except ImportError:
            print(f"  ⚠️ Parquet not saved (install pyarrow: pip install pyarrow)")
            
    except Exception as e:
        print(f"  ❌ Error exporting: {e}")

def summarize_dataset(dataframe, explicit, implicit):
    print("\n📊 Dataset Summary")
    print("=" * 40)
    print(f"Total interactions: {len(dataframe):,}")
    print(f"Unique users: {dataframe['user_id'].nunique():,}")
    print(f"Unique books: {dataframe['isbn'].nunique():,}")
    print(f"Explicit ratio: {len(explicit) / len(dataframe):.2%}")
    print(f"Implicit ratio: {len(implicit) / len(dataframe):.2%}")

def main():
    print("=" * 50)
    print("Ratings Data Cleaning Pipeline")
    print("=" * 50)
    
    dataframe = load_ratings_dataset()
    
    if dataframe is None:
        print("\n❌ Failed to load dataset. Exiting.")
        return
    
    print("\n📝 Standardizing column names...")
    dataframe = standardize_column_names(dataframe)
    
    print("\n🧹 Cleaning data...")
    dataframe = clean_ratings(dataframe)
    
    if len(dataframe) == 0:
        print("\n❌ No valid data after cleaning. Exiting.")
        return
    
    print("\n📊 Splitting ratings...")
    explicit, implicit = split_explicit_implicit(dataframe)
    
    summarize_dataset(dataframe, explicit, implicit)
    
    print("\n💾 Exporting datasets...")
    export_dataset(dataframe, OUTPUT_DIR / "ratings_cleaned")
    export_dataset(explicit, OUTPUT_DIR / "ratings_explicit")
    export_dataset(implicit, OUTPUT_DIR / "ratings_implicit")
    
    print("\n✅ Ratings cleaning pipeline completed successfully!")

if __name__ == "__main__":
    main()