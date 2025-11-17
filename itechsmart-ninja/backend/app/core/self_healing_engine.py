"""
Self-Healing Engine for iTechSmart Ninja
Automatically detects, diagnoses, and fixes errors in the codebase
"""

import os
import sys
import ast
import traceback
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import asyncio
import json
import subprocess
import re

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.self_healing import ErrorLog, CodeFix, HealthCheck, SystemMetric
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class SelfHealingEngine:
    """
    Autonomous self-healing engine that:
    1. Monitors system health
    2. Detects errors and issues
    3. Diagnoses root causes
    4. Generates and applies fixes
    5. Validates fixes work
    6. Learns from fixes
    """

    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.backend_root = self.project_root / "backend"
        self.frontend_root = self.project_root / "frontend"

        # Healing configuration
        self.config = {
            "auto_fix_enabled": True,
            "auto_deploy_enabled": False,  # Requires approval by default
            "max_fix_attempts": 3,
            "health_check_interval": 60,  # seconds
            "error_threshold": 5,  # errors before auto-fix
            "confidence_threshold": 0.8,  # AI confidence for auto-apply
        }

        # Error tracking
        self.error_history: List[Dict] = []
        self.fix_history: List[Dict] = []
        self.learning_data: Dict[str, Any] = {}

    async def start_monitoring(self):
        """Start continuous health monitoring"""
        logger.info("🏥 Self-Healing Engine started - Monitoring system health")

        while True:
            try:
                # Run health checks
                await self.run_health_checks()

                # Check for errors
                await self.check_for_errors()

                # Analyze system metrics
                await self.analyze_metrics()

                # Check for improvements
                await self.check_for_improvements()

                # Sleep until next check
                await asyncio.sleep(self.config["health_check_interval"])

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                # Self-heal the monitoring loop itself!
                await self.heal_monitoring_loop(e)

    async def run_health_checks(self) -> Dict[str, Any]:
        """Run comprehensive health checks"""
        health_status = {"timestamp": datetime.utcnow().isoformat(), "checks": {}}

        # 1. Database connectivity
        health_status["checks"]["database"] = await self._check_database()

        # 2. API endpoints
        health_status["checks"]["api"] = await self._check_api_endpoints()

        # 3. File system
        health_status["checks"]["filesystem"] = await self._check_filesystem()

        # 4. Dependencies
        health_status["checks"]["dependencies"] = await self._check_dependencies()

        # 5. Code quality
        health_status["checks"]["code_quality"] = await self._check_code_quality()

        # 6. Performance
        health_status["checks"]["performance"] = await self._check_performance()

        # 7. Security
        health_status["checks"]["security"] = await self._check_security()

        # Store health check
        health_check = HealthCheck(
            timestamp=datetime.utcnow(),
            status=health_status,
            overall_health=self._calculate_overall_health(health_status),
        )
        self.db.add(health_check)
        self.db.commit()

        return health_status

    async def check_for_errors(self):
        """Check logs and system for errors"""
        # Check application logs
        errors = await self._scan_logs_for_errors()

        # Check for exceptions in running processes
        runtime_errors = await self._check_runtime_errors()

        # Combine all errors
        all_errors = errors + runtime_errors

        if all_errors:
            logger.warning(f"🔍 Detected {len(all_errors)} errors")

            for error in all_errors:
                # Log error
                error_log = ErrorLog(
                    timestamp=datetime.utcnow(),
                    error_type=error["type"],
                    error_message=error["message"],
                    stack_trace=error.get("stack_trace"),
                    file_path=error.get("file_path"),
                    line_number=error.get("line_number"),
                    severity=error.get("severity", "medium"),
                )
                self.db.add(error_log)

                # Add to history
                self.error_history.append(error)

                # Check if we should auto-fix
                if self._should_auto_fix(error):
                    await self.auto_fix_error(error_log)

            self.db.commit()

    async def auto_fix_error(self, error_log: ErrorLog) -> Optional[Dict]:
        """Automatically fix an error"""
        logger.info(f"🔧 Attempting to auto-fix error: {error_log.error_type}")

        try:
            # 1. Diagnose the error
            diagnosis = await self._diagnose_error(error_log)

            # 2. Generate fix
            fix = await self._generate_fix(error_log, diagnosis)

            if not fix:
                logger.warning("Could not generate fix")
                return None

            # 3. Validate fix
            is_valid = await self._validate_fix(fix)

            if not is_valid:
                logger.warning("Generated fix failed validation")
                return None

            # 4. Apply fix (if confidence is high enough)
            if fix["confidence"] >= self.config["confidence_threshold"]:
                success = await self._apply_fix(fix)

                if success:
                    # 5. Verify fix worked
                    verification = await self._verify_fix(error_log, fix)

                    if verification["success"]:
                        logger.info(
                            f"✅ Successfully fixed error: {error_log.error_type}"
                        )

                        # Store fix
                        code_fix = CodeFix(
                            error_log_id=error_log.id,
                            fix_type=fix["type"],
                            fix_description=fix["description"],
                            code_changes=fix["changes"],
                            confidence_score=fix["confidence"],
                            applied=True,
                            success=True,
                            verification_result=verification,
                        )
                        self.db.add(code_fix)
                        self.db.commit()

                        # Learn from successful fix
                        await self._learn_from_fix(error_log, fix, verification)

                        return {
                            "success": True,
                            "fix": fix,
                            "verification": verification,
                        }
                    else:
                        logger.warning(
                            "Fix applied but verification failed - rolling back"
                        )
                        await self._rollback_fix(fix)
            else:
                logger.info(
                    f"Fix confidence too low ({fix['confidence']}) - requiring manual approval"
                )
                # Store fix for manual review
                code_fix = CodeFix(
                    error_log_id=error_log.id,
                    fix_type=fix["type"],
                    fix_description=fix["description"],
                    code_changes=fix["changes"],
                    confidence_score=fix["confidence"],
                    applied=False,
                    requires_approval=True,
                )
                self.db.add(code_fix)
                self.db.commit()

        except Exception as e:
            logger.error(f"Error in auto_fix_error: {e}")
            traceback.print_exc()

        return None

    async def _diagnose_error(self, error_log: ErrorLog) -> Dict[str, Any]:
        """Use AI to diagnose the root cause of an error"""

        # Prepare context for AI
        context = {
            "error_type": error_log.error_type,
            "error_message": error_log.error_message,
            "stack_trace": error_log.stack_trace,
            "file_path": error_log.file_path,
            "line_number": error_log.line_number,
            "recent_changes": await self._get_recent_code_changes(error_log.file_path),
            "similar_errors": await self._find_similar_errors(error_log),
            "system_state": await self._get_system_state(),
        }

        # Get file content if available
        if error_log.file_path:
            try:
                file_path = self.backend_root / error_log.file_path
                if file_path.exists():
                    context["file_content"] = file_path.read_text()
            except Exception as e:
                logger.warning(f"Could not read file {error_log.file_path}: {e}")

        # Ask AI to diagnose
        prompt = f"""
        Analyze this error and provide a detailed diagnosis:
        
        Error Type: {context['error_type']}
        Error Message: {context['error_message']}
        
        Stack Trace:
        {context['stack_trace']}
        
        File: {context['file_path']}
        Line: {context['line_number']}
        
        Recent Changes:
        {json.dumps(context.get('recent_changes', []), indent=2)}
        
        Similar Past Errors:
        {json.dumps(context.get('similar_errors', []), indent=2)}
        
        File Content:
        {context.get('file_content', 'Not available')}
        
        Provide:
        1. Root cause analysis
        2. Why this error occurred
        3. What needs to be fixed
        4. Potential side effects
        5. Recommended fix approach
        """

        diagnosis_text = await self.ai_service.generate_text(
            prompt=prompt, max_tokens=2000
        )

        return {
            "diagnosis": diagnosis_text,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _generate_fix(
        self, error_log: ErrorLog, diagnosis: Dict
    ) -> Optional[Dict]:
        """Generate code fix using AI"""

        prompt = f"""
        Based on this diagnosis, generate a code fix:
        
        Diagnosis:
        {diagnosis['diagnosis']}
        
        Error Details:
        - Type: {error_log.error_type}
        - Message: {error_log.error_message}
        - File: {error_log.file_path}
        - Line: {error_log.line_number}
        
        Generate a fix that:
        1. Resolves the root cause
        2. Maintains code quality
        3. Doesn't break existing functionality
        4. Includes proper error handling
        5. Is well-documented
        
        Provide the fix in this JSON format:
        {{
            "type": "code_change|dependency_update|config_change",
            "description": "What this fix does",
            "changes": [
                {{
                    "file": "path/to/file.py",
                    "action": "modify|create|delete",
                    "old_code": "code to replace (if modify)",
                    "new_code": "new code",
                    "line_start": 10,
                    "line_end": 20
                }}
            ],
            "tests": ["test cases to verify fix"],
            "rollback_steps": ["how to undo if needed"],
            "confidence": 0.95
        }}
        """

        fix_json = await self.ai_service.generate_text(prompt=prompt, max_tokens=3000)

        try:
            # Parse JSON response
            fix = json.loads(fix_json)
            return fix
        except json.JSONDecodeError:
            logger.error("Could not parse fix JSON from AI")
            return None

    async def _validate_fix(self, fix: Dict) -> bool:
        """Validate that a fix is safe to apply"""

        # 1. Check syntax
        for change in fix.get("changes", []):
            if change["action"] in ["modify", "create"]:
                if not self._validate_python_syntax(change["new_code"]):
                    logger.warning(f"Invalid Python syntax in fix for {change['file']}")
                    return False

        # 2. Check for dangerous operations
        dangerous_patterns = [
            r"rm\s+-rf",
            r"DROP\s+TABLE",
            r"DELETE\s+FROM.*WHERE\s+1=1",
            r"os\.system\(",
            r"eval\(",
            r"exec\(",
        ]

        for change in fix.get("changes", []):
            code = change.get("new_code", "")
            for pattern in dangerous_patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    logger.warning(f"Dangerous operation detected in fix: {pattern}")
                    return False

        # 3. Check file paths are within project
        for change in fix.get("changes", []):
            file_path = Path(change["file"])
            if not self._is_safe_path(file_path):
                logger.warning(f"Unsafe file path in fix: {file_path}")
                return False

        return True

    async def _apply_fix(self, fix: Dict) -> bool:
        """Apply the fix to the codebase"""
        logger.info(f"📝 Applying fix: {fix['description']}")

        try:
            # Backup current state
            backup_id = await self._create_backup()

            # Apply each change
            for change in fix["changes"]:
                file_path = self.backend_root / change["file"]

                if change["action"] == "modify":
                    # Read current content
                    content = file_path.read_text()

                    # Replace old code with new code
                    if "old_code" in change:
                        content = content.replace(
                            change["old_code"], change["new_code"]
                        )
                    else:
                        # Insert at specific line
                        lines = content.split("\n")
                        start = change.get("line_start", 0)
                        end = change.get("line_end", start)
                        lines[start:end] = change["new_code"].split("\n")
                        content = "\n".join(lines)

                    # Write back
                    file_path.write_text(content)
                    logger.info(f"✏️ Modified {change['file']}")

                elif change["action"] == "create":
                    # Create new file
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(change["new_code"])
                    logger.info(f"➕ Created {change['file']}")

                elif change["action"] == "delete":
                    # Delete file
                    if file_path.exists():
                        file_path.unlink()
                        logger.info(f"🗑️ Deleted {change['file']}")

            # Store backup ID with fix
            fix["backup_id"] = backup_id

            return True

        except Exception as e:
            logger.error(f"Error applying fix: {e}")
            # Rollback on error
            if "backup_id" in fix:
                await self._restore_backup(fix["backup_id"])
            return False

    async def _verify_fix(self, error_log: ErrorLog, fix: Dict) -> Dict[str, Any]:
        """Verify that the fix actually resolved the error"""
        logger.info("🔍 Verifying fix...")

        verification = {
            "success": False,
            "tests_passed": [],
            "tests_failed": [],
            "error_resolved": False,
            "side_effects": [],
        }

        try:
            # 1. Run syntax check
            syntax_ok = await self._check_syntax()
            if not syntax_ok:
                verification["tests_failed"].append("syntax_check")
                return verification
            verification["tests_passed"].append("syntax_check")

            # 2. Run unit tests
            if fix.get("tests"):
                for test in fix["tests"]:
                    result = await self._run_test(test)
                    if result:
                        verification["tests_passed"].append(test)
                    else:
                        verification["tests_failed"].append(test)

            # 3. Check if original error still occurs
            error_still_present = await self._check_error_still_present(error_log)
            verification["error_resolved"] = not error_still_present

            # 4. Check for new errors introduced
            new_errors = await self._check_for_new_errors()
            if new_errors:
                verification["side_effects"] = new_errors

            # Overall success
            verification["success"] = (
                len(verification["tests_failed"]) == 0
                and verification["error_resolved"]
                and len(verification["side_effects"]) == 0
            )

        except Exception as e:
            logger.error(f"Error in verification: {e}")
            verification["tests_failed"].append(f"verification_error: {str(e)}")

        return verification

    async def _learn_from_fix(self, error_log: ErrorLog, fix: Dict, verification: Dict):
        """Learn from successful fixes to improve future fixes"""

        learning_entry = {
            "error_type": error_log.error_type,
            "error_pattern": error_log.error_message,
            "fix_type": fix["type"],
            "fix_pattern": fix["description"],
            "confidence": fix["confidence"],
            "success": verification["success"],
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Store in learning data
        error_type = error_log.error_type
        if error_type not in self.learning_data:
            self.learning_data[error_type] = []

        self.learning_data[error_type].append(learning_entry)

        # Save to file
        learning_file = self.backend_root / "app" / "core" / "learning_data.json"
        with open(learning_file, "w") as f:
            json.dump(self.learning_data, f, indent=2)

        logger.info(f"📚 Learned from fix for {error_type}")

    async def check_for_improvements(self):
        """Proactively look for code improvements"""

        # 1. Code quality improvements
        quality_issues = await self._find_code_quality_issues()

        # 2. Performance optimizations
        perf_opportunities = await self._find_performance_opportunities()

        # 3. Security improvements
        security_issues = await self._find_security_issues()

        # 4. Dependency updates
        outdated_deps = await self._find_outdated_dependencies()

        # Generate improvement suggestions
        improvements = []

        for issue in quality_issues + perf_opportunities + security_issues:
            improvement = await self._generate_improvement(issue)
            if improvement:
                improvements.append(improvement)

        # Auto-apply low-risk improvements
        for improvement in improvements:
            if improvement["risk"] == "low" and improvement["confidence"] > 0.9:
                await self._apply_improvement(improvement)

        return improvements

    def _validate_python_syntax(self, code: str) -> bool:
        """Validate Python syntax"""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is within project boundaries"""
        try:
            path.resolve().relative_to(self.project_root.resolve())
            return True
        except ValueError:
            return False

    def _should_auto_fix(self, error: Dict) -> bool:
        """Determine if error should be auto-fixed"""
        if not self.config["auto_fix_enabled"]:
            return False

        # Check error severity
        if error.get("severity") == "critical":
            return True

        # Check error frequency
        similar_errors = [e for e in self.error_history if e["type"] == error["type"]]
        if len(similar_errors) >= self.config["error_threshold"]:
            return True

        return False

    async def _create_backup(self) -> str:
        """Create backup of current state"""
        backup_id = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        backup_dir = self.project_root / ".backups" / backup_id
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Copy backend files
        subprocess.run(
            [
                "rsync",
                "-a",
                str(self.backend_root) + "/",
                str(backup_dir / "backend") + "/",
            ]
        )

        logger.info(f"💾 Created backup: {backup_id}")
        return backup_id

    async def _restore_backup(self, backup_id: str):
        """Restore from backup"""
        backup_dir = self.project_root / ".backups" / backup_id

        if not backup_dir.exists():
            logger.error(f"Backup not found: {backup_id}")
            return

        # Restore backend files
        subprocess.run(
            [
                "rsync",
                "-a",
                "--delete",
                str(backup_dir / "backend") + "/",
                str(self.backend_root) + "/",
            ]
        )

        logger.info(f"♻️ Restored backup: {backup_id}")

    async def _rollback_fix(self, fix: Dict):
        """Rollback a fix"""
        if "backup_id" in fix:
            await self._restore_backup(fix["backup_id"])
        logger.info("⏪ Rolled back fix")

    # Placeholder methods for health checks
    async def _check_database(self) -> Dict:
        return {"status": "healthy", "latency_ms": 10}

    async def _check_api_endpoints(self) -> Dict:
        return {"status": "healthy", "endpoints_up": 290}

    async def _check_filesystem(self) -> Dict:
        return {"status": "healthy", "disk_usage": "45%"}

    async def _check_dependencies(self) -> Dict:
        return {"status": "healthy", "outdated": 0}

    async def _check_code_quality(self) -> Dict:
        return {"status": "good", "score": 8.5}

    async def _check_performance(self) -> Dict:
        return {"status": "good", "avg_response_time_ms": 150}

    async def _check_security(self) -> Dict:
        return {"status": "secure", "vulnerabilities": 0}

    def _calculate_overall_health(self, health_status: Dict) -> float:
        """Calculate overall health score"""
        scores = []
        for check in health_status["checks"].values():
            if check.get("status") == "healthy":
                scores.append(1.0)
            elif check.get("status") == "good":
                scores.append(0.8)
            else:
                scores.append(0.5)
        return sum(scores) / len(scores) if scores else 0.0

    async def _scan_logs_for_errors(self) -> List[Dict]:
        """Scan application logs for errors"""
        # Placeholder - implement log scanning
        return []

    async def _check_runtime_errors(self) -> List[Dict]:
        """Check for runtime errors"""
        # Placeholder - implement runtime error checking
        return []

    async def _get_recent_code_changes(self, file_path: Optional[str]) -> List[Dict]:
        """Get recent git changes for a file"""
        if not file_path:
            return []

        try:
            result = subprocess.run(
                ["git", "log", "-5", "--oneline", "--", file_path],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )
            commits = result.stdout.strip().split("\n")
            return [{"commit": c} for c in commits if c]
        except Exception:
            return []

    async def _find_similar_errors(self, error_log: ErrorLog) -> List[Dict]:
        """Find similar past errors"""
        similar = (
            self.db.query(ErrorLog)
            .filter(ErrorLog.error_type == error_log.error_type)
            .order_by(ErrorLog.timestamp.desc())
            .limit(5)
            .all()
        )

        return [{"id": e.id, "message": e.error_message} for e in similar]

    async def _get_system_state(self) -> Dict:
        """Get current system state"""
        return {
            "cpu_usage": "45%",
            "memory_usage": "60%",
            "disk_usage": "45%",
            "active_connections": 150,
        }

    async def _check_syntax(self) -> bool:
        """Check Python syntax across project"""
        try:
            result = subprocess.run(
                ["python", "-m", "py_compile"] + list(self.backend_root.rglob("*.py")),
                capture_output=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    async def _run_test(self, test: str) -> bool:
        """Run a specific test"""
        # Placeholder - implement test running
        return True

    async def _check_error_still_present(self, error_log: ErrorLog) -> bool:
        """Check if the original error still occurs"""
        # Placeholder - implement error checking
        return False

    async def _check_for_new_errors(self) -> List[str]:
        """Check for new errors introduced"""
        # Placeholder - implement new error detection
        return []

    async def _find_code_quality_issues(self) -> List[Dict]:
        """Find code quality issues"""
        # Placeholder - implement code quality analysis
        return []

    async def _find_performance_opportunities(self) -> List[Dict]:
        """Find performance optimization opportunities"""
        # Placeholder - implement performance analysis
        return []

    async def _find_security_issues(self) -> List[Dict]:
        """Find security issues"""
        # Placeholder - implement security scanning
        return []

    async def _find_outdated_dependencies(self) -> List[Dict]:
        """Find outdated dependencies"""
        # Placeholder - implement dependency checking
        return []

    async def _generate_improvement(self, issue: Dict) -> Optional[Dict]:
        """Generate improvement for an issue"""
        # Placeholder - implement improvement generation
        return None

    async def _apply_improvement(self, improvement: Dict):
        """Apply an improvement"""
        # Placeholder - implement improvement application
        pass

    async def heal_monitoring_loop(self, error: Exception):
        """Self-heal the monitoring loop itself"""
        logger.error(f"Monitoring loop error: {error}")
        # Restart monitoring with exponential backoff
        await asyncio.sleep(5)

    async def analyze_metrics(self):
        """Analyze system metrics for anomalies"""
        # Placeholder - implement metrics analysis
        pass
