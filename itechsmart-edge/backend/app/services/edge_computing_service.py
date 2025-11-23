"""
iTechSmart Edge Computing Optimization Service

Provides edge computing capabilities for distributed processing,
low-latency computing, and IoT device management.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging

from app.core.edge_config import EdgeConfig
from app.models.edge import (
    EdgeNode, 
    EdgeTask, 
    EdgeWorkload, 
    ResourceMetrics,
    EdgePolicy
)

logger = logging.getLogger(__name__)


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
class TaskDistributionResult:
    """Result of task distribution to edge nodes."""
    success: bool
    assigned_nodes: List[str]
    estimated_completion_time: datetime
    resource_utilization: Dict[str, float]
    failure_reason: Optional[str] = None


class EdgeComputingService:
    """Main edge computing service for distributed processing."""
    
    def __init__(self, config: EdgeConfig):
        self.config = config
        self.nodes: Dict[str, EdgeNode] = {}
        self.tasks: Dict[str, EdgeTask] = {}
        self.workloads: Dict[str, EdgeWorkload] = {}
        self.policies: Dict[str, EdgePolicy] = {}
        self.resource_metrics: Dict[str, ResourceMetrics] = {}
        
        # Service state
        self.is_running = False
        self.scheduler_active = False
        
    async def start(self):
        """Start the edge computing service."""
        logger.info("Starting Edge Computing Service...")
        
        # Initialize default policies
        await self._initialize_default_policies()
        
        # Start task scheduler
        self.scheduler_active = True
        asyncio.create_task(self._task_scheduler())
        
        # Start resource monitoring
        asyncio.create_task(self._resource_monitor())
        
        # Auto-discover edge nodes
        await self._discover_edge_nodes()
        
        self.is_running = True
        logger.info("Edge Computing Service started successfully")
    
    async def stop(self):
        """Stop the edge computing service."""
        logger.info("Stopping Edge Computing Service...")
        
        self.scheduler_active = False
        self.is_running = False
        
        logger.info("Edge Computing Service stopped")
    
    async def register_edge_node(self, node: EdgeNode) -> bool:
        """Register a new edge node."""
        try:
            # Validate node configuration
            if not await self._validate_node(node):
                logger.error(f"Invalid node configuration: {node.id}")
                return False
            
            # Check for duplicate node
            if node.id in self.nodes:
                logger.warning(f"Node {node.id} already exists, updating...")
            
            # Register node
            self.nodes[node.id] = node
            node.status = "active"
            node.last_seen = datetime.now()
            
            # Initialize metrics
            self.resource_metrics[node.id] = ResourceMetrics(
                node_id=node.id,
                cpu_usage=0.0,
                memory_usage=0.0,
                storage_usage=0.0,
                network_usage=0.0
            )
            
            logger.info(f"Edge node {node.id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register edge node {node.id}: {e}")
            return False
    
    async def submit_task(self, task: EdgeTask) -> TaskDistributionResult:
        """Submit a task for edge computing distribution."""
        try:
            # Generate task ID if not provided
            if not task.id:
                task.id = str(uuid.uuid4())
            
            # Validate task requirements
            if not await self._validate_task_requirements(task):
                return TaskDistributionResult(
                    success=False,
                    assigned_nodes=[],
                    estimated_completion_time=datetime.now(),
                    resource_utilization={},
                    failure_reason="Task requirements validation failed"
                )
            
            # Determine optimal node placement
            placement_result = await self._determine_task_placement(task)
            
            if not placement_result.success:
                return placement_result
            
            # Assign task to selected nodes
            task.status = TaskStatus.SCHEDULED.value
            task.assigned_nodes = placement_result.assigned_nodes
            task.created_at = datetime.now()
            
            # Store task
            self.tasks[task.id] = task
            
            # Deploy tasks to assigned nodes
            for node_id in placement_result.assigned_nodes:
                await self._deploy_task_to_node(task.id, node_id)
            
            logger.info(f"Task {task.id} submitted to {len(placement_result.assigned_nodes)} edge nodes")
            
            return TaskDistributionResult(
                success=True,
                assigned_nodes=placement_result.assigned_nodes,
                estimated_completion_time=placement_result.estimated_completion_time,
                resource_utilization=placement_result.resource_utilization
            )
            
        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            return TaskDistributionResult(
                success=False,
                assigned_nodes=[],
                estimated_completion_time=datetime.now(),
                resource_utilization={},
                failure_reason=str(e)
            )
    
    async def get_node_status(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific edge node."""
        node = self.nodes.get(node_id)
        if not node:
            return None
        
        metrics = self.resource_metrics.get(node_id)
        running_tasks = [task for task in self.tasks.values() 
                        if node_id in task.assigned_nodes and 
                        task.status == TaskStatus.RUNNING.value]
        
        return {
            "node": node.to_dict(),
            "metrics": metrics.to_dict() if metrics else {},
            "running_tasks": len(running_tasks),
            "last_seen": node.last_seen.isoformat() if node.last_seen else None,
            "health_score": await self._calculate_node_health_score(node_id)
        }
    
    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get overall edge computing cluster status."""
        total_nodes = len(self.nodes)
        active_nodes = len([n for n in self.nodes.values() if n.status == "active"])
        total_tasks = len(self.tasks)
        running_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.RUNNING.value])
        
        # Calculate aggregate resources
        total_cpu = sum(metrics.cpu_usage for metrics in self.resource_metrics.values())
        total_memory = sum(metrics.memory_usage for metrics in self.resource_metrics.values())
        total_storage = sum(metrics.storage_usage for metrics in self.resource_metrics.values())
        
        return {
            "cluster": {
                "total_nodes": total_nodes,
                "active_nodes": active_nodes,
                "total_tasks": total_tasks,
                "running_tasks": running_tasks,
                "scheduler_active": self.scheduler_active,
                "service_running": self.is_running
            },
            "resources": {
                "total_cpu_usage": round(total_cpu, 2),
                "total_memory_usage": round(total_memory, 2),
                "total_storage_usage": round(total_storage, 2),
                "average_cpu_usage": round(total_cpu / max(total_nodes, 1), 2),
                "average_memory_usage": round(total_memory / max(total_nodes, 1), 2)
            },
            "nodes_by_type": self._get_nodes_by_type(),
            "tasks_by_status": self._get_tasks_by_status()
        }
    
    async def optimize_resource_allocation(self) -> Dict[str, Any]:
        """Optimize resource allocation across edge nodes."""
        try:
            optimization_results = {
                "tasks_migrated": 0,
                "nodes_balanced": 0,
                "performance_improvement": 0.0,
                "actions_taken": []
            }
            
            # Get current resource usage
            overloaded_nodes = []
            underutilized_nodes = []
            
            for node_id, metrics in self.resource_metrics.items():
                if metrics.cpu_usage > 80.0 or metrics.memory_usage > 80.0:
                    overloaded_nodes.append(node_id)
                elif metrics.cpu_usage < 20.0 and metrics.memory_usage < 20.0:
                    underutilized_nodes.append(node_id)
            
            # Migrate tasks from overloaded to underutilized nodes
            for overloaded_node in overloaded_nodes:
                node_tasks = [task for task in self.tasks.values() 
                             if overloaded_node in task.assigned_nodes and 
                             task.status == TaskStatus.RUNNING.value]
                
                for task in node_tasks[:len(node_tasks)//2]:  # Migrate half the tasks
                    if underutilized_nodes:
                        target_node = underutilized_nodes[0]
                        await self._migrate_task(task.id, overloaded_node, target_node)
                        optimization_results["tasks_migrated"] += 1
                        optimization_results["actions_taken"].append(
                            f"Migrated task {task.id} from {overloaded_node} to {target_node}"
                        )
            
            # Calculate performance improvement
            if optimization_results["tasks_migrated"] > 0:
                optimization_results["performance_improvement"] = (
                    optimization_results["tasks_migrated"] * 15.0
                )
                optimization_results["nodes_balanced"] = min(
                    len(overloaded_nodes), len(underutilized_nodes)
                )
            
            logger.info(f"Resource optimization completed: {optimization_results}")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Resource optimization failed: {e}")
            return {
                "error": str(e),
                "tasks_migrated": 0,
                "nodes_balanced": 0,
                "performance_improvement": 0.0
            }
    
    # Private helper methods
    
    async def _initialize_default_policies(self):
        """Initialize default edge computing policies."""
        default_policies = [
            EdgePolicy(
                id="load_balancing",
                name="Load Balancing Policy",
                description="Distribute tasks across available edge nodes",
                policy_type="resource_allocation",
                enabled=True,
                priority=1
            ),
            EdgePolicy(
                id="fault_tolerance",
                name="Fault Tolerance Policy", 
                description="Ensure task execution with node redundancy",
                policy_type="reliability",
                enabled=True,
                priority=2
            ),
            EdgePolicy(
                id="latency_optimization",
                name="Low Latency Policy",
                description="Prioritize tasks for minimal execution latency",
                policy_type="performance",
                enabled=True,
                priority=1
            )
        ]
        
        for policy in default_policies:
            self.policies[policy.id] = policy
    
    async def _task_scheduler(self):
        """Background task for scheduling and monitoring edge tasks."""
        while self.scheduler_active:
            try:
                # Check for pending tasks
                pending_tasks = [task for task in self.tasks.values() 
                               if task.status == TaskStatus.PENDING.value]
                
                for task in pending_tasks:
                    await self.submit_task(task)
                
                # Monitor running tasks
                running_tasks = [task for task in self.tasks.values() 
                               if task.status == TaskStatus.RUNNING.value]
                
                for task in running_tasks:
                    await self._monitor_task_execution(task.id)
                
                # Clean up completed tasks
                await self._cleanup_completed_tasks()
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Task scheduler error: {e}")
                await asyncio.sleep(10)
    
    async def _resource_monitor(self):
        """Background task for monitoring edge node resources."""
        while self.is_running:
            try:
                for node_id, node in self.nodes.items():
                    if node.status == "active":
                        await self._update_node_metrics(node_id)
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Resource monitor error: {e}")
                await asyncio.sleep(15)
    
    async def _discover_edge_nodes(self):
        """Auto-discover edge nodes in the network."""
        # In a real implementation, this would scan the network for edge devices
        # For now, we'll create some demo nodes
        demo_nodes = [
            EdgeNode(
                id="edge-node-1",
                name="Gateway Node 1",
                node_type=EdgeNodeType.GATEWAY,
                ip_address="192.168.1.100",
                port=8080,
                cpu_cores=4,
                memory_gb=8,
                storage_gb=128,
                capabilities=["compute", "storage", "networking"]
            ),
            EdgeNode(
                id="edge-node-2", 
                name="Compute Node 1",
                node_type=EdgeNodeType.COMPUTE,
                ip_address="192.168.1.101",
                port=8081,
                cpu_cores=8,
                memory_gb=16,
                storage_gb=256,
                capabilities=["compute", "gpu_acceleration"]
            ),
            EdgeNode(
                id="edge-node-3",
                name="Aggregator Node 1",
                node_type=EdgeNodeType.AGGREGATOR,
                ip_address="192.168.1.102",
                port=8082,
                cpu_cores=6,
                memory_gb=12,
                storage_gb=512,
                capabilities=["compute", "storage", "data_aggregation"]
            )
        ]
        
        for node in demo_nodes:
            await self.register_edge_node(node)
        
        logger.info(f"Discovered and registered {len(demo_nodes)} edge nodes")
    
    async def _validate_node(self, node: EdgeNode) -> bool:
        """Validate edge node configuration."""
        if not node.id or not node.ip_address:
            return False
        
        if node.cpu_cores <= 0 or node.memory_gb <= 0:
            return False
        
        return True
    
    async def _validate_task_requirements(self, task: EdgeTask) -> bool:
        """Validate task requirements against available resources."""
        if task.cpu_cores_required > max((n.cpu_cores for n in self.nodes.values()), default=0):
            return False
        
        if task.memory_gb_required > max((n.memory_gb for n in self.nodes.values()), default=0):
            return False
        
        return True
    
    async def _determine_task_placement(self, task: EdgeTask) -> TaskDistributionResult:
        """Determine optimal placement for a task across edge nodes."""
        try:
            suitable_nodes = []
            
            # Find nodes that meet task requirements
            for node_id, node in self.nodes.items():
                if (node.status == "active" and
                    node.cpu_cores >= task.cpu_cores_required and
                    node.memory_gb >= task.memory_gb_required):
                    
                    metrics = self.resource_metrics.get(node_id)
                    if metrics and metrics.cpu_usage < 80.0 and metrics.memory_usage < 80.0:
                        suitable_nodes.append((node_id, metrics.cpu_usage + metrics.memory_usage))
            
            # Sort by resource usage (prefer less utilized nodes)
            suitable_nodes.sort(key=lambda x: x[1])
            
            if not suitable_nodes:
                return TaskDistributionResult(
                    success=False,
                    assigned_nodes=[],
                    estimated_completion_time=datetime.now(),
                    resource_utilization={},
                    failure_reason="No suitable edge nodes available"
                )
            
            # Select nodes based on task requirements
            assigned_nodes = []
            if task.requires_redundancy:
                # Assign to multiple nodes for redundancy
                assigned_nodes = [node[0] for node in suitable_nodes[:2]]
            else:
                # Assign to best single node
                assigned_nodes = [suitable_nodes[0][0]]
            
            # Calculate resource utilization
            resource_utilization = {}
            for node_id in assigned_nodes:
                metrics = self.resource_metrics.get(node_id)
                if metrics:
                    resource_utilization[node_id] = {
                        "cpu_usage": metrics.cpu_usage,
                        "memory_usage": metrics.memory_usage
                    }
            
            # Estimate completion time
            estimated_completion = datetime.now() + timedelta(
                minutes=task.estimated_duration_minutes
            )
            
            return TaskDistributionResult(
                success=True,
                assigned_nodes=assigned_nodes,
                estimated_completion_time=estimated_completion,
                resource_utilization=resource_utilization
            )
            
        except Exception as e:
            logger.error(f"Task placement determination failed: {e}")
            return TaskDistributionResult(
                success=False,
                assigned_nodes=[],
                estimated_completion_time=datetime.now(),
                resource_utilization={},
                failure_reason=str(e)
            )
    
    async def _deploy_task_to_node(self, task_id: str, node_id: str):
        """Deploy a task to a specific edge node."""
        try:
            task = self.tasks.get(task_id)
            node = self.nodes.get(node_id)
            
            if not task or not node:
                logger.error(f"Task {task_id} or node {node_id} not found")
                return
            
            # Simulate task deployment
            task.status = TaskStatus.RUNNING.value
            task.started_at = datetime.now()
            
            logger.info(f"Task {task_id} deployed to edge node {node_id}")
            
        except Exception as e:
            logger.error(f"Failed to deploy task {task_id} to node {node_id}: {e}")
            task.status = TaskStatus.FAILED.value
            task.error_message = str(e)
    
    async def _monitor_task_execution(self, task_id: str):
        """Monitor execution of a specific task."""
        try:
            task = self.tasks.get(task_id)
            if not task:
                return
            
            # Simulate task monitoring
            if task.started_at:
                elapsed = datetime.now() - task.started_at
                if elapsed.total_seconds() > task.estimated_duration_minutes * 60:
                    task.status = TaskStatus.COMPLETED.value
                    task.completed_at = datetime.now()
                    logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task monitoring failed for {task_id}: {e}")
    
    async def _cleanup_completed_tasks(self):
        """Clean up completed and old tasks."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            tasks_to_remove = []
            for task_id, task in self.tasks.items():
                if (task.status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value] and
                    task.completed_at and task.completed_at < cutoff_time):
                    tasks_to_remove.append(task_id)
            
            for task_id in tasks_to_remove:
                del self.tasks[task_id]
                logger.debug(f"Cleaned up task {task_id}")
            
        except Exception as e:
            logger.error(f"Task cleanup failed: {e}")
    
    async def _update_node_metrics(self, node_id: str):
        """Update resource metrics for a node."""
        try:
            metrics = self.resource_metrics.get(node_id)
            if not metrics:
                return
            
            # Simulate metric updates (in real implementation, would query the node)
            import random
            metrics.cpu_usage = random.uniform(10, 70)
            metrics.memory_usage = random.uniform(20, 80)
            metrics.storage_usage = random.uniform(30, 60)
            metrics.network_usage = random.uniform(5, 40)
            metrics.last_updated = datetime.now()
            
            # Update node last_seen
            node = self.nodes.get(node_id)
            if node:
                node.last_seen = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to update metrics for node {node_id}: {e}")
    
    async def _calculate_node_health_score(self, node_id: str) -> float:
        """Calculate health score for an edge node."""
        try:
            node = self.nodes.get(node_id)
            metrics = self.resource_metrics.get(node_id)
            
            if not node or not metrics:
                return 0.0
            
            # Calculate health based on resource usage and responsiveness
            cpu_score = max(0, 100 - metrics.cpu_usage)
            memory_score = max(0, 100 - metrics.memory_usage)
            storage_score = max(0, 100 - metrics.storage_usage)
            
            # Check if node is responsive
            responsiveness_score = 100.0  # Simplified
            if node.last_seen:
                time_since_last_seen = datetime.now() - node.last_seen
                if time_since_last_seen > timedelta(minutes=5):
                    responsiveness_score = 50.0
                elif time_since_last_seen > timedelta(minutes=1):
                    responsiveness_score = 80.0
            
            # Calculate weighted average
            health_score = (
                cpu_score * 0.3 +
                memory_score * 0.3 +
                storage_score * 0.2 +
                responsiveness_score * 0.2
            )
            
            return round(health_score, 2)
            
        except Exception as e:
            logger.error(f"Health score calculation failed for node {node_id}: {e}")
            return 0.0
    
    def _get_nodes_by_type(self) -> Dict[str, int]:
        """Get count of nodes by type."""
        nodes_by_type = {}
        for node in self.nodes.values():
            node_type = node.node_type.value
            nodes_by_type[node_type] = nodes_by_type.get(node_type, 0) + 1
        return nodes_by_type
    
    def _get_tasks_by_status(self) -> Dict[str, int]:
        """Get count of tasks by status."""
        tasks_by_status = {}
        for task in self.tasks.values():
            status = task.status
            tasks_by_status[status] = tasks_by_status.get(status, 0) + 1
        return tasks_by_status
    
    async def _migrate_task(self, task_id: str, source_node: str, target_node: str):
        """Migrate a task from source to target node."""
        try:
            task = self.tasks.get(task_id)
            if not task:
                return
            
            # Remove from source node
            if source_node in task.assigned_nodes:
                task.assigned_nodes.remove(source_node)
            
            # Add to target node
            if target_node not in task.assigned_nodes:
                task.assigned_nodes.append(target_node)
            
            logger.info(f"Migrated task {task_id} from {source_node} to {target_node}")
            
        except Exception as e:
            logger.error(f"Task migration failed: {e}")