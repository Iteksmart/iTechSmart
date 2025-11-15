"""
iTechSmart Ninja - Integration Module
This module provides self-healing and monitoring capabilities for all iTechSmart products
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import httpx

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorReport:
    """Error report"""
    service_id: str
    error_type: str
    severity: ErrorSeverity
    message: str
    stack_trace: Optional[str]
    context: Dict[str, Any]
    timestamp: datetime
    auto_fixed: bool = False


@dataclass
class PerformanceReport:
    """Performance report"""
    service_id: str
    endpoint: str
    response_time: float
    memory_usage: float
    cpu_usage: float
    timestamp: datetime


@dataclass
class HealthCheckResult:
    """Health check result"""
    service_id: str
    is_healthy: bool
    issues: List[str]
    recommendations: List[str]
    timestamp: datetime


class NinjaIntegrationClient:
    """
    Ninja Integration Client for iTechSmart Products
    
    This client enables any iTechSmart product to:
    - Report errors for auto-fixing
    - Get performance optimization recommendations
    - Receive self-healing actions
    - Monitor health continuously
    - Auto-update dependencies
    """
    
    def __init__(
        self,
        service_name: str,
        service_version: str,
        ninja_url: str = "http://localhost:8001",
        enable_auto_healing: bool = True
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.ninja_url = ninja_url
        self.service_id = f"{service_name}_{datetime.now().timestamp()}"
        self.enable_auto_healing = enable_auto_healing
        
        self.is_monitoring = False
        self.error_handlers: Dict[str, Callable] = {}
        
        self.client = httpx.AsyncClient(timeout=30.0)
        
        logger.info(f"Ninja Integration Client initialized for {service_name}")
    
    async def register_with_ninja(self) -> bool:
        """
        Register service with Ninja for monitoring
        
        Returns:
            True if registration successful
        """
        try:
            response = await self.client.post(
                f"{self.ninja_url}/api/ninja/register",
                json={
                    "service_id": self.service_id,
                    "service_name": self.service_name,
                    "version": self.service_version,
                    "enable_auto_healing": self.enable_auto_healing,
                    "registered_at": datetime.now().isoformat()
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully registered {self.service_name} with Ninja")
                return True
            else:
                logger.error(f"Failed to register with Ninja: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error registering with Ninja: {e}")
            return False
    
    async def report_error(
        self,
        error_type: str,
        severity: ErrorSeverity,
        message: str,
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Report error to Ninja for analysis and auto-fixing
        
        Args:
            error_type: Type of error
            severity: Error severity
            message: Error message
            stack_trace: Stack trace
            context: Additional context
        
        Returns:
            Ninja's response with fix recommendations
        """
        try:
            error_report = ErrorReport(
                service_id=self.service_id,
                error_type=error_type,
                severity=severity,
                message=message,
                stack_trace=stack_trace,
                context=context or {},
                timestamp=datetime.now()
            )
            
            response = await self.client.post(
                f"{self.ninja_url}/api/ninja/errors",
                json={
                    "service_id": error_report.service_id,
                    "error_type": error_report.error_type,
                    "severity": error_report.severity.value,
                    "message": error_report.message,
                    "stack_trace": error_report.stack_trace,
                    "context": error_report.context,
                    "timestamp": error_report.timestamp.isoformat()
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Error reported to Ninja: {result.get('fix_applied', False)}")
                return result
            else:
                logger.error(f"Failed to report error to Ninja: {response.status_code}")
                return {"fix_applied": False, "recommendations": []}
                
        except Exception as e:
            logger.error(f"Error reporting to Ninja: {e}")
            return {"fix_applied": False, "recommendations": []}
    
    async def report_performance(
        self,
        endpoint: str,
        response_time: float,
        memory_usage: float,
        cpu_usage: float
    ) -> Dict[str, Any]:
        """
        Report performance metrics to Ninja for optimization
        
        Args:
            endpoint: API endpoint
            response_time: Response time in ms
            memory_usage: Memory usage percentage
            cpu_usage: CPU usage percentage
        
        Returns:
            Optimization recommendations
        """
        try:
            perf_report = PerformanceReport(
                service_id=self.service_id,
                endpoint=endpoint,
                response_time=response_time,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                timestamp=datetime.now()
            )
            
            response = await self.client.post(
                f"{self.ninja_url}/api/ninja/performance",
                json={
                    "service_id": perf_report.service_id,
                    "endpoint": perf_report.endpoint,
                    "response_time": perf_report.response_time,
                    "memory_usage": perf_report.memory_usage,
                    "cpu_usage": perf_report.cpu_usage,
                    "timestamp": perf_report.timestamp.isoformat()
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"optimizations": []}
                
        except Exception as e:
            logger.error(f"Error reporting performance to Ninja: {e}")
            return {"optimizations": []}
    
    async def request_health_check(self) -> HealthCheckResult:
        """
        Request health check from Ninja
        
        Returns:
            Health check result
        """
        try:
            response = await self.client.get(
                f"{self.ninja_url}/api/ninja/health-check/{self.service_id}"
            )
            
            if response.status_code == 200:
                data = response.json()
                return HealthCheckResult(
                    service_id=self.service_id,
                    is_healthy=data.get("is_healthy", True),
                    issues=data.get("issues", []),
                    recommendations=data.get("recommendations", []),
                    timestamp=datetime.now()
                )
            else:
                return HealthCheckResult(
                    service_id=self.service_id,
                    is_healthy=False,
                    issues=["Failed to get health check from Ninja"],
                    recommendations=[],
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Error requesting health check from Ninja: {e}")
            return HealthCheckResult(
                service_id=self.service_id,
                is_healthy=False,
                issues=[str(e)],
                recommendations=[],
                timestamp=datetime.now()
            )
    
    async def request_optimization(self) -> Dict[str, Any]:
        """
        Request optimization recommendations from Ninja
        
        Returns:
            Optimization recommendations
        """
        try:
            response = await self.client.get(
                f"{self.ninja_url}/api/ninja/optimize/{self.service_id}"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"optimizations": []}
                
        except Exception as e:
            logger.error(f"Error requesting optimization from Ninja: {e}")
            return {"optimizations": []}
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """
        Start continuous monitoring with Ninja
        
        Args:
            interval_seconds: Monitoring interval in seconds
        """
        self.is_monitoring = True
        logger.info(f"Started Ninja monitoring every {interval_seconds} seconds")
        
        while self.is_monitoring:
            try:
                # Request health check
                health_result = await self.request_health_check()
                
                if not health_result.is_healthy:
                    logger.warning(f"Health issues detected: {health_result.issues}")
                    
                    # Apply recommendations if auto-healing is enabled
                    if self.enable_auto_healing and health_result.recommendations:
                        logger.info(f"Applying {len(health_result.recommendations)} recommendations")
                        # Apply recommendations here
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)
    
    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.is_monitoring = False
        logger.info("Stopped Ninja monitoring")
    
    def register_error_handler(self, error_type: str, handler: Callable):
        """
        Register custom error handler
        
        Args:
            error_type: Type of error to handle
            handler: Handler function
        """
        self.error_handlers[error_type] = handler
        logger.info(f"Registered error handler for {error_type}")
    
    async def handle_error(self, error_type: str, error: Exception) -> bool:
        """
        Handle error using registered handler or Ninja
        
        Args:
            error_type: Type of error
            error: Exception object
        
        Returns:
            True if error was handled
        """
        # Try custom handler first
        if error_type in self.error_handlers:
            try:
                await self.error_handlers[error_type](error)
                return True
            except Exception as e:
                logger.error(f"Error in custom handler: {e}")
        
        # Report to Ninja for auto-fixing
        result = await self.report_error(
            error_type=error_type,
            severity=ErrorSeverity.HIGH,
            message=str(error),
            stack_trace=None,
            context={"error_class": error.__class__.__name__}
        )
        
        return result.get("fix_applied", False)
    
    async def request_dependency_update(self) -> Dict[str, Any]:
        """
        Request dependency update check from Ninja
        
        Returns:
            Update recommendations
        """
        try:
            response = await self.client.get(
                f"{self.ninja_url}/api/ninja/dependencies/{self.service_id}"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"updates_available": []}
                
        except Exception as e:
            logger.error(f"Error requesting dependency update: {e}")
            return {"updates_available": []}
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()
        logger.info("Ninja Integration Client closed")


# Global ninja client instance
_ninja_client: Optional[NinjaIntegrationClient] = None


def initialize_ninja_client(
    service_name: str,
    service_version: str,
    ninja_url: str = "http://localhost:8001",
    enable_auto_healing: bool = True
) -> NinjaIntegrationClient:
    """
    Initialize global ninja client
    
    Args:
        service_name: Service name
        service_version: Service version
        ninja_url: Ninja URL
        enable_auto_healing: Enable auto-healing
    
    Returns:
        Ninja client instance
    """
    global _ninja_client
    _ninja_client = NinjaIntegrationClient(service_name, service_version, ninja_url, enable_auto_healing)
    return _ninja_client


def get_ninja_client() -> Optional[NinjaIntegrationClient]:
    """Get global ninja client instance"""
    return _ninja_client