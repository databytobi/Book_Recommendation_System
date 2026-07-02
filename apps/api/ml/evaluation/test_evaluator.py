"""
Recommendation Evaluation Test Script

Tests the offline evaluation pipeline with the hybrid recommender.
Provides comprehensive metrics and visual output.
"""

from pathlib import Path
import sys
import time
from datetime import datetime
from typing import Dict, Any
import logging

import pandas as pd
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import from the same directory
# pyrefly: ignore [missing-import]
from apps.api.ml.evaluation.evaluator import RecommendationEvaluator
# pyrefly: ignore [missing-import]
from apps.api.ml.hybrid.hybrid_recommender import HybridRecommender


def print_header(title: str, char: str = "=", length: int = 60):
    """Print a formatted header."""
    print("\n" + char * length)
    print(f"{title.upper()}")
    print(char * length)


def print_subheader(title: str, char: str = "-", length: int = 40):
    """Print a formatted subheader."""
    print(f"\n{title}")
    print(char * length)


def print_metric(name: str, value: Any, precision: int = 4):
    """Print a single metric with consistent formatting."""
    if isinstance(value, float):
        if value == 0.0:
            formatted = "0.0000"
        elif "std" in name or "time" in name:
            formatted = f"{value:.4f}"
        else:
            formatted = f"{value:.{precision}f}"
    elif isinstance(value, int):
        formatted = f"{value:,}"
    else:
        formatted = str(value)
    print(f"  {name:30s}: {formatted}")


def print_results(results: Dict[str, Any], title: str = "Evaluation Results"):
    """Print all results in a formatted way."""
    print_header(title)
    
    # Group metrics
    core_metrics = ['precision@k', 'recall@k', 'hit_rate@k', 'map@k', 'ndcg@k', 'mrr@k']
    stats_metrics = ['users_evaluated', 'avg_test_items', 'avg_train_items']
    quality_metrics = ['precision_std', 'recall_std', 'ndcg_std']
    
    # Print core metrics
    print("\n📊 Core Metrics:")
    print("-" * 40)
    for metric in core_metrics:
        if metric in results:
            print_metric(metric, results[metric])
    
    # Print statistics
    print("\n📈 Statistics:")
    print("-" * 40)
    for metric in stats_metrics:
        if metric in results:
            print_metric(metric, results[metric])
    
    # Print quality metrics
    has_std = any(m in results for m in quality_metrics)
    if has_std:
        print("\n🎯 Quality Metrics (Std Dev):")
        print("-" * 40)
        for metric in quality_metrics:
            if metric in results:
                print_metric(metric, results[metric])
    
    # Print timing
    if 'evaluation_time' in results:
        print("\n⏱️ Timing:")
        print("-" * 40)
        print_metric("evaluation_time", results['evaluation_time'])


def load_ratings():
    """
    Load ratings data for evaluation.
    
    Returns:
    --------
    pd.DataFrame: Ratings data
    """
    ARTIFACT_DIR = (
        Path(__file__)
        .resolve()
        .parents[3]  # Go up to project root (evaluation -> ml -> api -> apps -> project_root)
        / "apps"
        / "api"
        / "ml"
        / "artifacts"
    )
    
    ratings_path = ARTIFACT_DIR / "train_ratings.parquet"
    
    print(f"\n📂 Looking for ratings at:")
    print(f"  {ratings_path}")
    
    if not ratings_path.exists():
        # Try alternative path
        alt_path = Path(__file__).resolve().parents[4] / "data" / "processed" / "ratings" / "ratings_cleaned.parquet"
        print(f"\n📂 Trying alternative path:")
        print(f"  {alt_path}")
        
        if alt_path.exists():
            ratings_path = alt_path
        else:
            print(f"\n❌ Ratings file not found!")
            print(f"  Please run the collaborative training first:")
            print(f"  python apps/api/ml/collaborative/train_collaborative.py")
            return None
    
    try:
        ratings = pd.read_parquet(ratings_path)
        print(f"\n✅ Ratings loaded successfully!")
        print(f"  Total interactions: {len(ratings):,}")
        print(f"  Unique users: {ratings['user_id'].nunique():,}")
        print(f"  Unique items: {ratings['isbn'].nunique():,}")
        
        # Show rating statistics
        if 'book_rating' in ratings.columns:
            print(f"  Rating range: {ratings['book_rating'].min():.1f} - {ratings['book_rating'].max():.1f}")
            print(f"  Average rating: {ratings['book_rating'].mean():.2f}")
        
        # Show sparsity
        total_possible = ratings['user_id'].nunique() * ratings['isbn'].nunique()
        sparsity = 1 - (len(ratings) / total_possible)
        print(f"  Sparsity: {sparsity * 100:.2f}%")
        
        return ratings
        
    except Exception as e:
        print(f"\n❌ Error loading ratings: {e}")
        return None


def test_evaluation_pipeline():
    """
    Main test function for the evaluation pipeline.
    """
    print_header("RECOMMENDATION EVALUATION TEST")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ============================================================
    # LOAD DATA
    # ============================================================
    
    print_header("STEP 1: LOAD DATA")
    
    ratings = load_ratings()
    
    if ratings is None:
        print("\n❌ Failed to load ratings. Exiting.")
        return None, None
    
    # ============================================================
    # SETUP EVALUATOR
    # ============================================================
    
    print_header("STEP 2: SETUP EVALUATOR")
    
    try:
        evaluator = RecommendationEvaluator(ratings)
        print("\n✅ Evaluator initialized successfully")
        
        # Get dataset statistics
        stats = evaluator.get_statistics()
        print_subheader("Dataset Statistics")
        
        # Show key stats
        for key, value in stats.items():
            if key in ['total_interactions', 'unique_users', 'unique_items']:
                print(f"  {key}: {value:,}")
            elif key in ['avg_interactions_per_user', 'avg_interactions_per_item']:
                print(f"  {key}: {value:.2f}")
            elif key == 'sparsity':
                print(f"  {key}: {value * 100:.2f}%")
        
    except Exception as e:
        print(f"\n❌ Error setting up evaluator: {e}")
        return None, None
    
    # ============================================================
    # SAMPLE USERS
    # ============================================================
    
    print_header("STEP 3: SAMPLE USERS")
    
    try:
        # Try different strategies
        users = evaluator.sample_users(
            min_interactions=20,
            n_users=50,
            strategy='most_active'
        )
        
        if len(users) == 0:
            print("\n⚠️ No users with 20+ interactions. Trying with 10...")
            users = evaluator.sample_users(
                min_interactions=10,
                n_users=50,
                strategy='most_active'
            )
        
        if len(users) == 0:
            print("\n⚠️ No users with 10+ interactions. Trying with 5...")
            users = evaluator.sample_users(
                min_interactions=5,
                n_users=50,
                strategy='most_active'
            )
        
        print(f"\n✅ Using {len(users)} users for evaluation")
        
        if len(users) > 0:
            print(f"  Sample users: {users[:5]}")
        
    except Exception as e:
        print(f"\n❌ Error sampling users: {e}")
        return None, None
    
    # ============================================================
    # LOAD HYBRID RECOMMENDER
    # ============================================================
    
    print_header("STEP 4: LOAD HYBRID RECOMMENDER")
    
    try:
        print("\n🔄 Initializing Hybrid Recommender...")
        start_time = time.time()
        
        hybrid = HybridRecommender()
        
        load_time = time.time() - start_time
        print(f"\n✅ Hybrid Recommender loaded in {load_time:.2f}s")
        
        # Get recommender stats
        try:
            stats = hybrid.get_stats()
            if stats and 'weights' in stats:
                weights = stats['weights']
                print(f"\n  Weights:")
                print(f"    Collaborative: {weights.get('collaborative', 0):.2f}")
                print(f"    Content: {weights.get('content', 0):.2f}")
                print(f"    Popularity: {weights.get('popularity', 0):.2f}")
        except:
            pass
        
    except Exception as e:
        print(f"\n❌ Error loading hybrid recommender: {e}")
        import traceback
        traceback.print_exc()
        return None, None
    
    # ============================================================
    # EVALUATE
    # ============================================================
    
    print_header("STEP 5: EVALUATE RECOMMENDER")
    
    results = {}
    
    try:
        # Evaluate with different K values
        k_values = [5, 10, 20]
        
        for k in k_values:
            print(f"\n📊 Evaluating with K={k}...")
            print("-" * 40)
            
            start_time = time.time()
            
            results_k = evaluator.evaluate_model(
                recommender=hybrid,
                users=users,
                k=k,
                test_fraction=0.2,
                show_progress=True,
                verbose=False
            )
            
            eval_time = time.time() - start_time
            
            if results_k and 'users_evaluated' in results_k and results_k['users_evaluated'] > 0:
                print(f"\n✅ Evaluation complete ({eval_time:.2f}s)")
                print(f"  Users evaluated: {results_k.get('users_evaluated', 0)}")
                
                # Store results
                results[f'k_{k}'] = results_k
                
                # Show key metrics
                print(f"\n  Key Metrics:")
                print(f"    Precision@{k}: {results_k.get('precision@k', 0):.4f}")
                print(f"    Recall@{k}: {results_k.get('recall@k', 0):.4f}")
                print(f"    NDCG@{k}: {results_k.get('ndcg@k', 0):.4f}")
                print(f"    MAP@{k}: {results_k.get('map@k', 0):.4f}")
                
                # Interpretation
                precision = results_k.get('precision@k', 0)
                recall = results_k.get('recall@k', 0)
                
                print(f"\n  Interpretation:")
                if precision > 0.1:
                    print(f"    ✅ Precision is good ({precision:.2%} of recommendations are relevant)")
                elif precision > 0.05:
                    print(f"    📊 Precision is moderate ({precision:.2%} of recommendations are relevant)")
                else:
                    print(f"    ⚠️ Precision is low ({precision:.2%} of recommendations are relevant)")
                
                if recall > 0.1:
                    print(f"    ✅ Recall is good ({recall:.2%} of relevant items found)")
                elif recall > 0.05:
                    print(f"    📊 Recall is moderate ({recall:.2%} of relevant items found)")
                else:
                    print(f"    ⚠️ Recall is low ({recall:.2%} of relevant items found)")
            else:
                print(f"\n⚠️ No results for K={k}")
    
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
    
    # ============================================================
    # DISPLAY RESULTS
    # ============================================================
    
    if results:
        print_header("STEP 6: RESULTS SUMMARY")
        
        # Show results for each K
        for k, results_k in sorted(results.items()):
            k_value = int(k.split('_')[1])
            print_header(f"K={k_value} Results", char="-")
            
            print_results(results_k)
        
        # ============================================================
        # COMPARE ACROSS K VALUES
        # ============================================================
        
        print_header("STEP 7: COMPARISON ACROSS K VALUES")
        
        comparison_data = []
        for k, results_k in sorted(results.items()):
            k_value = int(k.split('_')[1])
            comparison_data.append({
                'K': k_value,
                'Precision': results_k.get('precision@k', 0),
                'Recall': results_k.get('recall@k', 0),
                'NDCG': results_k.get('ndcg@k', 0),
                'MAP': results_k.get('map@k', 0),
                'Users': results_k.get('users_evaluated', 0)
            })
        
        if comparison_data:
            df = pd.DataFrame(comparison_data)
            print("\n📊 Performance by K Value:")
            print("-" * 50)
            print(df.to_string(index=False))
            
            # Find best K
            best_k_row = df.loc[df['NDCG'].idxmax()]
            print(f"\n🏆 Best Performance:")
            print(f"  K={best_k_row['K']}: NDCG={best_k_row['NDCG']:.4f}")
    
    # ============================================================
    # SUMMARY
    # ============================================================
    
    print_header("EVALUATION COMPLETE")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n📊 Summary:")
    print(f"  Users evaluated: {len(users)}")
    print(f"  K values tested: {len(k_values) if 'k_values' in dir() else 0}")
    print(f"  Total results: {len(results)}")
    
    # Final recommendations
    print("\n💡 Recommendations:")
    print("  1. Use K=10 for balanced precision/recall")
    print("  2. Consider increasing test_fraction for more robust evaluation")
    print("  3. Run cross-validation for more reliable results")
    print("  4. Compare with other models to validate performance")
    
    return results, users


def main():
    """
    Main execution function.
    """
    try:
        results, users = test_evaluation_pipeline()
        
        if results is None:
            print("\n❌ Evaluation failed!")
            sys.exit(1)
        
        print("\n✅ All tests completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Evaluation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()