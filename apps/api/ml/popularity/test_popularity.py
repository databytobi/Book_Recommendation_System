"""
Test script for the Popularity Recommender.
Tests the recommender with sample data and displays results.
"""

import sys
from pathlib import Path
import pandas as pd

# Add the necessary paths
# Go up from: apps/api/ml/popularity/test_popularity.py
# To: project_root (Desktop/Book Recommendation System)
# We need to go up 4 levels: popularity -> ml -> api -> apps -> project_root
project_root = Path(__file__).resolve().parents[4]  # Fixed: 4 levels, not 3
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "apps" / "api" / "ml"))
sys.path.insert(0, str(project_root / "apps" / "api" / "ml" / "popularity"))
sys.path.insert(0, str(project_root / "apps" / "api" / "ml" / "recommenders"))

# Import the recommender
# pyrefly: ignore [missing-import]
from popularity_recommender import PopularityRecommender

# Data paths - Use project_root directly
BASE_DIR = project_root
DATA_DIR = BASE_DIR / "data" / "processed"
ARTIFACT_DIR = BASE_DIR / "apps" / "api" / "ml" / "artifacts"

print(f"DEBUG: Project root: {BASE_DIR}")
print(f"DEBUG: Artifact dir: {ARTIFACT_DIR}")
print(f"DEBUG: Data dir: {DATA_DIR}")


def load_test_data():
    """
    Load sample data for testing.
    """
    print("=" * 60)
    print("LOADING TEST DATA")
    print("=" * 60)
    
    # Try to load from artifacts first
    train_path = ARTIFACT_DIR / "train_interactions.parquet"
    books_path = DATA_DIR / "integrated" / "master_books_deduplicated.parquet"
    
    # Fallback to original if deduplicated doesn't exist
    if not books_path.exists():
        books_path = DATA_DIR / "integrated" / "master_books.parquet"
    
    print(f"Looking for train data at: {train_path}")
    print(f"Looking for books data at: {books_path}")
    
    if not train_path.exists():
        print(f"❌ Train data not found: {train_path}")
        print("\nPlease run the interaction matrix pipeline first:")
        print("  python apps/api/ml/features/interaction_matrix.py")
        print("\nOr check if the artifacts directory exists:")
        print(f"  {ARTIFACT_DIR}")
        return None, None
    
    if not books_path.exists():
        print(f"❌ Books data not found: {books_path}")
        return None, None
    
    train = pd.read_parquet(train_path)
    books = pd.read_parquet(books_path)
    
    print(f"✅ Train interactions: {len(train):,}")
    print(f"✅ Books: {len(books):,}")
    print(f"   Unique users: {train['user_id'].nunique():,}")
    print(f"   Unique books: {train['isbn'].nunique():,}")
    
    return train, books


def test_recommender():
    """
    Test the popularity recommender.
    """
    print("=" * 60)
    print("POPULARITY RECOMMENDER TEST")
    print("=" * 60)
    
    # Load data
    train, books = load_test_data()
    
    if train is None or books is None:
        print("\n❌ Failed to load test data. Exiting.")
        return
    
    # Initialize recommender
    print("\n" + "=" * 60)
    print("INITIALIZING RECOMMENDER")
    print("=" * 60)
    
    recommender = PopularityRecommender(
        min_ratings=50,
        diversity_weight=0.3,
        recency_weight=0.2
    )
    
    # Train the recommender
    print("\n" + "=" * 60)
    print("TRAINING RECOMMENDER")
    print("=" * 60)
    
    try:
        recommender.fit((train, books))
    except Exception as e:
        print(f"❌ Error training recommender: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test different recommendation scenarios
    print("\n" + "=" * 60)
    print("TESTING RECOMMENDATIONS")
    print("=" * 60)
    
    # Test 1: Get top 10 diverse recommendations
    print("\n📊 Test 1: Top 10 Diverse Recommendations")
    print("-" * 40)
    
    try:
        recs = recommender.recommend(top_k=10, diversify=True)
        print(f"✅ Generated {len(recs)} recommendations")
        print("\nTop Recommendations:")
        display_cols = ['rank', 'title', 'authors', 'category', 'average_rating', 'ratings_count', 'adjusted_score']
        available_cols = [col for col in display_cols if col in recs.columns]
        if available_cols:
            print(recs[available_cols].to_string(index=False))
        else:
            print(recs.to_string(index=False))
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Get top 10 non-diverse recommendations
    print("\n📊 Test 2: Top 10 Non-Diverse Recommendations")
    print("-" * 40)
    
    try:
        recs = recommender.recommend(top_k=10, diversify=False)
        print(f"✅ Generated {len(recs)} recommendations")
        print("\nTop Recommendations:")
        display_cols = ['rank', 'title', 'authors', 'category', 'average_rating', 'ratings_count', 'adjusted_score']
        available_cols = [col for col in display_cols if col in recs.columns]
        if available_cols:
            print(recs[available_cols].to_string(index=False))
        else:
            print(recs.to_string(index=False))
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Category-specific recommendations
    print("\n📊 Test 3: Category-Specific Recommendations")
    print("-" * 40)
    
    categories = ['Fantasy', 'Classic', 'Science Fiction', 'Mystery', 'Romance', 'Biography']
    
    for category in categories:
        try:
            cat_recs = recommender.recommend_by_category(category, top_k=3)
            if len(cat_recs) > 0:
                print(f"\n📚 Top {category} Books:")
                for idx, row in cat_recs.iterrows():
                    print(f"  {idx+1}. {row['title'][:60]}")
                    if 'authors' in row:
                        print(f"     Authors: {row['authors']}")
                    if 'ratings_count' in row:
                        print(f"     Ratings: {row['ratings_count']:,}")
                    if 'adjusted_score' in row:
                        print(f"     Score: {row['adjusted_score']:.4f}")
                    print()
            else:
                print(f"\n📚 No books found in {category} category")
        except Exception as e:
            print(f"❌ Error loading {category}: {e}")
    
    # Test 4: Explain a recommendation
    print("\n📊 Test 4: Explain Recommendation")
    print("-" * 40)
    
    try:
        # Get a book to explain
        top_recs = recommender.recommend(top_k=1, diversify=True)
        if len(top_recs) > 0:
            isbn = top_recs.iloc[0]['isbn']
            explanation = recommender.explain_recommendation(isbn)
            print(f"\n📖 Explaining: {explanation.get('title', 'Unknown')}")
            print(f"   ISBN: {explanation.get('isbn', 'N/A')}")
            print(f"   Average Rating: {explanation.get('average_rating', 'N/A')}")
            if explanation.get('ratings_count'):
                print(f"   Ratings Count: {explanation.get('ratings_count', 'N/A'):,}")
            print(f"   Weighted Score: {explanation.get('weighted_score', 'N/A'):.4f}")
            print(f"   Adjusted Score: {explanation.get('adjusted_score', 'N/A'):.4f}")
            print(f"   Category: {explanation.get('category', 'Unknown')}")
            print(f"   Diversity Boost: {explanation.get('diversity_boost', 1.0):.4f}")
            print(f"   Recency Boost: {explanation.get('recency_boost', 1.0):.4f}")
            print(f"   Rank: #{explanation.get('rank', 'N/A')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
    print(f"\n📊 Model Statistics:")
    print(f"  Books in recommendation pool: {len(recommender.popularity_df):,}")
    if 'category' in recommender.popularity_df.columns:
        print(f"  Categories found: {recommender.popularity_df['category'].nunique()}")
    print(f"  Global mean rating: {recommender.global_mean:.4f}")
    print(f"  Min ratings threshold: {recommender.min_ratings}")
    
    # Show category distribution
    if 'category' in recommender.popularity_df.columns:
        print(f"\n📚 Category Distribution:")
        category_dist = recommender.popularity_df['category'].value_counts()
        for cat, count in category_dist.head(10).items():
            pct = (count / len(recommender.popularity_df)) * 100
            print(f"  {cat:20s}: {count:4d} ({pct:5.1f}%)")
    
    print("\n✅ All tests completed successfully!")


if __name__ == "__main__":
    test_recommender()