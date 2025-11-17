"""
Performance Analytics Service
Tracks and analyzes system performance, user activity, and resource usage
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import time
import psutil
import logging
from dataclasses import dataclass, asdict
import statistics

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics tracked"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class TimeRange(str, Enum):
    """Time range for analytics queries"""

    LAST_HOUR = "1h"
    LAST_DAY = "24h"
    LAST_WEEK = "7d"
    LAST_MONTH = "30d"
    CUSTOM = "custom"


@dataclass
class MetricPoint:
    """Single metric data point"""

    timestamp: datetime
    value: float
    tags: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "tags": self.tags,
        }


@dataclass
class PerformanceMetrics:
    """System performance metrics"""

    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_used_gb: float
    disk_free_gb: float
    network_sent_mb: float
    network_recv_mb: float
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "timestamp": self.timestamp.isoformat()}


@dataclass
class APIMetrics:
    """API endpoint metrics"""

    endpoint: str
    method: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p50_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    error_rate: float
    requests_per_minute: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UserActivityMetrics:
    """User activity metrics"""

    user_id: str
    total_sessions: int
    total_requests: int
    avg_session_duration_minutes: float
    last_active: datetime
    most_used_features: List[Dict[str, Any]]
    error_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "last_active": self.last_active.isoformat()}


class MetricCollector:
    """Collects and stores metrics"""

    def __init__(self, max_points: int = 10000):
        self.max_points = max_points
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)

    def record_counter(
        self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None
    ):
        """Record counter metric (cumulative)"""
        self.counters[name] += value
        point = MetricPoint(timestamp=datetime.utcnow(), value=value, tags=tags or {})
        self.metrics[name].append(point)

    def record_gauge(
        self, name: str, value: float, tags: Optional[Dict[str, str]] = None
    ):
        """Record gauge metric (current value)"""
        self.gauges[name] = value
        point = MetricPoint(timestamp=datetime.utcnow(), value=value, tags=tags or {})
        self.metrics[name].append(point)

    def record_histogram(
        self, name: str, value: float, tags: Optional[Dict[str, str]] = None
    ):
        """Record histogram metric (distribution)"""
        point = MetricPoint(timestamp=datetime.utcnow(), value=value, tags=tags or {})
        self.metrics[name].append(point)

    def get_counter(self, name: str) -> float:
        """Get current counter value"""
        return self.counters.get(name, 0.0)

    def get_gauge(self, name: str) -> float:
        """Get current gauge value"""
        return self.gauges.get(name, 0.0)

    def get_metrics(
        self,
        name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[MetricPoint]:
        """Get metrics within time range"""
        points = self.metrics.get(name, deque())

        if not start_time and not end_time:
            return list(points)

        filtered = []
        for point in points:
            if start_time and point.timestamp < start_time:
                continue
            if end_time and point.timestamp > end_time:
                continue
            filtered.append(point)

        return filtered

    def get_statistics(
        self,
        name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, float]:
        """Get statistical summary of metrics"""
        points = self.get_metrics(name, start_time, end_time)

        if not points:
            return {
                "count": 0,
                "sum": 0.0,
                "mean": 0.0,
                "min": 0.0,
                "max": 0.0,
                "stddev": 0.0,
            }

        values = [p.value for p in points]

        return {
            "count": len(values),
            "sum": sum(values),
            "mean": statistics.mean(values),
            "min": min(values),
            "max": max(values),
            "stddev": statistics.stdev(values) if len(values) > 1 else 0.0,
            "median": statistics.median(values),
            "p50": statistics.median(values),
            "p95": self._percentile(values, 0.95),
            "p99": self._percentile(values, 0.99),
        }

    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]


class SystemMonitor:
    """Monitors system resources"""

    def __init__(self, collector: MetricCollector):
        self.collector = collector
        self.last_network_io = psutil.net_io_counters()
        self.start_time = datetime.utcnow()

    def collect_metrics(self) -> PerformanceMetrics:
        """Collect current system metrics"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)

        # Memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        memory_available_mb = memory.available / (1024 * 1024)

        # Disk
        disk = psutil.disk_usage("/")
        disk_usage_percent = disk.percent
        disk_used_gb = disk.used / (1024 * 1024 * 1024)
        disk_free_gb = disk.free / (1024 * 1024 * 1024)

        # Network
        network_io = psutil.net_io_counters()
        network_sent_mb = (network_io.bytes_sent - self.last_network_io.bytes_sent) / (
            1024 * 1024
        )
        network_recv_mb = (network_io.bytes_recv - self.last_network_io.bytes_recv) / (
            1024 * 1024
        )
        self.last_network_io = network_io

        metrics = PerformanceMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            memory_available_mb=memory_available_mb,
            disk_usage_percent=disk_usage_percent,
            disk_used_gb=disk_used_gb,
            disk_free_gb=disk_free_gb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            timestamp=datetime.utcnow(),
        )

        # Record metrics
        self.collector.record_gauge("system.cpu_percent", cpu_percent)
        self.collector.record_gauge("system.memory_percent", memory_percent)
        self.collector.record_gauge("system.disk_usage_percent", disk_usage_percent)
        self.collector.record_counter("system.network_sent_mb", network_sent_mb)
        self.collector.record_counter("system.network_recv_mb", network_recv_mb)

        return metrics

    def get_uptime(self) -> Dict[str, Any]:
        """Get system uptime"""
        uptime = datetime.utcnow() - self.start_time

        return {
            "uptime_seconds": uptime.total_seconds(),
            "uptime_minutes": uptime.total_seconds() / 60,
            "uptime_hours": uptime.total_seconds() / 3600,
            "uptime_days": uptime.total_seconds() / 86400,
            "start_time": self.start_time.isoformat(),
        }


class APIMonitor:
    """Monitors API endpoint performance"""

    def __init__(self, collector: MetricCollector):
        self.collector = collector
        self.endpoint_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"requests": [], "errors": 0, "total": 0}
        )

    def record_request(
        self, endpoint: str, method: str, response_time_ms: float, status_code: int
    ):
        """Record API request"""
        key = f"{method}:{endpoint}"

        # Record metrics
        self.collector.record_counter(f"api.requests.{key}", 1.0)
        self.collector.record_histogram(f"api.response_time.{key}", response_time_ms)

        if status_code >= 400:
            self.collector.record_counter(f"api.errors.{key}", 1.0)
            self.endpoint_stats[key]["errors"] += 1

        # Store request data
        self.endpoint_stats[key]["requests"].append(
            {
                "timestamp": datetime.utcnow(),
                "response_time_ms": response_time_ms,
                "status_code": status_code,
            }
        )
        self.endpoint_stats[key]["total"] += 1

        # Keep only last 1000 requests per endpoint
        if len(self.endpoint_stats[key]["requests"]) > 1000:
            self.endpoint_stats[key]["requests"].pop(0)

    def get_endpoint_metrics(
        self, endpoint: str, method: str, time_range: TimeRange = TimeRange.LAST_HOUR
    ) -> APIMetrics:
        """Get metrics for specific endpoint"""
        key = f"{method}:{endpoint}"
        stats = self.endpoint_stats.get(key, {"requests": [], "errors": 0, "total": 0})

        # Filter by time range
        cutoff_time = self._get_cutoff_time(time_range)
        requests = [r for r in stats["requests"] if r["timestamp"] >= cutoff_time]

        if not requests:
            return APIMetrics(
                endpoint=endpoint,
                method=method,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                avg_response_time_ms=0.0,
                min_response_time_ms=0.0,
                max_response_time_ms=0.0,
                p50_response_time_ms=0.0,
                p95_response_time_ms=0.0,
                p99_response_time_ms=0.0,
                error_rate=0.0,
                requests_per_minute=0.0,
            )

        response_times = [r["response_time_ms"] for r in requests]
        failed = sum(1 for r in requests if r["status_code"] >= 400)
        successful = len(requests) - failed

        # Calculate time span
        time_span_minutes = (datetime.utcnow() - cutoff_time).total_seconds() / 60

        return APIMetrics(
            endpoint=endpoint,
            method=method,
            total_requests=len(requests),
            successful_requests=successful,
            failed_requests=failed,
            avg_response_time_ms=statistics.mean(response_times),
            min_response_time_ms=min(response_times),
            max_response_time_ms=max(response_times),
            p50_response_time_ms=statistics.median(response_times),
            p95_response_time_ms=self._percentile(response_times, 0.95),
            p99_response_time_ms=self._percentile(response_times, 0.99),
            error_rate=failed / len(requests) if requests else 0.0,
            requests_per_minute=(
                len(requests) / time_span_minutes if time_span_minutes > 0 else 0.0
            ),
        )

    def get_all_endpoints(self) -> List[str]:
        """Get list of all monitored endpoints"""
        return list(self.endpoint_stats.keys())

    def _get_cutoff_time(self, time_range: TimeRange) -> datetime:
        """Get cutoff time for time range"""
        now = datetime.utcnow()

        if time_range == TimeRange.LAST_HOUR:
            return now - timedelta(hours=1)
        elif time_range == TimeRange.LAST_DAY:
            return now - timedelta(days=1)
        elif time_range == TimeRange.LAST_WEEK:
            return now - timedelta(days=7)
        elif time_range == TimeRange.LAST_MONTH:
            return now - timedelta(days=30)
        else:
            return now - timedelta(hours=1)

    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]


class UserActivityMonitor:
    """Monitors user activity and behavior"""

    def __init__(self, collector: MetricCollector):
        self.collector = collector
        self.user_sessions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.user_requests: Dict[str, int] = defaultdict(int)
        self.user_errors: Dict[str, int] = defaultdict(int)
        self.feature_usage: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

    def record_session_start(self, user_id: str, session_id: str):
        """Record session start"""
        self.user_sessions[user_id].append(
            {
                "session_id": session_id,
                "start_time": datetime.utcnow(),
                "end_time": None,
                "requests": 0,
            }
        )
        self.collector.record_counter(f"user.sessions.{user_id}", 1.0)

    def record_session_end(self, user_id: str, session_id: str):
        """Record session end"""
        sessions = self.user_sessions.get(user_id, [])
        for session in sessions:
            if session["session_id"] == session_id and session["end_time"] is None:
                session["end_time"] = datetime.utcnow()
                duration = (session["end_time"] - session["start_time"]).total_seconds()
                self.collector.record_histogram(
                    f"user.session_duration.{user_id}", duration
                )
                break

    def record_request(self, user_id: str, feature: str):
        """Record user request"""
        self.user_requests[user_id] += 1
        self.feature_usage[user_id][feature] += 1
        self.collector.record_counter(f"user.requests.{user_id}", 1.0)

    def record_error(self, user_id: str):
        """Record user error"""
        self.user_errors[user_id] += 1
        self.collector.record_counter(f"user.errors.{user_id}", 1.0)

    def get_user_metrics(self, user_id: str) -> UserActivityMetrics:
        """Get metrics for specific user"""
        sessions = self.user_sessions.get(user_id, [])

        # Calculate session durations
        durations = []
        for session in sessions:
            if session["end_time"]:
                duration = (
                    session["end_time"] - session["start_time"]
                ).total_seconds() / 60
                durations.append(duration)

        avg_duration = statistics.mean(durations) if durations else 0.0

        # Get most used features
        features = self.feature_usage.get(user_id, {})
        most_used = sorted(
            [{"feature": k, "count": v} for k, v in features.items()],
            key=lambda x: x["count"],
            reverse=True,
        )[:5]

        # Get last active time
        last_active = datetime.utcnow()
        if sessions:
            last_session = max(sessions, key=lambda s: s["start_time"])
            last_active = last_session["end_time"] or last_session["start_time"]

        return UserActivityMetrics(
            user_id=user_id,
            total_sessions=len(sessions),
            total_requests=self.user_requests.get(user_id, 0),
            avg_session_duration_minutes=avg_duration,
            last_active=last_active,
            most_used_features=most_used,
            error_count=self.user_errors.get(user_id, 0),
        )

    def get_all_users(self) -> List[str]:
        """Get list of all users"""
        return list(
            set(
                list(self.user_sessions.keys())
                + list(self.user_requests.keys())
                + list(self.user_errors.keys())
            )
        )


class AnalyticsService:
    """Main analytics service"""

    def __init__(self):
        self.collector = MetricCollector()
        self.system_monitor = SystemMonitor(self.collector)
        self.api_monitor = APIMonitor(self.collector)
        self.user_monitor = UserActivityMonitor(self.collector)

    def get_system_metrics(self) -> PerformanceMetrics:
        """Get current system metrics"""
        return self.system_monitor.collect_metrics()

    def get_system_uptime(self) -> Dict[str, Any]:
        """Get system uptime"""
        return self.system_monitor.get_uptime()

    def record_api_request(
        self, endpoint: str, method: str, response_time_ms: float, status_code: int
    ):
        """Record API request"""
        self.api_monitor.record_request(endpoint, method, response_time_ms, status_code)

    def get_api_metrics(
        self, endpoint: str, method: str, time_range: TimeRange = TimeRange.LAST_HOUR
    ) -> APIMetrics:
        """Get API endpoint metrics"""
        return self.api_monitor.get_endpoint_metrics(endpoint, method, time_range)

    def get_all_api_endpoints(self) -> List[str]:
        """Get all monitored API endpoints"""
        return self.api_monitor.get_all_endpoints()

    def record_user_session_start(self, user_id: str, session_id: str):
        """Record user session start"""
        self.user_monitor.record_session_start(user_id, session_id)

    def record_user_session_end(self, user_id: str, session_id: str):
        """Record user session end"""
        self.user_monitor.record_session_end(user_id, session_id)

    def record_user_request(self, user_id: str, feature: str):
        """Record user request"""
        self.user_monitor.record_request(user_id, feature)

    def record_user_error(self, user_id: str):
        """Record user error"""
        self.user_monitor.record_error(user_id)

    def get_user_metrics(self, user_id: str) -> UserActivityMetrics:
        """Get user activity metrics"""
        return self.user_monitor.get_user_metrics(user_id)

    def get_all_users(self) -> List[str]:
        """Get all users"""
        return self.user_monitor.get_all_users()

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary"""
        system_metrics = self.get_system_metrics()
        uptime = self.get_system_uptime()

        # Get top endpoints
        endpoints = self.get_all_api_endpoints()
        top_endpoints = []
        for endpoint in endpoints[:10]:
            method, path = endpoint.split(":", 1)
            metrics = self.get_api_metrics(path, method)
            top_endpoints.append(metrics.to_dict())

        # Get active users
        users = self.get_all_users()
        active_users = len(
            [u for u in users if self.user_monitor.user_requests.get(u, 0) > 0]
        )

        return {
            "system": system_metrics.to_dict(),
            "uptime": uptime,
            "api": {"total_endpoints": len(endpoints), "top_endpoints": top_endpoints},
            "users": {"total_users": len(users), "active_users": active_users},
            "timestamp": datetime.utcnow().isoformat(),
        }


# Global service instance
analytics_service = AnalyticsService()
