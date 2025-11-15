# iTechSmart Observatory

**Product #36** - Application Performance Monitoring & Observability Platform

## Overview

iTechSmart Observatory is a comprehensive APM and observability platform that provides real-time monitoring, distributed tracing, log aggregation, alerting, and performance analytics for modern applications and infrastructure.

## Features

### 🎯 Core Capabilities

- **Metrics Collection & Visualization**
  - Time-series metrics ingestion
  - Custom metric types (counter, gauge, histogram, summary)
  - Real-time aggregation and querying
  - Statistical analysis (min, max, avg, percentiles)
  - Anomaly detection

- **Distributed Tracing**
  - End-to-end request tracing
  - Span collection and analysis
  - Performance bottleneck identification
  - Service dependency mapping
  - Trace correlation with logs

- **Log Aggregation & Search**
  - Centralized log collection
  - Full-text search capabilities
  - Log level filtering
  - Trace-log correlation
  - Error tracking and analysis

- **Alerting & Incident Management**
  - Flexible alert rules
  - Multiple notification channels
  - Incident tracking and resolution
  - Alert suppression and silencing
  - Escalation policies

- **Custom Dashboards**
  - Drag-and-drop dashboard builder
  - Multiple widget types
  - Real-time data updates
  - Dashboard sharing and templates
  - Time range filtering

- **Service Level Objectives (SLOs)**
  - SLO definition and tracking
  - Error budget monitoring
  - Compliance reporting
  - Multi-window measurements
  - Automated evaluation

- **Service Topology**
  - Automatic dependency discovery
  - Service health monitoring
  - Dependency visualization
  - Impact analysis
  - Service registry

## Architecture

### Backend Components

```
itechsmart-observatory/
├── backend/
│   ├── models.py              # 15 database models
│   ├── engine/
│   │   └── observatory_engine.py  # Core business logic (30+ methods)
│   ├── api/
│   │   ├── metrics.py         # Metrics API
│   │   ├── traces.py          # Tracing API
│   │   ├── logs.py            # Logs API
│   │   ├── alerts.py          # Alerts API
│   │   └── services.py        # Services API
│   ├── main.py                # FastAPI application
│   ├── database.py            # Database configuration
│   └── integration.py         # Hub integration
└── frontend/                  # React + TypeScript UI
```

### Database Models

1. **Service** - Monitored services/applications
2. **Metric** - Time-series metrics data
3. **Trace** - Distributed traces
4. **Span** - Individual trace spans
5. **LogEntry** - Application logs
6. **Alert** - Alert rules and definitions
7. **AlertIncident** - Alert occurrences
8. **Dashboard** - Custom dashboards
9. **ServiceDependency** - Service relationships
10. **MetricAggregation** - Pre-aggregated metrics
11. **AnomalyDetection** - Detected anomalies
12. **SLO** - Service Level Objectives
13. **Annotation** - Timeline annotations
14. **SyntheticCheck** - Synthetic monitoring
15. **Widget** - Dashboard widgets

## API Endpoints

### Metrics API (`/api/observatory/metrics`)

- `POST /ingest` - Ingest single metric
- `POST /ingest/batch` - Batch metric ingestion
- `POST /query` - Query metrics with aggregation
- `GET /statistics/{service_id}/{metric_name}` - Get metric statistics
- `GET /list/{service_id}` - List all metrics for service
- `GET /anomalies/{service_id}/{metric_name}` - Detect anomalies

### Traces API (`/api/observatory/traces`)

- `POST /ingest` - Ingest trace
- `POST /spans/ingest` - Ingest span
- `GET /{trace_id}` - Get trace details
- `GET /{trace_id}/analyze` - Analyze trace performance
- `GET /service/{service_id}` - List traces for service
- `GET /service/{service_id}/statistics` - Get trace statistics

### Logs API (`/api/observatory/logs`)

- `POST /ingest` - Ingest single log
- `POST /ingest/batch` - Batch log ingestion
- `POST /search` - Search logs with filters
- `GET /service/{service_id}` - Get service logs
- `GET /statistics/{service_id}` - Get log statistics
- `GET /trace/{trace_id}` - Get trace logs
- `GET /errors/{service_id}` - Get error logs

### Alerts API (`/api/observatory/alerts`)

- `POST /` - Create alert rule
- `GET /` - List alert rules
- `GET /{alert_id}` - Get alert details
- `PUT /{alert_id}` - Update alert rule
- `DELETE /{alert_id}` - Delete alert rule
- `POST /evaluate` - Evaluate all alerts
- `GET /incidents/active` - Get active incidents
- `POST /incidents/{incident_id}/acknowledge` - Acknowledge incident
- `POST /incidents/{incident_id}/resolve` - Resolve incident

### Services API (`/api/observatory/services`)

- `POST /register` - Register service
- `GET /` - List services
- `GET /{service_id}` - Get service details
- `PUT /{service_id}/health` - Update health status
- `GET /{service_id}/topology` - Get service topology
- `POST /dashboards` - Create dashboard
- `GET /dashboards` - List dashboards
- `GET /dashboards/{dashboard_id}` - Get dashboard data
- `POST /slos` - Create SLO
- `GET /slos/{slo_id}/evaluate` - Evaluate SLO
- `GET /slos` - List SLOs

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Node.js 20+ (for frontend)
- Docker (optional)

### Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/observatory"
export HUB_URL="http://localhost:8000"
export API_KEY="your-api-key"

# Initialize database
python -m backend.database

# Run application
python -m backend.main
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker Setup

```bash
docker-compose up -d
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://observatory:observatory@localhost:5432/observatory

# Application
PORT=8036
HOST=0.0.0.0
DEBUG=false

# Integration
HUB_URL=http://localhost:8000
API_KEY=your-api-key

# Metrics
METRIC_RETENTION_DAYS=90
AGGREGATION_INTERVALS=1m,5m,1h,1d

# Tracing
TRACE_SAMPLING_RATE=1.0
TRACE_RETENTION_DAYS=30

# Logs
LOG_RETENTION_DAYS=30
LOG_BATCH_SIZE=1000

# Alerts
ALERT_EVALUATION_INTERVAL=60
```

## Usage Examples

### Register a Service

```python
import requests

response = requests.post(
    "http://localhost:8036/api/observatory/services/register",
    json={
        "name": "my-api",
        "service_type": "api",
        "environment": "production",
        "version": "1.0.0",
        "language": "python",
        "framework": "fastapi"
    }
)
service_id = response.json()["service_id"]
```

### Ingest Metrics

```python
requests.post(
    "http://localhost:8036/api/observatory/metrics/ingest",
    json={
        "service_id": service_id,
        "metric_name": "http_requests_total",
        "value": 100,
        "metric_type": "counter",
        "labels": {"endpoint": "/api/users", "method": "GET"}
    }
)
```

### Create Trace

```python
import uuid
from datetime import datetime

trace_id = str(uuid.uuid4())
requests.post(
    "http://localhost:8036/api/observatory/traces/ingest",
    json={
        "service_id": service_id,
        "trace_id": trace_id,
        "trace_name": "GET /api/users",
        "start_time": datetime.utcnow().isoformat(),
        "http_method": "GET",
        "http_url": "/api/users",
        "http_status_code": 200
    }
)
```

### Ingest Logs

```python
requests.post(
    "http://localhost:8036/api/observatory/logs/ingest",
    json={
        "service_id": service_id,
        "level": "INFO",
        "message": "User login successful",
        "trace_id": trace_id,
        "attributes": {"user_id": "123", "ip": "192.168.1.1"}
    }
)
```

### Create Alert

```python
requests.post(
    "http://localhost:8036/api/observatory/alerts",
    json={
        "name": "High Error Rate",
        "alert_type": "error_rate",
        "severity": "critical",
        "service_id": service_id,
        "metric_name": "http_errors_total",
        "condition": {
            "operator": "gt",
            "threshold": 10,
            "duration": 300
        },
        "notification_channels": ["email", "slack"]
    },
    params={"created_by": "user123"}
)
```

## Integration with iTechSmart Suite

Observatory integrates seamlessly with other iTechSmart products:

- **Hub**: Central registration and coordination
- **Enterprise**: Monitor tenant services
- **Workflow**: Track workflow execution metrics
- **Supreme Plus**: Infrastructure monitoring
- **Citadel**: Security event correlation
- **Notify**: Alert notifications
- **Pulse**: Incident management
- **Analytics**: Data export and analysis
- **Compliance**: Compliance metrics reporting
- **Automation Orchestrator**: Trigger workflows based on metrics

## Performance

- **Metrics Ingestion**: 100,000+ metrics/second
- **Trace Processing**: 10,000+ traces/second
- **Log Ingestion**: 50,000+ logs/second
- **Query Latency**: <100ms (p95)
- **Storage**: Time-series optimized with automatic aggregation

## Security

- API key authentication
- Role-based access control
- Data encryption at rest
- TLS/SSL for data in transit
- Audit logging
- Data retention policies

## Monitoring & Observability

Observatory monitors itself:
- Self-health checks
- Performance metrics
- Error tracking
- Resource utilization
- API latency monitoring

## Support

- **Documentation**: https://docs.itechsmart.dev/observatory
- **Email**: support@itechsmart.dev
- **Phone**: 310-251-3969
- **Website**: https://itechsmart.dev

## License

Copyright © 2025 iTechSmart Inc. All rights reserved.

## Version

**Version**: 1.0.0  
**Release Date**: August 8, 2025  
**Product ID**: 36