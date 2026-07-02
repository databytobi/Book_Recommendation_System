"""
Offline Recommendation Evaluator

Phase 4B

This module provides comprehensive offline evaluation of recommendation models
using historical interaction data. It supports multiple evaluation strategies,
caching, and detailed reporting.

Features:
- Holdout evaluation (train/test split per user)
- Cross-validation support
- Caching for performance
- Multiple sampling strategies
- Detailed metrics reporting
- Progress tracking
"""

from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any, Union
import logging
import time
from datetime import datetime
from collections import defaultdict

import numpy as np
import pandas as pd
from tqdm import tqdm

# pyrefly: ignore [missing-import]
from apps.api.ml.evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    hit_rate_at_k,
    average_precision,
    ndcg_at_k,
    mrr_at_k,
    map_at_k,
    catalog_coverage,
    diversity,
    novelty,
    evaluate_recommendations
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RecommendationEvaluator:
    """
    Evaluate recommendation models using historical interactions.
    
    Supports multiple evaluation strategies:
    - Holdout: Split each user's interactions into train/test
    - Cross-validation: K-fold validation per user
    - Time-based: Use earliest interactions for training, latest for testing
    
    Attributes:
    -----------
    ratings : pd.DataFrame
        User-item interaction data
    user_encoder : Optional
        Encoder for user IDs (if available)
    item_encoder : Optional
        Encoder for item IDs (if available)
    _cache : dict
        Cache for computed results
    """

    def __init__(
        self,
        ratings_df: pd.DataFrame,
        user_encoder: Optional[Any] = None,
        item_encoder: Optional[Any] = None,
        cache_results: bool = True
    ):
        """
        Initialize the evaluator.
        
        Parameters:
        -----------
        ratings_df : pd.DataFrame
            User-item interaction data with columns: user_id, isbn, book_rating
        user_encoder : Optional
            Encoder for user IDs (for collaborative models)
        item_encoder : Optional
            Encoder for item IDs (for collaborative models)
        cache_results : bool
            Whether to cache evaluation results for reuse
        """
        self.ratings = ratings_df.copy()
        self.user_encoder = user_encoder
        self.item_encoder = item_encoder
        self.cache_results = cache_results
        self._cache = {}
        self._user_history_cache = {}
        
        # Validate data
        required_cols = ['user_id', 'isbn']
        for col in required_cols:
            if col not in self.ratings.columns:
                raise ValueError(f"Missing required column: {col}")
        
        logger.info(f"Evaluator initialized with {len(self.ratings):,} interactions")
        logger.info(f"  Users: {self.ratings['user_id'].nunique():,}")
        logger.info(f"  Items: {self.ratings['isbn'].nunique():,}")

    def sample_users(
        self,
        min_interactions: int = 20,
        n_users: int = 100,
        random_state: int = 42,
        strategy: str = "random"
    ) -> List:
        """
        Select users for evaluation with various strategies.
        """
        user_counts = self.ratings.groupby("user_id").size()
        eligible = user_counts[user_counts >= min_interactions]
    
        if len(eligible) == 0:
            logger.warning(f"No users with {min_interactions} or more interactions")
            return []
    
        n_users = min(n_users, len(eligible))
    
        # FIX: Ensure seed is non-negative
        seed = abs(random_state) % (2**31 - 1)
        rng = np.random.default_rng(seed)
        
        if strategy == "random":
            selected = rng.choice(eligible.index, size=n_users, replace=False)
    
        elif strategy == "most_active":
            selected = eligible.nlargest(n_users).index
    
        elif strategy == "least_active":
            selected = eligible.nsmallest(n_users).index
    
        elif strategy == "stratified":
        # Divide users into bins by activity level
            bins = pd.qcut(eligible, q=min(5, len(eligible)), labels=False)
            users_by_bin = defaultdict(list)
            for user, bin_id in zip(eligible.index, bins):
                users_by_bin[bin_id].append(user)
        
            # Sample evenly from each bin
            per_bin = n_users // len(users_by_bin)
            selected = []
            for bin_id, users in users_by_bin.items():
                if len(users) >= per_bin:
                    selected.extend(rng.choice(users, size=per_bin, replace=False))
            else:
                selected.extend(users)
        
        # Trim if we oversampled
            selected = selected[:n_users]
    
        else:
            raise ValueError(f"Unknown sampling strategy: {strategy}")
    
        logger.info(f"Sampled {len(selected)} users (strategy: {strategy})")
        logger.info(f"  Interactions range: {eligible.min():,} - {eligible.max():,}")
    
        return list(selected)

    def build_holdout(
    self,
    user_id: Union[str, int],
    test_fraction: float = 0.2,
    min_test_items: int = 1,
    random_state: int = 42,
    time_col: Optional[str] = None
        ) -> Optional[Tuple[Set[str], Set[str]]]:
        """
        Split user interactions into train and test sets.
        
        Parameters:
        -----------
        user_id : str or int
            User ID to split
        test_fraction : float
            Fraction of interactions to use for testing
        min_test_items : int
            Minimum number of test items required
        random_state : int
            Random seed for reproducibility
        time_col : str, optional
            Column name for timestamp. If provided, uses time-based split.
        
        Returns:
        --------
        Tuple[Set[str], Set[str]] or None: (train_items, test_items)
        """
        cache_key = f"holdout_{user_id}_{test_fraction}_{min_test_items}_{random_state}"
        if cache_key in self._cache:
            return self._cache[cache_key]
    
        user_data = self.ratings[self.ratings["user_id"] == user_id]
        
        if len(user_data) < min_test_items + 1:
            return None
    
        books = user_data["isbn"].dropna().unique().tolist()
    
        if len(books) < min_test_items + 1:
            return None
    
        # FIX: Ensure the seed is non-negative
        # Use abs() to make hash positive, and modulo to keep it manageable
        seed = abs(hash(str(user_id)) + random_state) % (2**31 - 1)
        rng = np.random.default_rng(seed)
    
        # Time-based split if time column provided
        if time_col and time_col in user_data.columns:
            user_data = user_data.sort_values(time_col)
            split_idx = int(len(user_data) * (1 - test_fraction))
            train_books = set(user_data.iloc[:split_idx]["isbn"].unique())
            test_books = set(user_data.iloc[split_idx:]["isbn"].unique())
        else:
            # Random split
            n_test = max(min_test_items, int(len(books) * test_fraction))
            n_test = min(n_test, len(books) - 1)
        
            test_books = set(rng.choice(books, size=n_test, replace=False))
            train_books = set(books) - test_books
    
        if len(test_books) < min_test_items or len(train_books) == 0:
            return None
    
        result = (train_books, test_books)
    
        if self.cache_results:
            self._cache[cache_key] = result
    
        return result

    def get_user_history(
        self,
        user_id: Union[str, int],
        top_k: int = 20,
        include_ratings: bool = False
    ) -> pd.DataFrame:
        """
        Get a user's interaction history sorted by rating.
        
        Parameters:
        -----------
        user_id : str or int
            User ID
        top_k : int
            Number of top interactions to return
        include_ratings : bool
            Whether to include rating values
        
        Returns:
        --------
        pd.DataFrame: User's interaction history
        """
        cache_key = f"history_{user_id}_{top_k}_{include_ratings}"
        if cache_key in self._user_history_cache:
            return self._user_history_cache[cache_key]
        
        user_data = self.ratings[self.ratings["user_id"] == user_id].copy()
        
        if user_data.empty:
            return pd.DataFrame()
        
        # Sort by rating if available, otherwise by timestamp
        if "book_rating" in user_data.columns:
            user_data = user_data.sort_values("book_rating", ascending=False)
        elif "timestamp" in user_data.columns:
            user_data = user_data.sort_values("timestamp", ascending=False)
        
        if include_ratings:
            result = user_data.head(top_k)[["isbn", "book_rating" if "book_rating" in user_data.columns else "isbn"]]
        else:
            result = user_data.head(top_k)[["isbn"]]
        
        self._user_history_cache[cache_key] = result
        return result

    def evaluate_user(
        self,
        recommender: Any,
        user_id: Union[str, int],
        k: int = 10,
        test_fraction: float = 0.2,
        min_test_items: int = 1,
        random_state: int = 42,
        time_col: Optional[str] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate a single user using holdout split.
        
        Parameters:
        -----------
        recommender : Any
            Recommender object with a `recommend_for_user` method
        user_id : str or int
            User ID to evaluate
        k : int
            Number of recommendations to evaluate
        test_fraction : float
            Fraction of interactions to hold out for testing
        min_test_items : int
            Minimum number of test items required
        random_state : int
            Random seed for reproducibility
        time_col : str, optional
            Column name for timestamp (for time-based split)
        verbose : bool
            Whether to print debug information
        
        Returns:
        --------
        Dict[str, Any]: Evaluation metrics for the user
        """
        # Try to get from cache
        cache_key = f"user_{user_id}_{k}_{test_fraction}_{random_state}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Build holdout split
        split = self.build_holdout(
            user_id,
            test_fraction=test_fraction,
            min_test_items=min_test_items,
            random_state=random_state,
            time_col=time_col
        )
        
        if split is None:
            return {}
        
        train_books, test_books = split
        
        # Get recommendations
        try:
            if verbose:
                logger.info(f"Evaluating user {user_id}")
            
            # Check if recommender has recommend_for_user method
            if hasattr(recommender, 'recommend_for_user'):
                recommendations = recommender.recommend_for_user(
                    user_id=user_id,
                    top_k=k
                )
            else:
                # Try alternative method
                recommendations = recommender.recommend(
                    user_id=user_id,
                    top_k=k
                )
            
            if recommendations is None or recommendations.empty:
                return {}
            
            # Extract ISBNs
            if "isbn" in recommendations.columns:
                recommended = recommendations["isbn"].tolist()
            elif "item_id" in recommendations.columns:
                recommended = recommendations["item_id"].tolist()
            else:
                # Try first column
                recommended = recommendations.iloc[:, 0].tolist()
            
            # Calculate metrics
            metrics = {
                "precision": precision_at_k(recommended, test_books, k),
                "recall": recall_at_k(recommended, test_books, k),
                "hit_rate": hit_rate_at_k(recommended, test_books, k),
                "ap": average_precision(recommended, test_books, k),
                "ndcg": ndcg_at_k(recommended, test_books, k),
                "mrr": mrr_at_k(recommended, test_books, k),
                "n_test_items": len(test_books),
                "n_train_items": len(train_books),
                "user_id": user_id
            }
            
            if verbose:
                logger.info(f"User {user_id}: Precision@{k}={metrics['precision']:.4f}")
            
            if self.cache_results:
                self._cache[cache_key] = metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"Evaluation error for user {user_id}: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            return {}

    def evaluate_model(
        self,
        recommender: Any,
        users: Optional[List] = None,
        k: int = 10,
        test_fraction: float = 0.2,
        min_interactions: int = 20,
        n_users: int = 100,
        random_state: int = 42,
        time_col: Optional[str] = None,
        show_progress: bool = True,
        verbose: bool = False,
        return_details: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate a recommendation model across multiple users.
        
        Parameters:
        -----------
        recommender : Any
            Recommender object with a `recommend_for_user` method
        users : List, optional
            List of user IDs to evaluate. If None, sampled automatically.
        k : int
            Number of recommendations to evaluate
        test_fraction : float
            Fraction of interactions to hold out for testing
        min_interactions : int
            Minimum interactions for a user to be included
        n_users : int
            Number of users to sample (if users not provided)
        random_state : int
            Random seed for reproducibility
        time_col : str, optional
            Column name for timestamp (for time-based split)
        show_progress : bool
            Whether to show progress bar
        verbose : bool
            Whether to print detailed logs
        return_details : bool
            Whether to return detailed per-user results
        
        Returns:
        --------
        Dict[str, Any]: Evaluation results including aggregated metrics
        """
        start_time = time.time()
        
        # Sample users if not provided
        if users is None:
            users = self.sample_users(
                min_interactions=min_interactions,
                n_users=n_users,
                random_state=random_state
            )
        
        if not users:
            logger.warning("No users available for evaluation")
            return {"users_evaluated": 0, "error": "No users available"}
        
        logger.info(f"Evaluating {len(users)} users...")
        
        # Evaluate each user
        results = []
        progress = tqdm(users, desc="Evaluating users", disable=not show_progress)
        
        for user_id in progress:
            metrics = self.evaluate_user(
                recommender=recommender,
                user_id=user_id,
                k=k,
                test_fraction=test_fraction,
                min_test_items=1,
                random_state=random_state + hash(str(user_id)) % 1000,
                time_col=time_col,
                verbose=verbose
            )
            
            if metrics:
                results.append(metrics)
                progress.set_postfix({"users": len(results)})
        
        if not results:
            logger.warning("No users could be evaluated")
            return {"users_evaluated": 0, "error": "No users evaluated"}
        
        # Aggregate results
        df = pd.DataFrame(results)
        
        aggregated = {
            "users_evaluated": len(df),
            "precision@k": float(df["precision"].mean()),
            "recall@k": float(df["recall"].mean()),
            "hit_rate@k": float(df["hit_rate"].mean()),
            "map@k": float(df["ap"].mean()),
            "ndcg@k": float(df["ndcg"].mean()),
            "mrr@k": float(df["mrr"].mean()),
            "avg_test_items": float(df["n_test_items"].mean()),
            "avg_train_items": float(df["n_train_items"].mean()),
            "evaluation_time": time.time() - start_time
        }
        
        # Add standard deviation
        aggregated.update({
            "precision_std": float(df["precision"].std()),
            "recall_std": float(df["recall"].std()),
            "ndcg_std": float(df["ndcg"].std())
        })
        
        logger.info(f"Evaluation complete: {len(df)} users")
        logger.info(f"  Precision@{k}: {aggregated['precision@k']:.4f}")
        logger.info(f"  Recall@{k}: {aggregated['recall@k']:.4f}")
        logger.info(f"  NDCG@{k}: {aggregated['ndcg@k']:.4f}")
        logger.info(f"  Time: {aggregated['evaluation_time']:.2f}s")
        
        if return_details:
            return {
                "aggregated": aggregated,
                "per_user": df.to_dict(orient="records")
            }
        
        return aggregated

    def cross_validate(
        self,
        recommender: Any,
        users: Optional[List] = None,
        k: int = 10,
        n_folds: int = 5,
        min_interactions: int = 20,
        n_users: int = 50,
        random_state: int = 42,
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Perform K-fold cross-validation for a recommender.
        
        Parameters:
        -----------
        recommender : Any
            Recommender object with a `recommend_for_user` method
        users : List, optional
            List of user IDs to evaluate. If None, sampled automatically.
        k : int
            Number of recommendations to evaluate
        n_folds : int
            Number of folds for cross-validation
        min_interactions : int
            Minimum interactions for a user to be included
        n_users : int
            Number of users to sample (if users not provided)
        random_state : int
            Random seed for reproducibility
        show_progress : bool
            Whether to show progress bar
        
        Returns:
        --------
        Dict[str, Any]: Cross-validation results
        """
        if users is None:
            users = self.sample_users(
                min_interactions=min_interactions,
                n_users=n_users,
                random_state=random_state
            )
        
        if not users:
            return {"error": "No users available"}
        
        logger.info(f"Performing {n_folds}-fold cross-validation on {len(users)} users")
        
        fold_results = []
        
        for fold in range(n_folds):
            logger.info(f"Fold {fold + 1}/{n_folds}")
            
            # Different random state for each fold
            fold_state = random_state + fold * 1000
            
            # Evaluate with different test fractions
            # For cross-validation, we use larger test fractions
            test_fraction = 1.0 / n_folds
            
            result = self.evaluate_model(
                recommender=recommender,
                users=users,
                k=k,
                test_fraction=test_fraction,
                random_state=fold_state,
                show_progress=show_progress,
                verbose=False
            )
            
            if "users_evaluated" in result and result["users_evaluated"] > 0:
                fold_results.append(result)
        
        if not fold_results:
            return {"error": "No folds completed"}
        
        # Aggregate fold results
        aggregated = {
            "n_folds": len(fold_results),
            "n_users": fold_results[0].get("users_evaluated", 0),
            "precision@k_mean": np.mean([r.get("precision@k", 0) for r in fold_results]),
            "precision@k_std": np.std([r.get("precision@k", 0) for r in fold_results]),
            "recall@k_mean": np.mean([r.get("recall@k", 0) for r in fold_results]),
            "recall@k_std": np.std([r.get("recall@k", 0) for r in fold_results]),
            "ndcg@k_mean": np.mean([r.get("ndcg@k", 0) for r in fold_results]),
            "ndcg@k_std": np.std([r.get("ndcg@k", 0) for r in fold_results]),
            "fold_results": fold_results
        }
        
        logger.info(f"Cross-validation complete:")
        logger.info(f"  Precision@{k}: {aggregated['precision@k_mean']:.4f} ± {aggregated['precision@k_std']:.4f}")
        logger.info(f"  Recall@{k}: {aggregated['recall@k_mean']:.4f} ± {aggregated['recall@k_std']:.4f}")
        
        return aggregated

    def evaluate_with_ground_truth(
        self,
        recommendations: Dict[str, List[str]],
        ground_truth: Dict[str, Set[str]],
        k: int = 10,
        total_items: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Evaluate recommendations against ground truth data.
        
        Parameters:
        -----------
        recommendations : Dict[str, List[str]]
            Dictionary mapping user_id to list of recommended items
        ground_truth : Dict[str, Set[str]]
            Dictionary mapping user_id to set of relevant items
        k : int
            Number of recommendations to evaluate
        total_items : int, optional
            Total number of items in catalog (for coverage metrics)
        
        Returns:
        --------
        Dict[str, float]: Evaluation metrics
        """
        return evaluate_recommendations(
            recommendations=recommendations,
            ground_truth=ground_truth,
            k=k,
            total_items=total_items
        )

    def compare_models(
        self,
        models: Dict[str, Any],
        users: Optional[List] = None,
        k: int = 10,
        test_fraction: float = 0.2,
        min_interactions: int = 20,
        n_users: int = 100,
        random_state: int = 42,
        show_progress: bool = True
    ) -> pd.DataFrame:
        """
        Compare multiple recommendation models.
        
        Parameters:
        -----------
        models : Dict[str, Any]
            Dictionary mapping model_name -> recommender object
        users : List, optional
            List of user IDs to evaluate. If None, sampled automatically.
        k : int
            Number of recommendations to evaluate
        test_fraction : float
            Fraction of interactions to hold out for testing
        min_interactions : int
            Minimum interactions for a user to be included
        n_users : int
            Number of users to sample (if users not provided)
        random_state : int
            Random seed for reproducibility
        show_progress : bool
            Whether to show progress bar
        
        Returns:
        --------
        pd.DataFrame: Comparison results
        """
        if users is None:
            users = self.sample_users(
                min_interactions=min_interactions,
                n_users=n_users,
                random_state=random_state
            )
        
        if not users:
            logger.warning("No users available for comparison")
            return pd.DataFrame()
        
        results = []
        
        for model_name, model in models.items():
            logger.info(f"Evaluating model: {model_name}")
            
            # Use the same users for fair comparison
            result = self.evaluate_model(
                recommender=model,
                users=users,
                k=k,
                test_fraction=test_fraction,
                random_state=random_state,
                show_progress=show_progress,
                verbose=False
            )
            
            if result and "users_evaluated" in result and result["users_evaluated"] > 0:
                result["model_name"] = model_name
                results.append(result)
        
        if not results:
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        
        # Reorder columns for better readability
        cols = ["model_name", "users_evaluated", "precision@k", "recall@k", 
                "hit_rate@k", "map@k", "ndcg@k", "mrr@k"]
        available_cols = [c for c in cols if c in df.columns]
        df = df[available_cols]
        
        # Sort by NDCG
        if "ndcg@k" in df.columns:
            df = df.sort_values("ndcg@k", ascending=False)
        
        logger.info("\nModel Comparison Results:")
        logger.info(df.to_string(index=False))
        
        return df

    def clear_cache(self) -> None:
        """Clear all cached results."""
        self._cache.clear()
        self._user_history_cache.clear()
        logger.info("Cache cleared")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the evaluation data.
        
        Returns:
        --------
        Dict[str, Any]: Dataset statistics
        """
        user_counts = self.ratings.groupby("user_id").size()
        item_counts = self.ratings.groupby("isbn").size()
        
        return {
            "total_interactions": len(self.ratings),
            "unique_users": self.ratings["user_id"].nunique(),
            "unique_items": self.ratings["isbn"].nunique(),
            "avg_interactions_per_user": user_counts.mean(),
            "median_interactions_per_user": user_counts.median(),
            "min_interactions_per_user": user_counts.min(),
            "max_interactions_per_user": user_counts.max(),
            "avg_interactions_per_item": item_counts.mean(),
            "median_interactions_per_item": item_counts.median(),
            "sparsity": 1 - (len(self.ratings) / (self.ratings["user_id"].nunique() * self.ratings["isbn"].nunique())),
            "cache_size": len(self._cache)
        }


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def evaluate_recommender(
    recommender: Any,
    ratings: pd.DataFrame,
    k: int = 10,
    n_users: int = 100,
    min_interactions: int = 20,
    test_fraction: float = 0.2,
    random_state: int = 42,
    return_details: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to evaluate a recommender in one call.
    
    Parameters:
    -----------
    recommender : Any
        Recommender object with a `recommend_for_user` method
    ratings : pd.DataFrame
        User-item interaction data
    k : int
        Number of recommendations to evaluate
    n_users : int
        Number of users to evaluate
    min_interactions : int
        Minimum interactions for a user to be included
    test_fraction : float
        Fraction of interactions to hold out for testing
    random_state : int
        Random seed for reproducibility
    return_details : bool
        Whether to return detailed per-user results
    
    Returns:
    --------
    Dict[str, Any]: Evaluation results
    """
    evaluator = RecommendationEvaluator(ratings)
    return evaluator.evaluate_model(
        recommender=recommender,
        k=k,
        n_users=n_users,
        min_interactions=min_interactions,
        test_fraction=test_fraction,
        random_state=random_state,
        return_details=return_details
    )


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    # Example usage
    import sys
    from pathlib import Path
    
    # Load sample data
    data_dir = Path(__file__).resolve().parents[4] / "data" / "processed"
    ratings_path = data_dir / "ratings" / "ratings_cleaned.parquet"
    
    if ratings_path.exists():
        ratings = pd.read_parquet(ratings_path)
        
        # Create evaluator
        evaluator = RecommendationEvaluator(ratings)
        
        # Get statistics
        stats = evaluator.get_statistics()
        print("\n📊 Dataset Statistics:")
        for key, value in stats.items():
            if isinstance(value, float) and key != "sparsity":
                print(f"  {key}: {value:,.2f}")
            else:
                print(f"  {key}: {value:,.2f}" if isinstance(value, float) else f"  {key}: {value}")
        
        # Sample users
        users = evaluator.sample_users(n_users=10, min_interactions=10)
        print(f"\n✅ Sampled {len(users)} users")
        
        # Create a simple popularity recommender for testing
        class DummyRecommender:
            def recommend_for_user(self, user_id, top_k=10):
                # Return random books for testing
                import random
                all_items = ratings["isbn"].unique().tolist()
                return pd.DataFrame({
                    "isbn": random.sample(all_items, min(top_k, len(all_items)))
                })
        
        dummy = DummyRecommender()
        
        # Evaluate
        results = evaluator.evaluate_model(
            recommender=dummy,
            users=users[:5],
            k=5,
            show_progress=True
        )
        
        print("\n📊 Evaluation Results:")
        for key, value in results.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value}")
    else:
        print("No ratings data found. Please provide a valid ratings file.")    