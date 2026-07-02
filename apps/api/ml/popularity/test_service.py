"""
Test script for the PopularityService.
Tests the service layer functionality.
"""

# pyrefly: ignore [missing-import]
from popularity_service import PopularityService
import pandas as pd

def test_service():
    """
    Test the popularity service functionality.
    """
    print("=" * 60)
    print("TESTING POPULARITY SERVICE")
    print("=" * 60)
    
    try:
        # Initialize service
        print("\n📌 Initializing PopularityService...")
        service = PopularityService()
        print("✅ Service initialized successfully")
        
        # Test 1: Get homepage recommendations
        print("\n" + "=" * 60)
        print("TEST 1: HOMEPAGE RECOMMENDATIONS")
        print("=" * 60)
        
        books = service.homepage(top_k=10)
        
        if books is not None and len(books) > 0:
            print(f"✅ Got {len(books)} recommendations")
            print("\n📚 Top 10 Homepage Recommendations:")
            print("-" * 40)
            
            # Display the results
            display_cols = ['rank', 'title', 'authors', 'category', 'adjusted_score']
            available_cols = [col for col in display_cols if col in books.columns]
            
            if available_cols:
                print(books[available_cols].to_string(index=False))
            else:
                print(books.to_string(index=False))
        else:
            print("❌ No recommendations returned")
        
        # Test 2: Get category recommendations
        print("\n" + "=" * 60)
        print("TEST 2: CATEGORY RECOMMENDATIONS")
        print("=" * 60)
        
        categories = ['Fantasy', 'Classic', 'Science Fiction']
        for category in categories:
            try:
                cat_books = service.category(category, top_k=5)
                if cat_books is not None and len(cat_books) > 0:
                    print(f"\n📚 Top 5 {category} Books:")
                    print("-" * 40)
                    display_cols = ['title', 'authors', 'adjusted_score']
                    available_cols = [col for col in display_cols if col in cat_books.columns]
                    if available_cols:
                        print(cat_books[available_cols].to_string(index=False))
                    else:
                        print(cat_books.to_string(index=False))
                else:
                    print(f"\n⚠️ No books found in {category} category")
            except Exception as e:
                print(f"\n❌ Error getting {category} recommendations: {e}")
        
        # Test 3: Get trending recommendations
        print("\n" + "=" * 60)
        print("TEST 3: TRENDING RECOMMENDATIONS")
        print("=" * 60)
        
        trending = service.trending(top_k=5)
        if trending is not None and len(trending) > 0:
            print(f"✅ Got {len(trending)} trending books")
            display_cols = ['rank', 'title', 'authors', 'adjusted_score']
            available_cols = [col for col in display_cols if col in trending.columns]
            if available_cols:
                print(trending[available_cols].to_string(index=False))
        else:
            print("❌ No trending recommendations returned")
        
        # Test 4: Get cold start recommendations
        print("\n" + "=" * 60)
        print("TEST 4: COLD START RECOMMENDATIONS")
        print("=" * 60)
        
        cold_start = service.cold_start(top_k=5)
        if cold_start is not None and len(cold_start) > 0:
            print(f"✅ Got {len(cold_start)} cold start recommendations")
            display_cols = ['rank', 'title', 'authors', 'adjusted_score']
            available_cols = [col for col in display_cols if col in cold_start.columns]
            if available_cols:
                print(cold_start[available_cols].to_string(index=False))
        else:
            print("❌ No cold start recommendations returned")
        
        # Test 5: Get popular books (no diversity)
        print("\n" + "=" * 60)
        print("TEST 5: POPULAR BOOKS (NO DIVERSITY)")
        print("=" * 60)
        
        popular = service.get_popular_books(top_k=10)
        if popular is not None and len(popular) > 0:
            print(f"✅ Got {len(popular)} popular books")
            display_cols = ['rank', 'title', 'authors', 'ratings_count', 'adjusted_score']
            available_cols = [col for col in display_cols if col in popular.columns]
            if available_cols:
                print(popular[available_cols].to_string(index=False))
        else:
            print("❌ No popular books returned")
        
        # Test 6: Get service statistics
        print("\n" + "=" * 60)
        print("TEST 6: SERVICE STATISTICS")
        print("=" * 60)
        
        stats = service.get_stats()
        if stats:
            print("📊 Service Statistics:")
            print("-" * 40)
            for key, value in stats.items():
                if key == "top_categories":
                    print(f"\n  Top Categories:")
                    for cat, count in value.items():
                        print(f"    {cat}: {count}")
                else:
                    print(f"  {key}: {value}")
        else:
            print("❌ No statistics available")
        
        # Test 7: Explain a recommendation
        print("\n" + "=" * 60)
        print("TEST 7: EXPLAIN RECOMMENDATION")
        print("=" * 60)
        
        # Get a book to explain
        first_book = service.homepage(top_k=1)
        if first_book is not None and len(first_book) > 0:
            isbn = first_book.iloc[0]['isbn']
            print(f"📖 Explaining book: {first_book.iloc[0]['title']}")
            print(f"   ISBN: {isbn}")
            
            explanation = service.explain(isbn)
            if explanation:
                print("\n📋 Explanation:")
                print("-" * 40)
                for key, value in explanation.items():
                    if key == 'ratings_count' and value:
                        print(f"  {key}: {value:,}")
                    else:
                        print(f"  {key}: {value}")
            else:
                print("❌ No explanation returned")
        else:
            print("❌ No book available to explain")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_service()