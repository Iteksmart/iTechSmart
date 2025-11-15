"""
Dependency Manager for Auto-Evolution
Manages and updates project dependencies
"""
import subprocess
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class DependencyManager:
    """
    Manages project dependencies:
    1. Checks for outdated packages
    2. Identifies security vulnerabilities
    3. Generates update plans
    4. Applies safe updates
    5. Tests after updates
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_root = project_root / "backend"
        self.requirements_file = self.backend_root / "requirements.txt"
        
    async def check_outdated(self) -> List[Dict[str, Any]]:
        """Check for outdated dependencies"""
        logger.info("Checking for outdated dependencies...")
        
        try:
            # Run pip list --outdated
            result = subprocess.run(
                ["pip", "list", "--outdated", "--format=json"],
                capture_output=True,
                text=True,
                cwd=self.backend_root
            )
            
            if result.returncode == 0:
                outdated = json.loads(result.stdout)
                
                return [
                    {
                        "name": pkg["name"],
                        "current_version": pkg["version"],
                        "latest_version": pkg["latest_version"],
                        "type": pkg.get("latest_filetype", "wheel")
                    }
                    for pkg in outdated
                ]
            else:
                logger.error(f"Error checking outdated packages: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"Error in check_outdated: {e}")
            return []
    
    async def check_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Check for security vulnerabilities using pip-audit"""
        logger.info("Checking for security vulnerabilities...")
        
        try:
            # Try to use pip-audit if available
            result = subprocess.run(
                ["pip-audit", "--format=json"],
                capture_output=True,
                text=True,
                cwd=self.backend_root
            )
            
            if result.returncode == 0:
                vulnerabilities = json.loads(result.stdout)
                return vulnerabilities.get("dependencies", [])
            else:
                # pip-audit not installed, use safety
                result = subprocess.run(
                    ["safety", "check", "--json"],
                    capture_output=True,
                    text=True,
                    cwd=self.backend_root
                )
                
                if result.returncode == 0:
                    return json.loads(result.stdout)
                    
        except FileNotFoundError:
            logger.warning("pip-audit and safety not installed, skipping vulnerability check")
        except Exception as e:
            logger.error(f"Error checking vulnerabilities: {e}")
        
        return []
    
    async def generate_update_plan(
        self,
        outdated: List[Dict],
        vulnerabilities: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate a safe update plan"""
        
        update_plan = []
        
        # Create vulnerability lookup
        vuln_packages = {v.get("package", v.get("name")): v 
                        for v in vulnerabilities}
        
        for pkg in outdated:
            pkg_name = pkg["name"]
            
            # Determine risk level
            risk = self._assess_update_risk(pkg, vuln_packages)
            
            # Determine priority
            priority = self._determine_priority(pkg, vuln_packages)
            
            update = {
                "package": pkg_name,
                "current_version": pkg["current_version"],
                "target_version": pkg["latest_version"],
                "risk": risk,
                "priority": priority,
                "has_vulnerability": pkg_name in vuln_packages,
                "vulnerability_details": vuln_packages.get(pkg_name),
                "breaking_changes": await self._check_breaking_changes(pkg),
                "recommended_action": self._recommend_action(risk, priority)
            }
            
            update_plan.append(update)
        
        # Sort by priority
        update_plan.sort(key=lambda x: self._priority_score(x), reverse=True)
        
        return update_plan
    
    def _assess_update_risk(
        self,
        pkg: Dict,
        vuln_packages: Dict
    ) -> str:
        """Assess risk level of updating a package"""
        
        current = pkg["current_version"]
        latest = pkg["latest_version"]
        
        # Parse versions
        current_parts = self._parse_version(current)
        latest_parts = self._parse_version(latest)
        
        if not current_parts or not latest_parts:
            return "medium"
        
        # Major version change = high risk
        if latest_parts[0] > current_parts[0]:
            return "high"
        
        # Minor version change = medium risk
        if latest_parts[1] > current_parts[1]:
            return "medium"
        
        # Patch version change = low risk
        return "low"
    
    def _determine_priority(
        self,
        pkg: Dict,
        vuln_packages: Dict
    ) -> str:
        """Determine update priority"""
        
        pkg_name = pkg["name"]
        
        # Critical if has vulnerability
        if pkg_name in vuln_packages:
            vuln = vuln_packages[pkg_name]
            severity = vuln.get("severity", "").lower()
            
            if severity in ["critical", "high"]:
                return "critical"
            elif severity == "medium":
                return "high"
            else:
                return "medium"
        
        # High if major version behind
        current = self._parse_version(pkg["current_version"])
        latest = self._parse_version(pkg["latest_version"])
        
        if current and latest:
            if latest[0] - current[0] >= 2:
                return "high"
            elif latest[0] > current[0]:
                return "medium"
        
        return "low"
    
    def _parse_version(self, version: str) -> Optional[List[int]]:
        """Parse semantic version string"""
        try:
            parts = version.split(".")
            return [int(p.split("-")[0].split("+")[0]) for p in parts[:3]]
        except (ValueError, IndexError):
            return None
    
    async def _check_breaking_changes(self, pkg: Dict) -> List[str]:
        """Check for known breaking changes"""
        
        # This would ideally check changelog or release notes
        # For now, return empty list
        return []
    
    def _recommend_action(self, risk: str, priority: str) -> str:
        """Recommend action based on risk and priority"""
        
        if priority == "critical":
            return "update_immediately"
        
        if risk == "low" and priority in ["high", "medium"]:
            return "auto_update"
        
        if risk == "medium" and priority == "high":
            return "review_and_update"
        
        if risk == "high":
            return "manual_review_required"
        
        return "schedule_update"
    
    def _priority_score(self, update: Dict) -> int:
        """Calculate priority score for sorting"""
        
        priority_scores = {
            "critical": 100,
            "high": 50,
            "medium": 25,
            "low": 10
        }
        
        risk_penalties = {
            "high": -20,
            "medium": -10,
            "low": 0
        }
        
        score = priority_scores.get(update["priority"], 0)
        score += risk_penalties.get(update["risk"], 0)
        
        if update["has_vulnerability"]:
            score += 50
        
        return score
    
    async def apply_update(self, update: Dict) -> Dict[str, Any]:
        """Apply a dependency update"""
        
        package = update["package"]
        version = update["target_version"]
        
        logger.info(f"Updating {package} to {version}...")
        
        result = {
            "package": package,
            "version": version,
            "success": False,
            "error": None,
            "tests_passed": False
        }
        
        try:
            # Create backup of requirements.txt
            backup_path = self.requirements_file.with_suffix(".txt.backup")
            if self.requirements_file.exists():
                self.requirements_file.rename(backup_path)
            
            # Update package
            update_result = subprocess.run(
                ["pip", "install", "--upgrade", f"{package}=={version}"],
                capture_output=True,
                text=True,
                cwd=self.backend_root
            )
            
            if update_result.returncode == 0:
                # Update requirements.txt
                await self._update_requirements_file(package, version)
                
                # Run tests
                tests_passed = await self._run_tests()
                
                result["success"] = True
                result["tests_passed"] = tests_passed
                
                if not tests_passed:
                    logger.warning(f"Tests failed after updating {package}")
                    # Restore backup
                    if backup_path.exists():
                        backup_path.rename(self.requirements_file)
                    result["success"] = False
                    result["error"] = "Tests failed"
                else:
                    # Remove backup
                    if backup_path.exists():
                        backup_path.unlink()
                    
                    logger.info(f"Successfully updated {package} to {version}")
            else:
                result["error"] = update_result.stderr
                logger.error(f"Failed to update {package}: {update_result.stderr}")
                
                # Restore backup
                if backup_path.exists():
                    backup_path.rename(self.requirements_file)
        
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error updating {package}: {e}")
        
        return result
    
    async def _update_requirements_file(self, package: str, version: str):
        """Update requirements.txt with new version"""
        
        if not self.requirements_file.exists():
            return
        
        lines = self.requirements_file.read_text().split("\n")
        updated_lines = []
        
        package_lower = package.lower()
        found = False
        
        for line in lines:
            if line.strip().lower().startswith(package_lower):
                updated_lines.append(f"{package}=={version}")
                found = True
            else:
                updated_lines.append(line)
        
        if not found:
            updated_lines.append(f"{package}=={version}")
        
        self.requirements_file.write_text("\n".join(updated_lines))
    
    async def _run_tests(self) -> bool:
        """Run tests after update"""
        
        try:
            # Run pytest
            result = subprocess.run(
                ["pytest", "-x", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=self.backend_root,
                timeout=300  # 5 minutes
            )
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            logger.error("Tests timed out")
            return False
        except FileNotFoundError:
            logger.warning("pytest not found, skipping tests")
            return True  # Assume success if no test runner
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return False
    
    async def batch_update(
        self,
        updates: List[Dict],
        max_risk: str = "medium"
    ) -> Dict[str, Any]:
        """Apply multiple updates in batch"""
        
        risk_levels = ["low", "medium", "high"]
        max_risk_level = risk_levels.index(max_risk)
        
        results = {
            "total": len(updates),
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "details": []
        }
        
        for update in updates:
            # Check risk level
            update_risk_level = risk_levels.index(update["risk"])
            
            if update_risk_level > max_risk_level:
                results["skipped"] += 1
                results["details"].append({
                    "package": update["package"],
                    "status": "skipped",
                    "reason": f"Risk level {update['risk']} exceeds maximum {max_risk}"
                })
                continue
            
            # Apply update
            result = await self.apply_update(update)
            
            if result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append({
                "package": result["package"],
                "status": "success" if result["success"] else "failed",
                "error": result.get("error")
            })
        
        return results
    
    async def get_dependency_tree(self) -> Dict[str, Any]:
        """Get dependency tree"""
        
        try:
            result = subprocess.run(
                ["pipdeptree", "--json"],
                capture_output=True,
                text=True,
                cwd=self.backend_root
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            
        except FileNotFoundError:
            logger.warning("pipdeptree not installed")
        except Exception as e:
            logger.error(f"Error getting dependency tree: {e}")
        
        return {}
    
    async def check_compatibility(
        self,
        package: str,
        version: str
    ) -> Dict[str, Any]:
        """Check if package version is compatible"""
        
        compatibility = {
            "compatible": True,
            "conflicts": [],
            "warnings": []
        }
        
        try:
            # Try to resolve dependencies
            result = subprocess.run(
                ["pip", "install", "--dry-run", f"{package}=={version}"],
                capture_output=True,
                text=True,
                cwd=self.backend_root
            )
            
            if result.returncode != 0:
                compatibility["compatible"] = False
                compatibility["conflicts"].append(result.stderr)
        
        except Exception as e:
            logger.error(f"Error checking compatibility: {e}")
            compatibility["compatible"] = False
            compatibility["warnings"].append(str(e))
        
        return compatibility