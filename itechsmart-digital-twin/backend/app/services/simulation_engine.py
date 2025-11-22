import asyncio
import logging
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, AsyncGenerator, Optional
import numpy as np
import docker
from dataclasses import dataclass
import json

from app.core.config import settings
from app.core.database import get_database

logger = logging.getLogger(__name__)


@dataclass
class SimulationConfig:
    """Simulation configuration"""

    acceleration_factor: int = 10000  # 10,000x speed
    max_duration_hours: int = 168  # 1 week max
    max_parallel_simulations: int = 10
    timeout_minutes: int = 30
    confidence_threshold: float = 0.85


class SimulationEngine:
    """Core simulation engine for digital twin operations"""

    def __init__(self):
        self.config = SimulationConfig()
        self.active_simulations: Dict[str, Dict] = {}
        self.docker_client = None
        self.db = None
        self._initialized = False

    async def initialize(self):
        """Initialize the simulation engine"""
        try:
            self.db = get_database()
            self.docker_client = docker.from_env()

            # Test Docker connection
            self.docker_client.ping()

            self._initialized = True
            logger.info("🎮 Simulation Engine initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Simulation Engine: {str(e)}")
            raise

    async def create_simulation(
        self,
        change_type: str,
        target_system: str,
        changes: Dict[str, Any],
        duration_hours: int = 24,
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Create a new simulation environment"""
        if not self._initialized:
            raise RuntimeError("Simulation engine not initialized")

        if len(self.active_simulations) >= self.config.max_parallel_simulations:
            raise RuntimeError("Maximum parallel simulations reached")

        simulation_id = str(uuid.uuid4())

        try:
            # Create simulation record
            simulation = {
                "id": simulation_id,
                "change_type": change_type,
                "target_system": target_system,
                "changes": changes,
                "duration_hours": min(duration_hours, self.config.max_duration_hours),
                "context": context or {},
                "status": "created",
                "created_at": datetime.utcnow(),
                "progress": 0,
                "metrics": {},
                "predictions": {},
                "errors": [],
            }

            # Save to database
            await self.db.simulations.insert_one(simulation.copy())

            # Create virtual environment
            await self._create_virtual_environment(simulation)

            # Add to active simulations
            self.active_simulations[simulation_id] = simulation

            logger.info(f"✅ Simulation created: {simulation_id}")
            return simulation

        except Exception as e:
            logger.error(f"❌ Failed to create simulation: {str(e)}")
            # Cleanup on failure
            await self._cleanup_simulation_env(simulation_id)
            raise

    async def _create_virtual_environment(self, simulation: Dict[str, Any]):
        """Create virtual environment for simulation"""
        try:
            simulation_id = simulation["id"]

            # Create Docker network for simulation
            network_name = f"sim-{simulation_id}"
            network = self.docker_client.networks.create(
                network_name, driver="bridge", labels={"simulation_id": simulation_id}
            )

            # Create containers based on target system type
            containers = []

            if simulation["target_system"].startswith("database"):
                containers.append(await self._create_database_container(simulation))
            elif simulation["target_system"].startswith("web"):
                containers.append(await self._create_web_container(simulation))
            elif simulation["target_system"].startswith("network"):
                containers.append(await self._create_network_container(simulation))

            # Store container information
            simulation["containers"] = containers
            simulation["network_id"] = network.id

            # Update database
            await self.db.simulations.update_one(
                {"id": simulation_id},
                {
                    "$set": {
                        "containers": containers,
                        "network_id": network.id,
                        "status": "environment_ready",
                    }
                },
            )

            logger.info(f"🐳 Virtual environment created for {simulation_id}")

        except Exception as e:
            logger.error(f"❌ Failed to create virtual environment: {str(e)}")
            raise

    async def _create_database_container(
        self, simulation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create database container for simulation"""
        db_type = (
            simulation["target_system"].split("-")[1]
            if "-" in simulation["target_system"]
            else "postgres"
        )

        if db_type == "postgres":
            image = "postgres:15-alpine"
            env_vars = {
                "POSTGRES_USER": "sim_user",
                "POSTGRES_PASSWORD": "sim_pass",
                "POSTGRES_DB": "simulation_db",
            }
            ports = {"5432/tcp": None}  # Random port
        elif db_type == "mysql":
            image = "mysql:8.0"
            env_vars = {
                "MYSQL_ROOT_PASSWORD": "sim_pass",
                "MYSQL_DATABASE": "simulation_db",
            }
            ports = {"3306/tcp": None}
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        container = self.docker_client.containers.run(
            image,
            environment=env_vars,
            ports=ports,
            detach=True,
            labels={"simulation_id": simulation["id"], "type": "database"},
            network=f"sim-{simulation['id']}",
            name=f"sim-db-{simulation['id'][:8]}",
        )

        return {
            "id": container.id,
            "name": container.name,
            "type": "database",
            "db_type": db_type,
            "port": container.ports[f"{list(ports.keys())[0]}"][0]["HostPort"],
        }

    async def _create_web_container(self, simulation: Dict[str, Any]) -> Dict[str, Any]:
        """Create web application container for simulation"""
        # Use nginx as a simple web server
        container = self.docker_client.containers.run(
            "nginx:alpine",
            detach=True,
            labels={"simulation_id": simulation["id"], "type": "web"},
            network=f"sim-{simulation['id']}",
            name=f"sim-web-{simulation['id'][:8]}",
            ports={"80/tcp": None},
        )

        return {
            "id": container.id,
            "name": container.name,
            "type": "web",
            "port": container.ports["80/tcp"][0]["HostPort"],
        }

    async def _create_network_container(
        self, simulation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create network simulation container"""
        # Use a minimal Linux container for network simulations
        container = self.docker_client.containers.run(
            "alpine:latest",
            command=["sleep", "3600"],  # Keep running
            detach=True,
            labels={"simulation_id": simulation["id"], "type": "network"},
            network=f"sim-{simulation['id']}",
            name=f"sim-net-{simulation['id'][:8]}",
        )

        return {"id": container.id, "name": container.name, "type": "network"}

    async def run_simulation(
        self, simulation_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Run simulation with progress updates"""
        if simulation_id not in self.active_simulations:
            raise ValueError(f"Simulation {simulation_id} not found")

        simulation = self.active_simulations[simulation_id]

        try:
            # Update status
            simulation["status"] = "running"
            simulation["started_at"] = datetime.utcnow()
            await self._update_simulation(
                simulation_id,
                {"status": "running", "started_at": simulation["started_at"]},
            )

            yield {"status": "running", "progress": 0}

            # Step 1: Initialize baseline metrics
            baseline_metrics = await self._collect_baseline_metrics(simulation)
            simulation["baseline_metrics"] = baseline_metrics
            yield {"status": "running", "progress": 10, "step": "baseline_collected"}

            # Step 2: Apply changes
            await self._apply_simulation_changes(simulation)
            yield {"status": "running", "progress": 30, "step": "changes_applied"}

            # Step 3: Run accelerated simulation
            total_steps = int(simulation["duration_hours"] * 60 / 5)  # 5-minute steps

            for step in range(total_steps):
                # Simulate time advancement
                simulated_time = simulation["started_at"] + timedelta(minutes=step * 5)

                # Collect metrics
                current_metrics = await self._collect_metrics(
                    simulation, simulated_time
                )

                # Calculate deltas
                deltas = self._calculate_metrics_delta(
                    baseline_metrics, current_metrics
                )

                # Store metrics
                simulation["metrics"][step] = {
                    "timestamp": simulated_time.isoformat(),
                    "metrics": current_metrics,
                    "deltas": deltas,
                }

                # Update progress
                progress = 30 + int((step / total_steps) * 60)
                yield {
                    "status": "running",
                    "progress": progress,
                    "step": f"simulating_{step}_{total_steps}",
                    "current_metrics": current_metrics,
                    "deltas": deltas,
                }

                # Check for failures
                failure_prediction = self._predict_failure(current_metrics, deltas)
                if failure_prediction:
                    simulation["predictions"]["failure"] = failure_prediction
                    yield {
                        "status": "running",
                        "progress": progress,
                        "warning": "failure_detected",
                        "prediction": failure_prediction,
                    }

                # Accelerated delay (simulation runs much faster than real time)
                await asyncio.sleep(0.1)  # 100ms per step (10,000x acceleration)

            # Step 4: Generate final predictions
            predictions = await self._generate_predictions(simulation)
            simulation["predictions"] = predictions
            simulation["status"] = "completed"
            simulation["completed_at"] = datetime.utcnow()

            await self._update_simulation(
                simulation_id,
                {
                    "status": "completed",
                    "completed_at": simulation["completed_at"],
                    "predictions": predictions,
                },
            )

            yield {
                "status": "completed",
                "progress": 100,
                "predictions": predictions,
                "final_metrics": current_metrics,
            }

        except Exception as e:
            simulation["status"] = "failed"
            simulation["error"] = str(e)
            simulation["failed_at"] = datetime.utcnow()

            await self._update_simulation(
                simulation_id,
                {
                    "status": "failed",
                    "error": str(e),
                    "failed_at": simulation["failed_at"],
                },
            )

            logger.error(f"❌ Simulation {simulation_id} failed: {str(e)}")
            yield {"status": "failed", "error": str(e)}

    async def _collect_baseline_metrics(
        self, simulation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Collect baseline metrics before changes"""
        metrics = {}

        for container_info in simulation.get("containers", []):
            container_id = container_info["id"]
            try:
                container = self.docker_client.containers.get(container_id)
                stats = container.stats(stream=False)

                metrics[container_id] = {
                    "cpu_usage": self._calculate_cpu_percent(stats),
                    "memory_usage": stats["memory_stats"]["usage"],
                    "memory_limit": stats["memory_stats"]["limit"],
                    "network_rx": stats["networks"]["eth0"]["rx_bytes"],
                    "network_tx": stats["networks"]["eth0"]["tx_bytes"],
                    "timestamp": datetime.utcnow().isoformat(),
                }
            except Exception as e:
                logger.warning(
                    f"Failed to collect metrics for container {container_id}: {str(e)}"
                )

        return metrics

    async def _collect_metrics(
        self, simulation: Dict[str, Any], simulated_time: datetime
    ) -> Dict[str, Any]:
        """Collect metrics during simulation"""
        # In a real implementation, this would interact with the running containers
        # For now, we'll simulate metric changes based on the change type

        metrics = {}
        baseline = simulation.get("baseline_metrics", {})

        for container_id, baseline_data in baseline.items():
            # Simulate metric changes
            change_factor = self._get_change_factor(
                simulation["change_type"], simulated_time
            )

            metrics[container_id] = {
                "cpu_usage": baseline_data["cpu_usage"] * change_factor["cpu"],
                "memory_usage": baseline_data["memory_usage"] * change_factor["memory"],
                "memory_limit": baseline_data["memory_limit"],
                "network_rx": baseline_data["network_rx"] * change_factor["network"],
                "network_tx": baseline_data["network_tx"] * change_factor["network"],
                "timestamp": simulated_time.isoformat(),
            }

        return metrics

    def _get_change_factor(
        self, change_type: str, simulated_time: datetime
    ) -> Dict[str, float]:
        """Get change factors based on simulation type"""
        # Simulate different impact patterns
        hour = simulated_time.hour

        if change_type == "scaling":
            # Scaling improves performance initially but may increase resource usage
            return {
                "cpu": (
                    0.8 if hour in range(9, 17) else 0.6
                ),  # Business hours better performance
                "memory": 1.2,  # More memory usage with more instances
                "network": 1.1,  # Slightly more network traffic
            }
        elif change_type == "config_change":
            # Config changes might have mixed effects
            return {
                "cpu": 0.9,  # Slightly better CPU efficiency
                "memory": 1.1,  # Slightly more memory
                "network": 1.0,  # No network change
            }
        elif change_type == "security":
            # Security changes might have minimal performance impact
            return {
                "cpu": 1.05,  # Slight CPU overhead
                "memory": 1.02,  # Slight memory overhead
                "network": 0.98,  # Slightly less network due to filtering
            }
        else:
            # Default: no significant change
            return {"cpu": 1.0, "memory": 1.0, "network": 1.0}

    def _calculate_metrics_delta(
        self, baseline: Dict[str, Any], current: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate delta between baseline and current metrics"""
        deltas = {}

        for container_id in baseline:
            if container_id in current:
                baseline_data = baseline[container_id]
                current_data = current[container_id]

                deltas[container_id] = {
                    "cpu_delta": current_data["cpu_usage"] - baseline_data["cpu_usage"],
                    "memory_delta": current_data["memory_usage"]
                    - baseline_data["memory_usage"],
                    "network_rx_delta": current_data["network_rx"]
                    - baseline_data["network_rx"],
                    "network_tx_delta": current_data["network_tx"]
                    - baseline_data["network_tx"],
                }

        return deltas

    def _predict_failure(
        self, metrics: Dict[str, Any], deltas: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Predict potential failures based on metrics"""
        failure_indicators = []

        for container_id, metric_data in metrics.items():
            # Check CPU usage
            if metric_data["cpu_usage"] > 90:
                failure_indicators.append(
                    {
                        "type": "high_cpu",
                        "container": container_id,
                        "value": metric_data["cpu_usage"],
                        "threshold": 90,
                    }
                )

            # Check memory usage
            memory_percent = (
                metric_data["memory_usage"] / metric_data["memory_limit"]
            ) * 100
            if memory_percent > 85:
                failure_indicators.append(
                    {
                        "type": "high_memory",
                        "container": container_id,
                        "value": memory_percent,
                        "threshold": 85,
                    }
                )

            # Check for sudden spikes
            if container_id in deltas:
                delta = deltas[container_id]
                if abs(delta["cpu_delta"]) > 50:
                    failure_indicators.append(
                        {
                            "type": "cpu_spike",
                            "container": container_id,
                            "value": delta["cpu_delta"],
                            "threshold": 50,
                        }
                    )

        if failure_indicators:
            return {
                "predicted": True,
                "confidence": 0.75,
                "indicators": failure_indicators,
                "estimated_time_to_failure": (
                    "2-4 hours" if len(failure_indicators) > 2 else "6-8 hours"
                ),
            }

        return None

    async def _apply_simulation_changes(self, simulation: Dict[str, Any]):
        """Apply the simulated changes to the virtual environment"""
        # In a real implementation, this would apply actual changes to containers
        # For now, we'll simulate the application of changes

        change_type = simulation["change_type"]
        changes = simulation["changes"]

        logger.info(
            f"🔧 Applying {change_type} changes to simulation {simulation['id']}"
        )

        # Simulate change application delay
        await asyncio.sleep(1)

        # Store applied changes for reference
        simulation["applied_changes"] = changes
        await self._update_simulation(simulation["id"], {"applied_changes": changes})

    async def _generate_predictions(self, simulation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final predictions based on simulation results"""
        metrics_history = simulation.get("metrics", {})

        if not metrics_history:
            return {"error": "No metrics data available"}

        # Analyze trends
        final_metrics = list(metrics_history.values())[-1]["metrics"]
        baseline_metrics = simulation.get("baseline_metrics", {})

        # Calculate overall impact
        impact_score = self._calculate_impact_score(baseline_metrics, final_metrics)

        # Generate predictions
        predictions = {
            "impact_score": impact_score,
            "risk_level": self._determine_risk_level(impact_score),
            "performance_impact": self._analyze_performance_trend(metrics_history),
            "resource_impact": self._analyze_resource_impact(
                baseline_metrics, final_metrics
            ),
            "confidence": self._calculate_confidence(metrics_history),
            "recommendations": self._generate_recommendations(simulation, impact_score),
        }

        return predictions

    def _calculate_impact_score(
        self, baseline: Dict[str, Any], final: Dict[str, Any]
    ) -> float:
        """Calculate overall impact score (0-100)"""
        if not baseline or not final:
            return 50.0  # Neutral if no data

        total_impact = 0
        count = 0

        for container_id in baseline:
            if container_id in final:
                baseline_data = baseline[container_id]
                final_data = final[container_id]

                # CPU impact
                cpu_change = abs(final_data["cpu_usage"] - baseline_data["cpu_usage"])
                total_impact += min(cpu_change, 100)

                # Memory impact
                baseline_memory_percent = (
                    baseline_data["memory_usage"] / baseline_data["memory_limit"]
                ) * 100
                final_memory_percent = (
                    final_data["memory_usage"] / final_data["memory_limit"]
                ) * 100
                memory_change = abs(final_memory_percent - baseline_memory_percent)
                total_impact += min(memory_change, 100)

                count += 2

        return min(total_impact / count if count > 0 else 50, 100)

    def _determine_risk_level(self, impact_score: float) -> str:
        """Determine risk level based on impact score"""
        if impact_score >= 70:
            return "HIGH"
        elif impact_score >= 40:
            return "MEDIUM"
        else:
            return "LOW"

    def _analyze_performance_trend(
        self, metrics_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        if len(metrics_history) < 2:
            return {"trend": "insufficient_data"}

        cpu_values = []
        memory_values = []

        for step_data in metrics_history.values():
            for container_metrics in step_data["metrics"].values():
                cpu_values.append(container_metrics["cpu_usage"])
                memory_percent = (
                    container_metrics["memory_usage"]
                    / container_metrics["memory_limit"]
                ) * 100
                memory_values.append(memory_percent)

        # Calculate trends
        cpu_trend = "stable"
        memory_trend = "stable"

        if len(cpu_values) > 1:
            cpu_change = cpu_values[-1] - cpu_values[0]
            if cpu_change > 10:
                cpu_trend = "increasing"
            elif cpu_change < -10:
                cpu_trend = "decreasing"

        if len(memory_values) > 1:
            memory_change = memory_values[-1] - memory_values[0]
            if memory_change > 10:
                memory_trend = "increasing"
            elif memory_change < -10:
                memory_trend = "decreasing"

        return {
            "cpu_trend": cpu_trend,
            "memory_trend": memory_trend,
            "average_cpu": sum(cpu_values) / len(cpu_values),
            "average_memory": sum(memory_values) / len(memory_values),
        }

    def _analyze_resource_impact(
        self, baseline: Dict[str, Any], final: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze resource impact"""
        if not baseline or not final:
            return {"error": "No data available"}

        total_baseline_memory = sum(data["memory_usage"] for data in baseline.values())
        total_final_memory = sum(data["memory_usage"] for data in final.values())

        memory_change = total_final_memory - total_baseline_memory
        memory_change_percent = (
            (memory_change / total_baseline_memory) * 100
            if total_baseline_memory > 0
            else 0
        )

        return {
            "memory_change_bytes": memory_change,
            "memory_change_percent": memory_change_percent,
            "additional_memory_required": memory_change if memory_change > 0 else 0,
        }

    def _calculate_confidence(self, metrics_history: Dict[str, Any]) -> float:
        """Calculate confidence in predictions"""
        if len(metrics_history) < 10:
            return 0.5  # Low confidence with insufficient data

        # More data points = higher confidence
        confidence = min(len(metrics_history) / 100, 0.95)

        # Check for consistency in metrics
        if len(metrics_history) > 1:
            # Simple variance check (could be more sophisticated)
            cpu_values = []
            for step_data in list(metrics_history.values())[-10:]:  # Last 10 steps
                for container_metrics in step_data["metrics"].values():
                    cpu_values.append(container_metrics["cpu_usage"])

            if cpu_values:
                variance = np.var(cpu_values)
                if variance > 1000:  # High variance reduces confidence
                    confidence -= 0.1

        return max(confidence, 0.5)  # Minimum confidence of 50%

    def _generate_recommendations(
        self, simulation: Dict[str, Any], impact_score: float
    ) -> List[str]:
        """Generate recommendations based on simulation results"""
        recommendations = []

        change_type = simulation["change_type"]
        risk_level = self._determine_risk_level(impact_score)

        if risk_level == "HIGH":
            recommendations.append(
                "Consider applying changes during maintenance window"
            )
            recommendations.append("Have rollback plan ready")
            recommendations.append("Monitor system closely after deployment")
        elif risk_level == "MEDIUM":
            recommendations.append("Monitor system metrics after deployment")
            recommendations.append("Consider gradual rollout")
        else:
            recommendations.append("Changes appear safe for immediate deployment")

        # Change-specific recommendations
        if change_type == "scaling":
            recommendations.append("Ensure sufficient resources available")
        elif change_type == "config_change":
            recommendations.append("Test configuration in staging first")
        elif change_type == "security":
            recommendations.append("Verify functionality after security changes")

        return recommendations

    async def get_simulation_result(
        self, simulation_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get simulation result"""
        if simulation_id in self.active_simulations:
            return self.active_simulations[simulation_id]

        # Try to get from database
        simulation = await self.db.simulations.find_one({"id": simulation_id})
        return simulation

    async def get_active_simulations(self) -> List[str]:
        """Get list of active simulation IDs"""
        return list(self.active_simulations.keys())

    async def cleanup_simulation(self, simulation_id: str):
        """Clean up simulation resources"""
        try:
            if simulation_id in self.active_simulations:
                simulation = self.active_simulations[simulation_id]

                # Stop and remove containers
                for container_info in simulation.get("containers", []):
                    try:
                        container = self.docker_client.containers.get(
                            container_info["id"]
                        )
                        container.stop()
                        container.remove()
                        logger.info(f"🗑️ Removed container {container_info['name']}")
                    except Exception as e:
                        logger.warning(
                            f"Failed to remove container {container_info['id']}: {str(e)}"
                        )

                # Remove network
                if "network_id" in simulation:
                    try:
                        network = self.docker_client.networks.get(
                            simulation["network_id"]
                        )
                        network.remove()
                        logger.info(f"🗑️ Removed network {simulation['network_id']}")
                    except Exception as e:
                        logger.warning(
                            f"Failed to remove network {simulation['network_id']}: {str(e)}"
                        )

                # Remove from active simulations
                del self.active_simulations[simulation_id]

                # Update database
                await self.db.simulations.update_one(
                    {"id": simulation_id},
                    {
                        "$set": {
                            "status": "cleaned_up",
                            "cleaned_up_at": datetime.utcnow(),
                        }
                    },
                )

                logger.info(f"🧹 Simulation {simulation_id} cleaned up successfully")

        except Exception as e:
            logger.error(f"❌ Failed to cleanup simulation {simulation_id}: {str(e)}")

    async def _cleanup_simulation_env(self, simulation_id: str):
        """Clean up simulation environment (used for error handling)"""
        try:
            # Find and remove any containers with this simulation ID
            containers = self.docker_client.containers.list(
                all=True, filters={"label": f"simulation_id={simulation_id}"}
            )

            for container in containers:
                try:
                    container.remove(force=True)
                except Exception:
                    pass

            # Find and remove networks
            networks = self.docker_client.networks.list(
                filters={"label": f"simulation_id={simulation_id}"}
            )

            for network in networks:
                try:
                    network.remove()
                except Exception:
                    pass

        except Exception as e:
            logger.warning(
                f"Failed to cleanup simulation env {simulation_id}: {str(e)}"
            )

    def _calculate_cpu_percent(self, stats: Dict[str, Any]) -> float:
        """Calculate CPU percentage from Docker stats"""
        cpu_delta = (
            stats["cpu_stats"]["cpu_usage"]["total_usage"]
            - stats["precpu_stats"]["cpu_usage"]["total_usage"]
        )
        system_delta = (
            stats["cpu_stats"]["system_cpu_usage"]
            - stats["precpu_stats"]["system_cpu_usage"]
        )

        if system_delta > 0:
            return (
                (cpu_delta / system_delta)
                * len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"])
                * 100
            )
        return 0.0

    async def _update_simulation(self, simulation_id: str, updates: Dict[str, Any]):
        """Update simulation in database and memory"""
        if simulation_id in self.active_simulations:
            self.active_simulations[simulation_id].update(updates)

        await self.db.simulations.update_one({"id": simulation_id}, {"$set": updates})

    async def health_check(self) -> Dict[str, Any]:
        """Health check for the simulation engine"""
        return {
            "status": "healthy" if self._initialized else "uninitialized",
            "active_simulations": len(self.active_simulations),
            "docker_connected": self.docker_client is not None,
            "database_connected": self.db is not None,
            "max_parallel_simulations": self.config.max_parallel_simulations,
        }

    async def cleanup(self):
        """Cleanup resources"""
        # Clean up all active simulations
        for simulation_id in list(self.active_simulations.keys()):
            await self.cleanup_simulation(simulation_id)

        self._initialized = False
        logger.info("🧹 Simulation engine cleanup complete")
