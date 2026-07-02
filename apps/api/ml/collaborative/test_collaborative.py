"""
Test script for the Collaborative Recommender.
Tests all functionality of the collaborative filtering recommendation service.
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

# pyrefly: ignore [missing-import]
from collaborative_recommender import CollaborativeRecommender, get_collaborative_service


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
    
    # Check for rank or index
    if 'rank' in results.columns:
        display_cols.append('rank')
    
    # Check for common columns
    for col in ['title', 'authors', 'isbn', 'score', 'similarity', 'book_rating', 'rating_count', 'avg_rating']:
        if col in results.columns and col not in display_cols:
            display_cols.append(col)
    
    if not display_cols:
        display_cols = results.columns.tolist()[:5]  # Show first 5 columns
    
    # Display results
    for idx, (_, row) in enumerate(results.head(max_results).iterrows(), start=1):
        print(f"\n{idx}. ", end="")
        
        # Title
        if 'title' in row and pd.notna(row.get('title')):
            print(f"{row['title']}")
        else:
            print(f"Book {idx}")
        
        # Authors
        if 'authors' in row and pd.notna(row.get('authors')):
            print(f"   Author: {row['authors']}")
        
        # ISBN
        if 'isbn' in row and pd.notna(row.get('isbn')):
            print(f"   ISBN: {row['isbn']}")
        
        # Score/Similarity
        if 'score' in row and pd.notna(row.get('score')):
            print(f"   Score: {row['score']:.4f}")
        elif 'similarity' in row and pd.notna(row.get('similarity')):
            print(f"   Similarity: {row['similarity']:.4f}")
        
        # Rating
        if 'book_rating' in row and pd.notna(row.get('book_rating')):
            print(f"   Rating: {row['book_rating']:.2f}")
        
        # Rating count
        if 'rating_count' in row and pd.notna(row.get('rating_count')):
            print(f"   Ratings: {int(row['rating_count']):,}")
        elif 'ratings_count' in row and pd.notna(row.get('ratings_count')):
            print(f"   Ratings: {int(row['ratings_count']):,}")
        
        # Average rating
        if 'avg_rating' in row and pd.notna(row.get('avg_rating')):
            print(f"   Avg Rating: {row['avg_rating']:.2f}")
    
    # Show summary
    total_results = len(results)
    if total_results > max_results:
        print(f"\n... and {total_results - max_results} more results")
    print(f"\n✅ Total: {total_results} results")


def test_initialization():
    """Test recommender initialization."""
    print_header("TEST 1: INITIALIZATION")
    
    try:
        # Test creating a new instance
        recommender = CollaborativeRecommender(load_on_init=False)
        print("✅ CollaborativeRecommender instance created")
        
        # Test loading artifacts
        print("\n📌 Loading artifacts...")
        success = recommender.load_artifacts()
        
        if success:
            print("✅ Artifacts loaded successfully")
            
            # Test singleton
            service1 = get_collaborative_service()
            service2 = get_collaborative_service()
            
            if service1 is service2:
                print("✅ Singleton pattern works - both instances are the same")
            else:
                print("❌ Singleton pattern failed - instances are different")
            
            return recommender
        else:
            print("❌ Failed to load artifacts")
            return None
            
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_stats(recommender: CollaborativeRecommender):
    """Test statistics."""
    print_header("TEST 2: STATISTICS")
    
    try:
        stats = recommender.get_stats()
        
        if stats:
            print("\n📊 Recommender Statistics:")
            for key, value in stats.items():
                if key == "model" and isinstance(value, dict):
                    print(f"\n   Model Info:")
                    for k, v in value.items():
                        print(f"     - {k}: {v}")
                elif key == "matrix" and isinstance(value, dict):
                    print(f"\n   Matrix Info:")
                    for k, v in value.items():
                        if k == "sparsity":
                            print(f"     - {k}: {v:.2f}%")
                        else:
                            print(f"     - {k}: {v}")
                else:
                    print(f"   {key}: {value}")
        else:
            print("❌ No statistics available")
            
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")


def test_user_history(recommender: CollaborativeRecommender):
    """Test getting user history."""
    print_header("TEST 3: USER HISTORY")
    
    try:
        # Get some active users
        active_users = recommender.get_active_users(top_k=5)
        
        if active_users.empty:
            print("⚠️ No active users found")
            return
        
        # Test with first active user
        test_user = active_users.index[0]
        rating_count = active_users.iloc[0]
        
        print(f"📌 Testing with user: {test_user} ({rating_count:,} ratings)")
        
        history = recommender.get_user_history(test_user, top_k=10)
        
        if not history.empty:
            print_results(history, f"User {test_user} History", max_results=10)
        else:
            print(f"❌ No history found for user {test_user}")
            
    except Exception as e:
        print(f"❌ Error getting user history: {e}")
        import traceback
        traceback.print_exc()


def test_user_recommendations(recommender: CollaborativeRecommender):
    """Test user recommendations."""
    print_header("TEST 4: USER RECOMMENDATIONS")
    
    try:
        # Get some active users
        active_users = recommender.get_active_users(top_k=3)
        
        if active_users.empty:
            print("⚠️ No active users found")
            return
        
        # Test with first active user
        test_user = active_users.index[0]
        
        print(f"📌 Testing with user: {test_user}")
        
        # Test 1: Basic recommendations
        print_subheader("Basic Recommendations")
        recs = recommender.recommend_for_user(test_user, top_k=10)
        print_results(recs, f"Recommendations for {test_user}", max_results=10)
        
        # Test 2: With author exclusion
        if not recs.empty and 'authors' in recs.columns:
            author_to_exclude = recs.iloc[0]['authors']
            print_subheader(f"Excluding author: {author_to_exclude}")
            
            recs_excluded = recommender.recommend_for_user(
                test_user,
                top_k=10,
                exclude_authors=[author_to_exclude]
            )
            print_results(recs_excluded, f"Recommendations (excluding {author_to_exclude})", max_results=10)
        
        # Test 3: With min score threshold
        print_subheader("With Minimum Score Threshold (0.5)")
        recs_filtered = recommender.recommend_for_user(
            test_user,
            top_k=10,
            min_score=0.5
        )
        print_results(recs_filtered, "Recommendations (min_score=0.5)", max_results=10)
        
    except Exception as e:
        print(f"❌ Error getting recommendations: {e}")
        import traceback
        traceback.print_exc()


def test_similar_books(recommender: CollaborativeRecommender):
    """Test similar books."""
    print_header("TEST 5: SIMILAR BOOKS")
    
    try:
        # Get a sample book from the dataset
        sample_books = recommender.books.sample(5)
        
        for _, book in sample_books.iterrows():
            isbn = book['isbn']
            title = book['title']
            
            print(f"\n📌 Testing with book: {title} (ISBN: {isbn})")
            
            # Get similar books
            similar = recommender.similar_books(isbn, top_k=5)
            
            if not similar.empty:
                print_results(similar, f"Similar to '{title}'", max_results=5)
            else:
                print(f"   No similar books found for: {title}")
            
            # Only test first 2 books
            if _ >= 1:
                break
                
    except Exception as e:
        print(f"❌ Error finding similar books: {e}")
        import traceback
        traceback.print_exc()


def test_top_books(recommender: CollaborativeRecommender):
    """Test top books."""
    print_header("TEST 6: TOP BOOKS")
    
    try:
        top_books = recommender.get_top_books(top_k=10, min_ratings=5)
        
        if not top_books.empty:
            print_results(top_books, "Top Books by Rating Count", max_results=10)
        else:
            print("❌ No top books found")
            
    except Exception as e:
        print(f"❌ Error getting top books: {e}")


def test_active_users(recommender: CollaborativeRecommender):
    """Test active users."""
    print_header("TEST 7: ACTIVE USERS")
    
    try:
        active_users = recommender.get_active_users(top_k=10)
        
        if not active_users.empty:
            print("\n📊 Top 10 Active Users:")
            print("-" * 40)
            for idx, (user_id, count) in enumerate(active_users.items(), start=1):
                print(f"{idx}. User {user_id}: {count:,} ratings")
        else:
            print("❌ No active users found")
            
    except Exception as e:
        print(f"❌ Error getting active users: {e}")


def test_health_check(recommender: CollaborativeRecommender):
    """Test health check."""
    print_header("TEST 8: HEALTH CHECK")
    
    try:
        health = recommender.health_check()
        
        print("\n🏥 Health Status:")
        print("-" * 40)
        
        status_emoji = "✅" if health.get("status") == "healthy" else "⚠️" if health.get("status") == "degraded" else "❌"
        print(f"   Status: {status_emoji} {health.get('status', 'unknown')}")
        print(f"   Is Loaded: {health.get('is_loaded', False)}")
        
        if "components" in health:
            print("\n   Components:")
            for component, loaded in health["components"].items():
                emoji = "✅" if loaded else "❌"
                print(f"     {emoji} {component}: {loaded}")
        
        if "missing_components" in health:
            print(f"\n   ⚠️ Missing components: {health['missing_components']}")
            
    except Exception as e:
        print(f"❌ Error during health check: {e}")


def test_user_similarity(recommender: CollaborativeRecommender):
    """Test user similarity calculation."""
    print_header("TEST 9: USER SIMILARITY")
    
    try:
        # Get active users
        active_users = recommender.get_active_users(top_k=5)
        
        if len(active_users) < 2:
            print("⚠️ Need at least 2 users to test similarity")
            return
        
        # Get first two users
        users = list(active_users.index)
        user1 = users[0]
        user2 = users[1]
        
        print(f"📌 Calculating similarity between:")
        print(f"   User 1: {user1} ({active_users[user1]:,} ratings)")
        print(f"   User 2: {user2} ({active_users[user2]:,} ratings)")
        
        similarity = recommender.get_user_similarity(user1, user2)
        
        if similarity is not None:
            print(f"\n✅ Similarity Score: {similarity:.4f}")
            
            # Interpret the score
            if similarity > 0.8:
                print("   Interpretation: Very similar users")
            elif similarity > 0.6:
                print("   Interpretation: Moderately similar")
            elif similarity > 0.4:
                print("   Interpretation: Somewhat similar")
            else:
                print("   Interpretation: Not very similar")
        else:
            print("❌ Could not calculate similarity")
            
    except Exception as e:
        print(f"❌ Error calculating user similarity: {e}")


def test_cache_functionality(recommender: CollaborativeRecommender):
    """Test cache functionality."""
    print_header("TEST 10: CACHE FUNCTIONALITY")
    
    try:
        # Get a user to test with
        active_users = recommender.get_active_users(top_k=1)
        if active_users.empty:
            print("⚠️ No active users found")
            return
        
        test_user = active_users.index[0]
        
        # First request (should cache)
        print("📌 First request (should cache):")
        import time
        start = time.time()
        recs1 = recommender.recommend_for_user(test_user, top_k=5, use_cache=True)
        time1 = time.time() - start
        print(f"   Time: {time1:.4f} seconds")
        print(f"   Results: {len(recs1) if recs1 is not None else 0}")
        
        # Second request (should use cache)
        print("\n📌 Second request (should use cache):")
        start = time.time()
        recs2 = recommender.recommend_for_user(test_user, top_k=5, use_cache=True)
        time2 = time.time() - start
        print(f"   Time: {time2:.4f} seconds")
        print(f"   Results: {len(recs2) if recs2 is not None else 0}")
        
        # Compare times
        if time2 < time1 and time1 > 0:
            speedup = time1 / time2 if time2 > 0 else float('inf')
            print(f"\n✅ Cache working! Second request was {speedup:.2f}x faster")
        else:
            print("\n⚠️ Cache may not be working effectively")
            print(f"   First request: {time1:.4f}s, Second: {time2:.4f}s")
        
        # Clear cache and test again
        print("\n📌 After clearing cache:")
        recommender.clear_cache()
        start = time.time()
        recs3 = recommender.recommend_for_user(test_user, top_k=5, use_cache=True)
        time3 = time.time() - start
        print(f"   Time: {time3:.4f} seconds")
        print(f"   Results: {len(recs3) if recs3 is not None else 0}")
        
        if time3 > time2:
            print("✅ Cache cleared successfully")
        
        # Show cache stats
        stats = recommender.get_stats()
        print(f"\n📊 Cache Stats:")
        print(f"   Cache size: {stats.get('cache_size', 0)}")
        print(f"   Cache TTL: {stats.get('cache_ttl', 3600)} seconds")
        
    except Exception as e:
        print(f"❌ Error testing cache: {e}")
        import traceback
        traceback.print_exc()


def test_refresh_functionality(recommender: CollaborativeRecommender):
    """Test refresh functionality."""
    print_header("TEST 11: REFRESH FUNCTIONALITY")
    
    try:
        print("📌 Refreshing recommender...")
        success = recommender.refresh()
        
        if success:
            print("✅ Recommender refreshed successfully")
            
            # Verify it's working
            health = recommender.health_check()
            print(f"   Health status: {health.get('status', 'unknown')}")
            print(f"   Cache size after refresh: {len(recommender._cache)}")
        else:
            print("❌ Refresh failed")
            
    except Exception as e:
        print(f"❌ Error during refresh: {e}")


def test_batch_recommendations(recommender: CollaborativeRecommender):
    """Test batch recommendations."""
    print_header("TEST 12: BATCH RECOMMENDATIONS")
    
    try:
        # Get some active users
        active_users = recommender.get_active_users(top_k=5)
        
        if active_users.empty:
            print("⚠️ No active users found")
            return
        
        user_ids = list(active_users.index[:3])  # Test with first 3 users
        
        print(f"📌 Generating recommendations for {len(user_ids)} users...")
        
        batch_recs = recommender.recommend_for_users(
            user_ids=user_ids,
            top_k=5
        )
        
        for user_id, recs in batch_recs.items():
            if not recs.empty:
                print(f"\n✅ User {user_id}: {len(recs)} recommendations")
                print_results(recs, f"Recommendations for {user_id}", max_results=3)
            else:
                print(f"\n⚠️ No recommendations for user {user_id}")
                
    except Exception as e:
        print(f"❌ Error testing batch recommendations: {e}")
        import traceback
        traceback.print_exc()


def main():
    """
    Main test execution function.
    """
    print("=" * 60)
    print("COLLABORATIVE RECOMMENDER TEST SUITE")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize recommender
    recommender = test_initialization()
    
    if recommender is None:
        print("\n❌ Failed to initialize recommender. Exiting.")
        print("\n💡 Make sure you've run the training first:")
        print("   python apps/api/ml/collaborative/train_collaborative.py")
        return
    
    # Run all tests
    test_stats(recommender)
    test_user_history(recommender)
    test_user_recommendations(recommender)
    test_similar_books(recommender)
    test_top_books(recommender)
    test_active_users(recommender)
    test_health_check(recommender)
    test_user_similarity(recommender)
    test_cache_functionality(recommender)
    test_refresh_functionality(recommender)
    test_batch_recommendations(recommender)
    
    # Final summary
    print_header("TEST SUMMARY")
    print("\n✅ All tests completed successfully!")
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show final statistics
    stats = recommender.get_stats()
    if stats:
        print(f"\n📊 Final Statistics:")
        print(f"   Status: {stats.get('status', 'unknown')}")
        print(f"   Users: {stats.get('users', 0):,}")
        print(f"   Books: {stats.get('books', 0):,}")
        print(f"   Interactions: {stats.get('interactions', 0):,}")
        print(f"   Cache size: {stats.get('cache_size', 0)}")


if __name__ == "__main__":
    main()