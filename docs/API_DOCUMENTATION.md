# iTechSmart Suite - Complete API Documentation

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [iTechSmart Enterprise API](#itechsmart-enterprise-api)
4. [iTechSmart Analytics API](#itechsmart-analytics-api)
5. [iTechSmart Ninja API](#itechsmart-ninja-api)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Webhooks](#webhooks)
9. [SDKs & Libraries](#sdks--libraries)

---

## Overview

The iTechSmart Suite provides RESTful APIs for all products with consistent patterns, authentication, and error handling.

**Base URLs**:
- Enterprise: `https://api.itechsmart.dev/enterprise`
- Analytics: `https://api.itechsmart.dev/analytics`
- Ninja: `https://api.itechsmart.dev/ninja`

**API Version**: v1
**Content-Type**: `application/json`
**Authentication**: Bearer Token (JWT)

---

## Authentication

### Login

**Endpoint**: `POST /api/auth/login`

**Request**:
```json
{
  "username": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response**:
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com",
    "role": "admin",
    "permissions": ["read", "write", "admin"]
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400
}
```

### Refresh Token

**Endpoint**: `POST /api/auth/refresh`

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response**:
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400
}
```

### Using Access Token

Include the access token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## iTechSmart Enterprise API

### Dashboard

#### Get Suite Overview

**Endpoint**: `GET /api/dashboard/overview`

**Response**:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "products": {
    "total_products": 9,
    "active_products": 9,
    "inactive_products": 0,
    "products": [
      {
        "id": 1,
        "name": "iTechSmart Analytics",
        "type": "analytics",
        "status": "active",
        "version": "1.0.0",
        "uptime": "30d 5h",
        "health_score": 98.5
      }
    ]
  },
  "health": {
    "overall_status": "healthy",
    "healthy_services": 9,
    "degraded_services": 0,
    "unhealthy_services": 0,
    "average_response_time": 45.2
  },
  "activity": {
    "total_events_24h": 15420,
    "total_syncs_24h": 342,
    "successful_syncs": 340,
    "failed_syncs": 2,
    "active_workflows": 12
  }
}
```

#### Get Real-Time Metrics

**Endpoint**: `GET /api/dashboard/metrics/realtime`

**Response**:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "active_services": 9,
  "events_per_minute": 10.5,
  "active_syncs": 3,
  "average_response_time": 42.3
}
```

### Integration

#### Register Service

**Endpoint**: `POST /api/integration/services`

**Request**:
```json
{
  "name": "My Service",
  "service_type": "custom",
  "version": "1.0.0",
  "endpoint_url": "https://myservice.com",
  "capabilities": ["data_sync", "webhooks"],
  "metadata": {
    "description": "Custom service integration"
  }
}
```

**Response**:
```json
{
  "id": 10,
  "name": "My Service",
  "service_type": "custom",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Sync Data

**Endpoint**: `POST /api/integration/sync`

**Request**:
```json
{
  "source_service": "iTechSmart Analytics",
  "target_service": "My Service",
  "data_type": "metrics",
  "metrics": ["revenue", "users", "conversions"],
  "date_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-15T23:59:59Z"
  }
}
```

**Response**:
```json
{
  "id": 1234,
  "status": "completed",
  "records_synced": 1500,
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:15Z"
}
```

---

## iTechSmart Analytics API

### Forecasting

#### Generate Forecast

**Endpoint**: `POST /api/analytics/forecast`

**Request**:
```json
{
  "metric": "revenue",
  "data_source": "enterprise_metrics",
  "horizon": 30,
  "model_type": "auto"
}
```

**Response**:
```json
{
  "metric": "revenue",
  "model_type": "rf",
  "forecast": [
    {
      "date": "2024-01-16T00:00:00Z",
      "value": 125000.50,
      "lower_bound": 120000.00,
      "upper_bound": 130000.00
    },
    {
      "date": "2024-01-17T00:00:00Z",
      "value": 126500.75,
      "lower_bound": 121500.00,
      "upper_bound": 131500.00
    }
  ],
  "accuracy_score": 0.92,
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### Anomaly Detection

#### Detect Anomalies

**Endpoint**: `POST /api/analytics/anomalies`

**Request**:
```json
{
  "metric": "error_rate",
  "data_source": "enterprise_metrics",
  "sensitivity": "high"
}
```

**Response**:
```json
{
  "metric": "error_rate",
  "sensitivity": "high",
  "total_points": 1000,
  "anomalies_detected": 5,
  "anomalies": [
    {
      "timestamp": "2024-01-15T08:30:00Z",
      "value": 15.5,
      "anomaly_score": 0.95,
      "severity": "critical"
    },
    {
      "timestamp": "2024-01-15T09:15:00Z",
      "value": 12.3,
      "anomaly_score": 0.87,
      "severity": "high"
    }
  ],
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### Dashboards

#### Create Dashboard

**Endpoint**: `POST /api/analytics/dashboards?user_id=1`

**Request**:
```json
{
  "name": "Sales Dashboard",
  "description": "Real-time sales metrics",
  "layout": {
    "type": "grid",
    "columns": 12
  }
}
```

**Response**:
```json
{
  "id": 1,
  "name": "Sales Dashboard",
  "description": "Real-time sales metrics",
  "user_id": 1,
  "layout": {
    "type": "grid",
    "columns": 12
  },
  "widgets": [],
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Add Widget

**Endpoint**: `POST /api/analytics/dashboards/{dashboard_id}/widgets`

**Request**:
```json
{
  "type": "line_chart",
  "title": "Revenue Trend",
  "data_source": "sales_data",
  "config": {
    "metrics": ["revenue"],
    "time_range": "30d",
    "show_legend": true
  },
  "position": {
    "x": 0,
    "y": 0,
    "w": 6,
    "h": 4
  }
}
```

**Response**:
```json
{
  "id": 1,
  "dashboard_id": 1,
  "type": "line_chart",
  "title": "Revenue Trend",
  "data_source": "sales_data",
  "config": {
    "metrics": ["revenue"],
    "time_range": "30d",
    "show_legend": true
  },
  "position": {
    "x": 0,
    "y": 0,
    "w": 6,
    "h": 4
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Reports

#### Generate Report

**Endpoint**: `POST /api/reports/generate`

**Request**:
```json
{
  "report_id": 1,
  "date_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-15T23:59:59Z"
  },
  "filters": {
    "region": "North America"
  }
}
```

**Response**:
```json
{
  "success": true,
  "report_id": 1,
  "name": "Monthly Sales Report",
  "format": "pdf",
  "generated_at": "2024-01-15T10:30:00Z",
  "duration_seconds": 2.5,
  "size_bytes": 524288,
  "download_url": "https://api.itechsmart.dev/reports/download/abc123"
}
```

#### Schedule Report

**Endpoint**: `POST /api/reports/schedule`

**Request**:
```json
{
  "report_id": 1,
  "frequency": "weekly",
  "delivery_method": "email",
  "delivery_config": {
    "recipients": ["manager@example.com", "team@example.com"]
  }
}
```

**Response**:
```json
{
  "id": 1,
  "report_id": 1,
  "frequency": "weekly",
  "delivery_method": "email",
  "status": "active",
  "next_run": "2024-01-22T00:00:00Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Data Ingestion

#### Create Data Source

**Endpoint**: `POST /api/ingestion/sources`

**Request**:
```json
{
  "name": "Sales Database",
  "source_type": "database",
  "config": {
    "connection_string": "postgresql://user:pass@host:5432/db",
    "query": "SELECT * FROM sales WHERE date >= :start_date"
  },
  "ingestion_mode": "batch"
}
```

**Response**:
```json
{
  "id": 1,
  "name": "Sales Database",
  "type": "database",
  "config": {
    "connection_string": "postgresql://user:***@host:5432/db",
    "query": "SELECT * FROM sales WHERE date >= :start_date"
  },
  "ingestion_mode": "batch",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Ingest Data

**Endpoint**: `POST /api/ingestion/ingest`

**Request**:
```json
{
  "source_id": 1,
  "data": [
    {
      "date": "2024-01-15",
      "revenue": 125000,
      "orders": 450
    }
  ],
  "metadata": {
    "batch_id": "batch_001"
  }
}
```

**Response**:
```json
{
  "success": true,
  "source_id": 1,
  "records_ingested": 1,
  "duration_seconds": 0.15,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## iTechSmart Ninja API

### Suite Control

#### Analyze Service

**Endpoint**: `POST /api/suite-control/analyze`

**Request**:
```json
{
  "analysis_type": "performance_optimization",
  "target_service": "iTechSmart Supreme",
  "parameters": {
    "metric": "response_time",
    "threshold": 1000
  }
}
```

**Response**:
```json
{
  "task_id": "task_abc123",
  "status": "running",
  "analysis_type": "performance_optimization",
  "target_service": "iTechSmart Supreme",
  "started_at": "2024-01-15T10:30:00Z"
}
```

#### Fix Issues

**Endpoint**: `POST /api/suite-control/fix`

**Request**:
```json
{
  "service_id": 3,
  "issue_type": "performance_degradation",
  "auto_apply": true
}
```

**Response**:
```json
{
  "fix_id": "fix_xyz789",
  "status": "applied",
  "service_id": 3,
  "issue_type": "performance_degradation",
  "fixes_applied": [
    "Optimized database queries",
    "Increased cache TTL",
    "Added connection pooling"
  ],
  "completed_at": "2024-01-15T10:30:30Z"
}
```

### Self-Healing

#### Get Health Status

**Endpoint**: `GET /api/self-healing/status`

**Response**:
```json
{
  "status": "healthy",
  "last_check": "2024-01-15T10:30:00Z",
  "errors_detected": 0,
  "fixes_applied": 5,
  "uptime": "30d 5h 23m"
}
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTHENTICATION_REQUIRED` | 401 | Missing or invalid authentication token |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required permissions |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource does not exist |
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

---

## Rate Limiting

**Default Limits**:
- 1000 requests per hour per user
- 100 requests per minute per IP
- 10 concurrent requests per user

**Rate Limit Headers**:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1705320600
```

**Rate Limit Exceeded Response**:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "retry_after": 3600
  }
}
```

---

## Webhooks

### Configure Webhook

**Endpoint**: `POST /api/webhooks`

**Request**:
```json
{
  "url": "https://myapp.com/webhooks/itechsmart",
  "events": ["forecast.completed", "anomaly.detected", "report.generated"],
  "secret": "webhook_secret_key"
}
```

**Response**:
```json
{
  "id": 1,
  "url": "https://myapp.com/webhooks/itechsmart",
  "events": ["forecast.completed", "anomaly.detected", "report.generated"],
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Webhook Payload

```json
{
  "event": "anomaly.detected",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "metric": "error_rate",
    "value": 15.5,
    "severity": "critical",
    "service": "iTechSmart Supreme"
  },
  "signature": "sha256=abc123..."
}
```

---

## SDKs & Libraries

### Python SDK

```python
from itechsmart import ITechSmartClient

# Initialize client
client = ITechSmartClient(
    api_key="your_api_key",
    base_url="https://api.itechsmart.dev"
)

# Generate forecast
forecast = client.analytics.forecast(
    metric="revenue",
    data_source="sales_data",
    horizon=30
)

# Detect anomalies
anomalies = client.analytics.detect_anomalies(
    metric="error_rate",
    sensitivity="high"
)

# Create dashboard
dashboard = client.analytics.create_dashboard(
    name="Sales Dashboard",
    description="Real-time sales metrics"
)
```

### JavaScript SDK

```javascript
import { ITechSmartClient } from '@itechsmart/sdk';

// Initialize client
const client = new ITechSmartClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.itechsmart.dev'
});

// Generate forecast
const forecast = await client.analytics.forecast({
  metric: 'revenue',
  dataSource: 'sales_data',
  horizon: 30
});

// Detect anomalies
const anomalies = await client.analytics.detectAnomalies({
  metric: 'error_rate',
  sensitivity: 'high'
});
```

---

## Support

- **Documentation**: https://docs.itechsmart.dev
- **API Status**: https://status.itechsmart.dev
- **Support Email**: api-support@itechsmart.dev
- **Community**: https://community.itechsmart.dev