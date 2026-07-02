from pathlib import Path
import pickle
import logging
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List
import sys

import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix, save_npz, load_npz
from sklearn.preprocessing import LabelEncoder
from implicit.als import AlternatingLeastSquares
from implicit.nearest_neighbours import ItemItemRecommender

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[4]

DATA_DIR = BASE_DIR / "data" / "processed"
ARTIFACT_DIR = BASE_DIR / "apps" / "api" / "ml" / "artifacts"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CONFIGURATION
# ============================================================

class CollaborativeConfig:
    """Configuration for collaborative filtering model."""
    
    def __init__(
        self,
        factors: int = 64,
        regularization: float = 0.05,
        iterations: int = 20,
        random_state: int = 42,
        use_gpu: bool = False,
        confidence_scale: float = 1.0,
        min_ratings_per_user: int = 5,
        min_ratings_per_item: int = 5,
        test_size: float = 0.2,
        save_model: bool = True,
        model_name: str = "als_model"
    ):
        self.factors = factors
        self.regularization = regularization
        self.iterations = iterations
        self.random_state = random_state
        self.use_gpu = use_gpu
        self.confidence_scale = confidence_scale
        self.min_ratings_per_user = min_ratings_per_user
        self.min_ratings_per_item = min_ratings_per_item
        self.test_size = test_size
        self.save_model = save_model
        self.model_name = model_name
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "factors": self.factors,
            "regularization": self.regularization,
            "iterations": self.iterations,
            "random_state": self.random_state,
            "use_gpu": self.use_gpu,
            "confidence_scale": self.confidence_scale,
            "min_ratings_per_user": self.min_ratings_per_user,
            "min_ratings_per_item": self.min_ratings_per_item,
            "test_size": self.test_size,
            "model_name": self.model_name
        }


# ============================================================
# DATA LOADING
# ============================================================

def load_ratings(ratings_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load ratings data from parquet file.
    
    Parameters:
    -----------
    ratings_path : Path, optional
        Path to ratings file. Defaults to DATA_DIR/ratings/ratings_cleaned.parquet
    
    Returns:
    --------
    pd.DataFrame: Ratings data
    """
    print("=" * 60)
    print("LOADING RATINGS")
    print("=" * 60)
    
    if ratings_path is None:
        ratings_path = DATA_DIR / "ratings" / "ratings_cleaned.parquet"
    
    if not ratings_path.exists():
        raise FileNotFoundError(f"Ratings file not found: {ratings_path}")
    
    try:
        ratings = pd.read_parquet(ratings_path)
        
        print(f"✅ Interactions: {len(ratings):,}")
        print(f"✅ Users: {ratings['user_id'].nunique():,}")
        print(f"✅ Books: {ratings['isbn'].nunique():,}")
        print(f"✅ Rating range: {ratings['book_rating'].min():.1f} - {ratings['book_rating'].max():.1f}")
        
        # Calculate sparsity
        total_possible = ratings['user_id'].nunique() * ratings['isbn'].nunique()
        sparsity = (1 - len(ratings) / total_possible) * 100
        print(f"✅ Sparsity: {sparsity:.2f}%")
        
        return ratings
        
    except Exception as e:
        logger.error(f"Error loading ratings: {e}")
        raise


def filter_ratings(
    ratings: pd.DataFrame,
    min_user_ratings: int = 5,
    min_item_ratings: int = 5
) -> pd.DataFrame:
    """
    Filter ratings to remove users and items with too few ratings.
    
    Parameters:
    -----------
    ratings : pd.DataFrame
        Ratings data
    min_user_ratings : int
        Minimum ratings per user
    min_item_ratings : int
        Minimum ratings per item
    
    Returns:
    --------
    pd.DataFrame: Filtered ratings
    """
    print("\n" + "=" * 60)
    print("FILTERING RATINGS")
    print("=" * 60)
    
    original_users = ratings['user_id'].nunique()
    original_items = ratings['isbn'].nunique()
    original_interactions = len(ratings)
    
    # Filter users
    user_counts = ratings.groupby('user_id').size()
    active_users = user_counts[user_counts >= min_user_ratings].index
    ratings = ratings[ratings['user_id'].isin(active_users)]
    
    # Filter items
    item_counts = ratings.groupby('isbn').size()
    active_items = item_counts[item_counts >= min_item_ratings].index
    ratings = ratings[ratings['isbn'].isin(active_items)]
    
    print(f"✅ Users: {original_users:,} → {ratings['user_id'].nunique():,} (-{((1 - ratings['user_id'].nunique()/original_users)*100):.1f}%)")
    print(f"✅ Books: {original_items:,} → {ratings['isbn'].nunique():,} (-{((1 - ratings['isbn'].nunique()/original_items)*100):.1f}%)")
    print(f"✅ Interactions: {original_interactions:,} → {len(ratings):,} (-{((1 - len(ratings)/original_interactions)*100):.1f}%)")
    
    return ratings


# ============================================================
# CONFIDENCE SCORES
# ============================================================

def build_confidence(
    ratings: pd.DataFrame,
    confidence_scale: float = 1.0
) -> pd.DataFrame:
    """
    Build confidence scores from ratings.
    
    Parameters:
    -----------
    ratings : pd.DataFrame
        Ratings data with 'book_rating' column
    confidence_scale : float
        Scaling factor for confidence
    
    Returns:
    --------
    pd.DataFrame: Ratings with confidence column
    """
    print("\n" + "=" * 60)
    print("BUILDING CONFIDENCE SCORES")
    print("=" * 60)
    
    # Map ratings to confidence (higher rating = higher confidence)
    ratings["confidence"] = ratings["book_rating"].astype(float) * confidence_scale
    
    # Ensure minimum confidence for implicit feedback
    ratings.loc[ratings["confidence"] < 1, "confidence"] = 1.0
    
    print(f"✅ Confidence range: {ratings['confidence'].min():.2f} - {ratings['confidence'].max():.2f}")
    print(f"✅ Confidence mean: {ratings['confidence'].mean():.2f}")
    
    return ratings


# ============================================================
# ENCODERS
# ============================================================

def create_encoders(ratings: pd.DataFrame) -> Tuple[pd.DataFrame, LabelEncoder, LabelEncoder]:
    """
    Create user and item encoders.
    
    Parameters:
    -----------
    ratings : pd.DataFrame
        Ratings data with 'user_id' and 'isbn' columns
    
    Returns:
    --------
    tuple: (ratings_with_encodings, user_encoder, item_encoder)
    """
    print("\n" + "=" * 60)
    print("CREATING ENCODERS")
    print("=" * 60)
    
    user_encoder = LabelEncoder()
    item_encoder = LabelEncoder()
    
    ratings["user_idx"] = user_encoder.fit_transform(ratings["user_id"])
    ratings["item_idx"] = item_encoder.fit_transform(ratings["isbn"])
    
    print(f"✅ Users encoded: {len(user_encoder.classes_):,}")
    print(f"✅ Books encoded: {len(item_encoder.classes_):,}")
    
    return ratings, user_encoder, item_encoder


# ============================================================
# SPARSE MATRIX
# ============================================================

def build_matrix(ratings: pd.DataFrame) -> csr_matrix:
    """
    Build sparse interaction matrix.
    
    Parameters:
    -----------
    ratings : pd.DataFrame
        Ratings with 'user_idx', 'item_idx', and 'confidence' columns
    
    Returns:
    --------
    csr_matrix: Sparse interaction matrix
    """
    print("\n" + "=" * 60)
    print("BUILDING SPARSE MATRIX")
    print("=" * 60)
    
    n_users = ratings['user_idx'].nunique()
    n_items = ratings['item_idx'].nunique()
    
    matrix = csr_matrix(
        (
            ratings["confidence"],
            (
                ratings["user_idx"],
                ratings["item_idx"]
            )
        ),
        shape=(n_users, n_items)
    )
    
    # Calculate sparsity
    total_possible = n_items * n_users
    nnz = matrix.nnz
    sparsity = (1 - (nnz / total_possible)) * 100
    
    print(f"✅ Matrix shape: {matrix.shape}")
    print(f"✅ Non-zero entries: {nnz:,}")
    print(f"✅ Sparsity: {sparsity:.2f}%")
    print(f"✅ Memory usage: {matrix.data.nbytes / 1024**2:.2f} MB")
    
    return matrix


# ============================================================
# TRAIN-TEST SPLIT
# ============================================================

def train_test_split_ratings(
    ratings: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split ratings into train and test sets.
    
    Parameters:
    -----------
    ratings : pd.DataFrame
        Ratings data
    test_size : float
        Proportion of data to use for testing
    random_state : int
        Random seed for reproducibility
    
    Returns:
    --------
    tuple: (train_ratings, test_ratings)
    """
    from sklearn.model_selection import train_test_split
    
    print("\n" + "=" * 60)
    print("SPLITTING TRAIN/TEST")
    print("=" * 60)
    
    train, test = train_test_split(
        ratings,
        test_size=test_size,
        random_state=random_state
    )
    
    print(f"✅ Train interactions: {len(train):,} ({len(train)/len(ratings)*100:.1f}%)")
    print(f"✅ Test interactions: {len(test):,} ({len(test)/len(ratings)*100:.1f}%)")
    print(f"✅ Train users: {train['user_id'].nunique():,}")
    print(f"✅ Test users: {test['user_id'].nunique():,}")
    
    return train, test


# ============================================================
# ALS TRAINING
# ============================================================

def train_als(
    matrix: csr_matrix,
    config: CollaborativeConfig = None
) -> AlternatingLeastSquares:
    """
    Train ALS model.
    
    Parameters:
    -----------
    matrix : csr_matrix
        Sparse interaction matrix
    config : CollaborativeConfig
        Configuration for training
    
    Returns:
    --------
    AlternatingLeastSquares: Trained ALS model
    """
    if config is None:
        config = CollaborativeConfig()
    
    print("\n" + "=" * 60)
    print("TRAINING ALS MODEL")
    print("=" * 60)
    print(f"✅ Factors: {config.factors}")
    print(f"✅ Regularization: {config.regularization}")
    print(f"✅ Iterations: {config.iterations}")
    print(f"✅ Use GPU: {config.use_gpu}")
    print(f"✅ Random seed: {config.random_state}")
    
    try:
        model = AlternatingLeastSquares(
            factors=config.factors,
            regularization=config.regularization,
            iterations=config.iterations,
            random_state=config.random_state,
            use_gpu=config.use_gpu
        )
        
        # Train the model
        import time
        start_time = time.time()
        model.fit(matrix)
        elapsed = time.time() - start_time
        
        print(f"✅ Training complete in {elapsed:.2f} seconds")
        
        # Log model statistics
        print(f"✅ User factors: {model.user_factors.shape}")
        print(f"✅ Item factors: {model.item_factors.shape}")
        
        return model
        
    except Exception as e:
        logger.error(f"Error training ALS model: {e}")
        raise


# ============================================================
# SAVE ARTIFACTS
# ============================================================

def save_artifacts(
    model: AlternatingLeastSquares,
    matrix: csr_matrix,
    user_encoder: LabelEncoder,
    item_encoder: LabelEncoder,
    config: CollaborativeConfig = None,
    train_ratings: pd.DataFrame = None
) -> None:
    """
    Save all artifacts to disk.
    
    Parameters:
    -----------
    model : AlternatingLeastSquares
        Trained ALS model
    matrix : csr_matrix
        Sparse interaction matrix
    user_encoder : LabelEncoder
        User encoder
    item_encoder : LabelEncoder
        Item encoder
    config : CollaborativeConfig
        Configuration used for training
    train_ratings : pd.DataFrame
        Training ratings data (optional)
    """
    print("\n" + "=" * 60)
    print("SAVING ARTIFACTS")
    print("=" * 60)
    
    if config is None:
        config = CollaborativeConfig()
    
    # Save model
    model_path = ARTIFACT_DIR / f"{config.model_name}.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"✅ Model saved: {model_path}")
    
    # Save encoders
    user_encoder_path = ARTIFACT_DIR / "user_encoder.pkl"
    with open(user_encoder_path, "wb") as f:
        pickle.dump(user_encoder, f)
    print(f"✅ User encoder saved: {user_encoder_path}")
    
    item_encoder_path = ARTIFACT_DIR / "book_encoder.pkl"
    with open(item_encoder_path, "wb") as f:
        pickle.dump(item_encoder, f)
    print(f"✅ Book encoder saved: {item_encoder_path}")
    
    # Save matrix
    matrix_path = ARTIFACT_DIR / "interaction_matrix.npz"
    save_npz(matrix_path, matrix)
    print(f"✅ Interaction matrix saved: {matrix_path}")
    
    # Save metadata
    metadata = {
        "model_type": "ALS",
        "model_name": config.model_name,
        "n_users": len(user_encoder.classes_),
        "n_items": len(item_encoder.classes_),
        "n_interactions": matrix.nnz,
        "factors": config.factors,
        "regularization": config.regularization,
        "iterations": config.iterations,
        "confidence_scale": config.confidence_scale,
        "matrix_shape": matrix.shape,
        "sparsity": (1 - (matrix.nnz / (matrix.shape[0] * matrix.shape[1]))) * 100,
        "timestamp": datetime.now().isoformat(),
        "config": config.to_dict()
    }
    
    metadata_path = ARTIFACT_DIR / "collaborative_metadata.pkl"
    with open(metadata_path, "wb") as f:
        pickle.dump(metadata, f)
    print(f"✅ Metadata saved: {metadata_path}")
    
    # Save train ratings if provided
    if train_ratings is not None:
        train_path = ARTIFACT_DIR / "train_ratings.parquet"
        train_ratings.to_parquet(train_path, index=False)
        print(f"✅ Train ratings saved: {train_path}")
    
    print("\n" + "=" * 60)
    print("📊 ARTIFACT SUMMARY")
    print("=" * 60)
    print(f"✅ Users: {metadata['n_users']:,}")
    print(f"✅ Books: {metadata['n_items']:,}")
    print(f"✅ Interactions: {metadata['n_interactions']:,}")
    print(f"✅ Factors: {metadata['factors']}")
    print(f"✅ Sparsity: {metadata['sparsity']:.2f}%")


# ============================================================
# MAIN
# ============================================================

def main(
    config: CollaborativeConfig = None,
    skip_filtering: bool = False
):
    """
    Main training pipeline.
    
    Parameters:
    -----------
    config : CollaborativeConfig, optional
        Configuration for training
    skip_filtering : bool
        Whether to skip filtering ratings
    """
    if config is None:
        config = CollaborativeConfig()
    
    print("=" * 60)
    print("COLLABORATIVE RECOMMENDER TRAINING")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Config: {config.to_dict()}")
    
    try:
        # Load ratings
        ratings = load_ratings()
        
        # Filter ratings
        if not skip_filtering:
            ratings = filter_ratings(
                ratings,
                min_user_ratings=config.min_ratings_per_user,
                min_item_ratings=config.min_ratings_per_item
            )
        
        # Build confidence
        ratings = build_confidence(
            ratings,
            confidence_scale=config.confidence_scale
        )
        
        # Create encoders
        ratings, user_encoder, item_encoder = create_encoders(ratings)
        
        # Build matrix
        matrix = build_matrix(ratings)
        
        # Train model
        model = train_als(matrix, config)
        
        # Save artifacts
        save_artifacts(
            model,
            matrix,
            user_encoder,
            item_encoder,
            config,
            ratings
        )
        
        print("\n" + "=" * 60)
        print("✅ COLLABORATIVE TRAINING COMPLETE!")
        print("=" * 60)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n💡 Next steps:")
        print("  1. Load model in collaborative service")
        print("  2. Get recommendations: service.recommend(user_id, top_k=10)")
        print("  3. Test: python apps/api/ml/collaborative/test_collaborative.py")
        
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    # Run with default config
    config = CollaborativeConfig(
        factors=64,
        regularization=0.05,
        iterations=20,
        confidence_scale=1.0,
        min_ratings_per_user=5,
        min_ratings_per_item=5
    )
    main(config=config)