import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, List, Dict, Any

# Import from parent directory
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from base import BaseRecommender


class PopularityRecommender(BaseRecommender):
    """
    Enhanced popularity-based recommendation system with:
    - Category diversity to avoid single-series dominance
    - Recency weighting for newer books
    - Duplicate handling
    """
    
    def __init__(self, min_ratings: int = 50, diversity_weight: float = 0.3, recency_weight: float = 0.2):
        super().__init__()
        self.min_ratings = min_ratings
        self.diversity_weight = diversity_weight
        self.recency_weight = recency_weight
        self.popularity_df = None
        self.global_mean = None
        self.current_year = datetime.now().year
    
    def _extract_categories(self, books_df: pd.DataFrame) -> Dict[str, str]:
        """Extract main category/genre from book title or metadata."""
        categories = {}
        
        category_keywords = {
            'Fantasy': ['harry potter', 'lord of the rings', 'fantasy', 'wizard', 'magic', 'dragon', 'hobbit'],
            'Classic': ['classic', 'to kill a mockingbird', 'pride and prejudice', 'great gatsby', 'jane austen'],
            'Science Fiction': ['sci-fi', 'science fiction', 'dune', 'foundation', 'alien', 'matrix'],
            'Mystery': ['mystery', 'detective', 'sherlock', 'crime', 'thriller', 'murder'],
            'Romance': ['romance', 'love', 'bridget jones', 'notebook', 'relationship'],
            'Biography': ['biography', 'autobiography', 'memoir', 'life of', 'story of'],
            'History': ['history', 'war', 'civilization', 'ancient', 'world war'],
            'Horror': ['horror', 'stephen king', 'ghost', 'haunting', 'scary'],
            'Young Adult': ['young adult', 'ya', 'teen', 'hunger games', 'divergent'],
            'Children': ['children', 'picture', 'dr. seuss', 'curious george', 'kids'],
        }
        
        for idx, row in books_df.iterrows():
            title = str(row.get('title', '')).lower()
            authors = str(row.get('authors', '')).lower()
            
            category = 'Other'
            for cat, keywords in category_keywords.items():
                for keyword in keywords:
                    if keyword in title or keyword in authors:
                        category = cat
                        break
                if category != 'Other':
                    break
            
            categories[row['isbn']] = category
        
        return categories
    
    def _apply_category_diversity(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply category diversity to prevent single-series dominance."""
        if 'category' not in df.columns:
            categories = self._extract_categories(df)
            df['category'] = df['isbn'].map(categories)
        
        category_counts = df['category'].value_counts()
        total_books = len(df)
        
        def get_category_boost(category: str) -> float:
            count = category_counts.get(category, 1)
            ratio = count / total_books
            
            if ratio < 0.1:
                return 1 + (0.1 - ratio) * self.diversity_weight * 2
            elif ratio > 0.3:
                return 1 - (ratio - 0.3) * self.diversity_weight
            else:
                return 1.0
        
        df['diversity_boost'] = df['category'].apply(get_category_boost)
        df['adjusted_score'] = df['weighted_score'] * df['diversity_boost']
        
        return df
    
    def _apply_recency_weighting(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply recency weighting to favor newer books."""
        if 'publication_year' not in df.columns:
            df['recency_boost'] = 1.0
            return df
        
        def get_recency_boost(year: float) -> float:
            if pd.isna(year):
                return 0.8
            
            years_old = self.current_year - year
            
            if years_old <= 2:
                return 1 + self.recency_weight * 1.5
            elif years_old <= 5:
                return 1 + self.recency_weight
            elif years_old <= 10:
                return 1.0
            elif years_old <= 20:
                return 1 - self.recency_weight * 0.5
            else:
                return 1 - self.recency_weight
        
        df['recency_boost'] = df['publication_year'].apply(get_recency_boost)
        df['adjusted_score'] = df.get('adjusted_score', df['weighted_score']) * df['recency_boost']
        
        return df
    
    def fit(self, data):
        """Train the enhanced popularity recommender."""
        print("=" * 60)
        print("TRAINING ENHANCED POPULARITY RECOMMENDER")
        print("=" * 60)
        
        if isinstance(data, (tuple, list)) and len(data) == 2:
            ratings_df, books_df = data
        else:
            ratings_df = data
            books_df = None
        
        explicit = ratings_df[ratings_df["book_rating"] > 0]
        print(f"Explicit ratings: {len(explicit):,}")
        
        ratings_summary = (
            explicit
            .groupby("isbn")
            .agg(
                average_rating=("book_rating", "mean"),
                ratings_count=("book_rating", "count")
            )
            .reset_index()
        )
        
        print(f"Books with ratings: {len(ratings_summary):,}")
        
        self.global_mean = ratings_summary["average_rating"].mean()
        print(f"Global mean rating: {self.global_mean:.2f}")
        
        qualified = ratings_summary[
            ratings_summary["ratings_count"] >= self.min_ratings
        ].copy()
        
        print(f"Books above threshold ({self.min_ratings} ratings): {len(qualified):,}")
        
        m = self.min_ratings
        C = self.global_mean
        
        qualified["weighted_score"] = (
            (qualified["ratings_count"] / (qualified["ratings_count"] + m)) * qualified["average_rating"]
        ) + (
            (m / (qualified["ratings_count"] + m)) * C
        )
        
        self.popularity_df = qualified
        
        if books_df is not None:
            available_cols = ['isbn', 'title', 'authors', 'publisher', 'publication_year', 
                             'average_rating', 'ratings_count', 'language_code']
            existing_cols = [col for col in available_cols if col in books_df.columns]
            
            self.popularity_df = qualified.merge(
                books_df[existing_cols],
                on="isbn",
                how="left"
            )
        
        print("\nApplying category diversity...")
        self.popularity_df = self._apply_category_diversity(self.popularity_df)
        
        print("Applying recency weighting...")
        self.popularity_df = self._apply_recency_weighting(self.popularity_df)
        
        self.popularity_df = self.popularity_df.sort_values(
            by="adjusted_score",
            ascending=False
        ).reset_index(drop=True)
        
        self.is_fitted = True
        self.model = self.popularity_df
        
        print(f"\n✅ Training complete!")
        print(f"Final recommendations pool: {len(self.popularity_df):,}")
    
    def recommend(self, user_id=None, item_id=None, top_k=10, diversify=True, **kwargs):
        """Generate top-K popularity-based recommendations."""
        if not self.is_fitted or self.popularity_df is None:
            raise RuntimeError("Model has not been fitted yet. Call fit() first.")
        
        if diversify and 'category' in self.popularity_df.columns:
            recommendations = []
            categories_used = set()
            remaining_books = self.popularity_df.copy()
            
            while len(recommendations) < top_k and len(remaining_books) > 0:
                if len(categories_used) < remaining_books['category'].nunique():
                    unused = remaining_books[~remaining_books['category'].isin(categories_used)]
                    if len(unused) > 0:
                        book = unused.iloc[0]
                    else:
                        book = remaining_books.iloc[0]
                else:
                    book = remaining_books.iloc[0]
                
                recommendations.append(book)
                categories_used.add(book['category'])
                remaining_books = remaining_books[remaining_books['isbn'] != book['isbn']]
            
            result_df = pd.DataFrame(recommendations)
        else:
            result_df = self.popularity_df.head(top_k)
        
        columns = ["isbn", "title", "authors", "category", "average_rating", 
                   "ratings_count", "weighted_score", "adjusted_score", "publication_year"]
        available_columns = [col for col in columns if col in result_df.columns]
        
        result = result_df[available_columns].copy()
        result.insert(0, 'rank', range(1, len(result) + 1))
        
        return result
    
    def save_model(self, path):
        """Save the trained model to disk."""
        if not self.is_fitted:
            raise RuntimeError("Model has not been fitted yet. Call fit() first.")
        
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "wb") as file:
            pickle.dump(self, file)
        print(f"✅ Model saved to: {path}")
    
    def load_model(self, path):
        """Load a trained model from disk."""
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        with open(path, "rb") as file:
            model = pickle.load(file)
        
        self.popularity_df = model.popularity_df
        self.min_ratings = model.min_ratings
        self.diversity_weight = model.diversity_weight
        self.recency_weight = model.recency_weight
        self.global_mean = model.global_mean
        self.is_fitted = model.is_fitted
        self.current_year = model.current_year
        self.model = model.model
        
        print(f"✅ Model loaded from: {path}")
    
    def recommend_by_category(self, category, top_k=10):
        """Get top recommendations for a specific category."""
        if not self.is_fitted or self.popularity_df is None:
            raise RuntimeError("Model has not been fitted yet. Call fit() first.")
        
        if 'category' not in self.popularity_df.columns:
            raise ValueError("Category information not available in the model")
        
        category_books = self.popularity_df[
            self.popularity_df['category'] == category
        ].head(top_k)
        
        if 'title' in category_books.columns and 'adjusted_score' in category_books.columns:
            return category_books[['title', 'authors', 'adjusted_score', 'publication_year']]
        return category_books
    
    def __repr__(self):
        return f"PopularityRecommender(min_ratings={self.min_ratings}, diversity_weight={self.diversity_weight}, recency_weight={self.recency_weight}, is_fitted={self.is_fitted})"
