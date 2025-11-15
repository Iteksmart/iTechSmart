"""
iTechSmart Enterprise - Advanced Dashboard Engine
Provides real-time monitoring, analytics, and insights across all iTechSmart products
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import asyncio
from collections import defaultdict
import json

from app.models.integration import (
    IntegratedService,
    ServiceHealth,
    DataSync,
    CrossProductWorkflow,
    IntegrationEvent
)
from app.core.integration_hub import IntegrationHub


class DashboardEngine:
    """Advanced dashboard engine for real-time monitoring and analytics"""
    
    def __init__(self, db: Session):
        self.db = db
        self.integration_hub = IntegrationHub(db)
        self.cache = {}
        self.cache_ttl = 60  # seconds
    
    async def get_suite_overview(self) -> Dict[str, Any]:
        """Get comprehensive overview of entire iTechSmart Suite"""
        
        overview = {
            "timestamp": datetime.utcnow().isoformat(),
            "products": await self._get_products_summary(),
            "health": await self._get_health_summary(),
            "activity": await self._get_activity_summary(),
            "performance": await self._get_performance_metrics(),
            "alerts": await self._get_active_alerts(),
            "trends": await self._get_trend_analysis()
        }
        
        return overview
    
    async def _get_products_summary(self) -> Dict[str, Any]:
        """Get summary of all integrated products"""
        
        services = self.db.query(IntegratedService).all()
        
        summary = {
            "total_products": len(services),
            "active_products": sum(1 for s in services if s.status == "active"),
            "inactive_products": sum(1 for s in services if s.status == "inactive"),
            "products": []
        }
        
        for service in services:
            product_info = {
                "id": service.id,
                "name": service.name,
                "type": service.service_type,
                "status": service.status,
                "version": service.version,
                "uptime": self._calculate_uptime(service),
                "last_sync": service.last_sync.isoformat() if service.last_sync else None,
                "health_score": await self._calculate_health_score(service.id)
            }
            summary["products"].append(product_info)
        
        return summary
    
    async def _get_health_summary(self) -> Dict[str, Any]:
        """Get health summary across all products"""
        
        # Get recent health checks (last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        health_checks = self.db.query(ServiceHealth).filter(
            ServiceHealth.checked_at >= cutoff
        ).all()
        
        if not health_checks:
            return {
                "overall_status": "unknown",
                "healthy_services": 0,
                "degraded_services": 0,
                "unhealthy_services": 0,
                "average_response_time": 0
            }
        
        healthy = sum(1 for h in health_checks if h.status == "healthy")
        degraded = sum(1 for h in health_checks if h.status == "degraded")
        unhealthy = sum(1 for h in health_checks if h.status == "unhealthy")
        
        avg_response = sum(h.response_time for h in health_checks) / len(health_checks)
        
        # Determine overall status
        if unhealthy > 0:
            overall = "critical"
        elif degraded > 0:
            overall = "degraded"
        else:
            overall = "healthy"
        
        return {
            "overall_status": overall,
            "healthy_services": healthy,
            "degraded_services": degraded,
            "unhealthy_services": unhealthy,
            "average_response_time": round(avg_response, 2),
            "total_checks": len(health_checks)
        }
    
    async def _get_activity_summary(self) -> Dict[str, Any]:
        """Get activity summary across all products"""
        
        # Get recent events (last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        events = self.db.query(IntegrationEvent).filter(
            IntegrationEvent.created_at >= cutoff
        ).all()
        
        # Get recent syncs
        syncs = self.db.query(DataSync).filter(
            DataSync.started_at >= cutoff
        ).all()
        
        # Get active workflows
        active_workflows = self.db.query(CrossProductWorkflow).filter(
            CrossProductWorkflow.status == "active"
        ).count()
        
        return {
            "total_events_24h": len(events),
            "events_by_type": self._group_by_field(events, "event_type"),
            "total_syncs_24h": len(syncs),
            "successful_syncs": sum(1 for s in syncs if s.status == "completed"),
            "failed_syncs": sum(1 for s in syncs if s.status == "failed"),
            "active_workflows": active_workflows,
            "data_transferred_mb": sum(s.records_synced or 0 for s in syncs) / 1000
        }
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics across all products"""
        
        cutoff = datetime.utcnow() - timedelta(hours=1)
        
        # Get recent health checks for performance data
        health_checks = self.db.query(ServiceHealth).filter(
            ServiceHealth.checked_at >= cutoff
        ).all()
        
        if not health_checks:
            return {
                "average_response_time": 0,
                "p95_response_time": 0,
                "p99_response_time": 0,
                "error_rate": 0
            }
        
        response_times = sorted([h.response_time for h in health_checks])
        
        return {
            "average_response_time": round(sum(response_times) / len(response_times), 2),
            "p95_response_time": round(response_times[int(len(response_times) * 0.95)], 2) if response_times else 0,
            "p99_response_time": round(response_times[int(len(response_times) * 0.99)], 2) if response_times else 0,
            "error_rate": round(sum(1 for h in health_checks if h.status == "unhealthy") / len(health_checks) * 100, 2),
            "total_requests": len(health_checks)
        }
    
    async def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts and issues"""
        
        alerts = []
        
        # Check for unhealthy services
        unhealthy = self.db.query(ServiceHealth).filter(
            ServiceHealth.status == "unhealthy"
        ).order_by(ServiceHealth.checked_at.desc()).limit(10).all()
        
        for health in unhealthy:
            service = self.db.query(IntegratedService).filter(
                IntegratedService.id == health.service_id
            ).first()
            
            if service:
                alerts.append({
                    "severity": "critical",
                    "type": "service_health",
                    "service": service.name,
                    "message": f"{service.name} is unhealthy: {health.details}",
                    "timestamp": health.checked_at.isoformat()
                })
        
        # Check for failed syncs
        failed_syncs = self.db.query(DataSync).filter(
            DataSync.status == "failed"
        ).order_by(DataSync.started_at.desc()).limit(10).all()
        
        for sync in failed_syncs:
            source = self.db.query(IntegratedService).filter(
                IntegratedService.id == sync.source_service_id
            ).first()
            
            if source:
                alerts.append({
                    "severity": "warning",
                    "type": "sync_failure",
                    "service": source.name,
                    "message": f"Data sync failed: {sync.error_message}",
                    "timestamp": sync.started_at.isoformat()
                })
        
        return alerts[:20]  # Return top 20 alerts
    
    async def _get_trend_analysis(self) -> Dict[str, Any]:
        """Get trend analysis for key metrics"""
        
        # Get data for last 7 days
        cutoff = datetime.utcnow() - timedelta(days=7)
        
        # Health trend
        health_checks = self.db.query(ServiceHealth).filter(
            ServiceHealth.checked_at >= cutoff
        ).all()
        
        health_by_day = defaultdict(lambda: {"healthy": 0, "degraded": 0, "unhealthy": 0})
        for check in health_checks:
            day = check.checked_at.date().isoformat()
            health_by_day[day][check.status] += 1
        
        # Sync trend
        syncs = self.db.query(DataSync).filter(
            DataSync.started_at >= cutoff
        ).all()
        
        sync_by_day = defaultdict(lambda: {"total": 0, "successful": 0, "failed": 0})
        for sync in syncs:
            day = sync.started_at.date().isoformat()
            sync_by_day[day]["total"] += 1
            if sync.status == "completed":
                sync_by_day[day]["successful"] += 1
            elif sync.status == "failed":
                sync_by_day[day]["failed"] += 1
        
        return {
            "health_trend": dict(health_by_day),
            "sync_trend": dict(sync_by_day),
            "period": "7_days"
        }
    
    async def get_product_details(self, service_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific product"""
        
        service = self.db.query(IntegratedService).filter(
            IntegratedService.id == service_id
        ).first()
        
        if not service:
            return {"error": "Service not found"}
        
        # Get recent health checks
        health_checks = self.db.query(ServiceHealth).filter(
            ServiceHealth.service_id == service_id
        ).order_by(ServiceHealth.checked_at.desc()).limit(100).all()
        
        # Get recent events
        events = self.db.query(IntegrationEvent).filter(
            IntegrationEvent.service_id == service_id
        ).order_by(IntegrationEvent.created_at.desc()).limit(50).all()
        
        # Get syncs involving this service
        syncs = self.db.query(DataSync).filter(
            or_(
                DataSync.source_service_id == service_id,
                DataSync.target_service_id == service_id
            )
        ).order_by(DataSync.started_at.desc()).limit(50).all()
        
        return {
            "service": {
                "id": service.id,
                "name": service.name,
                "type": service.service_type,
                "status": service.status,
                "version": service.version,
                "endpoint": service.endpoint_url,
                "created_at": service.created_at.isoformat(),
                "last_sync": service.last_sync.isoformat() if service.last_sync else None
            },
            "health": {
                "current_status": health_checks[0].status if health_checks else "unknown",
                "uptime_percentage": self._calculate_uptime_percentage(health_checks),
                "average_response_time": self._calculate_avg_response_time(health_checks),
                "recent_checks": [
                    {
                        "status": h.status,
                        "response_time": h.response_time,
                        "checked_at": h.checked_at.isoformat()
                    }
                    for h in health_checks[:10]
                ]
            },
            "activity": {
                "total_events": len(events),
                "recent_events": [
                    {
                        "type": e.event_type,
                        "data": e.event_data,
                        "created_at": e.created_at.isoformat()
                    }
                    for e in events[:10]
                ]
            },
            "syncs": {
                "total_syncs": len(syncs),
                "recent_syncs": [
                    {
                        "direction": "outbound" if s.source_service_id == service_id else "inbound",
                        "status": s.status,
                        "records": s.records_synced,
                        "started_at": s.started_at.isoformat(),
                        "completed_at": s.completed_at.isoformat() if s.completed_at else None
                    }
                    for s in syncs[:10]
                ]
            }
        }
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics for live dashboard updates"""
        
        # Get metrics from last 5 minutes
        cutoff = datetime.utcnow() - timedelta(minutes=5)
        
        recent_health = self.db.query(ServiceHealth).filter(
            ServiceHealth.checked_at >= cutoff
        ).all()
        
        recent_events = self.db.query(IntegrationEvent).filter(
            IntegrationEvent.created_at >= cutoff
        ).count()
        
        active_syncs = self.db.query(DataSync).filter(
            DataSync.status == "in_progress"
        ).count()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "active_services": len([h for h in recent_health if h.status == "healthy"]),
            "events_per_minute": recent_events / 5,
            "active_syncs": active_syncs,
            "average_response_time": sum(h.response_time for h in recent_health) / len(recent_health) if recent_health else 0
        }
    
    # Helper methods
    
    def _calculate_uptime(self, service: IntegratedService) -> str:
        """Calculate service uptime"""
        if not service.created_at:
            return "Unknown"
        
        uptime = datetime.utcnow() - service.created_at
        days = uptime.days
        hours = uptime.seconds // 3600
        
        return f"{days}d {hours}h"
    
    async def _calculate_health_score(self, service_id: int) -> float:
        """Calculate health score (0-100) for a service"""
        
        # Get health checks from last 24 hours
        cutoff = datetime.utcnow() - timedelta(hours=24)
        checks = self.db.query(ServiceHealth).filter(
            and_(
                ServiceHealth.service_id == service_id,
                ServiceHealth.checked_at >= cutoff
            )
        ).all()
        
        if not checks:
            return 0.0
        
        # Calculate score based on health status
        score = 0
        for check in checks:
            if check.status == "healthy":
                score += 100
            elif check.status == "degraded":
                score += 50
            # unhealthy = 0 points
        
        return round(score / len(checks), 2)
    
    def _calculate_uptime_percentage(self, health_checks: List[ServiceHealth]) -> float:
        """Calculate uptime percentage from health checks"""
        if not health_checks:
            return 0.0
        
        healthy = sum(1 for h in health_checks if h.status == "healthy")
        return round((healthy / len(health_checks)) * 100, 2)
    
    def _calculate_avg_response_time(self, health_checks: List[ServiceHealth]) -> float:
        """Calculate average response time from health checks"""
        if not health_checks:
            return 0.0
        
        return round(sum(h.response_time for h in health_checks) / len(health_checks), 2)
    
    def _group_by_field(self, items: List, field: str) -> Dict[str, int]:
        """Group items by a specific field and count"""
        groups = defaultdict(int)
        for item in items:
            value = getattr(item, field, "unknown")
            groups[value] += 1
        return dict(groups)