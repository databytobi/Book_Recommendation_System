from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from scipy.sparse import csr_matrix, save_npz

# Get the project root
BASE_DIR = Path(__file__).resolve().parents[4]  # Go up 4 levels to project root

DATA_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)

OUTPUT_DIR = (
    BASE_DIR
    / "apps"
    / "api"
    / "ml"
    / "artifacts"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

def load_explicit_ratings():
    """
    Load explicit ratings dataset.
    """
    print("=" * 60)
    print("LOADING EXPLICIT RATINGS")
    print("=" * 60)
    
    ratings_path = DATA_DIR / "ratings" / "ratings_explicit.parquet"
    
    if not ratings_path.exists():
        print(f"❌ Ratings file not found: {ratings_path}")
        return None
    
    try:
        ratings = pd.read_parquet(ratings_path)
        print(f"✅ Explicit ratings loaded: {len(ratings):,}")
        return ratings
    except Exception as e:
        print(f"❌ Error loading ratings: {e}")
        return None

def filter_active_users(
    ratings,
    min_interactions=5
):
    """
    Filter users with minimum number of interactions.
    """
    print(
        f"\nFiltering users with >= "
        f"{min_interactions} interactions..."
    )
    
    user_counts = (
        ratings
        .groupby("user_id")
        .size()
    )
    
    active_users = user_counts[
        user_counts >= min_interactions
    ].index
    
    filtered = ratings[
        ratings["user_id"]
        .isin(active_users)
    ]
    
    print(
        f"Remaining interactions: "
        f"{len(filtered):,}"
    )
    
    print(
        f"Remaining users: "
        f"{filtered['user_id'].nunique():,}"
    )
    
    return filtered

def split_train_test(
    ratings,
    test_size=0.2,
    random_state=42
):
    """
    Split data into train and test sets.
    """
    print("\nSplitting train/test datasets...")
    
    train, test = train_test_split(
        ratings,
        test_size=test_size,
        random_state=random_state
    )
    
    print(
        f"Train interactions: "
        f"{len(train):,}"
    )
    
    print(
        f"Test interactions: "
        f"{len(test):,}"
    )
    
    return train, test

def export_datasets(
    train,
    test
):
    """
    Export train and test datasets to parquet files.
    """
    train_path = (
        OUTPUT_DIR
        / "train_interactions.parquet"
    )
    
    test_path = (
        OUTPUT_DIR
        / "test_interactions.parquet"
    )
    
    train.to_parquet(
        train_path,
        index=False
    )
    
    test.to_parquet(
        test_path,
        index=False
    )
    
    print(
        f"\n✅ Train dataset saved:"
    )
    print(train_path)
    
    print(
        f"\n✅ Test dataset saved:"
    )
    print(test_path)

def create_sparse_interaction_matrix(
    ratings,
    user_col='user_id',
    item_col='isbn',
    rating_col='book_rating'
):
    """
    Create sparse interaction matrix using scipy sparse matrix.
    This is memory efficient for large datasets.
    """
    print("\n" + "=" * 60)
    print("CREATING SPARSE INTERACTION MATRIX")
    print("=" * 60)
    
    # Get unique users and items
    users = ratings[user_col].unique()
    items = ratings[item_col].unique()
    
    # Create mappings
    user_to_idx = {user: idx for idx, user in enumerate(users)}
    item_to_idx = {item: idx for idx, item in enumerate(items)}
    
    print(f"Unique users: {len(users):,}")
    print(f"Unique items: {len(items):,}")
    print(f"Total interactions: {len(ratings):,}")
    
    # Create row and column indices
    row_ind = ratings[user_col].map(user_to_idx).values
    col_ind = ratings[item_col].map(item_to_idx).values
    data = ratings[rating_col].values
    
    # Create sparse matrix
    sparse_matrix = csr_matrix(
        (data, (row_ind, col_ind)),
        shape=(len(users), len(items))
    )
    
    # Calculate sparsity
    total_possible = len(users) * len(items)
    nonzero = sparse_matrix.nnz
    sparsity = (1 - (nonzero / total_possible)) * 100
    
    print(f"\n📊 Matrix Statistics:")
    print(f"  Shape: {sparse_matrix.shape}")
    print(f"  Non-zero entries: {nonzero:,}")
    print(f"  Density: {(nonzero / total_possible * 100):.4f}%")
    print(f"  Sparsity: {sparsity:.2f}%")
    print(f"  Memory usage: {sparse_matrix.data.nbytes / 1024**2:.2f} MB")
    
    return sparse_matrix, user_to_idx, item_to_idx

def create_dense_interaction_matrix_sample(
    ratings,
    sample_users=100,
    sample_items=100
):
    """
    Create a small dense sample of the interaction matrix for visualization.
    """
    print("\n" + "=" * 60)
    print("CREATING DENSE SAMPLE MATRIX")
    print("=" * 60)
    
    # Get most active users and items
    user_counts = ratings.groupby('user_id').size().sort_values(ascending=False)
    item_counts = ratings.groupby('isbn').size().sort_values(ascending=False)
    
    top_users = user_counts.head(sample_users).index
    top_items = item_counts.head(sample_items).index
    
    # Filter ratings to top users and items
    sample_ratings = ratings[
        ratings['user_id'].isin(top_users) &
        ratings['isbn'].isin(top_items)
    ]
    
    # Create dense matrix
    sample_matrix = sample_ratings.pivot_table(
        index='user_id',
        columns='isbn',
        values='book_rating',
        fill_value=0
    )
    
    print(f"Sample matrix shape: {sample_matrix.shape}")
    print(f"Users: {len(sample_matrix):,}")
    print(f"Items: {len(sample_matrix.columns):,}")
    
    return sample_matrix

def save_sparse_matrix(
    sparse_matrix,
    user_to_idx,
    item_to_idx
):
    """
    Save sparse matrix and mappings to disk.
    """
    print("\n" + "=" * 60)
    print("SAVING SPARSE MATRIX")
    print("=" * 60)
    
    # Save sparse matrix
    matrix_path = OUTPUT_DIR / "interaction_matrix.npz"
    save_npz(matrix_path, sparse_matrix)
    print(f"✅ Sparse matrix saved: {matrix_path}")
    
    # Save user mappings
    user_mapping_path = OUTPUT_DIR / "user_mapping.parquet"
    user_mapping = pd.DataFrame({
        'user_id': list(user_to_idx.keys()),
        'user_idx': list(user_to_idx.values())
    })
    user_mapping.to_parquet(user_mapping_path, index=False)
    print(f"✅ User mapping saved: {user_mapping_path}")
    
    # Save item mappings
    item_mapping_path = OUTPUT_DIR / "item_mapping.parquet"
    item_mapping = pd.DataFrame({
        'isbn': list(item_to_idx.keys()),
        'item_idx': list(item_to_idx.values())
    })
    item_mapping.to_parquet(item_mapping_path, index=False)
    print(f"✅ Item mapping saved: {item_mapping_path}")
    
    # Also save as text for easy viewing
    stats_path = OUTPUT_DIR / "matrix_stats.txt"
    with open(stats_path, 'w') as f:
        f.write("Interaction Matrix Statistics\n")
        f.write("=" * 40 + "\n")
        f.write(f"Users: {len(user_to_idx):,}\n")
        f.write(f"Items: {len(item_to_idx):,}\n")
        f.write(f"Non-zero entries: {sparse_matrix.nnz:,}\n")
        f.write(f"Shape: {sparse_matrix.shape}\n")
        f.write(f"Memory: {sparse_matrix.data.nbytes / 1024**2:.2f} MB\n")
    print(f"✅ Statistics saved: {stats_path}")

def debug_paths():
    """
    Debug function to check if paths are correct.
    """
    print("=" * 60)
    print("DEBUG - PATHS")
    print("=" * 60)
    print(f"Script location: {Path(__file__).resolve()}")
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"DATA_DIR: {DATA_DIR}")
    print(f"OUTPUT_DIR: {OUTPUT_DIR}")
    
    print(f"\nChecking if directories exist:")
    print(f"BASE_DIR exists: {BASE_DIR.exists()}")
    print(f"DATA_DIR exists: {DATA_DIR.exists()}")

def main():
    """
    Main execution function.
    """
    print("=" * 60)
    print("INTERACTION MATRIX PIPELINE")
    print("=" * 60)
    
    # Debug paths
    debug_paths()
    
    # Load explicit ratings
    ratings = load_explicit_ratings()
    
    if ratings is None:
        print("\n❌ Failed to load ratings. Please check file paths.")
        return
    
    # Filter active users
    ratings = filter_active_users(
        ratings,
        min_interactions=5
    )
    
    # Split train/test
    train, test = split_train_test(
        ratings
    )
    
    # Export datasets
    export_datasets(
        train,
        test
    )
    
    # Create sparse interaction matrix (memory efficient)
    try:
        sparse_matrix, user_to_idx, item_to_idx = create_sparse_interaction_matrix(
            ratings
        )
        
        # Save sparse matrix
        save_sparse_matrix(sparse_matrix, user_to_idx, item_to_idx)
        
        # Optionally create a small dense sample for visualization
        print("\n" + "=" * 60)
        print("CREATING SAMPLE MATRIX FOR VISUALIZATION")
        print("=" * 60)
        sample_matrix = create_dense_interaction_matrix_sample(
            ratings,
            sample_users=50,
            sample_items=50
        )
        
        # Save sample matrix
        sample_path = OUTPUT_DIR / "interaction_matrix_sample.csv"
        sample_matrix.to_csv(sample_path)
        print(f"✅ Sample matrix saved: {sample_path}")
        
    except Exception as e:
        print(f"⚠️ Could not create interaction matrix: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ INTERACTION MATRIX PIPELINE COMPLETE!")
    print("=" * 60)
    print(f"\n📁 All artifacts saved to: {OUTPUT_DIR}")
    print("\n📊 Files created:")
    for file in OUTPUT_DIR.iterdir():
        if file.is_file():
            size = file.stat().st_size / 1024**2
            print(f"  📄 {file.name} ({size:.2f} MB)")

if __name__ == "__main__":
    main()