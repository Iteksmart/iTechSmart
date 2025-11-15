# Sandbox Environment Documentation

## Overview

The Sandbox Environment feature provides secure, isolated Docker-based execution environments for running untrusted code. Each sandbox is a separate Docker container with configurable resource limits, network access, and execution timeouts.

## Features

### 🔒 Security
- **Isolated Execution**: Each sandbox runs in a separate Docker container
- **Resource Limits**: Configurable CPU and memory limits
- **Network Control**: Optional network access (disabled by default)
- **Timeout Protection**: Automatic termination of long-running processes
- **File System Isolation**: Sandboxes cannot access host file system

### 🚀 Performance
- **Fast Creation**: Sandboxes created in seconds
- **Reusable**: Execute multiple code snippets in the same sandbox
- **Resource Monitoring**: Track CPU and memory usage
- **Automatic Cleanup**: Remove old sandboxes automatically

### 🌐 Multi-Language Support
- Python 3.11
- JavaScript (Node.js 20)
- TypeScript
- Java 17
- Go 1.21
- Rust 1.75
- C++ (GCC 13)
- Ruby 3.2
- PHP 8.2

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Sandbox Manager                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Docker Client                            │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                  │
│         ┌─────────────────┼─────────────────┐               │
│         │                 │                 │               │
│    ┌────▼────┐      ┌────▼────┐      ┌────▼────┐          │
│    │Sandbox 1│      │Sandbox 2│      │Sandbox 3│          │
│    │ Python  │      │   Node  │      │  Java   │          │
│    └─────────┘      └─────────┘      └─────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### Creating a Sandbox

```python
from app.core.sandbox import SandboxManager, SandboxLanguage, SandboxConfig

manager = SandboxManager()

# Create a Python sandbox with default settings
sandbox_info = await manager.create_sandbox(
    language=SandboxLanguage.PYTHON
)

# Create a sandbox with custom configuration
config = SandboxConfig(
    language=SandboxLanguage.PYTHON,
    memory_limit="1g",
    cpu_limit=2.0,
    timeout=600,
    network_enabled=True,
    environment_vars={"API_KEY": "secret"}
)

sandbox_info = await manager.create_sandbox(
    language=SandboxLanguage.PYTHON,
    config=config
)
```

### Executing Code

```python
# Execute Python code
code = """
print("Hello from sandbox!")
result = 2 + 2
print(f"Result: {result}")
"""

result = await manager.execute_code(
    sandbox_id=sandbox_info.sandbox_id,
    code=code
)

print(f"Success: {result.success}")
print(f"Output: {result.output}")
print(f"Execution time: {result.execution_time}s")
print(f"Memory used: {result.memory_used} bytes")
```

### Managing Sandboxes

```python
# Get sandbox information
sandbox_info = await manager.get_sandbox_info(sandbox_id)

# List all sandboxes
all_sandboxes = await manager.list_sandboxes()

# List sandboxes by status
ready_sandboxes = await manager.list_sandboxes(
    status=SandboxStatus.READY
)

# List sandboxes by language
python_sandboxes = await manager.list_sandboxes(
    language=SandboxLanguage.PYTHON
)

# Stop a sandbox
await manager.stop_sandbox(sandbox_id)

# Terminate and remove a sandbox
await manager.terminate_sandbox(sandbox_id)

# Cleanup old sandboxes (older than 24 hours)
cleaned = await manager.cleanup_old_sandboxes(max_age_hours=24)
```

## API Endpoints

### POST /sandbox/create
Create a new sandbox environment.

**Request Body:**
```json
{
  "language": "python",
  "memory_limit": "512m",
  "cpu_limit": 1.0,
  "timeout": 300,
  "network_enabled": false,
  "environment_vars": {
    "API_KEY": "secret"
  }
}
```

**Response:**
```json
{
  "sandbox_id": "123e4567-e89b-12d3-a456-426614174000",
  "language": "python",
  "status": "ready",
  "container_id": "abc123...",
  "created_at": "2024-01-15T10:30:00Z",
  "started_at": "2024-01-15T10:30:05Z",
  "config": {
    "language": "python",
    "memory_limit": "512m",
    "cpu_limit": 1.0,
    "timeout": 300,
    "network_enabled": false
  }
}
```

### POST /sandbox/{sandbox_id}/execute
Execute code in a sandbox.

**Request Body:**
```json
{
  "code": "print('Hello, World!')",
  "filename": "main.py"
}
```

**Response:**
```json
{
  "sandbox_id": "123e4567-e89b-12d3-a456-426614174000",
  "success": true,
  "output": "Hello, World!\n",
  "error": null,
  "exit_code": 0,
  "execution_time": 0.123,
  "memory_used": 12345678,
  "cpu_used": 5.2
}
```

### GET /sandbox/{sandbox_id}
Get information about a sandbox.

**Response:**
```json
{
  "sandbox_id": "123e4567-e89b-12d3-a456-426614174000",
  "language": "python",
  "status": "ready",
  "container_id": "abc123...",
  "created_at": "2024-01-15T10:30:00Z",
  "started_at": "2024-01-15T10:30:05Z",
  "config": {...}
}
```

### GET /sandbox/
List all sandboxes with optional filtering.

**Query Parameters:**
- `status`: Filter by status (creating, ready, running, stopped, error, terminated)
- `language`: Filter by language

**Response:**
```json
{
  "sandboxes": [...],
  "total": 5
}
```

### POST /sandbox/{sandbox_id}/stop
Stop a sandbox.

**Response:**
```json
{
  "message": "Sandbox 123e4567-e89b-12d3-a456-426614174000 stopped successfully"
}
```

### DELETE /sandbox/{sandbox_id}
Terminate and remove a sandbox.

**Response:**
```json
{
  "message": "Sandbox 123e4567-e89b-12d3-a456-426614174000 terminated successfully"
}
```

### POST /sandbox/cleanup
Clean up old sandboxes.

**Query Parameters:**
- `max_age_hours`: Maximum age in hours (default: 24)

**Response:**
```json
{
  "cleaned": 3,
  "message": "Cleaned up 3 sandboxes older than 24 hours"
}
```

### POST /sandbox/execute-quick
Quick code execution (creates temporary sandbox).

**Request Body:**
```json
{
  "language": "python",
  "code": "print('Hello, World!')",
  "filename": "main.py"
}
```

**Response:**
```json
{
  "sandbox_id": "temp-123...",
  "success": true,
  "output": "Hello, World!\n",
  "error": null,
  "exit_code": 0,
  "execution_time": 0.123,
  "memory_used": 12345678,
  "cpu_used": 5.2
}
```

### GET /sandbox/health
Check sandbox service health.

**Response:**
```json
{
  "status": "healthy",
  "total_sandboxes": 5,
  "status_breakdown": {
    "ready": 3,
    "running": 1,
    "stopped": 1
  },
  "supported_languages": [
    "python",
    "javascript",
    "typescript",
    "java",
    "go",
    "rust",
    "cpp",
    "ruby",
    "php"
  ]
}
```

## Configuration

### Resource Limits

```python
config = SandboxConfig(
    language=SandboxLanguage.PYTHON,
    memory_limit="512m",  # 512 MB
    cpu_limit=1.0,        # 1 CPU core
    timeout=300,          # 5 minutes
    network_enabled=False
)
```

### Environment Variables

```python
config = SandboxConfig(
    language=SandboxLanguage.PYTHON,
    environment_vars={
        "DATABASE_URL": "postgresql://...",
        "API_KEY": "secret",
        "DEBUG": "true"
    }
)
```

## Security Considerations

### 1. Network Isolation
By default, sandboxes have network access disabled. Enable only when necessary:

```python
config = SandboxConfig(
    language=SandboxLanguage.PYTHON,
    network_enabled=True  # Use with caution
)
```

### 2. Resource Limits
Always set appropriate resource limits to prevent resource exhaustion:

```python
config = SandboxConfig(
    language=SandboxLanguage.PYTHON,
    memory_limit="256m",  # Limit memory
    cpu_limit=0.5,        # Limit CPU
    timeout=60            # Limit execution time
)
```

### 3. File System Isolation
Sandboxes cannot access the host file system. All file operations are contained within the container.

### 4. Output Size Limits
Large outputs are automatically truncated to prevent memory issues:

```python
config = SandboxConfig(
    language=SandboxLanguage.PYTHON,
    max_output_size=1024 * 1024  # 1 MB
)
```

## Best Practices

### 1. Reuse Sandboxes
For multiple executions, reuse the same sandbox instead of creating new ones:

```python
# Create once
sandbox_info = await manager.create_sandbox(SandboxLanguage.PYTHON)

# Execute multiple times
for code_snippet in code_snippets:
    result = await manager.execute_code(sandbox_info.sandbox_id, code_snippet)
    
# Cleanup once
await manager.terminate_sandbox(sandbox_info.sandbox_id)
```

### 2. Cleanup Old Sandboxes
Regularly cleanup old sandboxes to free resources:

```python
# Run cleanup daily
await manager.cleanup_old_sandboxes(max_age_hours=24)
```

### 3. Monitor Resource Usage
Track resource usage to optimize performance:

```python
result = await manager.execute_code(sandbox_id, code)
print(f"Memory used: {result.memory_used / 1024 / 1024:.2f} MB")
print(f"CPU used: {result.cpu_used:.2f}%")
print(f"Execution time: {result.execution_time:.2f}s")
```

### 4. Handle Errors Gracefully
Always handle execution errors:

```python
result = await manager.execute_code(sandbox_id, code)
if not result.success:
    print(f"Execution failed: {result.error}")
    print(f"Exit code: {result.exit_code}")
```

### 5. Use Quick Execution for One-Off Tasks
For single executions, use the quick execution endpoint:

```python
# Automatically creates and cleans up sandbox
result = await execute_code_quick(
    language=SandboxLanguage.PYTHON,
    code="print('Hello!')"
)
```

## Troubleshooting

### Docker Connection Issues
```
Error: Failed to initialize Docker client
```

**Solution:** Ensure Docker is running and accessible:
```bash
docker ps
```

### Container Creation Failures
```
Error: Failed to create sandbox
```

**Solution:** Check Docker resources and image availability:
```bash
docker images
docker system df
```

### Execution Timeouts
```
Error: Execution timed out
```

**Solution:** Increase timeout or optimize code:
```python
config = SandboxConfig(
    language=SandboxLanguage.PYTHON,
    timeout=600  # Increase to 10 minutes
)
```

### Memory Limit Exceeded
```
Error: Container killed due to memory limit
```

**Solution:** Increase memory limit:
```python
config = SandboxConfig(
    language=SandboxLanguage.PYTHON,
    memory_limit="1g"  # Increase to 1 GB
)
```

## Performance Optimization

### 1. Pre-pull Images
Pre-pull Docker images to reduce creation time:

```bash
docker pull python:3.11-slim
docker pull node:20-slim
docker pull openjdk:17-slim
```

### 2. Use Smaller Images
Use slim/alpine images for faster startup:

```python
# Already using slim images by default
LANGUAGE_IMAGES = {
    SandboxLanguage.PYTHON: "python:3.11-slim",
    SandboxLanguage.JAVASCRIPT: "node:20-slim",
    ...
}
```

### 3. Limit Concurrent Sandboxes
Limit the number of concurrent sandboxes based on available resources:

```python
# Monitor active sandboxes
active_sandboxes = await manager.list_sandboxes(
    status=SandboxStatus.READY
)

if len(active_sandboxes) < MAX_CONCURRENT_SANDBOXES:
    sandbox_info = await manager.create_sandbox(language)
```

## Examples

### Example 1: Python Data Analysis
```python
code = """
import pandas as pd
import numpy as np

# Create sample data
data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'salary': [50000, 60000, 70000]
}

df = pd.DataFrame(data)
print(df.describe())
"""

result = await manager.execute_code(sandbox_id, code)
print(result.output)
```

### Example 2: JavaScript Web Scraping
```python
code = """
const axios = require('axios');

async function fetchData() {
    const response = await axios.get('https://api.example.com/data');
    console.log(response.data);
}

fetchData();
"""

config = SandboxConfig(
    language=SandboxLanguage.JAVASCRIPT,
    network_enabled=True  # Required for HTTP requests
)

sandbox_info = await manager.create_sandbox(
    language=SandboxLanguage.JAVASCRIPT,
    config=config
)

result = await manager.execute_code(sandbox_info.sandbox_id, code)
```

### Example 3: Multi-Language Testing
```python
languages = [
    (SandboxLanguage.PYTHON, 'print("Hello from Python")'),
    (SandboxLanguage.JAVASCRIPT, 'console.log("Hello from JavaScript")'),
    (SandboxLanguage.RUBY, 'puts "Hello from Ruby"')
]

for language, code in languages:
    sandbox_info = await manager.create_sandbox(language)
    result = await manager.execute_code(sandbox_info.sandbox_id, code)
    print(f"{language}: {result.output}")
    await manager.terminate_sandbox(sandbox_info.sandbox_id)
```

## Monitoring and Metrics

### Track Sandbox Usage
```python
# Get all sandboxes
sandboxes = await manager.list_sandboxes()

# Calculate metrics
total_sandboxes = len(sandboxes)
active_sandboxes = len([s for s in sandboxes if s.status == SandboxStatus.READY])
stopped_sandboxes = len([s for s in sandboxes if s.status == SandboxStatus.STOPPED])

print(f"Total: {total_sandboxes}")
print(f"Active: {active_sandboxes}")
print(f"Stopped: {stopped_sandboxes}")
```

### Monitor Resource Usage
```python
# Execute code and track resources
result = await manager.execute_code(sandbox_id, code)

metrics = {
    "execution_time": result.execution_time,
    "memory_used_mb": result.memory_used / 1024 / 1024,
    "cpu_percent": result.cpu_used,
    "success": result.success
}

# Log metrics for analysis
logger.info(f"Execution metrics: {metrics}")
```

## Future Enhancements

- [ ] GPU support for ML workloads
- [ ] Persistent storage volumes
- [ ] Custom Docker images
- [ ] Sandbox snapshots and restore
- [ ] Multi-container sandboxes
- [ ] Kubernetes integration
- [ ] Advanced networking (VPN, proxies)
- [ ] Sandbox templates
- [ ] Cost tracking and billing
- [ ] Sandbox sharing and collaboration

## Support

For issues or questions:
- GitHub Issues: https://github.com/itechsmart/ninja/issues
- Documentation: https://docs.itechsmart.dev/ninja/sandbox
- Email: support@itechsmart.dev