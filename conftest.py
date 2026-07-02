"""
Pytest configuration for Author API tests.
"""

import sys
from pathlib import Path
from typing import Generator

# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker, Session
# pyrefly: ignore [missing-import]
from sqlalchemy.pool import StaticPool

# Add paths to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "apps" / "api"))
sys.path.insert(0, str(project_root / "apps" / "api" / "app"))

# pyrefly: ignore [missing-import]
from app.main import app
# pyrefly: ignore [missing-import]
from app.core.database import Base, get_db
# pyrefly: ignore [missing-import]
from app.models.user import User
# pyrefly: ignore [missing-import]
from app.dependencies.auth import get_current_user


# ============================================================
# TEST DATABASE SETUP
# ============================================================

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """Override the get_db dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ============================================================
# AUTH OVERRIDE
# ============================================================

class MockUser:
    """Mock user for testing."""
    id = 1
    email = "test@example.com"
    username = "testuser"
    is_active = True
    is_superuser = False


async def override_get_current_user() -> MockUser:
    """Override the get_current_user dependency for testing."""
    return MockUser()


# Override get_current_user for all import paths
app.dependency_overrides[get_current_user] = override_get_current_user

# Also try to override if imported from other paths
try:
    # pyrefly: ignore [missing-import]
    from app.api.v1.auth.dependencies import get_current_user as auth_deps_get_current_user
    app.dependency_overrides[auth_deps_get_current_user] = override_get_current_user
except (ImportError, AttributeError):
    pass


# ============================================================
# DISCOVERY SERVICE OVERRIDE
# ============================================================

class MockAuthorDiscoveryService:
    """Mock discovery service for testing."""
    
    def onboarding_authors(self, limit: int) -> list:
        """Return empty list for onboarding authors."""
        return []
    
    def build_discovery_response(self, sections_config) -> dict:
        """Return empty discovery response."""
        # pyrefly: ignore [missing-import]
        from app.api.v1.authors.schemas import AuthorDiscoveryResponse, AuthorDiscoverySection
        return AuthorDiscoveryResponse(sections=[])


def override_get_author_discovery_service() -> MockAuthorDiscoveryService:
    """Override the author discovery service dependency for testing."""
    return MockAuthorDiscoveryService()


try:
    # pyrefly: ignore [missing-import]
    from app.api.v1.authors.routes import get_author_discovery_service
    app.dependency_overrides[get_author_discovery_service] = override_get_author_discovery_service
except (ImportError, AttributeError):
    pass


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def client() -> TestClient:
    """Return a test client with auth headers pre-set."""
    return TestClient(app)


@pytest.fixture
def sample_author() -> dict:
    """Sample author data for testing."""
    return {
        "name": "J.K. Rowling",
        "bio": "British author best known for the Harry Potter series.",
        "birth_date": "1965-07-31",
        "nationality": "British",
    }


@pytest.fixture
def created_author(client: TestClient, sample_author: dict) -> dict:
    """Create a test author and return the created author data."""
    response = client.post("/api/v1/authors/", json=sample_author)
    if response.status_code == 201:
        return response.json()
    pytest.skip(f"Author creation failed with {response.status_code}: {response.text}")


# ============================================================
# TEST CLASSES
# ============================================================

class TestHealthCheck:
    """Test health check endpoints."""
    
    def test_authors_health(self, client: TestClient) -> None:
        """Test the authors health check endpoint."""
        response = client.get("/api/v1/authors/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "authors"


class TestCreateAuthor:
    """Test author creation endpoints."""
    
    def test_create_author_success(self, client: TestClient, sample_author: dict) -> None:
        """Test successful author creation."""
        response = client.post("/api/v1/authors/", json=sample_author)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_author["name"]
        assert "id" in data

    def test_create_author_missing_name(self, client: TestClient) -> None:
        """Test author creation with missing name."""
        response = client.post("/api/v1/authors/", json={"bio": "No name"})
        assert response.status_code == 422

    def test_create_author_empty_name(self, client: TestClient) -> None:
        """Test author creation with empty name."""
        response = client.post("/api/v1/authors/", json={"name": "", "bio": "Test"})
        assert response.status_code in [400, 422]


class TestGetAuthor:
    """Test get author endpoints."""
    
    def test_get_author_success(self, client: TestClient, created_author: dict) -> None:
        """Test successful author retrieval."""
        author_id = created_author["id"]
        response = client.get(f"/api/v1/authors/{author_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == author_id
        assert data["name"] == created_author["name"]

    def test_get_author_not_found(self, client: TestClient) -> None:
        """Test author retrieval for non-existent ID."""
        response = client.get("/api/v1/authors/999999")
        assert response.status_code == 404

    def test_get_author_invalid_id(self, client: TestClient) -> None:
        """Test author retrieval with invalid ID format."""
        response = client.get("/api/v1/authors/invalid")
        assert response.status_code == 422


class TestUpdateAuthor:
    """Test update author endpoints."""
    
    def test_update_author_success(self, client: TestClient, created_author: dict) -> None:
        """Test successful author update."""
        author_id = created_author["id"]
        update_data = {"name": "Joanne Rowling", "bio": "Updated bio"}
        response = client.put(f"/api/v1/authors/{author_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Joanne Rowling"

    def test_update_author_not_found(self, client: TestClient) -> None:
        """Test author update for non-existent ID."""
        response = client.put("/api/v1/authors/999999", json={"name": "Test"})
        assert response.status_code == 404


class TestDeleteAuthor:
    """Test delete author endpoints."""
    
    def test_delete_author_success(self, client: TestClient, created_author: dict) -> None:
        """Test successful author deletion."""
        author_id = created_author["id"]
        response = client.delete(f"/api/v1/authors/{author_id}")
        assert response.status_code in [200, 204]
        
        get_response = client.get(f"/api/v1/authors/{author_id}")
        assert get_response.status_code == 404

    def test_delete_author_not_found(self, client: TestClient) -> None:
        """Test author deletion for non-existent ID."""
        response = client.delete("/api/v1/authors/999999")
        assert response.status_code == 404


class TestListAuthors:
    """Test list authors endpoints."""
    
    def test_list_authors_success(self, client: TestClient) -> None:
        """Test successful author listing."""
        response = client.get("/api/v1/authors/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "items" in data
        assert "total" in data

    def test_list_authors_pagination(self, client: TestClient) -> None:
        """Test author listing with pagination."""
        response = client.get("/api/v1/authors/?skip=0&limit=5")
        assert response.status_code == 200

    def test_list_authors_invalid_limit(self, client: TestClient) -> None:
        """Test author listing with invalid limit."""
        response = client.get("/api/v1/authors/?limit=200")
        assert response.status_code == 422


class TestSearchAuthors:
    """Test search authors endpoints."""
    
    def test_search_authors(self, client: TestClient, created_author: dict) -> None:
        """Test successful author search."""
        response = client.get("/api/v1/authors/search?q=Rowling")
        assert response.status_code == 200

    def test_search_authors_empty_query(self, client: TestClient) -> None:
        """Test author search with empty query."""
        response = client.get("/api/v1/authors/search?q=")
        assert response.status_code == 422

    def test_search_authors_no_query(self, client: TestClient) -> None:
        """Test author search without query parameter."""
        response = client.get("/api/v1/authors/search")
        assert response.status_code == 422


class TestAutocompleteAuthors:
    """Test autocomplete authors endpoints."""
    
    def test_autocomplete(self, client: TestClient, created_author: dict) -> None:
        """Test successful author autocomplete."""
        response = client.get("/api/v1/authors/autocomplete?prefix=Row")
        assert response.status_code == 200

    def test_autocomplete_no_prefix(self, client: TestClient) -> None:
        """Test autocomplete without prefix."""
        response = client.get("/api/v1/authors/autocomplete")
        assert response.status_code == 422


class TestPopularAuthors:
    """Test popular authors endpoints."""
    
    def test_get_popular(self, client: TestClient) -> None:
        """Test getting popular authors."""
        response = client.get("/api/v1/authors/popular")
        assert response.status_code == 200

    def test_get_popular_with_limit(self, client: TestClient) -> None:
        """Test getting popular authors with limit."""
        response = client.get("/api/v1/authors/popular?limit=5")
        assert response.status_code == 200


class TestTopRatedAuthors:
    """Test top rated authors endpoints."""
    
    def test_get_top_rated(self, client: TestClient) -> None:
        """Test getting top rated authors."""
        response = client.get("/api/v1/authors/top-rated")
        assert response.status_code == 200

    def test_get_top_rated_with_min_rating(self, client: TestClient) -> None:
        """Test getting top rated authors with minimum rating."""
        response = client.get("/api/v1/authors/top-rated?min_rating=4.0")
        assert response.status_code == 200


class TestProlificAuthors:
    """Test prolific authors endpoints."""
    
    def test_get_prolific(self, client: TestClient) -> None:
        """Test getting prolific authors."""
        response = client.get("/api/v1/authors/prolific")
        assert response.status_code == 200


class TestFeaturedAuthors:
    """Test featured authors endpoints."""
    
    def test_get_featured(self, client: TestClient) -> None:
        """Test getting featured authors."""
        response = client.get("/api/v1/authors/featured")
        assert response.status_code == 200


class TestTrendingAuthors:
    """Test trending authors endpoints."""
    
    def test_get_trending(self, client: TestClient) -> None:
        """Test getting trending authors."""
        response = client.get("/api/v1/authors/trending")
        assert response.status_code == 200


class TestRandomAuthors:
    """Test random authors endpoints."""
    
    def test_get_random(self, client: TestClient) -> None:
        """Test getting random authors."""
        response = client.get("/api/v1/authors/random")
        assert response.status_code == 200

    def test_get_random_with_limit(self, client: TestClient) -> None:
        """Test getting random authors with limit."""
        response = client.get("/api/v1/authors/random?limit=10")
        assert response.status_code == 200


class TestFollowAuthor:
    """Test follow author endpoints."""
    
    def test_follow_author(self, client: TestClient, created_author: dict) -> None:
        """Test following an author."""
        payload = {
            "author_id": created_author["id"],
            "notification_preference": "all",
            "notes": "Test follow"
        }
        response = client.post("/api/v1/authors/follow", json=payload)
        assert response.status_code == 201

    def test_follow_author_invalid_id(self, client: TestClient) -> None:
        """Test following an author with invalid ID."""
        payload = {"author_id": 999999, "notification_preference": "all"}
        response = client.post("/api/v1/authors/follow", json=payload)
        assert response.status_code in [400, 404]

    def test_follow_author_missing_data(self, client: TestClient) -> None:
        """Test following an author with missing data."""
        response = client.post("/api/v1/authors/follow", json={})
        assert response.status_code == 422


class TestUnfollowAuthor:
    """Test unfollow author endpoints."""
    
    def test_unfollow_author(self, client: TestClient, created_author: dict) -> None:
        """Test unfollowing an author."""
        # First follow
        client.post("/api/v1/authors/follow", json={
            "author_id": created_author["id"],
            "notification_preference": "all"
        })
        response = client.delete(f"/api/v1/authors/follow/{created_author['id']}")
        assert response.status_code == 200

    def test_unfollow_author_invalid_id(self, client: TestClient) -> None:
        """Test unfollowing an author with invalid ID."""
        response = client.delete("/api/v1/authors/follow/999999")
        assert response.status_code in [400, 404]


class TestBulkFollow:
    """Test bulk follow endpoints."""
    
    def test_bulk_follow(self, client: TestClient, created_author: dict) -> None:
        """Test bulk following authors."""
        payload = {
            "author_ids": [created_author["id"]],
            "follow_source": "test"
        }
        response = client.post("/api/v1/authors/follow/bulk", json=payload)
        assert response.status_code == 200

    def test_bulk_follow_empty_list(self, client: TestClient) -> None:
        """Test bulk follow with empty list."""
        payload = {"author_ids": []}
        response = client.post("/api/v1/authors/follow/bulk", json=payload)
        assert response.status_code == 422


class TestGetFollowedAuthors:
    """Test get followed authors endpoints."""
    
    def test_get_followed(self, client: TestClient) -> None:
        """Test getting followed authors."""
        response = client.get("/api/v1/authors/following")
        assert response.status_code == 200


class TestDiscovery:
    """Test discovery endpoints."""
    
    def test_onboarding_discovery(self, client: TestClient) -> None:
        """Test onboarding discovery endpoint."""
        response = client.get("/api/v1/authors/discovery/onboarding")
        assert response.status_code == 200

    def test_discovery(self, client: TestClient) -> None:
        """Test discovery endpoint."""
        response = client.get("/api/v1/authors/discovery")
        assert response.status_code == 200
        data = response.json()
        assert "sections" in data

    def test_discovery_speed(self, client: TestClient) -> None:
        """Test discovery endpoint response speed."""
        import time
        start = time.time()
        response = client.get("/api/v1/authors/discovery")
        duration = time.time() - start
        assert response.status_code == 200
        assert duration < 2.0


class TestStats:
    """Test statistics endpoints."""
    
    def test_author_stats(self, client: TestClient) -> None:
        """Test getting author statistics."""
        response = client.get("/api/v1/authors/stats")
        assert response.status_code == 200

    def test_author_follow_stats(self, client: TestClient, created_author: dict) -> None:
        """Test getting author follow statistics."""
        response = client.get(f"/api/v1/authors/{created_author['id']}/stats/follow")
        assert response.status_code == 200

    def test_author_follow_stats_not_found(self, client: TestClient) -> None:
        """Test getting follow statistics for non-existent author."""
        response = client.get("/api/v1/authors/999999/stats/follow")
        assert response.status_code == 404


class TestPerformance:
    """Test performance of endpoints."""
    
    def test_search_speed(self, client: TestClient) -> None:
        """Test search endpoint response speed."""
        import time
        start = time.time()
        response = client.get("/api/v1/authors/search?q=Stephen")
        duration = time.time() - start
        assert response.status_code == 200
        assert duration < 2.0


class TestPagination:
    """Test pagination parameters."""
    
    def test_pagination_parameters(self, client: TestClient) -> None:
        """Test pagination parameters."""
        response = client.get("/api/v1/authors/?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "items" in data
        assert "total" in data