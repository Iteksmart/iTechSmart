# Feature 8: Concurrent VM Support - Complete Specification

## Overview
Support for running up to 10 concurrent virtual machines (sandboxes) for parallel code execution, testing, and experimentation. Each VM is isolated with resource limits.

---

## Capabilities

### VM Features
- Up to 10 concurrent VMs per user
- Isolated execution environments
- Resource limits (CPU, memory, disk)
- Multiple language support (Python, Node.js, Java, Go, Rust, etc.)
- Package installation per VM
- File system isolation
- Network isolation (optional)
- VM snapshots and restore
- VM templates for quick setup

### Use Cases
- Parallel test execution
- Multi-version testing
- Load testing
- Experimentation
- CI/CD pipelines
- Batch processing

---

## API Endpoints

### VM Pool Management
```
POST   /api/vms/create
GET    /api/vms
GET    /api/vms/{vm_id}
DELETE /api/vms/{vm_id}
POST   /api/vms/{vm_id}/start
POST   /api/vms/{vm_id}/stop
POST   /api/vms/{vm_id}/restart
POST   /api/vms/{vm_id}/execute
GET    /api/vms/{vm_id}/status
GET    /api/vms/{vm_id}/logs
POST   /api/vms/{vm_id}/snapshot
POST   /api/vms/{vm_id}/restore
POST   /api/vms/batch-execute
GET    /api/vms/pool-status
```

---

## Database Models

```python
class VirtualMachine(Base):
    __tablename__ = "virtual_machines"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    status = Column(String)  # running, stopped, error
    language = Column(String)  # python, nodejs, java, etc.
    container_id = Column(String)
    cpu_limit = Column(Float)  # CPU cores
    memory_limit = Column(Integer)  # MB
    disk_limit = Column(Integer)  # MB
    created_at = Column(DateTime)
    started_at = Column(DateTime)
    stopped_at = Column(DateTime)

class VMExecution(Base):
    __tablename__ = "vm_executions"
    
    id = Column(Integer, primary_key=True)
    vm_id = Column(Integer, ForeignKey("virtual_machines.id"))
    code = Column(Text)
    output = Column(Text)
    error = Column(Text)
    exit_code = Column(Integer)
    execution_time = Column(Float)  # seconds
    executed_at = Column(DateTime)
```

---

## VS Code Commands

1. `iTechSmart: Create VM` - Create new VM
2. `iTechSmart: List VMs` - List all VMs
3. `iTechSmart: Start VM` - Start VM
4. `iTechSmart: Stop VM` - Stop VM
5. `iTechSmart: Execute in VM` - Execute code in VM
6. `iTechSmart: VM Status` - Check VM status
7. `iTechSmart: Delete VM` - Delete VM
8. `iTechSmart: Batch Execute` - Execute in multiple VMs

---

## Terminal Commands

```bash
vm create <name> <language>  # Create VM
vm list                      # List VMs
vm start <id>               # Start VM
vm stop <id>                # Stop VM
vm execute <id> <code>      # Execute code
vm status <id>              # Check status
vm delete <id>              # Delete VM
vm batch <code>             # Execute in all VMs
```

---

## Implementation Steps

### Phase 1: Backend (8 hours)
1. Create `vm_pool_manager.py` integration (4 hours)
   - Docker container management
   - Resource allocation
   - VM lifecycle management
   - Concurrent execution handling
2. Create `vms.py` API routes (2 hours)
3. Add database models (1 hour)
4. Add monitoring and cleanup (1 hour)

### Phase 2: Frontend (1.5 hours)
1. Create `vmCommands.ts` (1 hour)
2. Add VM status panel (30 min)

### Phase 3: Testing & Documentation (1 hour)
1. Write unit tests (30 min)
2. Write integration tests (15 min)
3. Update documentation (15 min)

**Total Time**: 10-11 hours

---

## Testing Requirements

### Unit Tests
- VM creation and deletion
- Resource limit enforcement
- Concurrent execution
- Error handling
- Cleanup on failure

### Integration Tests
- Multiple VMs running simultaneously
- Batch execution
- Resource isolation
- Network isolation

### Load Tests
- 10 concurrent VMs
- High CPU/memory usage
- Long-running processes

---

## Dependencies

### Python Packages
```
docker>=6.1.0
asyncio>=3.4.3
psutil>=5.9.0
```

### System Dependencies
```
docker  # Docker engine
```

---

## Resource Limits

### Per VM Defaults
```python
DEFAULT_CPU_LIMIT = 1.0      # 1 CPU core
DEFAULT_MEMORY_LIMIT = 512   # 512 MB
DEFAULT_DISK_LIMIT = 1024    # 1 GB
DEFAULT_TIMEOUT = 300        # 5 minutes
```

### Pool Limits
```python
MAX_VMS_PER_USER = 10
MAX_TOTAL_VMS = 100
MAX_EXECUTION_TIME = 600  # 10 minutes
```

---

## Example Usage

### Create and Use VM
```python
# Create VM
vm = await create_vm(
    name="test-vm",
    language="python",
    cpu_limit=1.0,
    memory_limit=512
)

# Execute code
result = await execute_in_vm(
    vm_id=vm.id,
    code="print('Hello from VM!')"
)

print(result.output)  # "Hello from VM!"
```

### Batch Execution
```python
# Execute in all VMs
results = await batch_execute(
    code="import sys; print(sys.version)",
    vm_ids=[vm1.id, vm2.id, vm3.id]
)

for result in results:
    print(f"VM {result.vm_id}: {result.output}")
```

---

## Status

**Specification**: ✅ Complete
**Skeleton Code**: ✅ Provided
**Implementation**: ⏳ Pending
**Estimated Time**: 10-11 hours