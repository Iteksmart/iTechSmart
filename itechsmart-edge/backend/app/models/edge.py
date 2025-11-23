"""
iTechSmart Edge Computing Models

Data models for edge computing nodes, tasks, and workloads.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EdgeNodeType(Enum):
    """Types of edge computing nodes."""
    GATEWAY = "gateway"
    AGGREGATOR = "aggregator"
    COMPUTE = "compute"
    STORAGE = "storage"
    HYBRID = "hybrid"
    IOT_DEVICE = "iot_device"


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BATCH = 5


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ResourceMetrics:
    """Resource metrics for an edge node."""
    node_id: str
    cpu_usage: float = 0.0  # Percentage
    memory_usage: float = 0.0  # Percentage
    storage_usage: float = 0.0  # Percentage
    network_usage: float = 0.0  # Mbps
    gpu_usage: float = 0.0  # Percentage
    temperature: float = 0.0  # Celsius
    power_consumption: float = 0.0  # Watts
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "node_id": self.node_id,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "storage_usage": self.storage_usage,
            "network_usage": self.network_usage,
            "gpu_usage": self.gpu_usage,
            "temperature": self.temperature,
            "power_consumption": self.power_consumption,
            "last_updated": self.last_updated.isoformat()
        }


@dataclass
class EdgeNode:
    """Represents an edge computing node."""
    id: str
    name: str
    node_type: EdgeNodeType
    ip_address: str
    port: int
    cpu_cores: int
    memory_gb: int
    storage_gb: int
    capabilities: List[str]
    status: str = "inactive"
    last_seen: Optional[datetime] = None
    location: Optional[str] = None
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    gpu_accelerated: bool = False
    gpu_memory_gb: int = 0
    network_bandwidth_mbps: int = 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "node_type": self.node_type.value,
            "ip_address": self.ip_address,
            "port": self.port,
            "cpu_cores": self.cpu_cores,
            "memory_gb": self.memory_gb,
            "storage_gb": self.storage_gb,
            "capabilities": self.capabilities,
            "status": self.status,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "location": self.location,
            "version": self.version,
            "metadata": self.metadata,
            "gpu_accelerated": self.gpu_accelerated,
            "gpu_memory_gb": self.gpu_memory_gb,
            "network_bandwidth_mbps": self.network_bandwidth_mbps
        }


@dataclass
class EdgeTask:
    """Represents a task to be executed on edge nodes."""
    id: str = ""
    name: str = ""
    description: str = ""
    task_type: str = "compute"
    cpu_cores_required: int = 1
    memory_gb_required: float = 1.0
    storage_gb_required: float = 0.5
    estimated_duration_minutes: int = 10
    priority: TaskPriority = TaskPriority.NORMAL
    status: str = TaskStatus.PENDING.value
    assigned_nodes: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    requires_redundancy: bool = False
    max_retries: int = 3
    retry_count: int = 0
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    progress_percentage: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type,
            "cpu_cores_required": self.cpu_cores_required,
            "memory_gb_required": self.memory_gb_required,
            "storage_gb_required": self.storage_gb_required,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "priority": self.priority.value,
            "status": self.status,
            "assigned_nodes": self.assigned_nodes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "requires_redundancy": self.requires_redundancy,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "dependencies": self.dependencies,
            "parameters": self.parameters,
            "result": self.result,
            "error_message": self.error_message,
            "progress_percentage": self.progress_percentage
        }


@dataclass
class EdgeWorkload:
    """Represents a workload distributed across edge nodes."""
    id: str
    name: str
    description: str = ""
    tasks: List[str] = field(default_factory=list)  # Task IDs
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_execution_time_minutes: int = 0
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    optimization_policy: str = "load_balancing"
    priority: TaskPriority = TaskPriority.NORMAL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tasks": self.tasks,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_execution_time_minutes": self.total_execution_time_minutes,
            "resource_requirements": self.resource_requirements,
            "optimization_policy": self.optimization_policy,
            "priority": self.priority.value
        }
    
    @property
    def progress_percentage(self) -> float:
        """Calculate workload progress."""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate workload success rate."""
        if self.total_tasks == 0:
            return 0.0
        completed = self.completed_tasks + self.failed_tasks
        if completed == 0:
            return 0.0
        return (self.completed_tasks / completed) * 100


@dataclass
class EdgePolicy:
    """Represents an edge computing policy."""
    id: str
    name: str
    description: str = ""
    policy_type: str = "resource_allocation"  # resource_allocation, reliability, performance, security
    enabled: bool = True
    priority: int = 1
    conditions: Dict[str, Any] = field(default_factory=dict)
    actions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    execution_count: int = 0
    last_executed: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "policy_type": self.policy_type,
            "enabled": self.enabled,
            "priority": self.priority,
            "conditions": self.conditions,
            "actions": self.actions,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "execution_count": self.execution_count,
            "last_executed": self.last_executed.isoformat() if self.last_executed else None
        }


@dataclass
class EdgeCluster:
    """Represents a cluster of edge computing nodes."""
    id: str
    name: str
    description: str = ""
    nodes: List[str] = field(default_factory=list)  # Node IDs
    region: str = "default"
    zone: str = "default"
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)
    total_capacity: Dict[str, Any] = field(default_factory=dict)
    current_utilization: Dict[str, Any] = field(default_factory=dict)
    policies: List[str] = field(default_factory=list)  # Policy IDs
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "nodes": self.nodes,
            "region": self.region,
            "zone": self.zone,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "total_capacity": self.total_capacity,
            "current_utilization": self.current_utilization,
            "policies": self.policies,
            "metadata": self.metadata
        }


@dataclass
class EdgeAnalytics:
    """Analytics data for edge computing operations."""
    timestamp: datetime
    total_nodes: int
    active_nodes: int
    total_tasks: int
    running_tasks: int
    completed_tasks: int
    failed_tasks: int
    average_cpu_usage: float
    average_memory_usage: float
    average_task_duration_minutes: float
    total_throughput_tasks_per_hour: float
    error_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_nodes": self.total_nodes,
            "active_nodes": self.active_nodes,
            "total_tasks": self.total_tasks,
            "running_tasks": self.running_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "average_cpu_usage": self.average_cpu_usage,
            "average_memory_usage": self.average_memory_usage,
            "average_task_duration_minutes": self.average_task_duration_minutes,
            "total_throughput_tasks_per_hour": self.total_throughput_tasks_per_hour,
            "error_rate": self.error_rate
        }