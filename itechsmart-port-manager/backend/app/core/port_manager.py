"""
Port Manager Core - Handles port allocation, conflict detection, and management
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from pathlib import Path
import socket

logger = logging.getLogger(__name__)


class PortManager:
    """
    Core port management system for iTechSmart Suite
    Handles dynamic port allocation, conflict detection, and configuration
    """

    def __init__(self, config_file: str = "port_config.json"):
        self.config_file = Path(config_file)
        self.port_assignments: Dict[str, int] = {}
        self.port_history: Dict[str, List[int]] = {}
        self.reserved_ports: Set[int] = set()
        self.port_range = (8000, 9000)  # Default port range
        self.lock = asyncio.Lock()

        # Default port assignments for all 26 iTechSmart products
        self.default_ports = {
            # Foundation Products
            "itechsmart-enterprise": 8001,
            "itechsmart-ninja": 8002,
            "itechsmart-analytics": 8003,
            "itechsmart-supreme": 8004,
            "itechsmart-hl7": 8005,
            "prooflink-ai": 8006,
            "passport": 8007,
            "impactos": 8008,
            "legalai-pro": 8000,
            # Strategic Products
            "itechsmart-dataflow": 8010,
            "itechsmart-pulse": 8011,
            "itechsmart-connect": 8012,
            "itechsmart-vault": 8013,
            "itechsmart-notify": 8014,
            "itechsmart-ledger": 8015,
            "itechsmart-copilot": 8016,
            "itechsmart-shield": 8017,
            "itechsmart-workflow": 8018,
            "itechsmart-marketplace": 8019,
            # Business Products
            "itechsmart-cloud": 8020,
            "itechsmart-devops": 8021,
            "itechsmart-mobile": 8022,
            "itechsmart-ai": 8023,
            "itechsmart-compliance": 8024,
            "itechsmart-data-platform": 8025,
            "itechsmart-customer-success": 8026,
            # Port Manager itself
            "itechsmart-port-manager": 8100,
        }

    async def initialize(self):
        """Initialize port manager and load configuration"""
        logger.info("Initializing Port Manager...")

        # Load existing configuration or use defaults
        if self.config_file.exists():
            await self.load_configuration()
        else:
            self.port_assignments = self.default_ports.copy()
            await self.save_configuration()

        # Initialize port history
        for service in self.port_assignments:
            if service not in self.port_history:
                self.port_history[service] = [self.port_assignments[service]]

        logger.info(
            f"Port Manager initialized with {len(self.port_assignments)} services"
        )

    async def load_configuration(self):
        """Load port configuration from file"""
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
                self.port_assignments = config.get(
                    "port_assignments", self.default_ports
                )
                self.port_history = config.get("port_history", {})
                self.reserved_ports = set(config.get("reserved_ports", []))
                logger.info(f"Loaded configuration from {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.port_assignments = self.default_ports.copy()

    async def save_configuration(self):
        """Save port configuration to file"""
        try:
            config = {
                "port_assignments": self.port_assignments,
                "port_history": self.port_history,
                "reserved_ports": list(self.reserved_ports),
                "last_updated": datetime.utcnow().isoformat(),
            }
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
            logger.info(f"Saved configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def is_port_available(self, port: int) -> bool:
        """Check if a port is available on the system"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", port))
                return True
        except OSError:
            return False

    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is already assigned to a service"""
        return port in self.port_assignments.values()

    async def find_available_port(
        self, start_port: int = None, exclude_ports: Set[int] = None
    ) -> Optional[int]:
        """Find an available port in the configured range"""
        if start_port is None:
            start_port = self.port_range[0]

        if exclude_ports is None:
            exclude_ports = set()

        # Combine reserved ports and excluded ports
        unavailable_ports = (
            self.reserved_ports | exclude_ports | set(self.port_assignments.values())
        )

        for port in range(start_port, self.port_range[1]):
            if port not in unavailable_ports and self.is_port_available(port):
                return port

        return None

    async def assign_port(
        self, service_id: str, port: int = None, force: bool = False
    ) -> Tuple[bool, int, str]:
        """
        Assign a port to a service
        Returns: (success, port, message)
        """
        async with self.lock:
            # If no port specified, find an available one
            if port is None:
                port = await self.find_available_port()
                if port is None:
                    return False, 0, "No available ports in range"

            # Check if port is available
            if not force:
                if not self.is_port_available(port):
                    return False, port, f"Port {port} is already in use by system"

                if self.is_port_in_use(port):
                    current_service = next(
                        (s for s, p in self.port_assignments.items() if p == port), None
                    )
                    return (
                        False,
                        port,
                        f"Port {port} is already assigned to {current_service}",
                    )

            # Assign the port
            old_port = self.port_assignments.get(service_id)
            self.port_assignments[service_id] = port

            # Update history
            if service_id not in self.port_history:
                self.port_history[service_id] = []
            self.port_history[service_id].append(port)

            # Save configuration
            await self.save_configuration()

            message = f"Assigned port {port} to {service_id}"
            if old_port:
                message += f" (previously {old_port})"

            logger.info(message)
            return True, port, message

    async def reassign_port(
        self, service_id: str, new_port: int = None
    ) -> Tuple[bool, int, str]:
        """
        Reassign a service to a different port
        Returns: (success, new_port, message)
        """
        if service_id not in self.port_assignments:
            return False, 0, f"Service {service_id} not found"

        old_port = self.port_assignments[service_id]

        # If no new port specified, find an available one
        if new_port is None:
            new_port = await self.find_available_port(exclude_ports={old_port})
            if new_port is None:
                return False, 0, "No available ports for reassignment"

        # Assign the new port
        success, port, message = await self.assign_port(service_id, new_port)

        if success:
            return True, port, f"Reassigned {service_id} from port {old_port} to {port}"
        else:
            return False, 0, message

    async def detect_conflicts(self) -> List[Dict]:
        """Detect port conflicts across all services"""
        conflicts = []

        # Check for duplicate port assignments
        port_usage = {}
        for service, port in self.port_assignments.items():
            if port not in port_usage:
                port_usage[port] = []
            port_usage[port].append(service)

        for port, services in port_usage.items():
            if len(services) > 1:
                conflicts.append(
                    {
                        "type": "duplicate_assignment",
                        "port": port,
                        "services": services,
                        "severity": "high",
                    }
                )

        # Check for system-level conflicts
        for service, port in self.port_assignments.items():
            if not self.is_port_available(port):
                conflicts.append(
                    {
                        "type": "system_conflict",
                        "port": port,
                        "service": service,
                        "severity": "critical",
                    }
                )

        return conflicts

    async def resolve_conflicts(self) -> List[Dict]:
        """Automatically resolve detected conflicts"""
        conflicts = await self.detect_conflicts()
        resolutions = []

        for conflict in conflicts:
            if conflict["type"] == "duplicate_assignment":
                # Keep first service, reassign others
                services = conflict["services"]
                for service in services[1:]:
                    success, new_port, message = await self.reassign_port(service)
                    resolutions.append(
                        {
                            "service": service,
                            "old_port": conflict["port"],
                            "new_port": new_port,
                            "success": success,
                            "message": message,
                        }
                    )

            elif conflict["type"] == "system_conflict":
                # Reassign to available port
                service = conflict["service"]
                success, new_port, message = await self.reassign_port(service)
                resolutions.append(
                    {
                        "service": service,
                        "old_port": conflict["port"],
                        "new_port": new_port,
                        "success": success,
                        "message": message,
                    }
                )

        return resolutions

    async def get_service_port(self, service_id: str) -> Optional[int]:
        """Get the current port for a service"""
        return self.port_assignments.get(service_id)

    async def get_all_assignments(self) -> Dict[str, int]:
        """Get all current port assignments"""
        return self.port_assignments.copy()

    async def get_service_history(self, service_id: str) -> List[int]:
        """Get port history for a service"""
        return self.port_history.get(service_id, [])

    async def reserve_port(self, port: int) -> bool:
        """Reserve a port to prevent assignment"""
        if port in self.reserved_ports:
            return False

        self.reserved_ports.add(port)
        await self.save_configuration()
        return True

    async def unreserve_port(self, port: int) -> bool:
        """Remove port reservation"""
        if port not in self.reserved_ports:
            return False

        self.reserved_ports.remove(port)
        await self.save_configuration()
        return True

    async def get_port_statistics(self) -> Dict:
        """Get statistics about port usage"""
        total_services = len(self.port_assignments)
        used_ports = len(set(self.port_assignments.values()))
        available_ports = sum(
            1
            for p in range(self.port_range[0], self.port_range[1])
            if self.is_port_available(p) and not self.is_port_in_use(p)
        )

        return {
            "total_services": total_services,
            "used_ports": used_ports,
            "available_ports": available_ports,
            "reserved_ports": len(self.reserved_ports),
            "port_range": self.port_range,
            "conflicts": len(await self.detect_conflicts()),
        }

    async def backup_configuration(self, backup_file: str = None) -> str:
        """Create a backup of current configuration"""
        if backup_file is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_file = f"port_config_backup_{timestamp}.json"

        config = {
            "port_assignments": self.port_assignments,
            "port_history": self.port_history,
            "reserved_ports": list(self.reserved_ports),
            "backup_timestamp": datetime.utcnow().isoformat(),
        }

        with open(backup_file, "w") as f:
            json.dump(config, f, indent=2)

        logger.info(f"Configuration backed up to {backup_file}")
        return backup_file

    async def restore_configuration(self, backup_file: str) -> bool:
        """Restore configuration from backup"""
        try:
            with open(backup_file, "r") as f:
                config = json.load(f)
                self.port_assignments = config.get("port_assignments", {})
                self.port_history = config.get("port_history", {})
                self.reserved_ports = set(config.get("reserved_ports", []))

            await self.save_configuration()
            logger.info(f"Configuration restored from {backup_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore configuration: {e}")
            return False

    async def reset_to_defaults(self) -> bool:
        """Reset all port assignments to defaults"""
        self.port_assignments = self.default_ports.copy()
        self.port_history = {
            service: [port] for service, port in self.default_ports.items()
        }
        self.reserved_ports = set()
        await self.save_configuration()
        logger.info("Port assignments reset to defaults")
        return True

    async def shutdown(self):
        """Shutdown port manager"""
        await self.save_configuration()
        logger.info("Port Manager shutdown complete")
