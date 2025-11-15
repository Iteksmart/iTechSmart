"""
Tests for Advanced Debugging functionality
"""

import pytest
from app.integrations.advanced_debugger import AdvancedDebugger, Breakpoint, VariableInfo


@pytest.fixture
def debugger():
    """Create debugger instance"""
    return AdvancedDebugger()


class TestErrorAnalysis:
    """Test error analysis functionality"""
    
    @pytest.mark.asyncio
    async def test_analyze_syntax_error(self, debugger):
        """Test syntax error analysis"""
        error_message = "SyntaxError: invalid syntax"
        stack_trace = 'File "test.py", line 10, in <module>'
        
        result = await debugger.analyze_error(
            error_message=error_message,
            stack_trace=stack_trace
        )
        
        assert result["success"] is True
        assert result["error_type"] == "syntax_error"
        assert result["severity"] in ["low", "medium", "high", "critical"]
        assert len(result["fix_suggestions"]) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_type_error(self, debugger):
        """Test type error analysis"""
        error_message = "TypeError: unsupported operand type(s)"
        
        result = await debugger.analyze_error(error_message=error_message)
        
        assert result["success"] is True
        assert result["error_type"] == "type_error"
        assert "type" in result["root_cause"].lower()
    
    @pytest.mark.asyncio
    async def test_analyze_with_code_context(self, debugger):
        """Test error analysis with code context"""
        error_message = "NameError: name 'x' is not defined"
        code = """
def test():
    print(x)
    
test()
"""
        
        result = await debugger.analyze_error(
            error_message=error_message,
            code=code
        )
        
        assert result["success"] is True
        assert result["code_analysis"] is not None


class TestBreakpoints:
    """Test breakpoint functionality"""
    
    @pytest.mark.asyncio
    async def test_set_breakpoint(self, debugger):
        """Test setting a breakpoint"""
        breakpoint = await debugger.set_breakpoint(
            file_path="test.py",
            line_number=10
        )
        
        assert isinstance(breakpoint, Breakpoint)
        assert breakpoint.file_path == "test.py"
        assert breakpoint.line_number == 10
        assert breakpoint.enabled is True
    
    @pytest.mark.asyncio
    async def test_set_conditional_breakpoint(self, debugger):
        """Test setting a conditional breakpoint"""
        breakpoint = await debugger.set_breakpoint(
            file_path="test.py",
            line_number=10,
            condition="x > 5"
        )
        
        assert breakpoint.condition == "x > 5"
    
    @pytest.mark.asyncio
    async def test_list_breakpoints(self, debugger):
        """Test listing breakpoints"""
        await debugger.set_breakpoint("test1.py", 10)
        await debugger.set_breakpoint("test2.py", 20)
        
        breakpoints = await debugger.list_breakpoints()
        
        assert len(breakpoints) == 2
    
    @pytest.mark.asyncio
    async def test_remove_breakpoint(self, debugger):
        """Test removing a breakpoint"""
        breakpoint = await debugger.set_breakpoint("test.py", 10)
        
        success = await debugger.remove_breakpoint(breakpoint.id)
        
        assert success is True
        
        breakpoints = await debugger.list_breakpoints()
        assert len(breakpoints) == 0
    
    @pytest.mark.asyncio
    async def test_toggle_breakpoint(self, debugger):
        """Test toggling a breakpoint"""
        breakpoint = await debugger.set_breakpoint("test.py", 10)
        
        await debugger.toggle_breakpoint(breakpoint.id)
        
        breakpoints = await debugger.list_breakpoints()
        assert breakpoints[0].enabled is False


class TestVariableInspection:
    """Test variable inspection functionality"""
    
    @pytest.mark.asyncio
    async def test_inspect_string_variable(self, debugger):
        """Test inspecting a string variable"""
        context = {"test_var": "hello world"}
        
        var_info = await debugger.inspect_variable("test_var", context)
        
        assert isinstance(var_info, VariableInfo)
        assert var_info.name == "test_var"
        assert var_info.type == "str"
        assert var_info.is_mutable is False
    
    @pytest.mark.asyncio
    async def test_inspect_list_variable(self, debugger):
        """Test inspecting a list variable"""
        context = {"test_list": [1, 2, 3]}
        
        var_info = await debugger.inspect_variable("test_list", context)
        
        assert var_info.type == "list"
        assert var_info.is_mutable is True
    
    @pytest.mark.asyncio
    async def test_inspect_nonexistent_variable(self, debugger):
        """Test inspecting a non-existent variable"""
        context = {}
        
        with pytest.raises(ValueError):
            await debugger.inspect_variable("nonexistent", context)


class TestCodeProfiling:
    """Test code profiling functionality"""
    
    @pytest.mark.asyncio
    async def test_profile_simple_code(self, debugger):
        """Test profiling simple code"""
        code = """
x = 0
for i in range(100):
    x += i
"""
        
        result = await debugger.profile_code(code)
        
        assert result.execution_time >= 0
        assert result.memory_usage >= 0
        assert result.cpu_usage >= 0
    
    @pytest.mark.asyncio
    async def test_profile_identifies_hotspots(self, debugger):
        """Test that profiling identifies hotspots"""
        code = """
for i in range(10):
    for j in range(10):
        x = i * j
"""
        
        result = await debugger.profile_code(code)
        
        # Should identify nested loop
        assert len(result.hotspots) > 0


class TestMemoryLeakDetection:
    """Test memory leak detection functionality"""
    
    @pytest.mark.asyncio
    async def test_detect_unclosed_file(self, debugger):
        """Test detecting unclosed file handles"""
        code = """
f = open('test.txt', 'r')
data = f.read()
"""
        
        leaks = await debugger.detect_memory_leaks(code)
        
        # Should detect unclosed file
        assert len(leaks) > 0
        assert any(leak.leak_type == "unclosed_file" for leak in leaks)
    
    @pytest.mark.asyncio
    async def test_detect_global_accumulation(self, debugger):
        """Test detecting global variable accumulation"""
        code = """
global data
data = []
for i in range(1000):
    data.append(i)
"""
        
        leaks = await debugger.detect_memory_leaks(code)
        
        # Should detect global accumulation
        assert any(leak.leak_type == "global_accumulation" for leak in leaks)
    
    @pytest.mark.asyncio
    async def test_no_leaks_in_clean_code(self, debugger):
        """Test that clean code has no leaks"""
        code = """
with open('test.txt', 'r') as f:
    data = f.read()
"""
        
        leaks = await debugger.detect_memory_leaks(code)
        
        # Should not detect unclosed file leak
        assert not any(leak.leak_type == "unclosed_file" for leak in leaks)


class TestCallStack:
    """Test call stack functionality"""
    
    @pytest.mark.asyncio
    async def test_get_call_stack(self, debugger):
        """Test getting call stack"""
        call_stack = await debugger.get_call_stack("exec_123")
        
        assert isinstance(call_stack, list)
        assert len(call_stack) > 0


class TestCodeCoverage:
    """Test code coverage functionality"""
    
    @pytest.mark.asyncio
    async def test_get_code_coverage(self, debugger):
        """Test getting code coverage"""
        coverage = await debugger.get_code_coverage("test_project")
        
        assert "total_lines" in coverage
        assert "covered_lines" in coverage
        assert "percentage" in coverage
        assert coverage["percentage"] >= 0
        assert coverage["percentage"] <= 100


class TestStackTraceAnalysis:
    """Test stack trace analysis"""
    
    def test_analyze_stack_trace(self, debugger):
        """Test analyzing stack trace"""
        stack_trace = """
Traceback (most recent call last):
  File "main.py", line 10, in <module>
    result = divide(10, 0)
  File "utils.py", line 5, in divide
    return a / b
ZeroDivisionError: division by zero
"""
        
        analysis = debugger._analyze_stack_trace(stack_trace)
        
        assert "call_stack" in analysis
        assert len(analysis["call_stack"]) == 2
        assert analysis["depth"] == 2


class TestErrorSeverity:
    """Test error severity calculation"""
    
    def test_critical_severity(self, debugger):
        """Test critical severity errors"""
        severity = debugger._calculate_error_severity("memory_error", {})
        assert severity == "critical"
    
    def test_high_severity(self, debugger):
        """Test high severity errors"""
        severity = debugger._calculate_error_severity("zero_division", {})
        assert severity == "high"
    
    def test_medium_severity(self, debugger):
        """Test medium severity errors"""
        severity = debugger._calculate_error_severity("type_error", {})
        assert severity == "medium"
    
    def test_low_severity(self, debugger):
        """Test low severity errors"""
        severity = debugger._calculate_error_severity("unknown_error", {})
        assert severity == "low"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])