"""
iTechSmart Supreme - Main Entry Point
Self-Healing Infrastructure Platform
"""

import asyncio
import logging
import signal
import sys
from typing import Optional
import yaml
from pathlib import Path

from core.auto_remediation_engine import AutoRemediationEngine, RemediationMode
from core.vm_provisioner import VMProvisioner
from core.domain_admin_manager import DomainAdminManager
from execution.network_device_manager import NetworkDeviceManager
from use_cases.use_case_manager import UseCaseManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/supreme.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


class iTechSmartSupreme:
    """
    Main application class for iTechSmart Supreme

    Orchestrates all components:
    - Auto-remediation engine
    - VM provisioning
    - Domain admin management
    - Network device management
    - Use case implementations
    """

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.running = False

        # Initialize components
        self.engine: Optional[AutoRemediationEngine] = None
        self.vm_provisioner: Optional[VMProvisioner] = None
        self.domain_manager: Optional[DomainAdminManager] = None
        self.network_manager: Optional[NetworkDeviceManager] = None
        self.use_case_manager: Optional[UseCaseManager] = None

        logger.info("🚀 iTechSmart Supreme initialized")

    def _load_config(self) -> dict:
        """Load configuration from YAML file"""

        config_file = Path(self.config_path)

        if not config_file.exists():
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            return self._default_config()

        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)
                logger.info(f"✅ Configuration loaded from {self.config_path}")
                return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self._default_config()

    def _default_config(self) -> dict:
        """Return default configuration"""
        return {
            "mode": "semi_auto",
            "monitoring": {
                "prometheus": {"endpoints": ["http://localhost:9090"]},
                "wazuh": {"endpoints": []},
            },
            "cloud": {},
            "domain": {},
            "logging": {"level": "INFO", "file": "logs/supreme.log"},
        }

    async def initialize(self):
        """Initialize all components"""

        logger.info("🔧 Initializing components...")

        # Determine remediation mode
        mode_str = self.config.get("mode", "semi_auto")
        mode = RemediationMode[mode_str.upper()]

        # Initialize auto-remediation engine
        prometheus_endpoints = (
            self.config.get("monitoring", {}).get("prometheus", {}).get("endpoints", [])
        )
        wazuh_endpoints = (
            self.config.get("monitoring", {}).get("wazuh", {}).get("endpoints", [])
        )
        ai_api_key = self.config.get("ai", {}).get("api_key")

        self.engine = AutoRemediationEngine(
            prometheus_endpoints=prometheus_endpoints,
            wazuh_endpoints=wazuh_endpoints,
            ai_api_key=ai_api_key,
            mode=mode,
        )

        logger.info(f"✅ Auto-remediation engine initialized (Mode: {mode.value})")

        # Initialize VM provisioner
        cloud_config = self.config.get("cloud", {})
        if cloud_config:
            self.vm_provisioner = VMProvisioner(cloud_config)
            logger.info("✅ VM provisioner initialized")

        # Initialize domain admin manager
        domain_config = self.config.get("domain", {})
        if domain_config:
            self.domain_manager = DomainAdminManager(domain_config)
            await self.domain_manager.connect_domain()
            logger.info("✅ Domain admin manager initialized")

        # Initialize network device manager
        self.network_manager = NetworkDeviceManager()
        logger.info("✅ Network device manager initialized")

        # Initialize use case manager
        self.use_case_manager = UseCaseManager()
        logger.info("✅ Use case manager initialized")

        logger.info("🎉 All components initialized successfully")

    async def start(self):
        """Start the self-healing platform"""

        self.running = True

        logger.info("=" * 80)
        logger.info("🚀 Starting iTechSmart Supreme - Self-Healing Infrastructure")
        logger.info("=" * 80)

        # Initialize components
        await self.initialize()

        # Start background tasks
        tasks = []

        # Start auto-remediation engine
        if self.engine:
            tasks.append(asyncio.create_task(self.engine.start()))
            logger.info("✅ Auto-remediation engine started")

        # Start VM cleanup task
        if self.vm_provisioner:
            tasks.append(asyncio.create_task(self._vm_cleanup_loop()))
            logger.info("✅ VM cleanup task started")

        # Start domain account cleanup task
        if self.domain_manager:
            tasks.append(asyncio.create_task(self._domain_cleanup_loop()))
            logger.info("✅ Domain account cleanup task started")

        logger.info("=" * 80)
        logger.info("✅ iTechSmart Supreme is now running!")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📊 Statistics:")
        logger.info(f"   Mode: {self.engine.mode.value if self.engine else 'N/A'}")
        logger.info(
            f"   Prometheus: {len(self.engine.prometheus.endpoints) if self.engine else 0} endpoints"
        )
        logger.info(
            f"   Wazuh: {len(self.engine.wazuh.endpoints) if self.engine else 0} endpoints"
        )
        logger.info("")
        logger.info("🎯 Monitoring for incidents...")
        logger.info("")

        # Wait for all tasks
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Shutting down...")

    async def stop(self):
        """Stop the platform"""

        self.running = False

        logger.info("🛑 Stopping iTechSmart Supreme...")

        # Stop auto-remediation engine
        if self.engine:
            await self.engine.stop()
            logger.info("✅ Auto-remediation engine stopped")

        # Disconnect network devices
        if self.network_manager:
            await self.network_manager.disconnect_all()
            logger.info("✅ Network devices disconnected")

        logger.info("✅ iTechSmart Supreme stopped")

    async def _vm_cleanup_loop(self):
        """Background task to cleanup expired VMs"""

        while self.running:
            try:
                if self.vm_provisioner:
                    await self.vm_provisioner.cleanup_expired_vms()
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"VM cleanup error: {e}")
                await asyncio.sleep(60)

    async def _domain_cleanup_loop(self):
        """Background task to cleanup expired domain accounts"""

        while self.running:
            try:
                if self.domain_manager:
                    await self.domain_manager.cleanup_expired_accounts()
                    await self.domain_manager.auto_rotate_accounts()
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"Domain cleanup error: {e}")
                await asyncio.sleep(60)

    def get_statistics(self) -> dict:
        """Get platform statistics"""

        stats = {
            "running": self.running,
            "mode": self.engine.mode.value if self.engine else "unknown",
        }

        if self.engine:
            stats["engine"] = self.engine.get_statistics()

        if self.vm_provisioner:
            stats["vms"] = self.vm_provisioner.get_statistics()

        if self.domain_manager:
            stats["domain_accounts"] = self.domain_manager.get_statistics()

        if self.use_case_manager:
            stats["use_cases"] = self.use_case_manager.get_statistics()

        return stats


async def main():
    """Main entry point"""

    # Create logs directory
    Path("logs").mkdir(exist_ok=True)

    # Initialize platform
    supreme = iTechSmartSupreme()

    # Setup signal handlers
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        asyncio.create_task(supreme.stop())
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start platform
    try:
        await supreme.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        await supreme.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        await supreme.stop()
        sys.exit(1)


if __name__ == "__main__":
    # Run the platform
    asyncio.run(main())
