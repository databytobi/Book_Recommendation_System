"""
Recommendation System Metrics

Prometheus metrics for monitoring the recommendation system.
Tracks requests, recommendations, performance, and errors.

Phase: Observability
"""

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    Info,
    Enum,
    generate_latest,
    REGISTRY
)
from typing import Optional, Dict, Any
import time
from functools import wraps
from contextlib import contextmanager
from enum import Enum
from typing import Optional, Dict, Any
import logging
from datetime import datetime


# ============================================================
# COUNTERS
# ============================================================

# Total recommendations generated
recommendations_generated = Counter(
    "recommendations_generated_total",
    "Total number of recommendations generated",
    ["type", "status"]  # type: user, similar, search, trending
)

# Total recommendation requests
recommendation_requests = Counter(
    "recommendation_requests_total",
    "Total number of recommendation requests",
    ["endpoint", "method"]
)

# Total errors
recommendation_errors = Counter(
    "recommendation_errors_total",
    "Total number of recommendation errors",
    ["endpoint", "error_type"]
)

# Total cache hits/misses
cache_operations = Counter(
    "cache_operations_total",
    "Total cache operations (hits/misses)",
    ["operation", "result"]  # operation: get, set; result: hit, miss, success, failure
)

# ============================================================
# HISTOGRAMS
# ============================================================

# Recommendation generation time
recommendation_duration = Histogram(
    "recommendation_duration_seconds",
    "Time taken to generate recommendations",
    ["type"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# Request processing time
request_duration = Histogram(
    "request_duration_seconds",
    "Time taken to process API requests",
    ["endpoint", "method"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# Number of recommendations per request
recommendation_count = Histogram(
    "recommendation_count_per_request",
    "Number of recommendations returned per request",
    ["type"],
    buckets=(1, 5, 10, 20, 50, 100)
)

# ============================================================
# GAUGES
# ============================================================

# Currently active requests
active_requests = Gauge(
    "active_requests",
    "Number of currently active requests",
    ["endpoint"]
)

# Cache size
cache_size = Gauge(
    "cache_size_total",
    "Current size of recommendation cache"
)

# Model version information
model_version = Gauge(
    "model_version",
    "Current model version",
    ["model_name"]
)

# ============================================================
# SUMMARY METRICS
# ============================================================

# Recommendation score distribution
recommendation_scores = Summary(
    "recommendation_scores",
    "Distribution of recommendation scores",
    ["type"]
)

# ============================================================
# INFO METRICS
# ============================================================

# Service information
service_info = Info(
    "recommendation_service",
    "Recommendation service information"
)

# ============================================================
# ENUM METRICS
# ============================================================

# Service status
# At the top of the file, update the import

# Replace the ServiceStatus definition
class ServiceStatus(str, Enum):
    """Service status enumeration with utility methods."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    
    @classmethod
    def state(cls, status: str) -> "ServiceStatus":
        """
        Validate and return a ServiceStatus enum value.
        
        Args:
            status: Status string to validate
            
        Returns:
            ServiceStatus enum value
        """
        try:
            return cls(status.lower())
        except (ValueError, AttributeError):
            return cls.UNHEALTHY
    
    @classmethod
    def is_healthy(cls, status: str) -> bool:
        """Check if status string represents healthy state."""
        return cls.state(status) == cls.HEALTHY
    
    @classmethod
    def is_degraded(cls, status: str) -> bool:
        """Check if status string represents degraded state."""
        return cls.state(status) == cls.DEGRADED
    
    @classmethod
    def is_unhealthy(cls, status: str) -> bool:
        """Check if status string represents unhealthy state."""
        return cls.state(status) == cls.UNHEALTHY
# Then use it like:
# ServiceStatus.HEALTHY, ServiceStatus.DEGRADED, or ServiceStatus.UNHEALTHY
# Default: ServiceStatus.UNHEALTHY

# ============================================================
# METRICS UPDATE FUNCTIONS
# ============================================================

def record_recommendation(
    rec_type: str,
    count: int,
    duration: float,
    status: str = "success"
) -> None:
    """
    Record a recommendation generation.
    
    Parameters:
    -----------
    rec_type : str
        Type of recommendation (user, similar, search, trending)
    count : int
        Number of recommendations generated
    duration : float
        Time taken in seconds
    status : str
        Status of the request (success, error)
    """
    recommendations_generated.labels(type=rec_type, status=status).inc(count)
    recommendation_duration.labels(type=rec_type).observe(duration)
    recommendation_count.labels(type=rec_type).observe(count)


def record_request(
    endpoint: str,
    method: str,
    duration: float,
    status_code: int
) -> None:
    """
    Record an API request.
    
    Parameters:
    -----------
    endpoint : str
        API endpoint
    method : str
        HTTP method
    duration : float
        Time taken in seconds
    status_code : int
        HTTP status code
    """
    recommendation_requests.labels(endpoint=endpoint, method=method).inc()
    request_duration.labels(endpoint=endpoint, method=method).observe(duration)
    
    if status_code >= 400:
        error_type = f"{status_code}"
        recommendation_errors.labels(endpoint=endpoint, error_type=error_type).inc()


def record_cache_hit(hit: bool) -> None:
    """
    Record a cache operation result.
    
    Parameters:
    -----------
    hit : bool
        Whether the cache was hit
    """
    if hit:
        cache_operations.labels(operation="get", result="hit").inc()
    else:
        cache_operations.labels(operation="get", result="miss").inc()


def record_cache_set(success: bool) -> None:
    """
    Record a cache set operation.
    
    Parameters:
    -----------
    success : bool
        Whether the cache set was successful
    """
    if success:
        cache_operations.labels(operation="set", result="success").inc()
    else:
        cache_operations.labels(operation="set", result="failure").inc()


def update_service_status(status: str) -> None:
    """
    Update the service status.
    
    Parameters:
    -----------
    status : str
        Service status (healthy, degraded, unhealthy)
    """
    current_status = ServiceStatus.state(status)


def update_model_version(model_name: str, version: str) -> None:
    """
    Update the model version.
    
    Parameters:
    -----------
    model_name : str
        Name of the model
    version : str
        Version string
    """
    model_version.labels(model_name=model_name).set(float(version))


# ============================================================
# CONTEXT MANAGERS
# ============================================================

@contextmanager
def track_request(endpoint: str, method: str = "GET"):
    """
    Context manager for tracking API requests.
    
    Parameters:
    -----------
    endpoint : str
        API endpoint
    method : str
        HTTP method
    
    Usage:
    ------
    with track_request("/api/v1/user", "POST") as recorder:
        # Your code here
        recorder.status_code = 200
    """
    active_requests.labels(endpoint=endpoint).inc()
    start_time = time.time()
    
    class Recorder:
        status_code = 200
    
    recorder = Recorder()
    
    try:
        yield recorder
    finally:
        duration = time.time() - start_time
        active_requests.labels(endpoint=endpoint).dec()
        record_request(endpoint, method, duration, recorder.status_code)


@contextmanager
def track_recommendation(rec_type: str):
    """
    Context manager for tracking recommendation generation.
    
    Parameters:
    -----------
    rec_type : str
        Type of recommendation
    
    Usage:
    ------
    with track_recommendation("user") as recorder:
        recommendations = get_recommendations()
        recorder.count = len(recommendations)
        recorder.status = "success"
    """
    start_time = time.time()
    
    class Recorder:
        count = 0
        status = "success"
    
    recorder = Recorder()
    
    try:
        yield recorder
    except Exception as e:
        recorder.status = "error"
        raise
    finally:
        duration = time.time() - start_time
        record_recommendation(rec_type, recorder.count, duration, recorder.status)


# ============================================================
# DECORATORS
# ============================================================

def track_endpoint(endpoint: str, method: str = "GET"):
    """
    Decorator for tracking API endpoints.
    
    Parameters:
    -----------
    endpoint : str
        API endpoint
    method : str
        HTTP method
    
    Usage:
    ------
    @track_endpoint("/api/v1/recommendation/user", "POST")
    async def recommend_for_user(request: Request):
        return {"recommendations": []}
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with track_request(endpoint, method) as recorder:
                try:
                    response = await func(*args, **kwargs)
                    recorder.status_code = 200
                    return response
                except Exception as e:
                    recorder.status_code = 500
                    raise
        return wrapper
    return decorator


def track_recommendations(rec_type: str):
    """
    Decorator for tracking recommendation generation.
    
    Parameters:
    -----------
    rec_type : str
        Type of recommendation
    
    Usage:
    ------
    @track_recommendations("user")
    async def get_user_recommendations(user_id: int):
        return recommendations
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with track_recommendation(rec_type) as recorder:
                result = await func(*args, **kwargs)
                if hasattr(result, '__len__'):
                    recorder.count = len(result)
                return result
        return wrapper
    return decorator


# ============================================================
# METRICS ENDPOINT
# ============================================================

def get_metrics():
    """
    Get Prometheus metrics.
    
    Returns:
    --------
    bytes: Prometheus metrics in text format
    """
    return generate_latest(REGISTRY)


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("RECOMMENDATION METRICS TEST")
    print("=" * 60)
    
    # Test 1: Record recommendations
    print("\n📌 Test 1: Record Recommendations")
    record_recommendation("user", 10, 0.045)
    record_recommendation("similar", 5, 0.032)
    record_recommendation("search", 8, 0.028)
    record_recommendation("trending", 20, 0.015)
    print("✅ Recommendations recorded")
    
    # Test 2: Record requests
    print("\n📌 Test 2: Record Requests")
    record_request("/api/v1/recommendation/user", "POST", 0.045, 200)
    record_request("/api/v1/recommendation/similar", "POST", 0.032, 200)
    record_request("/api/v1/recommendation/search", "POST", 0.028, 400)
    print("✅ Requests recorded")
    
    # Test 3: Record cache operations
    print("\n📌 Test 3: Cache Operations")
    record_cache_hit(True)
    record_cache_hit(False)
    record_cache_set(True)
    print("✅ Cache operations recorded")
    
    # Test 4: Update service status
    print("\n📌 Test 4: Service Status")
    update_service_status("healthy")
    print("✅ Service status updated")
    
    # Test 5: Context manager
    print("\n📌 Test 5: Context Manager")
    with track_request("/api/v1/test", "GET") as recorder:
        recorder.status_code = 200
    print("✅ Request tracked with context manager")
    
    # Test 6: Print metrics
    print("\n📌 Test 6: Generated Metrics")
    metrics = get_metrics()
    print(f"✅ Metrics generated: {len(metrics)} bytes")
    
    print("\n✅ All tests completed!")