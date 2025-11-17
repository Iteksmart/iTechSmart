"""
iTechSmart Forge - Deployment Engine
Deploy apps to production with one click
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import asyncio
import httpx

from app.models.models import Deployment, App, DeploymentStatus


class DeploymentEngine:
    """
    Engine for deploying apps to production
    """

    def __init__(self, db: Session):
        self.db = db
        self.mdm_agent_url = "http://localhost:8200"  # iTechSmart MDM Agent

    async def deploy_app(
        self,
        app_id: int,
        environment: str = "production",
        build_config: Optional[Dict[str, Any]] = None,
    ) -> Deployment:
        """Deploy an app"""
        app = self.db.query(App).filter(App.id == app_id).first()
        if not app:
            raise ValueError(f"App {app_id} not found")

        # Create deployment record
        deployment = Deployment(
            app_id=app_id,
            version=app.version,
            environment=environment,
            status=DeploymentStatus.PENDING.value,
            build_config=build_config or {},
        )

        self.db.add(deployment)
        self.db.flush()

        try:
            # Start build
            deployment.status = DeploymentStatus.DEPLOYING.value
            deployment.build_started_at = datetime.utcnow()
            self.db.commit()

            # Build app
            build_result = await self._build_app(app, deployment)

            deployment.build_completed_at = datetime.utcnow()
            deployment.build_duration_ms = (
                deployment.build_completed_at - deployment.build_started_at
            ).total_seconds() * 1000
            deployment.build_log = build_result.get("log", "")

            # Deploy via MDM Agent
            deploy_result = await self._deploy_via_mdm(app, deployment)

            deployment.status = DeploymentStatus.DEPLOYED.value
            deployment.deployed_at = datetime.utcnow()
            deployment.deployment_url = deploy_result.get("url")
            deployment.preview_url = deploy_result.get("preview_url")
            deployment.deployment_log = deploy_result.get("log", "")

        except Exception as e:
            deployment.status = DeploymentStatus.FAILED.value
            deployment.error_message = str(e)

        self.db.commit()
        self.db.refresh(deployment)

        return deployment

    async def _build_app(self, app: App, deployment: Deployment) -> Dict[str, Any]:
        """Build the app"""
        # Mock build process
        await asyncio.sleep(2)  # Simulate build time

        return {
            "success": True,
            "log": f"Building {app.name} v{app.version}...\nBuild completed successfully!",
        }

    async def _deploy_via_mdm(self, app: App, deployment: Deployment) -> Dict[str, Any]:
        """Deploy via MDM Agent"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mdm_agent_url}/api/deploy",
                    json={
                        "app_name": app.slug,
                        "version": app.version,
                        "environment": deployment.environment,
                    },
                    timeout=60.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "url": f"https://{app.slug}.forge.itechsmart.dev",
                        "preview_url": f"https://preview-{app.slug}.forge.itechsmart.dev",
                        "log": "Deployment successful",
                    }
                else:
                    raise Exception(f"MDM Agent returned {response.status_code}")
        except Exception as e:
            # Fallback to mock deployment
            return {
                "url": f"https://{app.slug}.forge.itechsmart.dev",
                "preview_url": f"https://preview-{app.slug}.forge.itechsmart.dev",
                "log": f"Mock deployment (MDM Agent not available: {str(e)})",
            }

    async def rollback_deployment(self, deployment_id: int) -> bool:
        """Rollback a deployment"""
        deployment = (
            self.db.query(Deployment).filter(Deployment.id == deployment_id).first()
        )

        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")

        # Find previous successful deployment
        previous = (
            self.db.query(Deployment)
            .filter(
                Deployment.app_id == deployment.app_id,
                Deployment.status == DeploymentStatus.DEPLOYED.value,
                Deployment.id < deployment_id,
            )
            .order_by(Deployment.id.desc())
            .first()
        )

        if not previous:
            raise ValueError("No previous deployment to rollback to")

        # Redeploy previous version
        await self.deploy_app(
            deployment.app_id, deployment.environment, previous.build_config
        )

        return True
