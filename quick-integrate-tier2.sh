#!/bin/bash
# Quick integration script for remaining Tier 2 products

echo "🚀 Quick Integration for Tier 2 Products"
echo "=========================================="

# Function to add agent endpoints to Python backend
add_python_agent_endpoints() {
    local product=$1
    local port=$2
    
    echo "📦 Integrating $product..."
    
    # Create agents.py API file
    cat > "$product/backend/app/api/agents.py" << 'EOF'
"""
Agent Integration API
Provides agent monitoring endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
import httpx
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

LICENSE_SERVER_URL = os.getenv("LICENSE_SERVER_URL", "http://localhost:3000")

async def get_license_server_client():
    return httpx.AsyncClient(
        base_url=LICENSE_SERVER_URL,
        timeout=30.0,
        headers={"Content-Type": "application/json"}
    )

@router.get("/agents")
async def get_agents(
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
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

@router.get("/agents/stats/summary")
async def get_agents_summary():
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
            
            return {
                "total": total,
                "active": active,
                "offline": offline,
                "error": error,
                "timestamp": datetime.utcnow().isoformat()
            }
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch agents summary: {e}")
        raise HTTPException(status_code=502, detail="Failed to connect to License Server")
EOF

    # Create .env.example
    cat > "$product/.env.example" << EOF
# $product - Environment Configuration

PORT=$port
HOST=0.0.0.0

# License Server Integration
LICENSE_SERVER_URL=http://localhost:3000

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/db

# Logging
LOG_LEVEL=INFO
EOF

    echo "✅ $product integrated successfully"
}

# Integrate Sentinel (port 8018)
add_python_agent_endpoints "itechsmart-sentinel" "8018"

# Integrate DevOps (port 8019)
add_python_agent_endpoints "itechsmart-devops" "8019"

echo ""
echo "✅ All Tier 2 products integrated!"
echo "📝 Next: Update main.py files to include agent routers"
EOF

chmod +x iTechSmart/quick-integrate-tier2.sh