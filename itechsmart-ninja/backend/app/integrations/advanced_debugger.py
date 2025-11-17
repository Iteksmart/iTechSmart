"""
Advanced Debugger Integration
Provides comprehensive debugging capabilities with AI-powered analysis
"""

from typing import Dict, Any, List, Optional, Tuple
import asyncio
import json
import re
import ast
import sys
import traceback
import time
import psutil
import logging
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class Breakpoint:
    """Represents a debugging breakpoint"""

    id: str
    file_path: str
    line_number: int
    condition: Optional[str] = None
    enabled: bool = True
    hit_count: int = 0
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VariableInfo:
    """Information about a variable"""

    name: str
    value: Any
    type: str
    size: int
    memory_address: str
    is_mutable: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": str(self.value),
            "type": self.type,
            "size": self.size,
            "memory_address": self.memory_address,
            "is_mutable": self.is_mutable,
        }


@dataclass
class ProfileResult:
    """Code profiling result"""

    execution_time: float
    memory_usage: float
    cpu_usage: float
    function_calls: int
    hotspots: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MemoryLeak:
    """Memory leak information"""

    location: str
    line_number: int
    leak_type: str
    severity: str
    description: str
    suggestion: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AdvancedDebugger:
    """Advanced debugging capabilities with AI integration"""

    def __init__(self):
        self.breakpoints: Dict[str, Breakpoint] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.profiling_data: Dict[str, Any] = {}

        # Error patterns for analysis
        self.error_patterns = {
            "syntax_error": r"SyntaxError|IndentationError|TabError",
            "name_error": r"NameError|UnboundLocalError",
            "type_error": r"TypeError",
            "value_error": r"ValueError",
            "attribute_error": r"AttributeError",
            "import_error": r"ImportError|ModuleNotFoundError",
            "index_error": r"IndexError",
            "key_error": r"KeyError",
            "zero_division": r"ZeroDivisionError",
            "file_not_found": r"FileNotFoundError",
            "permission_error": r"PermissionError",
            "timeout_error": r"TimeoutError",
            "connection_error": r"ConnectionError|ConnectionRefusedError",
            "memory_error": r"MemoryError",
            "recursion_error": r"RecursionError",
        }

        # Common fixes for error types
        self.common_fixes = {
            "syntax_error": [
                "Check for missing colons, parentheses, or brackets",
                "Verify proper indentation (use spaces, not tabs)",
                "Look for unclosed strings or comments",
            ],
            "name_error": [
                "Check if variable is defined before use",
                "Verify correct variable name spelling",
                "Ensure variable is in correct scope",
            ],
            "type_error": [
                "Verify data types match expected types",
                "Add type conversion if needed",
                "Check function arguments",
            ],
            "import_error": [
                "Install missing package: pip install <package>",
                "Check package name spelling",
                "Verify package is in Python path",
            ],
            "index_error": [
                "Check list/array bounds",
                "Verify index is within range",
                "Add bounds checking",
            ],
            "key_error": [
                "Check if key exists in dictionary",
                "Use dict.get() with default value",
                "Add key existence check",
            ],
        }

    async def analyze_error(
        self,
        error_message: str,
        stack_trace: Optional[str] = None,
        code: Optional[str] = None,
        language: str = "python",
    ) -> Dict[str, Any]:
        """
        Analyze error with AI-powered insights

        Args:
            error_message: The error message
            stack_trace: Stack trace if available
            code: Code that caused the error
            language: Programming language

        Returns:
            Analysis result with suggestions
        """
        try:
            # Identify error type
            error_type = self._identify_error_type(error_message)

            # Extract error details
            error_details = self._extract_error_details(error_message, stack_trace)

            # Get common fixes
            fixes = self.common_fixes.get(error_type, [])

            # Analyze code if provided
            code_analysis = None
            if code:
                code_analysis = self._analyze_code_context(code, error_details)

            # Generate fix suggestions
            fix_suggestions = self._generate_fix_suggestions(
                error_type, error_details, code_analysis
            )

            # Calculate severity
            severity = self._calculate_error_severity(error_type, error_details)

            return {
                "success": True,
                "error_type": error_type,
                "severity": severity,
                "root_cause": error_details.get("root_cause", "Unknown"),
                "line_number": error_details.get("line_number"),
                "file_path": error_details.get("file_path"),
                "fix_suggestions": fix_suggestions,
                "common_fixes": fixes,
                "code_analysis": code_analysis,
                "stack_trace_analysis": (
                    self._analyze_stack_trace(stack_trace) if stack_trace else None
                ),
            }

        except Exception as e:
            logger.error(f"Error analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def _identify_error_type(self, error_message: str) -> str:
        """Identify the type of error from message"""
        for error_type, pattern in self.error_patterns.items():
            if re.search(pattern, error_message, re.IGNORECASE):
                return error_type
        return "unknown_error"

    def _extract_error_details(
        self, error_message: str, stack_trace: Optional[str]
    ) -> Dict[str, Any]:
        """Extract detailed information from error"""
        details = {
            "message": error_message,
            "root_cause": (
                error_message.split(":")[-1].strip()
                if ":" in error_message
                else error_message
            ),
        }

        # Extract line number and file from stack trace
        if stack_trace:
            # Look for file and line number patterns
            file_pattern = r'File "([^"]+)", line (\d+)'
            matches = re.findall(file_pattern, stack_trace)
            if matches:
                details["file_path"] = matches[-1][0]
                details["line_number"] = int(matches[-1][1])

        return details

    def _analyze_code_context(
        self, code: str, error_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze code context around error"""
        try:
            lines = code.split("\n")
            line_num = error_details.get("line_number", 0)

            # Get context lines
            start = max(0, line_num - 3)
            end = min(len(lines), line_num + 3)
            context_lines = lines[start:end]

            # Analyze for common issues
            issues = []

            # Check for common Python issues
            if line_num > 0 and line_num <= len(lines):
                error_line = lines[line_num - 1]

                # Check indentation
                if error_line.strip() and error_line[0] in [" ", "\t"]:
                    issues.append("Possible indentation issue")

                # Check for unclosed brackets
                if error_line.count("(") != error_line.count(")"):
                    issues.append("Unclosed parentheses")
                if error_line.count("[") != error_line.count("]"):
                    issues.append("Unclosed brackets")
                if error_line.count("{") != error_line.count("}"):
                    issues.append("Unclosed braces")

            return {
                "context_lines": context_lines,
                "start_line": start + 1,
                "end_line": end,
                "issues": issues,
            }

        except Exception as e:
            logger.error(f"Code context analysis failed: {str(e)}")
            return {}

    def _generate_fix_suggestions(
        self,
        error_type: str,
        error_details: Dict[str, Any],
        code_analysis: Optional[Dict[str, Any]],
    ) -> List[str]:
        """Generate specific fix suggestions"""
        suggestions = []

        # Add type-specific suggestions
        if error_type in self.common_fixes:
            suggestions.extend(self.common_fixes[error_type])

        # Add context-specific suggestions
        if code_analysis and code_analysis.get("issues"):
            for issue in code_analysis["issues"]:
                if "indentation" in issue.lower():
                    suggestions.append(
                        "Fix indentation - use consistent spaces (4 spaces recommended)"
                    )
                elif "parentheses" in issue.lower():
                    suggestions.append("Add missing closing parenthesis")
                elif "brackets" in issue.lower():
                    suggestions.append("Add missing closing bracket")

        # Add general suggestions
        suggestions.extend(
            [
                "Review the error line and surrounding code",
                "Check variable names and types",
                "Verify function arguments and return values",
            ]
        )

        return suggestions[:5]  # Return top 5 suggestions

    def _calculate_error_severity(
        self, error_type: str, error_details: Dict[str, Any]
    ) -> str:
        """Calculate error severity"""
        critical_errors = ["memory_error", "recursion_error", "system_exit"]
        high_errors = ["zero_division", "file_not_found", "permission_error"]
        medium_errors = ["type_error", "value_error", "attribute_error"]

        if error_type in critical_errors:
            return "critical"
        elif error_type in high_errors:
            return "high"
        elif error_type in medium_errors:
            return "medium"
        else:
            return "low"

    def _analyze_stack_trace(self, stack_trace: str) -> Dict[str, Any]:
        """Analyze stack trace for insights"""
        try:
            lines = stack_trace.split("\n")

            # Extract call stack
            call_stack = []
            file_pattern = r'File "([^"]+)", line (\d+), in (.+)'

            for line in lines:
                match = re.search(file_pattern, line)
                if match:
                    call_stack.append(
                        {
                            "file": match.group(1),
                            "line": int(match.group(2)),
                            "function": match.group(3),
                        }
                    )

            return {
                "call_stack": call_stack,
                "depth": len(call_stack),
                "entry_point": call_stack[0] if call_stack else None,
                "error_location": call_stack[-1] if call_stack else None,
            }

        except Exception as e:
            logger.error(f"Stack trace analysis failed: {str(e)}")
            return {}

    async def set_breakpoint(
        self, file_path: str, line_number: int, condition: Optional[str] = None
    ) -> Breakpoint:
        """
        Set a smart breakpoint

        Args:
            file_path: File path
            line_number: Line number
            condition: Optional condition for breakpoint

        Returns:
            Breakpoint object
        """
        breakpoint_id = f"bp_{len(self.breakpoints) + 1}"

        breakpoint = Breakpoint(
            id=breakpoint_id,
            file_path=file_path,
            line_number=line_number,
            condition=condition,
            enabled=True,
            hit_count=0,
            created_at=datetime.now().isoformat(),
        )

        self.breakpoints[breakpoint_id] = breakpoint

        logger.info(f"Breakpoint set: {file_path}:{line_number}")

        return breakpoint

    async def list_breakpoints(self) -> List[Breakpoint]:
        """List all breakpoints"""
        return list(self.breakpoints.values())

    async def remove_breakpoint(self, breakpoint_id: str) -> bool:
        """Remove a breakpoint"""
        if breakpoint_id in self.breakpoints:
            del self.breakpoints[breakpoint_id]
            return True
        return False

    async def toggle_breakpoint(self, breakpoint_id: str) -> bool:
        """Enable/disable a breakpoint"""
        if breakpoint_id in self.breakpoints:
            self.breakpoints[breakpoint_id].enabled = not self.breakpoints[
                breakpoint_id
            ].enabled
            return True
        return False

    async def inspect_variable(
        self, variable_name: str, context: Dict[str, Any]
    ) -> VariableInfo:
        """
        Inspect a variable's value and properties

        Args:
            variable_name: Variable name
            context: Execution context containing variables

        Returns:
            Variable information
        """
        try:
            # Get variable from context
            value = context.get(variable_name)

            if value is None:
                raise ValueError(f"Variable '{variable_name}' not found in context")

            # Get variable info
            var_type = type(value).__name__
            var_size = sys.getsizeof(value)
            memory_addr = hex(id(value))
            is_mutable = not isinstance(
                value, (int, float, str, tuple, frozenset, bytes)
            )

            return VariableInfo(
                name=variable_name,
                value=value,
                type=var_type,
                size=var_size,
                memory_address=memory_addr,
                is_mutable=is_mutable,
            )

        except Exception as e:
            logger.error(f"Variable inspection failed: {str(e)}")
            raise

    async def profile_code(self, code: str, language: str = "python") -> ProfileResult:
        """
        Profile code performance

        Args:
            code: Code to profile
            language: Programming language

        Returns:
            Profiling results
        """
        try:
            # Get initial metrics
            process = psutil.Process()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
            start_cpu = process.cpu_percent()
            start_time = time.time()

            # Execute code (in safe environment)
            # Note: In production, this should use sandboxed execution
            exec_globals = {}
            function_calls = 0

            try:
                exec(code, exec_globals)
            except Exception as e:
                logger.warning(f"Code execution error during profiling: {str(e)}")

            # Get final metrics
            end_time = time.time()
            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            end_cpu = process.cpu_percent()

            execution_time = end_time - start_time
            memory_usage = end_memory - start_memory
            cpu_usage = (start_cpu + end_cpu) / 2

            # Identify hotspots (simplified)
            hotspots = self._identify_hotspots(code)

            return ProfileResult(
                execution_time=execution_time,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                function_calls=function_calls,
                hotspots=hotspots,
            )

        except Exception as e:
            logger.error(f"Code profiling failed: {str(e)}")
            raise

    def _identify_hotspots(self, code: str) -> List[Dict[str, Any]]:
        """Identify performance hotspots in code"""
        hotspots = []
        lines = code.split("\n")

        # Look for common performance issues
        for i, line in enumerate(lines, 1):
            # Nested loops
            if "for" in line and any("for" in l for l in lines[i : i + 5]):
                hotspots.append(
                    {
                        "line": i,
                        "type": "nested_loop",
                        "severity": "high",
                        "description": "Nested loop detected - potential O(n²) complexity",
                    }
                )

            # Large list comprehensions
            if "[" in line and "for" in line and len(line) > 80:
                hotspots.append(
                    {
                        "line": i,
                        "type": "complex_comprehension",
                        "severity": "medium",
                        "description": "Complex list comprehension - consider breaking down",
                    }
                )

            # String concatenation in loops
            if ("+" in line or "+=" in line) and "str" in line.lower():
                hotspots.append(
                    {
                        "line": i,
                        "type": "string_concat",
                        "severity": "medium",
                        "description": "String concatenation - consider using join()",
                    }
                )

        return hotspots[:10]  # Return top 10 hotspots

    async def detect_memory_leaks(
        self, code: str, language: str = "python"
    ) -> List[MemoryLeak]:
        """
        Detect potential memory leaks in code

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            List of potential memory leaks
        """
        leaks = []
        lines = code.split("\n")

        try:
            # Check for common memory leak patterns
            for i, line in enumerate(lines, 1):
                # Unclosed file handles
                if "open(" in line and "with" not in line:
                    leaks.append(
                        MemoryLeak(
                            location=f"Line {i}",
                            line_number=i,
                            leak_type="unclosed_file",
                            severity="high",
                            description="File opened without 'with' statement",
                            suggestion="Use 'with open(...) as f:' to ensure file is closed",
                        )
                    )

                # Global variables accumulation
                if line.strip().startswith("global ") and "append" in line:
                    leaks.append(
                        MemoryLeak(
                            location=f"Line {i}",
                            line_number=i,
                            leak_type="global_accumulation",
                            severity="medium",
                            description="Global variable accumulation detected",
                            suggestion="Clear global collections periodically or use local variables",
                        )
                    )

                # Circular references
                if "self." in line and "=" in line and "self" in line.split("=")[1]:
                    leaks.append(
                        MemoryLeak(
                            location=f"Line {i}",
                            line_number=i,
                            leak_type="circular_reference",
                            severity="medium",
                            description="Potential circular reference",
                            suggestion="Use weak references or break circular references explicitly",
                        )
                    )

                # Large data structures in loops
                if any(
                    keyword in line for keyword in ["list(", "dict(", "set("]
                ) and any("for" in l or "while" in l for l in lines[max(0, i - 5) : i]):
                    leaks.append(
                        MemoryLeak(
                            location=f"Line {i}",
                            line_number=i,
                            leak_type="loop_allocation",
                            severity="low",
                            description="Data structure created in loop",
                            suggestion="Consider creating outside loop or using generators",
                        )
                    )

            return leaks

        except Exception as e:
            logger.error(f"Memory leak detection failed: {str(e)}")
            return []

    async def get_call_stack(self, execution_id: str) -> List[Dict[str, Any]]:
        """
        Get call stack for an execution

        Args:
            execution_id: Execution identifier

        Returns:
            Call stack information
        """
        # In a real implementation, this would retrieve from execution history
        # For now, return a sample call stack
        return [
            {
                "frame": 0,
                "function": "main",
                "file": "main.py",
                "line": 10,
                "locals": {},
            }
        ]

    async def get_code_coverage(self, project_id: str) -> Dict[str, Any]:
        """
        Get code coverage statistics

        Args:
            project_id: Project identifier

        Returns:
            Coverage statistics
        """
        # In a real implementation, this would analyze actual coverage data
        # For now, return sample coverage data
        return {
            "total_lines": 1000,
            "covered_lines": 850,
            "percentage": 85.0,
            "uncovered_files": [{"file": "utils.py", "uncovered_lines": [45, 67, 89]}],
            "coverage_by_file": {"main.py": 95.0, "utils.py": 75.0, "helpers.py": 88.0},
        }
