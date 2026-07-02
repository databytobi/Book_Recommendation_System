"""
Test script for the Hybrid Recommender Service.
Tests all functionality including trending, search, similar books, and user recommendations.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

# pyrefly: ignore [missing-import]
from apps.api.ml.hybrid.hybrid_service import (
    HybridService, get_hybrid_service
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def print_header(title: str, char: str = "=", length: int = 60):
    """Print a formatted header."""
    print("\n" + char * length)
    print(f"{title.upper()}")
    print(char * length)


def print_subheader(title: str, char: str = "-", length: int = 40):
    """Print a formatted subheader."""
    print(f"\n{title}")
    print(char * length)


def print_results(
    title: str,
    results: pd.DataFrame,
    columns: list = None,
    limit: int = 10,
    show_stats: bool = True
):
    """
    Pretty print recommendation results.
    
    Parameters:
    -----------
    title : str
        Section title
    results : pd.DataFrame
        Results to display
    columns : list, optional
        Columns to display
    limit : int
        Maximum number of results to show
    show_stats : bool
        Whether to show statistics
    """
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    
    if results is None or results.empty:
        print("   ❌ No results found")
        return
    
    # Determine columns to display
    if columns is None:
        # Try to use common columns
        common_cols = ['rank', 'title', 'authors', 'score', 'hybrid_score', 'similarity', 'adjusted_score']
        columns = [col for col in common_cols if col in results.columns]
        if not columns:
            columns = results.columns.tolist()[:5]
    
    # Filter to existing columns
    existing_cols = [c for c in columns if c in results.columns]
    
    if not existing_cols:
        existing_cols = results.columns.tolist()[:5]
    
    # Show results
    display_df = results.head(limit)[existing_cols].copy()
    
    # Format numeric columns
    for col in display_df.columns:
        if display_df[col].dtype in ['float64', 'float32']:
            display_df[col] = display_df[col].map(lambda x: f"{x:.4f}" if pd.notna(x) else "N/A")
    
    print(display_df.to_string(index=False))
    
    # Show statistics
    if show_stats:
        print(f"\n📊 Summary: {len(results)} total results, showing {min(limit, len(results))}")
        
        # Show score range if available
        score_cols = ['score', 'hybrid_score', 'similarity', 'adjusted_score']
        for col in score_cols:
            if col in results.columns and not results[col].isna().all():
                print(f"   {col}: min={results[col].min():.4f}, max={results[col].max():.4f}, mean={results[col].mean():.4f}")


def test_service_initialization():
    """Test service initialization."""
    print_header("TEST 1: SERVICE INITIALIZATION")
    
    try:
        # Test singleton
        service1 = get_hybrid_service()
        service2 = get_hybrid_service()
        
        if service1 is service2:
            print("✅ Singleton pattern works - both instances are the same")
        else:
            print("❌ Singleton pattern failed - instances are different")
        
        # Test stats
        stats = service1.get_stats()
        if stats:
            print(f"\n📊 Service Stats:")
            print(f"   Status: {stats.get('status', 'unknown')}")
            print(f"   Cache size: {stats.get('cache_size', 0)}")
            
            if 'recommender' in stats:
                weights = stats['recommender'].get('weights', {})
                if weights:
                    print(f"\n   Weights:")
                    print(f"     Collaborative: {weights.get('collaborative', 0):.2f}")
                    print(f"     Content: {weights.get('content', 0):.2f}")
                    print(f"     Popularity: {weights.get('popularity', 0):.2f}")
        
        return service1
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_health_check(service: HybridService):
    """Test health check endpoint."""
    print_header("TEST 2: HEALTH CHECK")
    
    try:
        health = service.health_check()
        
        print("\n🏥 Health Status:")
        print("-" * 40)
        
        status_emoji = "✅" if health.get("status") == "healthy" else "⚠️" if health.get("status") == "degraded" else "❌"
        print(f"   Status: {status_emoji} {health.get('status', 'unknown')}")
        print(f"   Service Initialized: {health.get('service_initialized', False)}")
        print(f"   Cache Size: {health.get('cache_size', 0)}")
        print(f"   Request Count: {health.get('request_count', 0)}")
        
        # Show service status
        if "services" in health:
            print("\n   Services:")
            for service_name, loaded in health["services"].items():
                if service_name in ["popularity", "content", "collaborative"]:
                    emoji = "✅" if loaded else "❌"
                    print(f"     {emoji} {service_name}: {loaded}")
        
        return health
        
    except Exception as e:
        print(f"❌ Error in health check: {e}")
        return None


def test_trending_books(service: HybridService):
    """Test trending books."""
    print_header("TEST 3: TRENDING BOOKS")
    
    try:
        # Test with different top_k values
        test_cases = [5, 10, 20]
        
        for top_k in test_cases:
            print_subheader(f"Top {top_k} Trending Books")
            
            trending = service.trending_books(top_k=top_k)
            
            print_results(
                f"Trending Books (top {top_k})",
                trending,
                columns=['title', 'authors', 'adjusted_score', 'ratings_count'],
                limit=top_k
            )
            
            # Verify we got the right number
            if not trending.empty:
                print(f"✅ Returned {len(trending)} books")
            else:
                print("⚠️ No trending books returned")
            
    except Exception as e:
        print(f"❌ Error in trending books test: {e}")
        import traceback
        traceback.print_exc()


def test_semantic_search(service: HybridService):
    """Test semantic search."""
    print_header("TEST 4: SEMANTIC SEARCH")
    
    test_queries = [
        "science fiction space exploration",
        "magic fantasy wizard school",
        "romance love story",
        "mystery thriller detective",
        "history war biography"
    ]
    
    for query in test_queries:
        print_subheader(f"Query: '{query}'")
        
        try:
            results = service.search_books(
                query=query,
                top_k=10
            )
            
            print_results(
                f"Search Results for '{query}'",
                results,
                columns=['title', 'authors', 'hybrid_score', 'similarity'],
                limit=5
            )
            
            if not results.empty:
                print(f"✅ Found {len(results)} results")
            else:
                print("⚠️ No results found")
                
        except Exception as e:
            print(f"❌ Error in search: {e}")


def test_similar_books(service: HybridService):
    """Test similar books recommendations."""
    print_header("TEST 5: SIMILAR BOOKS")
    
    # Sample ISBNs to test
    test_isbns = [
        "0439136369",  # Harry Potter
        "0446310786",  # To Kill a Mockingbird
        "0553382565",  # A Game of Thrones
        "0142001740",  # The Secret Life of Bees
    ]
    
    for isbn in test_isbns:
        print_subheader(f"ISBN: {isbn}")
        
        try:
            # Get book title if available
            similar = service.recommend_similar_books(
                isbn=isbn,
                top_k=5
            )
            
            # Show the book we're finding similar for
            try:
                # Try to get book info from content service
                book_info = service.recommender.content_service.get_book_info(isbn)
                if book_info:
                    print(f"📚 Query Book: {book_info.get('title', 'Unknown')}")
                    print(f"   Author: {book_info.get('authors', 'Unknown')}")
            except:
                pass
            
            print_results(
                f"Similar Books (ISBN: {isbn})",
                similar,
                columns=['title', 'authors', 'hybrid_score', 'similarity'],
                limit=5
            )
            
            if not similar.empty:
                print(f"✅ Found {len(similar)} similar books")
            else:
                print("⚠️ No similar books found")
                
        except Exception as e:
            print(f"❌ Error finding similar books for {isbn}: {e}")


def test_user_recommendations(service: HybridService):
    """Test user recommendations."""
    print_header("TEST 6: USER RECOMMENDATIONS")
    
    # Sample users to test (from the active users list)
    test_users = [
        11676,   # Most active user
        35859,   # Second most active
        153662,  # Third most active
    ]
    
    for user_id in test_users:
        print_subheader(f"User ID: {user_id}")
        
        try:
            results = service.recommend_for_user(
                user_id=user_id,
                top_k=10,
                min_score=0.1
            )
            
            print_results(
                f"Recommendations for User {user_id}",
                results,
                columns=['title', 'authors', 'hybrid_score', 'score'],
                limit=10
            )
            
            if not results.empty:
                print(f"✅ Found {len(results)} recommendations")
                
                # Show score breakdown if available
                if 'hybrid_score' in results.columns:
                    print(f"   Avg hybrid score: {results['hybrid_score'].mean():.4f}")
                    print(f"   Max hybrid score: {results['hybrid_score'].max():.4f}")
            else:
                print("⚠️ No recommendations found")
                
        except Exception as e:
            print(f"❌ Error recommending for user {user_id}: {e}")


def test_batch_recommendations(service: HybridService):
    """Test batch recommendations."""
    print_header("TEST 7: BATCH RECOMMENDATIONS")
    
    test_users = [11676, 35859, 153662]
    
    try:
        print(f"📌 Generating recommendations for {len(test_users)} users...")
        
        batch_results = service.recommend_for_users(
            user_ids=test_users,
            top_k=5
        )
        
        for user_id, recs in batch_results.items():
            if not recs.empty:
                print(f"\n✅ User {user_id}: {len(recs)} recommendations")
                print_results(
                    f"Batch Recommendations for User {user_id}",
                    recs,
                    columns=['title', 'authors', 'hybrid_score'],
                    limit=3
                )
            else:
                print(f"\n⚠️ No recommendations for user {user_id}")
                
    except Exception as e:
        print(f"❌ Error in batch recommendations: {e}")


def test_explain_recommendation(service: HybridService):
    """Test recommendation explanation."""
    print_header("TEST 8: EXPLAIN RECOMMENDATION")
    
    try:
        # Get some recommendations first
        recs = service.recommend_for_user(11676, top_k=5)
        
        if not recs.empty:
            # Explain the first recommendation
            first_row = recs.iloc[0]
            explanation = service.explain(first_row)
            
            print("\n📖 Recommendation Explanation:")
            print("-" * 40)
            print(f"   Title: {explanation.get('title', 'Unknown')}")
            print(f"   Hybrid Score: {explanation.get('hybrid_score', 0):.4f}")
            
            if 'score_breakdown' in explanation and explanation['score_breakdown']:
                print("\n   Score Breakdown:")
                breakdown = explanation['score_breakdown']
                for key, value in breakdown.items():
                    print(f"     {key}: {value:.4f}")
            
            print(f"\n   Weights:")
            print(f"     Collaborative: {explanation.get('collaborative_weight', 0):.2f}")
            print(f"     Content: {explanation.get('content_weight', 0):.2f}")
            print(f"     Popularity: {explanation.get('popularity_weight', 0):.2f}")
            
        else:
            print("⚠️ No recommendations available to explain")
            
    except Exception as e:
        print(f"❌ Error in explain test: {e}")


def test_cache_functionality(service: HybridService):
    """Test cache functionality."""
    print_header("TEST 9: CACHE FUNCTIONALITY")
    
    try:
        import time
        
        user_id = 11676
        
        # First request (should cache)
        print("📌 First request (should cache):")
        start = time.time()
        recs1 = service.recommend_for_user(user_id, top_k=5, use_cache=True)
        time1 = time.time() - start
        print(f"   Time: {time1:.4f} seconds")
        print(f"   Results: {len(recs1) if recs1 is not None else 0}")
        
        # Second request (should use cache)
        print("\n📌 Second request (should use cache):")
        start = time.time()
        recs2 = service.recommend_for_user(user_id, top_k=5, use_cache=True)
        time2 = time.time() - start
        print(f"   Time: {time2:.4f} seconds")
        print(f"   Results: {len(recs2) if recs2 is not None else 0}")
        
        # Compare times
        if time2 < time1 and time1 > 0:
            speedup = time1 / time2 if time2 > 0 else float('inf')
            print(f"\n✅ Cache working! Second request was {speedup:.2f}x faster")
        else:
            print("\n⚠️ Cache may not be working effectively")
        
        # Clear cache and test again
        print("\n📌 After clearing cache:")
        service.clear_cache()
        start = time.time()
        recs3 = service.recommend_for_user(user_id, top_k=5, use_cache=True)
        time3 = time.time() - start
        print(f"   Time: {time3:.4f} seconds")
        print(f"   Results: {len(recs3) if recs3 is not None else 0}")
        
        if time3 > time2:
            print("✅ Cache cleared successfully")
        
        # Show cache stats
        stats = service.get_stats()
        print(f"\n📊 Cache Stats:")
        print(f"   Cache size: {stats.get('cache_size', 0)}")
        print(f"   Cache TTL: {stats.get('cache_ttl', 3600)} seconds")
        
    except Exception as e:
        print(f"❌ Error testing cache: {e}")


def test_weight_configuration(service: HybridService):
    """Test weight configuration."""
    print_header("TEST 10: WEIGHT CONFIGURATION")
    
    try:
        # Get current weights
        stats = service.get_stats()
        current_weights = stats.get('recommender', {}).get('weights', {})
        
        print("📌 Current Weights:")
        print(f"   Collaborative: {current_weights.get('collaborative', 0):.2f}")
        print(f"   Content: {current_weights.get('content', 0):.2f}")
        print(f"   Popularity: {current_weights.get('popularity', 0):.2f}")
        
        # Test updating weights
        print("\n📌 Updating weights...")
        success = service.update_weights(
            collaborative_weight=0.6,
            content_weight=0.3,
            popularity_weight=0.1
        )
        
        if success:
            print("✅ Weights updated successfully")
            
            # Verify new weights
            new_stats = service.get_stats()
            new_weights = new_stats.get('recommender', {}).get('weights', {})
            
            print("\n📌 New Weights:")
            print(f"   Collaborative: {new_weights.get('collaborative', 0):.2f}")
            print(f"   Content: {new_weights.get('content', 0):.2f}")
            print(f"   Popularity: {new_weights.get('popularity', 0):.2f}")
            
            # Test recommendations with new weights
            recs = service.recommend_for_user(11676, top_k=5)
            if not recs.empty:
                print(f"\n✅ Recommendations generated with new weights: {len(recs)} results")
        else:
            print("❌ Failed to update weights")
            
    except Exception as e:
        print(f"❌ Error in weight configuration test: {e}")


def test_service_stats(service: HybridService):
    """Test service statistics."""
    print_header("TEST 11: SERVICE STATISTICS")
    
    try:
        stats = service.get_stats()
        
        if stats:
            print("\n📊 Service Statistics:")
            for key, value in stats.items():
                if key == "recommender" and isinstance(value, dict):
                    print(f"\n   Recommender Stats:")
                    for k, v in value.items():
                        if k == "weights" and isinstance(v, dict):
                            print(f"\n     Weights:")
                            for wk, wv in v.items():
                                print(f"       {wk}: {wv:.2f}")
                        elif k == "cache" and isinstance(v, dict):
                            print(f"\n     Cache:")
                            for ck, cv in v.items():
                                print(f"       {ck}: {cv}")
                        else:
                            print(f"     {k}: {v}")
                else:
                    print(f"   {key}: {value}")
        else:
            print("❌ No statistics available")
            
    except Exception as e:
        print(f"❌ Error getting stats: {e}")


def test_refresh_functionality(service: HybridService):
    """Test refresh functionality."""
    print_header("TEST 12: REFRESH FUNCTIONALITY")
    
    try:
        print("📌 Refreshing hybrid service...")
        success = service.refresh()
        
        if success:
            print("✅ Service refreshed successfully")
            
            # Verify it's working
            health = service.health_check()
            print(f"   Health status: {health.get('status', 'unknown')}")
            print(f"   Cache size after refresh: {service._cache_size if hasattr(service, '_cache_size') else 0}")
        else:
            print("❌ Refresh failed")
            
    except Exception as e:
        print(f"❌ Error during refresh: {e}")


def main():
    """
    Main test execution function.
    """
    print("=" * 60)
    print("HYBRID RECOMMENDER TEST SUITE")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize service
    service = test_service_initialization()
    
    if service is None:
        print("\n❌ Failed to initialize service. Exiting.")
        return
    
    # Run all tests
    test_health_check(service)
    test_trending_books(service)
    test_semantic_search(service)
    test_similar_books(service)
    test_user_recommendations(service)
    test_batch_recommendations(service)
    test_explain_recommendation(service)
    test_cache_functionality(service)
    test_weight_configuration(service)
    test_service_stats(service)
    test_refresh_functionality(service)
    
    # Final summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    # Show final stats
    stats = service.get_stats()
    if stats:
        print(f"\n📊 Final Service Statistics:")
        print(f"   Status: {stats.get('status', 'unknown')}")
        print(f"   Cache size: {stats.get('cache_size', 0)}")
        print(f"   Request count: {stats.get('request_count', 0)}")
        
        if 'recommender' in stats:
            weights = stats['recommender'].get('weights', {})
            if weights:
                print(f"\n   Current Weights:")
                print(f"     Collaborative: {weights.get('collaborative', 0):.2f}")
                print(f"     Content: {weights.get('content', 0):.2f}")
                print(f"     Popularity: {weights.get('popularity', 0):.2f}")
    
    print(f"\n✅ ALL TESTS COMPLETED!")
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()