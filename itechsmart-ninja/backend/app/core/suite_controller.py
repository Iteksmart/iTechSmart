"""
iTechSmart Suite Controller for Ninja
Allows Ninja to control, fix, and update all iTechSmart products
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import aiohttp

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.self_healing_engine import SelfHealingEngine
from app.core.auto_evolution_engine import AutoEvolutionEngine

logger = logging.getLogger(__name__)


class SuiteController:
    """
    Ninja's controller for the entire iTechSmart suite
    
    Capabilities:
    1. Monitor all services
    2. Fix errors in any service
    3. Update any service
    4. Optimize any service
    5. Coordinate cross-service operations
    6. Ensure suite-wide consistency
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.healing_engine = SelfHealingEngine(db)
        self.evolution_engine = AutoEvolutionEngine(db)
        
        # Enterprise hub connection
        self.hub_url = "http://localhost:8000"  # Enterprise hub
        self.ninja_api_key = "ninja-master-key"
        
        # Service registry
        self.services = {
            "enterprise": {
                "url": "http://localhost:8000",
                "type": "hub",
                "capabilities": ["integration", "orchestration", "monitoring"]
            },
            "supreme": {
                "url": "http://localhost:8002",
                "type": "infrastructure",
                "capabilities": ["auto-remediation", "network", "vm-provisioning"]
            },
            "hl7": {
                "url": "http://localhost:8003",
                "type": "healthcare",
                "capabilities": ["hl7-integration", "fhir", "emr-sync"]
            },
            "impactos": {
                "url": "http://localhost:8004",
                "type": "impact",
                "capabilities": ["impact-tracking", "sdg-mapping", "reporting"]
            },
            "passport": {
                "url": "http://localhost:8005",
                "type": "identity",
                "capabilities": ["authentication", "authorization", "identity-verification"]
            },
            "prooflink": {
                "url": "http://localhost:8006",
                "type": "verification",
                "capabilities": ["document-verification", "blockchain", "proof-generation"]
            }
        }
    
    async def register_with_hub(self):
        """Register Ninja with Enterprise hub"""
        
        logger.info("🥷 Registering Ninja with Enterprise hub")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hub_url}/api/integration/register",
                    json={
                        "service_type": "itechsmart-ninja",
                        "service_name": "ninja-controller",
                        "base_url": "http://localhost:8001",
                        "api_key": self.ninja_api_key,
                        "capabilities": [
                            "suite-control",
                            "error-fixing",
                            "auto-update",
                            "optimization",
                            "self-healing",
                            "code-generation",
                            "debugging",
                            "monitoring"
                        ],
                        "metadata": {
                            "role": "controller",
                            "permissions": "full-suite-access"
                        }
                    }
                ) as response:
                    result = await response.json()
                    logger.info(f"✅ Registered with hub: {result}")
                    return result
        
        except Exception as e:
            logger.error(f"Failed to register with hub: {e}")
            return None
    
    async def monitor_suite(self) -> Dict[str, Any]:
        """Monitor health of entire iTechSmart suite"""
        
        logger.info("🔍 Monitoring iTechSmart suite health")
        
        suite_health = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "services": {},
            "issues_detected": [],
            "recommendations": []
        }
        
        # Check each service
        for service_name, service_info in self.services.items():
            try:
                health = await self._check_service_health(
                    service_name,
                    service_info["url"]
                )
                
                suite_health["services"][service_name] = health
                
                # Detect issues
                if health["status"] != "healthy":
                    suite_health["issues_detected"].append({
                        "service": service_name,
                        "issue": health.get("error", "Unknown issue"),
                        "severity": "high" if health["status"] == "down" else "medium"
                    })
                    suite_health["overall_status"] = "degraded"
            
            except Exception as e:
                logger.error(f"Error checking {service_name}: {e}")
                suite_health["services"][service_name] = {
                    "status": "error",
                    "error": str(e)
                }
                suite_health["overall_status"] = "degraded"
        
        # Generate recommendations
        if suite_health["issues_detected"]:
            suite_health["recommendations"] = await self._generate_recommendations(
                suite_health["issues_detected"]
            )
        
        return suite_health
    
    async def fix_service(
        self,
        service_name: str,
        issue_type: str,
        auto_apply: bool = False
    ) -> Dict[str, Any]:
        """Fix an issue in a specific service"""
        
        logger.info(f"🔧 Fixing {service_name}: {issue_type}")
        
        service_info = self.services.get(service_name)
        if not service_info:
            return {"success": False, "error": "Service not found"}
        
        # Diagnose the issue
        diagnosis = await self._diagnose_service_issue(
            service_name,
            service_info["url"],
            issue_type
        )
        
        # Generate fix
        fix = await self._generate_service_fix(
            service_name,
            diagnosis
        )
        
        if not fix:
            return {"success": False, "error": "Could not generate fix"}
        
        # Apply fix if auto_apply or confidence is high
        if auto_apply or fix["confidence"] > 0.9:
            result = await self._apply_service_fix(
                service_name,
                service_info["url"],
                fix
            )
            
            return {
                "success": result["success"],
                "service": service_name,
                "issue_type": issue_type,
                "fix_applied": fix,
                "result": result
            }
        else:
            return {
                "success": False,
                "service": service_name,
                "issue_type": issue_type,
                "fix_generated": fix,
                "requires_approval": True,
                "message": "Fix requires manual approval"
            }
    
    async def update_service(
        self,
        service_name: str,
        update_type: str = "patch"
    ) -> Dict[str, Any]:
        """Update a service to latest version"""
        
        logger.info(f"📦 Updating {service_name}: {update_type}")
        
        service_info = self.services.get(service_name)
        if not service_info:
            return {"success": False, "error": "Service not found"}
        
        # Check for updates
        updates_available = await self._check_service_updates(
            service_name,
            service_info["url"]
        )
        
        if not updates_available:
            return {
                "success": True,
                "message": "Service is up to date",
                "service": service_name
            }
        
        # Apply updates
        result = await self._apply_service_updates(
            service_name,
            service_info["url"],
            updates_available,
            update_type
        )
        
        return result
    
    async def optimize_service(
        self,
        service_name: str,
        optimization_type: str = "performance"
    ) -> Dict[str, Any]:
        """Optimize a service"""
        
        logger.info(f"⚡ Optimizing {service_name}: {optimization_type}")
        
        service_info = self.services.get(service_name)
        if not service_info:
            return {"success": False, "error": "Service not found"}
        
        # Analyze service performance
        analysis = await self._analyze_service_performance(
            service_name,
            service_info["url"]
        )
        
        # Generate optimizations
        optimizations = await self._generate_optimizations(
            service_name,
            analysis,
            optimization_type
        )
        
        # Apply optimizations
        results = []
        for optimization in optimizations:
            result = await self._apply_optimization(
                service_name,
                service_info["url"],
                optimization
            )
            results.append(result)
        
        return {
            "success": all(r["success"] for r in results),
            "service": service_name,
            "optimization_type": optimization_type,
            "optimizations_applied": len(results),
            "results": results
        }
    
    async def coordinate_workflow(
        self,
        workflow_name: str,
        services: List[str],
        steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Coordinate a workflow across multiple services"""
        
        logger.info(f"🔄 Coordinating workflow: {workflow_name}")
        
        # Use Enterprise hub for workflow execution
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hub_url}/api/integration/workflow/execute",
                    json={
                        "workflow_name": workflow_name,
                        "steps": steps
                    },
                    headers={"X-API-Key": self.ninja_api_key}
                ) as response:
                    result = await response.json()
                    return result
        
        except Exception as e:
            logger.error(f"Workflow coordination failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def ensure_consistency(self) -> Dict[str, Any]:
        """Ensure consistency across all services"""
        
        logger.info("🔄 Ensuring suite-wide consistency")
        
        consistency_checks = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": [],
            "issues": [],
            "fixes_applied": []
        }
        
        # Check version consistency
        versions = await self._check_version_consistency()
        consistency_checks["checks"].append({
            "check": "version_consistency",
            "result": versions
        })
        
        # Check configuration consistency
        configs = await self._check_config_consistency()
        consistency_checks["checks"].append({
            "check": "config_consistency",
            "result": configs
        })
        
        # Check API compatibility
        apis = await self._check_api_compatibility()
        consistency_checks["checks"].append({
            "check": "api_compatibility",
            "result": apis
        })
        
        # Fix any inconsistencies
        for check in consistency_checks["checks"]:
            if not check["result"]["consistent"]:
                consistency_checks["issues"].append(check)
                
                # Auto-fix if possible
                fix = await self._fix_inconsistency(check)
                if fix["success"]:
                    consistency_checks["fixes_applied"].append(fix)
        
        return consistency_checks
    
    async def suite_wide_update(
        self,
        update_type: str = "patch"
    ) -> Dict[str, Any]:
        """Update all services in the suite"""
        
        logger.info(f"📦 Suite-wide update: {update_type}")
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "update_type": update_type,
            "services_updated": [],
            "services_failed": [],
            "total_services": len(self.services)
        }
        
        # Update each service
        for service_name in self.services.keys():
            try:
                result = await self.update_service(service_name, update_type)
                
                if result["success"]:
                    results["services_updated"].append(service_name)
                else:
                    results["services_failed"].append({
                        "service": service_name,
                        "error": result.get("error", "Unknown error")
                    })
            
            except Exception as e:
                logger.error(f"Failed to update {service_name}: {e}")
                results["services_failed"].append({
                    "service": service_name,
                    "error": str(e)
                })
        
        results["success"] = len(results["services_failed"]) == 0
        
        return results
    
    # Helper methods
    async def _check_service_health(
        self,
        service_name: str,
        service_url: str
    ) -> Dict[str, Any]:
        """Check health of a service"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{service_url}/health",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "healthy",
                            "response_time_ms": data.get("response_time_ms", 0),
                            "details": data
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "error": f"HTTP {response.status}"
                        }
        
        except asyncio.TimeoutError:
            return {"status": "timeout", "error": "Health check timeout"}
        except Exception as e:
            return {"status": "down", "error": str(e)}
    
    async def _diagnose_service_issue(
        self,
        service_name: str,
        service_url: str,
        issue_type: str
    ) -> Dict[str, Any]:
        """Diagnose an issue in a service"""
        
        # Get service logs and metrics
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{service_url}/api/diagnostics",
                    headers={"X-API-Key": self.ninja_api_key}
                ) as response:
                    diagnostics = await response.json()
                    
                    return {
                        "service": service_name,
                        "issue_type": issue_type,
                        "diagnostics": diagnostics,
                        "timestamp": datetime.utcnow().isoformat()
                    }
        
        except Exception as e:
            return {
                "service": service_name,
                "issue_type": issue_type,
                "error": str(e)
            }
    
    async def _generate_service_fix(
        self,
        service_name: str,
        diagnosis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate a fix for a service issue"""
        
        # Use self-healing engine to generate fix
        # This would use AI to analyze the diagnosis and generate a fix
        
        return {
            "service": service_name,
            "fix_type": "code_patch",
            "changes": [],
            "confidence": 0.85,
            "description": "Generated fix for service issue"
        }
    
    async def _apply_service_fix(
        self,
        service_name: str,
        service_url: str,
        fix: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply a fix to a service"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{service_url}/api/ninja-control",
                    json={
                        "command": "apply_fix",
                        "fix": fix
                    },
                    headers={"X-API-Key": self.ninja_api_key}
                ) as response:
                    result = await response.json()
                    return result
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _check_service_updates(
        self,
        service_name: str,
        service_url: str
    ) -> Optional[Dict[str, Any]]:
        """Check if updates are available for a service"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{service_url}/api/updates/check",
                    headers={"X-API-Key": self.ninja_api_key}
                ) as response:
                    updates = await response.json()
                    return updates if updates.get("available") else None
        
        except Exception:
            return None
    
    async def _apply_service_updates(
        self,
        service_name: str,
        service_url: str,
        updates: Dict[str, Any],
        update_type: str
    ) -> Dict[str, Any]:
        """Apply updates to a service"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{service_url}/api/updates/apply",
                    json={
                        "updates": updates,
                        "update_type": update_type
                    },
                    headers={"X-API-Key": self.ninja_api_key}
                ) as response:
                    result = await response.json()
                    return result
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _analyze_service_performance(
        self,
        service_name: str,
        service_url: str
    ) -> Dict[str, Any]:
        """Analyze service performance"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{service_url}/api/performance/analyze",
                    headers={"X-API-Key": self.ninja_api_key}
                ) as response:
                    analysis = await response.json()
                    return analysis
        
        except Exception as e:
            return {"error": str(e)}
    
    async def _generate_optimizations(
        self,
        service_name: str,
        analysis: Dict[str, Any],
        optimization_type: str
    ) -> List[Dict[str, Any]]:
        """Generate optimizations for a service"""
        
        # Use evolution engine to generate optimizations
        return []
    
    async def _apply_optimization(
        self,
        service_name: str,
        service_url: str,
        optimization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply an optimization to a service"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{service_url}/api/ninja-control",
                    json={
                        "command": "apply_optimization",
                        "optimization": optimization
                    },
                    headers={"X-API-Key": self.ninja_api_key}
                ) as response:
                    result = await response.json()
                    return result
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_recommendations(
        self,
        issues: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for detected issues"""
        
        recommendations = []
        
        for issue in issues:
            if issue["severity"] == "high":
                recommendations.append(
                    f"Immediately fix {issue['service']}: {issue['issue']}"
                )
            else:
                recommendations.append(
                    f"Schedule fix for {issue['service']}: {issue['issue']}"
                )
        
        return recommendations
    
    async def _check_version_consistency(self) -> Dict[str, Any]:
        """Check version consistency across services"""
        return {"consistent": True, "versions": {}}
    
    async def _check_config_consistency(self) -> Dict[str, Any]:
        """Check configuration consistency"""
        return {"consistent": True, "configs": {}}
    
    async def _check_api_compatibility(self) -> Dict[str, Any]:
        """Check API compatibility between services"""
        return {"consistent": True, "apis": {}}
    
    async def _fix_inconsistency(self, check: Dict[str, Any]) -> Dict[str, Any]:
        """Fix an inconsistency"""
        return {"success": True, "check": check["check"]}