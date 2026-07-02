from pathlib import Path
import sys

# Add the parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))


# pyrefly: ignore [missing-import]
from popularity_recommender import PopularityRecommender



class PopularityService:
    """
    Service layer for popularity-based recommendations.
    """

    def __init__(self, train_path=None, books_path=None):
        """
        Initialize the popularity service.
        
        Parameters:
        -----------
        train_path : Path, optional
            Path to train interactions parquet file.
        books_path : Path, optional
            Path to books parquet file.
        """
        # Get project root
        # This file is at: apps/api/ml/popularity/popularity_service.py
        # Go up 5 levels to project root: popularity -> ml -> api -> apps -> project_root
        project_root = Path(__file__).resolve().parents[4]
        
        if train_path is None:
            train_path = project_root / "apps" / "api" / "ml" / "artifacts" / "train_interactions.parquet"
        
        if books_path is None:
            books_path = project_root / "data" / "processed" / "integrated" / "master_books_deduplicated.parquet"
            if not books_path.exists():
                books_path = project_root / "data" / "processed" / "integrated" / "master_books.parquet"
        
        print(f"Project root: {project_root}")
        print(f"Train path: {train_path}")
        print(f"Books path: {books_path}")
        
        self.recommender = PopularityRecommender(
            min_ratings=50,
            diversity_weight=0.3,
            recency_weight=0.2
        )
        
        # Try to load existing model, or train if not found
        model_path = Path(__file__).resolve().parent / "models" / "popularity_recommender.pkl"
        
        if model_path.exists():
            print(f"✅ Loading existing model from: {model_path}")
            try:
                self.recommender.load_model(str(model_path))
            except Exception as e:
                print(f"⚠️ Error loading model: {e}")
                print("🔄 Training new model...")
                self.recommender.train(train_path=train_path, books_path=books_path)
        else:
            print("🔄 No existing model found. Training new model...")
            self.recommender.train(train_path=train_path, books_path=books_path)
            
        print("✅ PopularityService initialized")

    def homepage(self, top_k=20):
        """
        Homepage recommendations.
        Returns diverse popular books for the homepage.
        """
        if not self.recommender.is_fitted:
            self.recommender.train()
            
        return self.recommender.recommend(
            top_k=top_k,
            diversify=True
        )

    def trending(self, top_k=20):
        """
        Trending recommendations.
        Currently uses popularity with recency weighting.
        """
        if not self.recommender.is_fitted:
            self.recommender.train()
            
        return self.recommender.recommend(
            top_k=top_k,
            diversify=True
        )

    def category(self, category, top_k=20):
        """
        Category-specific recommendations.
        """
        if not self.recommender.is_fitted:
            self.recommender.train()
            
        try:
            return self.recommender.recommend_by_category(category, top_k=top_k)
        except Exception as e:
            print(f"⚠️ Error getting category recommendations: {e}")
            books = self.recommender.recommend(
                top_k=100,
                diversify=False
            )
            if 'category' in books.columns:
                books = books[books["category"] == category]
                return books.head(top_k)
            return books.head(top_k)

    def cold_start(self, top_k=20):
        """
        Cold-start / new user recommendations.
        """
        return self.homepage(top_k=top_k)

    def explain(self, isbn):
        """
        Get explanation for why a book is recommended.
        """
        if not self.recommender.is_fitted:
            self.recommender.train()
            
        return self.recommender.explain_recommendation(isbn)

    def get_popular_books(self, top_k=50):
        """
        Get most popular books without diversity filtering.
        """
        if not self.recommender.is_fitted:
            self.recommender.train()
            
        return self.recommender.recommend(
            top_k=top_k,
            diversify=False
        )

    def refresh_model(self):
        """
        Force retrain the model with current data.
        """
        print("🔄 Retraining popularity model...")
        self.recommender.train()
        print("✅ Model refreshed")
        
    def get_stats(self):
        """
        Get model statistics.
        """
        if not self.recommender.is_fitted:
            return {"status": "not_fitted"}
            
        stats = {
            "status": "fitted",
            "total_books": len(self.recommender.popularity_df) if hasattr(self.recommender, 'popularity_df') and self.recommender.popularity_df is not None else 0,
            "min_ratings": self.recommender.min_ratings,
            "global_mean": float(self.recommender.global_mean) if self.recommender.global_mean else None,
        }
        
        if hasattr(self.recommender, 'popularity_df') and self.recommender.popularity_df is not None and 'category' in self.recommender.popularity_df.columns:
            stats["categories"] = self.recommender.popularity_df['category'].nunique()
            category_counts = self.recommender.popularity_df['category'].value_counts().head(10).to_dict()
            stats["top_categories"] = {k: int(v) for k, v in category_counts.items()}
            
        return stats


# Singleton instance
_popularity_service = None


def get_popularity_service():
    """
    Get or create the singleton PopularityService instance.
    """
    global _popularity_service
    if _popularity_service is None:
        _popularity_service = PopularityService()
    return _popularity_service