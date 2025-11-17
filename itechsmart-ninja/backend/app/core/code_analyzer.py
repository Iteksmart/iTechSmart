"""
Code Analyzer for Self-Healing System
Analyzes code quality, performance, and security
"""

import ast
import os
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """
    Analyzes Python code for:
    1. Code quality issues
    2. Performance bottlenecks
    3. Security vulnerabilities
    4. Best practice violations
    5. Optimization opportunities
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_root = project_root / "backend"

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file"""

        if not file_path.exists():
            return {"error": "File not found"}

        try:
            content = file_path.read_text()
            tree = ast.parse(content)

            analysis = {
                "file": str(file_path.relative_to(self.project_root)),
                "lines": len(content.split("\n")),
                "quality_issues": self._check_quality(tree, content),
                "performance_issues": self._check_performance(tree, content),
                "security_issues": self._check_security(tree, content),
                "complexity": self._calculate_complexity(tree),
                "documentation": self._check_documentation(tree, content),
                "best_practices": self._check_best_practices(tree, content),
            }

            return analysis

        except SyntaxError as e:
            return {
                "file": str(file_path.relative_to(self.project_root)),
                "error": f"Syntax error: {e}",
            }
        except Exception as e:
            return {
                "file": str(file_path.relative_to(self.project_root)),
                "error": f"Analysis error: {e}",
            }

    def analyze_project(self) -> Dict[str, Any]:
        """Analyze entire project"""

        results = {
            "files_analyzed": 0,
            "total_lines": 0,
            "quality_score": 0.0,
            "issues": {
                "quality": [],
                "performance": [],
                "security": [],
                "documentation": [],
            },
            "files": [],
        }

        # Analyze all Python files
        for py_file in self.backend_root.rglob("*.py"):
            if self._should_analyze(py_file):
                analysis = self.analyze_file(py_file)

                if "error" not in analysis:
                    results["files_analyzed"] += 1
                    results["total_lines"] += analysis["lines"]
                    results["files"].append(analysis)

                    # Collect issues
                    results["issues"]["quality"].extend(analysis["quality_issues"])
                    results["issues"]["performance"].extend(
                        analysis["performance_issues"]
                    )
                    results["issues"]["security"].extend(analysis["security_issues"])

        # Calculate overall quality score
        results["quality_score"] = self._calculate_quality_score(results)

        return results

    def _should_analyze(self, file_path: Path) -> bool:
        """Check if file should be analyzed"""

        # Skip test files, migrations, etc.
        skip_patterns = ["__pycache__", ".pytest_cache", "migrations", "venv", ".venv"]

        for pattern in skip_patterns:
            if pattern in str(file_path):
                return False

        return True

    def _check_quality(self, tree: ast.AST, content: str) -> List[Dict]:
        """Check code quality issues"""
        issues = []

        # Check for long functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno
                if func_lines > 50:
                    issues.append(
                        {
                            "type": "long_function",
                            "severity": "medium",
                            "line": node.lineno,
                            "message": f"Function '{node.name}' is {func_lines} lines long (>50)",
                            "suggestion": "Consider breaking into smaller functions",
                        }
                    )

        # Check for too many arguments
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                num_args = len(node.args.args)
                if num_args > 5:
                    issues.append(
                        {
                            "type": "too_many_arguments",
                            "severity": "low",
                            "line": node.lineno,
                            "message": f"Function '{node.name}' has {num_args} arguments (>5)",
                            "suggestion": "Consider using a config object or dataclass",
                        }
                    )

        # Check for nested loops (complexity)
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                nested_loops = sum(
                    1 for n in ast.walk(node) if isinstance(n, (ast.For, ast.While))
                )
                if nested_loops > 2:
                    issues.append(
                        {
                            "type": "nested_loops",
                            "severity": "medium",
                            "line": node.lineno,
                            "message": f"Deeply nested loops detected ({nested_loops} levels)",
                            "suggestion": "Consider refactoring to reduce nesting",
                        }
                    )

        # Check for magic numbers
        for node in ast.walk(tree):
            if isinstance(node, ast.Num):
                if node.n not in [0, 1, -1] and isinstance(node.n, (int, float)):
                    issues.append(
                        {
                            "type": "magic_number",
                            "severity": "low",
                            "line": node.lineno,
                            "message": f"Magic number {node.n} found",
                            "suggestion": "Consider using a named constant",
                        }
                    )

        return issues

    def _check_performance(self, tree: ast.AST, content: str) -> List[Dict]:
        """Check performance issues"""
        issues = []

        # Check for inefficient string concatenation in loops
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(
                        child.op, ast.Add
                    ):
                        if isinstance(child.target, ast.Name):
                            issues.append(
                                {
                                    "type": "string_concat_in_loop",
                                    "severity": "medium",
                                    "line": node.lineno,
                                    "message": "String concatenation in loop detected",
                                    "suggestion": "Use list.append() and ''.join() instead",
                                }
                            )

        # Check for repeated list.append in comprehension
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                appends = [
                    n
                    for n in ast.walk(node)
                    if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)
                    and n.func.attr == "append"
                ]
                if len(appends) > 0:
                    issues.append(
                        {
                            "type": "loop_append",
                            "severity": "low",
                            "line": node.lineno,
                            "message": "Loop with append() detected",
                            "suggestion": "Consider using list comprehension",
                        }
                    )

        # Check for global variables
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                issues.append(
                    {
                        "type": "global_variable",
                        "severity": "medium",
                        "line": node.lineno,
                        "message": "Global variable usage detected",
                        "suggestion": "Avoid global state, use function parameters",
                    }
                )

        return issues

    def _check_security(self, tree: ast.AST, content: str) -> List[Dict]:
        """Check security issues"""
        issues = []

        # Check for eval/exec usage
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ["eval", "exec"]:
                        issues.append(
                            {
                                "type": "dangerous_function",
                                "severity": "critical",
                                "line": node.lineno,
                                "message": f"Dangerous function '{node.func.id}' used",
                                "suggestion": "Avoid eval/exec, use safer alternatives",
                            }
                        )

        # Check for SQL injection risks
        sql_patterns = [
            r"execute\(['&quot;].*%s.*['&quot;]\s*%",
            r"execute\(['&quot;].*\+.*['&quot;]\)",
            r"execute\(.*\.format\(",
        ]

        for pattern in sql_patterns:
            if re.search(pattern, content):
                issues.append(
                    {
                        "type": "sql_injection_risk",
                        "severity": "critical",
                        "message": "Potential SQL injection vulnerability",
                        "suggestion": "Use parameterized queries",
                    }
                )

        # Check for hardcoded secrets
        secret_patterns = [
            r"password\s*=\s*['&quot;][^'&quot;]+['&quot;]",
            r"api_key\s*=\s*['&quot;][^'&quot;]+['&quot;]",
            r"secret\s*=\s*['&quot;][^'&quot;]+['&quot;]",
            r"token\s*=\s*['&quot;][^'&quot;]+['&quot;]",
        ]

        for pattern in secret_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[: match.start()].count("\n") + 1
                issues.append(
                    {
                        "type": "hardcoded_secret",
                        "severity": "high",
                        "line": line_num,
                        "message": "Potential hardcoded secret detected",
                        "suggestion": "Use environment variables or secret management",
                    }
                )

        # Check for insecure random
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if (
                        isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "random"
                    ):
                        issues.append(
                            {
                                "type": "insecure_random",
                                "severity": "medium",
                                "line": node.lineno,
                                "message": "Using 'random' module for security",
                                "suggestion": "Use 'secrets' module for cryptographic purposes",
                            }
                        )

        return issues

    def _calculate_complexity(self, tree: ast.AST) -> Dict[str, Any]:
        """Calculate code complexity metrics"""

        complexity = {
            "cyclomatic": 0,
            "functions": 0,
            "classes": 0,
            "max_function_complexity": 0,
        }

        # Count functions and classes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity["functions"] += 1
                func_complexity = self._calculate_cyclomatic_complexity(node)
                complexity["cyclomatic"] += func_complexity
                complexity["max_function_complexity"] = max(
                    complexity["max_function_complexity"], func_complexity
                )
            elif isinstance(node, ast.ClassDef):
                complexity["classes"] += 1

        return complexity

    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Add 1 for each decision point
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _check_documentation(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """Check documentation quality"""

        doc_stats = {
            "functions_documented": 0,
            "functions_total": 0,
            "classes_documented": 0,
            "classes_total": 0,
            "coverage": 0.0,
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                doc_stats["functions_total"] += 1
                if ast.get_docstring(node):
                    doc_stats["functions_documented"] += 1

            elif isinstance(node, ast.ClassDef):
                doc_stats["classes_total"] += 1
                if ast.get_docstring(node):
                    doc_stats["classes_documented"] += 1

        total = doc_stats["functions_total"] + doc_stats["classes_total"]
        documented = doc_stats["functions_documented"] + doc_stats["classes_documented"]

        if total > 0:
            doc_stats["coverage"] = documented / total

        return doc_stats

    def _check_best_practices(self, tree: ast.AST, content: str) -> List[Dict]:
        """Check Python best practices"""
        issues = []

        # Check for bare except
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues.append(
                        {
                            "type": "bare_except",
                            "severity": "medium",
                            "line": node.lineno,
                            "message": "Bare except clause detected",
                            "suggestion": "Catch specific exceptions",
                        }
                    )

        # Check for mutable default arguments
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append(
                            {
                                "type": "mutable_default",
                                "severity": "high",
                                "line": node.lineno,
                                "message": f"Mutable default argument in '{node.name}'",
                                "suggestion": "Use None and initialize in function body",
                            }
                        )

        # Check for print statements (should use logging)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "print":
                    issues.append(
                        {
                            "type": "print_statement",
                            "severity": "low",
                            "line": node.lineno,
                            "message": "print() statement found",
                            "suggestion": "Use logging module instead",
                        }
                    )

        return issues

    def _calculate_quality_score(self, results: Dict) -> float:
        """Calculate overall quality score (0-10)"""

        if results["files_analyzed"] == 0:
            return 0.0

        # Start with perfect score
        score = 10.0

        # Deduct points for issues
        issue_weights = {"critical": 2.0, "high": 1.0, "medium": 0.5, "low": 0.1}

        for category in results["issues"].values():
            for issue in category:
                severity = issue.get("severity", "low")
                score -= issue_weights.get(severity, 0.1)

        # Ensure score is between 0 and 10
        return max(0.0, min(10.0, score))

    def suggest_improvements(self, analysis: Dict) -> List[Dict]:
        """Generate improvement suggestions based on analysis"""

        suggestions = []

        # Aggregate issues by type
        issue_counts = {}
        for category in analysis["issues"].values():
            for issue in category:
                issue_type = issue.get("type", "unknown")
                if issue_type not in issue_counts:
                    issue_counts[issue_type] = 0
                issue_counts[issue_type] += 1

        # Generate suggestions for common issues
        for issue_type, count in sorted(
            issue_counts.items(), key=lambda x: x[1], reverse=True
        ):
            if count >= 3:  # Only suggest if issue appears multiple times
                suggestion = self._generate_improvement_for_issue(issue_type, count)
                if suggestion:
                    suggestions.append(suggestion)

        return suggestions

    def _generate_improvement_for_issue(
        self, issue_type: str, count: int
    ) -> Optional[Dict]:
        """Generate improvement suggestion for specific issue type"""

        improvements = {
            "long_function": {
                "title": "Refactor Long Functions",
                "description": f"Found {count} functions longer than 50 lines",
                "action": "Break down into smaller, focused functions",
                "impact": "medium",
                "effort": "medium",
            },
            "nested_loops": {
                "title": "Reduce Loop Nesting",
                "description": f"Found {count} deeply nested loops",
                "action": "Extract inner loops into separate functions",
                "impact": "medium",
                "effort": "low",
            },
            "bare_except": {
                "title": "Improve Exception Handling",
                "description": f"Found {count} bare except clauses",
                "action": "Catch specific exceptions",
                "impact": "high",
                "effort": "low",
            },
            "hardcoded_secret": {
                "title": "Remove Hardcoded Secrets",
                "description": f"Found {count} potential hardcoded secrets",
                "action": "Move to environment variables",
                "impact": "critical",
                "effort": "low",
            },
        }

        return improvements.get(issue_type)
