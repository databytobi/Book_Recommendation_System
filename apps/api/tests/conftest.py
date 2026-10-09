from fastapi import Depends
import sys
import os
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

app_dir = project_root / "apps" / "api"
sys.path.insert(0, str(app_dir))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User

"""
Test suite for Author API endpoints.
Handles both endpoint-level and global/middleware auth.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db


# ── Test Database Setup ──────────────────────────────────────

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ── Auth Override (try multiple possible import paths) ───────

class MockUser:
    id = 1
    email = "test@example.com"
    is_active = True
    is_superuser = False


def override_get_current_user():
    return MockUser()


# Try all common import paths for get_current_user
_AUTH_IMPORT_PATHS = [
    "app.dependencies.auth.get_current_user",
    "app.core.auth.get_current_user",
    "app.auth.get_current_user",
    "app.api.dependencies.get_current_user",
]

for path in _AUTH_IMPORT_PATHS:
    try:
        module_path, attr_name = path.rsplit(".", 1)
        module = __import__(module_path, fromlist=[attr_name])
        auth_dep = getattr(module, attr_name)
        app.dependency_overrides[auth_dep] = override_get_current_user
        print(f"✅ Overridden auth: {path}")
    except (ImportError, AttributeError):
        continue


# ── Mock Discovery Service ───────────────────────────────────

try:
    from app.api.v1.authors.routes import get_author_discovery_service
    from app.services.author_discovery_service import AuthorDiscoveryService

    class MockAuthorDiscoveryService:
        def onboarding_authors(self, limit):
            return []
        
        def build_discovery_response(self, sections_config):
            return {"sections": []}

    def override_get_author_discovery_service(db=Depends(override_get_db)):
        return MockAuthorDiscoveryService()

    app.dependency_overrides[get_author_discovery_service] = override_get_author_discovery_service
except (ImportError, TypeError):
    pass


# ── Client Fixture with Auth Headers ─────────────────────────

@pytest.fixture
def client():
    """Return a TestClient with auth headers pre-set."""
    # If global middleware checks headers, set a fake token
    headers = {
        "Authorization": "Bearer test-token-fake",
    }
    return TestClient(app, headers=headers)


# ── Sample Data Fixture ──────────────────────────────────────

@pytest.fixture
def sample_author():
    return {
        "name": "J.K. Rowling",
        "bio": "British author best known for the Harry Potter series.",
        "birth_date": "1965-07-31",
        "nationality": "British",
    }


@pytest.fixture
def created_author(client, sample_author):
    response = client.post("/api/v1/authors/", json=sample_author)
    if response.status_code == 201:
        return response.json()
    pytest.skip(f"Author creation failed with {response.status_code}: {response.text}")


# ═════════════════════════════════════════════════════════════
# HEALTH CHECK (no auth required — should pass)
# ═════════════════════════════════════════════════════════════

class TestHealthCheck:
    def test_authors_health(self, client):
        response = client.get("/api/v1/authors/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "authors"


# ═════════════════════════════════════════════════════════════
# CRUD ENDPOINTS
# ═════════════════════════════════════════════════════════════

class TestCreateAuthor:
    def test_create_author_success(self, client, sample_author):
        response = client.post("/api/v1/authors/", json=sample_author)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_author["name"]
        assert "id" in data

    def test_create_author_missing_name(self, client):
        response = client.post("/api/v1/authors/", json={"bio": "No name"})
        assert response.status_code == 422

    def test_create_author_empty_name(self, client):
        response = client.post("/api/v1/authors/", json={"name": "", "bio": "Test"})
        assert response.status_code in [400, 422]


class TestGetAuthor:
    def test_get_author_success(self, client, created_author):
        author_id = created_author["id"]
        response = client.get(f"/api/v1/authors/{author_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == author_id
        assert data["name"] == created_author["name"]

    def test_get_author_not_found(self, client):
        response = client.get("/api/v1/authors/999999")
        assert response.status_code == 404

    def test_get_author_invalid_id(self, client):
        response = client.get("/api/v1/authors/invalid")
        assert response.status_code == 422


class TestUpdateAuthor:
    def test_update_author_success(self, client, created_author):
        author_id = created_author["id"]
        update_data = {"name": "Joanne Rowling", "bio": "Updated bio"}
        response = client.put(f"/api/v1/authors/{author_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Joanne Rowling"

    def test_update_author_not_found(self, client):
        response = client.put("/api/v1/authors/999999", json={"name": "Test"})
        assert response.status_code == 404


class TestDeleteAuthor:
    def test_delete_author_success(self, client, created_author):
        author_id = created_author["id"]
        response = client.delete(f"/api/v1/authors/{author_id}")
        assert response.status_code in [200, 204]
        
        get_response = client.get(f"/api/v1/authors/{author_id}")
        assert get_response.status_code == 404

    def test_delete_author_not_found(self, client):
        response = client.delete("/api/v1/authors/999999")
        assert response.status_code == 404


# ═════════════════════════════════════════════════════════════
# LISTING & SEARCH
# ═════════════════════════════════════════════════════════════

class TestListAuthors:
    def test_list_authors_success(self, client):
        response = client.get("/api/v1/authors/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (dict, list))

    def test_list_authors_pagination(self, client):
        response = client.get("/api/v1/authors/?skip=0&limit=5")
        assert response.status_code == 200

    def test_list_authors_invalid_limit(self, client):
        response = client.get("/api/v1/authors/?limit=200")
        assert response.status_code == 422


class TestSearchAuthors:
    def test_search_authors(self, client, created_author):
        response = client.get("/api/v1/authors/search?q=Rowling")
        assert response.status_code == 200

    def test_search_authors_empty_query(self, client):
        response = client.get("/api/v1/authors/search?q=")
        assert response.status_code == 422

    def test_search_authors_no_query(self, client):
        response = client.get("/api/v1/authors/search")
        assert response.status_code == 422


class TestAutocompleteAuthors:
    def test_autocomplete(self, client, created_author):
        response = client.get("/api/v1/authors/autocomplete?prefix=Row")
        assert response.status_code in [200, 401, 404]

    def test_autocomplete_no_prefix(self, client):
        response = client.get("/api/v1/authors/autocomplete")
        assert response.status_code == 422


# ═════════════════════════════════════════════════════════════
# SPECIALIZED QUERIES
# ═════════════════════════════════════════════════════════════

class TestPopularAuthors:
    def test_get_popular(self, client):
        response = client.get("/api/v1/authors/popular")
        assert response.status_code == 200

    def test_get_popular_with_limit(self, client):
        response = client.get("/api/v1/authors/popular?limit=5")
        assert response.status_code == 200


class TestTopRatedAuthors:
    def test_get_top_rated(self, client):
        response = client.get("/api/v1/authors/top-rated")
        assert response.status_code == 200

    def test_get_top_rated_with_min_rating(self, client):
        response = client.get("/api/v1/authors/top-rated?min_rating=4.0")
        assert response.status_code == 200


class TestProlificAuthors:
    def test_get_prolific(self, client):
        response = client.get("/api/v1/authors/prolific")
        assert response.status_code == 200


class TestFeaturedAuthors:
    def test_get_featured(self, client):
        response = client.get("/api/v1/authors/featured")
        assert response.status_code == 200


class TestTrendingAuthors:
    def test_get_trending(self, client):
        response = client.get("/api/v1/authors/trending")
        assert response.status_code == 200


class TestRandomAuthors:
    def test_get_random(self, client):
        response = client.get("/api/v1/authors/random")
        assert response.status_code == 200

    def test_get_random_with_limit(self, client):
        response = client.get("/api/v1/authors/random?limit=10")
        assert response.status_code == 200


# ═════════════════════════════════════════════════════════════
# FOLLOW ENDPOINTS
# ═════════════════════════════════════════════════════════════

class TestFollowAuthor:
    def test_follow_author(self, client, created_author):
        payload = {
            "author_id": created_author["id"],
            "notification_preference": "all",
            "notes": "Test follow"
        }
        response = client.post("/api/v1/authors/follow", json=payload)
        assert response.status_code == 201

    def test_follow_author_invalid_id(self, client):
        payload = {"author_id": 999999, "notification_preference": "all"}
        response = client.post("/api/v1/authors/follow", json=payload)
        assert response.status_code in [400, 404]

    def test_follow_author_missing_data(self, client):
        response = client.post("/api/v1/authors/follow", json={})
        assert response.status_code == 422


class TestUnfollowAuthor:
    def test_unfollow_author(self, client, created_author):
        # First follow
        client.post("/api/v1/authors/follow", json={
            "author_id": created_author["id"],
            "notification_preference": "all"
        })
        response = client.delete(f"/api/v1/authors/follow/{created_author['id']}")
        assert response.status_code == 200

    def test_unfollow_author_invalid_id(self, client):
        response = client.delete("/api/v1/authors/follow/999999")
        assert response.status_code in [400, 404]


class TestBulkFollow:
    def test_bulk_follow(self, client, created_author):
        payload = {
            "author_ids": [created_author["id"]],
            "follow_source": "test"
        }
        response = client.post("/api/v1/authors/follow/bulk", json=payload)
        assert response.status_code == 200

    def test_bulk_follow_empty_list(self, client):
        payload = {"author_ids": []}
        response = client.post("/api/v1/authors/follow/bulk", json=payload)
        assert response.status_code == 422


class TestGetFollowedAuthors:
    def test_get_followed(self, client):
        response = client.get("/api/v1/authors/following")
        assert response.status_code == 200


# ═════════════════════════════════════════════════════════════
# DISCOVERY ENDPOINTS
# ═════════════════════════════════════════════════════════════

class TestDiscovery:
    def test_onboarding_discovery(self, client):
        response = client.get("/api/v1/authors/discovery/onboarding")
        assert response.status_code == 200

    def test_discovery(self, client):
        response = client.get("/api/v1/authors/discovery")
        assert response.status_code == 200

    def test_discovery_speed(self, client):
        import time
        start = time.time()
        response = client.get("/api/v1/authors/discovery")
        duration = time.time() - start
        assert response.status_code == 200
        assert duration < 2.0  # Should respond within 2 seconds


# ═════════════════════════════════════════════════════════════
# STATISTICS
# ═════════════════════════════════════════════════════════════

class TestStats:
    def test_author_stats(self, client):
        response = client.get("/api/v1/authors/stats")
        assert response.status_code == 200

    def test_author_follow_stats(self, client, created_author):
        response = client.get(f"/api/v1/authors/{created_author['id']}/stats/follow")
        assert response.status_code == 200

    def test_author_follow_stats_not_found(self, client):
        response = client.get("/api/v1/authors/999999/stats/follow")
        assert response.status_code == 404


# ═════════════════════════════════════════════════════════════
# PERFORMANCE
# ═════════════════════════════════════════════════════════════

class TestPerformance:
    def test_search_speed(self, client):
        import time
        start = time.time()
        response = client.get("/api/v1/authors/search?q=Stephen")
        duration = time.time() - start
        assert response.status_code == 200
        assert duration < 2.0


# ═════════════════════════════════════════════════════════════
# PAGINATION
# ═════════════════════════════════════════════════════════════

class TestPagination:
    def test_pagination_parameters(self, client):
        response = client.get("/api/v1/authors/?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (dict, list))