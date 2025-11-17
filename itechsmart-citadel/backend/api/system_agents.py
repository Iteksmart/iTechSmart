"""
System Agents API
Provides access to iTechSmart Agent monitoring and management for Citadel Security
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import os
import httpx

from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

# License Server configuration
LICENSE_SERVER_URL = os.getenv('LICENSE_SERVER_URL', 'http://localhost:3000')

# Pydantic models for request/response
class SystemMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_rx: float
    network_tx: float

class SecurityStatus(BaseModel):
    firewall_enabled: bool
    antivirus_enabled: bool
    updates_available: int

class AgentStatus(BaseModel):
    id: str
    hostname: str
    ip_address: str
    platform: str
    status: str
    last_seen: datetime
    version: str
    organization_id: Optional[str] = None

class AgentMetric(BaseModel):
    id: str
    agent_id: str
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_rx: float
    network_tx: float

class AgentAlert(BaseModel):
    id: str
    agent_id: str
    severity: str
    message: str
    created_at: datetime
    resolved: bool
    resolved_at: Optional[datetime] = None

class AgentCommand(BaseModel):
    id: str
    agent_id: str
    command: str
    parameters: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    executed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None

class CommandRequest(BaseModel):
    command: str
    parameters: Optional[Dict[str, Any]] = None

class SecurityScore(BaseModel):
    agent_id: str
    score: int
    firewall: bool
    antivirus: bool
    updates_current: bool
    encryption_enabled: bool
    last_scan: datetime

# Helper function to make authenticated requests to License Server
async def make_license_server_request(
    method: str,
    endpoint: str,
    token: str,
    data: Optional[Dict] = None,
    params: Optional[Dict] = None
):
    """Make authenticated request to License Server"""
    url = f"{LICENSE_SERVER_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"License Server request failed: {e}")
            raise HTTPException(status_code=500, detail=f"License Server error: {str(e)}")

def get_auth_token():
    """Get authentication token from environment"""
    token = os.getenv('AUTH_TOKEN', 'demo-token')
    return token

@router.get("/", response_model=Dict[str, Any])
async def list_agents(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """
    List all system monitoring agents
    """
    params = {
        "page": page,
        "limit": limit,
    }
    if status:
        params["status"] = status
    if search:
        params["search"] = search
    
    token = get_auth_token()
    
    result = await make_license_server_request(
        "GET",
        "/api/agents",
        token,
        params=params
    )
    
    return result

@router.get("/{agent_id}", response_model=AgentStatus)
async def get_agent(agent_id: str):
    """Get detailed information about a specific agent"""
    token = get_auth_token()
    
    result = await make_license_server_request(
        "GET",
        f"/api/agents/{agent_id}",
        token
    )
    
    return result

@router.put("/{agent_id}", response_model=AgentStatus)
async def update_agent(agent_id: str, data: Dict[str, Any]):
    """Update agent configuration"""
    token = get_auth_token()
    
    result = await make_license_server_request(
        "PUT",
        f"/api/agents/{agent_id}",
        token,
        data=data
    )
    
    return result

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent"""
    token = get_auth_token()
    
    await make_license_server_request(
        "DELETE",
        f"/api/agents/{agent_id}",
        token
    )
    
    return {"message": "Agent deleted successfully"}

@router.get("/{agent_id}/metrics", response_model=List[AgentMetric])
async def get_agent_metrics(
    agent_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Get historical metrics for an agent"""
    token = get_auth_token()
    
    params = {"limit": limit}
    if start_date:
        params["startDate"] = start_date.isoformat()
    if end_date:
        params["endDate"] = end_date.isoformat()
    
    result = await make_license_server_request(
        "GET",
        f"/api/agents/{agent_id}/metrics",
        token,
        params=params
    )
    
    return result

@router.get("/{agent_id}/metrics/latest", response_model=AgentMetric)
async def get_latest_metrics(agent_id: str):
    """Get the most recent metrics for an agent"""
    token = get_auth_token()
    
    result = await make_license_server_request(
        "GET",
        f"/api/agents/{agent_id}/metrics/latest",
        token
    )
    
    return result

@router.get("/{agent_id}/metrics/system", response_model=SystemMetrics)
async def get_system_metrics(agent_id: str):
    """Get current system metrics (CPU, Memory, Disk, Network)"""
    token = get_auth_token()
    
    metrics = await make_license_server_request(
        "GET",
        f"/api/agents/{agent_id}/metrics/latest",
        token
    )
    
    return SystemMetrics(
        cpu_usage=metrics.get('cpu_usage', 0),
        memory_usage=metrics.get('memory_usage', 0),
        disk_usage=metrics.get('disk_usage', 0),
        network_rx=metrics.get('network_rx', 0),
        network_tx=metrics.get('network_tx', 0)
    )

@router.get("/{agent_id}/security", response_model=SecurityStatus)
async def get_security_status(agent_id: str):
    """Get security status for an agent"""
    token = get_auth_token()
    
    metrics = await make_license_server_request(
        "GET",
        f"/api/agents/{agent_id}/metrics/latest",
        token
    )
    
    return SecurityStatus(
        firewall_enabled=metrics.get('firewall_enabled', False),
        antivirus_enabled=metrics.get('antivirus_enabled', False),
        updates_available=metrics.get('updates_available', 0)
    )

@router.get("/{agent_id}/security/score", response_model=SecurityScore)
async def get_security_score(agent_id: str):
    """
    Get comprehensive security score for an agent (Citadel-specific)
    """
    token = get_auth_token()
    
    metrics = await make_license_server_request(
        "GET",
        f"/api/agents/{agent_id}/metrics/latest",
        token
    )
    
    # Calculate security score (0-100)
    score = 100
    firewall = metrics.get('firewall_enabled', False)
    antivirus = metrics.get('antivirus_enabled', False)
    updates = metrics.get('updates_available', 0)
    
    if not firewall:
        score -= 30
    if not antivirus:
        score -= 30
    if updates > 0:
        score -= min(updates * 5, 40)
    
    return SecurityScore(
        agent_id=agent_id,
        score=max(0, score),
        firewall=firewall,
        antivirus=antivirus,
        updates_current=(updates == 0),
        encryption_enabled=True,  # Assume enabled for now
        last_scan=datetime.utcnow()
    )

@router.get("/{agent_id}/alerts", response_model=List[AgentAlert])
async def get_agent_alerts(
    agent_id: str,
    severity: Optional[str] = None,
    resolved: Optional[bool] = None
):
    """Get alerts for an agent"""
    token = get_auth_token()
    
    params = {}
    if severity:
        params["severity"] = severity
    if resolved is not None:
        params["resolved"] = resolved
    
    result = await make_license_server_request(
        "GET",
        f"/api/agents/{agent_id}/alerts",
        token,
        params=params
    )
    
    return result

@router.put("/{agent_id}/alerts/{alert_id}/resolve")
async def resolve_alert(agent_id: str, alert_id: str):
    """Mark an alert as resolved"""
    token = get_auth_token()
    
    await make_license_server_request(
        "PUT",
        f"/api/agents/{agent_id}/alerts/{alert_id}/resolve",
        token
    )
    
    return {"message": "Alert resolved successfully"}

@router.get("/{agent_id}/alerts/count")
async def get_unresolved_alert_count(agent_id: str):
    """Get count of unresolved alerts"""
    token = get_auth_token()
    
    result = await make_license_server_request(
        "GET",
        f"/api/agents/{agent_id}/alerts/count",
        token
    )
    
    return result

@router.post("/{agent_id}/commands", response_model=AgentCommand)
async def send_command(agent_id: str, command_request: CommandRequest):
    """Send a command to an agent"""
    token = get_auth_token()
    
    result = await make_license_server_request(
        "POST",
        f"/api/agents/{agent_id}/commands",
        token,
        data=command_request.dict()
    )
    
    return result

@router.post("/{agent_id}/commands/execute")
async def execute_command(agent_id: str, command_request: CommandRequest):
    """Execute a command on an agent and wait for result"""
    token = get_auth_token()
    
    result = await make_license_server_request(
        "POST",
        f"/api/agents/{agent_id}/commands/execute",
        token,
        data=command_request.dict()
    )
    
    return result

@router.get("/{agent_id}/commands", response_model=List[AgentCommand])
async def get_agent_commands(agent_id: str):
    """Get command history for an agent"""
    token = get_auth_token()
    
    result = await make_license_server_request(
        "GET",
        f"/api/agents/{agent_id}/commands",
        token
    )
    
    return result

@router.get("/{agent_id}/commands/{command_id}", response_model=AgentCommand)
async def get_command_status(agent_id: str, command_id: str):
    """Get status of a specific command"""
    token = get_auth_token()
    
    result = await make_license_server_request(
        "GET",
        f"/api/agents/{agent_id}/commands/{command_id}",
        token
    )
    
    return result

@router.get("/stats/overview")
async def get_agent_stats():
    """Get overview statistics for all agents"""
    token = get_auth_token()
    
    agents_result = await make_license_server_request(
        "GET",
        "/api/agents",
        token,
        params={"limit": 1000}
    )
    
    agents = agents_result.get('agents', [])
    total = len(agents)
    active = len([a for a in agents if a.get('status') == 'ACTIVE'])
    offline = len([a for a in agents if a.get('status') == 'OFFLINE'])
    error = len([a for a in agents if a.get('status') == 'ERROR'])
    
    # Get total unresolved alerts
    total_alerts = 0
    for agent in agents:
        try:
            alert_count = await make_license_server_request(
                "GET",
                f"/api/agents/{agent['id']}/alerts/count",
                token
            )
            total_alerts += alert_count.get('count', 0)
        except:
            pass
    
    return {
        "total_agents": total,
        "active_agents": active,
        "offline_agents": offline,
        "error_agents": error,
        "total_unresolved_alerts": total_alerts
    }

@router.get("/security/overview")
async def get_security_overview():
    """
    Get security overview for all agents (Citadel-specific)
    """
    token = get_auth_token()
    
    agents_result = await make_license_server_request(
        "GET",
        "/api/agents",
        token,
        params={"limit": 1000}
    )
    
    agents = agents_result.get('agents', [])
    
    # Calculate security metrics
    total_agents = len(agents)
    secure_agents = 0
    at_risk_agents = 0
    critical_agents = 0
    
    for agent in agents:
        try:
            metrics = await make_license_server_request(
                "GET",
                f"/api/agents/{agent['id']}/metrics/latest",
                token
            )
            
            firewall = metrics.get('firewall_enabled', False)
            antivirus = metrics.get('antivirus_enabled', False)
            updates = metrics.get('updates_available', 0)
            
            # Calculate risk level
            if firewall and antivirus and updates == 0:
                secure_agents += 1
            elif not firewall or not antivirus:
                critical_agents += 1
            else:
                at_risk_agents += 1
        except:
            critical_agents += 1
    
    return {
        "total_agents": total_agents,
        "secure_agents": secure_agents,
        "at_risk_agents": at_risk_agents,
        "critical_agents": critical_agents,
        "security_score": round((secure_agents / total_agents * 100) if total_agents > 0 else 0, 2)
    }