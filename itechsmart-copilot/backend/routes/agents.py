"""
iTechSmart Copilot - Agent Integration API
Provides agent monitoring with AI-powered insights
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
        headers={"Content-Type": "application/json"}
    )


@router.get("/agents")
async def get_agents(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get all registered agents"""
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
        raise HTTPException(status_code=502, detail="Failed to connect to License Server")


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get detailed information about a specific agent"""
    try:
        async with await get_license_server_client() as client:
            response = await client.get(f"/api/agents/{agent_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Agent not found")
        raise HTTPException(status_code=502, detail="Failed to connect to License Server")
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch agent {agent_id}: {e}")
        raise HTTPException(status_code=502, detail="Failed to connect to License Server")


@router.get("/agents/{agent_id}/metrics")
async def get_agent_metrics(
    agent_id: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of metrics to retrieve")
):
    """Get metrics for a specific agent"""
    try:
        async with await get_license_server_client() as client:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            params = {
                "startTime": start_time.isoformat(),
                "endTime": datetime.utcnow().isoformat()
            }
            
            response = await client.get(f"/api/agents/{agent_id}/metrics", params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Agent not found")
        raise HTTPException(status_code=502, detail="Failed to connect to License Server")
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch metrics for agent {agent_id}: {e}")
        raise HTTPException(status_code=502, detail="Failed to connect to License Server")


@router.get("/agents/{agent_id}/alerts")
async def get_agent_alerts(
    agent_id: str,
    severity: Optional[str] = Query(None, description="Filter by severity"),
    resolved: Optional[bool] = Query(None, description="Filter by resolution status")
):
    """Get alerts for a specific agent"""
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
        raise HTTPException(status_code=502, detail="Failed to connect to License Server")
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch alerts for agent {agent_id}: {e}")
        raise HTTPException(status_code=502, detail="Failed to connect to License Server")


@router.get("/agents/stats/summary")
async def get_agents_summary():
    """Get summary statistics for all agents"""
    try:
        async with await get_license_server_client() as client:
            response = await client.get("/api/agents")
            response.raise_for_status()
            data = response.json()
            agents = data.get("agents", [])
            
            total = len(agents)
            active = sum(1 for a in agents if a.get("status") == "ACTIVE")
            offline = sum(1 for a in agents if a.get("status") == "OFFLINE")
            error = sum(1 for a in agents if a.get("status") == "ERROR")
            
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
                    "disk": round(avg_disk, 2)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch agents summary: {e}")
        raise HTTPException(status_code=502, detail="Failed to connect to License Server")


@router.get("/agents/ai/insights")
async def get_ai_insights():
    """
    Get AI-powered insights about agent performance and health
    
    Uses Copilot's AI capabilities to analyze agent data and provide recommendations
    """
    try:
        async with await get_license_server_client() as client:
            # Get all agents
            response = await client.get("/api/agents")
            response.raise_for_status()
            data = response.json()
            agents = data.get("agents", [])
            
            if not agents:
                return {
                    "insights": [],
                    "recommendations": ["No agents registered. Deploy agents to start monitoring."],
                    "summary": "No data available for analysis"
                }
            
            insights = []
            recommendations = []
            
            # Analyze agent status
            offline_agents = [a for a in agents if a.get("status") == "OFFLINE"]
            error_agents = [a for a in agents if a.get("status") == "ERROR"]
            
            if offline_agents:
                insights.append({
                    "type": "warning",
                    "title": "Offline Agents Detected",
                    "description": f"{len(offline_agents)} agent(s) are currently offline",
                    "severity": "medium",
                    "agents": [a.get("hostname") for a in offline_agents[:5]]
                })
                recommendations.append("Investigate offline agents and ensure they are running properly")
            
            if error_agents:
                insights.append({
                    "type": "error",
                    "title": "Agents in Error State",
                    "description": f"{len(error_agents)} agent(s) are reporting errors",
                    "severity": "high",
                    "agents": [a.get("hostname") for a in error_agents[:5]]
                })
                recommendations.append("Review error logs and resolve agent issues immediately")
            
            # Analyze resource usage
            high_cpu_agents = [a for a in agents if a.get("lastMetrics", {}).get("cpuUsage", 0) > 80]
            high_memory_agents = [a for a in agents if a.get("lastMetrics", {}).get("memoryUsage", 0) > 80]
            high_disk_agents = [a for a in agents if a.get("lastMetrics", {}).get("diskUsage", 0) > 75]
            
            if high_cpu_agents:
                insights.append({
                    "type": "warning",
                    "title": "High CPU Usage",
                    "description": f"{len(high_cpu_agents)} agent(s) have CPU usage above 80%",
                    "severity": "medium",
                    "agents": [a.get("hostname") for a in high_cpu_agents[:5]]
                })
                recommendations.append("Monitor CPU-intensive processes and consider scaling resources")
            
            if high_memory_agents:
                insights.append({
                    "type": "warning",
                    "title": "High Memory Usage",
                    "description": f"{len(high_memory_agents)} agent(s) have memory usage above 80%",
                    "severity": "medium",
                    "agents": [a.get("hostname") for a in high_memory_agents[:5]]
                })
                recommendations.append("Review memory consumption and optimize applications")
            
            if high_disk_agents:
                insights.append({
                    "type": "warning",
                    "title": "High Disk Usage",
                    "description": f"{len(high_disk_agents)} agent(s) have disk usage above 75%",
                    "severity": "medium",
                    "agents": [a.get("hostname") for a in high_disk_agents[:5]]
                })
                recommendations.append("Clean up disk space or expand storage capacity")
            
            # Analyze alerts
            total_alerts = sum(a.get("alertCount", 0) for a in agents)
            if total_alerts > 0:
                insights.append({
                    "type": "info",
                    "title": "Active Alerts",
                    "description": f"{total_alerts} total alert(s) across all agents",
                    "severity": "low"
                })
                recommendations.append("Review and resolve active alerts to maintain system health")
            
            # Generate summary
            active_count = sum(1 for a in agents if a.get("status") == "ACTIVE")
            health_percentage = (active_count / len(agents)) * 100 if agents else 0
            
            if health_percentage >= 90:
                summary = "System health is excellent. All agents are performing well."
            elif health_percentage >= 75:
                summary = "System health is good. Minor issues detected that should be addressed."
            elif health_percentage >= 60:
                summary = "System health is fair. Several issues require attention."
            else:
                summary = "System health is poor. Immediate action required."
            
            if not insights:
                insights.append({
                    "type": "success",
                    "title": "All Systems Operational",
                    "description": "All agents are healthy and performing within normal parameters",
                    "severity": "low"
                })
                recommendations.append("Continue monitoring and maintain current practices")
            
            return {
                "insights": insights,
                "recommendations": recommendations,
                "summary": summary,
                "healthPercentage": round(health_percentage, 1),
                "timestamp": datetime.utcnow().isoformat()
            }
    except httpx.HTTPError as e:
        logger.error(f"Failed to generate AI insights: {e}")
        raise HTTPException(status_code=502, detail="Failed to connect to License Server")


@router.post("/agents/{agent_id}/ai/analyze")
async def analyze_agent_with_ai(agent_id: str):
    """
    Use AI to analyze a specific agent's performance and provide recommendations
    """
    try:
        async with await get_license_server_client() as client:
            # Get agent details
            agent_response = await client.get(f"/api/agents/{agent_id}")
            agent_response.raise_for_status()
            agent = agent_response.json()
            
            # Get recent metrics
            start_time = datetime.utcnow() - timedelta(hours=24)
            params = {
                "startTime": start_time.isoformat(),
                "endTime": datetime.utcnow().isoformat()
            }
            metrics_response = await client.get(f"/api/agents/{agent_id}/metrics", params=params)
            metrics_response.raise_for_status()
            metrics_data = metrics_response.json()
            
            # Get alerts
            alerts_response = await client.get(f"/api/agents/{agent_id}/alerts")
            alerts_response.raise_for_status()
            alerts_data = alerts_response.json()
            
            # AI Analysis
            analysis = {
                "agentId": agent_id,
                "hostname": agent.get("hostname"),
                "status": agent.get("status"),
                "analysis": [],
                "recommendations": [],
                "score": 100
            }
            
            # Analyze status
            if agent.get("status") == "OFFLINE":
                analysis["analysis"].append("Agent is currently offline")
                analysis["recommendations"].append("Check agent service and network connectivity")
                analysis["score"] -= 30
            elif agent.get("status") == "ERROR":
                analysis["analysis"].append("Agent is in error state")
                analysis["recommendations"].append("Review agent logs and resolve errors")
                analysis["score"] -= 50
            
            # Analyze metrics
            metrics = metrics_data.get("metrics", [])
            if metrics:
                avg_cpu = sum(m.get("cpuUsage", 0) for m in metrics) / len(metrics)
                avg_memory = sum(m.get("memoryUsage", 0) for m in metrics) / len(metrics)
                avg_disk = sum(m.get("diskUsage", 0) for m in metrics) / len(metrics)
                
                if avg_cpu > 80:
                    analysis["analysis"].append(f"Average CPU usage is high ({avg_cpu:.1f}%)")
                    analysis["recommendations"].append("Optimize CPU-intensive processes")
                    analysis["score"] -= 15
                
                if avg_memory > 80:
                    analysis["analysis"].append(f"Average memory usage is high ({avg_memory:.1f}%)")
                    analysis["recommendations"].append("Review memory leaks and optimize memory usage")
                    analysis["score"] -= 15
                
                if avg_disk > 75:
                    analysis["analysis"].append(f"Disk usage is high ({avg_disk:.1f}%)")
                    analysis["recommendations"].append("Clean up disk space or expand storage")
                    analysis["score"] -= 10
            
            # Analyze alerts
            alerts = alerts_data.get("alerts", [])
            unresolved = [a for a in alerts if not a.get("resolved")]
            if unresolved:
                analysis["analysis"].append(f"{len(unresolved)} unresolved alert(s)")
                analysis["recommendations"].append("Address unresolved alerts promptly")
                analysis["score"] -= min(20, len(unresolved) * 2)
            
            # Overall assessment
            if analysis["score"] >= 90:
                analysis["assessment"] = "Excellent - Agent is performing optimally"
            elif analysis["score"] >= 75:
                analysis["assessment"] = "Good - Minor issues detected"
            elif analysis["score"] >= 60:
                analysis["assessment"] = "Fair - Several issues need attention"
            else:
                analysis["assessment"] = "Poor - Immediate action required"
            
            if not analysis["analysis"]:
                analysis["analysis"].append("Agent is healthy and performing well")
                analysis["recommendations"].append("Continue monitoring")
            
            analysis["timestamp"] = datetime.utcnow().isoformat()
            
            return analysis
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Agent not found")
        raise HTTPException(status_code=502, detail="Failed to connect to License Server")
    except httpx.HTTPError as e:
        logger.error(f"Failed to analyze agent {agent_id}: {e}")
        raise HTTPException(status_code=502, detail="Failed to connect to License Server")