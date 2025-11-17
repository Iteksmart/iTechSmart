"""
Prometheus monitoring integration
"""

import asyncio
import logging
from typing import List, Dict, Any, Callable
from datetime import datetime, timedelta
import aiohttp
from prometheus_api_client import PrometheusConnect

from ..core.models import Alert, AlertSource, SeverityLevel


class PrometheusMonitor:
    """Monitor Prometheus metrics and generate alerts"""

    def __init__(self, endpoints: List[str], alert_callback: Callable):
        self.endpoints = endpoints
        self.alert_callback = alert_callback
        self.clients = {}
        self.running = False
        self.logger = logging.getLogger(__name__)

        # Initialize Prometheus clients
        for endpoint in endpoints:
            try:
                self.clients[endpoint] = PrometheusConnect(
                    url=endpoint, disable_ssl=True
                )
                self.logger.info(f"Connected to Prometheus at {endpoint}")
            except Exception as e:
                self.logger.error(f"Failed to connect to Prometheus at {endpoint}: {e}")

    async def start(self):
        """Start monitoring Prometheus metrics"""
        self.running = True
        self.logger.info("Starting Prometheus monitoring...")

        tasks = [
            self.monitor_cpu_usage(),
            self.monitor_memory_usage(),
            self.monitor_disk_usage(),
            self.monitor_service_health(),
            self.monitor_network_metrics(),
        ]

        await asyncio.gather(*tasks)

    async def stop(self):
        """Stop monitoring"""
        self.running = False
        self.logger.info("Stopping Prometheus monitoring...")

    async def monitor_cpu_usage(self):
        """Monitor CPU usage across all hosts"""
        while self.running:
            try:
                for endpoint, client in self.clients.items():
                    # Query for high CPU usage
                    query = '100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'

                    try:
                        result = client.custom_query(query=query)

                        for metric in result:
                            cpu_usage = float(metric["value"][1])
                            instance = metric["metric"].get("instance", "unknown")

                            if cpu_usage > 80:  # High CPU threshold
                                alert = Alert(
                                    source=AlertSource.PROMETHEUS,
                                    severity=(
                                        SeverityLevel.HIGH
                                        if cpu_usage > 90
                                        else SeverityLevel.MEDIUM
                                    ),
                                    message=f"High CPU usage detected: {cpu_usage:.2f}%",
                                    host=instance,
                                    metrics={
                                        "cpu_usage": cpu_usage,
                                        "threshold": 80,
                                        "metric_type": "cpu",
                                    },
                                    raw_data=metric,
                                    tags=["cpu", "performance"],
                                )
                                await self.alert_callback(alert)

                    except Exception as e:
                        self.logger.error(f"Error querying CPU metrics: {e}")

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"CPU monitoring error: {e}")
                await asyncio.sleep(60)

    async def monitor_memory_usage(self):
        """Monitor memory usage across all hosts"""
        while self.running:
            try:
                for endpoint, client in self.clients.items():
                    # Query for memory usage
                    query = "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100"

                    try:
                        result = client.custom_query(query=query)

                        for metric in result:
                            memory_usage = float(metric["value"][1])
                            instance = metric["metric"].get("instance", "unknown")

                            if memory_usage > 85:  # High memory threshold
                                alert = Alert(
                                    source=AlertSource.PROMETHEUS,
                                    severity=(
                                        SeverityLevel.HIGH
                                        if memory_usage > 95
                                        else SeverityLevel.MEDIUM
                                    ),
                                    message=f"High memory usage detected: {memory_usage:.2f}%",
                                    host=instance,
                                    metrics={
                                        "memory_usage": memory_usage,
                                        "threshold": 85,
                                        "metric_type": "memory",
                                    },
                                    raw_data=metric,
                                    tags=["memory", "performance"],
                                )
                                await self.alert_callback(alert)

                    except Exception as e:
                        self.logger.error(f"Error querying memory metrics: {e}")

                await asyncio.sleep(30)

            except Exception as e:
                self.logger.error(f"Memory monitoring error: {e}")
                await asyncio.sleep(60)

    async def monitor_disk_usage(self):
        """Monitor disk usage across all hosts"""
        while self.running:
            try:
                for endpoint, client in self.clients.items():
                    # Query for disk usage
                    query = '(1 - (node_filesystem_avail_bytes{fstype!="tmpfs"} / node_filesystem_size_bytes{fstype!="tmpfs"})) * 100'

                    try:
                        result = client.custom_query(query=query)

                        for metric in result:
                            disk_usage = float(metric["value"][1])
                            instance = metric["metric"].get("instance", "unknown")
                            mountpoint = metric["metric"].get("mountpoint", "/")

                            if disk_usage > 80:  # High disk threshold
                                alert = Alert(
                                    source=AlertSource.PROMETHEUS,
                                    severity=(
                                        SeverityLevel.HIGH
                                        if disk_usage > 90
                                        else SeverityLevel.MEDIUM
                                    ),
                                    message=f"High disk usage detected on {mountpoint}: {disk_usage:.2f}%",
                                    host=instance,
                                    metrics={
                                        "disk_usage": disk_usage,
                                        "mountpoint": mountpoint,
                                        "threshold": 80,
                                        "metric_type": "disk",
                                    },
                                    raw_data=metric,
                                    tags=["disk", "storage"],
                                )
                                await self.alert_callback(alert)

                    except Exception as e:
                        self.logger.error(f"Error querying disk metrics: {e}")

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Disk monitoring error: {e}")
                await asyncio.sleep(60)

    async def monitor_service_health(self):
        """Monitor service health and availability"""
        while self.running:
            try:
                for endpoint, client in self.clients.items():
                    # Query for service down
                    query = "up == 0"

                    try:
                        result = client.custom_query(query=query)

                        for metric in result:
                            instance = metric["metric"].get("instance", "unknown")
                            job = metric["metric"].get("job", "unknown")

                            alert = Alert(
                                source=AlertSource.PROMETHEUS,
                                severity=SeverityLevel.CRITICAL,
                                message=f"Service down: {job} on {instance}",
                                host=instance,
                                metrics={
                                    "service": job,
                                    "status": "down",
                                    "metric_type": "availability",
                                },
                                raw_data=metric,
                                tags=["service", "availability", "critical"],
                            )
                            await self.alert_callback(alert)

                    except Exception as e:
                        self.logger.error(f"Error querying service health: {e}")

                await asyncio.sleep(30)

            except Exception as e:
                self.logger.error(f"Service health monitoring error: {e}")
                await asyncio.sleep(60)

    async def monitor_network_metrics(self):
        """Monitor network metrics"""
        while self.running:
            try:
                for endpoint, client in self.clients.items():
                    # Query for high network errors
                    query = "rate(node_network_receive_errs_total[5m]) > 10"

                    try:
                        result = client.custom_query(query=query)

                        for metric in result:
                            error_rate = float(metric["value"][1])
                            instance = metric["metric"].get("instance", "unknown")
                            device = metric["metric"].get("device", "unknown")

                            alert = Alert(
                                source=AlertSource.PROMETHEUS,
                                severity=SeverityLevel.HIGH,
                                message=f"High network errors on {device}: {error_rate:.2f} errors/sec",
                                host=instance,
                                metrics={
                                    "error_rate": error_rate,
                                    "device": device,
                                    "metric_type": "network",
                                },
                                raw_data=metric,
                                tags=["network", "errors"],
                            )
                            await self.alert_callback(alert)

                    except Exception as e:
                        self.logger.error(f"Error querying network metrics: {e}")

                await asyncio.sleep(60)

            except Exception as e:
                self.logger.error(f"Network monitoring error: {e}")
                await asyncio.sleep(60)

    async def query_custom_metric(self, query: str) -> List[Dict[str, Any]]:
        """Execute custom Prometheus query"""
        results = []

        for endpoint, client in self.clients.items():
            try:
                result = client.custom_query(query=query)
                results.extend(result)
            except Exception as e:
                self.logger.error(f"Error executing custom query: {e}")

        return results
