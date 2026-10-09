import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, List, Dict, Any

# Import from parent directory
import sys
# Add the parent directory (apps/api/ml) to path
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, parent_dir)
# Add the recommenders directory
recommenders_dir = str(Path(__file__).resolve().parent.parent / "recommenders")
sys.path.insert(0, recommenders_dir)

# pyrefly: ignore [missing-import]
from base import BaseRecommender

class PopularityRecommender(BaseRecommender):
    """
    Enhanced popularity-based recommendation system with:
    - Category diversity to avoid single-series dominance
    - Recency weighting for newer books
    - Better merge handling for ratings data
    """
    
    def __init__(self, min_ratings: int = 30, diversity_weight: float = 0.4, recency_weight: float = 0.3):
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
            'Fantasy': ['harry potter', 'lord of the rings', 'fantasy', 'wizard', 'magic', 'dragon', 'hobbit',
                       'wheel of time', 'mistborn', 'stormlight', 'chronicles of narnia', 'game of thrones'],
            'Classic': ['classic', 'to kill a mockingbird', 'pride and prejudice', 'great gatsby', 'jane austen',
                       'moby dick', 'war and peace', 'crime and punishment', 'ulysses', 'dickens'],
            'Science Fiction': ['sci-fi', 'science fiction', 'dune', 'foundation', 'alien', 'matrix',
                               'sci fi', 'space', 'cyberpunk', 'fahrenheit', 'brave new world'],
            'Mystery': ['mystery', 'detective', 'sherlock', 'crime', 'thriller', 'murder', 'suspense',
                       'agatha christie', 'p.d. james', 'whodunit'],
            'Romance': ['romance', 'love', 'bridget jones', 'notebook', 'relationship', 'romantic',
                       'chick lit', 'contemporary romance'],
            'Biography': ['biography', 'autobiography', 'memoir', 'life of', 'story of', 'biographical',
                         'historical biography'],
            'History': ['history', 'war', 'civilization', 'ancient', 'world war', 'historical',
                       'middle ages', 'renaissance'],
            'Horror': ['horror', 'stephen king', 'ghost', 'haunting', 'scary', 'terror', 'creepy',
                      'supernatural', 'paranormal'],
            'Young Adult': ['young adult', 'ya', 'teen', 'hunger games', 'divergent', 'young adult',
                           'teen fiction', 'ya fantasy'],
            'Children': ['children', 'picture', 'dr. seuss', 'curious george', 'kids', 'childrens',
                        'early reader', 'picture book'],
            'Adventure': ['adventure', 'quest', 'journey', 'expedition', 'exploration'],
            'Thriller': ['thriller', 'suspense', 'psychological thriller'],
            'Self Help': ['self help', 'self-help', 'personal development', 'motivation'],
            'Business': ['business', 'leadership', 'entrepreneurship', 'economics', 'finance'],
            'Philosophy': ['philosophy', 'stoic', 'existentialism', 'ethics'],
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
            ratio = count / total_books if total_books > 0 else 0.1
            
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
        """Train the enhanced popularity recommender with better merge handling."""
        print("=" * 60)
        print("TRAINING ENHANCED POPULARITY RECOMMENDER")
        print("=" * 60)
        
        # Handle different input formats
        if isinstance(data, (tuple, list)) and len(data) == 2:
            ratings_df, books_df = data
        else:
            ratings_df = data
            books_df = None
        
        # Use explicit ratings only (ratings > 0)
        explicit = ratings_df[ratings_df["book_rating"] > 0].copy()
        print(f"Explicit ratings: {len(explicit):,}")
        
        # Calculate total ratings count per book from explicit ratings
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
        
        # Calculate global mean rating
        self.global_mean = ratings_summary["average_rating"].mean()
        print(f"Global mean rating: {self.global_mean:.2f}")

        # ------------------------------------------------------------------
        # Prefer catalog popularity over interaction-sample counts
        # ------------------------------------------------------------------
        # `train_interactions.parquet` is very sparse: ~272k ratings spread
        # across ~136k distinct books, i.e. roughly two per book. Counting
        # ratings from that sample and then discarding everything below
        # `min_ratings` shrank the entire pool to 208 books out of a 248k
        # catalog, so trending kept surfacing the same handful of titles.
        #
        # The catalog itself carries the authoritative Goodreads popularity
        # (`ratings_count`, up to 2.5M). When those columns are present we
        # rank on them instead, which restores the pool to catalog scale.
        # Books lacking a catalog rating simply remain below the threshold,
        # exactly as before.
        if (
            books_df is not None
            and "ratings_count" in books_df.columns
            and "average_rating" in books_df.columns
        ):
            catalog = books_df[["isbn", "ratings_count", "average_rating"]].copy()
            catalog["ratings_count"] = pd.to_numeric(
                catalog["ratings_count"], errors="coerce"
            )
            catalog["average_rating"] = pd.to_numeric(
                catalog["average_rating"], errors="coerce"
            )
            catalog = catalog.dropna(subset=["ratings_count", "average_rating"])
            catalog = catalog[catalog["ratings_count"] > 0]

            if len(catalog):
                print(
                    "Popularity source: catalog ratings_count "
                    f"({len(catalog):,} books carry a catalog rating)"
                )
                ratings_summary = catalog
                self.global_mean = float(catalog["average_rating"].mean())
                print(f"Global mean rating (catalog): {self.global_mean:.2f}")
        
        # Filter books below minimum rating threshold
        qualified = ratings_summary[
            ratings_summary["ratings_count"] >= self.min_ratings
        ].copy()
        
        print(f"Books above threshold ({self.min_ratings} ratings): {len(qualified):,}")
        
        # Calculate weighted score using Bayesian average
        m = self.min_ratings
        C = self.global_mean
        
        qualified["weighted_score"] = (
            (qualified["ratings_count"] / (qualified["ratings_count"] + m)) * qualified["average_rating"]
        ) + (
            (m / (qualified["ratings_count"] + m)) * C
        )
        
        # Start with qualified as the base
        self.popularity_df = qualified.copy()
        
        # Merge with book metadata if available - CAREFUL not to overwrite ratings_count
        if books_df is not None:
            print("\nMerging with book metadata...")
            
            # Metadata columns to merge (excluding ratings_count to keep our computed value)
            metadata_cols = ['isbn', 'title', 'authors', 'publisher', 'publication_year', 
                            'language_code', 'image_url_s', 'image_url_m', 'image_url_l']
            
            # Also keep Goodreads average_rating but rename it
            if 'average_rating' in books_df.columns:
                books_df = books_df.rename(columns={'average_rating': 'goodreads_rating'})
                metadata_cols.append('goodreads_rating')
            
            existing_cols = [col for col in metadata_cols if col in books_df.columns]
            
            if existing_cols:
                # Merge metadata
                self.popularity_df = self.popularity_df.merge(
                    books_df[existing_cols],
                    on="isbn",
                    how="left"
                )
                print(f"  Merged {len(existing_cols)} metadata columns")
                
                # Fill missing titles with placeholder
                if 'title' in self.popularity_df.columns:
                    self.popularity_df['title'] = self.popularity_df['title'].fillna('Unknown Title')
                
                # Fill missing authors
                if 'authors' in self.popularity_df.columns:
                    self.popularity_df['authors'] = self.popularity_df['authors'].fillna('Unknown Author')
        
        # Verify ratings_count is still there
        print(f"\nRatings count column available: {'ratings_count' in self.popularity_df.columns}")
        if 'ratings_count' in self.popularity_df.columns:
            print(f"Sample ratings_count: {self.popularity_df['ratings_count'].head(3).tolist()}")
        
        # Apply category diversity
        print("\nApplying category diversity...")
        self.popularity_df = self._apply_category_diversity(self.popularity_df)
        
        # Apply recency weighting
        print("Applying recency weighting...")
        self.popularity_df = self._apply_recency_weighting(self.popularity_df)
        
        # Sort by final adjusted score
        self.popularity_df = self.popularity_df.sort_values(
            by="adjusted_score",
            ascending=False
        ).reset_index(drop=True)
        
        self.is_fitted = True
        self.model = self.popularity_df
        
        print(f"\n✅ Training complete!")
        print(f"Final recommendations pool: {len(self.popularity_df):,}")
        
        # Show sample of top recommendations
        print("\n📚 Top 5 Recommendations Preview:")
        preview_cols = ['title', 'average_rating', 'ratings_count', 'weighted_score', 'adjusted_score', 'category']
        available_preview = [col for col in preview_cols if col in self.popularity_df.columns]
        if available_preview:
            print(self.popularity_df[available_preview].head(5).to_string())
    
    def recommend(self, user_id=None, item_id=None, top_k=10, diversify=True, **kwargs):
        """Generate top-K popularity-based recommendations."""
        if not self.is_fitted or self.popularity_df is None:
            raise RuntimeError("Model has not been fitted yet. Call fit() first.")
        
        if diversify and 'category' in self.popularity_df.columns:
            # Get diverse recommendations (alternate between categories)
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
        
        # Prepare output with required columns - ADD ratings_count here.
        # image_url_* must be carried through as well: they are merged into
        # popularity_df during fit(), but omitting them here meant every
        # trending/homepage recommendation reached the API without a cover and
        # the UI rendered placeholder images.
        columns = ["isbn", "title", "authors", "category", "average_rating", 
                   "ratings_count", "weighted_score", "adjusted_score", "publication_year",
                   "image_url_s", "image_url_m", "image_url_l", "publisher"]
        available_columns = [col for col in columns if col in result_df.columns]
        
        # Make sure ratings_count is included
        if 'ratings_count' not in available_columns and 'ratings_count' in self.popularity_df.columns:
            # Add it from the full dataframe if missing
            result_df = result_df.merge(
                self.popularity_df[['isbn', 'ratings_count']],
                on='isbn',
                how='left'
            )
            available_columns.append('ratings_count')
        
        result = result_df[available_columns].copy()
        result.insert(0, 'rank', range(1, len(result) + 1))
        
        return result

    def train(self, data=None, train_path=None, books_path=None):
        """
        Train the recommender.
        
        Parameters:
        -----------
        data : tuple, optional
            (train_df, books_df) tuple. If provided, uses this data.
        train_path : Path, optional
            Path to train interactions parquet file.
        books_path : Path, optional
            Path to books parquet file.
        """
        if data is not None:
            self.fit(data)
            return
        
        # Load default data
        import pandas as pd
        
        # Paths are resolved centrally (see apps/api/ml/paths.py).
        # The previous code used Path(__file__).resolve().parents[4], which
        # raised IndexError in the container layout: /app/ml/popularity only
        # has three ancestors, so train() crashed before it could load data.
        try:
            from paths import ARTIFACT_DIR as _ARTIFACT_DIR
            from paths import INTEGRATED_DIR as _INTEGRATED_DIR
        except ImportError:  # executed as a standalone script
            import sys as _sys
            _sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
            from paths import ARTIFACT_DIR as _ARTIFACT_DIR
            from paths import INTEGRATED_DIR as _INTEGRATED_DIR
        
        if train_path is None:
            train_path = _ARTIFACT_DIR / "train_interactions.parquet"
        
        if books_path is None:
            books_path = _INTEGRATED_DIR / "master_books_deduplicated.parquet"
            if not books_path.exists():
                books_path = _INTEGRATED_DIR / "master_books.parquet"
        
        print(f"Looking for train data at: {train_path}")
        print(f"Looking for books data at: {books_path}")
        
        if train_path.exists() and books_path.exists():
            print(f"✅ Found training data")
            train = pd.read_parquet(train_path)
            books = pd.read_parquet(books_path)
            self.fit((train, books))
        else:
            raise FileNotFoundError(
                f"Training data not found. Run interaction_matrix.py first.\n"
                f"Train path: {train_path}\n"
                f"Books path: {books_path}"
            )
    
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
        
        # Copy attributes to self
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
            return category_books[['title', 'authors', 'adjusted_score', 'publication_year', 'ratings_count']]
        return category_books
    
    def explain_recommendation(self, isbn):
        """Explain why a book is recommended."""
        if not self.is_fitted or self.popularity_df is None:
            raise RuntimeError("Model has not been fitted yet. Call fit() first.")
        
        book = self.popularity_df[self.popularity_df["isbn"] == isbn]
        
        if len(book) == 0:
            return {"error": f"Book with ISBN {isbn} not found"}
        
        explanation = {
            "isbn": isbn,
            "title": book["title"].iloc[0] if "title" in book.columns else "Unknown",
            "average_rating": float(book["average_rating"].iloc[0]) if "average_rating" in book.columns else None,
            "ratings_count": int(book["ratings_count"].iloc[0]) if "ratings_count" in book.columns else 0,
            "weighted_score": float(book["weighted_score"].iloc[0]),
            "adjusted_score": float(book["adjusted_score"].iloc[0]),
            "category": book["category"].iloc[0] if "category" in book.columns else "Unknown",
            "diversity_boost": float(book["diversity_boost"].iloc[0]) if "diversity_boost" in book.columns else 1.0,
            "recency_boost": float(book["recency_boost"].iloc[0]) if "recency_boost" in book.columns else 1.0,
            "global_mean": float(self.global_mean) if self.global_mean else None,
            "min_ratings_threshold": self.min_ratings,
            "rank": int(book.index[0]) + 1
        }
        
        return explanation
    
    def __repr__(self):
        return f"PopularityRecommender(min_ratings={self.min_ratings}, diversity_weight={self.diversity_weight}, recency_weight={self.recency_weight}, is_fitted={self.is_fitted})"