"""
iTechSmart Enterprise - Dashboard API Endpoints
Provides REST API for accessing dashboard data and real-time metrics
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, List, Any
import asyncio
import json

from app.core.dashboard_engine import DashboardEngine
from app.core.database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/overview")
async def get_suite_overview(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get comprehensive overview of entire iTechSmart Suite
    
    Returns:
        - Products summary
        - Health status
        - Activity metrics
        - Performance data
        - Active alerts
        - Trend analysis
    """
    dashboard = DashboardEngine(db)
    return await dashboard.get_suite_overview()


@router.get("/products")
async def get_products_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get summary of all integrated products
    
    Returns:
        - Total products count
        - Active/inactive breakdown
        - Individual product details
    """
    dashboard = DashboardEngine(db)
    overview = await dashboard.get_suite_overview()
    return overview["products"]


@router.get("/products/{service_id}")
async def get_product_details(
    service_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific product
    
    Args:
        service_id: ID of the integrated service
    
    Returns:
        - Service details
        - Health metrics
        - Recent activity
        - Sync history
    """
    dashboard = DashboardEngine(db)
    details = await dashboard.get_product_details(service_id)
    
    if "error" in details:
        raise HTTPException(status_code=404, detail=details["error"])
    
    return details


@router.get("/health")
async def get_health_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get health summary across all products
    
    Returns:
        - Overall health status
        - Healthy/degraded/unhealthy counts
        - Average response time
    """
    dashboard = DashboardEngine(db)
    overview = await dashboard.get_suite_overview()
    return overview["health"]


@router.get("/activity")
async def get_activity_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get activity summary across all products
    
    Returns:
        - Total events (24h)
        - Events by type
        - Sync statistics
        - Active workflows
    """
    dashboard = DashboardEngine(db)
    overview = await dashboard.get_suite_overview()
    return overview["activity"]


@router.get("/performance")
async def get_performance_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get performance metrics across all products
    
    Returns:
        - Average response time
        - P95/P99 response times
        - Error rate
    """
    dashboard = DashboardEngine(db)
    overview = await dashboard.get_suite_overview()
    return overview["performance"]


@router.get("/alerts")
async def get_active_alerts(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get active alerts and issues
    
    Returns:
        - List of active alerts
        - Severity levels
        - Affected services
    """
    dashboard = DashboardEngine(db)
    overview = await dashboard.get_suite_overview()
    return overview["alerts"]


@router.get("/trends")
async def get_trend_analysis(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get trend analysis for key metrics
    
    Returns:
        - Health trends (7 days)
        - Sync trends (7 days)
        - Performance trends
    """
    dashboard = DashboardEngine(db)
    overview = await dashboard.get_suite_overview()
    return overview["trends"]


@router.get("/metrics/realtime")
async def get_realtime_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get real-time metrics for live dashboard updates
    
    Returns:
        - Current active services
        - Events per minute
        - Active syncs
        - Current response time
    """
    dashboard = DashboardEngine(db)
    return await dashboard.get_real_time_metrics()


# WebSocket endpoint for real-time updates
class ConnectionManager:
    """Manage WebSocket connections for real-time dashboard updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)


manager = ConnectionManager()


@router.websocket("/ws/realtime")
async def websocket_realtime_updates(
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time dashboard updates
    
    Sends updates every 5 seconds with:
        - Real-time metrics
        - Health status changes
        - New alerts
    """
    await manager.connect(websocket)
    dashboard = DashboardEngine(db)
    
    try:
        while True:
            # Get real-time metrics
            metrics = await dashboard.get_real_time_metrics()
            
            # Send to client
            await websocket.send_json({
                "type": "metrics_update",
                "data": metrics
            })
            
            # Wait 5 seconds before next update
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)
        print(f"WebSocket error: {str(e)}")


@router.get("/export/overview")
async def export_overview_data(
    format: str = "json",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Export dashboard overview data
    
    Args:
        format: Export format (json, csv) - currently only json supported
    
    Returns:
        Complete dashboard data for export
    """
    if format not in ["json"]:
        raise HTTPException(
            status_code=400,
            detail="Only 'json' format is currently supported"
        )
    
    dashboard = DashboardEngine(db)
    overview = await dashboard.get_suite_overview()
    
    return {
        "export_format": format,
        "exported_at": overview["timestamp"],
        "data": overview
    }


@router.post("/refresh")
async def refresh_dashboard_cache(db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Force refresh of dashboard cache
    
    Returns:
        Success message
    """
    dashboard = DashboardEngine(db)
    dashboard.cache.clear()
    
    return {
        "status": "success",
        "message": "Dashboard cache refreshed successfully"
    }