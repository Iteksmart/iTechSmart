"""
iTechSmart Edge Computing Configuration

Configuration settings for edge computing services and node management.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import os
from enum import Enum


class NodeStatus(Enum):
    """Node status values."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    OFFLINE = "offline"


class OptimizationPolicy(Enum):
    """Resource optimization policies."""

    LOAD_BALANCING = "load_balancing"
    LATENCY_OPTIMIZATION = "latency_optimization"
    THROUGHPUT_MAXIMIZATION = "throughput_maximization"
    ENERGY_EFFICIENCY = "energy_efficiency"
    FAULT_TOLERANCE = "fault_tolerance"


@dataclass
class EdgeNodeConfig:
    """Configuration for an edge computing node."""

    node_id: str
    name: str
    node_type: str
    ip_address: str
    port: int
    cpu_cores: int
    memory_gb: int
    storage_gb: int
    capabilities: List[str]
    gpu_accelerated: bool = False
    gpu_memory_gb: int = 0
    network_bandwidth_mbps: int = 1000
    max_concurrent_tasks: int = 10
    health_check_interval: int = 30
    metrics_collection_interval: int = 10
    auto_scaling_enabled: bool = False
    auto_scale_min_nodes: int = 1
    auto_scale_max_nodes: int = 5
    auto_scale_cpu_threshold: float = 80.0
    auto_scale_memory_threshold: float = 80.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "node_id": self.node_id,
            "name": self.name,
            "node_type": self.node_type,
            "ip_address": self.ip_address,
            "port": self.port,
            "cpu_cores": self.cpu_cores,
            "memory_gb": self.memory_gb,
            "storage_gb": self.storage_gb,
            "capabilities": self.capabilities,
            "gpu_accelerated": self.gpu_accelerated,
            "gpu_memory_gb": self.gpu_memory_gb,
            "network_bandwidth_mbps": self.network_bandwidth_mbps,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "health_check_interval": self.health_check_interval,
            "metrics_collection_interval": self.metrics_collection_interval,
            "auto_scaling_enabled": self.auto_scaling_enabled,
            "auto_scale_min_nodes": self.auto_scale_min_nodes,
            "auto_scale_max_nodes": self.auto_scale_max_nodes,
            "auto_scale_cpu_threshold": self.auto_scale_cpu_threshold,
            "auto_scale_memory_threshold": self.auto_scale_memory_threshold,
        }


@dataclass
class TaskSchedulingConfig:
    """Configuration for task scheduling."""

    default_timeout_minutes: int = 60
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 30
    scheduling_interval_seconds: int = 5
    task_queue_max_size: int = 1000
    load_balancing_algorithm: str = "round_robin"  # round_robin, least_loaded, weighted
    enable_task_prioritization: bool = True
    enable_dependency_resolution: bool = True
    enable_task_affinity: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "default_timeout_minutes": self.default_timeout_minutes,
            "max_retry_attempts": self.max_retry_attempts,
            "retry_delay_seconds": self.retry_delay_seconds,
            "scheduling_interval_seconds": self.scheduling_interval_seconds,
            "task_queue_max_size": self.task_queue_max_size,
            "load_balancing_algorithm": self.load_balancing_algorithm,
            "enable_task_prioritization": self.enable_task_prioritization,
            "enable_dependency_resolution": self.enable_dependency_resolution,
            "enable_task_affinity": self.enable_task_affinity,
        }


@dataclass
class ResourceMonitoringConfig:
    """Configuration for resource monitoring."""

    metrics_retention_hours: int = 24
    metrics_aggregation_interval_seconds: int = 60
    alert_cpu_threshold: float = 90.0
    alert_memory_threshold: float = 90.0
    alert_storage_threshold: float = 95.0
    alert_temperature_threshold: float = 80.0
    enable_predictive_alerts: bool = True
    predictive_alert_window_minutes: int = 15
    performance_history_days: int = 7

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metrics_retention_hours": self.metrics_retention_hours,
            "metrics_aggregation_interval_seconds": self.metrics_aggregation_interval_seconds,
            "alert_cpu_threshold": self.alert_cpu_threshold,
            "alert_memory_threshold": self.alert_memory_threshold,
            "alert_storage_threshold": self.alert_storage_threshold,
            "alert_temperature_threshold": self.alert_temperature_threshold,
            "enable_predictive_alerts": self.enable_predictive_alerts,
            "predictive_alert_window_minutes": self.predictive_alert_window_minutes,
            "performance_history_days": self.performance_history_days,
        }


@dataclass
class SecurityConfig:
    """Configuration for edge computing security."""

    enable_encryption: bool = True
    encryption_algorithm: str = "AES-256-GCM"
    enable_authentication: bool = True
    authentication_method: str = "jwt"
    token_expiry_hours: int = 24
    enable_authorization: bool = True
    role_based_access: bool = True
    audit_logging_enabled: bool = True
    audit_log_retention_days: int = 30
    enable_intrusion_detection: bool = True
    firewall_rules: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "enable_encryption": self.enable_encryption,
            "encryption_algorithm": self.encryption_algorithm,
            "enable_authentication": self.enable_authentication,
            "authentication_method": self.authentication_method,
            "token_expiry_hours": self.token_expiry_hours,
            "enable_authorization": self.enable_authorization,
            "role_based_access": self.role_based_access,
            "audit_logging_enabled": self.audit_logging_enabled,
            "audit_log_retention_days": self.audit_log_retention_days,
            "enable_intrusion_detection": self.enable_intrusion_detection,
            "firewall_rules": self.firewall_rules,
        }


@dataclass
class NetworkConfig:
    """Configuration for edge network management."""

    enable_service_discovery: bool = True
    service_discovery_protocol: str = "mdns"
    network_partition_handling: str = (
        "graceful_degradation"  # graceful_degradation, fail_fast
    )
    enable_network_mesh: bool = False
    mesh_protocol: str = "wireguard"
    load_balancing_enabled: bool = True
    connection_pool_size: int = 10
    connection_timeout_seconds: int = 30
    keep_alive_interval_seconds: int = 60
    enable_bandwidth_optimization: bool = True
    compression_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "enable_service_discovery": self.enable_service_discovery,
            "service_discovery_protocol": self.service_discovery_protocol,
            "network_partition_handling": self.network_partition_handling,
            "enable_network_mesh": self.enable_network_mesh,
            "mesh_protocol": self.mesh_protocol,
            "load_balancing_enabled": self.load_balancing_enabled,
            "connection_pool_size": self.connection_pool_size,
            "connection_timeout_seconds": self.connection_timeout_seconds,
            "keep_alive_interval_seconds": self.keep_alive_interval_seconds,
            "enable_bandwidth_optimization": self.enable_bandwidth_optimization,
            "compression_enabled": self.compression_enabled,
        }


@dataclass
class EdgeConfig:
    """Main edge computing configuration."""

    # Service settings
    service_name: str = "iTechSmart Edge Computing"
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Node configurations
    nodes: Dict[str, EdgeNodeConfig] = field(default_factory=dict)

    # Component configurations
    task_scheduling: TaskSchedulingConfig = field(default_factory=TaskSchedulingConfig)
    resource_monitoring: ResourceMonitoringConfig = field(
        default_factory=ResourceMonitoringConfig
    )
    security: SecurityConfig = field(default_factory=SecurityConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)

    # Cluster settings
    cluster_name: str = "default"
    cluster_region: str = "us-west-1"
    cluster_zone: str = "us-west-1a"
    enable_auto_scaling: bool = True
    max_cluster_nodes: int = 100
    min_cluster_nodes: int = 3

    # Performance settings
    default_task_timeout_minutes: int = 60
    max_concurrent_workloads: int = 50
    workload_queue_size: int = 1000
    metrics_retention_days: int = 30

    # Optimization settings
    optimization_policy: OptimizationPolicy = OptimizationPolicy.LOAD_BALANCING
    enable_predictive_scaling: bool = True
    predictive_scaling_window_minutes: int = 15
    enable_workload_balancing: bool = True
    enable_resource_optimization: bool = True

    # Integration settings
    enable_cloud_sync: bool = True
    cloud_sync_interval_minutes: int = 5
    cloud_backup_enabled: bool = True
    cloud_backup_interval_hours: int = 24

    # Monitoring and alerting
    enable_monitoring: bool = True
    enable_alerting: bool = True
    alert_webhook_urls: List[str] = field(default_factory=list)
    email_alerts_enabled: bool = False
    sms_alerts_enabled: bool = False

    # Development settings
    enable_debug_endpoints: bool = False
    enable_simulation_mode: bool = False
    mock_nodes_count: int = 3

    def __post_init__(self):
        """Post-initialization setup."""
        # Load environment-specific configurations
        self._load_from_environment()

        # Initialize default nodes if none provided
        if not self.nodes:
            self.nodes = self._get_default_nodes()

    def _load_from_environment(self):
        """Load configuration from environment variables."""
        self.debug = os.getenv("EDGE_DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("EDGE_LOG_LEVEL", self.log_level)
        self.cluster_name = os.getenv("EDGE_CLUSTER_NAME", self.cluster_name)
        self.cluster_region = os.getenv("EDGE_CLUSTER_REGION", self.cluster_region)
        self.cluster_zone = os.getenv("EDGE_CLUSTER_ZONE", self.cluster_zone)

        # Load task scheduling config
        self.task_scheduling.default_timeout_minutes = int(
            os.getenv(
                "EDGE_TASK_TIMEOUT_MINUTES",
                self.task_scheduling.default_timeout_minutes,
            )
        )
        self.task_scheduling.max_retry_attempts = int(
            os.getenv(
                "EDGE_MAX_RETRY_ATTEMPTS", self.task_scheduling.max_retry_attempts
            )
        )

        # Load monitoring config
        self.resource_monitoring.alert_cpu_threshold = float(
            os.getenv(
                "EDGE_ALERT_CPU_THRESHOLD", self.resource_monitoring.alert_cpu_threshold
            )
        )
        self.resource_monitoring.alert_memory_threshold = float(
            os.getenv(
                "EDGE_ALERT_MEMORY_THRESHOLD",
                self.resource_monitoring.alert_memory_threshold,
            )
        )

        # Load security config
        self.security.enable_encryption = (
            os.getenv("EDGE_ENABLE_ENCRYPTION", "true").lower() == "true"
        )
        self.security.enable_authentication = (
            os.getenv("EDGE_ENABLE_AUTH", "true").lower() == "true"
        )

    def _get_default_nodes(self) -> Dict[str, EdgeNodeConfig]:
        """Get default edge node configurations."""
        return {
            "gateway-1": EdgeNodeConfig(
                node_id="gateway-1",
                name="Edge Gateway 1",
                node_type="gateway",
                ip_address="192.168.1.100",
                port=8080,
                cpu_cores=4,
                memory_gb=8,
                storage_gb=128,
                capabilities=["compute", "storage", "networking", "gateway"],
            ),
            "compute-1": EdgeNodeConfig(
                node_id="compute-1",
                name="Edge Compute Node 1",
                node_type="compute",
                ip_address="192.168.1.101",
                port=8081,
                cpu_cores=8,
                memory_gb=16,
                storage_gb=256,
                capabilities=["compute", "gpu_acceleration"],
                gpu_accelerated=True,
                gpu_memory_gb=8,
            ),
            "storage-1": EdgeNodeConfig(
                node_id="storage-1",
                name="Edge Storage Node 1",
                node_type="storage",
                ip_address="192.168.1.102",
                port=8082,
                cpu_cores=2,
                memory_gb=4,
                storage_gb=1024,
                capabilities=["storage", "data_replication", "backup"],
            ),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "service_name": self.service_name,
            "version": self.version,
            "debug": self.debug,
            "log_level": self.log_level,
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "task_scheduling": self.task_scheduling.to_dict(),
            "resource_monitoring": self.resource_monitoring.to_dict(),
            "security": self.security.to_dict(),
            "network": self.network.to_dict(),
            "cluster_name": self.cluster_name,
            "cluster_region": self.cluster_region,
            "cluster_zone": self.cluster_zone,
            "enable_auto_scaling": self.enable_auto_scaling,
            "max_cluster_nodes": self.max_cluster_nodes,
            "min_cluster_nodes": self.min_cluster_nodes,
            "default_task_timeout_minutes": self.default_task_timeout_minutes,
            "max_concurrent_workloads": self.max_concurrent_workloads,
            "workload_queue_size": self.workload_queue_size,
            "metrics_retention_days": self.metrics_retention_days,
            "optimization_policy": self.optimization_policy.value,
            "enable_predictive_scaling": self.enable_predictive_scaling,
            "predictive_scaling_window_minutes": self.predictive_scaling_window_minutes,
            "enable_workload_balancing": self.enable_workload_balancing,
            "enable_resource_optimization": self.enable_resource_optimization,
            "enable_cloud_sync": self.enable_cloud_sync,
            "cloud_sync_interval_minutes": self.cloud_sync_interval_minutes,
            "cloud_backup_enabled": self.cloud_backup_enabled,
            "cloud_backup_interval_hours": self.cloud_backup_interval_hours,
            "enable_monitoring": self.enable_monitoring,
            "enable_alerting": self.enable_alerting,
            "alert_webhook_urls": self.alert_webhook_urls,
            "email_alerts_enabled": self.email_alerts_enabled,
            "sms_alerts_enabled": self.sms_alerts_enabled,
            "enable_debug_endpoints": self.enable_debug_endpoints,
            "enable_simulation_mode": self.enable_simulation_mode,
            "mock_nodes_count": self.mock_nodes_count,
        }
