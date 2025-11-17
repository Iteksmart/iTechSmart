"""
iTechSmart Enterprise Hub - Integration Module
This module provides integration capabilities for all iTechSmart products
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)


@dataclass
class ServiceRegistration:
    """Service registration information"""

    service_id: str
    service_name: str
    version: str
    host: str
    port: int
    health_endpoint: str
    capabilities: List[str]
    registered_at: datetime


@dataclass
class HealthReport:
    """Service health report"""

    service_id: str
    status: str  # healthy, degraded, unhealthy
    uptime: float
    cpu_usage: float
    memory_usage: float
    active_connections: int
    error_count: int
    timestamp: datetime


@dataclass
class MetricsReport:
    """Service metrics report"""

    service_id: str
    requests_per_minute: int
    average_response_time: float
    error_rate: float
    active_users: int
    custom_metrics: Dict[str, Any]
    timestamp: datetime


class HubIntegrationClient:
    """
    Hub Integration Client for iTechSmart Products

    This client enables any iTechSmart product to:
    - Register with the Enterprise Hub
    - Report health status
    - Send metrics
    - Communicate with other products
    - Receive configuration updates
    """

    def __init__(
        self,
        service_name: str,
        service_version: str,
        hub_url: str = "http://localhost:8000",
        enable_auto_registration: bool = True,
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.hub_url = hub_url
        self.service_id = f"{service_name}_{datetime.now().timestamp()}"
        self.enable_auto_registration = enable_auto_registration

        self.is_registered = False
        self.health_reporting_active = False
        self.metrics_reporting_active = False

        self.client = httpx.AsyncClient(timeout=30.0)

        logger.info(f"Hub Integration Client initialized for {service_name}")

    async def register_with_hub(
        self,
        host: str,
        port: int,
        health_endpoint: str = "/health",
        capabilities: Optional[List[str]] = None,
    ) -> bool:
        """
        Register service with Enterprise Hub

        Args:
            host: Service host
            port: Service port
            health_endpoint: Health check endpoint
            capabilities: List of service capabilities

        Returns:
            True if registration successful
        """
        try:
            registration = ServiceRegistration(
                service_id=self.service_id,
                service_name=self.service_name,
                version=self.service_version,
                host=host,
                port=port,
                health_endpoint=health_endpoint,
                capabilities=capabilities or [],
                registered_at=datetime.now(),
            )

            response = await self.client.post(
                f"{self.hub_url}/api/services/register",
                json={
                    "service_id": registration.service_id,
                    "service_name": registration.service_name,
                    "version": registration.version,
                    "host": registration.host,
                    "port": registration.port,
                    "health_endpoint": registration.health_endpoint,
                    "capabilities": registration.capabilities,
                    "registered_at": registration.registered_at.isoformat(),
                },
            )

            if response.status_code == 200:
                self.is_registered = True
                logger.info(f"Successfully registered {self.service_name} with Hub")
                return True
            else:
                logger.error(f"Failed to register with Hub: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error registering with Hub: {e}")
            return False

    async def report_health(
        self,
        status: str,
        uptime: float,
        cpu_usage: float,
        memory_usage: float,
        active_connections: int = 0,
        error_count: int = 0,
    ) -> bool:
        """
        Report health status to Hub

        Args:
            status: Service status (healthy, degraded, unhealthy)
            uptime: Service uptime in seconds
            cpu_usage: CPU usage percentage
            memory_usage: Memory usage percentage
            active_connections: Number of active connections
            error_count: Number of errors

        Returns:
            True if report successful
        """
        try:
            health_report = HealthReport(
                service_id=self.service_id,
                status=status,
                uptime=uptime,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                active_connections=active_connections,
                error_count=error_count,
                timestamp=datetime.now(),
            )

            response = await self.client.post(
                f"{self.hub_url}/api/services/health",
                json={
                    "service_id": health_report.service_id,
                    "status": health_report.status,
                    "uptime": health_report.uptime,
                    "cpu_usage": health_report.cpu_usage,
                    "memory_usage": health_report.memory_usage,
                    "active_connections": health_report.active_connections,
                    "error_count": health_report.error_count,
                    "timestamp": health_report.timestamp.isoformat(),
                },
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Error reporting health to Hub: {e}")
            return False

    async def report_metrics(
        self,
        requests_per_minute: int,
        average_response_time: float,
        error_rate: float,
        active_users: int = 0,
        custom_metrics: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Report metrics to Hub

        Args:
            requests_per_minute: Requests per minute
            average_response_time: Average response time in ms
            error_rate: Error rate percentage
            active_users: Number of active users
            custom_metrics: Custom metrics dictionary

        Returns:
            True if report successful
        """
        try:
            metrics_report = MetricsReport(
                service_id=self.service_id,
                requests_per_minute=requests_per_minute,
                average_response_time=average_response_time,
                error_rate=error_rate,
                active_users=active_users,
                custom_metrics=custom_metrics or {},
                timestamp=datetime.now(),
            )

            response = await self.client.post(
                f"{self.hub_url}/api/services/metrics",
                json={
                    "service_id": metrics_report.service_id,
                    "requests_per_minute": metrics_report.requests_per_minute,
                    "average_response_time": metrics_report.average_response_time,
                    "error_rate": metrics_report.error_rate,
                    "active_users": metrics_report.active_users,
                    "custom_metrics": metrics_report.custom_metrics,
                    "timestamp": metrics_report.timestamp.isoformat(),
                },
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Error reporting metrics to Hub: {e}")
            return False

    async def start_health_reporting(self, interval_seconds: int = 30):
        """
        Start automatic health reporting

        Args:
            interval_seconds: Reporting interval in seconds
        """
        self.health_reporting_active = True
        logger.info(f"Started health reporting every {interval_seconds} seconds")

        while self.health_reporting_active:
            try:
                # Get system metrics (simplified)
                await self.report_health(
                    status="healthy",
                    uptime=0.0,  # Should be calculated
                    cpu_usage=0.0,  # Should be measured
                    memory_usage=0.0,  # Should be measured
                    active_connections=0,
                    error_count=0,
                )

                await asyncio.sleep(interval_seconds)

            except Exception as e:
                logger.error(f"Error in health reporting loop: {e}")
                await asyncio.sleep(interval_seconds)

    async def start_metrics_reporting(self, interval_seconds: int = 60):
        """
        Start automatic metrics reporting

        Args:
            interval_seconds: Reporting interval in seconds
        """
        self.metrics_reporting_active = True
        logger.info(f"Started metrics reporting every {interval_seconds} seconds")

        while self.metrics_reporting_active:
            try:
                # Get metrics (simplified)
                await self.report_metrics(
                    requests_per_minute=0,  # Should be measured
                    average_response_time=0.0,  # Should be measured
                    error_rate=0.0,  # Should be calculated
                    active_users=0,
                    custom_metrics={},
                )

                await asyncio.sleep(interval_seconds)

            except Exception as e:
                logger.error(f"Error in metrics reporting loop: {e}")
                await asyncio.sleep(interval_seconds)

    async def stop_health_reporting(self):
        """Stop automatic health reporting"""
        self.health_reporting_active = False
        logger.info("Stopped health reporting")

    async def stop_metrics_reporting(self):
        """Stop automatic metrics reporting"""
        self.metrics_reporting_active = False
        logger.info("Stopped metrics reporting")

    async def get_service_info(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about another service

        Args:
            service_name: Name of the service

        Returns:
            Service information or None
        """
        try:
            response = await self.client.get(
                f"{self.hub_url}/api/services/{service_name}"
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting service info: {e}")
            return None

    async def call_service(
        self,
        service_name: str,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Call another service through the Hub

        Args:
            service_name: Target service name
            endpoint: Service endpoint
            method: HTTP method
            data: Request data

        Returns:
            Response data or None
        """
        try:
            # Get service info from Hub
            service_info = await self.get_service_info(service_name)

            if not service_info:
                logger.error(f"Service {service_name} not found")
                return None

            # Make request to service
            service_url = (
                f"http://{service_info['host']}:{service_info['port']}{endpoint}"
            )

            if method == "GET":
                response = await self.client.get(service_url)
            elif method == "POST":
                response = await self.client.post(service_url, json=data)
            elif method == "PUT":
                response = await self.client.put(service_url, json=data)
            elif method == "DELETE":
                response = await self.client.delete(service_url)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Service call failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error calling service: {e}")
            return None

    async def get_configuration(self) -> Optional[Dict[str, Any]]:
        """
        Get configuration from Hub

        Returns:
            Configuration dictionary or None
        """
        try:
            response = await self.client.get(
                f"{self.hub_url}/api/services/{self.service_id}/config"
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting configuration: {e}")
            return None

    async def close(self):
        """Close the client"""
        await self.client.aclose()
        logger.info("Hub Integration Client closed")


# Global hub client instance
_hub_client: Optional[HubIntegrationClient] = None


def initialize_hub_client(
    service_name: str, service_version: str, hub_url: str = "http://localhost:8000"
) -> HubIntegrationClient:
    """
    Initialize global hub client

    Args:
        service_name: Service name
        service_version: Service version
        hub_url: Hub URL

    Returns:
        Hub client instance
    """
    global _hub_client
    _hub_client = HubIntegrationClient(service_name, service_version, hub_url)
    return _hub_client


def get_hub_client() -> Optional[HubIntegrationClient]:
    """Get global hub client instance"""
    return _hub_client
