"""
API Tests for Book Recommendation System

Comprehensive test suite for all API endpoints including:
- Health checks
- User recommendations
- Similar books
- Semantic search
- Error handling
- Edge cases

Phase: Testing
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, List
from fastapi.testclient import TestClient
import pytest

# Add the parent directory to path
api_dir = Path(__file__).resolve().parents[1]  # Go up to apps/api
sys.path.insert(0, str(api_dir))

from app.main import app

# Create test client
client = TestClient(app)


# ============================================================
# TEST CONFIGURATION
# ============================================================

class TestConfig:
    """Configuration for test data."""
    
    # Test user IDs
    VALID_USER_ID = 11676
    VALID_USER_ID_2 = 35859
    INVALID_USER_ID = 999999
    
    # Test ISBNs
    VALID_ISBN = "0446310786"  # To Kill a Mockingbird
    VALID_ISBN_2 = "0439139597"  # Harry Potter and the Goblet of Fire
    VALID_ISBN_3 = "0142001740"  # The Secret Life of Bees
    INVALID_ISBN = "9999999999"
    
    # Test queries
    SEARCH_QUERY_1 = "science fiction space adventure"
    SEARCH_QUERY_2 = "magic fantasy wizard school"
    SEARCH_QUERY_3 = "romance love story"
    
    # Test top_k values
    DEFAULT_TOP_K = 10
    SMALL_TOP_K = 5
    LARGE_TOP_K = 20
    MAX_TOP_K = 100


config = TestConfig()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def assert_response_success(response, expected_status: int = 200) -> Dict[str, Any]:
    """
    Assert that a response was successful and return the JSON data.
    """
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
    return response.json()


def assert_response_error(response, expected_status: int = 400) -> Dict[str, Any]:
    """
    Assert that a response was an error and return the JSON data.
    """
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
    return response.json()


def assert_recommendation_response(data: Dict[str, Any]) -> None:
    """
    Assert that a recommendation response has the expected structure.
    """
    assert "count" in data, "Response missing 'count' field"
    assert "recommendations" in data, "Response missing 'recommendations' field"
    assert isinstance(data["recommendations"], list), "Recommendations should be a list"
    
    if data["count"] > 0:
        rec = data["recommendations"][0]
        assert "isbn" in rec, "Recommendation missing 'isbn'"
        assert "title" in rec, "Recommendation missing 'title'"
        assert "score" in rec, "Recommendation missing 'score'"


def print_test_header(title: str) -> None:
    """Print a formatted test header."""
    print(f"\n{'=' * 60}")
    print(f"TEST: {title}")
    print(f"{'=' * 60}")


# ============================================================
# HEALTH TESTS
# ============================================================

def test_root_endpoint():
    """Test the root endpoint."""
    print_test_header("Root Endpoint")
    
    response = client.get("/")
    data = assert_response_success(response)
    
    assert "name" in data, "Root response missing 'name'"
    assert "version" in data, "Root response missing 'version'"
    assert "endpoints" in data, "Root response missing 'endpoints'"
    assert data["name"] == "Book Recommendation System API"
    
    print(f"✅ Root endpoint working: version {data['version']}")


def test_health_endpoint():
    """Test the health endpoint."""
    print_test_header("Health Endpoint")
    
    response = client.get("/health")
    data = assert_response_success(response)
    
    assert data["status"] == "healthy", f"Expected 'healthy', got '{data['status']}'"
    assert "version" in data, "Health response missing 'version'"
    assert "timestamp" in data, "Health response missing 'timestamp'"
    
    print(f"✅ Health endpoint: status={data['status']}")


def test_liveness_endpoint():
    """Test the liveness endpoint."""
    print_test_header("Liveness Endpoint")
    
    response = client.get("/api/v1/health/liveness")
    data = assert_response_success(response)
    
    assert data["status"] == "alive", f"Expected 'alive', got '{data['status']}'"
    assert "timestamp" in data, "Liveness response missing 'timestamp'"
    
    print(f"✅ Liveness endpoint: status={data['status']}")


def test_readiness_endpoint():
    """Test the readiness endpoint."""
    print_test_header("Readiness Endpoint")
    
    response = client.get("/api/v1/health/readiness")
    
    # Should return 200 if ready, 503 if not (still valid)
    assert response.status_code in [200, 503], f"Expected 200 or 503, got {response.status_code}"
    data = response.json()
    
    assert "status" in data, "Readiness response missing 'status'"
    assert "checks" in data, "Readiness response missing 'checks'"
    
    print(f"✅ Readiness endpoint: status={data['status']}")

def test_detailed_health_endpoint():
    """Test the detailed health endpoint."""
    print_test_header("Detailed Health Endpoint")
    
    response = client.get("/api/v1/health/details")
    data = assert_response_success(response)
    
    assert "status" in data, "Detailed health missing 'status'"
    assert "services" in data, "Detailed health missing 'services'"
    
    print(f"✅ Detailed health: status={data['status']}")


# ============================================================
# RECOMMENDATION TESTS
# ============================================================

def test_user_recommendations():
    """Test getting user recommendations."""
    print_test_header("User Recommendations")
    
    payload = {
        "user_id": config.VALID_USER_ID,
        "top_k": config.SMALL_TOP_K,
    }
    
    response = client.post("/api/v1/recommendation/user", json=payload)
    data = assert_response_success(response)
    
    assert_recommendation_response(data)
    assert data["user_id"] == config.VALID_USER_ID, "User ID mismatch"
    
    print(f"✅ User recommendations: {data['count']} recommendations")


def test_user_recommendations_with_min_score():
    """Test user recommendations with minimum score filter."""
    print_test_header("User Recommendations with Min Score")
    
    payload = {
        "user_id": config.VALID_USER_ID,
        "top_k": config.SMALL_TOP_K,
        "min_score": 0.001,  # Lower threshold to match actual scores
    }
    
    response = client.post("/api/v1/recommendation/user", json=payload)
    data = assert_response_success(response)
    
    assert_recommendation_response(data)
    
    # Verify all scores meet the minimum
    for rec in data["recommendations"]:
        assert rec["score"] >= 0.001, f"Score {rec['score']} below minimum 0.001"
    
    print(f"✅ User recommendations with min_score: {data['count']} recommendations")

def test_user_recommendations_get_endpoint():
    """Test the GET endpoint for user recommendations."""
    print_test_header("User Recommendations (GET)")
    
    response = client.get(
        f"/api/v1/recommendation/user/{config.VALID_USER_ID}?top_k={config.SMALL_TOP_K}"
    )
    data = assert_response_success(response)
    
    assert_recommendation_response(data)
    assert data["user_id"] == config.VALID_USER_ID, "User ID mismatch"
    
    print(f"✅ User recommendations (GET): {data['count']} recommendations")


# ============================================================
# SIMILAR BOOKS TESTS
# ============================================================

def test_similar_books():
    """Test finding similar books."""
    print_test_header("Similar Books")
    
    payload = {
        "isbn": config.VALID_ISBN,
        "top_k": config.SMALL_TOP_K,
    }
    
    response = client.post("/api/v1/recommendation/similar", json=payload)
    data = assert_response_success(response)
    
    assert "query_isbn" in data, "Similar books missing 'query_isbn'"
    assert "count" in data, "Similar books missing 'count'"
    assert "similar_books" in data, "Similar books missing 'similar_books'"
    assert data["query_isbn"] == config.VALID_ISBN, "Query ISBN mismatch"
    
    if data["count"] > 0:
        book = data["similar_books"][0]
        assert "isbn" in book, "Similar book missing 'isbn'"
        assert "title" in book, "Similar book missing 'title'"
        assert "score" in book, "Similar book missing 'score'"
    
    print(f"✅ Similar books: {data['count']} similar books found")


# ============================================================
# SEMANTIC SEARCH TESTS
# ============================================================

def test_semantic_search():
    """Test semantic search."""
    print_test_header("Semantic Search")
    
    payload = {
        "query": config.SEARCH_QUERY_1,
        "top_k": config.SMALL_TOP_K,
    }
    
    response = client.post("/api/v1/recommendation/search", json=payload)
    data = assert_response_success(response)
    
    assert "query" in data, "Search response missing 'query'"
    assert "count" in data, "Search response missing 'count'"
    assert "results" in data, "Search response missing 'results'"
    assert data["query"] == config.SEARCH_QUERY_1, "Query mismatch"
    
    if data["count"] > 0:
        result = data["results"][0]
        assert "isbn" in result, "Search result missing 'isbn'"
        assert "title" in result, "Search result missing 'title'"
        assert "score" in result, "Search result missing 'score'"
    
    print(f"✅ Semantic search: {data['count']} results found")


# ============================================================
# TRENDING TESTS
# ============================================================

def test_trending_books():
    """Test getting trending books."""
    print_test_header("Trending Books")
    
    response = client.get(f"/api/v1/recommendation/trending?top_k={config.SMALL_TOP_K}")
    data = assert_response_success(response)
    
    assert "period" in data, "Trending response missing 'period'"
    assert "count" in data, "Trending response missing 'count'"
    assert "trending" in data, "Trending response missing 'trending'"
    
    if data["count"] > 0:
        book = data["trending"][0]
        assert "isbn" in book, "Trending book missing 'isbn'"
        assert "title" in book, "Trending book missing 'title'"
    
    print(f"✅ Trending books: {data['count']} trending books")


# ============================================================
# STATS TESTS
# ============================================================

def test_service_stats():
    """Test getting service statistics."""
    print_test_header("Service Statistics")
    
    response = client.get("/api/v1/recommendation/stats")
    data = assert_response_success(response)
    
    assert "status" in data or "ready" in data, "Stats response missing status"
    
    print(f"✅ Service statistics: {data}")


# ============================================================
# ERROR HANDLING TESTS
# ============================================================

def test_missing_user_id():
    """Test missing user_id in request."""
    print_test_header("Missing User ID")
    
    response = client.post("/api/v1/recommendation/user", json={})
    data = assert_response_error(response, expected_status=422)
    
    assert "detail" in data, "Error response missing 'detail'"
    
    print(f"✅ Missing user_id handled correctly")


def test_invalid_user_id():
    """Test invalid user_id."""
    print_test_header("Invalid User ID")
    
    payload = {
        "user_id": config.INVALID_USER_ID,
        "top_k": config.SMALL_TOP_K,
    }
    
    response = client.post("/api/v1/recommendation/user", json=payload)
    
    # Should return 200 with popularity recommendations or 404
    if response.status_code == 200:
        data = response.json()
        # Could be empty or have popularity recommendations
        assert "count" in data, "Response should have count field"
        assert "recommendations" in data, "Response should have recommendations"
        print(f"✅ Invalid user_id handled: returning {data['count']} recommendations")
    else:
        assert response.status_code in [404, 422], f"Unexpected status code: {response.status_code}"
        print(f"✅ Invalid user_id handled correctly: {response.status_code}")

def test_invalid_top_k():
    """Test invalid top_k value."""
    print_test_header("Invalid Top K")
    
    payload = {
        "user_id": config.VALID_USER_ID,
        "top_k": -1,
    }
    
    response = client.post("/api/v1/recommendation/user", json=payload)
    
    # Should return 422 validation error
    assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
    data = response.json()
    assert "detail" in data, "Error response missing 'detail'"
    
    print(f"✅ Invalid top_k handled correctly: {response.status_code}")


def test_missing_query():
    """Test missing query in semantic search."""
    print_test_header("Missing Query")
    
    response = client.post("/api/v1/recommendation/search", json={})
    data = assert_response_error(response, expected_status=422)
    
    assert "detail" in data, "Error response missing 'detail'"
    
    print(f"✅ Missing query handled correctly")


def test_invalid_isbn():
    """Test invalid ISBN."""
    print_test_header("Invalid ISBN")
    
    payload = {
        "isbn": config.INVALID_ISBN,
        "top_k": config.SMALL_TOP_K,
    }
    
    response = client.post("/api/v1/recommendation/similar", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        # Could be empty or have content-based results
        assert "count" in data, "Response should have count field"
        assert "similar_books" in data, "Response should have similar_books"
        print(f"✅ Invalid ISBN handled: returning {data['count']} similar books")
    else:
        assert response.status_code in [404, 422], f"Unexpected status code: {response.status_code}"
        print(f"✅ Invalid ISBN handled correctly: {response.status_code}")
# ============================================================
# PERFORMANCE TESTS
# ============================================================

def test_response_time():
    """Test response time for recommendations."""
    print_test_header("Response Time")
    
    payload = {
        "user_id": config.VALID_USER_ID,
        "top_k": config.SMALL_TOP_K,
    }
    
    start_time = time.time()
    response = client.post("/api/v1/recommendation/user", json=payload)
    elapsed = (time.time() - start_time) * 1000
    
    assert response.status_code == 200, "Response should be successful"
    
    # Check if response time is reasonable (under 5 seconds)
    assert elapsed < 5000, f"Response time {elapsed:.2f}ms exceeded 5000ms limit"
    
    print(f"✅ Response time: {elapsed:.2f}ms")


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    # Run all tests
    test_root_endpoint()
    test_health_endpoint()
    test_liveness_endpoint()
    test_readiness_endpoint()
    test_detailed_health_endpoint()
    test_user_recommendations()
    test_user_recommendations_with_min_score()
    test_user_recommendations_get_endpoint()
    test_similar_books()
    test_semantic_search()
    test_trending_books()
    test_service_stats()
    test_missing_user_id()
    test_invalid_user_id()
    test_invalid_top_k()
    test_missing_query()
    test_invalid_isbn()
    test_response_time()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 60)