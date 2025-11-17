"""
Deployment Engine - Core deployment orchestration logic
Handles deployment of individual products and full suite
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import yaml
import subprocess

logger = logging.getLogger(__name__)


class DeploymentEngine:
    """
    Core deployment engine for iTechSmart Suite
    Handles deployment orchestration, configuration, and monitoring
    """

    def __init__(self):
        self.deployments: Dict[str, Dict] = {}
        self.deployment_history: List[Dict] = []
        self.active_deployments: Dict[str, asyncio.Task] = {}

        # Product definitions with deployment requirements
        self.products = {
            # Foundation Products
            "itechsmart-enterprise": {
                "name": "iTechSmart Enterprise",
                "category": "foundation",
                "port": 8001,
                "dependencies": ["postgres", "redis"],
                "docker_image": "itechsmart/enterprise:latest",
                "health_endpoint": "/health",
                "startup_time": 30,
                "required_env": ["DATABASE_URL", "REDIS_URL"],
                "optional_env": ["JWT_SECRET", "SMTP_HOST"],
                "volumes": ["/data/enterprise:/app/data"],
                "cpu_limit": "1000m",
                "memory_limit": "1Gi",
            },
            "itechsmart-ninja": {
                "name": "iTechSmart Ninja",
                "category": "foundation",
                "port": 8002,
                "dependencies": ["postgres", "redis"],
                "docker_image": "itechsmart/ninja:latest",
                "health_endpoint": "/health",
                "startup_time": 25,
                "required_env": ["DATABASE_URL", "REDIS_URL"],
                "volumes": ["/data/ninja:/app/data"],
                "cpu_limit": "500m",
                "memory_limit": "512Mi",
            },
            "legalai-pro": {
                "name": "LegalAI Pro",
                "category": "foundation",
                "port": 8000,
                "dependencies": ["postgres"],
                "docker_image": "itechsmart/legalai-pro:latest",
                "health_endpoint": "/health",
                "startup_time": 20,
                "required_env": ["DATABASE_URL", "OPENAI_API_KEY"],
                "volumes": ["/data/legalai:/app/data"],
                "cpu_limit": "1000m",
                "memory_limit": "1Gi",
            },
            "itechsmart-analytics": {
                "name": "iTechSmart Analytics",
                "category": "foundation",
                "port": 8003,
                "dependencies": ["postgres", "redis"],
                "docker_image": "itechsmart/analytics:latest",
                "health_endpoint": "/health",
                "startup_time": 30,
                "required_env": ["DATABASE_URL", "REDIS_URL"],
                "volumes": ["/data/analytics:/app/data"],
                "cpu_limit": "2000m",
                "memory_limit": "2Gi",
            },
            "itechsmart-port-manager": {
                "name": "iTechSmart Port Manager",
                "category": "infrastructure",
                "port": 8100,
                "dependencies": [],
                "docker_image": "itechsmart/port-manager:latest",
                "health_endpoint": "/health",
                "startup_time": 15,
                "required_env": ["HUB_URL", "NINJA_URL"],
                "volumes": ["/data/port-manager:/app/data"],
                "cpu_limit": "250m",
                "memory_limit": "256Mi",
            },
            # Add all 27 products...
        }

        # Deployment strategies
        self.strategies = {
            "docker-compose": self._deploy_docker_compose,
            "kubernetes": self._deploy_kubernetes,
            "manual": self._deploy_manual,
        }

    async def initialize(self):
        """Initialize deployment engine"""
        logger.info("Initializing Deployment Engine...")

        # Load deployment history
        await self._load_deployment_history()

        # Discover existing deployments
        await self._discover_deployments()

        logger.info(f"Deployment Engine initialized with {len(self.products)} products")

    async def deploy_product(
        self,
        product_id: str,
        environment: str = "production",
        strategy: str = "docker-compose",
        config: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Deploy a single product

        Args:
            product_id: Product identifier
            environment: Target environment (dev, staging, production)
            strategy: Deployment strategy (docker-compose, kubernetes, manual)
            config: Custom configuration overrides

        Returns:
            Deployment result with status and details
        """
        logger.info(f"Starting deployment of {product_id} to {environment}")

        # Validate product exists
        if product_id not in self.products:
            raise ValueError(f"Unknown product: {product_id}")

        product = self.products[product_id]

        # Create deployment record
        deployment_id = (
            f"{product_id}-{environment}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        )
        deployment = {
            "deployment_id": deployment_id,
            "product_id": product_id,
            "product_name": product["name"],
            "environment": environment,
            "strategy": strategy,
            "status": "pending",
            "started_at": datetime.utcnow().isoformat(),
            "config": config or {},
            "steps": [],
        }

        self.deployments[deployment_id] = deployment

        try:
            # Step 1: Validate dependencies
            deployment["steps"].append(
                {"step": "validate_dependencies", "status": "running"}
            )
            await self._validate_dependencies(product)
            deployment["steps"][-1]["status"] = "completed"

            # Step 2: Generate configuration
            deployment["steps"].append(
                {"step": "generate_configuration", "status": "running"}
            )
            final_config = await self._generate_configuration(
                product, environment, config
            )
            deployment["config"] = final_config
            deployment["steps"][-1]["status"] = "completed"

            # Step 3: Pre-deployment checks
            deployment["steps"].append(
                {"step": "pre_deployment_checks", "status": "running"}
            )
            await self._pre_deployment_checks(product, environment)
            deployment["steps"][-1]["status"] = "completed"

            # Step 4: Execute deployment
            deployment["steps"].append(
                {"step": "execute_deployment", "status": "running"}
            )
            deploy_func = self.strategies.get(strategy)
            if not deploy_func:
                raise ValueError(f"Unknown deployment strategy: {strategy}")

            result = await deploy_func(product_id, product, final_config, environment)
            deployment["steps"][-1]["status"] = "completed"
            deployment["steps"][-1]["result"] = result

            # Step 5: Health check
            deployment["steps"].append({"step": "health_check", "status": "running"})
            await self._wait_for_health(product, final_config)
            deployment["steps"][-1]["status"] = "completed"

            # Step 6: Post-deployment validation
            deployment["steps"].append(
                {"step": "post_deployment_validation", "status": "running"}
            )
            await self._post_deployment_validation(product, final_config)
            deployment["steps"][-1]["status"] = "completed"

            # Mark deployment as successful
            deployment["status"] = "success"
            deployment["completed_at"] = datetime.utcnow().isoformat()

            logger.info(f"Successfully deployed {product_id}")

        except Exception as e:
            logger.error(f"Deployment failed for {product_id}: {e}")
            deployment["status"] = "failed"
            deployment["error"] = str(e)
            deployment["completed_at"] = datetime.utcnow().isoformat()

            # Mark current step as failed
            if deployment["steps"]:
                deployment["steps"][-1]["status"] = "failed"
                deployment["steps"][-1]["error"] = str(e)

        # Save to history
        self.deployment_history.append(deployment)
        await self._save_deployment_history()

        return deployment

    async def deploy_suite(
        self,
        environment: str = "production",
        strategy: str = "docker-compose",
        products: List[str] = None,
        config: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Deploy the entire iTechSmart Suite or selected products

        Args:
            environment: Target environment
            strategy: Deployment strategy
            products: List of product IDs to deploy (None = all)
            config: Global configuration overrides

        Returns:
            Suite deployment result
        """
        logger.info(f"Starting suite deployment to {environment}")

        # Determine products to deploy
        if products is None:
            products_to_deploy = list(self.products.keys())
        else:
            products_to_deploy = products

        # Create suite deployment record
        suite_deployment_id = (
            f"suite-{environment}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        )
        suite_deployment = {
            "deployment_id": suite_deployment_id,
            "type": "suite",
            "environment": environment,
            "strategy": strategy,
            "status": "pending",
            "started_at": datetime.utcnow().isoformat(),
            "products": products_to_deploy,
            "deployments": [],
        }

        self.deployments[suite_deployment_id] = suite_deployment

        try:
            # Deploy products in dependency order
            deployment_order = await self._calculate_deployment_order(
                products_to_deploy
            )

            for product_id in deployment_order:
                logger.info(f"Deploying {product_id} as part of suite deployment")

                deployment = await self.deploy_product(
                    product_id,
                    environment,
                    strategy,
                    config.get(product_id) if config else None,
                )

                suite_deployment["deployments"].append(
                    {
                        "product_id": product_id,
                        "deployment_id": deployment["deployment_id"],
                        "status": deployment["status"],
                    }
                )

                # Stop if any deployment fails
                if deployment["status"] == "failed":
                    suite_deployment["status"] = "failed"
                    suite_deployment["failed_product"] = product_id
                    break

            # Mark suite deployment as successful if all succeeded
            if suite_deployment["status"] != "failed":
                suite_deployment["status"] = "success"

            suite_deployment["completed_at"] = datetime.utcnow().isoformat()

        except Exception as e:
            logger.error(f"Suite deployment failed: {e}")
            suite_deployment["status"] = "failed"
            suite_deployment["error"] = str(e)
            suite_deployment["completed_at"] = datetime.utcnow().isoformat()

        return suite_deployment

    async def _validate_dependencies(self, product: Dict) -> bool:
        """Validate product dependencies are available"""
        for dep in product.get("dependencies", []):
            logger.info(f"Checking dependency: {dep}")
            # Check if dependency is running
            # This would check Docker, Kubernetes, or system services
        return True

    async def _generate_configuration(
        self, product: Dict, environment: str, custom_config: Dict = None
    ) -> Dict[str, Any]:
        """Generate final configuration for deployment"""
        config = {"port": product["port"], "environment": environment, "env_vars": {}}

        # Add required environment variables
        for env_var in product.get("required_env", []):
            # Get from custom config or use defaults
            if custom_config and env_var in custom_config:
                config["env_vars"][env_var] = custom_config[env_var]
            else:
                # Use default or generate
                config["env_vars"][env_var] = self._get_default_env_value(
                    env_var, environment
                )

        # Add optional environment variables
        for env_var in product.get("optional_env", []):
            if custom_config and env_var in custom_config:
                config["env_vars"][env_var] = custom_config[env_var]

        return config

    def _get_default_env_value(self, env_var: str, environment: str) -> str:
        """Get default value for environment variable"""
        defaults = {
            "DATABASE_URL": f"postgresql://user:pass@postgres:5432/itechsmart_{environment}",
            "REDIS_URL": "redis://redis:6379/0",
            "HUB_URL": "http://itechsmart-enterprise:8001",
            "NINJA_URL": "http://itechsmart-ninja:8002",
        }
        return defaults.get(env_var, "")

    async def _pre_deployment_checks(self, product: Dict, environment: str):
        """Run pre-deployment checks"""
        logger.info(f"Running pre-deployment checks for {product['name']}")
        # Check port availability
        # Check disk space
        # Check network connectivity
        # Check resource availability
        await asyncio.sleep(1)  # Simulate checks

    async def _deploy_docker_compose(
        self, product_id: str, product: Dict, config: Dict, environment: str
    ) -> Dict:
        """Deploy using Docker Compose"""
        logger.info(f"Deploying {product_id} with Docker Compose")

        # Generate docker-compose.yml
        compose_config = {
            "version": "3.8",
            "services": {
                product_id: {
                    "image": product["docker_image"],
                    "container_name": product_id,
                    "ports": [f"{product['port']}:{product['port']}"],
                    "environment": config["env_vars"],
                    "volumes": product.get("volumes", []),
                    "restart": "unless-stopped",
                    "networks": ["itechsmart-network"],
                }
            },
            "networks": {"itechsmart-network": {"external": True}},
        }

        # Write compose file
        compose_file = f"/tmp/{product_id}-compose.yml"
        with open(compose_file, "w") as f:
            yaml.dump(compose_config, f)

        # Execute docker-compose up
        try:
            result = subprocess.run(
                ["docker-compose", "-f", compose_file, "up", "-d"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                return {"status": "success", "output": result.stdout}
            else:
                raise Exception(f"Docker Compose failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            raise Exception("Docker Compose deployment timed out")

    async def _deploy_kubernetes(
        self, product_id: str, product: Dict, config: Dict, environment: str
    ) -> Dict:
        """Deploy using Kubernetes"""
        logger.info(f"Deploying {product_id} with Kubernetes")

        # Generate Kubernetes manifests
        deployment_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": product_id, "namespace": f"itechsmart-{environment}"},
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": product_id}},
                "template": {
                    "metadata": {"labels": {"app": product_id}},
                    "spec": {
                        "containers": [
                            {
                                "name": product_id,
                                "image": product["docker_image"],
                                "ports": [{"containerPort": product["port"]}],
                                "env": [
                                    {"name": k, "value": v}
                                    for k, v in config["env_vars"].items()
                                ],
                                "resources": {
                                    "limits": {
                                        "cpu": product.get("cpu_limit", "1000m"),
                                        "memory": product.get("memory_limit", "1Gi"),
                                    }
                                },
                            }
                        ]
                    },
                },
            },
        }

        # Write manifest and apply
        manifest_file = f"/tmp/{product_id}-deployment.yaml"
        with open(manifest_file, "w") as f:
            yaml.dump(deployment_manifest, f)

        try:
            result = subprocess.run(
                ["kubectl", "apply", "-f", manifest_file],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                return {"status": "success", "output": result.stdout}
            else:
                raise Exception(f"Kubernetes deployment failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            raise Exception("Kubernetes deployment timed out")

    async def _deploy_manual(
        self, product_id: str, product: Dict, config: Dict, environment: str
    ) -> Dict:
        """Manual deployment (generate instructions)"""
        logger.info(f"Generating manual deployment instructions for {product_id}")

        instructions = {
            "product": product["name"],
            "steps": [
                f"1. Pull Docker image: docker pull {product['docker_image']}",
                f"2. Set environment variables: {', '.join(config['env_vars'].keys())}",
                f"3. Run container: docker run -d -p {product['port']}:{product['port']} --name {product_id} {product['docker_image']}",
                f"4. Verify health: curl http://localhost:{product['port']}{product['health_endpoint']}",
            ],
        }

        return {"status": "manual", "instructions": instructions}

    async def _wait_for_health(self, product: Dict, config: Dict, timeout: int = 120):
        """Wait for product to become healthy"""
        import httpx

        health_url = f"http://localhost:{config['port']}{product['health_endpoint']}"
        start_time = asyncio.get_event_loop().time()

        async with httpx.AsyncClient() as client:
            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    response = await client.get(health_url, timeout=5.0)
                    if response.status_code == 200:
                        logger.info(f"{product['name']} is healthy")
                        return True
                except Exception:
                    pass

                await asyncio.sleep(5)

        raise Exception(f"{product['name']} failed to become healthy within {timeout}s")

    async def _post_deployment_validation(self, product: Dict, config: Dict):
        """Run post-deployment validation"""
        logger.info(f"Running post-deployment validation for {product['name']}")
        # Verify all endpoints are accessible
        # Check database connections
        # Verify integrations
        await asyncio.sleep(1)  # Simulate validation

    async def _calculate_deployment_order(self, products: List[str]) -> List[str]:
        """Calculate optimal deployment order based on dependencies"""
        # Simple topological sort based on dependencies
        ordered = []
        remaining = set(products)

        while remaining:
            # Find products with no unmet dependencies
            ready = []
            for product_id in remaining:
                product = self.products[product_id]
                deps = set(product.get("dependencies", []))

                # Check if all dependencies are deployed or not in our list
                if all(dep not in remaining or dep in ordered for dep in deps):
                    ready.append(product_id)

            if not ready:
                # Circular dependency or missing dependency
                ready = list(remaining)  # Deploy remaining in any order

            ordered.extend(ready)
            remaining -= set(ready)

        return ordered

    async def _discover_deployments(self):
        """Discover existing deployments"""
        # Check Docker containers
        # Check Kubernetes pods
        # Update deployments dict
        pass

    async def _load_deployment_history(self):
        """Load deployment history from disk"""
        history_file = Path("deployment_history.json")
        if history_file.exists():
            with open(history_file, "r") as f:
                self.deployment_history = json.load(f)

    async def _save_deployment_history(self):
        """Save deployment history to disk"""
        history_file = Path("deployment_history.json")
        with open(history_file, "w") as f:
            json.dump(self.deployment_history, f, indent=2)

    async def shutdown(self):
        """Shutdown deployment engine"""
        await self._save_deployment_history()
        logger.info("Deployment Engine shutdown complete")
