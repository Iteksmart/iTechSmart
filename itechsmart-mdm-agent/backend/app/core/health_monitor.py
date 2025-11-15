"""
Health Monitor Module for iTechSmart MDM Deployment Agent

Provides continuous health monitoring, service health checks, auto-healing integration,
alert generation, performance tracking, and anomaly detection.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import aiohttp
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HealthCheckResult:
    """Health check result"""
    service_name: str
    status: HealthStatus
    response_time: float
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class ServiceMetrics:
    """Service performance metrics"""
    service_name: str
    cpu_usage: float
    memory_usage: float
    request_count: int
    error_count: int
    avg_response_time: float
    timestamp: datetime


@dataclass
class Alert:
    """System alert"""
    id: str
    service_name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class HealthMonitor:
    """
    Health Monitor for continuous monitoring of deployed services
    
    Features:
    - Continuous health monitoring
    - Service health checks
    - Auto-healing integration with Ninja
    - Alert generation
    - Performance tracking
    - Anomaly detection
    """
    
    def __init__(
        self,
        check_interval: int = 30,
        metrics_interval: int = 60,
        alert_threshold: int = 3,
        ninja_url: Optional[str] = None
    ):
        """
        Initialize Health Monitor
        
        Args:
            check_interval: Health check interval in seconds (default: 30)
            metrics_interval: Metrics collection interval in seconds (default: 60)
            alert_threshold: Number of failures before alerting (default: 3)
            ninja_url: URL of Ninja service for auto-healing
        """
        self.check_interval = check_interval
        self.metrics_interval = metrics_interval
        self.alert_threshold = alert_threshold
        self.ninja_url = ninja_url
        
        # Monitoring state
        self.services: Dict[str, Dict[str, Any]] = {}
        self.health_history: Dict[str, List[HealthCheckResult]] = {}
        self.metrics_history: Dict[str, List[ServiceMetrics]] = {}
        self.active_alerts: List[Alert] = []
        self.failure_counts: Dict[str, int] = {}
        
        # Monitoring tasks
        self.monitoring_task: Optional[asyncio.Task] = None
        self.metrics_task: Optional[asyncio.Task] = None
        self.running = False
        
        logger.info("Health Monitor initialized")
    
    async def start(self):
        """Start health monitoring"""
        if self.running:
            logger.warning("Health Monitor already running")
            return
        
        self.running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.metrics_task = asyncio.create_task(self._metrics_loop())
        logger.info("Health Monitor started")
    
    async def stop(self):
        """Stop health monitoring"""
        self.running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        if self.metrics_task:
            self.metrics_task.cancel()
            try:
                await self.metrics_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Health Monitor stopped")
    
    def register_service(
        self,
        service_name: str,
        health_endpoint: str,
        port: int,
        expected_status: int = 200
    ):
        """
        Register a service for monitoring
        
        Args:
            service_name: Name of the service
            health_endpoint: Health check endpoint path
            port: Service port
            expected_status: Expected HTTP status code (default: 200)
        """
        self.services[service_name] = {
            "health_endpoint": health_endpoint,
            "port": port,
            "expected_status": expected_status,
            "url": f"http://localhost:{port}{health_endpoint}"
        }
        self.health_history[service_name] = []
        self.metrics_history[service_name] = []
        self.failure_counts[service_name] = 0
        
        logger.info(f"Registered service: {service_name} at port {port}")
    
    def unregister_service(self, service_name: str):
        """Unregister a service from monitoring"""
        if service_name in self.services:
            del self.services[service_name]
            del self.health_history[service_name]
            del self.metrics_history[service_name]
            del self.failure_counts[service_name]
            logger.info(f"Unregistered service: {service_name}")
    
    async def check_service_health(self, service_name: str) -> HealthCheckResult:
        """
        Check health of a specific service
        
        Args:
            service_name: Name of the service to check
            
        Returns:
            HealthCheckResult with status and details
        """
        if service_name not in self.services:
            return HealthCheckResult(
                service_name=service_name,
                status=HealthStatus.UNKNOWN,
                response_time=0.0,
                timestamp=datetime.now(),
                error="Service not registered"
            )
        
        service = self.services[service_name]
        start_time = datetime.now()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    service["url"],
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response_time = (datetime.now() - start_time).total_seconds()
                    
                    if response.status == service["expected_status"]:
                        status = HealthStatus.HEALTHY
                        self.failure_counts[service_name] = 0
                    else:
                        status = HealthStatus.DEGRADED
                        self.failure_counts[service_name] += 1
                    
                    result = HealthCheckResult(
                        service_name=service_name,
                        status=status,
                        response_time=response_time,
                        timestamp=datetime.now(),
                        details={
                            "status_code": response.status,
                            "expected_status": service["expected_status"]
                        }
                    )
                    
        except asyncio.TimeoutError:
            self.failure_counts[service_name] += 1
            result = HealthCheckResult(
                service_name=service_name,
                status=HealthStatus.UNHEALTHY,
                response_time=5.0,
                timestamp=datetime.now(),
                error="Health check timeout"
            )
            
        except Exception as e:
            self.failure_counts[service_name] += 1
            result = HealthCheckResult(
                service_name=service_name,
                status=HealthStatus.UNHEALTHY,
                response_time=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now(),
                error=str(e)
            )
        
        # Store in history
        self.health_history[service_name].append(result)
        
        # Keep only last 100 checks
        if len(self.health_history[service_name]) > 100:
            self.health_history[service_name] = self.health_history[service_name][-100:]
        
        # Check if alert needed
        if self.failure_counts[service_name] >= self.alert_threshold:
            await self._generate_alert(service_name, result)
        
        return result
    
    async def check_all_services(self) -> Dict[str, HealthCheckResult]:
        """Check health of all registered services"""
        results = {}
        tasks = [
            self.check_service_health(service_name)
            for service_name in self.services.keys()
        ]
        
        if tasks:
            health_results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in health_results:
                if isinstance(result, HealthCheckResult):
                    results[result.service_name] = result
        
        return results
    
    async def collect_metrics(self, service_name: str) -> Optional[ServiceMetrics]:
        """
        Collect performance metrics for a service
        
        Args:
            service_name: Name of the service
            
        Returns:
            ServiceMetrics or None if collection fails
        """
        # In a real implementation, this would collect actual metrics
        # For now, we'll simulate metrics based on health checks
        
        if service_name not in self.health_history:
            return None
        
        recent_checks = self.health_history[service_name][-10:]
        if not recent_checks:
            return None
        
        # Calculate average response time
        avg_response_time = sum(c.response_time for c in recent_checks) / len(recent_checks)
        
        # Count errors
        error_count = sum(1 for c in recent_checks if c.status == HealthStatus.UNHEALTHY)
        
        # Simulate CPU and memory usage (in real implementation, get from system)
        cpu_usage = 50.0 + (error_count * 10)  # Higher CPU with more errors
        memory_usage = 60.0 + (avg_response_time * 5)  # Higher memory with slower responses
        
        metrics = ServiceMetrics(
            service_name=service_name,
            cpu_usage=min(cpu_usage, 100.0),
            memory_usage=min(memory_usage, 100.0),
            request_count=len(recent_checks),
            error_count=error_count,
            avg_response_time=avg_response_time,
            timestamp=datetime.now()
        )
        
        # Store in history
        self.metrics_history[service_name].append(metrics)
        
        # Keep only last 100 metrics
        if len(self.metrics_history[service_name]) > 100:
            self.metrics_history[service_name] = self.metrics_history[service_name][-100:]
        
        return metrics
    
    async def _monitoring_loop(self):
        """Continuous health monitoring loop"""
        logger.info("Starting health monitoring loop")
        
        while self.running:
            try:
                await self.check_all_services()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _metrics_loop(self):
        """Continuous metrics collection loop"""
        logger.info("Starting metrics collection loop")
        
        while self.running:
            try:
                for service_name in self.services.keys():
                    await self.collect_metrics(service_name)
                await asyncio.sleep(self.metrics_interval)
            except Exception as e:
                logger.error(f"Error in metrics loop: {e}")
                await asyncio.sleep(self.metrics_interval)
    
    async def _generate_alert(self, service_name: str, health_result: HealthCheckResult):
        """Generate alert for service failure"""
        # Check if alert already exists
        existing_alert = next(
            (a for a in self.active_alerts 
             if a.service_name == service_name and not a.resolved),
            None
        )
        
        if existing_alert:
            return  # Alert already active
        
        # Determine severity
        if self.failure_counts[service_name] >= self.alert_threshold * 2:
            severity = AlertSeverity.CRITICAL
        elif self.failure_counts[service_name] >= self.alert_threshold:
            severity = AlertSeverity.ERROR
        else:
            severity = AlertSeverity.WARNING
        
        alert = Alert(
            id=f"{service_name}_{datetime.now().timestamp()}",
            service_name=service_name,
            severity=severity,
            message=f"Service {service_name} is {health_result.status.value}. "
                   f"Failure count: {self.failure_counts[service_name]}. "
                   f"Error: {health_result.error or 'Unknown'}",
            timestamp=datetime.now()
        )
        
        self.active_alerts.append(alert)
        logger.warning(f"Alert generated: {alert.message}")
        
        # Trigger auto-healing if Ninja is available
        if self.ninja_url and severity in [AlertSeverity.ERROR, AlertSeverity.CRITICAL]:
            await self._trigger_auto_healing(service_name, health_result)
    
    async def _trigger_auto_healing(self, service_name: str, health_result: HealthCheckResult):
        """Trigger auto-healing via Ninja"""
        if not self.ninja_url:
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "service_name": service_name,
                    "status": health_result.status.value,
                    "error": health_result.error,
                    "timestamp": health_result.timestamp.isoformat()
                }
                
                async with session.post(
                    f"{self.ninja_url}/api/heal",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Auto-healing triggered for {service_name}")
                    else:
                        logger.error(f"Failed to trigger auto-healing: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error triggering auto-healing: {e}")
    
    def resolve_alert(self, alert_id: str):
        """Resolve an active alert"""
        for alert in self.active_alerts:
            if alert.id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                logger.info(f"Alert resolved: {alert_id}")
                return True
        return False
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        if not self.services:
            return {
                "status": HealthStatus.UNKNOWN,
                "total_services": 0,
                "healthy": 0,
                "degraded": 0,
                "unhealthy": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        # Get latest health check for each service
        latest_checks = {}
        for service_name in self.services.keys():
            if self.health_history[service_name]:
                latest_checks[service_name] = self.health_history[service_name][-1]
        
        # Count statuses
        healthy = sum(1 for c in latest_checks.values() if c.status == HealthStatus.HEALTHY)
        degraded = sum(1 for c in latest_checks.values() if c.status == HealthStatus.DEGRADED)
        unhealthy = sum(1 for c in latest_checks.values() if c.status == HealthStatus.UNHEALTHY)
        
        # Determine overall status
        if unhealthy > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded > 0:
            overall_status = HealthStatus.DEGRADED
        elif healthy == len(self.services):
            overall_status = HealthStatus.HEALTHY
        else:
            overall_status = HealthStatus.UNKNOWN
        
        return {
            "status": overall_status,
            "total_services": len(self.services),
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "active_alerts": len([a for a in self.active_alerts if not a.resolved]),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_service_health_history(
        self,
        service_name: str,
        hours: int = 24
    ) -> List[HealthCheckResult]:
        """Get health history for a service"""
        if service_name not in self.health_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            check for check in self.health_history[service_name]
            if check.timestamp >= cutoff_time
        ]
    
    def get_service_metrics_history(
        self,
        service_name: str,
        hours: int = 24
    ) -> List[ServiceMetrics]:
        """Get metrics history for a service"""
        if service_name not in self.metrics_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            metrics for metrics in self.metrics_history[service_name]
            if metrics.timestamp >= cutoff_time
        ]
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        return [alert for alert in self.active_alerts if not alert.resolved]
    
    def get_all_alerts(self, hours: int = 24) -> List[Alert]:
        """Get all alerts within specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            alert for alert in self.active_alerts
            if alert.timestamp >= cutoff_time
        ]