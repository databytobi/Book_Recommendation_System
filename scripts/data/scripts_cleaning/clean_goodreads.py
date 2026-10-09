import sys
from pathlib import Path
import pandas as pd
import csv

# Add the project root to Python path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from scripts.data.scripts_cleaning.config import (
    GOODREADS_BOOKS_FILE,
    PROCESSED_DATA_DIR
)

from scripts.data.scripts_cleaning.utils import (
    normalize_text,
    normalize_author
)

OUTPUT_DIR = PROCESSED_DATA_DIR / "goodreads"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_goodreads_dataset():
    """Load Goodreads dataset with error handling for malformed rows."""
    print("Loading Goodreads dataset...")
    print(f"Looking for file: {GOODREADS_BOOKS_FILE}")
    
    if not GOODREADS_BOOKS_FILE.exists():
        print(f"❌ File not found: {GOODREADS_BOOKS_FILE}")
        return None
    
    try:
        # First, try reading with error handling
        dataframe = pd.read_csv(
            GOODREADS_BOOKS_FILE,
            encoding="utf-8",
            low_memory=False,
            on_bad_lines='skip',  # Skip problematic lines
            engine='python'  # More flexible parser
        )
        
        print(f"✅ Loaded {len(dataframe):,} rows")
        print(f"   Columns: {list(dataframe.columns)}")
        
        return dataframe
        
    except Exception as e:
        print(f"⚠️ Standard loading failed: {e}")
        print("   Trying alternative loading method...")
        
        try:
            # Alternative: Read with error handling and warn
            dataframe = pd.read_csv(
                GOODREADS_BOOKS_FILE,
                encoding="utf-8",
                low_memory=False,
                error_bad_lines=False,
                warn_bad_lines=True
            )
            
            print(f"✅ Loaded {len(dataframe):,} rows with error handling")
            print(f"   Columns: {list(dataframe.columns)}")
            
            return dataframe
            
        except Exception as e2:
            print(f"❌ Alternative loading also failed: {e2}")
            
            # Last resort: Try to read and fix column issues
            try:
                print("   Attempting to fix column issues...")
                
                # Read as CSV with Python's csv module to handle quotes properly
                with open(GOODREADS_BOOKS_FILE, 'r', encoding='utf-8') as f:
                    # Check first few lines to determine structure
                    sample = [next(csv.reader([line])) for line in [next(f) for _ in range(5)]]
                    
                print(f"   Sample columns: {sample[0][:5]}...")
                print(f"   Detected {len(sample[0])} columns in header")
                
                # Try reading with quote handling
                dataframe = pd.read_csv(
                    GOODREADS_BOOKS_FILE,
                    encoding="utf-8",
                    quotechar='"',
                    escapechar='\\',
                    on_bad_lines='skip',
                    engine='python'
                )
                
                print(f"✅ Loaded {len(dataframe):,} rows with quote handling")
                print(f"   Columns: {list(dataframe.columns)}")
                
                return dataframe
                
            except Exception as e3:
                print(f"❌ All loading methods failed: {e3}")
                return None

def standardize_column_names(dataframe):
    """Standardize column names to lowercase with underscores."""
    dataframe.columns = (
        dataframe.columns
        .str.strip()
        .str.lower()
        .str.replace("-", "_")
        .str.replace(" ", "_")
        .str.replace("[()]", "", regex=True)
    )
    
    return dataframe

def clean_goodreads(dataframe):
    """Clean the Goodreads dataset."""
    print("Cleaning Goodreads dataset...")
    original_len = len(dataframe)
    
    # Identify and handle duplicate columns (if any)
    if dataframe.columns.duplicated().any():
        print("  Removing duplicate columns...")
        dataframe = dataframe.loc[:, ~dataframe.columns.duplicated()]
    
    # Normalize titles
    if "title" in dataframe.columns:
        print("  Normalizing titles...")
        dataframe["title"] = dataframe["title"].apply(normalize_text)
    
    # Normalize authors
    if "authors" in dataframe.columns:
        print("  Normalizing authors...")
        dataframe["authors"] = dataframe["authors"].apply(normalize_author)
    
    # Normalize publishers
    if "publisher" in dataframe.columns:
        print("  Normalizing publishers...")
        dataframe["publisher"] = dataframe["publisher"].apply(normalize_text)
    
    # Normalize ISBNs
    if "isbn" in dataframe.columns:
        print("  Cleaning ISBNs...")
        dataframe["isbn"] = dataframe["isbn"].astype(str).str.replace('-', '').str.strip()
        dataframe["isbn"] = dataframe["isbn"].replace('nan', None)
    
    if "isbn13" in dataframe.columns:
        print("  Cleaning ISBN13s...")
        dataframe["isbn13"] = dataframe["isbn13"].astype(str).str.replace('-', '').str.strip()
        dataframe["isbn13"] = dataframe["isbn13"].replace('nan', None)
    
    # Normalize language codes
    if "language_code" in dataframe.columns:
        print("  Normalizing language codes...")
        dataframe["language_code"] = (
            dataframe["language_code"]
            .astype(str)
            .str.lower()
            .str.strip()
        )
        
        # Map common language codes to standard format
        language_mapping = {
            'eng': 'eng', 'en-us': 'eng', 'en-gb': 'eng', 'en-ca': 'eng',
            'en': 'eng', 'english': 'eng', 'en-US': 'eng', 'en-GB': 'eng',
            'fre': 'fre', 'fr': 'fre', 'french': 'fre', 'fr-FR': 'fre',
            'ger': 'ger', 'de': 'ger', 'german': 'ger', 'deu': 'ger', 'de-DE': 'ger',
            'spa': 'spa', 'es': 'spa', 'spanish': 'spa', 'es-ES': 'spa',
            'ita': 'ita', 'it': 'ita', 'italian': 'ita', 'it-IT': 'ita',
            'jpn': 'jpn', 'ja': 'jpn', 'japanese': 'jpn', 'ja-JP': 'jpn',
            'chi': 'chi', 'zh': 'chi', 'chinese': 'chi', 'zh-CN': 'chi',
            'rus': 'rus', 'ru': 'rus', 'russian': 'rus', 'ru-RU': 'rus',
            'por': 'por', 'pt': 'por', 'portuguese': 'por', 'pt-PT': 'por',
            'dut': 'dut', 'nl': 'dut', 'dutch': 'dut', 'nl-NL': 'dut',
            'swe': 'swe', 'sv': 'swe', 'swedish': 'swe', 'sv-SE': 'swe',
            'pol': 'pol', 'pl': 'pol', 'polish': 'pol', 'pl-PL': 'pol',
            'tur': 'tur', 'tr': 'tur', 'turkish': 'tur', 'tr-TR': 'tur',
            'ara': 'ara', 'ar': 'ara', 'arabic': 'ara', 'ar-SA': 'ara',
            'hin': 'hin', 'hi': 'hin', 'hindi': 'hin', 'hi-IN': 'hin',
            'lat': 'lat', 'la': 'lat', 'latin': 'lat',
        }
        dataframe["language_code"] = dataframe["language_code"].map(language_mapping).fillna(dataframe["language_code"])
        
        # Replace 'nan' strings with None
        dataframe["language_code"] = dataframe["language_code"].replace('nan', None)
    
    # Parse publication dates
    if "publication_date" in dataframe.columns:
        print("  Parsing publication dates...")
        dataframe["publication_date"] = pd.to_datetime(
            dataframe["publication_date"],
            errors="coerce"
        )
        # Extract year from publication date
        dataframe["publication_year"] = dataframe["publication_date"].dt.year
    
    # Clean numeric columns
    numeric_columns = ['average_rating', 'ratings_count', 'text_reviews_count', 'num_pages']
    for col in numeric_columns:
        if col in dataframe.columns:
            dataframe[col] = pd.to_numeric(dataframe[col], errors='coerce')
    
    # Remove duplicate book IDs
    if "bookid" in dataframe.columns:
        before = len(dataframe)
        dataframe = dataframe.drop_duplicates(subset=["bookid"])
        removed = before - len(dataframe)
        print(f"  Removed {removed:,} duplicate book IDs")
    
    print(f"  Final rows: {len(dataframe):,} (from {original_len:,})")
    
    return dataframe

def summarize_dataset(dataframe):
    """Print dataset summary."""
    print("\n" + "=" * 60)
    print("Goodreads Dataset Summary")
    print("=" * 60)
    
    print(f"Rows: {len(dataframe):,}")
    print(f"Columns: {len(dataframe.columns)}")
    
    if "authors" in dataframe.columns:
        print(f"Unique authors: {dataframe['authors'].nunique():,}")
    
    if "publisher" in dataframe.columns:
        print(f"Unique publishers: {dataframe['publisher'].nunique():,}")
    
    if "language_code" in dataframe.columns:
        unique_langs = dataframe['language_code'].nunique()
        print(f"Unique languages: {unique_langs:,}")
        
        # Show top languages
        print("\n  Top 10 languages:")
        lang_counts = dataframe['language_code'].value_counts().head(10)
        for lang, count in lang_counts.items():
            if pd.notna(lang) and lang != 'nan':
                pct = (count / len(dataframe)) * 100
                print(f"    {lang}: {count:,} ({pct:.1f}%)")
    
    if "publication_date" in dataframe.columns:
        missing_dates = dataframe['publication_date'].isna().sum()
        print(f"\nBooks missing publication dates: {missing_dates:,} ({missing_dates/len(dataframe)*100:.1f}%)")
        
        # Show publication year range
        if 'publication_year' in dataframe.columns:
            valid_years = dataframe['publication_year'].notna().sum()
            if valid_years > 0:
                print(f"Publication year range: {int(dataframe['publication_year'].min()):.0f} - {int(dataframe['publication_year'].max()):.0f}")
    
    if "average_rating" in dataframe.columns:
        valid_ratings = dataframe['average_rating'].notna().sum()
        if valid_ratings > 0:
            print(f"\nAverage rating: {dataframe['average_rating'].mean():.2f}")
            print(f"Rating range: {dataframe['average_rating'].min():.2f} - {dataframe['average_rating'].max():.2f}")
            print(f"Median rating: {dataframe['average_rating'].median():.2f}")
    
    if "ratings_count" in dataframe.columns:
        print(f"Total ratings count: {dataframe['ratings_count'].sum():,.0f}")

def export_dataset(dataframe):
    """Export cleaned dataset."""
    csv_output = OUTPUT_DIR / "goodreads_cleaned.csv"
    parquet_output = OUTPUT_DIR / "goodreads_cleaned.parquet"
    
    print(f"\nExporting cleaned dataset to {OUTPUT_DIR}...")
    
    try:
        dataframe.to_csv(csv_output, index=False)
        print(f"✅ CSV saved to: {csv_output}")
        
        try:
            dataframe.to_parquet(parquet_output, index=False)
            print(f"✅ Parquet saved to: {parquet_output}")
        except ImportError:
            print(f"⚠️ Parquet not saved (install pyarrow: pip install pyarrow)")
        
        # Export language code mapping for reference
        if "language_code" in dataframe.columns:
            lang_summary = dataframe['language_code'].value_counts().reset_index()
            lang_summary.columns = ['language_code', 'count']
            lang_summary = lang_summary[lang_summary['language_code'] != 'nan']
            lang_summary.to_csv(OUTPUT_DIR / "language_summary.csv", index=False)
            print(f"✅ Language summary saved to: {OUTPUT_DIR / 'language_summary.csv'}")
            
    except Exception as e:
        print(f"❌ Error exporting dataset: {e}")

def main():
    print("=" * 60)
    print("Goodreads Data Cleaning Pipeline")
    print("=" * 60)
    
    # Load data
    dataframe = load_goodreads_dataset()
    
    if dataframe is None:
        print("\n❌ Failed to load dataset. Exiting.")
        print("\n💡 Troubleshooting tips:")
        print("   1. Check that the CSV file is not corrupted")
        print("   2. Try opening the file in Excel to check for issues")
        print("   3. Consider re-downloading the dataset from Kaggle")
        return
    
    # Standardize column names
    print("\n📝 Standardizing column names...")
    dataframe = standardize_column_names(dataframe)
    
    # Clean data
    print("\n🧹 Cleaning data...")
    dataframe = clean_goodreads(dataframe)
    
    # Summary
    summarize_dataset(dataframe)
    
    # Export
    print("\n💾 Exporting cleaned dataset...")
    export_dataset(dataframe)
    
    print("\n✅ Goodreads cleaning pipeline completed successfully!")

if __name__ == "__main__":
    main()