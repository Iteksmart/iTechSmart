# iTechSmart Suite - API Migration Guide
## Version 1.0 → 2.0

**Document Version:** 1.0  
**Release Date:** August 8, 2025  
**Company:** iTechSmart Inc.

---

## Overview

This guide helps developers migrate from iTechSmart Suite v1.0 to v2.0. Version 2.0 introduces 150+ new API endpoints across 5 enhanced products.

### What's Changed

- **5 Products Enhanced** with new capabilities
- **150+ New Endpoints** added
- **New API Namespaces** for better organization
- **Authentication Updates** for improved security
- **Response Format Changes** for consistency

---

## General Changes

### API Versioning

All new endpoints use `/api/v1/` namespace:

```
Old: /api/compliance/...
New: /api/v1/compliance/...

Old: /api/service-catalog/...
New: /api/v1/service-catalog/...
```

### Authentication

**New Header Required:**
```http
Authorization: Bearer <jwt-token>
X-Tenant-ID: <tenant-id>
```

**Old Format:**
```http
Authorization: Bearer <jwt-token>
```

### Query Parameters

**tenant_id now required for all endpoints:**

```http
Old: GET /api/compliance/frameworks
New: GET /api/v1/compliance/frameworks?tenant_id=1
```

### Response Format

**Standardized response structure:**

```json
{
  "success": true,
  "data": {...},
  "meta": {
    "timestamp": "2025-08-08T12:00:00Z",
    "version": "2.0"
  }
}
```

**Error response:**

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": {...}
  }
}
```

---

## Compliance Center (Product #19)

### New Endpoints

#### Frameworks

```http
# List frameworks
GET /api/v1/compliance/frameworks?tenant_id=1

# Create framework
POST /api/v1/compliance/frameworks?tenant_id=1
{
  "name": "SOC2 Framework",
  "framework_type": "SOC2",
  "description": "SOC2 compliance framework"
}

# Get framework
GET /api/v1/compliance/frameworks/{id}?tenant_id=1

# Update framework
PUT /api/v1/compliance/frameworks/{id}?tenant_id=1

# Delete framework
DELETE /api/v1/compliance/frameworks/{id}?tenant_id=1
```

#### Controls

```http
# List controls
GET /api/v1/compliance/controls?tenant_id=1&framework_id=1

# Create control
POST /api/v1/compliance/controls?tenant_id=1
{
  "framework_id": 1,
  "control_id": "CC1.1",
  "title": "Control Objective",
  "description": "Control description"
}
```

#### Assessments

```http
# List assessments
GET /api/v1/compliance/assessments?tenant_id=1

# Create assessment
POST /api/v1/compliance/assessments?tenant_id=1
{
  "framework_id": 1,
  "name": "Q1 2025 Assessment",
  "scheduled_date": "2025-03-01"
}

# Run assessment
POST /api/v1/compliance/assessments/{id}/run?tenant_id=1
```

#### Compliance Score

```http
# Get overall score
GET /api/v1/compliance/score?tenant_id=1

# Get framework score
GET /api/v1/compliance/score/{framework_id}?tenant_id=1
```

### Migration Examples

**Old API (v1.0):**
```javascript
// Get compliance status
fetch('/api/compliance/status', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
```

**New API (v2.0):**
```javascript
// Get compliance score
fetch('/api/v1/compliance/score?tenant_id=1', {
  headers: {
    'Authorization': 'Bearer ' + token,
    'X-Tenant-ID': '1'
  }
})
```

---

## Service Catalog (Product #1)

### New Endpoints

#### Services

```http
# List services
GET /api/v1/service-catalog/services?tenant_id=1

# Create service
POST /api/v1/service-catalog/services?tenant_id=1
{
  "name": "VM Provisioning",
  "category": "infrastructure",
  "description": "Provision virtual machine",
  "approval_required": true
}

# Get service
GET /api/v1/service-catalog/services/{id}?tenant_id=1
```

#### Requests

```http
# List requests
GET /api/v1/service-catalog/requests?tenant_id=1

# Create request
POST /api/v1/service-catalog/requests?tenant_id=1
{
  "service_id": 1,
  "requested_by": 1,
  "request_data": {
    "cpu": 4,
    "memory": "16GB"
  }
}

# Approve request
POST /api/v1/service-catalog/requests/{id}/approve?tenant_id=1
{
  "approver_id": 2,
  "comments": "Approved"
}

# Reject request
POST /api/v1/service-catalog/requests/{id}/reject?tenant_id=1
{
  "approver_id": 2,
  "reason": "Insufficient budget"
}
```

#### Fulfillment

```http
# List tasks
GET /api/v1/service-catalog/tasks?tenant_id=1&request_id=1

# Update task
PUT /api/v1/service-catalog/tasks/{id}?tenant_id=1
{
  "status": "completed",
  "notes": "VM provisioned successfully"
}
```

### Migration Examples

**Old API (v1.0):**
```javascript
// Submit service request
fetch('/api/services/request', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    service: 'vm_provisioning',
    specs: {...}
  })
})
```

**New API (v2.0):**
```javascript
// Submit service request
fetch('/api/v1/service-catalog/requests?tenant_id=1', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'X-Tenant-ID': '1',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    service_id: 1,
    requested_by: 1,
    request_data: {...}
  })
})
```

---

## Automation Orchestrator (Product #23)

### New Endpoints

#### Workflows

```http
# List workflows
GET /api/v1/automation/workflows?tenant_id=1

# Create workflow
POST /api/v1/automation/workflows?tenant_id=1
{
  "name": "Incident Response",
  "description": "Automated incident response",
  "trigger_type": "webhook"
}

# Get workflow
GET /api/v1/automation/workflows/{id}?tenant_id=1

# Execute workflow
POST /api/v1/automation/workflows/{id}/execute?tenant_id=1
{
  "input_data": {...}
}
```

#### Nodes

```http
# List nodes
GET /api/v1/automation/workflows/{workflow_id}/nodes?tenant_id=1

# Add node
POST /api/v1/automation/workflows/{workflow_id}/nodes?tenant_id=1
{
  "node_type": "action",
  "action_type": "http_request",
  "config": {
    "url": "https://api.example.com",
    "method": "POST"
  }
}

# Update node
PUT /api/v1/automation/nodes/{id}?tenant_id=1

# Delete node
DELETE /api/v1/automation/nodes/{id}?tenant_id=1
```

#### Executions

```http
# List executions
GET /api/v1/automation/executions?tenant_id=1&workflow_id=1

# Get execution
GET /api/v1/automation/executions/{id}?tenant_id=1

# Get execution logs
GET /api/v1/automation/executions/{id}/logs?tenant_id=1
```

### Migration Examples

**Old API (v1.0):**
```javascript
// Execute workflow
fetch('/api/workflows/execute', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    workflow_id: 1,
    data: {...}
  })
})
```

**New API (v2.0):**
```javascript
// Execute workflow
fetch('/api/v1/automation/workflows/1/execute?tenant_id=1', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'X-Tenant-ID': '1'
  },
  body: JSON.stringify({
    input_data: {...}
  })
})
```

---

## Observatory (Product #36)

### New Endpoints

#### Services

```http
# Register service
POST /api/v1/observatory/services?tenant_id=1
{
  "name": "api-gateway",
  "service_type": "api",
  "environment": "production"
}

# List services
GET /api/v1/observatory/services?tenant_id=1

# Get service health
GET /api/v1/observatory/services/{id}/health?tenant_id=1
```

#### Metrics

```http
# Ingest metrics
POST /api/v1/observatory/metrics/ingest?tenant_id=1
{
  "service_id": 1,
  "metrics": [
    {
      "name": "response_time",
      "value": 150.5,
      "timestamp": "2025-08-08T12:00:00Z"
    }
  ]
}

# Query metrics
GET /api/v1/observatory/metrics?tenant_id=1&service_name=api-gateway&metric_name=response_time

# Get statistics
GET /api/v1/observatory/metrics/statistics?tenant_id=1&service_id=1
```

#### Traces

```http
# Ingest trace
POST /api/v1/observatory/traces/ingest?tenant_id=1
{
  "trace_id": "abc123",
  "service_id": 1,
  "spans": [...]
}

# Get trace
GET /api/v1/observatory/traces/{trace_id}?tenant_id=1

# Analyze traces
GET /api/v1/observatory/traces/analyze?tenant_id=1&service_id=1
```

#### Logs

```http
# Ingest logs
POST /api/v1/observatory/logs/ingest?tenant_id=1
{
  "service_id": 1,
  "logs": [
    {
      "level": "ERROR",
      "message": "Connection timeout",
      "timestamp": "2025-08-08T12:00:00Z"
    }
  ]
}

# Search logs
GET /api/v1/observatory/logs?tenant_id=1&service_id=1&level=ERROR
```

### Migration Examples

**New Feature (no v1.0 equivalent):**
```javascript
// Ingest metrics
fetch('/api/v1/observatory/metrics/ingest?tenant_id=1', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'X-Tenant-ID': '1',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    service_id: 1,
    metrics: [
      {
        name: 'response_time',
        value: 150.5,
        timestamp: new Date().toISOString()
      }
    ]
  })
})
```

---

## AI Insights (Product #3)

### New Endpoints

#### Models

```http
# Create model
POST /api/v1/ai/models?tenant_id=1
{
  "name": "Sales Forecaster",
  "model_type": "forecasting",
  "algorithm": "Prophet",
  "features": ["date", "sales", "promotions"],
  "target_variable": "future_sales"
}

# List models
GET /api/v1/ai/models?tenant_id=1

# Train model
POST /api/v1/ai/models/{id}/train?tenant_id=1
{
  "training_data": [...],
  "validation_split": 0.2
}

# Deploy model
POST /api/v1/ai/models/{id}/deploy?tenant_id=1
```

#### Predictions

```http
# Make prediction
POST /api/v1/ai/predictions?tenant_id=1
{
  "model_id": 1,
  "input_data": {
    "feature1": 100,
    "feature2": 200
  }
}

# Batch predictions
POST /api/v1/ai/predictions/batch?tenant_id=1
{
  "model_id": 1,
  "input_data_list": [...]
}

# Forecast
POST /api/v1/ai/forecast?tenant_id=1
{
  "metric_name": "sales",
  "historical_data": [...],
  "forecast_periods": 30
}
```

#### Insights

```http
# Generate insights
POST /api/v1/ai/insights/generate?tenant_id=1
{
  "data": [...],
  "metrics": ["response_time", "error_rate"],
  "time_range_days": 30
}

# List insights
GET /api/v1/ai/insights?tenant_id=1

# Generate recommendations
POST /api/v1/ai/insights/{id}/recommendations?tenant_id=1
```

#### Data Quality

```http
# Assess quality
POST /api/v1/ai/quality/assess?tenant_id=1
{
  "dataset_name": "customer_data",
  "data": [...]
}

# Get quality scores
GET /api/v1/ai/quality/scores?tenant_id=1

# Get quality trends
GET /api/v1/ai/quality/trends?tenant_id=1&dataset_name=customer_data
```

### Migration Examples

**New Feature (no v1.0 equivalent):**
```javascript
// Create and train AI model
async function createAndTrainModel() {
  // Create model
  const model = await fetch('/api/v1/ai/models?tenant_id=1', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + token,
      'X-Tenant-ID': '1',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: 'Sales Forecaster',
      model_type: 'forecasting',
      algorithm: 'Prophet',
      features: ['date', 'sales'],
      target_variable: 'future_sales'
    })
  }).then(r => r.json());
  
  // Train model
  await fetch(`/api/v1/ai/models/${model.id}/train?tenant_id=1`, {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + token,
      'X-Tenant-ID': '1',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      training_data: [...],
      validation_split: 0.2
    })
  });
  
  // Deploy model
  await fetch(`/api/v1/ai/models/${model.id}/deploy?tenant_id=1`, {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + token,
      'X-Tenant-ID': '1'
    }
  });
}
```

---

## Rate Limiting

### New Rate Limits

```
Standard Tier:
- 1,000 requests/hour per tenant
- 100 requests/minute per endpoint

Premium Tier:
- 10,000 requests/hour per tenant
- 1,000 requests/minute per endpoint

Enterprise Tier:
- Unlimited requests
```

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1625097600
```

---

## Error Codes

### New Error Codes

```
400 - Bad Request
401 - Unauthorized
403 - Forbidden
404 - Not Found
422 - Validation Error
429 - Rate Limit Exceeded
500 - Internal Server Error
503 - Service Unavailable
```

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  }
}
```

---

## SDK Updates

### Python SDK

```python
# Old (v1.0)
from itechsmart import Client
client = Client(api_key='xxx')
client.compliance.get_status()

# New (v2.0)
from itechsmart import Client
client = Client(
    api_key='xxx',
    tenant_id=1,
    version='v1'
)
client.compliance.get_score()
```

### JavaScript SDK

```javascript
// Old (v1.0)
const client = new ITechSmart({ apiKey: 'xxx' });
await client.compliance.getStatus();

// New (v2.0)
const client = new ITechSmart({
  apiKey: 'xxx',
  tenantId: 1,
  version: 'v1'
});
await client.compliance.getScore();
```

---

## Testing

### Test Your Migration

```bash
# Run migration tests
npm run test:migration

# Or manually test endpoints
curl -H "Authorization: Bearer $TOKEN" \
     -H "X-Tenant-ID: 1" \
     "https://api.itechsmart.dev/api/v1/compliance/score?tenant_id=1"
```

---

## Support

### Getting Help

- **Documentation:** https://docs.itechsmart.dev
- **API Reference:** https://api.itechsmart.dev/docs
- **Support:** support@itechsmart.dev
- **Phone:** 310-251-3969

---

**© 2025 iTechSmart Inc. All rights reserved.**