from pathlib import Path
import faiss
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import sys

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

# pyrefly: ignore [missing-import]
from content_recommender import ContentRecommender


# Fix the path calculation - go up 4 levels to project root
# content/test_content.py -> content -> ml -> api -> apps -> project_root
BASE_DIR = Path(__file__).resolve().parents[4]

ARTIFACT_DIR = (
    BASE_DIR
    / "apps"
    / "api"
    / "ml"
    / "artifacts"
)


def load_artifacts():
    """
    Load content artifacts from the artifacts directory.
    
    Returns:
    --------
    tuple: (books_df, faiss_index)
    """
    print("=" * 60)
    print("LOADING CONTENT ARTIFACTS")
    print("=" * 60)
    
    books_path = ARTIFACT_DIR / "semantic_books.parquet"
    index_path = ARTIFACT_DIR / "books_faiss.index"
    metadata_path = ARTIFACT_DIR / "embedding_metadata.pkl"
    
    print(f"Looking for books at: {books_path}")
    print(f"Looking for index at: {index_path}")
    
    # Check if files exist
    if not books_path.exists():
        print(f"❌ Books file not found: {books_path}")
        print("Please run the embedding pipeline first:")
        print("  python apps/api/ml/features/embedding_pipeline.py")
        return None, None
    
    if not index_path.exists():
        print(f"❌ FAISS index not found: {index_path}")
        print("Please run the embedding pipeline first:")
        print("  python apps/api/ml/features/embedding_pipeline.py")
        return None, None
    
    # Load files
    try:
        books = pd.read_parquet(books_path)
        index = faiss.read_index(str(index_path))
        
        print(f"✅ Books loaded: {len(books):,}")
        print(f"✅ Vectors loaded: {index.ntotal:,}")
        print(f"✅ Vector dimension: {index.d}")
        
        # Load metadata if available
        if metadata_path.exists():
            import pickle
            with open(metadata_path, "rb") as f:
                metadata = pickle.load(f)
            print(f"✅ Model: {metadata.get('embedding_model', 'Unknown')}")
        
        return books, index
        
    except Exception as e:
        print(f"❌ Error loading artifacts: {e}")
        return None, None


def print_results(recommendations: pd.DataFrame, title: str = "Recommendations"):
    """
    Pretty print recommendation results.
    
    Parameters:
    -----------
    recommendations : pd.DataFrame
        DataFrame with recommendation results
    title : str
        Section title
    """
    if recommendations is None or recommendations.empty:
        print("   ❌ No recommendations found")
        return
    
    print()
    print("=" * 60)
    print(f"{title.upper()}")
    print("=" * 60)
    
    for rank, (_, row) in enumerate(recommendations.iterrows(), start=1):
        print(f"\n{rank}. {row.get('title', 'Unknown Title')} ({row.get('similarity', 0):.4f})")
        print(f"   Author: {row.get('authors', 'Unknown')}")
        print(f"   ISBN: {row.get('isbn', 'N/A')}")
        
        # Additional fields if available
        if 'category' in row and pd.notna(row.get('category')):
            print(f"   Category: {row['category']}")
        if 'publisher' in row and pd.notna(row.get('publisher')):
            print(f"   Publisher: {row['publisher']}")
        if 'publication_year' in row and pd.notna(row.get('publication_year')):
            print(f"   Year: {int(row['publication_year'])}")
        if 'average_rating' in row and pd.notna(row.get('average_rating')):
            print(f"   Rating: {row['average_rating']:.2f}")
        if 'ratings_count' in row and pd.notna(row.get('ratings_count')):
            print(f"   Ratings: {int(row['ratings_count']):,}")


def print_explanation(explanation: Optional[Dict[str, Any]]):
    """
    Pretty print book explanation.
    
    Parameters:
    -----------
    explanation : dict or None
        Book explanation dictionary
    """
    if explanation is None:
        print("   ❌ No explanation available")
        return
    
    print()
    print("=" * 60)
    print("BOOK EXPLANATION")
    print("=" * 60)
    
    for key, value in explanation.items():
        if value is not None:
            if key in ['ratings_count'] and isinstance(value, (int, float)):
                print(f"   {key}: {int(value):,}")
            elif key in ['average_rating', 'similarity'] and isinstance(value, (int, float)):
                print(f"   {key}: {value:.4f}")
            else:
                print(f"   {key}: {value}")
        else:
            print(f"   {key}: N/A")


def test_isbn_recommendation(recommender: ContentRecommender, isbn: str = None):
    """
    Test ISBN-based recommendations.
    """
    print()
    print("=" * 60)
    print("TEST 1: ISBN-BASED RECOMMENDATIONS")
    print("=" * 60)
    
    # Try to get a book if ISBN not provided
    if isbn is None:
        # Get a random book from the dataset
        sample_book = recommender.books.sample(1).iloc[0]
        isbn = sample_book['isbn']
        print(f"Using sample book: '{sample_book['title']}' (ISBN: {isbn})")
    
    # Get recommendations
    try:
        recommendations = recommender.recommend_by_isbn(
            isbn=isbn,
            top_k=10,
            min_similarity=0.1
        )
        print_results(recommendations, f"Books similar to ISBN: {isbn}")
        return recommendations
    except Exception as e:
        print(f"❌ Error in ISBN recommendation: {e}")
        return None


def test_title_recommendation(recommender: ContentRecommender, title: str = "Harry Potter"):
    """
    Test title-based recommendations.
    """
    print()
    print("=" * 60)
    print("TEST 2: TITLE-BASED RECOMMENDATIONS")
    print("=" * 60)
    
    try:
        recommendations = recommender.recommend_by_title(
            title=title,
            top_k=10,
            fuzzy_match=True
        )
        print_results(recommendations, f"Books similar to: {title}")
        return recommendations
    except Exception as e:
        print(f"❌ Error in title recommendation: {e}")
        return None


def test_text_query_recommendation(recommender: ContentRecommender, query: str = "science fiction space exploration"):
    """
    Test text query recommendations.
    """
    print()
    print("=" * 60)
    print("TEST 3: TEXT QUERY RECOMMENDATIONS")
    print("=" * 60)
    
    try:
        recommendations = recommender.recommend_by_text(
            query_text=query,
            top_k=10
        )
        print_results(recommendations, f"Books matching query: {query}")
        return recommendations
    except Exception as e:
        print(f"❌ Error in text query recommendation: {e}")
        return None


def test_similarity_calculation(recommender: ContentRecommender):
    """
    Test similarity calculation between two books.
    """
    print()
    print("=" * 60)
    print("TEST 4: SIMILARITY CALCULATION")
    print("=" * 60)
    
    try:
        # Get two random books
        sample_books = recommender.books.sample(2)
        isbn1 = sample_books.iloc[0]['isbn']
        isbn2 = sample_books.iloc[1]['isbn']
        
        title1 = sample_books.iloc[0]['title']
        title2 = sample_books.iloc[1]['title']
        
        print(f"📚 Book 1: {title1} (ISBN: {isbn1})")
        print(f"📚 Book 2: {title2} (ISBN: {isbn2})")
        
        similarity = recommender.get_similarity(isbn1, isbn2)
        
        if similarity is not None:
            print(f"\n✅ Similarity Score: {similarity:.4f}")
            
            # Interpret the score
            if similarity > 0.7:
                print("   Interpretation: Very similar books")
            elif similarity > 0.5:
                print("   Interpretation: Moderately similar")
            elif similarity > 0.3:
                print("   Interpretation: Somewhat similar")
            else:
                print("   Interpretation: Not very similar")
        else:
            print("❌ Could not calculate similarity")
    except Exception as e:
        print(f"❌ Error in similarity calculation: {e}")


def test_exclude_same_author(recommender: ContentRecommender):
    """
    Test excluding same author from recommendations.
    """
    print()
    print("=" * 60)
    print("TEST 5: EXCLUDE SAME AUTHOR")
    print("=" * 60)
    
    try:
        # Get a random book with an author
        sample_books = recommender.books[recommender.books['authors'].notna()]
        if len(sample_books) == 0:
            print("No books with authors found")
            return
        
        sample_book = sample_books.sample(1).iloc[0]
        isbn = sample_book['isbn']
        author = sample_book['authors']
        
        print(f"📚 Query book: {sample_book['title']}")
        print(f"   Author: {author}")
        
        # Get recommendations with author exclusion
        recommendations = recommender.recommend_by_isbn(
            isbn=isbn,
            top_k=10,
            exclude_same_author=True,
            min_similarity=0.1
        )
        
        print_results(recommendations, f"Recommendations (excluding {author})")
        
        # Check if any same-author books are in results
        if not recommendations.empty and 'authors' in recommendations.columns:
            same_author = recommendations[recommendations['authors'] == author]
            if len(same_author) > 0:
                print(f"⚠️ Still found {len(same_author)} books by same author")
            else:
                print("✅ No books by same author found")
    except Exception as e:
        print(f"❌ Error in exclude same author test: {e}")


def test_recommender_statistics(recommender: ContentRecommender):
    """
    Test getting recommender statistics.
    """
    print()
    print("=" * 60)
    print("TEST 6: RECOMMENDER STATISTICS")
    print("=" * 60)
    
    try:
        stats = recommender.get_statistics()
        if stats:
            print("📊 Content Recommender Statistics:")
            for key, value in stats.items():
                if key == "top_categories" and isinstance(value, dict):
                    print(f"\n   Top Categories:")
                    for cat, count in value.items():
                        print(f"     - {cat}: {count}")
                else:
                    print(f"   {key}: {value}")
        else:
            print("❌ No statistics available")
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")


def main():
    """
    Main test execution function.
    """
    print("=" * 60)
    print("CONTENT RECOMMENDER TEST SUITE")
    print("=" * 60)
    
    # Load artifacts
    books, index = load_artifacts()
    
    if books is None or index is None:
        print("\n❌ Failed to load artifacts. Exiting.")
        print("\n💡 Make sure you've run the embedding pipeline first:")
        print("   python apps/api/ml/features/embedding_pipeline.py")
        return
    
    # Initialize recommender
    print("\n" + "=" * 60)
    print("INITIALIZING RECOMMENDER")
    print("=" * 60)
    
    try:
        recommender = ContentRecommender(books, index)
        print(f"✅ ContentRecommender initialized")
        print(f"   {len(recommender.books):,} books loaded")
        print(f"   {recommender.index.ntotal:,} vectors in index")
    except Exception as e:
        print(f"❌ Error initializing recommender: {e}")
        return
    
    # Run all tests
    print("\n" + "=" * 60)
    print("RUNNING TESTS")
    print("=" * 60)
    
    # Test 1: ISBN-based recommendation
    recommendations_1 = test_isbn_recommendation(recommender)
    
    # Test 2: Title-based recommendation
    recommendations_2 = test_title_recommendation(recommender, "Harry Potter")
    
    # Test 3: Text query recommendation
    recommendations_3 = test_text_query_recommendation(recommender, "science fiction space adventure")
    
    # Test 4: Similarity calculation
    test_similarity_calculation(recommender)
    
    # Test 5: Exclude same author
    test_exclude_same_author(recommender)
    
    # Test 6: Statistics
    test_recommender_statistics(recommender)
    
    # Test 7: Book explanation (if we have recommendations)
    print()
    print("=" * 60)
    print("TEST 7: BOOK EXPLANATION")
    print("=" * 60)
    
    if recommendations_2 is not None and not recommendations_2.empty:
        first_book = recommendations_2.iloc[0]["isbn"]
        explanation = recommender.explain_book(first_book)
        print_explanation(explanation)
        
        # Also test get_most_similar
        if explanation:
            print()
            print("=" * 60)
            print("GET MOST SIMILAR (Detailed)")
            print("=" * 60)
            similar_books = recommender.get_most_similar(first_book, top_k=5)
            for book in similar_books:
                print(f"   {book['title']} (Similarity: {book['similarity']:.4f})")
    else:
        print("❌ No recommendations available to explain")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    tests_passed = [
        recommendations_1 is not None and not recommendations_1.empty,
        recommendations_2 is not None and not recommendations_2.empty,
    ]
    
    print(f"✅ ISBN-based test: {'PASSED' if tests_passed[0] else 'FAILED'}")
    print(f"✅ Title-based test: {'PASSED' if tests_passed[1] else 'FAILED'}")
    print(f"✅ Text query test: {'PASSED' if recommendations_3 is not None and not recommendations_3.empty else 'FAILED'}")
    
    print("\n✅ ALL TESTS COMPLETED!")


if __name__ == "__main__":
    main()