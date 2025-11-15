# iTechSmart Port Manager - Integration Guide

## Overview

This guide explains how to integrate iTechSmart Port Manager with all products in the iTechSmart Suite.

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  iTechSmart Port Manager                     │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Port Manager Core                        │  │
│  │  • Port allocation                                    │  │
│  │  • Conflict detection                                 │  │
│  │  • Configuration management                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ▲                                 │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Suite Communicator                          │  │
│  │  • Service discovery                                  │  │
│  │  • Port update requests                               │  │
│  │  • Health monitoring                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ▲                                 │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Hub/Ninja Integration                         │  │
│  │  • Service registration                               │  │
│  │  • Health/metrics reporting                           │  │
│  │  • Event broadcasting                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────▼──────┐                       ┌───────▼──────┐
│ Enterprise   │                       │    Ninja     │
│     Hub      │                       │  Monitoring  │
└──────────────┘                       └──────────────┘
        │                                       │
        └───────────────────┬───────────────────┘
                            │
                ┌───────────▼───────────┐
                │   All 27 Products     │
                │   in Suite            │
                └───────────────────────┘
```

---

## How It Works

### 1. Service Registration

When Port Manager starts:
1. Loads port configuration from `port_config.json`
2. Registers with Enterprise Hub
3. Registers with Ninja for monitoring
4. Starts health and metrics reporting

### 2. Port Assignment

When assigning a port:
1. Port Manager checks if port is available
2. Validates no conflicts exist
3. Updates internal configuration
4. Saves to disk
5. Returns success/failure

### 3. Port Reassignment

When reassigning a port:
1. Validates new port is available
2. Calls service's `/api/config/update-port` endpoint
3. Service updates its configuration
4. Service restarts on new port
5. Port Manager broadcasts change to Hub and Ninja
6. All services notified of the change

### 4. Conflict Detection

Port Manager continuously:
1. Checks for duplicate port assignments
2. Verifies ports are available at system level
3. Reports conflicts via API
4. Can auto-resolve conflicts

### 5. Auto-Resolution

When conflicts are detected:
1. Port Manager identifies conflicting services
2. Finds available ports for reassignment
3. Updates services one by one
4. Verifies each update succeeded
5. Broadcasts all changes

---

## Adding Port Manager Support to Your Service

To make your service compatible with Port Manager, add this endpoint:

### Required Endpoint

```python
@app.post("/api/config/update-port")
async def update_port(request: PortUpdateRequest):
    """
    Handle port update request from Port Manager
    """
    new_port = request.new_port
    old_port = request.old_port
    
    # 1. Validate new port
    if new_port < 1024 or new_port > 65535:
        raise HTTPException(400, "Invalid port")
    
    # 2. Update configuration
    config['port'] = new_port
    save_config(config)
    
    # 3. Schedule restart (optional)
    asyncio.create_task(restart_service(new_port))
    
    return {
        "success": True,
        "message": f"Port updated from {old_port} to {new_port}",
        "restart_required": True
    }
```

### Request Format

```json
{
  "new_port": 8050,
  "old_port": 8000,
  "timestamp": "2024-12-12T14:30:22Z",
  "source": "port-manager"
}
```

### Response Format

```json
{
  "success": true,
  "message": "Port updated successfully",
  "restart_required": true
}
```

---

## Integration with Enterprise Hub

### Service Registration

Port Manager registers with Hub on startup:

```python
registration = {
    "service_id": "itechsmart-port-manager",
    "service_name": "iTechSmart Port Manager",
    "service_type": "infrastructure",
    "version": "1.0.0",
    "host": "itechsmart-port-manager",
    "port": 8100,
    "health_endpoint": "/health",
    "capabilities": [
        "port_management",
        "conflict_detection",
        "automatic_reassignment",
        "real_time_monitoring"
    ]
}
```

### Health Reporting

Every 30 seconds:

```python
health = {
    "service_id": "itechsmart-port-manager",
    "status": "healthy",
    "timestamp": "2024-12-12T14:30:22Z",
    "metrics": {
        "uptime": 3600,
        "port_manager_active": True,
        "suite_communicator_active": True
    }
}
```

### Metrics Reporting

Every 60 seconds:

```python
metrics = {
    "service_id": "itechsmart-port-manager",
    "timestamp": "2024-12-12T14:30:22Z",
    "cpu_usage": 15.5,
    "memory_usage": 45.2,
    "custom_metrics": {
        "managed_services": 27,
        "port_assignments": 27,
        "conflicts_detected": 0,
        "ports_reassigned": 0
    }
}
```

### Port Change Events

When a port changes:

```python
event = {
    "event": "port_changed",
    "service_id": "legalai-pro",
    "old_port": 8000,
    "new_port": 8050,
    "timestamp": "2024-12-12T14:30:22Z"
}

# Broadcast to Hub
POST /api/v1/events/port-change

# Broadcast to Ninja
POST /api/v1/events/port-change
```

---

## Integration with Ninja

### Error Reporting

When errors occur:

```python
error_report = {
    "service_id": "itechsmart-port-manager",
    "error_type": "PortConflictError",
    "error_message": "Port 8000 assigned to multiple services",
    "stack_trace": "...",
    "timestamp": "2024-12-12T14:30:22Z",
    "severity": "high",
    "context": {
        "port": 8000,
        "services": ["service1", "service2"]
    }
}
```

### Performance Monitoring

Every 60 seconds:

```python
performance = {
    "service_id": "itechsmart-port-manager",
    "timestamp": "2024-12-12T14:30:22Z",
    "endpoint": "/api/ports/assignments",
    "response_time": 85.3,
    "status_code": 200,
    "error": None
}
```

---

## WebSocket Integration

### Connecting to WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8100/ws/updates');

ws.onopen = () => {
    console.log('Connected to Port Manager');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'connected':
            console.log('Connection established');
            break;
        
        case 'port_change':
            console.log(`Port changed: ${data.service_id}`);
            console.log(`Old: ${data.old_port}, New: ${data.new_port}`);
            break;
        
        case 'conflicts_detected':
            console.log(`${data.count} conflicts detected`);
            break;
        
        case 'service_status':
            console.log(`${data.service_id}: ${data.status}`);
            break;
    }
};
```

### Message Types

**Connected**
```json
{
  "type": "connected",
  "message": "Connected to Port Manager updates"
}
```

**Port Change**
```json
{
  "type": "port_change",
  "service_id": "legalai-pro",
  "old_port": 8000,
  "new_port": 8050,
  "timestamp": 1702389022.123
}
```

**Conflicts Detected**
```json
{
  "type": "conflicts_detected",
  "conflicts": [...],
  "count": 2,
  "timestamp": 1702389022.123
}
```

**Service Status**
```json
{
  "type": "service_status",
  "service_id": "legalai-pro",
  "status": "healthy",
  "timestamp": 1702389022.123
}
```

---

## Configuration Files

### port_config.json

```json
{
  "port_assignments": {
    "itechsmart-enterprise": 8001,
    "itechsmart-ninja": 8002,
    "legalai-pro": 8000,
    ...
  },
  "port_history": {
    "legalai-pro": [8000, 8050, 8075]
  },
  "reserved_ports": [8888, 9999],
  "last_updated": "2024-12-12T14:30:22Z"
}
```

### Backup Files

Backup files are automatically named with timestamp:
```
port_config_backup_20241212_143022.json
```

---

## API Integration Examples

### Python Example

```python
import requests

API_URL = "http://localhost:8100/api"

# Get all port assignments
response = requests.get(f"{API_URL}/ports/assignments")
assignments = response.json()['assignments']

# Reassign a port
response = requests.post(f"{API_URL}/ports/reassign", json={
    "service_id": "legalai-pro",
    "new_port": 8050
})

# Detect conflicts
response = requests.get(f"{API_URL}/ports/conflicts")
conflicts = response.json()['conflicts']

# Auto-resolve conflicts
response = requests.post(f"{API_URL}/ports/resolve-conflicts")
resolutions = response.json()['resolutions']
```

### JavaScript Example

```javascript
const API_URL = 'http://localhost:8100/api';

// Get all port assignments
const assignments = await fetch(`${API_URL}/ports/assignments`)
    .then(r => r.json());

// Reassign a port
const result = await fetch(`${API_URL}/ports/reassign`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        service_id: 'legalai-pro',
        new_port: 8050
    })
}).then(r => r.json());

// Get service status
const status = await fetch(`${API_URL}/services/status`)
    .then(r => r.json());
```

### cURL Examples

```bash
# Get all assignments
curl http://localhost:8100/api/ports/assignments

# Reassign port
curl -X POST http://localhost:8100/api/ports/reassign \
  -H "Content-Type: application/json" \
  -d '{"service_id":"legalai-pro","new_port":8050}'

# Detect conflicts
curl http://localhost:8100/api/ports/conflicts

# Resolve conflicts
curl -X POST http://localhost:8100/api/ports/resolve-conflicts

# Get statistics
curl http://localhost:8100/api/ports/statistics

# Backup configuration
curl -X POST http://localhost:8100/api/ports/backup
```

---

## Troubleshooting

### Port Manager Not Starting

**Issue:** Port Manager fails to start

**Solutions:**
1. Check if port 8100 is available
2. Verify Python dependencies installed
3. Check logs for errors
4. Ensure configuration file is valid JSON

### Service Not Updating

**Issue:** Service doesn't update to new port

**Solutions:**
1. Verify service has `/api/config/update-port` endpoint
2. Check service is reachable at current port
3. Review service logs for errors
4. Try manual restart of service

### Conflicts Not Resolving

**Issue:** Auto-resolve doesn't fix conflicts

**Solutions:**
1. Check if ports are available at system level
2. Verify services are responding
3. Try manual reassignment
4. Check for reserved ports blocking assignment

### WebSocket Not Connecting

**Issue:** Frontend can't connect to WebSocket

**Solutions:**
1. Verify backend is running
2. Check WebSocket URL is correct
3. Ensure no firewall blocking
4. Check browser console for errors

---

## Best Practices

### 1. Regular Backups

```bash
# Create daily backups
curl -X POST http://localhost:8100/api/ports/backup
```

### 2. Monitor Conflicts

```bash
# Check for conflicts regularly
curl http://localhost:8100/api/ports/conflicts
```

### 3. Use Port Ranges

- Keep services in logical port ranges
- Foundation: 8000-8009
- Strategic: 8010-8019
- Business: 8020-8029

### 4. Reserve Critical Ports

```bash
# Reserve important ports
curl -X POST http://localhost:8100/api/ports/reserve \
  -H "Content-Type: application/json" \
  -d '{"port":8888}'
```

### 5. Test Before Production

- Test port changes in staging first
- Verify services restart correctly
- Check all integrations still work
- Monitor for 24 hours before production

---

## Summary

iTechSmart Port Manager provides:
- ✅ Centralized port management
- ✅ Automatic conflict detection
- ✅ Dynamic port reassignment
- ✅ Real-time monitoring
- ✅ Full suite integration
- ✅ WebSocket updates
- ✅ Backup/restore capabilities

**Status:** 🎉 **Production Ready** 🎉