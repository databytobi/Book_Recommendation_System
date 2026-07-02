"""
Debug script to inspect the trained model and verify ratings_count
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

import pickle
import pandas as pd

# Import the recommender class before loading the model
from recommenders.popularity.popularity_recommender import PopularityRecommender

def debug_model():
    """Load and inspect the trained model."""
    
    model_path = Path("apps/ml/models/popularity_recommender.pkl")
    
    if not model_path.exists():
        print(f"❌ Model not found at {model_path}")
        return
    
    print("=" * 60)
    print("DEBUGGING TRAINED MODEL")
    print("=" * 60)
    
    # Load the model with the class already imported
    with open(model_path, "rb") as f:
        recommender = pickle.load(f)
    
    print(f"✅ Model loaded successfully")
    print(f"   Model type: {type(recommender).__name__}")
    print(f"   Is fitted: {recommender.is_fitted}")
    print(f"   Min ratings: {recommender.min_ratings}")
    print(f"   Global mean: {recommender.global_mean}")
    
    print("\n" + "=" * 60)
    print("POPULARITY DATAFRAME INFO")
    print("=" * 60)
    
    df = recommender.popularity_df
    
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Total books: {len(df):,}")
    
    # Check for ratings_count column
    if 'ratings_count' in df.columns:
        print(f"\n✅ ratings_count column exists")
        print(f"   Non-null count: {df['ratings_count'].notna().sum():,}")
        print(f"   Min: {df['ratings_count'].min():.0f}")
        print(f"   Max: {df['ratings_count'].max():.0f}")
        print(f"   Mean: {df['ratings_count'].mean():.0f}")
        print(f"   Median: {df['ratings_count'].median():.0f}")
        
        print(f"\n📊 Top 10 books by ratings_count:")
        top_by_ratings = df.nlargest(10, 'ratings_count')
        for _, row in top_by_ratings.iterrows():
            title = row['title'][:50] if 'title' in row else 'Unknown'
            print(f"  {title}... {int(row['ratings_count']):,} ratings, score: {row['weighted_score']:.2f}")
    else:
        print("\n❌ ratings_count column NOT found in dataframe!")
        print("Available numeric columns:")
        for col in df.select_dtypes(include=['number']).columns:
            print(f"  - {col}")
    
    # Check for weighted_score and adjusted_score
    print(f"\n📊 Score columns:")
    for col in ['weighted_score', 'adjusted_score', 'average_rating']:
        if col in df.columns:
            print(f"  {col}: mean={df[col].mean():.2f}, min={df[col].min():.2f}, max={df[col].max():.2f}")
    
    # Check categories
    if 'category' in df.columns:
        print(f"\n📚 Category distribution:")
        for cat, count in df['category'].value_counts().head(10).items():
            pct = (count / len(df)) * 100
            print(f"  {cat}: {count} ({pct:.1f}%)")
    
    # Show a sample of the top recommendations with all columns
    print("\n" + "=" * 60)
    print("SAMPLE TOP 5 RECOMMENDATIONS (ALL COLUMNS)")
    print("=" * 60)
    
    top_5 = df.head(5)
    display_cols = ['title', 'average_rating', 'ratings_count', 'weighted_score', 'adjusted_score', 'category']
    available_cols = [col for col in display_cols if col in df.columns]
    
    if available_cols:
        print(top_5[available_cols].to_string())
    else:
        print("No display columns found")
        print(f"Available columns: {list(df.columns)}")
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    debug_model()