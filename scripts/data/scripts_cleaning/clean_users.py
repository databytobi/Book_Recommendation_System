"""
Complete Users Data Cleaning Pipeline
Handles: basic cleaning, country normalization, ISO codes, final validation
"""

import sys
from pathlib import Path
import pandas as pd
import re
# pyrefly: ignore [missing-import]
import pycountry

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from scripts.data.scripts_cleaning.config import USERS_FILE, PROCESSED_DATA_DIR
from scripts.data.scripts_cleaning.utils import normalize_text, clean_age

OUTPUT_DIR = PROCESSED_DATA_DIR / "users"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Complete country mapping dictionary
COUNTRY_MAPPINGS = {
    # US variations
    'usa': 'United States', 'us': 'United States', 'u.s.a.': 'United States',
    'united states of america': 'United States', 'america': 'United States',
    # UK variations
    'uk': 'United Kingdom', 'u.k.': 'United Kingdom', 'great britain': 'United Kingdom',
    'britain': 'United Kingdom', 'england': 'United Kingdom', 'scotland': 'United Kingdom',
    'wales': 'United Kingdom', 'northern ireland': 'United Kingdom',
    # US States (should map to United States)
    'california': 'United States', 'texas': 'United States', 'new york': 'United States',
    'florida': 'United States', 'illinois': 'United States', 'pennsylvania': 'United States',
    'ohio': 'United States', 'michigan': 'United States', 'georgia': 'United States',
    # Canadian provinces
    'ontario': 'Canada', 'quebec': 'Canada', 'british columbia': 'Canada',
    'alberta': 'Canada', 'manitoba': 'Canada', 'saskatchewan': 'Canada',
    # Australian states
    'new south wales': 'Australia', 'victoria': 'Australia', 'queensland': 'Australia',
    'western australia': 'Australia', 'south australia': 'Australia', 'tasmania': 'Australia',
    # German regions
    'bayern': 'Germany', 'bavaria': 'Germany', 'nordrhein-westfalen': 'Germany',
    'baden-württemberg': 'Germany', 'niedersachsen': 'Germany', 'hessen': 'Germany',
    'berlin': 'Germany', 'hamburg': 'Germany', 'munich': 'Germany',
    # French regions
    'paris': 'France', 'provence': 'France', 'côte d\'azur': 'France',
    'brittany': 'France', 'normandy': 'France', 'alsace': 'France',
    # Italian regions
    'lombardy': 'Italy', 'tuscany': 'Italy', 'sicily': 'Italy', 'veneto': 'Italy',
    'rome': 'Italy', 'milan': 'Italy', 'naples': 'Italy', 'turin': 'Italy',
    # Spanish regions
    'catalonia': 'Spain', 'madrid': 'Spain', 'andalusia': 'Spain',
    'valencia': 'Spain', 'barcelona': 'Spain', 'españa': 'Spain',
    # Common cities
    'london': 'United Kingdom', 'manchester': 'United Kingdom', 'birmingham': 'United Kingdom',
    'glasgow': 'United Kingdom', 'edinburgh': 'United Kingdom', 'liverpool': 'United Kingdom',
    'sydney': 'Australia', 'melbourne': 'Australia', 'brisbane': 'Australia', 'perth': 'Australia',
    'toronto': 'Canada', 'vancouver': 'Canada', 'montreal': 'Canada', 'ottawa': 'Canada',
    # Fix typos
    'espaã±a': 'Spain', 'u.s.': 'United States', 'u.k.': 'United Kingdom',
}

def extract_country_from_location(location):
    """Extract country from location string."""
    if pd.isna(location):
        return None
    
    location = str(location).lower().strip()
    
    # Try to match from mappings first
    for pattern, country in COUNTRY_MAPPINGS.items():
        if pattern in location:
            return country
    
    # Split by comma and take the last part
    parts = location.split(',')
    if len(parts) > 0:
        country = parts[-1].strip().title()
        # Fix common issues
        if country == 'Usa':
            return 'United States'
        if country == 'Uk':
            return 'United Kingdom'
        if len(country) == 2 and country.isalpha():
            # Handle 2-letter codes
            return None
        return country if len(country) > 2 else None
    
    return None

def add_iso_codes(df):
    """Add ISO country codes."""
    country_to_iso2 = {}
    country_to_iso3 = {}
    
    for country in pycountry.countries:
        country_to_iso2[country.name] = country.alpha_2
        country_to_iso3[country.name] = country.alpha_3
    
    # Manual overrides
    manual_iso2 = {
        'United States': 'US', 'United Kingdom': 'GB', 'Russia': 'RU',
        'China': 'CN', 'South Korea': 'KR', 'Taiwan': 'TW', 'Hong Kong': 'HK'
    }
    
    df['country_iso2'] = df['country'].map(country_to_iso2)
    df['country_iso3'] = df['country'].map(country_to_iso3)
    
    for country, iso2 in manual_iso2.items():
        df.loc[df['country'] == country, 'country_iso2'] = iso2
    
    return df

def load_users():
    """Load users dataset."""
    print("Loading users dataset...")
    if not USERS_FILE.exists():
        print(f"❌ File not found: {USERS_FILE}")
        return None
    
    df = pd.read_csv(USERS_FILE, sep=",", encoding="latin-1", low_memory=False)
    print(f"✅ Loaded {len(df):,} rows")
    return df

def clean_basic(df):
    """Basic cleaning: column names, duplicates, ages."""
    print("\n📝 Basic Cleaning...")
    
    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace("-", "_").str.replace(" ", "_")
    
    # Clean ages
    if 'age' in df.columns:
        before = df['age'].notna().sum()
        df['age'] = df['age'].apply(clean_age)
        after = df['age'].notna().sum()
        print(f"  Ages: {after:,} valid (from {before:,})")
    
    # Remove duplicates
    if 'user_id' in df.columns:
        before = len(df)
        df = df.drop_duplicates(subset=['user_id'])
        print(f"  Removed {before - len(df):,} duplicate users")
    
    return df

def clean_countries(df):
    """Country extraction and normalization."""
    print("\n🌍 Country Normalization...")
    
    # Clean location text
    if 'location' in df.columns:
        df['location'] = df['location'].apply(normalize_text)
        
        # Extract country
        df['country'] = df['location'].apply(extract_country_from_location)
        
        unique_before = df['country'].nunique()
        print(f"  Unique countries before: {unique_before}")
    
    # Add ISO codes
    df = add_iso_codes(df)
    
    unique_after = df['country'].nunique()
    print(f"  Unique countries after: {unique_after}")
    
    return df

def generate_report(df):
    """Generate final report."""
    print("\n" + "=" * 60)
    print("📊 FINAL DATASET SUMMARY")
    print("=" * 60)
    
    print(f"\n📈 Basic Statistics:")
    print(f"  Total users: {len(df):,}")
    print(f"  Users with age: {df['age'].notna().sum():,} ({df['age'].notna().sum()/len(df)*100:.1f}%)")
    print(f"  Users with country: {df['country'].notna().sum():,} ({df['country'].notna().sum()/len(df)*100:.1f}%)")
    print(f"  Users with ISO codes: {df['country_iso2'].notna().sum():,}")
    
    print(f"\n🌍 Top 15 Countries:")
    country_counts = df['country'].value_counts().head(15)
    for i, (country, count) in enumerate(country_counts.items(), 1):
        if pd.notna(country):
            pct = count / len(df) * 100
            bar = "█" * int(pct / 2)
            print(f"  {i:2d}. {country:25s}: {count:6,} ({pct:4.1f}%) {bar}")
    
    print(f"\n📁 Output directory: {OUTPUT_DIR}")

def export_data(df):
    """Export cleaned data."""
    print("\n💾 Exporting...")
    
    # Select final columns
    final_cols = ['user_id', 'location', 'country', 'country_iso2', 'country_iso3', 'age']
    final_cols = [c for c in final_cols if c in df.columns]
    final_df = df[final_cols]
    
    # Save files
    csv_path = OUTPUT_DIR / "users_cleaned.csv"
    parquet_path = OUTPUT_DIR / "users_cleaned.parquet"
    
    final_df.to_csv(csv_path, index=False)
    print(f"✅ CSV: {csv_path}")
    
    try:
        final_df.to_parquet(parquet_path, index=False)
        print(f"✅ Parquet: {parquet_path}")
    except:
        print(f"⚠️ Parquet not saved (install pyarrow)")
    
    return final_df

def main():
    print("=" * 60)
    print("USERS DATA CLEANING PIPELINE")
    print("=" * 60)
    
    # Load
    df = load_users()
    if df is None:
        return
    
    # Clean
    df = clean_basic(df)
    df = clean_countries(df)
    
    # Report & Export
    generate_report(df)
    export_data(df)
    
    print("\n✅ Pipeline complete!")

if __name__ == "__main__":
    main()