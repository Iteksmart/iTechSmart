# iTechSmart Sentinel

**Real-Time Observability & Incident Management Platform**

Product #31 in the iTechSmart Suite

---

## 🎯 Overview

iTechSmart Sentinel is a comprehensive observability platform that provides real-time monitoring, alerting, and incident management across your entire infrastructure. Built to replace expensive tools like Datadog, PagerDuty, and New Relic, Sentinel offers enterprise-grade observability at a fraction of the cost.

### Key Features

#### 🔍 Distributed Tracing
- Track requests across all 30+ iTechSmart products
- OpenTelemetry integration for standardized tracing
- Visualize service dependencies and data flow
- Identify bottlenecks and performance issues
- P50, P95, P99 latency percentiles
- Trace search and filtering

#### 🚨 Smart Alerting
- ML-based alert fatigue reduction
- Intelligent alert routing and escalation
- Alert deduplication and grouping
- On-call scheduling and rotation
- Multi-channel notifications (Slack, email, SMS, phone)
- Alert statistics and analytics

#### 📊 Log Aggregation
- Centralized logs from all services
- Natural language log search
- Anomaly detection in logs
- Log pattern recognition
- Error log tracking
- Trace-log correlation

#### 🎯 Incident Management
- Automated incident creation from alerts
- Incident timeline and war rooms
- Runbook automation
- Post-mortem generation
- MTTR and MTTA tracking
- Root cause analysis

#### 📈 SLO Tracking
- Define Service Level Objectives
- Error budget tracking
- Burn rate alerts
- SLO compliance reporting
- Predictive breach detection
- Multi-window SLO support

---

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker Compose (Recommended)

```bash
# Clone the repository
cd itechsmart-sentinel

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Access Points
- **Frontend**: http://localhost:3310
- **Backend API**: http://localhost:8310
- **API Documentation**: http://localhost:8310/docs
- **PostgreSQL**: localhost:5432

---

## 📋 Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    iTechSmart Sentinel                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Tracing    │  │   Alerting   │  │     Logs     │      │
│  │    Engine    │  │    Engine    │  │    Engine    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │   Incident   │  │     SLO      │                         │
│  │    Engine    │  │    Engine    │                         │
│  └──────────────┘  └──────────────┘                         │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│              PostgreSQL Database + Redis Cache               │
└─────────────────────────────────────────────────────────────┘
         │                                    │
         ▼                                    ▼
┌──────────────────┐              ┌──────────────────┐
│ Enterprise Hub   │              │  Ninja (Self-    │
│  (Integration)   │              │    Healing)      │
└──────────────────┘              └──────────────────┘
```

### Integration with iTechSmart Suite

Sentinel automatically integrates with:
- **Enterprise Hub**: Service registration, health reporting, metrics collection
- **Ninja**: Error reporting, auto-healing, performance monitoring
- **All 30 Products**: Automatic observability for the entire suite

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# Server
PORT=8310
HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://sentinel:sentinel_password@postgres:5432/sentinel

# iTechSmart Suite Integration
ENTERPRISE_HUB_URL=http://localhost:8001
NINJA_URL=http://localhost:8002

# Service
SERVICE_NAME=itechsmart-sentinel
SERVICE_VERSION=1.0.0

# Logging
LOG_LEVEL=INFO
```

---

## 📡 API Endpoints

### Distributed Tracing
- `POST /api/tracing/traces` - Create trace
- `POST /api/tracing/spans` - Add span
- `GET /api/tracing/traces/{trace_id}` - Get trace
- `GET /api/tracing/traces` - Search traces
- `GET /api/tracing/services/{service_name}/dependencies` - Get dependencies
- `GET /api/tracing/statistics` - Get statistics
- `GET /api/tracing/slow-traces` - Get slow traces

### Alerting
- `POST /api/alerts` - Create alert
- `POST /api/alerts/{alert_id}/acknowledge` - Acknowledge alert
- `POST /api/alerts/{alert_id}/resolve` - Resolve alert
- `POST /api/alerts/{alert_id}/silence` - Silence alert
- `GET /api/alerts/active` - Get active alerts
- `GET /api/alerts/statistics` - Get statistics
- `GET /api/alerts/fatigue` - Detect alert fatigue

### Log Aggregation
- `POST /api/logs/ingest` - Ingest log
- `GET /api/logs/search` - Search logs (NL support)
- `GET /api/logs/patterns` - Get log patterns
- `GET /api/logs/statistics` - Get statistics
- `GET /api/logs/errors` - Get error logs
- `GET /api/logs/anomalies` - Get anomalous logs
- `GET /api/logs/trace/{trace_id}` - Correlate with trace

### Incident Management
- `POST /api/incidents` - Create incident
- `POST /api/incidents/{incident_id}/status` - Update status
- `POST /api/incidents/{incident_id}/updates` - Add update
- `POST /api/incidents/{incident_id}/assign` - Assign incident
- `POST /api/incidents/{incident_id}/root-cause` - Add root cause
- `GET /api/incidents/active` - Get active incidents
- `GET /api/incidents/{incident_id}/timeline` - Get timeline
- `GET /api/incidents/statistics` - Get statistics
- `GET /api/incidents/{incident_id}/post-mortem` - Generate post-mortem

### SLO Tracking
- `POST /api/slo` - Create SLO
- `POST /api/slo/{slo_id}/measurements` - Record measurement
- `GET /api/slo/{slo_id}/status` - Get status
- `GET /api/slo/{slo_id}/history` - Get history
- `GET /api/slo` - Get all SLOs
- `GET /api/slo/violations` - Check violations
- `GET /api/slo/{slo_id}/predict` - Predict breach
- `GET /api/slo/report` - Generate report

---

## 💡 Usage Examples

### Creating a Trace

```python
import httpx
from datetime import datetime

async def create_trace():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8310/api/tracing/traces",
            json={
                "service_name": "my-service",
                "operation_name": "GET /api/users",
                "start_time": datetime.utcnow().isoformat(),
                "end_time": datetime.utcnow().isoformat(),
                "status_code": 200,
                "http_method": "GET",
                "http_url": "/api/users"
            }
        )
        return response.json()
```

### Creating an Alert

```python
async def create_alert():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8310/api/alerts",
            json={
                "service_name": "my-service",
                "alert_name": "high_latency",
                "alert_type": "threshold",
                "severity": "high",
                "title": "High latency detected",
                "description": "P95 latency exceeded 1000ms",
                "current_value": 1250.0,
                "threshold_value": 1000.0
            }
        )
        return response.json()
```

### Searching Logs

```python
async def search_logs():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8310/api/logs/search",
            params={
                "query": "error database connection",
                "service_name": "my-service",
                "level": "ERROR",
                "limit": 100
            }
        )
        return response.json()
```

---

## 🎨 Features in Detail

### ML-Based Alert Fatigue Reduction

Sentinel uses machine learning to detect and reduce alert fatigue:
- **Flapping Detection**: Identifies alerts that fire/resolve repeatedly
- **Noisy Alert Detection**: Finds high-frequency low-severity alerts
- **Smart Grouping**: Groups related alerts automatically
- **Fatigue Score**: 0-100 score indicating alert health
- **Recommendations**: Actionable suggestions to reduce fatigue

### Natural Language Log Search

Search logs using natural language:
- "show me errors from database"
- "find timeout issues in API"
- "get critical logs from last hour"

### Predictive SLO Breach Detection

Sentinel predicts SLO breaches before they happen:
- Analyzes current burn rate
- Projects error budget consumption
- Calculates time to breach
- Provides confidence scores
- Sends proactive alerts

---

## 📊 Monitoring & Metrics

### Key Metrics Tracked

- **Traces**: Total count, error rate, latency percentiles
- **Alerts**: Active count, by severity, MTTR
- **Logs**: Total count, error rate, anomaly rate
- **Incidents**: Open count, MTTR, MTTA
- **SLOs**: Compliance rate, error budget, burn rate

### Health Checks

- Database connectivity
- Service health
- Integration status
- Resource usage

---

## 🔒 Security

- JWT-based authentication
- Role-based access control (RBAC)
- TLS 1.3 encryption
- Audit logging
- Secrets management via Vault integration

---

## 🚀 Deployment

### Production Deployment

```bash
# Build images
docker-compose build

# Start in production mode
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale backend=3
```

### Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n sentinel

# View logs
kubectl logs -f deployment/sentinel-backend -n sentinel
```

---

## 📈 Performance

- **API Response Time**: <100ms (P95)
- **Throughput**: >1000 req/sec
- **Trace Ingestion**: >10,000 traces/sec
- **Log Ingestion**: >50,000 logs/sec
- **Concurrent Users**: 500+

---

## 🤝 Integration

### With iTechSmart Suite

Sentinel automatically integrates with all iTechSmart products:
- Receives traces, logs, and metrics
- Creates alerts and incidents
- Tracks SLOs
- Provides unified observability

### With External Tools

- **OpenTelemetry**: Standard tracing protocol
- **Prometheus**: Metrics export
- **Grafana**: Dashboard integration
- **Slack**: Alert notifications
- **PagerDuty**: Incident routing

---

## 📝 License

Part of the iTechSmart Suite - Proprietary Software

---

## 🆘 Support

- **Documentation**: http://localhost:8310/docs
- **Health Check**: http://localhost:8310/health
- **Suite Info**: http://localhost:8310/suite-info

---

## 🎯 Roadmap

- [ ] Machine learning anomaly detection
- [ ] Advanced service mesh support
- [ ] Custom dashboard builder
- [ ] Mobile app
- [ ] AI-powered root cause analysis
- [ ] Automated remediation

---

**Built with ❤️ by the iTechSmart Inc**

*Replacing Datadog, PagerDuty, and New Relic - One Platform at a Time*
## 🤖 Agent Integration

This product integrates with the iTechSmart Agent monitoring system through the License Server. The agent system provides:

- Real-time system monitoring
- Performance metrics collection
- Security status tracking
- Automated alerting

### Configuration

Set the License Server URL in your environment:

```bash
LICENSE_SERVER_URL=http://localhost:3000
```

The product will automatically connect to the License Server to access agent data and monitoring capabilities.



## 🚀 Upcoming Features (v1.4.0)

1. **Smart alert grouping and correlation**
2. **Escalation policies with multiple channels**
3. **On-call scheduling and rotation**
4. **Mobile push notifications (iOS/Android)**
5. **Integration with incident management tools**
6. **Custom alert rules and conditions**
7. **Historical alert analysis and trends**
8. **Automated alert remediation**

**Product Value**: $1.8M  
**Tier**: 2  
**Total Features**: 8

