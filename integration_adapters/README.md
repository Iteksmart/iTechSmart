# 🔌 iTechSmart Integration Adapters

## Overview

Integration adapters enable each iTechSmart service to seamlessly integrate with the suite while maintaining standalone functionality.

---

## 📦 Available Adapters

### 1. **Base Adapter** (`base_adapter.py`)
The foundation for all service adapters.

**Features:**
- ✅ Hub registration/unregistration
- ✅ Service discovery
- ✅ Cross-service communication
- ✅ Event publishing/subscribing
- ✅ Ninja command handling
- ✅ Health monitoring
- ✅ Standalone mode support

### 2. **HL7 Adapter** (`hl7_adapter.py`)
Integration adapter for iTechSmart HL7.

**Capabilities:**
- HL7 v2.x messaging
- FHIR R4 support
- EMR integration
- Message routing
- Auto-remediation

### 3. **Supreme Adapter** (To be created)
Integration adapter for iTechSmart Supreme.

**Capabilities:**
- Auto-remediation
- Network management
- VM provisioning
- Infrastructure monitoring

### 4. **ImpactOS Adapter** (To be created)
Integration adapter for iTechSmart ImpactOS.

**Capabilities:**
- Impact tracking
- SDG mapping
- ESG reporting
- Data aggregation

### 5. **Passport Adapter** (To be created)
Integration adapter for iTechSmart Passport.

**Capabilities:**
- Authentication
- Authorization
- Identity verification
- SSO

### 6. **ProofLink Adapter** (To be created)
Integration adapter for iTechSmart ProofLink.

**Capabilities:**
- Document verification
- Blockchain proofs
- Audit trails
- Tamper detection

---

## 🚀 Usage

### Implementing an Adapter

```python
from integration_adapters.base_adapter import BaseServiceAdapter, StandaloneMode

class MyServiceAdapter(BaseServiceAdapter, StandaloneMode):
    def __init__(self):
        BaseServiceAdapter.__init__(
            self,
            service_type="itechsmart-myservice",
            service_name="myservice-main",
            base_url="http://localhost:8007",
            api_key="myservice-key"
        )
        StandaloneMode.__init__(self)
    
    async def get_capabilities(self) -> List[str]:
        return ["capability1", "capability2"]
    
    async def get_metadata(self) -> Dict[str, Any]:
        return {"version": "1.0.0"}
    
    async def get_event_subscriptions(self) -> List[str]:
        return ["event.type1", "event.type2"]
    
    async def handle_fix_command(self, parameters):
        # Implement fix logic
        return {"success": True}
    
    # ... implement other abstract methods
```

### Using the Adapter

```python
# Initialize adapter
adapter = MyServiceAdapter()

# Integrated mode
await adapter.initialize()

# OR Standalone mode
adapter.enable_standalone_mode()
await adapter.initialize_standalone()

# Call another service
result = await adapter.call_service(
    target_service="itechsmart-passport:main",
    endpoint="/api/auth/verify",
    method="POST",
    data={"token": "user-token"}
)

# Publish event
await adapter.publish_event(
    event_type="myservice.event",
    event_data={"key": "value"}
)

# Handle event
adapter.register_event_handler(
    event_type="user.verified",
    handler=my_event_handler
)
```

---

## 🔄 Integration Patterns

### Pattern 1: Service Registration

```python
# Automatic on initialization
await adapter.initialize()

# Service is now registered with Enterprise hub
```

### Pattern 2: Cross-Service Call

```python
# Call another service through hub
result = await adapter.call_service(
    target_service="itechsmart-hl7:main",
    endpoint="/api/messages/send",
    method="POST",
    data={"message_type": "ADT^A01"}
)
```

### Pattern 3: Event Publishing

```python
# Publish event to all subscribers
await adapter.publish_event(
    event_type="document.verified",
    event_data={
        "document_id": "DOC123",
        "verification_level": "high"
    }
)
```

### Pattern 4: Event Handling

```python
# Register handler
async def handle_user_verified(event_data, source_service):
    user_id = event_data["user_id"]
    # Process event
    print(f"User {user_id} verified by {source_service}")

adapter.register_event_handler(
    event_type="user.verified",
    handler=handle_user_verified
)
```

### Pattern 5: Ninja Commands

```python
# Ninja sends command
result = await adapter.handle_ninja_command(
    command="fix",
    parameters={"issue_type": "performance"}
)

# Adapter executes fix and returns result
```

---

## 🔒 Standalone Mode

Each adapter supports standalone mode for independent operation:

```python
# Enable standalone mode
adapter.enable_standalone_mode()
await adapter.initialize_standalone()

# Service runs independently without hub
# No registration, no events, no cross-service calls

# Check mode
if adapter.is_standalone():
    print("Running in standalone mode")
```

---

## 🎯 Required Methods

All adapters must implement these abstract methods:

### 1. **get_capabilities()**
Return list of service capabilities.

```python
async def get_capabilities(self) -> List[str]:
    return ["capability1", "capability2", "capability3"]
```

### 2. **get_metadata()**
Return service metadata.

```python
async def get_metadata(self) -> Dict[str, Any]:
    return {
        "version": "1.0.0",
        "region": "us-east-1",
        "custom_field": "value"
    }
```

### 3. **get_event_subscriptions()**
Return events to subscribe to.

```python
async def get_event_subscriptions(self) -> List[str]:
    return ["event.type1", "event.type2"]
```

### 4. **handle_fix_command()**
Handle fix command from Ninja.

```python
async def handle_fix_command(self, parameters: Dict) -> Dict:
    issue_type = parameters.get("issue_type")
    # Fix the issue
    return {"success": True, "action": "fixed"}
```

### 5. **handle_update_command()**
Handle update command from Ninja.

```python
async def handle_update_command(self, parameters: Dict) -> Dict:
    update_type = parameters.get("update_type")
    # Apply update
    return {"success": True, "version": "1.0.1"}
```

### 6. **handle_optimize_command()**
Handle optimize command from Ninja.

```python
async def handle_optimize_command(self, parameters: Dict) -> Dict:
    # Apply optimizations
    return {"success": True, "optimizations": ["opt1", "opt2"]}
```

### 7. **handle_restart_command()**
Handle restart command from Ninja.

```python
async def handle_restart_command(self, parameters: Dict) -> Dict:
    # Restart service
    return {"success": True, "downtime_seconds": 5}
```

### 8. **handle_diagnose_command()**
Handle diagnose command from Ninja.

```python
async def handle_diagnose_command(self, parameters: Dict) -> Dict:
    return {
        "success": True,
        "diagnostics": {
            "cpu_usage": "45%",
            "memory_usage": "60%"
        }
    }
```

### 9. **get_health_status()**
Return current health status.

```python
async def get_health_status(self) -> Dict:
    return {
        "status": "healthy",
        "response_time_ms": 45,
        "metrics": {}
    }
```

### 10. **get_service_info()**
Return service information.

```python
async def get_service_info(self) -> Dict:
    return {
        "name": "My Service",
        "version": "1.0.0",
        "type": "service-type"
    }
```

---

## 📊 Health Monitoring

Adapters automatically send heartbeats to the hub:

```python
# Automatic heartbeat every 30 seconds
# No manual intervention needed

# Hub tracks:
# - Last heartbeat timestamp
# - Service status
# - Response times
```

---

## 🎮 Example: Complete Integration

```python
from integration_adapters.hl7_adapter import HL7ServiceAdapter

# Initialize
adapter = HL7ServiceAdapter()
await adapter.initialize()

# Register event handler
async def handle_patient_admitted(event_data, source):
    patient_id = event_data["patient_id"]
    
    # Verify identity
    identity = await adapter.call_service(
        target_service="itechsmart-passport:main",
        endpoint="/api/identity/verify",
        method="POST",
        data={"patient_id": patient_id}
    )
    
    # Verify documents
    docs = await adapter.call_service(
        target_service="itechsmart-prooflink:main",
        endpoint="/api/documents/verify",
        method="POST",
        data={"patient_id": patient_id}
    )
    
    # Send HL7 admission message
    # ... HL7 logic ...
    
    # Track impact
    await adapter.call_service(
        target_service="itechsmart-impactos:main",
        endpoint="/api/impact/track",
        method="POST",
        data={"event": "patient_admitted"}
    )

adapter.register_event_handler(
    event_type="patient.admitted",
    handler=handle_patient_admitted
)

# Service is now fully integrated!
```

---

## 🚀 Deployment

### Integrated Mode

```yaml
# docker-compose.yml
services:
  myservice:
    image: itechsmart/myservice:latest
    environment:
      - HUB_URL=http://enterprise-hub:8000
      - STANDALONE_MODE=false
```

### Standalone Mode

```yaml
# docker-compose.yml
services:
  myservice:
    image: itechsmart/myservice:latest
    environment:
      - STANDALONE_MODE=true
```

---

## 🎯 Best Practices

1. **Always implement all abstract methods**
2. **Use meaningful capability names**
3. **Subscribe only to relevant events**
4. **Handle Ninja commands gracefully**
5. **Provide detailed health status**
6. **Support both integrated and standalone modes**
7. **Log all integration activities**
8. **Handle errors gracefully**
9. **Use async/await properly**
10. **Test both modes thoroughly**

---

## 📚 Additional Resources

- **Integration Architecture**: See `ITECHSMART_INTEGRATION_ARCHITECTURE.md`
- **Enterprise Hub**: See `itechsmart-enterprise/backend/app/core/integration_hub.py`
- **Ninja Controller**: See `itechsmart-ninja/backend/app/core/suite_controller.py`

---

## 🎉 Conclusion

Integration adapters make it easy to:
- ✅ Connect services to the suite
- ✅ Enable cross-service communication
- ✅ Support Ninja control
- ✅ Maintain standalone functionality
- ✅ Standardize integration patterns

**Every iTechSmart service should implement an adapter for seamless integration!** 🚀