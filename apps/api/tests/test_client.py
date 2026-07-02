"""
Test Client for Book Recommendation System API

Provides a configured TestClient for testing the FastAPI application.
Includes fixtures, helper functions, and utilities for testing.

Phase: Testing
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi.testclient import TestClient
import pytest
from datetime import datetime

# Add the parent directory to path
api_dir = Path(__file__).resolve().parents[1]  # Go up to apps/api
sys.path.insert(0, str(api_dir))

from app.main import app

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# TEST CLIENT CONFIGURATION
# ============================================================

class TestConfig:
    """Configuration for test client."""
    
    # API endpoints
    BASE_URL = "/api/v1"
    RECOMMENDATION_URL = f"{BASE_URL}/recommendation"
    HEALTH_URL = f"{BASE_URL}/health"
    
    # Test data
    TEST_USER_ID = 11676
    TEST_ISBN = "0446310786"  # To Kill a Mockingbird
    TEST_ISBN_2 = "0439139597"  # Harry Potter and the Goblet of Fire
    TEST_ISBN_3 = "0142001740"  # The Secret Life of Bees
    
    # Test queries
    TEST_SEARCH_QUERY = "science fiction space adventure"
    TEST_SEARCH_QUERY_2 = "magic fantasy wizard school"
    
    # Timeouts
    DEFAULT_TIMEOUT = 30
    LONG_TIMEOUT = 60


# ============================================================
# TEST CLIENT CREATION
# ============================================================

def create_test_client() -> TestClient:
    """
    Create a configured TestClient instance.
    
    Returns:
    --------
    TestClient: Configured test client
    """
    return TestClient(app, follow_redirects=False)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

class TestHelpers:
    """Helper functions for testing."""
    
    @staticmethod
    def assert_response_success(response, expected_status: int = 200) -> Dict[str, Any]:
        """
        Assert that a response was successful and return the JSON data.
        
        Parameters:
        -----------
        response : Response
            The response from the test client
        expected_status : int
            Expected HTTP status code
        
        Returns:
        --------
        Dict[str, Any]: Response JSON data
        """
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        data = response.json()
        return data
    
    @staticmethod
    def assert_response_error(response, expected_status: int = 400) -> Dict[str, Any]:
        """
        Assert that a response was an error and return the JSON data.
        
        Parameters:
        -----------
        response : Response
            The response from the test client
        expected_status : int
            Expected HTTP status code
        
        Returns:
        --------
        Dict[str, Any]: Response JSON data
        """
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        data = response.json()
        assert "error" in data or "detail" in data, "Error response missing error details"
        return data
    
    @staticmethod
    def print_response(response, title: str = "Response"):
        """
        Pretty print a response for debugging.
        
        Parameters:
        -----------
        response : Response
            The response from the test client
        title : str
            Title for the print output
        """
        print(f"\n{'=' * 60}")
        print(f"{title.upper()}")
        print(f"{'=' * 60}")
        print(f"Status Code: {response.status_code}")
        try:
            data = response.json()
            print(json.dumps(data, indent=2))
        except:
            print(response.text)
        print(f"{'=' * 60}\n")
    
    @staticmethod
    def print_metrics(metrics: Dict[str, Any], title: str = "Metrics"):
        """
        Pretty print metrics for debugging.
        
        Parameters:
        -----------
        metrics : Dict[str, Any]
            Metrics dictionary
        title : str
            Title for the print output
        """
        print(f"\n{'=' * 60}")
        print(f"{title.upper()}")
        print(f"{'=' * 60}")
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"  {key:20s}: {value:.4f}")
            elif isinstance(value, dict):
                print(f"  {key:20s}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key:18s}: {sub_value}")
            else:
                print(f"  {key:20s}: {value}")
        print(f"{'=' * 60}\n")


# ============================================================
# TEST FIXTURES (for pytest)
# ============================================================

@pytest.fixture
def test_client():
    """
    Pytest fixture for test client.
    
    Returns:
    --------
    TestClient: Configured test client
    """
    return create_test_client()


@pytest.fixture
def test_helpers():
    """
    Pytest fixture for test helpers.
    
    Returns:
    --------
    TestHelpers: Test helper functions
    """
    return TestHelpers()


@pytest.fixture
def test_config():
    """
    Pytest fixture for test configuration.
    
    Returns:
    --------
    TestConfig: Test configuration
    """
    return TestConfig()


# ============================================================
# API REQUEST HELPERS
# ============================================================

class APIRequestHelpers:
    """
    Helper functions for making API requests.
    """
    
    def __init__(self, client: TestClient):
        self.client = client
        self.config = TestConfig()
        self.helpers = TestHelpers()
    
    def health_check(self) -> Dict[str, Any]:
        """Make a health check request."""
        response = self.client.get(f"{self.config.HEALTH_URL}/liveness")
        return self.helpers.assert_response_success(response)
    
    def get_recommendations(
        self,
        user_id: int,
        top_k: int = 10,
        min_score: float = 0.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get recommendations for a user.
        
        Parameters:
        -----------
        user_id : int
            User ID
        top_k : int
            Number of recommendations
        min_score : float
            Minimum score threshold
        **kwargs : Additional parameters
        
        Returns:
        --------
        Dict[str, Any]: Response data
        """
        payload = {
            "user_id": user_id,
            "top_k": top_k,
            "min_score": min_score,
            **kwargs
        }
        response = self.client.post(
            f"{self.config.RECOMMENDATION_URL}/user",
            json=payload
        )
        return self.helpers.assert_response_success(response)
    
    def get_similar_books(
        self,
        isbn: str,
        top_k: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get similar books for an ISBN.
        
        Parameters:
        -----------
        isbn : str
            ISBN to find similar books for
        top_k : int
            Number of similar books
        **kwargs : Additional parameters
        
        Returns:
        --------
        Dict[str, Any]: Response data
        """
        payload = {
            "isbn": isbn,
            "top_k": top_k,
            **kwargs
        }
        response = self.client.post(
            f"{self.config.RECOMMENDATION_URL}/similar",
            json=payload
        )
        return self.helpers.assert_response_success(response)
    
    def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform semantic search.
        
        Parameters:
        -----------
        query : str
            Search query
        top_k : int
            Number of results
        **kwargs : Additional parameters
        
        Returns:
        --------
        Dict[str, Any]: Response data
        """
        payload = {
            "query": query,
            "top_k": top_k,
            **kwargs
        }
        response = self.client.post(
            f"{self.config.RECOMMENDATION_URL}/search",
            json=payload
        )
        return self.helpers.assert_response_success(response)
    
    def get_trending(
        self,
        top_k: int = 20,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get trending books.
        
        Parameters:
        -----------
        top_k : int
            Number of trending books
        **kwargs : Additional parameters
        
        Returns:
        --------
        Dict[str, Any]: Response data
        """
        params = {"top_k": top_k, **kwargs}
        response = self.client.get(
            f"{self.config.RECOMMENDATION_URL}/trending",
            params=params
        )
        return self.helpers.assert_response_success(response)
    
    def explain_recommendation(
        self,
        user_id: int,
        isbn: str
    ) -> Dict[str, Any]:
        """
        Get explanation for a recommendation.
        
        Parameters:
        -----------
        user_id : int
            User ID
        isbn : str
            Book ISBN
        
        Returns:
        --------
        Dict[str, Any]: Response data
        """
        response = self.client.get(
            f"{self.config.RECOMMENDATION_URL}/explain/{user_id}/{isbn}"
        )
        return self.helpers.assert_response_success(response)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        response = self.client.get(f"{self.config.RECOMMENDATION_URL}/stats")
        return self.helpers.assert_response_success(response)
    
    def update_weights(
        self,
        collaborative_weight: float = 0.50,
        content_weight: float = 0.30,
        popularity_weight: float = 0.20
    ) -> Dict[str, Any]:
        """
        Update recommendation weights.
        
        Parameters:
        -----------
        collaborative_weight : float
            Collaborative weight
        content_weight : float
            Content weight
        popularity_weight : float
            Popularity weight
        
        Returns:
        --------
        Dict[str, Any]: Response data
        """
        payload = {
            "collaborative_weight": collaborative_weight,
            "content_weight": content_weight,
            "popularity_weight": popularity_weight
        }
        response = self.client.put(
            f"{self.config.RECOMMENDATION_URL}/weights",
            json=payload
        )
        return self.helpers.assert_response_success(response)
    
    def reload_recommender(self) -> Dict[str, Any]:
        """Reload the recommender."""
        response = self.client.post(f"{self.config.RECOMMENDATION_URL}/reload")
        return self.helpers.assert_response_success(response)


# ============================================================
# MAIN TEST CLIENT
# ============================================================

# Create the main test client instance
client = TestClient(app)
helpers = TestHelpers()
config = TestConfig()

# Create API request helpers
api = APIRequestHelpers(client)


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST CLIENT EXAMPLE")
    print("=" * 60)
    
    # Test health check
    print("\n📊 Testing Health Check:")
    try:
        health = api.health_check()
        print(f"  Health: {health}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test recommendations
    print("\n📊 Testing Recommendations:")
    try:
        recs = api.get_recommendations(
            user_id=config.TEST_USER_ID,
            top_k=5
        )
        print(f"  Recommendations count: {recs.get('count', 0)}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test similar books
    print("\n📊 Testing Similar Books:")
    try:
        similar = api.get_similar_books(
            isbn=config.TEST_ISBN,
            top_k=5
        )
        print(f"  Similar books count: {similar.get('count', 0)}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test semantic search
    print("\n📊 Testing Semantic Search:")
    try:
        results = api.semantic_search(
            query=config.TEST_SEARCH_QUERY,
            top_k=5
        )
        print(f"  Results count: {results.get('count', 0)}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test trending
    print("\n📊 Testing Trending:")
    try:
        trending = api.get_trending(top_k=5)
        print(f"  Trending count: {trending.get('count', 0)}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test stats
    print("\n📊 Testing Stats:")
    try:
        stats = api.get_stats()
        print(f"  Stats: {stats}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n✅ All tests completed!")