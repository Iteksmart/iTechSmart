"""
iTechSmart Analytics - Agent Integration API
Provides agent monitoring and management endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import httpx
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# License Server configuration
LICENSE_SERVER_URL = os.getenv("LICENSE_SERVER_URL", "http://localhost:3000")


async def get_license_server_client():
    """Get HTTP client for License Server"""
    return httpx.AsyncClient(
        base_url=LICENSE_SERVER_URL,
        timeout=30.0,
        headers={"Content-Type": "application/json"},
    )


@router.get("/agents")
async def get_agents(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    Get all registered agents

    Returns list of agents with their current status and metrics
    """
    try:
        async with await get_license_server_client() as client:
            params = {"limit": limit, "offset": offset}
            if status:
                params["status"] = status

            response = await client.get("/api/agents", params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch agents: {e}")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """
    Get detailed information about a specific agent

    Returns agent details including latest metrics and alerts
    """
    try:
        async with await get_license_server_client() as client:
            response = await client.get(f"/api/agents/{agent_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Agent not found")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch agent {agent_id}: {e}")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )


@router.get("/agents/{agent_id}/metrics")
async def get_agent_metrics(
    agent_id: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of metrics to retrieve"),
):
    """
    Get metrics for a specific agent

    Returns time-series metrics data for analytics and visualization
    """
    try:
        async with await get_license_server_client() as client:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            params = {
                "startTime": start_time.isoformat(),
                "endTime": datetime.utcnow().isoformat(),
            }

            response = await client.get(
                f"/api/agents/{agent_id}/metrics", params=params
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Agent not found")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch metrics for agent {agent_id}: {e}")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )


@router.get("/agents/{agent_id}/alerts")
async def get_agent_alerts(
    agent_id: str,
    severity: Optional[str] = Query(None, description="Filter by severity"),
    resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
):
    """
    Get alerts for a specific agent

    Returns list of alerts with filtering options
    """
    try:
        async with await get_license_server_client() as client:
            params = {}
            if severity:
                params["severity"] = severity
            if resolved is not None:
                params["resolved"] = str(resolved).lower()

            response = await client.get(f"/api/agents/{agent_id}/alerts", params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Agent not found")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch alerts for agent {agent_id}: {e}")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )


@router.get("/agents/stats/summary")
async def get_agents_summary():
    """
    Get summary statistics for all agents

    Returns aggregated metrics and status counts
    """
    try:
        async with await get_license_server_client() as client:
            # Get all agents
            response = await client.get("/api/agents")
            response.raise_for_status()
            data = response.json()
            agents = data.get("agents", [])

            # Calculate summary statistics
            total = len(agents)
            active = sum(1 for a in agents if a.get("status") == "ACTIVE")
            offline = sum(1 for a in agents if a.get("status") == "OFFLINE")
            error = sum(1 for a in agents if a.get("status") == "ERROR")

            # Calculate average metrics
            avg_cpu = 0
            avg_memory = 0
            avg_disk = 0

            if agents:
                for agent in agents:
                    metrics = agent.get("lastMetrics", {})
                    avg_cpu += metrics.get("cpuUsage", 0)
                    avg_memory += metrics.get("memoryUsage", 0)
                    avg_disk += metrics.get("diskUsage", 0)

                avg_cpu /= total
                avg_memory /= total
                avg_disk /= total

            return {
                "total": total,
                "active": active,
                "offline": offline,
                "error": error,
                "averageMetrics": {
                    "cpu": round(avg_cpu, 2),
                    "memory": round(avg_memory, 2),
                    "disk": round(avg_disk, 2),
                },
                "timestamp": datetime.utcnow().isoformat(),
            }
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch agents summary: {e}")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )


@router.get("/agents/analytics/trends")
async def get_agent_trends(
    hours: int = Query(24, ge=1, le=168, description="Hours of data to analyze")
):
    """
    Get trend analysis for agent metrics

    Returns trend data for CPU, memory, and disk usage across all agents
    """
    try:
        async with await get_license_server_client() as client:
            # Get all agents
            response = await client.get("/api/agents")
            response.raise_for_status()
            data = response.json()
            agents = data.get("agents", [])

            # Collect metrics for each agent
            all_metrics = []
            for agent in agents:
                agent_id = agent.get("id")
                if agent_id:
                    start_time = datetime.utcnow() - timedelta(hours=hours)
                    params = {
                        "startTime": start_time.isoformat(),
                        "endTime": datetime.utcnow().isoformat(),
                    }

                    metrics_response = await client.get(
                        f"/api/agents/{agent_id}/metrics", params=params
                    )
                    if metrics_response.status_code == 200:
                        metrics_data = metrics_response.json()
                        all_metrics.extend(metrics_data.get("metrics", []))

            # Analyze trends
            if not all_metrics:
                return {
                    "trends": {
                        "cpu": {"direction": "stable", "change": 0},
                        "memory": {"direction": "stable", "change": 0},
                        "disk": {"direction": "stable", "change": 0},
                    },
                    "dataPoints": 0,
                }

            # Sort by timestamp
            all_metrics.sort(key=lambda x: x.get("timestamp", ""))

            # Calculate trends (simple comparison of first half vs second half)
            mid_point = len(all_metrics) // 2
            first_half = all_metrics[:mid_point]
            second_half = all_metrics[mid_point:]

            def calculate_trend(metrics, field):
                if not metrics:
                    return {"direction": "stable", "change": 0}

                first_avg = sum(m.get(field, 0) for m in first_half) / len(first_half)
                second_avg = sum(m.get(field, 0) for m in second_half) / len(
                    second_half
                )
                change = second_avg - first_avg

                if abs(change) < 5:
                    direction = "stable"
                elif change > 0:
                    direction = "increasing"
                else:
                    direction = "decreasing"

                return {"direction": direction, "change": round(change, 2)}

            return {
                "trends": {
                    "cpu": calculate_trend(all_metrics, "cpuUsage"),
                    "memory": calculate_trend(all_metrics, "memoryUsage"),
                    "disk": calculate_trend(all_metrics, "diskUsage"),
                },
                "dataPoints": len(all_metrics),
                "timeRange": f"{hours} hours",
            }
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch agent trends: {e}")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )


@router.get("/agents/analytics/health-score")
async def get_agents_health_score():
    """
    Calculate overall health score for all agents

    Returns a health score (0-100) based on agent status and metrics
    """
    try:
        async with await get_license_server_client() as client:
            response = await client.get("/api/agents")
            response.raise_for_status()
            data = response.json()
            agents = data.get("agents", [])

            if not agents:
                return {
                    "healthScore": 100,
                    "status": "excellent",
                    "details": "No agents to monitor",
                }

            # Calculate health score
            total_score = 0
            for agent in agents:
                agent_score = 100

                # Deduct points for status
                status = agent.get("status")
                if status == "OFFLINE":
                    agent_score -= 30
                elif status == "ERROR":
                    agent_score -= 50
                elif status == "MAINTENANCE":
                    agent_score -= 10

                # Deduct points for high resource usage
                metrics = agent.get("lastMetrics", {})
                cpu = metrics.get("cpuUsage", 0)
                memory = metrics.get("memoryUsage", 0)
                disk = metrics.get("diskUsage", 0)

                if cpu > 90:
                    agent_score -= 15
                elif cpu > 80:
                    agent_score -= 10

                if memory > 90:
                    agent_score -= 15
                elif memory > 80:
                    agent_score -= 10

                if disk > 90:
                    agent_score -= 15
                elif disk > 75:
                    agent_score -= 10

                # Deduct points for unresolved alerts
                alert_count = agent.get("alertCount", 0)
                if alert_count > 10:
                    agent_score -= 20
                elif alert_count > 5:
                    agent_score -= 10
                elif alert_count > 0:
                    agent_score -= 5

                total_score += max(0, agent_score)

            health_score = round(total_score / len(agents))

            # Determine status
            if health_score >= 90:
                status = "excellent"
            elif health_score >= 75:
                status = "good"
            elif health_score >= 60:
                status = "fair"
            elif health_score >= 40:
                status = "poor"
            else:
                status = "critical"

            return {
                "healthScore": health_score,
                "status": status,
                "totalAgents": len(agents),
                "timestamp": datetime.utcnow().isoformat(),
            }
    except httpx.HTTPError as e:
        logger.error(f"Failed to calculate health score: {e}")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )
