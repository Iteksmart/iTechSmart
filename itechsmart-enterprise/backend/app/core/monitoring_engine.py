"""
iTechSmart Enterprise - Real-Time Monitoring Engine
Continuous monitoring, alerting, and anomaly detection across all products
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import asyncio
from collections import deque
import statistics

from app.models.integration import (
    IntegratedService,
    ServiceHealth,
    DataSync,
    IntegrationEvent
)


class MonitoringEngine:
    """Real-time monitoring engine with alerting and anomaly detection"""
    
    def __init__(self, db: Session):
        self.db = db
        self.alert_handlers = []
        self.metrics_buffer = {}
        self.anomaly_thresholds = {
            "response_time": {
                "warning": 1000,  # ms
                "critical": 3000
            },
            "error_rate": {
                "warning": 5,  # percentage
                "critical": 10
            },
            "sync_failure_rate": {
                "warning": 10,  # percentage
                "critical": 25
            }
        }
    
    async def start_monitoring(self):
        """Start continuous monitoring loop"""
        while True:
            try:
                await self._monitor_cycle()
                await asyncio.sleep(60)  # Run every minute
            except Exception as e:
                print(f"Monitoring error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _monitor_cycle(self):
        """Execute one monitoring cycle"""
        
        # Check service health
        await self._check_service_health()
        
        # Monitor performance metrics
        await self._monitor_performance()
        
        # Check sync operations
        await self._monitor_syncs()
        
        # Detect anomalies
        await self._detect_anomalies()
        
        # Check for stuck workflows
        await self._check_workflows()
    
    async def _check_service_health(self):
        """Check health of all integrated services"""
        
        services = self.db.query(IntegratedService).filter(
            IntegratedService.status == "active"
        ).all()
        
        for service in services:
            try:
                # Get recent health checks
                recent_checks = self.db.query(ServiceHealth).filter(
                    and_(
                        ServiceHealth.service_id == service.id,
                        ServiceHealth.checked_at >= datetime.utcnow() - timedelta(minutes=5)
                    )
                ).all()
                
                if not recent_checks:
                    await self._create_alert(
                        severity="warning",
                        service_id=service.id,
                        alert_type="no_health_data",
                        message=f"No health data received for {service.name} in last 5 minutes"
                    )
                    continue
                
                # Check for consecutive failures
                if all(check.status == "unhealthy" for check in recent_checks[-3:]):
                    await self._create_alert(
                        severity="critical",
                        service_id=service.id,
                        alert_type="service_down",
                        message=f"{service.name} has failed 3 consecutive health checks"
                    )
                
                # Check response time degradation
                avg_response = statistics.mean([c.response_time for c in recent_checks])
                if avg_response > self.anomaly_thresholds["response_time"]["critical"]:
                    await self._create_alert(
                        severity="critical",
                        service_id=service.id,
                        alert_type="high_response_time",
                        message=f"{service.name} response time critically high: {avg_response:.2f}ms"
                    )
                elif avg_response > self.anomaly_thresholds["response_time"]["warning"]:
                    await self._create_alert(
                        severity="warning",
                        service_id=service.id,
                        alert_type="elevated_response_time",
                        message=f"{service.name} response time elevated: {avg_response:.2f}ms"
                    )
                
            except Exception as e:
                print(f"Error checking health for {service.name}: {str(e)}")
    
    async def _monitor_performance(self):
        """Monitor performance metrics across all services"""
        
        cutoff = datetime.utcnow() - timedelta(hours=1)
        
        # Get recent health checks
        health_checks = self.db.query(ServiceHealth).filter(
            ServiceHealth.checked_at >= cutoff
        ).all()
        
        if not health_checks:
            return
        
        # Calculate error rate
        total_checks = len(health_checks)
        failed_checks = sum(1 for h in health_checks if h.status == "unhealthy")
        error_rate = (failed_checks / total_checks) * 100
        
        if error_rate > self.anomaly_thresholds["error_rate"]["critical"]:
            await self._create_alert(
                severity="critical",
                service_id=None,
                alert_type="high_error_rate",
                message=f"System-wide error rate critically high: {error_rate:.2f}%"
            )
        elif error_rate > self.anomaly_thresholds["error_rate"]["warning"]:
            await self._create_alert(
                severity="warning",
                service_id=None,
                alert_type="elevated_error_rate",
                message=f"System-wide error rate elevated: {error_rate:.2f}%"
            )
        
        # Check for performance degradation trends
        await self._check_performance_trends(health_checks)
    
    async def _monitor_syncs(self):
        """Monitor data synchronization operations"""
        
        cutoff = datetime.utcnow() - timedelta(hours=1)
        
        # Get recent syncs
        syncs = self.db.query(DataSync).filter(
            DataSync.started_at >= cutoff
        ).all()
        
        if not syncs:
            return
        
        # Calculate sync failure rate
        total_syncs = len(syncs)
        failed_syncs = sum(1 for s in syncs if s.status == "failed")
        failure_rate = (failed_syncs / total_syncs) * 100
        
        if failure_rate > self.anomaly_thresholds["sync_failure_rate"]["critical"]:
            await self._create_alert(
                severity="critical",
                service_id=None,
                alert_type="high_sync_failure_rate",
                message=f"Sync failure rate critically high: {failure_rate:.2f}%"
            )
        elif failure_rate > self.anomaly_thresholds["sync_failure_rate"]["warning"]:
            await self._create_alert(
                severity="warning",
                service_id=None,
                alert_type="elevated_sync_failure_rate",
                message=f"Sync failure rate elevated: {failure_rate:.2f}%"
            )
        
        # Check for stuck syncs
        stuck_syncs = self.db.query(DataSync).filter(
            and_(
                DataSync.status == "in_progress",
                DataSync.started_at < datetime.utcnow() - timedelta(hours=2)
            )
        ).all()
        
        for sync in stuck_syncs:
            await self._create_alert(
                severity="warning",
                service_id=sync.source_service_id,
                alert_type="stuck_sync",
                message=f"Sync operation stuck for over 2 hours"
            )
    
    async def _detect_anomalies(self):
        """Detect anomalies using statistical analysis"""
        
        services = self.db.query(IntegratedService).filter(
            IntegratedService.status == "active"
        ).all()
        
        for service in services:
            # Get historical data (last 7 days)
            historical_cutoff = datetime.utcnow() - timedelta(days=7)
            historical_checks = self.db.query(ServiceHealth).filter(
                and_(
                    ServiceHealth.service_id == service.id,
                    ServiceHealth.checked_at >= historical_cutoff
                )
            ).all()
            
            if len(historical_checks) < 100:  # Need sufficient data
                continue
            
            # Calculate baseline metrics
            response_times = [c.response_time for c in historical_checks]
            mean_response = statistics.mean(response_times)
            stdev_response = statistics.stdev(response_times)
            
            # Get recent data (last hour)
            recent_cutoff = datetime.utcnow() - timedelta(hours=1)
            recent_checks = self.db.query(ServiceHealth).filter(
                and_(
                    ServiceHealth.service_id == service.id,
                    ServiceHealth.checked_at >= recent_cutoff
                )
            ).all()
            
            if not recent_checks:
                continue
            
            # Check for anomalies (3 standard deviations)
            recent_avg = statistics.mean([c.response_time for c in recent_checks])
            if abs(recent_avg - mean_response) > (3 * stdev_response):
                await self._create_alert(
                    severity="warning",
                    service_id=service.id,
                    alert_type="performance_anomaly",
                    message=f"{service.name} showing unusual performance pattern. "
                            f"Current: {recent_avg:.2f}ms, Baseline: {mean_response:.2f}ms"
                )
    
    async def _check_workflows(self):
        """Check for stuck or failing workflows"""
        
        from app.models.integration import CrossProductWorkflow
        
        # Check for workflows stuck in running state
        stuck_workflows = self.db.query(CrossProductWorkflow).filter(
            and_(
                CrossProductWorkflow.status == "running",
                CrossProductWorkflow.updated_at < datetime.utcnow() - timedelta(hours=1)
            )
        ).all()
        
        for workflow in stuck_workflows:
            await self._create_alert(
                severity="warning",
                service_id=None,
                alert_type="stuck_workflow",
                message=f"Workflow '{workflow.name}' stuck in running state for over 1 hour"
            )
    
    async def _check_performance_trends(self, health_checks: List[ServiceHealth]):
        """Check for performance degradation trends"""
        
        if len(health_checks) < 10:
            return
        
        # Sort by time
        sorted_checks = sorted(health_checks, key=lambda x: x.checked_at)
        
        # Split into two halves
        mid = len(sorted_checks) // 2
        first_half = sorted_checks[:mid]
        second_half = sorted_checks[mid:]
        
        # Calculate averages
        first_avg = statistics.mean([c.response_time for c in first_half])
        second_avg = statistics.mean([c.response_time for c in second_half])
        
        # Check for significant degradation (>50% increase)
        if second_avg > first_avg * 1.5:
            await self._create_alert(
                severity="warning",
                service_id=None,
                alert_type="performance_degradation",
                message=f"Performance degrading over time. "
                        f"Earlier: {first_avg:.2f}ms, Recent: {second_avg:.2f}ms"
            )
    
    async def _create_alert(
        self,
        severity: str,
        service_id: Optional[int],
        alert_type: str,
        message: str
    ):
        """Create and dispatch an alert"""
        
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "severity": severity,
            "service_id": service_id,
            "alert_type": alert_type,
            "message": message
        }
        
        # Log the alert
        print(f"[{severity.upper()}] {alert_type}: {message}")
        
        # Store in database
        event = IntegrationEvent(
            service_id=service_id,
            event_type=f"alert_{alert_type}",
            event_data=alert,
            created_at=datetime.utcnow()
        )
        self.db.add(event)
        self.db.commit()
        
        # Notify alert handlers
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                print(f"Error in alert handler: {str(e)}")
    
    def register_alert_handler(self, handler):
        """Register a custom alert handler"""
        self.alert_handlers.append(handler)
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        
        return {
            "monitoring_active": True,
            "last_check": datetime.utcnow().isoformat(),
            "thresholds": self.anomaly_thresholds,
            "alert_handlers": len(self.alert_handlers)
        }
    
    async def update_thresholds(self, thresholds: Dict[str, Any]):
        """Update monitoring thresholds"""
        
        self.anomaly_thresholds.update(thresholds)
        
        return {
            "status": "success",
            "message": "Thresholds updated",
            "new_thresholds": self.anomaly_thresholds
        }


class AlertManager:
    """Manage alert notifications and escalations"""
    
    def __init__(self):
        self.notification_channels = []
        self.escalation_rules = []
    
    async def send_alert(self, alert: Dict[str, Any]):
        """Send alert through configured channels"""
        
        for channel in self.notification_channels:
            try:
                await channel.send(alert)
            except Exception as e:
                print(f"Error sending alert through {channel}: {str(e)}")
    
    def add_notification_channel(self, channel):
        """Add a notification channel (email, Slack, etc.)"""
        self.notification_channels.append(channel)
    
    def add_escalation_rule(self, rule):
        """Add an escalation rule"""
        self.escalation_rules.append(rule)