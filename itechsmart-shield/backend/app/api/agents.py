"""
iTechSmart Shield - Agent Integration API
Provides agent monitoring with security-focused insights
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
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )


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
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch agent {agent_id}: {e}")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )


@router.get("/agents/{agent_id}/security")
async def get_agent_security_status(agent_id: str):
    """
    Get security status for a specific agent

    Returns security-specific information including firewall status,
    antivirus status, and security compliance
    """
    try:
        async with await get_license_server_client() as client:
            # Get agent details
            response = await client.get(f"/api/agents/{agent_id}")
            response.raise_for_status()
            agent = response.json()

            # Extract security information from latest metrics
            last_metrics = agent.get("lastMetrics", {})
            security_info = last_metrics.get("security", {})

            # Calculate security score
            security_score = 100
            issues = []

            if not security_info.get("firewallEnabled", True):
                security_score -= 30
                issues.append(
                    {
                        "severity": "critical",
                        "type": "firewall",
                        "message": "Firewall is disabled",
                    }
                )

            if not security_info.get("antivirusEnabled", True):
                security_score -= 30
                issues.append(
                    {
                        "severity": "critical",
                        "type": "antivirus",
                        "message": "Antivirus is disabled",
                    }
                )

            if security_info.get("updatesAvailable", 0) > 0:
                security_score -= 10
                issues.append(
                    {
                        "severity": "warning",
                        "type": "updates",
                        "message": f"{security_info.get('updatesAvailable')} security updates available",
                    }
                )

            # Determine security status
            if security_score >= 90:
                status = "secure"
            elif security_score >= 70:
                status = "warning"
            else:
                status = "critical"

            return {
                "agentId": agent_id,
                "hostname": agent.get("hostname"),
                "securityScore": max(0, security_score),
                "status": status,
                "firewall": {
                    "enabled": security_info.get("firewallEnabled", True),
                    "status": (
                        "active"
                        if security_info.get("firewallEnabled", True)
                        else "disabled"
                    ),
                },
                "antivirus": {
                    "enabled": security_info.get("antivirusEnabled", True),
                    "status": (
                        "active"
                        if security_info.get("antivirusEnabled", True)
                        else "disabled"
                    ),
                    "lastScan": security_info.get("lastAntivirusScan"),
                },
                "updates": {
                    "available": security_info.get("updatesAvailable", 0),
                    "lastCheck": security_info.get("lastUpdateCheck"),
                },
                "issues": issues,
                "timestamp": datetime.utcnow().isoformat(),
            }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Agent not found")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch security status for agent {agent_id}: {e}")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )


@router.get("/agents/security/summary")
async def get_security_summary():
    """
    Get security summary for all agents

    Returns aggregated security metrics and threat levels
    """
    try:
        async with await get_license_server_client() as client:
            response = await client.get("/api/agents")
            response.raise_for_status()
            data = response.json()
            agents = data.get("agents", [])

            if not agents:
                return {
                    "totalAgents": 0,
                    "secureAgents": 0,
                    "atRiskAgents": 0,
                    "criticalAgents": 0,
                    "averageSecurityScore": 0,
                    "threats": [],
                    "recommendations": ["Deploy agents to start security monitoring"],
                }

            secure_count = 0
            at_risk_count = 0
            critical_count = 0
            total_score = 0
            threats = []

            for agent in agents:
                last_metrics = agent.get("lastMetrics", {})
                security_info = last_metrics.get("security", {})

                # Calculate security score for each agent
                score = 100

                if not security_info.get("firewallEnabled", True):
                    score -= 30
                    threats.append(
                        {
                            "agent": agent.get("hostname"),
                            "type": "firewall_disabled",
                            "severity": "critical",
                        }
                    )

                if not security_info.get("antivirusEnabled", True):
                    score -= 30
                    threats.append(
                        {
                            "agent": agent.get("hostname"),
                            "type": "antivirus_disabled",
                            "severity": "critical",
                        }
                    )

                if security_info.get("updatesAvailable", 0) > 0:
                    score -= 10
                    threats.append(
                        {
                            "agent": agent.get("hostname"),
                            "type": "updates_pending",
                            "severity": "warning",
                            "count": security_info.get("updatesAvailable"),
                        }
                    )

                total_score += max(0, score)

                if score >= 90:
                    secure_count += 1
                elif score >= 70:
                    at_risk_count += 1
                else:
                    critical_count += 1

            avg_score = round(total_score / len(agents)) if agents else 0

            # Generate recommendations
            recommendations = []
            if critical_count > 0:
                recommendations.append(
                    f"Immediately address {critical_count} critical security issue(s)"
                )
            if at_risk_count > 0:
                recommendations.append(
                    f"Review and resolve {at_risk_count} at-risk agent(s)"
                )
            if len(threats) > 0:
                recommendations.append(
                    "Enable all security features on affected agents"
                )
            if not recommendations:
                recommendations.append("All agents are secure. Continue monitoring.")

            return {
                "totalAgents": len(agents),
                "secureAgents": secure_count,
                "atRiskAgents": at_risk_count,
                "criticalAgents": critical_count,
                "averageSecurityScore": avg_score,
                "threats": threats[:10],  # Limit to top 10 threats
                "recommendations": recommendations,
                "timestamp": datetime.utcnow().isoformat(),
            }
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch security summary: {e}")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )


@router.get("/agents/security/threats")
async def get_security_threats():
    """
    Get all security threats across agents

    Returns detailed threat information with severity classification
    """
    try:
        async with await get_license_server_client() as client:
            response = await client.get("/api/agents")
            response.raise_for_status()
            data = response.json()
            agents = data.get("agents", [])

            threats = []

            for agent in agents:
                last_metrics = agent.get("lastMetrics", {})
                security_info = last_metrics.get("security", {})
                hostname = agent.get("hostname")

                if not security_info.get("firewallEnabled", True):
                    threats.append(
                        {
                            "id": f"{agent.get('id')}_firewall",
                            "agent": hostname,
                            "agentId": agent.get("id"),
                            "type": "firewall_disabled",
                            "severity": "critical",
                            "title": "Firewall Disabled",
                            "description": f"Firewall is disabled on {hostname}",
                            "recommendation": "Enable firewall immediately to protect against network threats",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

                if not security_info.get("antivirusEnabled", True):
                    threats.append(
                        {
                            "id": f"{agent.get('id')}_antivirus",
                            "agent": hostname,
                            "agentId": agent.get("id"),
                            "type": "antivirus_disabled",
                            "severity": "critical",
                            "title": "Antivirus Disabled",
                            "description": f"Antivirus protection is disabled on {hostname}",
                            "recommendation": "Enable antivirus and run a full system scan",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

                updates_available = security_info.get("updatesAvailable", 0)
                if updates_available > 0:
                    threats.append(
                        {
                            "id": f"{agent.get('id')}_updates",
                            "agent": hostname,
                            "agentId": agent.get("id"),
                            "type": "updates_pending",
                            "severity": "warning" if updates_available < 5 else "high",
                            "title": "Security Updates Pending",
                            "description": f"{updates_available} security update(s) available on {hostname}",
                            "recommendation": "Install security updates as soon as possible",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

            # Sort by severity
            severity_order = {"critical": 0, "high": 1, "warning": 2, "low": 3}
            threats.sort(key=lambda x: severity_order.get(x["severity"], 99))

            return {
                "threats": threats,
                "total": len(threats),
                "critical": sum(1 for t in threats if t["severity"] == "critical"),
                "high": sum(1 for t in threats if t["severity"] == "high"),
                "warning": sum(1 for t in threats if t["severity"] == "warning"),
                "timestamp": datetime.utcnow().isoformat(),
            }
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch security threats: {e}")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )


@router.get("/agents/{agent_id}/alerts")
async def get_agent_alerts(
    agent_id: str,
    severity: Optional[str] = Query(None, description="Filter by severity"),
    resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
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
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch alerts for agent {agent_id}: {e}")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )


@router.post("/agents/{agent_id}/security/scan")
async def trigger_security_scan(agent_id: str):
    """
    Trigger a security scan on a specific agent

    This would send a command to the agent to perform a security scan
    """
    try:
        async with await get_license_server_client() as client:
            # Send command to agent
            command_data = {
                "command": "security_scan",
                "parameters": {"type": "full", "priority": "high"},
            }

            response = await client.post(
                f"/api/agents/{agent_id}/commands", json=command_data
            )
            response.raise_for_status()

            return {
                "message": "Security scan initiated",
                "agentId": agent_id,
                "commandId": response.json().get("id"),
                "status": "pending",
                "timestamp": datetime.utcnow().isoformat(),
            }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Agent not found")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )
    except httpx.HTTPError as e:
        logger.error(f"Failed to trigger security scan for agent {agent_id}: {e}")
        raise HTTPException(
            status_code=502, detail="Failed to connect to License Server"
        )
