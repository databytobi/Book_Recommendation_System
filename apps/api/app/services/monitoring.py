"""
Monitoring and Observability Service

Provides logging, metrics, and performance monitoring for the recommendation system.
Tracks recommendations, API requests, service health, and performance metrics.

Phase: Observability
"""

import logging
import time
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict
import threading
from enum import Enum

# ============================================================
# ENUMS
# ============================================================

class RecommendationType(str, Enum):
    """Types of recommendation requests."""
    USER = "user"
    SIMILAR = "similar"
    SEARCH = "search"
    TRENDING = "trending"
    HYBRID = "hybrid"
    POPULARITY = "popularity"
    CONTENT = "content"
    COLLABORATIVE = "collaborative"


class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class RecommendationLog:
    """Data class for recommendation logs."""
    user_id: str
    recommendation_type: str
    count: int
    timestamp: float = field(default_factory=time.time)
    duration_ms: Optional[float] = None
    status: str = "success"
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "type": self.recommendation_type,
            "count": self.count,
            "timestamp": datetime.fromtimestamp(self.timestamp).isoformat(),
            "duration_ms": self.duration_ms,
            "status": self.status,
            "error": self.error,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class APILog:
    """Data class for API request logs."""
    method: str
    path: str
    status_code: int
    duration_ms: float
    timestamp: float = field(default_factory=time.time)
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "method": self.method,
            "path": self.path,
            "status_code": self.status_code,
            "duration_ms": self.duration_ms,
            "timestamp": datetime.fromtimestamp(self.timestamp).isoformat(),
            "client_ip": self.client_ip,
            "user_agent": self.user_agent,
            "error": self.error
        }


# ============================================================
# METRICS COLLECTOR
# ============================================================

class MetricsCollector:
    """
    Collects and tracks metrics for the recommendation system.
    
    Features:
    - Request counting by endpoint and status
    - Response time tracking
    - Error rate monitoring
    - Recommendation tracking
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._request_counts = defaultdict(int)
        self._response_times = defaultdict(list)
        self._error_counts = defaultdict(int)
        self._recommendation_counts = defaultdict(int)
        self._recommendation_types = defaultdict(int)
        self._start_time = time.time()
    
    def record_request(self, endpoint: str, status_code: int, duration_ms: float) -> None:
        """
        Record an API request.
        
        Parameters:
        -----------
        endpoint : str
            API endpoint path
        status_code : int
            HTTP status code
        duration_ms : float
            Request duration in milliseconds
        """
        with self._lock:
            self._request_counts[f"{endpoint}:{status_code}"] += 1
            self._response_times[endpoint].append(duration_ms)
            
            if status_code >= 400:
                self._error_counts[endpoint] += 1
    
    def record_recommendation(self, user_id: str, rec_type: str, count: int) -> None:
        """
        Record a recommendation request.
        
        Parameters:
        -----------
        user_id : str
            User ID
        rec_type : str
            Recommendation type
        count : int
            Number of recommendations
        """
        with self._lock:
            self._recommendation_counts[user_id] += count
            self._recommendation_types[rec_type] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics.
        
        Returns:
        --------
        Dict[str, Any]: Current metrics
        """
        with self._lock:
            total_requests = sum(self._request_counts.values())
            total_errors = sum(self._error_counts.values())
            
            # Calculate average response times
            avg_response_times = {}
            for endpoint, times in self._response_times.items():
                if times:
                    avg_response_times[endpoint] = sum(times) / len(times)
            
            return {
                "uptime_seconds": time.time() - self._start_time,
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0,
                "request_counts": dict(self._request_counts),
                "avg_response_times": avg_response_times,
                "recommendation_counts": dict(self._recommendation_counts),
                "recommendation_types": dict(self._recommendation_types),
                "timestamp": datetime.now().isoformat()
            }
    
    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._request_counts.clear()
            self._response_times.clear()
            self._error_counts.clear()
            self._recommendation_counts.clear()
            self._recommendation_types.clear()
            self._start_time = time.time()


# ============================================================
# MONITORING SERVICE
# ============================================================

class MonitoringService:
    """
    Central monitoring service for the recommendation system.
    
    Provides:
    - Structured logging
    - Metrics collection
    - Performance monitoring
    - Health tracking
    """
    
    def __init__(self, service_name: str = "recommendations"):
        """
        Initialize the monitoring service.
        
        Parameters:
        -----------
        service_name : str
            Name of the service for logging
        """
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self.metrics = MetricsCollector()
        self._log_buffer = []
        self._buffer_size = 1000
    
    # ============================================================
    # LOGGING METHODS
    # ============================================================
    
    def _log(self, level: LogLevel, message: str, **kwargs) -> None:
        """
        Internal logging method.
        
        Parameters:
        -----------
        level : LogLevel
            Log level
        message : str
            Log message
        **kwargs : Additional fields to include in log
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "service": self.service_name,
            "level": level.value,
            "message": message,
            **kwargs
        }
        
        log_message = json.dumps(log_data)
        
        if level == LogLevel.DEBUG:
            self.logger.debug(log_message)
        elif level == LogLevel.INFO:
            self.logger.info(log_message)
        elif level == LogLevel.WARNING:
            self.logger.warning(log_message)
        elif level == LogLevel.ERROR:
            self.logger.error(log_message)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(log_message)
        
        # Buffer for batch processing
        self._log_buffer.append(log_data)
        if len(self._log_buffer) >= self._buffer_size:
            self.flush_logs()
    
    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message."""
        self._log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log an info message."""
        self._log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message."""
        self._log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log an error message."""
        self._log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log a critical message."""
        self._log(LogLevel.CRITICAL, message, **kwargs)
    
    def flush_logs(self) -> None:
        """Flush the log buffer."""
        self._log_buffer.clear()
    
    # ============================================================
    # RECOMMENDATION LOGGING
    # ============================================================
    
    def log_recommendation(
        self,
        user_id: str,
        recommendation_type: str,
        count: int,
        duration_ms: Optional[float] = None,
        status: str = "success",
        error: Optional[str] = None,
        **metadata
    ) -> None:
        """
        Log a recommendation request.
        
        Parameters:
        -----------
        user_id : str
            User ID
        recommendation_type : str
            Type of recommendation (user, similar, search, trending)
        count : int
            Number of recommendations returned
        duration_ms : Optional[float]
            Request duration in milliseconds
        status : str
            Status of the request (success, error)
        error : Optional[str]
            Error message if any
        **metadata : Additional metadata
        """
        # Record metrics
        self.metrics.record_recommendation(user_id, recommendation_type, count)
        
        # Create log entry
        log_entry = RecommendationLog(
            user_id=user_id,
            recommendation_type=recommendation_type,
            count=count,
            duration_ms=duration_ms,
            status=status,
            error=error,
            metadata=metadata
        )
        
        # Log with appropriate level
        if status == "success":
            self.info(
                f"Recommendation: user={user_id} type={recommendation_type} count={count}",
                **log_entry.to_dict()
            )
        else:
            self.error(
                f"Recommendation failed: user={user_id} type={recommendation_type} error={error}",
                **log_entry.to_dict()
            )
    
    def log_user_recommendation(
        self,
        user_id: str,
        count: int,
        duration_ms: Optional[float] = None,
        **metadata
    ) -> None:
        """Log a user recommendation request."""
        self.log_recommendation(
            user_id=user_id,
            recommendation_type=RecommendationType.USER.value,
            count=count,
            duration_ms=duration_ms,
            **metadata
        )
    
    def log_similar_books(
        self,
        isbn: str,
        count: int,
        duration_ms: Optional[float] = None,
        **metadata
    ) -> None:
        """Log a similar books request."""
        self.log_recommendation(
            user_id=isbn,
            recommendation_type=RecommendationType.SIMILAR.value,
            count=count,
            duration_ms=duration_ms,
            **metadata
        )
    
    def log_search(
        self,
        query: str,
        count: int,
        duration_ms: Optional[float] = None,
        **metadata
    ) -> None:
        """Log a search request."""
        self.log_recommendation(
            user_id=f"search:{query[:50]}",
            recommendation_type=RecommendationType.SEARCH.value,
            count=count,
            duration_ms=duration_ms,
            **metadata
        )
    
    def log_trending(
        self,
        count: int,
        duration_ms: Optional[float] = None,
        **metadata
    ) -> None:
        """Log a trending books request."""
        self.log_recommendation(
            user_id="trending",
            recommendation_type=RecommendationType.TRENDING.value,
            count=count,
            duration_ms=duration_ms,
            **metadata
        )
    
    # ============================================================
    # API LOGGING
    # ============================================================
    
    def log_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Log an API request.
        
        Parameters:
        -----------
        method : str
            HTTP method
        path : str
            Request path
        status_code : int
            HTTP status code
        duration_ms : float
            Request duration in milliseconds
        client_ip : Optional[str]
            Client IP address
        user_agent : Optional[str]
            User agent string
        error : Optional[str]
            Error message if any
        """
        # Record metrics
        self.metrics.record_request(path, status_code, duration_ms)
        
        log_entry = APILog(
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            client_ip=client_ip,
            user_agent=user_agent,
            error=error
        )
        
        if status_code >= 400:
            self.error(f"API error: {method} {path} {status_code}", **log_entry.to_dict())
        else:
            self.debug(f"API request: {method} {path} {status_code}", **log_entry.to_dict())
    
    # ============================================================
    # HEALTH AND METRICS
    # ============================================================
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics.
        
        Returns:
        --------
        Dict[str, Any]: Current metrics
        """
        metrics = self.metrics.get_metrics()
        metrics["service"] = self.service_name
        metrics["log_buffer_size"] = len(self._log_buffer)
        return metrics
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status.
        
        Returns:
        --------
        Dict[str, Any]: Health status
        """
        metrics = self.get_metrics()
        return {
            "service": self.service_name,
            "status": "healthy",
            "uptime_seconds": metrics.get("uptime_seconds", 0),
            "total_requests": metrics.get("total_requests", 0),
            "error_rate": metrics.get("error_rate", 0),
            "timestamp": datetime.now().isoformat()
        }


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_monitoring_service: Optional[MonitoringService] = None


def get_monitoring_service() -> MonitoringService:
    """
    Get or create the singleton MonitoringService instance.
    
    Returns:
    --------
    MonitoringService: The singleton instance
    """
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def log_recommendation(
    user_id: str,
    recommendation_type: str,
    count: int,
    duration_ms: Optional[float] = None,
    status: str = "success",
    error: Optional[str] = None,
    **metadata
) -> None:
    """
    Convenience function to log a recommendation.
    
    Parameters:
    -----------
    user_id : str
        User ID
    recommendation_type : str
        Type of recommendation
    count : int
        Number of recommendations
    duration_ms : Optional[float]
        Duration in milliseconds
    status : str
        Status of the request
    error : Optional[str]
        Error message if any
    **metadata : Additional metadata
    """
    service = get_monitoring_service()
    service.log_recommendation(
        user_id=user_id,
        recommendation_type=recommendation_type,
        count=count,
        duration_ms=duration_ms,
        status=status,
        error=error,
        **metadata
    )


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    error: Optional[str] = None
) -> None:
    """
    Convenience function to log an API request.
    
    Parameters:
    -----------
    method : str
        HTTP method
    path : str
        Request path
    status_code : int
        HTTP status code
    duration_ms : float
        Duration in milliseconds
    client_ip : Optional[str]
        Client IP address
    user_agent : Optional[str]
        User agent string
    error : Optional[str]
        Error message if any
    """
    service = get_monitoring_service()
    service.log_api_request(
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        client_ip=client_ip,
        user_agent=user_agent,
        error=error
    )


def get_metrics() -> Dict[str, Any]:
    """
    Get current metrics.
    
    Returns:
    --------
    Dict[str, Any]: Current metrics
    """
    service = get_monitoring_service()
    return service.get_metrics()


# ============================================================
# FASTAPI MIDDLEWARE
# ============================================================

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time
import logging

logger = logging.getLogger(__name__)

class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware for monitoring API requests.
    Tracks request metrics, response times, and errors.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and track metrics.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            Response: The response from the next handler
        """
        start_time = time.time()
        
        # Process the request
        try:
            response = await call_next(request)
            
            # Track the request
            duration = time.time() - start_time
            self._record_metrics(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=duration
            )
            
            return response
            
        except Exception as e:
            # Track failed requests
            duration = time.time() - start_time
            self._record_metrics(
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration=duration,
                error=str(e)
            )
            raise
    
    def _record_metrics(self, method: str, path: str, status_code: int, duration: float, error: str = None):
        """
        Record metrics for the request.
        
        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration: Request duration in seconds
            error: Error message if any
        """
        # Log the metrics
        logger.debug(
            f"Metrics: {method} {path} - {status_code} - {duration:.4f}s"
            + (f" - Error: {error}" if error else "")
        )
        
        # You can add Prometheus metrics here if needed
        # Example:
        # request_counter.labels(method=method, path=path, status=status_code).inc()
        # request_duration.labels(method=method, path=path).observe(duration)