"""
Analytics API Endpoints
Provides REST API for performance monitoring and analytics
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..services.analytics_service import (
    analytics_service,
    TimeRange,
    PerformanceMetrics,
    APIMetrics,
    UserActivityMetrics,
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# Response Models
class SystemMetricsResponse(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_used_gb: float
    disk_free_gb: float
    network_sent_mb: float
    network_recv_mb: float
    timestamp: str


class UptimeResponse(BaseModel):
    uptime_seconds: float
    uptime_minutes: float
    uptime_hours: float
    uptime_days: float
    start_time: str


class APIMetricsResponse(BaseModel):
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


class UserMetricsResponse(BaseModel):
    user_id: str
    total_sessions: int
    total_requests: int
    avg_session_duration_minutes: float
    last_active: str
    most_used_features: List[dict]
    error_count: int


# Endpoints


@router.get("/system/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics():
    """
    Get current system performance metrics

    Returns real-time CPU, memory, disk, and network usage
    """
    metrics = analytics_service.get_system_metrics()
    return SystemMetricsResponse(**metrics.to_dict())


@router.get("/system/uptime", response_model=UptimeResponse)
async def get_system_uptime():
    """
    Get system uptime information

    Returns how long the system has been running
    """
    uptime = analytics_service.get_system_uptime()
    return UptimeResponse(**uptime)


@router.get("/system/health")
async def get_system_health():
    """
    Get overall system health status

    Returns health indicators based on resource usage
    """
    metrics = analytics_service.get_system_metrics()

    # Determine health status
    health_score = 100.0
    issues = []

    if metrics.cpu_percent > 80:
        health_score -= 20
        issues.append("High CPU usage")

    if metrics.memory_percent > 80:
        health_score -= 20
        issues.append("High memory usage")

    if metrics.disk_usage_percent > 90:
        health_score -= 30
        issues.append("Low disk space")

    status = "healthy"
    if health_score < 50:
        status = "critical"
    elif health_score < 70:
        status = "warning"

    return {
        "status": status,
        "health_score": health_score,
        "issues": issues,
        "metrics": metrics.to_dict(),
    }


@router.post("/api/record")
async def record_api_request(
    endpoint: str, method: str, response_time_ms: float, status_code: int
):
    """
    Record an API request for analytics

    Should be called by middleware for each API request
    """
    analytics_service.record_api_request(
        endpoint=endpoint,
        method=method,
        response_time_ms=response_time_ms,
        status_code=status_code,
    )

    return {"success": True, "recorded": True}


@router.get("/api/metrics", response_model=APIMetricsResponse)
async def get_api_metrics(
    endpoint: str = Query(..., description="API endpoint path"),
    method: str = Query(..., description="HTTP method"),
    time_range: TimeRange = Query(
        TimeRange.LAST_HOUR, description="Time range for metrics"
    ),
):
    """
    Get metrics for specific API endpoint

    Returns request counts, response times, error rates, etc.
    """
    metrics = analytics_service.get_api_metrics(endpoint, method, time_range)
    return APIMetricsResponse(**metrics.to_dict())


@router.get("/api/endpoints")
async def get_all_endpoints():
    """
    Get list of all monitored API endpoints

    Returns all endpoints that have been accessed
    """
    endpoints = analytics_service.get_all_api_endpoints()

    return {"success": True, "total_endpoints": len(endpoints), "endpoints": endpoints}


@router.get("/api/top-endpoints")
async def get_top_endpoints(
    limit: int = Query(10, ge=1, le=50),
    time_range: TimeRange = Query(TimeRange.LAST_HOUR),
):
    """
    Get top API endpoints by request count

    Returns most frequently accessed endpoints
    """
    endpoints = analytics_service.get_all_api_endpoints()

    endpoint_metrics = []
    for endpoint in endpoints:
        method, path = endpoint.split(":", 1)
        metrics = analytics_service.get_api_metrics(path, method, time_range)
        endpoint_metrics.append(metrics.to_dict())

    # Sort by total requests
    top_endpoints = sorted(
        endpoint_metrics, key=lambda x: x["total_requests"], reverse=True
    )[:limit]

    return {"success": True, "time_range": time_range.value, "endpoints": top_endpoints}


@router.get("/api/slowest-endpoints")
async def get_slowest_endpoints(
    limit: int = Query(10, ge=1, le=50),
    time_range: TimeRange = Query(TimeRange.LAST_HOUR),
):
    """
    Get slowest API endpoints by response time

    Returns endpoints with highest average response times
    """
    endpoints = analytics_service.get_all_api_endpoints()

    endpoint_metrics = []
    for endpoint in endpoints:
        method, path = endpoint.split(":", 1)
        metrics = analytics_service.get_api_metrics(path, method, time_range)
        if metrics.total_requests > 0:
            endpoint_metrics.append(metrics.to_dict())

    # Sort by average response time
    slowest_endpoints = sorted(
        endpoint_metrics, key=lambda x: x["avg_response_time_ms"], reverse=True
    )[:limit]

    return {
        "success": True,
        "time_range": time_range.value,
        "endpoints": slowest_endpoints,
    }


@router.get("/api/error-endpoints")
async def get_error_endpoints(
    limit: int = Query(10, ge=1, le=50),
    time_range: TimeRange = Query(TimeRange.LAST_HOUR),
):
    """
    Get API endpoints with highest error rates

    Returns endpoints with most failures
    """
    endpoints = analytics_service.get_all_api_endpoints()

    endpoint_metrics = []
    for endpoint in endpoints:
        method, path = endpoint.split(":", 1)
        metrics = analytics_service.get_api_metrics(path, method, time_range)
        if metrics.failed_requests > 0:
            endpoint_metrics.append(metrics.to_dict())

    # Sort by error rate
    error_endpoints = sorted(
        endpoint_metrics, key=lambda x: x["error_rate"], reverse=True
    )[:limit]

    return {
        "success": True,
        "time_range": time_range.value,
        "endpoints": error_endpoints,
    }


@router.post("/user/session/start")
async def start_user_session(user_id: str, session_id: str):
    """
    Record user session start

    Should be called when user logs in or starts a session
    """
    analytics_service.record_user_session_start(user_id, session_id)

    return {
        "success": True,
        "user_id": user_id,
        "session_id": session_id,
        "started_at": datetime.utcnow().isoformat(),
    }


@router.post("/user/session/end")
async def end_user_session(user_id: str, session_id: str):
    """
    Record user session end

    Should be called when user logs out or session expires
    """
    analytics_service.record_user_session_end(user_id, session_id)

    return {
        "success": True,
        "user_id": user_id,
        "session_id": session_id,
        "ended_at": datetime.utcnow().isoformat(),
    }


@router.post("/user/request")
async def record_user_request(user_id: str, feature: str):
    """
    Record user request/action

    Should be called for each user action to track feature usage
    """
    analytics_service.record_user_request(user_id, feature)

    return {"success": True, "recorded": True}


@router.post("/user/error")
async def record_user_error(user_id: str):
    """
    Record user error

    Should be called when user encounters an error
    """
    analytics_service.record_user_error(user_id)

    return {"success": True, "recorded": True}


@router.get("/user/metrics", response_model=UserMetricsResponse)
async def get_user_metrics(user_id: str = Query(..., description="User ID")):
    """
    Get activity metrics for specific user

    Returns session counts, request counts, feature usage, etc.
    """
    metrics = analytics_service.get_user_metrics(user_id)
    return UserMetricsResponse(**metrics.to_dict())


@router.get("/user/all")
async def get_all_users():
    """
    Get list of all users with activity

    Returns all users that have been tracked
    """
    users = analytics_service.get_all_users()

    return {"success": True, "total_users": len(users), "users": users}


@router.get("/user/active")
async def get_active_users(time_range: TimeRange = Query(TimeRange.LAST_HOUR)):
    """
    Get list of active users in time range

    Returns users who have made requests in the specified time period
    """
    users = analytics_service.get_all_users()

    # Get metrics for each user and filter by activity
    active_users = []
    for user_id in users:
        metrics = analytics_service.get_user_metrics(user_id)
        if metrics.total_requests > 0:
            active_users.append(metrics.to_dict())

    return {
        "success": True,
        "time_range": time_range.value,
        "total_active_users": len(active_users),
        "users": active_users,
    }


@router.get("/user/top-features")
async def get_top_features(limit: int = Query(10, ge=1, le=50)):
    """
    Get most used features across all users

    Returns features ranked by usage count
    """
    users = analytics_service.get_all_users()

    # Aggregate feature usage
    feature_counts = {}
    for user_id in users:
        metrics = analytics_service.get_user_metrics(user_id)
        for feature_data in metrics.most_used_features:
            feature = feature_data["feature"]
            count = feature_data["count"]
            feature_counts[feature] = feature_counts.get(feature, 0) + count

    # Sort and limit
    top_features = sorted(
        [{"feature": k, "total_usage": v} for k, v in feature_counts.items()],
        key=lambda x: x["total_usage"],
        reverse=True,
    )[:limit]

    return {"success": True, "features": top_features}


@router.get("/dashboard")
async def get_dashboard_summary():
    """
    Get comprehensive dashboard summary

    Returns overview of system, API, and user metrics
    """
    summary = analytics_service.get_dashboard_summary()
    return summary


@router.get("/reports/performance")
async def get_performance_report(time_range: TimeRange = Query(TimeRange.LAST_DAY)):
    """
    Get comprehensive performance report

    Returns detailed analysis of system and API performance
    """
    # System metrics
    system_metrics = analytics_service.get_system_metrics()
    uptime = analytics_service.get_system_uptime()

    # API metrics
    endpoints = analytics_service.get_all_api_endpoints()
    total_requests = 0
    total_errors = 0
    avg_response_times = []

    for endpoint in endpoints:
        method, path = endpoint.split(":", 1)
        metrics = analytics_service.get_api_metrics(path, method, time_range)
        total_requests += metrics.total_requests
        total_errors += metrics.failed_requests
        if metrics.total_requests > 0:
            avg_response_times.append(metrics.avg_response_time_ms)

    overall_avg_response = (
        sum(avg_response_times) / len(avg_response_times) if avg_response_times else 0.0
    )
    error_rate = total_errors / total_requests if total_requests > 0 else 0.0

    return {
        "time_range": time_range.value,
        "system": {
            "cpu_percent": system_metrics.cpu_percent,
            "memory_percent": system_metrics.memory_percent,
            "disk_usage_percent": system_metrics.disk_usage_percent,
            "uptime_hours": uptime["uptime_hours"],
        },
        "api": {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": error_rate,
            "avg_response_time_ms": overall_avg_response,
            "total_endpoints": len(endpoints),
        },
        "users": {"total_users": len(analytics_service.get_all_users())},
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/reports/user-activity")
async def get_user_activity_report(time_range: TimeRange = Query(TimeRange.LAST_DAY)):
    """
    Get user activity report

    Returns detailed analysis of user behavior and engagement
    """
    users = analytics_service.get_all_users()

    total_sessions = 0
    total_requests = 0
    total_errors = 0
    session_durations = []

    user_details = []
    for user_id in users:
        metrics = analytics_service.get_user_metrics(user_id)
        total_sessions += metrics.total_sessions
        total_requests += metrics.total_requests
        total_errors += metrics.error_count

        if metrics.avg_session_duration_minutes > 0:
            session_durations.append(metrics.avg_session_duration_minutes)

        user_details.append(metrics.to_dict())

    avg_session_duration = (
        sum(session_durations) / len(session_durations) if session_durations else 0.0
    )

    return {
        "time_range": time_range.value,
        "summary": {
            "total_users": len(users),
            "total_sessions": total_sessions,
            "total_requests": total_requests,
            "total_errors": total_errors,
            "avg_session_duration_minutes": avg_session_duration,
        },
        "users": user_details,
        "generated_at": datetime.utcnow().isoformat(),
    }
