from pathlib import Path
import pandas as pd
import sys

# Add paths to match the structure used in popularity_recommender.py
project_root = Path(__file__).resolve().parents[3]  # Go up to project root

# CRITICAL: Add the parent directory of popularity so base can be found
# popularity_recommender.py looks in parent.parent, which is apps/api/ml
# We need to make sure base.py is accessible from there
sys.path.insert(0, str(project_root / "apps" / "api" / "ml" / "recommenders"))
sys.path.insert(0, str(project_root / "apps" / "api" / "ml"))
sys.path.insert(0, str(project_root / "apps" / "api" / "ml" / "popularity"))
sys.path.insert(0, str(project_root))

# Now import
# pyrefly: ignore [missing-import]
from popularity.popularity_recommender import PopularityRecommender
# pyrefly: ignore [missing-import]
from evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    mean_average_precision_at_k,
    catalog_coverage
)

BASE_DIR = project_root

DATA_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)

ARTIFACT_DIR = (
    BASE_DIR
    / "apps"
    / "api"
    / "ml"
    / "artifacts"
)

MODEL_DIR = (
    BASE_DIR
    / "apps"
    / "api"
    / "ml"
    / "models"
)

def load_datasets():
    """
    Load train, test, and books datasets.
    """
    print("=" * 60)
    print("LOADING DATASETS")
    print("=" * 60)
    
    train_path = ARTIFACT_DIR / "train_interactions.parquet"
    test_path = ARTIFACT_DIR / "test_interactions.parquet"
    books_path = DATA_DIR / "integrated" / "master_books.parquet"
    
    # Check if files exist
    if not train_path.exists():
        print(f"❌ Train file not found: {train_path}")
        return None, None, None
    
    if not test_path.exists():
        print(f"❌ Test file not found: {test_path}")
        return None, None, None
    
    if not books_path.exists():
        print(f"❌ Books file not found: {books_path}")
        return None, None, None
    
    train = pd.read_parquet(train_path)
    test = pd.read_parquet(test_path)
    books = pd.read_parquet(books_path)
    
    print(f"Train interactions: {len(train):,}")
    print(f"Test interactions: {len(test):,}")
    print(f"Books: {len(books):,}")
    print(f"Unique users in train: {train['user_id'].nunique():,}")
    print(f"Unique users in test: {test['user_id'].nunique():,}")
    
    return train, test, books

def build_ground_truth(test_df):
    """
    Build ground truth dictionary from test data.
    """
    print("\n" + "=" * 60)
    print("BUILDING GROUND TRUTH")
    print("=" * 60)
    
    ground_truth = (
        test_df
        .groupby("user_id")["isbn"]
        .apply(list)
        .to_dict()
    )
    
    print(f"Users in test set: {len(ground_truth):,}")
    
    # Show sample
    sample_user = list(ground_truth.keys())[0] if ground_truth else None
    if sample_user:
        print(f"Sample user {sample_user}: {len(ground_truth[sample_user])} items")
    
    return ground_truth

def generate_recommendations(
    recommender,
    users,
    top_k=10
):
    """
    Generate recommendations for all users.
    """
    print("\n" + "=" * 60)
    print("GENERATING RECOMMENDATIONS")
    print("=" * 60)
    
    recommendations = {}
    
    # Get top K recommendations from popularity model
    try:
        top_books = recommender.recommend(top_k=top_k, diversify=True)
        recommended_isbns = top_books["isbn"].tolist()
    except Exception as e:
        print(f"⚠️ Error getting recommendations: {e}")
        # Try without diversification
        top_books = recommender.recommend(top_k=top_k, diversify=False)
        recommended_isbns = top_books["isbn"].tolist()
    
    print(f"Top {top_k} popular books: {recommended_isbns[:3]}...")
    
    # Assign same recommendations to all users (popularity-based)
    users_list = list(users)
    for user_id in users_list:
        recommendations[user_id] = recommended_isbns.copy()
    
    print(f"Generated recommendations for {len(users_list):,} users")
    
    return recommendations

def evaluate(
    recommendations,
    ground_truth,
    total_books,
    k=10
):
    """
    Evaluate recommendations using multiple metrics.
    """
    print("\n" + "=" * 60)
    print(f"EVALUATING METRICS (K={k})")
    print("=" * 60)
    
    precision_scores = []
    recall_scores = []
    
    users_evaluated = 0
    
    for user_id in recommendations:
        if user_id not in ground_truth:
            continue
        
        recommended = recommendations[user_id]
        relevant = ground_truth[user_id]
        
        # Skip users with no relevant items
        if len(relevant) == 0:
            continue
        
        precision_scores.append(
            precision_at_k(
                recommended,
                relevant,
                k
            )
        )
        
        recall_scores.append(
            recall_at_k(
                recommended,
                relevant,
                k
            )
        )
        
        users_evaluated += 1
    
    if len(precision_scores) == 0:
        print("⚠️ No users evaluated!")
        return {
            "Precision@K": 0.0,
            "Recall@K": 0.0,
            "MAP@K": 0.0,
            "Coverage": 0.0,
            "Users_Evaluated": 0
        }
    
    precision = sum(precision_scores) / len(precision_scores)
    recall = sum(recall_scores) / len(recall_scores)
    
    map_k = mean_average_precision_at_k(
        recommendations,
        ground_truth,
        k
    )
    
    coverage = catalog_coverage(
        recommendations,
        total_books
    )
    
    results = {
        "Precision@K": precision,
        "Recall@K": recall,
        "MAP@K": map_k,
        "Coverage": coverage,
        "Users_Evaluated": users_evaluated
    }
    
    return results

def print_results(results):
    """
    Print evaluation results in a formatted way.
    """
    print("\n" + "=" * 60)
    print("POPULARITY RECOMMENDER EVALUATION RESULTS")
    print("=" * 60)
    
    for metric, value in results.items():
        if metric == "Coverage":
            print(f"{metric:20s}: {value:.2f}%")
        elif metric == "Users_Evaluated":
            print(f"{metric:20s}: {value:,}")
        else:
            print(f"{metric:20s}: {value:.4f}")
    
    # Add interpretation
    print("\n" + "=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    
    if results.get("Precision@K", 0) < 0.01:
        print("⚠️ Precision is very low - recommendations rarely match user preferences")
    elif results.get("Precision@K", 0) < 0.05:
        print("📊 Precision is moderate - some recommendations match user preferences")
    else:
        print("✅ Precision is good - recommendations often match user preferences")
    
    if results.get("Coverage", 0) < 10:
        print("⚠️ Coverage is low - recommender only recommends a small portion of the catalog")
    elif results.get("Coverage", 0) < 30:
        print("📊 Coverage is moderate - recommender covers a fair portion of the catalog")
    else:
        print("✅ Coverage is good - recommender covers a wide portion of the catalog")

def debug_paths():
    """
    Debug function to check paths.
    """
    print("=" * 60)
    print("DEBUG - PATHS")
    print("=" * 60)
    print(f"Script location: {Path(__file__).resolve()}")
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"DATA_DIR: {DATA_DIR}")
    print(f"ARTIFACT_DIR: {ARTIFACT_DIR}")
    print(f"MODEL_DIR: {MODEL_DIR}")
    
    print(f"\nChecking if directories exist:")
    print(f"BASE_DIR exists: {BASE_DIR.exists()}")
    print(f"DATA_DIR exists: {DATA_DIR.exists()}")
    print(f"ARTIFACT_DIR exists: {ARTIFACT_DIR.exists()}")
    
    if ARTIFACT_DIR.exists():
        print(f"\n📁 Contents of {ARTIFACT_DIR}:")
        for item in ARTIFACT_DIR.iterdir():
            if item.is_file():
                size = item.stat().st_size / 1024**2
                print(f"  📄 {item.name} ({size:.2f} MB)")
            else:
                print(f"  📁 {item.name}")
    
    # Check if base.py is accessible
    base_path = project_root / "apps" / "api" / "ml" / "recommenders" / "base.py"
    print(f"\nChecking base.py path:")
    print(f"Base.py exists: {base_path.exists()}")
    if base_path.exists():
        print(f"Base.py location: {base_path}")

def main():
    """
    Main execution function.
    """
    print("=" * 60)
    print("POPULARITY RECOMMENDER EVALUATION")
    print("=" * 60)
    
    # Debug paths
    debug_paths()
    
    # Load datasets
    train, test, books = load_datasets()
    
    if train is None or test is None or books is None:
        print("\n❌ Failed to load datasets. Exiting.")
        print("\n💡 Make sure you've run the interaction matrix pipeline first:")
        print("   python apps/api/ml/features/interaction_matrix.py")
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
    
    # Train recommender
    print("\n" + "=" * 60)
    print("TRAINING RECOMMENDER")
    print("=" * 60)
    
    # Fit the model
    recommender.fit((train, books))
    
    # Build ground truth
    ground_truth = build_ground_truth(test)
    
    # Generate recommendations (limit to first 1000 users for speed)
    users_list = list(ground_truth.keys())
    if len(users_list) > 1000:
        print(f"\n⚠️ Limiting evaluation to first 1000 users (out of {len(users_list):,})")
        users_list = users_list[:1000]
    
    recommendations = generate_recommendations(
        recommender,
        users=users_list,
        top_k=10
    )
    
    # Evaluate
    results = evaluate(
        recommendations,
        ground_truth,
        total_books=len(books),
        k=10
    )
    
    # Print results
    print_results(results)
    
    # Save results
    results_path = ARTIFACT_DIR / "evaluation_results_popularity.csv"
    results_df = pd.DataFrame([results])
    results_df.to_csv(results_path, index=False)
    print(f"\n✅ Results saved to: {results_path}")
    
    print("\n✅ Evaluation completed.")

if __name__ == "__main__":
    main()