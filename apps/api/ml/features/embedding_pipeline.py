from pathlib import Path
import pickle
import sys
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize

# Central path resolution. This file lives at
# apps/api/ml/features/embedding_pipeline.py, so the ml package root is the
# parent directory. Previously BASE_DIR was computed as parents[1] (= ml/),
# which resolved DATA_DIR to apps/api/ml/data/processed and ARTIFACT_DIR to
# apps/api/ml/apps/api/ml/artifacts — neither of which exists.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from paths import (  # noqa: E402
    ARTIFACT_DIR,
    INTEGRATED_DIR,
    PROCESSED_DATA_DIR,
    PROJECT_ROOT,
)

DATA_DIR = PROCESSED_DATA_DIR

ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "sentence-transformers/" "all-MiniLM-L6-v2"


def load_books():
    """
    Load master books dataset.
    Prefer deduplicated catalog if available.
    """
    print("=" * 60)
    print("LOADING MASTER BOOKS")
    print("=" * 60)

    dedup_path = DATA_DIR / "integrated" / "master_books_deduplicated.parquet"

    legacy_path = DATA_DIR / "integrated" / "master_books.parquet"

    if dedup_path.exists():
        books_path = dedup_path
        print("✅ Using deduplicated catalog")
    elif legacy_path.exists():
        books_path = legacy_path
        print("⚠️ Using legacy catalog")
    else:
        print("❌ No catalog found")
        return None

    print(f"Loading: {books_path}")

    books = pd.read_parquet(books_path)

    print(f"Books loaded: {len(books):,}")
    print(f"Columns: {books.columns.tolist()}")

    return books


def build_text_features(books):
    """
    Build semantic text fields from book metadata.
    """
    print("\n" + "=" * 60)
    print("BUILDING SEMANTIC TEXT FIELDS")
    print("=" * 60)

    # Combine relevant text fields for semantic search
    books["semantic_text"] = (
        books["title"].fillna("")
        + ". "
        + books["authors"].fillna("")
        + ". "
        + books["publisher"].fillna("")
        + ". "
        + books["language_code"].fillna("")
    )

    print("✅ Semantic text generated.")
    print(f"Sample: {books['semantic_text'].iloc[0][:100]}...")

    return books


def load_embedding_model():
    """
    Load the sentence transformer model.
    """
    print("\n" + "=" * 60)
    print("LOADING TRANSFORMER MODEL")
    print("=" * 60)

    model = SentenceTransformer(MODEL_NAME)

    print(f"✅ Loaded model: {MODEL_NAME}")
    print(f"   Max sequence length: {model.max_seq_length}")
    print(f"   Embedding dimension: {model.get_embedding_dimension()}")

    return model


def generate_embeddings(model, books, batch_size=256):
    """
    Generate embeddings for all books.
    """
    print("\n" + "=" * 60)
    print("GENERATING EMBEDDINGS")
    print("=" * 60)

    texts = books["semantic_text"].tolist()

    print(f"Generating embeddings for {len(texts):,} books...")
    print(f"Batch size: {batch_size}")

    embeddings = model.encode(
        texts, batch_size=batch_size, show_progress_bar=True, convert_to_numpy=True
    )

    print(f"✅ Embeddings generated.")
    print(f"   Shape: {embeddings.shape}")
    print(f"   Memory: {embeddings.nbytes / 1024**2:.2f} MB")

    return embeddings


def normalize_embeddings(embeddings):
    """
    Normalize embeddings for cosine similarity.
    """
    print("\n" + "=" * 60)
    print("NORMALIZING EMBEDDINGS")
    print("=" * 60)

    normalized = normalize(embeddings, norm="l2")

    print("✅ Embeddings normalized.")
    print(f"   Shape: {normalized.shape}")

    return normalized.astype("float32")


def build_faiss_index(embeddings):
    """
    Build FAISS index for fast similarity search.
    """
    print("\n" + "=" * 60)
    print("BUILDING FAISS INDEX")
    print("=" * 60)

    embedding_dim = embeddings.shape[1]

    # Using IndexFlatIP for inner product (cosine similarity with normalized vectors)
    index = faiss.IndexFlatIP(embedding_dim)
    index.add(embeddings)

    # Calculate memory usage
    memory_bytes = index.ntotal * index.d * 4  # 4 bytes per float32
    memory_mb = memory_bytes / 1024**2

    print(f"✅ FAISS index built.")
    print(f"   Vectors indexed: {index.ntotal:,}")
    print(f"   Dimension: {index.d}")
    print(f"   Memory: {memory_mb:.2f} MB")

    return index


def export_artifacts(books, embeddings, index):
    """
    Export all artifacts to disk.
    """
    print("\n" + "=" * 60)
    print("EXPORTING ARTIFACTS")
    print("=" * 60)

    # Paths
    books_path = ARTIFACT_DIR / "semantic_books.parquet"
    embeddings_path = ARTIFACT_DIR / "book_embeddings.npy"
    index_path = ARTIFACT_DIR / "books_faiss.index"
    metadata_path = ARTIFACT_DIR / "embedding_metadata.pkl"

    # Save books
    books.to_parquet(books_path, index=False)
    print(f"✅ Books saved: {books_path}")

    # Save embeddings
    np.save(embeddings_path, embeddings)
    print(f"✅ Embeddings saved: {embeddings_path}")

    # Save FAISS index
    faiss.write_index(index, str(index_path))
    print(f"✅ FAISS index saved: {index_path}")

    # Save metadata
    metadata = {
        "embedding_model": MODEL_NAME,
        "vector_dimension": embeddings.shape[1],
        "total_books": len(books),
        "embedding_dtype": str(embeddings.dtype),
        "faiss_index_type": type(index).__name__,
    }

    with open(metadata_path, "wb") as file:
        pickle.dump(metadata, file)
    print(f"✅ Metadata saved: {metadata_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("EXPORT SUMMARY")
    print("=" * 60)
    print(f"Books: {len(books):,}")
    print(f"Embedding dimension: {embeddings.shape[1]}")
    print(f"FAISS vectors: {index.ntotal:,}")
    print(f"Total artifacts size:")

    total_size = 0
    for path in [books_path, embeddings_path, index_path, metadata_path]:
        if path.exists():
            size = path.stat().st_size / 1024**2
            total_size += size
            print(f"  {path.name}: {size:.2f} MB")
    print(f"  Total: {total_size:.2f} MB")


def test_recommendation(index, books, query_text="Harry Potter", top_k=5):
    """
    Test the semantic search with a sample query.
    """
    print("\n" + "=" * 60)
    print("TESTING SEMANTIC SEARCH")
    print("=" * 60)

    # Load model for testing
    model = load_embedding_model()

    # Generate query embedding
    query_embedding = model.encode([query_text], convert_to_numpy=True)
    query_embedding = normalize(query_embedding, norm="l2").astype("float32")

    # Search
    distances, indices = index.search(query_embedding, top_k)

    print(f"\nQuery: '{query_text}'")
    print("\nTop results:")
    print("-" * 40)

    for i, (idx, dist) in enumerate(zip(indices[0], distances[0])):
        book = books.iloc[idx]
        print(f"{i+1}. {book['title']} (Score: {dist:.4f})")
        print(f"   Authors: {book['authors']}")
        print(f"   ISBN: {book['isbn']}")
        print()


def debug_paths():
    """
    Debug function to check paths.
    """
    print("=" * 60)
    print("DEBUG - PATHS")
    print("=" * 60)
    print(f"Script location: {Path(__file__).resolve()}")
    print(f"BASE_DIR: {PROJECT_ROOT}")
    print(f"DATA_DIR: {DATA_DIR}")
    print(f"ARTIFACT_DIR: {ARTIFACT_DIR}")

    print(f"\nChecking if directories exist:")
    print(f"BASE_DIR exists: {PROJECT_ROOT.exists()}")
    print(f"DATA_DIR exists: {DATA_DIR.exists()}")

    if DATA_DIR.exists():
        print(f"\n📁 Contents of {DATA_DIR}:")
        for item in DATA_DIR.iterdir():
            if item.is_dir():
                print(f"  📁 {item.name}")
            else:
                print(f"  📄 {item.name}")


def main():
    """
    Main execution function.
    """
    print("=" * 60)
    print("SEMANTIC EMBEDDING PIPELINE")
    print("=" * 60)

    # Debug paths
    debug_paths()

    # Load books
    books = load_books()

    if books is None:
        print("\n❌ Failed to load books. Exiting.")
        return

    # Build text features
    books = build_text_features(books)

    # Load embedding model
    model = load_embedding_model()

    # Generate embeddings
    embeddings = generate_embeddings(model, books)

    # Normalize embeddings
    embeddings = normalize_embeddings(embeddings)

    # Build FAISS index
    index = build_faiss_index(embeddings)

    # Export artifacts
    export_artifacts(books, embeddings, index)

    # Test with sample queries (only if we have enough books)
    if len(books) > 0:
        test_recommendation(index, books, query_text="Harry Potter", top_k=5)
        test_recommendation(index, books, query_text="science fiction space", top_k=5)
        test_recommendation(index, books, query_text="romance love story", top_k=5)

    print("\n" + "=" * 60)
    print("✅ SEMANTIC EMBEDDING PIPELINE COMPLETED!")
    print("=" * 60)

    print("\n💡 Next steps:")
    print("  1. Load embeddings: np.load('book_embeddings.npy')")
    print("  2. Load FAISS index: faiss.read_index('books_faiss.index')")
    print("  3. Use for semantic search or recommendations")


if __name__ == "__main__":
    main()
