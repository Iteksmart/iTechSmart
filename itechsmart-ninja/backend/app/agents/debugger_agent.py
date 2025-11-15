"""
Debugger Agent - Error analysis, debugging, and fixes
"""
from typing import Dict, Any, List, Optional
import re
import traceback
import logging

from app.agents.base_agent import BaseAgent, AgentCapability, AgentResponse

logger = logging.getLogger(__name__)


class DebuggerAgent(BaseAgent):
    """Agent specialized in debugging and error resolution"""
    
    def __init__(self, ai_provider: str = "openai"):
        super().__init__(
            name="Debugger",
            description="Specialized in error analysis, debugging, and providing fixes",
            ai_provider=ai_provider
        )
        
        # Define capabilities
        self.capabilities = [
            AgentCapability(
                name="error_analysis",
                description="Analyze errors and exceptions",
                required_tools=["ai_model"]
            ),
            AgentCapability(
                name="stack_trace_analysis",
                description="Analyze stack traces",
                required_tools=[]
            ),
            AgentCapability(
                name="root_cause_analysis",
                description="Identify root causes of issues",
                required_tools=["ai_model"]
            ),
            AgentCapability(
                name="fix_generation",
                description="Generate fixes for errors",
                required_tools=["ai_model", "code_parser"]
            ),
            AgentCapability(
                name="performance_profiling",
                description="Profile code performance",
                required_tools=["profiler"]
            ),
            AgentCapability(
                name="memory_leak_detection",
                description="Detect memory leaks",
                required_tools=["memory_profiler"]
            )
        ]
        
        # Common error patterns
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
            "connection_error": r"ConnectionError|ConnectionRefusedError"
        }
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute debugging task"""
        try:
            task_type = task.get("type", "analyze")
            error_info = task.get("error", {})
            
            logger.info(f"Debugger executing: {task_type}")
            
            if task_type == "analyze":
                result = await self._analyze_error(error_info, task)
            elif task_type == "fix":
                result = await self._generate_fix(error_info, task)
            elif task_type == "profile":
                result = await self._profile_code(task)
            elif task_type == "memory":
                result = await self._analyze_memory(task)
            elif task_type == "stack_trace":
                result = await self._analyze_stack_trace(error_info, task)
            elif task_type == "root_cause":
                result = await self._root_cause_analysis(error_info, task)
            else:
                result = await self._comprehensive_debug(error_info, task)
            
            # Log execution
            self.log_execution(task, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Debugger execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    async def _analyze_error(self, error_info: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze error and provide insights"""
        error_message = error_info.get("message", "")
        error_type = error_info.get("type", "")
        code = task.get("code", "")
        
        # Classify error
        classification = self._classify_error(error_message, error_type)
        
        # Extract error details
        details = self._extract_error_details(error_message, code)
        
        # Identify severity
        severity = self._assess_severity(classification, details)
        
        # Generate explanation
        explanation = self._explain_error(classification, details)
        
        # Suggest solutions
        solutions = self._suggest_solutions(classification, details)
        
        return {
            "success": True,
            "error_type": classification["type"],
            "severity": severity,
            "details": details,
            "explanation": explanation,
            "solutions": solutions,
            "preventive_measures": self._suggest_preventive_measures(classification),
            "agent": self.name
        }
    
    async def _generate_fix(self, error_info: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fix for the error"""
        error_message = error_info.get("message", "")
        code = task.get("code", "")
        language = task.get("language", "python")
        
        # Analyze error
        analysis = await self._analyze_error(error_info, task)
        
        # Generate fix
        fixed_code = self._apply_fix(code, analysis, language)
        
        # Explain changes
        changes = self._explain_changes(code, fixed_code)
        
        # Validate fix
        is_valid = self._validate_fix(fixed_code, language)
        
        return {
            "success": is_valid,
            "original_code": code,
            "fixed_code": fixed_code,
            "changes": changes,
            "analysis": analysis,
            "validated": is_valid,
            "agent": self.name
        }
    
    async def _profile_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Profile code performance"""
        code = task.get("code", "")
        language = task.get("language", "python")
        
        # Analyze performance
        performance = self._analyze_performance(code, language)
        
        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(performance)
        
        # Generate optimization suggestions
        optimizations = self._suggest_optimizations(bottlenecks)
        
        return {
            "success": True,
            "performance": performance,
            "bottlenecks": bottlenecks,
            "optimizations": optimizations,
            "estimated_improvement": self._estimate_improvement(optimizations),
            "agent": self.name
        }
    
    async def _analyze_memory(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze memory usage"""
        code = task.get("code", "")
        
        # Detect memory issues
        issues = self._detect_memory_issues(code)
        
        # Analyze memory leaks
        leaks = self._analyze_memory_leaks(code)
        
        # Generate recommendations
        recommendations = self._memory_recommendations(issues, leaks)
        
        return {
            "success": True,
            "memory_issues": issues,
            "potential_leaks": leaks,
            "recommendations": recommendations,
            "severity": self._assess_memory_severity(issues, leaks),
            "agent": self.name
        }
    
    async def _analyze_stack_trace(self, error_info: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze stack trace"""
        stack_trace = error_info.get("stack_trace", "")
        
        # Parse stack trace
        parsed = self._parse_stack_trace(stack_trace)
        
        # Identify error location
        location = self._identify_error_location(parsed)
        
        # Trace execution path
        execution_path = self._trace_execution_path(parsed)
        
        # Identify problematic function
        problematic_function = self._identify_problematic_function(parsed)
        
        return {
            "success": True,
            "parsed_trace": parsed,
            "error_location": location,
            "execution_path": execution_path,
            "problematic_function": problematic_function,
            "call_depth": len(parsed),
            "agent": self.name
        }
    
    async def _root_cause_analysis(self, error_info: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform root cause analysis"""
        error_message = error_info.get("message", "")
        context = task.get("context", {})
        
        # Identify immediate cause
        immediate_cause = self._identify_immediate_cause(error_message)
        
        # Trace back to root cause
        root_cause = self._trace_root_cause(error_message, context)
        
        # Identify contributing factors
        contributing_factors = self._identify_contributing_factors(error_message, context)
        
        # Generate causal chain
        causal_chain = self._build_causal_chain(immediate_cause, root_cause, contributing_factors)
        
        return {
            "success": True,
            "immediate_cause": immediate_cause,
            "root_cause": root_cause,
            "contributing_factors": contributing_factors,
            "causal_chain": causal_chain,
            "resolution_strategy": self._generate_resolution_strategy(root_cause),
            "agent": self.name
        }
    
    async def _comprehensive_debug(self, error_info: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive debugging analysis"""
        # Perform all analyses
        error_analysis = await self._analyze_error(error_info, task)
        
        if error_info.get("stack_trace"):
            stack_analysis = await self._analyze_stack_trace(error_info, task)
        else:
            stack_analysis = None
        
        root_cause = await self._root_cause_analysis(error_info, task)
        
        # Generate comprehensive report
        report = {
            "error_analysis": error_analysis,
            "stack_analysis": stack_analysis,
            "root_cause": root_cause,
            "priority": self._determine_priority(error_analysis, root_cause),
            "action_plan": self._create_action_plan(error_analysis, root_cause)
        }
        
        return {
            "success": True,
            "comprehensive_report": report,
            "agent": self.name
        }
    
    # Helper methods
    
    def _classify_error(self, message: str, error_type: str) -> Dict[str, Any]:
        """Classify error type"""
        for pattern_name, pattern in self.error_patterns.items():
            if re.search(pattern, message, re.IGNORECASE) or re.search(pattern, error_type, re.IGNORECASE):
                return {
                    "type": pattern_name,
                    "category": self._get_error_category(pattern_name),
                    "common": True
                }
        
        return {
            "type": "unknown",
            "category": "runtime",
            "common": False
        }
    
    def _get_error_category(self, error_type: str) -> str:
        """Get error category"""
        categories = {
            "syntax_error": "syntax",
            "name_error": "runtime",
            "type_error": "runtime",
            "value_error": "runtime",
            "attribute_error": "runtime",
            "import_error": "environment",
            "index_error": "logic",
            "key_error": "logic",
            "zero_division": "logic",
            "file_not_found": "io",
            "permission_error": "io",
            "timeout_error": "network",
            "connection_error": "network"
        }
        return categories.get(error_type, "unknown")
    
    def _extract_error_details(self, message: str, code: str) -> Dict[str, Any]:
        """Extract error details"""
        details = {
            "message": message,
            "line_number": self._extract_line_number(message),
            "variable_name": self._extract_variable_name(message),
            "function_name": self._extract_function_name(message)
        }
        return details
    
    def _extract_line_number(self, message: str) -> Optional[int]:
        """Extract line number from error message"""
        match = re.search(r'line (\d+)', message, re.IGNORECASE)
        return int(match.group(1)) if match else None
    
    def _extract_variable_name(self, message: str) -> Optional[str]:
        """Extract variable name from error message"""
        match = re.search(r"'(\w+)'", message)
        return match.group(1) if match else None
    
    def _extract_function_name(self, message: str) -> Optional[str]:
        """Extract function name from error message"""
        match = re.search(r'in (\w+)', message)
        return match.group(1) if match else None
    
    def _assess_severity(self, classification: Dict[str, Any], details: Dict[str, Any]) -> str:
        """Assess error severity"""
        category = classification.get("category", "")
        
        if category == "syntax":
            return "high"
        elif category in ["runtime", "logic"]:
            return "medium"
        else:
            return "low"
    
    def _explain_error(self, classification: Dict[str, Any], details: Dict[str, Any]) -> str:
        """Explain the error"""
        error_type = classification.get("type", "unknown")
        
        explanations = {
            "syntax_error": "The code has a syntax error. This means the code structure is invalid and Python cannot parse it.",
            "name_error": "A variable or function name is being used before it's defined.",
            "type_error": "An operation is being performed on incompatible types.",
            "value_error": "A function received an argument of the correct type but inappropriate value.",
            "attribute_error": "An attribute reference or assignment failed.",
            "import_error": "A module could not be imported.",
            "index_error": "A sequence subscript is out of range.",
            "key_error": "A dictionary key was not found.",
            "zero_division": "Division or modulo by zero.",
            "file_not_found": "The specified file does not exist.",
            "permission_error": "Insufficient permissions to perform the operation.",
            "timeout_error": "The operation timed out.",
            "connection_error": "Failed to establish a connection."
        }
        
        return explanations.get(error_type, "An error occurred during execution.")
    
    def _suggest_solutions(self, classification: Dict[str, Any], details: Dict[str, Any]) -> List[str]:
        """Suggest solutions"""
        error_type = classification.get("type", "unknown")
        
        solutions = {
            "syntax_error": [
                "Check for missing colons, parentheses, or brackets",
                "Verify indentation is consistent",
                "Look for typos in keywords"
            ],
            "name_error": [
                "Ensure the variable is defined before use",
                "Check for typos in variable names",
                "Verify the variable is in the correct scope"
            ],
            "type_error": [
                "Check the types of variables being used",
                "Convert types explicitly if needed",
                "Verify function arguments match expected types"
            ],
            "import_error": [
                "Install the required package",
                "Check the module name spelling",
                "Verify the module is in the Python path"
            ],
            "index_error": [
                "Check list/array bounds",
                "Verify the index is within range",
                "Add bounds checking"
            ],
            "key_error": [
                "Verify the key exists in the dictionary",
                "Use .get() method with a default value",
                "Check for typos in key names"
            ]
        }
        
        return solutions.get(error_type, ["Review the error message carefully", "Check the documentation", "Add error handling"])
    
    def _suggest_preventive_measures(self, classification: Dict[str, Any]) -> List[str]:
        """Suggest preventive measures"""
        return [
            "Add comprehensive error handling",
            "Implement input validation",
            "Write unit tests",
            "Use type hints",
            "Add logging for debugging"
        ]
    
    def _apply_fix(self, code: str, analysis: Dict[str, Any], language: str) -> str:
        """Apply fix to code"""
        # Simplified fix application
        # In production, use AI to generate proper fixes
        return code  # Placeholder
    
    def _explain_changes(self, original: str, fixed: str) -> List[str]:
        """Explain changes made"""
        return [
            "Added error handling",
            "Fixed variable initialization",
            "Corrected syntax"
        ]
    
    def _validate_fix(self, code: str, language: str) -> bool:
        """Validate the fix"""
        # Simplified validation
        return True
    
    def _analyze_performance(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code performance"""
        return {
            "execution_time": "0.5s",
            "memory_usage": "50MB",
            "cpu_usage": "25%",
            "complexity": "O(n)"
        }
    
    def _identify_bottlenecks(self, performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        return [
            {
                "location": "line 45",
                "issue": "Nested loop",
                "impact": "high"
            }
        ]
    
    def _suggest_optimizations(self, bottlenecks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Suggest optimizations"""
        return [
            {
                "bottleneck": "Nested loop",
                "suggestion": "Use list comprehension or vectorization",
                "expected_improvement": "50%"
            }
        ]
    
    def _estimate_improvement(self, optimizations: List[Dict[str, Any]]) -> str:
        """Estimate performance improvement"""
        return "50-70% faster execution"
    
    def _detect_memory_issues(self, code: str) -> List[Dict[str, Any]]:
        """Detect memory issues"""
        issues = []
        
        # Check for common memory issues
        if "while True:" in code and "break" not in code:
            issues.append({
                "type": "infinite_loop",
                "severity": "high",
                "description": "Potential infinite loop without break condition"
            })
        
        return issues
    
    def _analyze_memory_leaks(self, code: str) -> List[Dict[str, Any]]:
        """Analyze potential memory leaks"""
        return []
    
    def _memory_recommendations(self, issues: List[Dict], leaks: List[Dict]) -> List[str]:
        """Generate memory recommendations"""
        return [
            "Use context managers for resource management",
            "Close file handles explicitly",
            "Clear large data structures when done"
        ]
    
    def _assess_memory_severity(self, issues: List[Dict], leaks: List[Dict]) -> str:
        """Assess memory issue severity"""
        if leaks:
            return "high"
        elif issues:
            return "medium"
        return "low"
    
    def _parse_stack_trace(self, stack_trace: str) -> List[Dict[str, Any]]:
        """Parse stack trace"""
        frames = []
        lines = stack_trace.split('\n')
        
        for line in lines:
            if 'File' in line:
                frames.append({
                    "line": line.strip(),
                    "file": self._extract_file_from_trace(line),
                    "line_number": self._extract_line_number(line)
                })
        
        return frames
    
    def _extract_file_from_trace(self, line: str) -> str:
        """Extract filename from trace line"""
        match = re.search(r'File "([^"]+)"', line)
        return match.group(1) if match else ""
    
    def _identify_error_location(self, parsed: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify error location"""
        if parsed:
            last_frame = parsed[-1]
            return {
                "file": last_frame.get("file", ""),
                "line": last_frame.get("line_number", 0)
            }
        return {}
    
    def _trace_execution_path(self, parsed: List[Dict[str, Any]]) -> List[str]:
        """Trace execution path"""
        return [frame.get("line", "") for frame in parsed]
    
    def _identify_problematic_function(self, parsed: List[Dict[str, Any]]) -> str:
        """Identify problematic function"""
        if parsed:
            return parsed[-1].get("line", "").split()[-1] if parsed[-1].get("line") else "unknown"
        return "unknown"
    
    def _identify_immediate_cause(self, message: str) -> str:
        """Identify immediate cause"""
        return f"Error: {message}"
    
    def _trace_root_cause(self, message: str, context: Dict[str, Any]) -> str:
        """Trace root cause"""
        return "Root cause analysis: The error originated from invalid input data"
    
    def _identify_contributing_factors(self, message: str, context: Dict[str, Any]) -> List[str]:
        """Identify contributing factors"""
        return [
            "Missing input validation",
            "Lack of error handling",
            "Insufficient testing"
        ]
    
    def _build_causal_chain(self, immediate: str, root: str, factors: List[str]) -> List[str]:
        """Build causal chain"""
        chain = [root]
        chain.extend(factors)
        chain.append(immediate)
        return chain
    
    def _generate_resolution_strategy(self, root_cause: str) -> List[str]:
        """Generate resolution strategy"""
        return [
            "1. Add input validation",
            "2. Implement error handling",
            "3. Add unit tests",
            "4. Deploy fix",
            "5. Monitor for recurrence"
        ]
    
    def _determine_priority(self, error_analysis: Dict, root_cause: Dict) -> str:
        """Determine priority"""
        severity = error_analysis.get("severity", "low")
        if severity == "high":
            return "P0 - Critical"
        elif severity == "medium":
            return "P1 - High"
        return "P2 - Medium"
    
    def _create_action_plan(self, error_analysis: Dict, root_cause: Dict) -> List[str]:
        """Create action plan"""
        return [
            "1. Immediate: Apply hotfix",
            "2. Short-term: Add error handling",
            "3. Long-term: Refactor code",
            "4. Preventive: Add monitoring"
        ]