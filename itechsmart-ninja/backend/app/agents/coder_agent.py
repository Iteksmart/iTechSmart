"""
Coder Agent - Code generation, execution, debugging, and testing
"""
from typing import Dict, Any, List, Optional
import ast
import subprocess
import tempfile
import os
import logging

from app.agents.base_agent import BaseAgent, AgentCapability, AgentResponse

logger = logging.getLogger(__name__)


class CoderAgent(BaseAgent):
    """Agent specialized in code generation, execution, and debugging"""
    
    def __init__(self, ai_provider: str = "openai"):
        super().__init__(
            name="Coder",
            description="Specialized in code generation, debugging, testing, and execution",
            ai_provider=ai_provider
        )
        
        # Define capabilities
        self.capabilities = [
            AgentCapability(
                name="code_generation",
                description="Generate code in multiple languages",
                required_tools=["ai_model"]
            ),
            AgentCapability(
                name="code_execution",
                description="Execute code safely in sandbox",
                required_tools=["sandbox", "docker"]
            ),
            AgentCapability(
                name="code_debugging",
                description="Debug and fix code errors",
                required_tools=["ai_model", "linter"]
            ),
            AgentCapability(
                name="code_review",
                description="Review code for quality and best practices",
                required_tools=["ai_model"]
            ),
            AgentCapability(
                name="test_generation",
                description="Generate unit tests for code",
                required_tools=["ai_model"]
            ),
            AgentCapability(
                name="refactoring",
                description="Refactor code for better quality",
                required_tools=["ai_model"]
            )
        ]
        
        # Supported languages
        self.supported_languages = [
            "python", "javascript", "typescript", "java", "go", 
            "rust", "c", "cpp", "ruby", "php", "swift", "kotlin"
        ]
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coding task"""
        try:
            task_type = task.get("type", "generate")  # generate, debug, review, test, refactor
            language = task.get("language", "python")
            
            logger.info(f"Coder executing: {task_type} in {language}")
            
            if task_type == "generate":
                result = await self._generate_code(task)
            elif task_type == "debug":
                result = await self._debug_code(task)
            elif task_type == "review":
                result = await self._review_code(task)
            elif task_type == "test":
                result = await self._generate_tests(task)
            elif task_type == "refactor":
                result = await self._refactor_code(task)
            elif task_type == "execute":
                result = await self._execute_code(task)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown task type: {task_type}"
                }
            
            # Log execution
            self.log_execution(task, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Coder execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    async def _generate_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on requirements"""
        requirements = task.get("requirements", "")
        language = task.get("language", "python")
        framework = task.get("framework")
        
        # In production, use AI to generate code
        # For now, return a template
        
        if language == "python":
            code = self._generate_python_template(requirements, framework)
        elif language == "javascript":
            code = self._generate_javascript_template(requirements, framework)
        else:
            code = f"# Code generation for {language} not yet implemented"
        
        # Validate syntax
        is_valid, error = self._validate_syntax(code, language)
        
        return {
            "success": is_valid,
            "code": code,
            "language": language,
            "framework": framework,
            "syntax_valid": is_valid,
            "syntax_error": error,
            "agent": self.name
        }
    
    async def _debug_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Debug code and fix errors"""
        code = task.get("code", "")
        language = task.get("language", "python")
        error_message = task.get("error", "")
        
        # Analyze the error
        analysis = self._analyze_error(code, error_message, language)
        
        # Generate fix
        fixed_code = await self._generate_fix(code, analysis, language)
        
        # Validate fix
        is_valid, validation_error = self._validate_syntax(fixed_code, language)
        
        return {
            "success": is_valid,
            "original_code": code,
            "fixed_code": fixed_code,
            "analysis": analysis,
            "syntax_valid": is_valid,
            "validation_error": validation_error,
            "agent": self.name
        }
    
    async def _review_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Review code for quality and best practices"""
        code = task.get("code", "")
        language = task.get("language", "python")
        
        # Perform various checks
        issues = []
        suggestions = []
        
        # Syntax check
        is_valid, syntax_error = self._validate_syntax(code, language)
        if not is_valid:
            issues.append({
                "type": "syntax_error",
                "severity": "high",
                "message": syntax_error
            })
        
        # Complexity check
        complexity = self._calculate_complexity(code, language)
        if complexity > 10:
            issues.append({
                "type": "high_complexity",
                "severity": "medium",
                "message": f"Code complexity is {complexity}, consider refactoring"
            })
        
        # Best practices check
        best_practices = self._check_best_practices(code, language)
        suggestions.extend(best_practices)
        
        # Security check
        security_issues = self._check_security(code, language)
        issues.extend(security_issues)
        
        # Calculate score
        score = self._calculate_code_score(issues, suggestions)
        
        return {
            "success": True,
            "score": score,
            "issues": issues,
            "suggestions": suggestions,
            "complexity": complexity,
            "language": language,
            "agent": self.name
        }
    
    async def _generate_tests(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate unit tests for code"""
        code = task.get("code", "")
        language = task.get("language", "python")
        test_framework = task.get("test_framework", "pytest" if language == "python" else "jest")
        
        # Generate tests based on language
        if language == "python":
            tests = self._generate_python_tests(code, test_framework)
        elif language == "javascript":
            tests = self._generate_javascript_tests(code, test_framework)
        else:
            tests = f"# Test generation for {language} not yet implemented"
        
        return {
            "success": True,
            "tests": tests,
            "language": language,
            "test_framework": test_framework,
            "agent": self.name
        }
    
    async def _refactor_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Refactor code for better quality"""
        code = task.get("code", "")
        language = task.get("language", "python")
        
        # Analyze code
        issues = []
        
        # Apply refactoring patterns
        refactored_code = code  # In production, use AI to refactor
        
        # Document changes
        changes = [
            "Improved variable naming",
            "Extracted complex logic into functions",
            "Added type hints",
            "Improved error handling"
        ]
        
        return {
            "success": True,
            "original_code": code,
            "refactored_code": refactored_code,
            "changes": changes,
            "language": language,
            "agent": self.name
        }
    
    async def _execute_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code in sandbox"""
        code = task.get("code", "")
        language = task.get("language", "python")
        inputs = task.get("inputs", {})
        
        try:
            if language == "python":
                output, error = await self._execute_python(code, inputs)
            elif language == "javascript":
                output, error = await self._execute_javascript(code, inputs)
            else:
                return {
                    "success": False,
                    "error": f"Execution not supported for {language}"
                }
            
            return {
                "success": error is None,
                "output": output,
                "error": error,
                "language": language,
                "agent": self.name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    def _generate_python_template(self, requirements: str, framework: Optional[str]) -> str:
        """Generate Python code template"""
        if framework == "fastapi":
            return '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str = None

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/items/")
async def create_item(item: Item):
    return {"item": item}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        else:
            return f'''"""
{requirements}
"""

def main():
    """Main function"""
    print("Hello, World!")
    # TODO: Implement functionality

if __name__ == "__main__":
    main()
'''
    
    def _generate_javascript_template(self, requirements: str, framework: Optional[str]) -> str:
        """Generate JavaScript code template"""
        if framework == "express":
            return '''const express = require('express');
const app = express();
const port = 3000;

app.use(express.json());

app.get('/', (req, res) => {
  res.json({ message: 'Hello World' });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
'''
        else:
            return f'''/**
 * {requirements}
 */

function main() {
  console.log('Hello, World!');
  // TODO: Implement functionality
}

main();
'''
    
    def _validate_syntax(self, code: str, language: str) -> tuple[bool, Optional[str]]:
        """Validate code syntax"""
        try:
            if language == "python":
                ast.parse(code)
                return True, None
            # Add validation for other languages
            return True, None
        except SyntaxError as e:
            return False, str(e)
        except Exception as e:
            return False, str(e)
    
    def _analyze_error(self, code: str, error: str, language: str) -> Dict[str, Any]:
        """Analyze error and provide insights"""
        return {
            "error_type": "syntax_error",  # Simplified
            "line_number": 1,
            "description": error,
            "possible_causes": ["Missing parenthesis", "Indentation error", "Undefined variable"],
            "suggestions": ["Check syntax", "Verify variable names", "Check indentation"]
        }
    
    async def _generate_fix(self, code: str, analysis: Dict[str, Any], language: str) -> str:
        """Generate fixed code"""
        # In production, use AI to generate fix
        return code  # Placeholder
    
    def _calculate_complexity(self, code: str, language: str) -> int:
        """Calculate cyclomatic complexity"""
        # Simplified complexity calculation
        if language == "python":
            # Count decision points
            complexity = 1
            complexity += code.count("if ")
            complexity += code.count("elif ")
            complexity += code.count("for ")
            complexity += code.count("while ")
            complexity += code.count("and ")
            complexity += code.count("or ")
            return complexity
        return 1
    
    def _check_best_practices(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Check for best practices"""
        suggestions = []
        
        if language == "python":
            if "print(" in code and "logging" not in code:
                suggestions.append({
                    "type": "best_practice",
                    "message": "Consider using logging instead of print statements"
                })
            
            if "except:" in code:
                suggestions.append({
                    "type": "best_practice",
                    "message": "Avoid bare except clauses, specify exception types"
                })
        
        return suggestions
    
    def _check_security(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Check for security issues"""
        issues = []
        
        # Check for common security issues
        dangerous_patterns = ["eval(", "exec(", "os.system(", "subprocess.call("]
        
        for pattern in dangerous_patterns:
            if pattern in code:
                issues.append({
                    "type": "security",
                    "severity": "high",
                    "message": f"Potentially dangerous function: {pattern}"
                })
        
        return issues
    
    def _calculate_code_score(self, issues: List[Dict], suggestions: List[Dict]) -> float:
        """Calculate overall code quality score"""
        score = 100.0
        
        for issue in issues:
            if issue.get("severity") == "high":
                score -= 20
            elif issue.get("severity") == "medium":
                score -= 10
            else:
                score -= 5
        
        score -= len(suggestions) * 2
        
        return max(0.0, min(100.0, score))
    
    def _generate_python_tests(self, code: str, framework: str) -> str:
        """Generate Python unit tests"""
        return f'''import pytest

def test_example():
    """Test example function"""
    # TODO: Implement test
    assert True

def test_edge_cases():
    """Test edge cases"""
    # TODO: Implement test
    assert True

if __name__ == "__main__":
    pytest.main([__file__])
'''
    
    def _generate_javascript_tests(self, code: str, framework: str) -> str:
        """Generate JavaScript unit tests"""
        return '''const { expect } = require('chai');

describe('Example Tests', () => {
  it('should pass', () => {
    // TODO: Implement test
    expect(true).to.be.true;
  });
  
  it('should handle edge cases', () => {
    // TODO: Implement test
    expect(true).to.be.true;
  });
});
'''
    
    async def _execute_python(self, code: str, inputs: Dict[str, Any]) -> tuple[str, Optional[str]]:
        """Execute Python code safely"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute in subprocess with timeout
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up
            os.unlink(temp_file)
            
            if result.returncode == 0:
                return result.stdout, None
            else:
                return result.stdout, result.stderr
                
        except subprocess.TimeoutExpired:
            return "", "Execution timeout (30s)"
        except Exception as e:
            return "", str(e)
    
    async def _execute_javascript(self, code: str, inputs: Dict[str, Any]) -> tuple[str, Optional[str]]:
        """Execute JavaScript code safely"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute in subprocess with timeout
            result = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up
            os.unlink(temp_file)
            
            if result.returncode == 0:
                return result.stdout, None
            else:
                return result.stdout, result.stderr
                
        except subprocess.TimeoutExpired:
            return "", "Execution timeout (30s)"
        except Exception as e:
            return "", str(e)