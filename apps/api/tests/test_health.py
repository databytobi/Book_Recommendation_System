import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/v1/health/")
    
    assert response.status_code == 200
    
    data = response.json()
    
    # Check response structure (no 'data' wrapper)
    assert "status" in data
    assert "timestamp" in data
    assert "response_time_ms" in data
    assert "services" in data
    
    # Check values
    assert data["status"] in ["healthy", "degraded"]
    assert isinstance(data["response_time_ms"], (int, float))
    # Allow response_time_ms to be >= 0 (0 is acceptable for very fast responses)
    assert data["response_time_ms"] >= 0

def test_health_check_with_services(client):
    """Test health check with service status details."""
    response = client.get("/api/v1/health/")
    
    assert response.status_code == 200
    
    data = response.json()
    
    # Check service statuses
    assert "services" in data
    services = data["services"]
    assert "database" in services
    assert "redis" in services
    assert services["database"]["status"] in ["connected", "disconnected"]
    assert services["redis"]["status"] in ["connected", "disconnected"]

def test_health_check_response_time(client):
    """Test health check includes response time."""
    response = client.get("/api/v1/health/")
    
    assert response.status_code == 200
    
    data = response.json()
    
    # Check if response time is included and reasonable
    assert "response_time_ms" in data
    response_time = data["response_time_ms"]
    assert isinstance(response_time, (int, float))
    # Changed from > 0 to >= 0 to handle 0.0 values
    assert response_time >= 0
    assert response_time < 10000  # Should be less than 10 seconds

def test_health_check_timestamp(client):
    """Test health check includes timestamp."""
    response = client.get("/api/v1/health/")
    
    assert response.status_code == 200
    
    data = response.json()
    
    # Check if timestamp exists and is valid
    assert "timestamp" in data
    timestamp = data["timestamp"]
    assert isinstance(timestamp, (int, float))
    assert timestamp > 0