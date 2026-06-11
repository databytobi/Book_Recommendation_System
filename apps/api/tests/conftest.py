import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.redis import redis_client
import redis

# Mock Redis for testing
class MockRedis:
    def ping(self):
        return True
    
    def get(self, key):
        return None
    
    def set(self, key, value, ex=None):
        return True

@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """Mock Redis for all tests."""
    mock = MockRedis()
    monkeypatch.setattr(redis_client, "ping", mock.ping)
    monkeypatch.setattr(redis_client, "get", mock.get)
    monkeypatch.setattr(redis_client, "set", mock.set)
    return mock

@pytest.fixture
def client():
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client