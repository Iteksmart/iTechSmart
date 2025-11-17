"""
Tests for Sandbox Environment Manager
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from app.core.sandbox import (
    SandboxManager,
    SandboxConfig,
    SandboxStatus,
    SandboxLanguage,
    get_sandbox_manager,
)


@pytest.fixture
def sandbox_manager():
    """Create a sandbox manager for testing"""
    return SandboxManager()


@pytest.mark.asyncio
async def test_create_python_sandbox(sandbox_manager):
    """Test creating a Python sandbox"""
    sandbox_info = await sandbox_manager.create_sandbox(language=SandboxLanguage.PYTHON)

    assert sandbox_info.sandbox_id is not None
    assert sandbox_info.language == SandboxLanguage.PYTHON
    assert sandbox_info.status == SandboxStatus.READY
    assert sandbox_info.container_id is not None

    # Cleanup
    await sandbox_manager.terminate_sandbox(sandbox_info.sandbox_id)


@pytest.mark.asyncio
async def test_execute_python_code(sandbox_manager):
    """Test executing Python code in sandbox"""
    # Create sandbox
    sandbox_info = await sandbox_manager.create_sandbox(language=SandboxLanguage.PYTHON)

    # Execute code
    code = """
print("Hello from sandbox!")
print(2 + 2)
"""

    result = await sandbox_manager.execute_code(
        sandbox_id=sandbox_info.sandbox_id, code=code
    )

    assert result.success is True
    assert "Hello from sandbox!" in result.output
    assert "4" in result.output
    assert result.exit_code == 0
    assert result.execution_time > 0

    # Cleanup
    await sandbox_manager.terminate_sandbox(sandbox_info.sandbox_id)


@pytest.mark.asyncio
async def test_execute_javascript_code(sandbox_manager):
    """Test executing JavaScript code in sandbox"""
    # Create sandbox
    sandbox_info = await sandbox_manager.create_sandbox(
        language=SandboxLanguage.JAVASCRIPT
    )

    # Execute code
    code = """
console.log("Hello from Node.js!");
console.log(2 + 2);
"""

    result = await sandbox_manager.execute_code(
        sandbox_id=sandbox_info.sandbox_id, code=code
    )

    assert result.success is True
    assert "Hello from Node.js!" in result.output
    assert "4" in result.output

    # Cleanup
    await sandbox_manager.terminate_sandbox(sandbox_info.sandbox_id)


@pytest.mark.asyncio
async def test_execute_code_with_error(sandbox_manager):
    """Test executing code that produces an error"""
    # Create sandbox
    sandbox_info = await sandbox_manager.create_sandbox(language=SandboxLanguage.PYTHON)

    # Execute code with error
    code = """
print("Before error")
raise ValueError("Test error")
print("After error")
"""

    result = await sandbox_manager.execute_code(
        sandbox_id=sandbox_info.sandbox_id, code=code
    )

    assert result.success is False
    assert "Before error" in result.output
    assert "ValueError: Test error" in result.output
    assert result.exit_code != 0

    # Cleanup
    await sandbox_manager.terminate_sandbox(sandbox_info.sandbox_id)


@pytest.mark.asyncio
async def test_sandbox_with_custom_config(sandbox_manager):
    """Test creating sandbox with custom configuration"""
    config = SandboxConfig(
        language=SandboxLanguage.PYTHON,
        memory_limit="256m",
        cpu_limit=0.5,
        timeout=60,
        network_enabled=False,
        environment_vars={"TEST_VAR": "test_value"},
    )

    sandbox_info = await sandbox_manager.create_sandbox(
        language=SandboxLanguage.PYTHON, config=config
    )

    assert sandbox_info.config.memory_limit == "256m"
    assert sandbox_info.config.cpu_limit == 0.5
    assert sandbox_info.config.timeout == 60
    assert sandbox_info.config.network_enabled is False
    assert sandbox_info.config.environment_vars["TEST_VAR"] == "test_value"

    # Test environment variable
    code = """
import os
print(os.environ.get('TEST_VAR', 'not found'))
"""

    result = await sandbox_manager.execute_code(
        sandbox_id=sandbox_info.sandbox_id, code=code
    )

    assert "test_value" in result.output

    # Cleanup
    await sandbox_manager.terminate_sandbox(sandbox_info.sandbox_id)


@pytest.mark.asyncio
async def test_stop_and_terminate_sandbox(sandbox_manager):
    """Test stopping and terminating a sandbox"""
    # Create sandbox
    sandbox_info = await sandbox_manager.create_sandbox(language=SandboxLanguage.PYTHON)
    sandbox_id = sandbox_info.sandbox_id

    # Stop sandbox
    await sandbox_manager.stop_sandbox(sandbox_id)
    sandbox_info = await sandbox_manager.get_sandbox_info(sandbox_id)
    assert sandbox_info.status == SandboxStatus.STOPPED

    # Terminate sandbox
    await sandbox_manager.terminate_sandbox(sandbox_id)
    sandbox_info = await sandbox_manager.get_sandbox_info(sandbox_id)
    assert sandbox_info.status == SandboxStatus.TERMINATED


@pytest.mark.asyncio
async def test_list_sandboxes(sandbox_manager):
    """Test listing sandboxes with filters"""
    # Create multiple sandboxes
    python_sandbox = await sandbox_manager.create_sandbox(
        language=SandboxLanguage.PYTHON
    )
    js_sandbox = await sandbox_manager.create_sandbox(
        language=SandboxLanguage.JAVASCRIPT
    )

    # List all sandboxes
    all_sandboxes = await sandbox_manager.list_sandboxes()
    assert len(all_sandboxes) >= 2

    # List Python sandboxes
    python_sandboxes = await sandbox_manager.list_sandboxes(
        language=SandboxLanguage.PYTHON
    )
    assert len(python_sandboxes) >= 1
    assert all(s.language == SandboxLanguage.PYTHON for s in python_sandboxes)

    # List ready sandboxes
    ready_sandboxes = await sandbox_manager.list_sandboxes(status=SandboxStatus.READY)
    assert len(ready_sandboxes) >= 2
    assert all(s.status == SandboxStatus.READY for s in ready_sandboxes)

    # Cleanup
    await sandbox_manager.terminate_sandbox(python_sandbox.sandbox_id)
    await sandbox_manager.terminate_sandbox(js_sandbox.sandbox_id)


@pytest.mark.asyncio
async def test_cleanup_old_sandboxes(sandbox_manager):
    """Test cleaning up old sandboxes"""
    # Create a sandbox
    sandbox_info = await sandbox_manager.create_sandbox(language=SandboxLanguage.PYTHON)

    # Manually set old creation time
    sandbox_info.created_at = datetime.now() - timedelta(hours=25)

    # Cleanup old sandboxes
    cleaned = await sandbox_manager.cleanup_old_sandboxes(max_age_hours=24)

    assert cleaned >= 1


@pytest.mark.asyncio
async def test_resource_usage_tracking(sandbox_manager):
    """Test tracking resource usage during execution"""
    # Create sandbox
    sandbox_info = await sandbox_manager.create_sandbox(language=SandboxLanguage.PYTHON)

    # Execute code that uses resources
    code = """
import time
data = [i for i in range(1000000)]
time.sleep(0.1)
print(f"Processed {len(data)} items")
"""

    result = await sandbox_manager.execute_code(
        sandbox_id=sandbox_info.sandbox_id, code=code
    )

    assert result.success is True
    assert result.memory_used is not None
    assert result.memory_used > 0
    assert result.execution_time > 0.1

    # Cleanup
    await sandbox_manager.terminate_sandbox(sandbox_info.sandbox_id)


@pytest.mark.asyncio
async def test_multiple_executions_same_sandbox(sandbox_manager):
    """Test multiple code executions in the same sandbox"""
    # Create sandbox
    sandbox_info = await sandbox_manager.create_sandbox(language=SandboxLanguage.PYTHON)

    # First execution
    result1 = await sandbox_manager.execute_code(
        sandbox_id=sandbox_info.sandbox_id, code="print('First execution')"
    )
    assert result1.success is True
    assert "First execution" in result1.output

    # Second execution
    result2 = await sandbox_manager.execute_code(
        sandbox_id=sandbox_info.sandbox_id, code="print('Second execution')"
    )
    assert result2.success is True
    assert "Second execution" in result2.output

    # Third execution
    result3 = await sandbox_manager.execute_code(
        sandbox_id=sandbox_info.sandbox_id, code="print('Third execution')"
    )
    assert result3.success is True
    assert "Third execution" in result3.output

    # Cleanup
    await sandbox_manager.terminate_sandbox(sandbox_info.sandbox_id)


@pytest.mark.asyncio
async def test_sandbox_isolation(sandbox_manager):
    """Test that sandboxes are isolated from each other"""
    # Create two sandboxes
    sandbox1 = await sandbox_manager.create_sandbox(language=SandboxLanguage.PYTHON)
    sandbox2 = await sandbox_manager.create_sandbox(language=SandboxLanguage.PYTHON)

    # Write file in sandbox1
    code1 = """
with open('/tmp/test.txt', 'w') as f:
    f.write('Sandbox 1 data')
print('File written in sandbox 1')
"""
    result1 = await sandbox_manager.execute_code(
        sandbox_id=sandbox1.sandbox_id, code=code1
    )
    assert result1.success is True

    # Try to read file in sandbox2 (should not exist)
    code2 = """
import os
if os.path.exists('/tmp/test.txt'):
    print('File exists in sandbox 2')
else:
    print('File does not exist in sandbox 2')
"""
    result2 = await sandbox_manager.execute_code(
        sandbox_id=sandbox2.sandbox_id, code=code2
    )
    assert result2.success is True
    assert "File does not exist in sandbox 2" in result2.output

    # Cleanup
    await sandbox_manager.terminate_sandbox(sandbox1.sandbox_id)
    await sandbox_manager.terminate_sandbox(sandbox2.sandbox_id)


@pytest.mark.asyncio
async def test_get_sandbox_manager_singleton():
    """Test that get_sandbox_manager returns singleton"""
    manager1 = get_sandbox_manager()
    manager2 = get_sandbox_manager()

    assert manager1 is manager2
