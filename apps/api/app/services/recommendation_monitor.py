"""
Recommendation System Monitor

Real-time monitoring of recommendation system performance.
Tracks scores, latency, request rates, and cache performance.

Phase: Observability
"""

import time
import threading
import logging
from typing import Optional, Dict, Any, List, Deque
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
import statistics
from enum import Enum

# Set up logging
logger = logging.getLogger(__name__)


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


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class RecommendationRecord:
    """Individual recommendation record."""
    timestamp: float
    rec_type: str
    count: int
    score: float
    latency_ms: float
    cache_hit: bool = False
    user_id: Optional[str] = None
    isbn: Optional[str] = None
    query: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": datetime.fromtimestamp(self.timestamp).isoformat(),
            "type": self.rec_type,
            "count": self.count,
            "score": self.score,
            "latency_ms": round(self.latency_ms, 2),
            "cache_hit": self.cache_hit,
            "user_id": self.user_id,
            "isbn": self.isbn,
            "query": self.query
        }


# ============================================================
# MONITORING SERVICE
# ============================================================

class RecommendationMonitor:
    """
    Real-time monitor for recommendation system.
    
    Features:
    - Average score tracking
    - Average latency monitoring
    - Requests per minute calculation
    - Cache hit rate tracking
    - Performance alerts
    - Historical data storage
    """
    
    def __init__(self, window_size: int = 1000, history_size: int = 10000):
        """
        Initialize the monitor.
        
        Parameters:
        -----------
        window_size : int
            Size of the sliding window for recent records
        history_size : int
            Maximum size of historical records
        """
        self.window_size = window_size
        self.history_size = history_size
        
        # Sliding windows for recent data
        self._recent_records: Deque[RecommendationRecord] = deque(maxlen=window_size)
        self._scores: Deque[float] = deque(maxlen=window_size)
        self._latencies: Deque[float] = deque(maxlen=window_size)
        self._cache_hits: Deque[bool] = deque(maxlen=window_size)
        self._requests: Deque[float] = deque(maxlen=3600)  # 1 hour of timestamps
        
        # Historical data
        self._history: Deque[RecommendationRecord] = deque(maxlen=history_size)
        
        # Per-type statistics
        self._type_stats: Dict[str, Dict[str, Any]] = {}
        
        # Aggregated metrics
        self._total_requests = 0
        self._total_cache_hits = 0
        self._start_time = time.time()
        self._last_minute_time = time.time()
        self._requests_this_minute = 0
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        # Alert thresholds
        self._alert_thresholds = {
            "max_latency_ms": 5000,
            "min_cache_hit_rate": 0.10,
            "max_error_rate": 0.05,
            "min_avg_score": 0.0
        }
        
        # Alerts
        self._alerts: Deque[Dict[str, Any]] = deque(maxlen=100)
        
        logger.info("✅ RecommendationMonitor initialized")
    
    # ============================================================
    # RECORDING METHODS
    # ============================================================
    
    def record_recommendation(
        self,
        rec_type: str,
        count: int,
        score: float,
        latency_ms: float,
        cache_hit: bool = False,
        user_id: Optional[str] = None,
        isbn: Optional[str] = None,
        query: Optional[str] = None
    ) -> None:
        """
        Record a recommendation event.
        
        Parameters:
        -----------
        rec_type : str
            Type of recommendation
        count : int
            Number of recommendations
        score : float
            Average score of recommendations
        latency_ms : float
            Response latency in milliseconds
        cache_hit : bool
            Whether the response came from cache
        user_id : Optional[str]
            User ID if applicable
        isbn : Optional[str]
            ISBN if applicable
        query : Optional[str]
            Search query if applicable
        """
        with self._lock:
            timestamp = time.time()
            
            record = RecommendationRecord(
                timestamp=timestamp,
                rec_type=rec_type,
                count=count,
                score=score,
                latency_ms=latency_ms,
                cache_hit=cache_hit,
                user_id=user_id,
                isbn=isbn,
                query=query
            )
            
            # Add to recent records
            self._recent_records.append(record)
            self._history.append(record)
            
            # Update sliding windows
            self._scores.append(score)
            self._latencies.append(latency_ms)
            self._cache_hits.append(cache_hit)
            self._requests.append(timestamp)
            
            # Update counters
            self._total_requests += 1
            if cache_hit:
                self._total_cache_hits += 1
            self._requests_this_minute += 1
            
            # Update type-specific stats
            self._update_type_stats(record)
            
            # Check for alerts
            self._check_alerts(record)
    
    def _update_type_stats(self, record: RecommendationRecord) -> None:
        """
        Update statistics for a specific recommendation type.
        
        Parameters:
        -----------
        record : RecommendationRecord
            The recommendation record
        """
        if record.rec_type not in self._type_stats:
            self._type_stats[record.rec_type] = {
                "count": 0,
                "total_score": 0.0,
                "total_latency": 0.0,
                "cache_hits": 0,
                "max_latency": 0.0,
                "min_latency": float('inf'),
                "max_score": 0.0,
                "min_score": float('inf')
            }
        
        stats = self._type_stats[record.rec_type]
        stats["count"] += 1
        stats["total_score"] += record.score
        stats["total_latency"] += record.latency_ms
        if record.cache_hit:
            stats["cache_hits"] += 1
        stats["max_latency"] = max(stats["max_latency"], record.latency_ms)
        stats["min_latency"] = min(stats["min_latency"], record.latency_ms)
        stats["max_score"] = max(stats["max_score"], record.score)
        stats["min_score"] = min(stats["min_score"], record.score)
    
    # ============================================================
    # METRICS CALCULATION
    # ============================================================
    
    def get_average_score(self, rec_type: Optional[str] = None) -> float:
        """
        Get average recommendation score.
        
        Parameters:
        -----------
        rec_type : Optional[str]
            Filter by recommendation type
        
        Returns:
        --------
        float: Average score
        """
        with self._lock:
            if rec_type and rec_type in self._type_stats:
                stats = self._type_stats[rec_type]
                return stats["total_score"] / stats["count"] if stats["count"] > 0 else 0.0
            
            return statistics.mean(self._scores) if self._scores else 0.0
    
    def get_average_latency(self, rec_type: Optional[str] = None) -> float:
        """
        Get average latency in milliseconds.
        
        Parameters:
        -----------
        rec_type : Optional[str]
            Filter by recommendation type
        
        Returns:
        --------
        float: Average latency in milliseconds
        """
        with self._lock:
            if rec_type and rec_type in self._type_stats:
                stats = self._type_stats[rec_type]
                return stats["total_latency"] / stats["count"] if stats["count"] > 0 else 0.0
            
            return statistics.mean(self._latencies) if self._latencies else 0.0
    
    def get_requests_per_minute(self) -> float:
        """
        Get current requests per minute rate.
        
        Returns:
        --------
        float: Requests per minute
        """
        with self._lock:
            if not self._requests:
                return 0.0
            
            now = time.time()
            one_minute_ago = now - 60
            
            # Count requests in the last minute
            recent_requests = [t for t in self._requests if t >= one_minute_ago]
            return len(recent_requests) / 1.0  # Per minute
    
    def get_cache_hit_rate(self) -> float:
        """
        Get cache hit rate as a percentage.
        
        Returns:
        --------
        float: Cache hit rate (0.0 to 1.0)
        """
        with self._lock:
            if self._total_requests == 0:
                return 0.0
            
            return self._total_cache_hits / self._total_requests
    
    def get_type_cache_hit_rate(self, rec_type: str) -> float:
        """
        Get cache hit rate for a specific recommendation type.
        
        Parameters:
        -----------
        rec_type : str
            Recommendation type
        
        Returns:
        --------
        float: Cache hit rate (0.0 to 1.0)
        """
        with self._lock:
            if rec_type not in self._type_stats:
                return 0.0
            
            stats = self._type_stats[rec_type]
            return stats["cache_hits"] / stats["count"] if stats["count"] > 0 else 0.0
    
    def get_type_stats(self, rec_type: str) -> Dict[str, Any]:
        """
        Get statistics for a specific recommendation type.
        
        Parameters:
        -----------
        rec_type : str
            Recommendation type
        
        Returns:
        --------
        Dict[str, Any]: Type statistics
        """
        with self._lock:
            if rec_type not in self._type_stats:
                return {}
            
            stats = self._type_stats[rec_type]
            return {
                "total_requests": stats["count"],
                "avg_score": stats["total_score"] / stats["count"] if stats["count"] > 0 else 0.0,
                "avg_latency_ms": stats["total_latency"] / stats["count"] if stats["count"] > 0 else 0.0,
                "cache_hit_rate": stats["cache_hits"] / stats["count"] if stats["count"] > 0 else 0.0,
                "max_latency_ms": stats["max_latency"] if stats["count"] > 0 else 0.0,
                "min_latency_ms": stats["min_latency"] if stats["count"] > 0 else 0.0,
                "max_score": stats["max_score"] if stats["count"] > 0 else 0.0,
                "min_score": stats["min_score"] if stats["count"] > 0 else 0.0
            }
    
    def get_all_type_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all recommendation types.
        
        Returns:
        --------
        Dict[str, Dict[str, Any]]: Statistics by type
        """
        with self._lock:
            return {
                rec_type: self.get_type_stats(rec_type)
                for rec_type in self._type_stats.keys()
            }
    
    def get_percentiles(self, percentile: float = 95.0) -> Dict[str, float]:
        """
        Get percentile values for latencies and scores.
        
        Parameters:
        -----------
        percentile : float
            Percentile to calculate (e.g., 95.0 for 95th percentile)
        
        Returns:
        --------
        Dict[str, float]: Percentile values
        """
        with self._lock:
            result = {}
            
            if self._latencies:
                sorted_latencies = sorted(self._latencies)
                index = int(len(sorted_latencies) * (percentile / 100))
                result[f"latency_{percentile}th_percentile_ms"] = sorted_latencies[min(index, len(sorted_latencies) - 1)]
            
            if self._scores:
                sorted_scores = sorted(self._scores)
                index = int(len(sorted_scores) * (percentile / 100))
                result[f"score_{percentile}th_percentile"] = sorted_scores[min(index, len(sorted_scores) - 1)]
            
            return result
    
    # ============================================================
    # AGGREGATED METRICS
    # ============================================================
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all current metrics.
        
        Returns:
        --------
        Dict[str, Any]: Current metrics
        """
        with self._lock:
            return {
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": time.time() - self._start_time,
                "total_requests": self._total_requests,
                "total_cache_hits": self._total_cache_hits,
                "avg_score": self.get_average_score(),
                "avg_latency_ms": self.get_average_latency(),
                "requests_per_minute": self.get_requests_per_minute(),
                "cache_hit_rate": self.get_cache_hit_rate(),
                "requests_per_type": {
                    rec_type: stats["count"]
                    for rec_type, stats in self._type_stats.items()
                },
                "type_stats": self.get_all_type_stats(),
                "percentiles": self.get_percentiles(95.0),
                "alerts": list(self._alerts) if self._alerts else [],
                "recent_samples": len(self._recent_records)
            }
    
    def get_summary(self) -> str:
        """
        Get a human-readable summary of current metrics.
        
        Returns:
        --------
        str: Summary string
        """
        metrics = self.get_metrics()
        
        lines = [
            "=" * 60,
            "📊 RECOMMENDATION SYSTEM STATUS",
            "=" * 60,
            f"🕐 Uptime: {metrics['uptime_seconds'] / 60:.1f} minutes",
            f"📈 Total Requests: {metrics['total_requests']:,}",
            f"💾 Cache Hit Rate: {metrics['cache_hit_rate'] * 100:.1f}%",
            f"⚡ Requests/Min: {metrics['requests_per_minute']:.1f}",
            f"⭐ Average Score: {metrics['avg_score']:.4f}",
            f"⏱️ Average Latency: {metrics['avg_latency_ms']:.1f}ms",
            "-" * 60,
            "📚 Per Type:",
        ]
        
        for rec_type, stats in metrics.get('type_stats', {}).items():
            lines.append(
                f"  {rec_type}: {stats.get('total_requests', 0)} requests, "
                f"avg score: {stats.get('avg_score', 0):.3f}, "
                f"cache hit: {stats.get('cache_hit_rate', 0) * 100:.1f}%"
            )
        
        if metrics.get('alerts'):
            lines.extend([
                "-" * 60,
                "⚠️ Recent Alerts:",
            ])
            for alert in list(metrics['alerts'])[-5:]:
                lines.append(f"  {alert['timestamp']}: {alert['message']}")
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    # ============================================================
    # ALERT MANAGEMENT
    # ============================================================
    
    def _check_alerts(self, record: RecommendationRecord) -> None:
        """
        Check for alerts based on the record.
        
        Parameters:
        -----------
        record : RecommendationRecord
            The recommendation record
        """
        alerts = []
        
        # Check latency
        if record.latency_ms > self._alert_thresholds["max_latency_ms"]:
            alerts.append({
                "type": "high_latency",
                "message": f"High latency: {record.latency_ms:.1f}ms exceeds {self._alert_thresholds['max_latency_ms']}ms",
                "severity": "warning"
            })
        
        # Check score
        if record.score < self._alert_thresholds["min_avg_score"]:
            alerts.append({
                "type": "low_score",
                "message": f"Low score: {record.score:.3f} below threshold {self._alert_thresholds['min_avg_score']}",
                "severity": "warning"
            })
        
        # Check cache hit rate (periodically)
        if self._total_requests % 100 == 0 and self._total_requests > 0:
            cache_hit_rate = self.get_cache_hit_rate()
            if cache_hit_rate < self._alert_thresholds["min_cache_hit_rate"]:
                alerts.append({
                    "type": "low_cache_hit_rate",
                    "message": f"Low cache hit rate: {cache_hit_rate * 100:.1f}% below {self._alert_thresholds['min_cache_hit_rate'] * 100:.1f}%",
                    "severity": "warning"
                })
        
        for alert in alerts:
            alert["timestamp"] = datetime.fromtimestamp(record.timestamp).isoformat()
            self._alerts.append(alert)
            logger.warning(f"ALERT: {alert['message']}")
    
    def set_alert_threshold(
        self,
        max_latency_ms: Optional[float] = None,
        min_cache_hit_rate: Optional[float] = None,
        max_error_rate: Optional[float] = None,
        min_avg_score: Optional[float] = None
    ) -> None:
        """
        Set alert thresholds.
        
        Parameters:
        -----------
        max_latency_ms : Optional[float]
            Maximum allowed latency in milliseconds
        min_cache_hit_rate : Optional[float]
            Minimum acceptable cache hit rate
        max_error_rate : Optional[float]
            Maximum acceptable error rate
        min_avg_score : Optional[float]
            Minimum acceptable average score
        """
        with self._lock:
            if max_latency_ms is not None:
                self._alert_thresholds["max_latency_ms"] = max_latency_ms
            if min_cache_hit_rate is not None:
                self._alert_thresholds["min_cache_hit_rate"] = min_cache_hit_rate
            if max_error_rate is not None:
                self._alert_thresholds["max_error_rate"] = max_error_rate
            if min_avg_score is not None:
                self._alert_thresholds["min_avg_score"] = min_avg_score
            
            logger.info(f"Alert thresholds updated: {self._alert_thresholds}")
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """
        Get recent alerts.
        
        Returns:
        --------
        List[Dict[str, Any]]: Recent alerts
        """
        with self._lock:
            return list(self._alerts)
    
    def clear_alerts(self) -> None:
        """Clear all alerts."""
        with self._lock:
            self._alerts.clear()
            logger.info("Alerts cleared")
    
    # ============================================================
    # RESET METHODS
    # ============================================================
    
    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._recent_records.clear()
            self._scores.clear()
            self._latencies.clear()
            self._cache_hits.clear()
            self._requests.clear()
            self._history.clear()
            self._type_stats.clear()
            self._total_requests = 0
            self._total_cache_hits = 0
            self._start_time = time.time()
            self._last_minute_time = time.time()
            self._requests_this_minute = 0
            self._alerts.clear()
            logger.info("Metrics reset")


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_monitor: Optional[RecommendationMonitor] = None


def get_monitor() -> RecommendationMonitor:
    """
    Get or create the singleton monitor instance.
    
    Returns:
    --------
    RecommendationMonitor: The singleton instance
    """
    global _monitor
    if _monitor is None:
        _monitor = RecommendationMonitor()
    return _monitor


# ============================================================
# FASTAPI DEPENDENCY
# ============================================================

async def get_monitor_dependency() -> RecommendationMonitor:
    """
    FastAPI dependency for getting the monitor.
    
    Usage:
    ```python
    @app.get("/metrics")
    async def get_metrics(monitor: RecommendationMonitor = Depends(get_monitor_dependency)):
        return monitor.get_metrics()
        """