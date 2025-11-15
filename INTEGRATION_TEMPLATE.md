# Integration Template for All Products

This template should be added to each product's README after the Performance/Deployment section and before Contributing.

---

## 🔗 Integration Points

### Enterprise Hub Integration

This product integrates with iTechSmart Enterprise Hub for:

- **Centralized Management**: Register and manage from Hub dashboard
- **Health Monitoring**: Real-time health checks every 30 seconds
- **Metrics Reporting**: Send performance metrics to Hub
- **Configuration Updates**: Receive configuration from Hub
- **Cross-Product Workflows**: Participate in multi-product workflows
- **Unified Authentication**: Use PassPort for authentication via Hub

#### Hub Registration

On startup, this product automatically registers with Enterprise Hub:

```python
# Automatic registration on startup
{
  "product_id": "PRODUCT_ID",
  "product_name": "PRODUCT_NAME",
  "version": "1.0.0",
  "api_endpoint": "http://PRODUCT:8080",
  "health_endpoint": "http://PRODUCT:8080/health",
  "capabilities": ["CAPABILITY_1", "CAPABILITY_2"],
  "status": "healthy"
}
```

#### Health Reporting

```python
# Health updates sent every 30 seconds
POST /api/v1/hub/products/{product_id}/health
{
  "status": "healthy",
  "metrics": {
    "cpu_usage": 45.2,
    "memory_usage": 62.8,
    "active_connections": 150,
    "requests_per_minute": 1200
  }
}
```

### Ninja Integration

This product is monitored and managed by iTechSmart Ninja for:

- **Self-Healing**: Automatic detection and recovery from errors
- **Performance Optimization**: Continuous performance monitoring and optimization
- **Auto-Scaling**: Automatic scaling based on load
- **Error Detection**: Real-time error detection and alerting
- **Dependency Management**: Automatic dependency updates and patches
- **Resource Optimization**: Memory and CPU optimization

#### Ninja Monitoring

```python
# Ninja monitors these metrics
{
  "error_rate": 0.01,
  "response_time_p95": 120,
  "memory_usage": 62.8,
  "cpu_usage": 45.2,
  "active_connections": 150,
  "queue_size": 50
}
```

#### Auto-Healing Actions

Ninja can automatically:
- Restart service on critical errors
- Clear caches on memory issues
- Scale resources on high load
- Rollback on deployment failures
- Fix configuration issues
- Update dependencies

### Standalone Mode

This product can operate independently without Hub connection:

**Standalone Features:**
- ✅ Core functionality available
- ✅ Local configuration management
- ✅ File-based settings
- ✅ Offline operation
- ❌ No cross-product workflows
- ❌ No centralized monitoring
- ❌ Manual configuration updates

**Enable Standalone Mode:**
```bash
export PRODUCT_HUB_ENABLED=false
export PRODUCT_STANDALONE_MODE=true
export PRODUCT_CONFIG_FILE=/config/local.yaml
```

**Standalone Configuration:**
```yaml
# config/local.yaml
standalone:
  enabled: true
  hub_integration: false
  local_auth: true
  config_source: file
```

---

## 🔧 Integration Configuration

### Environment Variables

```bash
# Hub Integration
PRODUCT_HUB_URL=http://enterprise-hub:8000
PRODUCT_HUB_API_KEY=hub_api_key
PRODUCT_HUB_ENABLED=true
PRODUCT_HUB_HEALTH_INTERVAL=30
PRODUCT_HUB_METRICS_INTERVAL=60

# Ninja Integration
PRODUCT_NINJA_URL=http://ninja:8000
PRODUCT_NINJA_API_KEY=ninja_api_key
PRODUCT_NINJA_ENABLED=true
PRODUCT_NINJA_ERROR_THRESHOLD=5
PRODUCT_NINJA_PERFORMANCE_THRESHOLD=0.8

# Standalone Mode
PRODUCT_STANDALONE_MODE=false
PRODUCT_LOCAL_CONFIG=/config/local.yaml
```

### Integration Health Check

```bash
# Check Hub connection
curl http://localhost:8080/integration/hub/status

# Check Ninja connection
curl http://localhost:8080/integration/ninja/status

# Check all integrations
curl http://localhost:8080/integration/status
```

---

## 🌐 Cross-Product Integration

### Integrated With

This product integrates with the following iTechSmart products:

**Core Integrations:**
- **Enterprise Hub**: Central management and monitoring
- **Ninja**: Self-healing and optimization
- **PassPort**: Authentication and authorization
- **Vault**: Secrets management
- **Connect**: API gateway
- **Notify**: Notifications

**Product-Specific Integrations:**
[Add product-specific integrations here]

### Integration Examples

#### Example 1: Cross-Product Workflow
```python
# Trigger workflow across products
POST /api/v1/workflows/execute
{
  "workflow_id": "example_workflow",
  "steps": [
    {"product": "THIS_PRODUCT", "action": "action_1"},
    {"product": "OTHER_PRODUCT", "action": "action_2"}
  ]
}
```

#### Example 2: Shared Data Access
```python
# Access data from other products via Hub
GET /api/v1/hub/data/{product_id}/{resource}
```

---