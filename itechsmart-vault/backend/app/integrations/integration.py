"""
Integration with iTechSmart Enterprise Hub and Ninja
"""

import asyncio
import logging
from typing import Optional
import sys
import os

# Add parent directory to path to import integration modules
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

try:
    from itechsmart_enterprise.backend.app.core.hub_integration import (
        HubIntegrationClient,
        initialize_hub_client,
        get_hub_client,
    )
    from itechsmart_ninja.backend.app.core.ninja_integration import (
        NinjaIntegrationClient,
        initialize_ninja_client,
        get_ninja_client,
        ErrorSeverity,
    )

    HUB_AVAILABLE = True
    NINJA_AVAILABLE = True
except ImportError:
    HUB_AVAILABLE = False
    NINJA_AVAILABLE = False
    logging.warning("Hub or Ninja integration modules not available")

logger = logging.getLogger(__name__)


class ProductIntegration:
    """
    Integration manager for iTechSmart products
    Handles Hub and Ninja connectivity
    """

    def __init__(
        self,
        product_name: str,
        product_version: str,
        hub_url: str = "http://localhost:8000",
        ninja_url: str = "http://localhost:8001",
        enable_hub: bool = True,
        enable_ninja: bool = True,
    ):
        self.product_name = product_name
        self.product_version = product_version
        self.hub_url = hub_url
        self.ninja_url = ninja_url
        self.enable_hub = enable_hub
        self.enable_ninja = enable_ninja

        self.hub_client: Optional[HubIntegrationClient] = None
        self.ninja_client: Optional[NinjaIntegrationClient] = None

        self.is_integrated = False

    async def initialize(self, host: str = "localhost", port: int = 8000):
        """
        Initialize integration with Hub and Ninja

        Args:
            host: Service host
            port: Service port
        """
        try:
            # Initialize Hub integration
            if self.enable_hub and HUB_AVAILABLE:
                self.hub_client = initialize_hub_client(
                    service_name=self.product_name,
                    service_version=self.product_version,
                    hub_url=self.hub_url,
                )

                # Register with Hub
                success = await self.hub_client.register_with_hub(
                    host=host,
                    port=port,
                    health_endpoint="/health",
                    capabilities=self._get_capabilities(),
                )

                if success:
                    logger.info(f"{self.product_name} registered with Hub")

                    # Start health and metrics reporting
                    asyncio.create_task(self.hub_client.start_health_reporting(30))
                    asyncio.create_task(self.hub_client.start_metrics_reporting(60))
                else:
                    logger.warning(f"Failed to register {self.product_name} with Hub")

            # Initialize Ninja integration
            if self.enable_ninja and NINJA_AVAILABLE:
                self.ninja_client = initialize_ninja_client(
                    service_name=self.product_name,
                    service_version=self.product_version,
                    ninja_url=self.ninja_url,
                    enable_auto_healing=True,
                )

                # Register with Ninja
                success = await self.ninja_client.register_with_ninja()

                if success:
                    logger.info(f"{self.product_name} registered with Ninja")

                    # Start monitoring
                    asyncio.create_task(self.ninja_client.start_monitoring(60))
                else:
                    logger.warning(f"Failed to register {self.product_name} with Ninja")

            self.is_integrated = True
            logger.info(f"{self.product_name} integration initialized")

        except Exception as e:
            logger.error(f"Error initializing integration: {e}")
            self.is_integrated = False

    def _get_capabilities(self) -> list:
        """Get product capabilities"""
        # Override this in each product to specify capabilities
        return ["api", "health-check", "metrics"]

    async def report_error(
        self,
        error_type: str,
        severity: str,
        message: str,
        stack_trace: Optional[str] = None,
    ):
        """Report error to Ninja"""
        if self.ninja_client and NINJA_AVAILABLE:
            try:
                severity_enum = ErrorSeverity[severity.upper()]
                await self.ninja_client.report_error(
                    error_type=error_type,
                    severity=severity_enum,
                    message=message,
                    stack_trace=stack_trace,
                )
            except Exception as e:
                logger.error(f"Error reporting to Ninja: {e}")

    async def call_service(
        self,
        service_name: str,
        endpoint: str,
        method: str = "GET",
        data: Optional[dict] = None,
    ):
        """Call another service through Hub"""
        if self.hub_client and HUB_AVAILABLE:
            try:
                return await self.hub_client.call_service(
                    service_name=service_name,
                    endpoint=endpoint,
                    method=method,
                    data=data,
                )
            except Exception as e:
                logger.error(f"Error calling service: {e}")
                return None
        return None

    async def shutdown(self):
        """Shutdown integration"""
        try:
            if self.hub_client:
                await self.hub_client.stop_health_reporting()
                await self.hub_client.stop_metrics_reporting()
                await self.hub_client.close()

            if self.ninja_client:
                await self.ninja_client.stop_monitoring()
                await self.ninja_client.close()

            logger.info(f"{self.product_name} integration shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Global integration instance
_integration: Optional[ProductIntegration] = None


def initialize_integration(
    product_name: str,
    product_version: str,
    host: str = "localhost",
    port: int = 8000,
    hub_url: str = "http://localhost:8000",
    ninja_url: str = "http://localhost:8001",
) -> ProductIntegration:
    """
    Initialize product integration

    Args:
        product_name: Product name
        product_version: Product version
        host: Service host
        port: Service port
        hub_url: Hub URL
        ninja_url: Ninja URL

    Returns:
        Integration instance
    """
    global _integration
    _integration = ProductIntegration(
        product_name=product_name,
        product_version=product_version,
        hub_url=hub_url,
        ninja_url=ninja_url,
    )

    # Initialize asynchronously
    asyncio.create_task(_integration.initialize(host, port))

    return _integration


def get_integration() -> Optional[ProductIntegration]:
    """Get global integration instance"""
    return _integration
