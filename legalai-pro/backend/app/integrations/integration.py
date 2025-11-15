"""
LegalAI Pro - iTechSmart Suite Integration
Connects with Enterprise Hub and Ninja for monitoring, self-healing, and cross-product communication
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ServiceRegistration(BaseModel):
    """Service registration data for Enterprise Hub"""
    service_id: str
    service_name: str
    service_type: str
    version: str
    host: str
    port: int
    health_endpoint: str
    capabilities: List[str]
    metadata: Dict[str, Any]


class HealthReport(BaseModel):
    """Health status report for Enterprise Hub"""
    service_id: str
    status: str  # healthy, degraded, unhealthy
    timestamp: datetime
    metrics: Dict[str, Any]
    issues: List[str]


class MetricsReport(BaseModel):
    """Performance metrics report for Enterprise Hub"""
    service_id: str
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    active_connections: int
    request_count: int
    error_count: int
    avg_response_time: float
    custom_metrics: Dict[str, Any]


class ErrorReport(BaseModel):
    """Error report for Ninja self-healing"""
    service_id: str
    error_type: str
    error_message: str
    stack_trace: str
    timestamp: datetime
    severity: str  # low, medium, high, critical
    context: Dict[str, Any]


class PerformanceReport(BaseModel):
    """Performance report for Ninja monitoring"""
    service_id: str
    timestamp: datetime
    endpoint: str
    response_time: float
    status_code: int
    error: Optional[str]


class LegalAIIntegration:
    """
    Main integration class for connecting LegalAI Pro with iTechSmart Suite
    Handles Hub registration, Ninja monitoring, and cross-product communication
    """
    
    def __init__(
        self,
        service_id: str = "legalai-pro",
        hub_url: Optional[str] = None,
        ninja_url: Optional[str] = None,
        enable_hub: bool = True,
        enable_ninja: bool = True
    ):
        self.service_id = service_id
        self.hub_url = hub_url or "http://itechsmart-enterprise:8000"
        self.ninja_url = ninja_url or "http://itechsmart-ninja:8000"
        self.enable_hub = enable_hub
        self.enable_ninja = enable_ninja
        
        self.client = httpx.AsyncClient(timeout=30.0)
        self.registered = False
        self.health_task: Optional[asyncio.Task] = None
        self.metrics_task: Optional[asyncio.Task] = None
        self.performance_task: Optional[asyncio.Task] = None
        
        logger.info(f"LegalAI Pro Integration initialized - Hub: {enable_hub}, Ninja: {enable_ninja}")
    
    async def initialize(self):
        """Initialize integration with Hub and Ninja"""
        try:
            if self.enable_hub:
                await self.register_with_hub()
                # Start background tasks
                self.health_task = asyncio.create_task(self._health_reporter())
                self.metrics_task = asyncio.create_task(self._metrics_reporter())
            
            if self.enable_ninja:
                await self.register_with_ninja()
                self.performance_task = asyncio.create_task(self._performance_monitor())
            
            logger.info("LegalAI Pro successfully integrated with iTechSmart Suite")
        except Exception as e:
            logger.error(f"Integration initialization failed: {e}")
            logger.info("Running in standalone mode")
    
    async def register_with_hub(self):
        """Register LegalAI Pro with Enterprise Hub"""
        try:
            registration = ServiceRegistration(
                service_id=self.service_id,
                service_name="LegalAI Pro",
                service_type="legal_management",
                version="1.0.0",
                host="legalai-pro",
                port=8000,
                health_endpoint="/health",
                capabilities=[
                    "client_management",
                    "case_management",
                    "document_management",
                    "ai_assistant",
                    "legal_research",
                    "contract_analysis",
                    "case_prediction",
                    "billing",
                    "time_tracking",
                    "calendar",
                    "reports"
                ],
                metadata={
                    "industry": "legal",
                    "ai_enabled": True,
                    "auto_fill": True,
                    "perfectlaw_compatible": True
                }
            )
            
            response = await self.client.post(
                f"{self.hub_url}/api/v1/services/register",
                json=registration.dict()
            )
            
            if response.status_code == 200:
                self.registered = True
                logger.info("Successfully registered with Enterprise Hub")
            else:
                logger.warning(f"Hub registration failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to register with Hub: {e}")
    
    async def register_with_ninja(self):
        """Register LegalAI Pro with Ninja for monitoring"""
        try:
            response = await self.client.post(
                f"{self.ninja_url}/api/v1/monitoring/register",
                json={
                    "service_id": self.service_id,
                    "service_name": "LegalAI Pro",
                    "monitoring_enabled": True,
                    "self_healing_enabled": True
                }
            )
            
            if response.status_code == 200:
                logger.info("Successfully registered with Ninja")
            else:
                logger.warning(f"Ninja registration failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to register with Ninja: {e}")
    
    async def _health_reporter(self):
        """Background task to report health to Hub every 30 seconds"""
        while True:
            try:
                await asyncio.sleep(30)
                
                if not self.registered:
                    continue
                
                health = await self._get_health_status()
                report = HealthReport(
                    service_id=self.service_id,
                    status=health["status"],
                    timestamp=datetime.utcnow(),
                    metrics=health["metrics"],
                    issues=health.get("issues", [])
                )
                
                await self.client.post(
                    f"{self.hub_url}/api/v1/services/health",
                    json=report.dict()
                )
            except Exception as e:
                logger.error(f"Health reporting failed: {e}")
    
    async def _metrics_reporter(self):
        """Background task to report metrics to Hub every 60 seconds"""
        while True:
            try:
                await asyncio.sleep(60)
                
                if not self.registered:
                    continue
                
                metrics = await self._collect_metrics()
                report = MetricsReport(
                    service_id=self.service_id,
                    timestamp=datetime.utcnow(),
                    cpu_usage=metrics["cpu_usage"],
                    memory_usage=metrics["memory_usage"],
                    active_connections=metrics["active_connections"],
                    request_count=metrics["request_count"],
                    error_count=metrics["error_count"],
                    avg_response_time=metrics["avg_response_time"],
                    custom_metrics={
                        "ai_queries": metrics.get("ai_queries", 0),
                        "documents_processed": metrics.get("documents_processed", 0),
                        "active_cases": metrics.get("active_cases", 0),
                        "billable_hours": metrics.get("billable_hours", 0)
                    }
                )
                
                await self.client.post(
                    f"{self.hub_url}/api/v1/services/metrics",
                    json=report.dict()
                )
            except Exception as e:
                logger.error(f"Metrics reporting failed: {e}")
    
    async def _performance_monitor(self):
        """Background task to monitor performance for Ninja every 60 seconds"""
        while True:
            try:
                await asyncio.sleep(60)
                
                performance = await self._check_performance()
                report = PerformanceReport(
                    service_id=self.service_id,
                    timestamp=datetime.utcnow(),
                    endpoint="/api/v1/health",
                    response_time=performance["response_time"],
                    status_code=performance["status_code"],
                    error=performance.get("error")
                )
                
                await self.client.post(
                    f"{self.ninja_url}/api/v1/monitoring/performance",
                    json=report.dict()
                )
            except Exception as e:
                logger.error(f"Performance monitoring failed: {e}")
    
    async def report_error(self, error: Exception, severity: str = "medium", context: Dict[str, Any] = None):
        """Report error to Ninja for self-healing"""
        if not self.enable_ninja:
            return
        
        try:
            import traceback
            
            report = ErrorReport(
                service_id=self.service_id,
                error_type=type(error).__name__,
                error_message=str(error),
                stack_trace=traceback.format_exc(),
                timestamp=datetime.utcnow(),
                severity=severity,
                context=context or {}
            )
            
            response = await self.client.post(
                f"{self.ninja_url}/api/v1/errors/report",
                json=report.dict()
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("auto_fix_available"):
                    logger.info(f"Ninja will attempt auto-fix: {result.get('fix_description')}")
                    return result
        except Exception as e:
            logger.error(f"Failed to report error to Ninja: {e}")
    
    async def call_service(self, service_id: str, endpoint: str, method: str = "GET", data: Dict[str, Any] = None):
        """Call another iTechSmart service via Hub routing"""
        if not self.enable_hub or not self.registered:
            raise Exception("Hub integration not available")
        
        try:
            response = await self.client.request(
                method=method,
                url=f"{self.hub_url}/api/v1/services/{service_id}/proxy{endpoint}",
                json=data
            )
            return response.json()
        except Exception as e:
            logger.error(f"Service call failed: {e}")
            raise
    
    async def discover_services(self) -> List[Dict[str, Any]]:
        """Discover other available iTechSmart services"""
        if not self.enable_hub or not self.registered:
            return []
        
        try:
            response = await self.client.get(f"{self.hub_url}/api/v1/services/discover")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Service discovery failed: {e}")
            return []
    
    async def _get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        # In production, implement actual health checks
        return {
            "status": "healthy",
            "metrics": {
                "uptime": 3600,
                "database_connected": True,
                "ai_service_available": True
            },
            "issues": []
        }
    
    async def _collect_metrics(self) -> Dict[str, Any]:
        """Collect current metrics"""
        # In production, implement actual metrics collection
        return {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "active_connections": 15,
            "request_count": 1250,
            "error_count": 3,
            "avg_response_time": 125.5,
            "ai_queries": 45,
            "documents_processed": 120,
            "active_cases": 78,
            "billable_hours": 156.5
        }
    
    async def _check_performance(self) -> Dict[str, Any]:
        """Check current performance"""
        # In production, implement actual performance checks
        return {
            "response_time": 95.3,
            "status_code": 200,
            "error": None
        }
    
    async def shutdown(self):
        """Gracefully shutdown integration"""
        logger.info("Shutting down iTechSmart integration...")
        
        # Cancel background tasks
        if self.health_task:
            self.health_task.cancel()
        if self.metrics_task:
            self.metrics_task.cancel()
        if self.performance_task:
            self.performance_task.cancel()
        
        # Unregister from Hub
        if self.registered:
            try:
                await self.client.post(
                    f"{self.hub_url}/api/v1/services/unregister",
                    json={"service_id": self.service_id}
                )
            except Exception as e:
                logger.error(f"Failed to unregister from Hub: {e}")
        
        await self.client.aclose()
        logger.info("Integration shutdown complete")


# Global integration instance
_integration: Optional[LegalAIIntegration] = None


def get_integration() -> LegalAIIntegration:
    """Get the global integration instance"""
    global _integration
    if _integration is None:
        _integration = LegalAIIntegration()
    return _integration


async def initialize_integration():
    """Initialize the global integration"""
    integration = get_integration()
    await integration.initialize()


async def shutdown_integration():
    """Shutdown the global integration"""
    global _integration
    if _integration:
        await _integration.shutdown()
        _integration = None