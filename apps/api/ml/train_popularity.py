from pathlib import Path
import pandas as pd
import sys

# Make the `ml` package importable (this file lives at apps/api/ml/).
ML_DIR = Path(__file__).resolve().parent
API_DIR = ML_DIR.parent
sys.path.insert(0, str(API_DIR))
sys.path.insert(0, str(ML_DIR))

# pyrefly: ignore [missing-import]
from ml.popularity.popularity_recommender import PopularityRecommender

# Central path resolution — see apps/api/ml/paths.py.
# This previously hard-coded the absolute POSIX path "/data/processed",
# which only exists inside a container that mounts data there.
from paths import (  # noqa: E402
    INTEGRATED_DIR,
    PROCESSED_DATA_DIR,
    ARTIFACT_DIR,
    MODEL_DIR,
)

DATA_DIR = PROCESSED_DATA_DIR

# Check if deduplicated dataset exists, otherwise use original
deduplicated_path = INTEGRATED_DIR / "master_books_deduplicated.parquet"
original_path = INTEGRATED_DIR / "master_books.parquet"

if deduplicated_path.exists():
    BOOKS_PATH = deduplicated_path
    print("✅ Using deduplicated books dataset (315 duplicates removed)")

    # Show file size comparison
    dedup_size = deduplicated_path.stat().st_size / 1024**2
    orig_size = original_path.stat().st_size / 1024**2 if original_path.exists() else 0
    if orig_size > 0:
        print(f"   File size: {dedup_size:.2f} MB (vs {orig_size:.2f} MB original)")
else:
    BOOKS_PATH = original_path
    print("⚠️ Using original books dataset (may contain duplicates)")
    print("   Run deduplicate_books.py to clean the dataset")

# Verify data files exist
if not BOOKS_PATH.exists():
    print(f"❌ Books file not found: {BOOKS_PATH}")
    sys.exit(1)

ratings_path = DATA_DIR / "ratings" / "ratings_cleaned.parquet"
if not ratings_path.exists():
    print(f"❌ Ratings file not found: {ratings_path}")
    sys.exit(1)

# Output directories (resolved centrally — no longer relative to this file).
MODEL_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    print("=" * 60)
    print("LOADING DATASETS")
    print("=" * 60)

    print("Loading ratings...")
    ratings = pd.read_parquet(ratings_path)
    print(f"  ✅ Ratings: {len(ratings):,} interactions")
    print(f"     Unique users: {ratings['user_id'].nunique():,}")
    print(f"     Unique books: {ratings['isbn'].nunique():,}")

    print("\nLoading books...")
    books = pd.read_parquet(BOOKS_PATH)
    print(f"  ✅ Books: {len(books):,} unique titles")
    print(f"     With ratings: {books['ratings_count'].notna().sum():,}")
    print(f"     With publication years: {books['publication_year'].notna().sum():,}")

    return ratings, books


def main():
    print("=" * 60)
    print("ENHANCED POPULARITY RECOMMENDER TRAINING")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  - Category diversity weight: 0.3 (boosts underrepresented genres)")
    print(f"  - Recency weighting: 0.2 (favors newer books)")
    print(f"  - Minimum ratings threshold: 50")
    print("=" * 60)

    # Load data
    ratings, books = load_data()

    # Initialize enhanced recommender
    recommender = PopularityRecommender(
        min_ratings=50, diversity_weight=0.3, recency_weight=0.2
    )

    # Train the model
    print("\n" + "=" * 60)
    print("TRAINING MODEL")
    print("=" * 60)
    recommender.fit((ratings, books))

    # DEBUG: Check what's in the dataframe
    print("\n" + "=" * 60)
    print("DEBUG - DATAFRAME COLUMNS")
    print("=" * 60)
    print(f"Columns in popularity_df: {recommender.popularity_df.columns.tolist()}")
    print(
        f"\nratings_count exists: {'ratings_count' in recommender.popularity_df.columns}"
    )
    if "ratings_count" in recommender.popularity_df.columns:
        print(
            f"Sample ratings_count values: {recommender.popularity_df['ratings_count'].head(5).tolist()}"
        )
        print(
            f"Mean ratings_count: {recommender.popularity_df['ratings_count'].mean():.2f}"
        )
        print(
            f"Min ratings_count: {recommender.popularity_df['ratings_count'].min():.0f}"
        )
        print(
            f"Max ratings_count: {recommender.popularity_df['ratings_count'].max():.0f}"
        )

    # Get diverse recommendations
    print("\n" + "=" * 60)
    print("TOP 10 DIVERSE RECOMMENDATIONS")
    print("=" * 60)
    print("(Balanced across categories to avoid single-series dominance)\n")

    # Get recommendations
    recommendations = recommender.recommend(top_k=10, diversify=True)

    # Check if ratings_count is in recommendations
    print(f"\nDEBUG - Columns in recommendations: {recommendations.columns.tolist()}")
    if (
        "ratings_count" not in recommendations.columns
        and "ratings_count" in recommender.popularity_df.columns
    ):
        print("⚠️ Adding ratings_count from full dataframe...")
        recommendations = recommendations.merge(
            recommender.popularity_df[["isbn", "ratings_count"]], on="isbn", how="left"
        )
        print(f"✅ ratings_count added to recommendations")

    for idx, row in recommendations.iterrows():
        # Get ratings count
        ratings_cnt = 0
        if "ratings_count" in row and pd.notna(row.get("ratings_count")):
            ratings_cnt = int(row["ratings_count"])
        elif "ratings_count" in recommender.popularity_df.columns:
            # Try to get it from the full dataframe
            full_row = recommender.popularity_df[
                recommender.popularity_df["isbn"] == row["isbn"]
            ]
            if len(full_row) > 0 and "ratings_count" in full_row.columns:
                val = full_row["ratings_count"].iloc[0]
                if pd.notna(val):
                    ratings_cnt = int(val)

        year = (
            int(row["publication_year"])
            if pd.notna(row.get("publication_year"))
            else "N/A"
        )
        category = row.get("category", "Unknown")
        score = row["adjusted_score"]
        weighted = row["weighted_score"]

        print(f"{idx + 1}. {row['title'][:70]}")
        print(
            f"   📚 Category: {category} | 📅 Year: {year} | ⭐ Rating: {ratings_cnt:,} votes"
        )
        print(f"   📊 Score: {score:.2f} (weighted: {weighted:.2f})")
        print()

    # Category-specific recommendations
    print("\n" + "=" * 60)
    print("CATEGORY-SPECIFIC RECOMMENDATIONS")
    print("=" * 60)

    categories = [
        "Fantasy",
        "Classic",
        "Science Fiction",
        "Mystery",
        "Romance",
        "Biography",
    ]
    for category in categories:
        print(f"\n📚 Top {category} Books:")
        try:
            cat_recs = recommender.recommend_by_category(category, top_k=3)
            if len(cat_recs) > 0:
                for idx, row in cat_recs.iterrows():
                    score = row["adjusted_score"]
                    # Get ratings count for category recommendations
                    cat_ratings = 0
                    if "ratings_count" in row and pd.notna(row.get("ratings_count")):
                        cat_ratings = int(row["ratings_count"])
                    elif "ratings_count" in recommender.popularity_df.columns:
                        full_row = recommender.popularity_df[
                            recommender.popularity_df["isbn"] == row["isbn"]
                        ]
                        if len(full_row) > 0 and "ratings_count" in full_row.columns:
                            val = full_row["ratings_count"].iloc[0]
                            if pd.notna(val):
                                cat_ratings = int(val)
                    print(
                        f"  {idx + 1}. {row['title'][:55]} (Score: {score:.2f}, Ratings: {cat_ratings:,})"
                    )
            else:
                print(f"  No books found in {category} category")
        except Exception as e:
            print(f"  Error loading {category}: {e}")

    # Save the model
    print("\n" + "=" * 60)
    print("SAVING MODEL")
    print("=" * 60)

    model_path = MODEL_DIR / "popularity_recommender_enhanced.pkl"
    recommender.save_model(model_path)

    # Save a copy as the default recommender
    default_path = MODEL_DIR / "popularity_recommender.pkl"
    recommender.save_model(default_path)

    # Save popularity scores as a parquet artifact for the API
    popularity_scores_path = ARTIFACT_DIR / "popularity_scores.parquet"
    recommender.popularity_df.to_parquet(popularity_scores_path, index=False)

    print(f"✅ Popularity scores saved to: {popularity_scores_path}")
    print(f"   Rows: {len(recommender.popularity_df):,}")
    print(f"   Columns: {len(recommender.popularity_df.columns)}")

    # Print training summary
    print("\n" + "=" * 60)
    print("TRAINING SUMMARY")
    print("=" * 60)
    print(f"✅ Model saved to: {model_path}")
    print(f"✅ Model saved to: {default_path}")
    print(f"\n📊 Dataset Statistics:")
    print(f"  Books in recommendation pool: {len(recommender.popularity_df):,}")
    print(f"  Categories found: {recommender.popularity_df['category'].nunique()}")
    print(f"  Global mean rating: {recommender.global_mean:.2f}")

    # Category distribution
    if "category" in recommender.popularity_df.columns:
        print(f"\n📚 Category Distribution in Top 1000:")
        category_dist = recommender.popularity_df.head(1000)["category"].value_counts()
        for cat, count in category_dist.head(10).items():
            pct = (count / 1000) * 100
            bar = "█" * int(pct / 2)
            print(f"  {cat:15s}: {count:3d} ({pct:4.1f}%) {bar}")

    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE!")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("  1. Test the model: python apps/api/ml/test_recommender.py")
    print("  2. Deploy the API endpoint for recommendations")
    print("  3. Implement collaborative filtering for personalized recommendations")


if __name__ == "__main__":
    main()
