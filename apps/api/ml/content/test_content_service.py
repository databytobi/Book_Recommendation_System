"""
Test script for the ContentService.
Tests all functionality of the content-based recommendation service.
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

# pyrefly: ignore [missing-import]
from content_service import get_content_service, ContentService


def print_header(title: str, char: str = "=", length: int = 60):
    """Print a formatted header."""
    print("\n" + char * length)
    print(f"{title.upper()}")
    print(char * length)


def print_subheader(title: str, char: str = "-", length: int = 40):
    """Print a formatted subheader."""
    print(f"\n{title}")
    print(char * length)


def print_results(results: pd.DataFrame, title: str = "Results", max_results: int = 10):
    """
    Pretty print recommendation results.
    
    Parameters:
    -----------
    results : pd.DataFrame
        DataFrame with recommendation results
    title : str
        Section title
    max_results : int
        Maximum number of results to display
    """
    if results is None or results.empty:
        print("   ❌ No results found")
        return
    
    print(f"\n{title}:")
    print("-" * 40)
    
    # Determine which columns to display
    display_cols = []
    if 'rank' in results.columns:
        display_cols.append('rank')
    if 'title' in results.columns:
        display_cols.append('title')
    if 'authors' in results.columns:
        display_cols.append('authors')
    if 'similarity' in results.columns:
        display_cols.append('similarity')
    if 'category' in results.columns:
        display_cols.append('category')
    if 'average_rating' in results.columns:
        display_cols.append('average_rating')
    
    if not display_cols:
        display_cols = results.columns.tolist()
    
    # Display results
    for idx, (_, row) in enumerate(results.head(max_results).iterrows(), start=1):
        print(f"\n{idx}. {row.get('title', 'Unknown Title')}")
        
        if 'authors' in row and pd.notna(row.get('authors')):
            print(f"   Author: {row['authors']}")
        
        if 'similarity' in row and pd.notna(row.get('similarity')):
            print(f"   Similarity: {row['similarity']:.4f}")
        
        if 'category' in row and pd.notna(row.get('category')):
            print(f"   Category: {row['category']}")
        
        if 'average_rating' in row and pd.notna(row.get('average_rating')):
            print(f"   Rating: {row['average_rating']:.2f}")
        
        if 'ratings_count' in row and pd.notna(row.get('ratings_count')):
            print(f"   Ratings: {int(row['ratings_count']):,}")
        
        if 'isbn' in row and pd.notna(row.get('isbn')):
            print(f"   ISBN: {row['isbn']}")
    
    # Show summary
    total_results = len(results)
    if total_results > max_results:
        print(f"\n... and {total_results - max_results} more results")
    print(f"\n✅ Total: {total_results} results")


def test_service_initialization():
    """Test service initialization."""
    print_header("TEST 1: SERVICE INITIALIZATION")
    
    try:
        # Test getting the singleton instance
        service1 = get_content_service()
        service2 = get_content_service()
        
        if service1 is service2:
            print("✅ Singleton pattern works - both instances are the same")
        else:
            print("❌ Singleton pattern failed - instances are different")
        
        # Test creating a new instance
        service3 = ContentService(load_on_init=False)
        print(f"✅ New service instance created (lazy loading)")
        
        # Test health status
        health = service1.get_health_status()
        print(f"\n📊 Health Status:")
        for key, value in health.items():
            print(f"   {key}: {value}")
        
        return service1
        
    except Exception as e:
        print(f"❌ Error during initialization test: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_recommend_by_title(service: ContentService):
    """Test title-based recommendations."""
    print_header("TEST 2: RECOMMEND BY TITLE")
    
    test_cases = [
        ("Harry Potter", 5),
        ("Lord of the Rings", 3),
        ("To Kill a Mockingbird", 5),
        ("Non-existent Book That Doesn't Exist", 5),  # Should handle gracefully
    ]
    
    for title, top_k in test_cases:
        print_subheader(f"Query: '{title}' (top_k={top_k})")
        
        try:
            results = service.recommend_by_book(
                title=title,
                top_k=top_k,
                fuzzy_match=True
            )
            
            if results is not None and not results.empty:
                print(f"✅ Found {len(results)} recommendations")
                print_results(results, f"Recommendations for '{title}'", max_results=top_k)
            else:
                print(f"⚠️ No recommendations found for '{title}'")
                
        except Exception as e:
            print(f"❌ Error: {e}")


def test_recommend_by_isbn(service: ContentService):
    """Test ISBN-based recommendations."""
    print_header("TEST 3: RECOMMEND BY ISBN")
    
    # Get a sample ISBN from the service
    try:
        # Try to get a sample book
        sample_book = service.recommender.books.sample(1).iloc[0]
        sample_isbn = sample_book['isbn']
        sample_title = sample_book['title']
        
        print(f"Using sample book: '{sample_title}' (ISBN: {sample_isbn})")
        
        # Test with the sample ISBN
        print_subheader(f"Query ISBN: {sample_isbn}")
        
        results = service.recommend_by_isbn(
            isbn=sample_isbn,
            top_k=10,
            min_similarity=0.1
        )
        
        print_results(results, f"Books similar to '{sample_title}'", max_results=5)
        
        # Test with exclude same author
        print_subheader(f"Excluding same author")
        results_excluded = service.recommend_by_isbn(
            isbn=sample_isbn,
            top_k=10,
            exclude_same_author=True,
            min_similarity=0.1
        )
        
        print_results(results_excluded, f"Books similar to '{sample_title}' (excluding same author)", max_results=5)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_semantic_search(service: ContentService):
    """Test semantic search."""
    print_header("TEST 4: SEMANTIC SEARCH")
    
    test_queries = [
        "magic school fantasy wizard",
        "science fiction space exploration",
        "romance love story",
        "mystery thriller detective",
    ]
    
    for query in test_queries:
        print_subheader(f"Query: '{query}'")
        
        try:
            results = service.recommend_by_description(
                query=query,
                top_k=5
            )
            
            print_results(results, f"Semantic search results for '{query}'", max_results=5)
            
        except Exception as e:
            print(f"❌ Error: {e}")


def test_explain_recommendation(service: ContentService):
    """Test explanation functionality."""
    print_header("TEST 5: EXPLAIN RECOMMENDATION")
    
    test_titles = [
        "Harry Potter",
        "The Hobbit",
    ]
    
    for title in test_titles:
        print_subheader(f"Explaining recommendations for: '{title}'")
        
        try:
            explanation = service.explain(title, top_k=5)
            
            if explanation:
                print(f"\n📖 Query Book: {explanation.get('query_book', 'Unknown')}")
                
                matched_book = explanation.get('matched_book')
                if matched_book:
                    print(f"   Matched: {matched_book.get('title', 'Unknown')} by {matched_book.get('authors', 'Unknown')}")
                
                print(f"\n📚 Total Recommendations: {explanation.get('total_recommendations', 0)}")
                
                recommendations = explanation.get('recommendations')
                if recommendations is not None and not recommendations.empty:
                    print_results(recommendations, "Top Recommendations", max_results=5)
            else:
                print("❌ No explanation returned")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


def test_book_info(service: ContentService):
    """Test getting book information."""
    print_header("TEST 6: GET BOOK INFO")
    
    # Get a sample book
    try:
        sample_book = service.recommender.books.sample(1).iloc[0]
        sample_isbn = sample_book['isbn']
        sample_title = sample_book['title']
        
        print(f"Querying book: '{sample_title}' (ISBN: {sample_isbn})")
        
        book_info = service.get_book_info(sample_isbn)
        
        if book_info:
            print("\n📖 Book Information:")
            for key, value in book_info.items():
                if value is not None:
                    if key in ['ratings_count'] and isinstance(value, (int, float)):
                        print(f"   {key}: {int(value):,}")
                    elif key in ['average_rating'] and isinstance(value, (int, float)):
                        print(f"   {key}: {value:.2f}")
                    else:
                        print(f"   {key}: {value}")
        else:
            print("❌ No book info returned")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def test_similarity_calculation(service: ContentService):
    """Test similarity calculation."""
    print_header("TEST 7: SIMILARITY CALCULATION")
    
    try:
        # Get two random books
        sample_books = service.recommender.books.sample(2)
        isbn1 = sample_books.iloc[0]['isbn']
        isbn2 = sample_books.iloc[1]['isbn']
        title1 = sample_books.iloc[0]['title']
        title2 = sample_books.iloc[1]['title']
        
        print(f"📚 Book 1: {title1}")
        print(f"📚 Book 2: {title2}")
        
        similarity = service.get_similarity(isbn1, isbn2)
        
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
        print(f"❌ Error: {e}")


def test_service_statistics(service: ContentService):
    """Test getting service statistics."""
    print_header("TEST 8: SERVICE STATISTICS")
    
    try:
        stats = service.get_statistics()
        
        if stats:
            print("\n📊 Service Statistics:")
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
        print(f"❌ Error: {e}")


def test_cache_functionality(service: ContentService):
    """Test cache functionality."""
    print_header("TEST 9: CACHE FUNCTIONALITY")
    
    try:
        # First request (should cache)
        print("📌 First request (should cache):")
        start = datetime.now()
        results1 = service.recommend_by_book("Harry Potter", top_k=5)
        time1 = (datetime.now() - start).total_seconds()
        print(f"   Time: {time1:.4f} seconds")
        print(f"   Results: {len(results1) if results1 is not None else 0}")
        
        # Second request (should use cache)
        print("\n📌 Second request (should use cache):")
        start = datetime.now()
        results2 = service.recommend_by_book("Harry Potter", top_k=5)
        time2 = (datetime.now() - start).total_seconds()
        print(f"   Time: {time2:.4f} seconds")
        print(f"   Results: {len(results2) if results2 is not None else 0}")
        
        # Compare times
        if time2 < time1:
            print(f"\n✅ Cache working! Second request was {time1/time2:.2f}x faster")
        else:
            print("\n⚠️ Cache may not be working effectively")
        
        # Clear cache and test again
        print("\n📌 After clearing cache:")
        service.clear_cache()
        start = datetime.now()
        results3 = service.recommend_by_book("Harry Potter", top_k=5)
        time3 = (datetime.now() - start).total_seconds()
        print(f"   Time: {time3:.4f} seconds")
        print(f"   Results: {len(results3) if results3 is not None else 0}")
        
        if time3 > time2:
            print("✅ Cache cleared successfully")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def test_health_status(service: ContentService):
    """Test health status endpoint."""
    print_header("TEST 10: HEALTH STATUS")
    
    try:
        health = service.get_health_status()
        
        print("\n🏥 Health Status:")
        for key, value in health.items():
            if key == "status":
                status_emoji = "✅" if value == "healthy" else "⚠️" if value == "degraded" else "❌"
                print(f"   {key}: {status_emoji} {value}")
            else:
                print(f"   {key}: {value}")
                
    except Exception as e:
        print(f"❌ Error: {e}")


def test_refresh_functionality(service: ContentService):
    """Test refresh functionality."""
    print_header("TEST 11: REFRESH FUNCTIONALITY")
    
    try:
        print("📌 Refreshing service...")
        result = service.refresh()
        
        if result:
            print("✅ Service refreshed successfully")
            print(f"   Cache size after refresh: {len(service._cache)}")
            
            # Verify service is still working
            health = service.get_health_status()
            print(f"   Health status: {health.get('status', 'unknown')}")
        else:
            print("❌ Service refresh failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """
    Main test execution function.
    """
    print("=" * 60)
    print("CONTENT SERVICE TEST SUITE")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize service
    print_header("INITIALIZING CONTENT SERVICE")
    
    try:
        # Get the singleton instance
        service = test_service_initialization()
        
        if service is None:
            print("\n❌ Failed to initialize service. Exiting.")
            return
        
        # Run all tests
        test_recommend_by_title(service)
        test_recommend_by_isbn(service)
        test_semantic_search(service)
        test_explain_recommendation(service)
        test_book_info(service)
        test_similarity_calculation(service)
        test_service_statistics(service)
        test_cache_functionality(service)
        test_health_status(service)
        test_refresh_functionality(service)
        
        # Final summary
        print_header("TEST SUMMARY")
        print("\n✅ All tests completed successfully!")
        print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show final statistics
        stats = service.get_statistics()
        if stats:
            print(f"\n📊 Final Service Statistics:")
            print(f"   Books in index: {stats.get('total_books', 0):,}")
            print(f"   Cache size: {stats.get('cache_size', 0)}")
            print(f"   Status: {stats.get('status', 'unknown')}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()