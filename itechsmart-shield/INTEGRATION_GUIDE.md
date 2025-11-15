# 🔌 iTechSmart Shield - Integration Guide

## 🎯 Overview

This guide explains how to integrate iTechSmart Shield with:
1. The iTechSmart Enterprise Hub
2. Other iTechSmart services
3. External security tools
4. Your existing infrastructure

---

## 🌐 Integration with iTechSmart Suite

### 1. Register with Enterprise Hub

Shield automatically registers with the Enterprise Hub on startup when in integrated mode.

**Automatic Registration:**

```python
# In your .env file
HUB_URL=http://localhost:8000
STANDALONE_MODE=false

# Shield will auto-register on startup
```

**Manual Registration:**

```bash
curl -X POST http://localhost:8000/api/integration/register \
  -H "Content-Type: application/json" \
  -d '{
    "service_type": "itechsmart-shield",
    "service_name": "shield-main",
    "base_url": "http://localhost:8007",
    "api_key": "shield-service-key",
    "capabilities": [
      "threat-detection",
      "vulnerability-scanning",
      "compliance-management",
      "incident-response",
      "ai-anomaly-detection"
    ],
    "metadata": {
      "version": "1.0.0",
      "supported_frameworks": ["SOC2", "ISO27001", "GDPR", "HIPAA"]
    }
  }'
```

### 2. Protect Other Services

Shield can protect all iTechSmart services:

**Enable Protection:**

```python
from app.integrations.shield_adapter import ShieldServiceAdapter

adapter = ShieldServiceAdapter()
await adapter.initialize()

# Protect a service
result = await adapter.protect_service(
    service_id="itechsmart-hl7:main",
    protection_type="full"
)

# Result:
{
  "success": true,
  "service_id": "itechsmart-hl7:main",
  "protection_enabled": {
    "threat_detection": true,
    "intrusion_prevention": true,
    "malware_scanning": true,
    "vulnerability_scanning": true,
    "compliance_monitoring": true
  }
}
```

### 3. Monitor Suite Security

**Monitor all services:**

```python
# Monitor entire suite
security_status = await adapter.monitor_suite_security()

# Result:
{
  "suite_security_score": 94.2,
  "services_monitored": 7,
  "services": {
    "itechsmart-ninja:main": {
      "status": "secure",
      "threats_detected": 0,
      "vulnerabilities": 1,
      "compliance_score": 95.0
    },
    "itechsmart-hl7:main": {
      "status": "secure",
      "threats_detected": 0,
      "vulnerabilities": 2,
      "compliance_score": 92.0
    }
    // ... other services
  }
}
```

---

## 🥷 Ninja Control Integration

### Ninja Can Control Shield

Ninja can send commands to Shield for:
- Fixing security issues
- Updating threat signatures
- Optimizing detection
- Running scans
- Generating reports

**Example: Ninja Fixes Vulnerability**

```bash
# Ninja sends fix command
curl -X POST http://localhost:8000/api/integration/ninja/control \
  -H "Content-Type: application/json" \
  -d '{
    "target_service": "itechsmart-shield:main",
    "command": "fix",
    "parameters": {
      "issue_type": "security_vulnerability",
      "vulnerability_id": 123
    }
  }'

# Shield responds:
{
  "success": true,
  "action": "patched_vulnerability",
  "vulnerability_id": 123,
  "patch_applied": true
}
```

**Supported Ninja Commands:**
- `fix` - Fix security issues
- `update` - Update signatures and rules
- `optimize` - Optimize detection
- `restart` - Restart service
- `diagnose` - Get diagnostics

---

## 🔄 Event-Driven Integration

### Subscribe to Events

Shield subscribes to events from other services:

```python
# Shield automatically subscribes to:
- user.login              # Monitor login attempts
- user.failed_login       # Detect brute force
- api.request             # Monitor API usage
- file.uploaded           # Scan uploads
- data.accessed           # Monitor data access
- system.error            # Detect issues
```

### Publish Security Events

Shield publishes events that other services can use:

```python
# Shield publishes:
- shield.threat_detected
- shield.incident_created
- shield.vulnerability_found
- shield.compliance_gap
- shield.ip_blocked
- shield.system_isolated
```

**Example: React to Shield Events**

```python
# In another service (e.g., Passport)
from integration_adapters.passport_adapter import PassportServiceAdapter

adapter = PassportServiceAdapter()

# Register event handler
async def handle_threat_detected(event_data, source_service):
    if event_data["threat_type"] == "brute_force":
        username = event_data.get("username")
        if username:
            # Lock the account
            await lock_account(username)

adapter.register_event_handler(
    event_type="shield.threat_detected",
    handler=handle_threat_detected
)
```

---

## 🔗 Cross-Service Workflows

### Example 1: Secure User Onboarding

```python
# Multi-service workflow with Shield protection
POST /api/integration/workflow/execute
{
  "workflow_name": "secure_user_onboarding",
  "steps": [
    {
      "name": "verify_identity",
      "service_id": "itechsmart-passport:main",
      "endpoint": "/api/identity/verify",
      "data": {"user_id": "user123"}
    },
    {
      "name": "scan_for_threats",
      "service_id": "itechsmart-shield:main",
      "endpoint": "/api/shield/threats/analyze",
      "data": {"source_ip": "192.168.1.100"}
    },
    {
      "name": "verify_documents",
      "service_id": "itechsmart-prooflink:main",
      "endpoint": "/api/documents/verify",
      "data": {"document_id": "DOC123"}
    },
    {
      "name": "check_compliance",
      "service_id": "itechsmart-shield:main",
      "endpoint": "/api/shield/compliance/assess",
      "data": {"framework": "GDPR"}
    }
  ]
}
```

### Example 2: Secure Healthcare Data Exchange

```python
# HL7 message with Shield protection
POST /api/integration/workflow/execute
{
  "workflow_name": "secure_hl7_exchange",
  "steps": [
    {
      "name": "authenticate_sender",
      "service_id": "itechsmart-passport:main",
      "endpoint": "/api/auth/verify"
    },
    {
      "name": "scan_message",
      "service_id": "itechsmart-shield:main",
      "endpoint": "/api/shield/threats/analyze"
    },
    {
      "name": "send_hl7_message",
      "service_id": "itechsmart-hl7:main",
      "endpoint": "/api/messages/send"
    },
    {
      "name": "verify_delivery",
      "service_id": "itechsmart-prooflink:main",
      "endpoint": "/api/proofs/generate"
    }
  ]
}
```

---

## 🔧 External Tool Integration

### 1. SIEM Integration

**Splunk:**

```python
# Send Shield alerts to Splunk
import requests

def send_to_splunk(alert):
    requests.post(
        "https://splunk.example.com:8088/services/collector",
        headers={"Authorization": "Splunk your-token"},
        json={
            "event": alert,
            "sourcetype": "itechsmart:shield"
        }
    )

# Configure webhook in Shield
POST /api/shield/webhooks
{
  "name": "splunk",
  "url": "https://splunk.example.com:8088/services/collector",
  "events": ["threat_detected", "incident_created"]
}
```

**ELK Stack:**

```python
# Send logs to Elasticsearch
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])

def send_to_elk(threat):
    es.index(
        index="shield-threats",
        document=threat
    )
```

### 2. Ticketing System Integration

**Jira:**

```python
# Create Jira ticket for incidents
from jira import JIRA

jira = JIRA('https://your-domain.atlassian.net', 
            basic_auth=('email', 'api_token'))

def create_jira_ticket(incident):
    issue = jira.create_issue(
        project='SEC',
        summary=incident['title'],
        description=incident['description'],
        issuetype={'name': 'Bug'},
        priority={'name': 'High'}
    )
    return issue.key
```

**ServiceNow:**

```python
# Create ServiceNow incident
import requests

def create_servicenow_incident(incident):
    response = requests.post(
        'https://instance.service-now.com/api/now/table/incident',
        auth=('admin', 'password'),
        json={
            'short_description': incident['title'],
            'description': incident['description'],
            'urgency': '1',
            'impact': '1'
        }
    )
    return response.json()
```

### 3. Threat Intelligence Feeds

**AlienVault OTX:**

```python
# Import threat intelligence
from OTXv2 import OTXv2

otx = OTXv2("your-api-key")

def import_threat_intel():
    pulses = otx.getall()
    for pulse in pulses:
        for indicator in pulse['indicators']:
            # Store in Shield
            requests.post(
                "http://localhost:8007/api/shield/threat-intel",
                json={
                    "ioc_type": indicator['type'],
                    "ioc_value": indicator['indicator'],
                    "source": "AlienVault OTX"
                }
            )
```

---

## 🔐 API Integration Examples

### Python SDK

```python
from itechsmart_shield import ShieldClient

# Initialize client
client = ShieldClient(
    base_url="http://localhost:8007",
    api_key="your-api-key"
)

# Analyze request
result = client.threats.analyze({
    "source_ip": "192.168.1.100",
    "url": "/api/users"
})

# Scan for vulnerabilities
scan = client.vulnerabilities.scan(
    target="192.168.1.50",
    scan_type="comprehensive"
)

# Check compliance
compliance = client.compliance.assess(
    framework="SOC2"
)
```

### JavaScript SDK

```javascript
import { ShieldClient } from '@itechsmart/shield-sdk';

// Initialize client
const client = new ShieldClient({
  baseUrl: 'http://localhost:8007',
  apiKey: 'your-api-key'
});

// Analyze request
const result = await client.threats.analyze({
  sourceIp: '192.168.1.100',
  url: '/api/users'
});

// Scan for vulnerabilities
const scan = await client.vulnerabilities.scan({
  target: '192.168.1.50',
  scanType: 'comprehensive'
});
```

---

## 🎮 Integration Patterns

### Pattern 1: Middleware Integration

```python
# Flask middleware
from flask import Flask, request
import requests

app = Flask(__name__)

@app.before_request
def check_threat():
    result = requests.post(
        "http://localhost:8007/api/shield/threats/analyze",
        json={
            "source_ip": request.remote_addr,
            "url": request.url,
            "method": request.method
        }
    )
    
    if result.json()["blocked"]:
        return "Blocked by Shield", 403
```

### Pattern 2: Event-Driven Integration

```python
# Subscribe to Shield events
from app.integrations.shield_adapter import ShieldServiceAdapter

adapter = ShieldServiceAdapter()
await adapter.initialize()

# Handle threat events
async def handle_threat(event_data, source):
    threat_type = event_data["threat_type"]
    severity = event_data["severity"]
    
    if severity == "critical":
        # Take immediate action
        await emergency_response(event_data)

adapter.register_event_handler(
    event_type="shield.threat_detected",
    handler=handle_threat
)
```

### Pattern 3: Scheduled Integration

```python
# Periodic security checks
import schedule
import requests

def daily_security_check():
    # Run vulnerability scan
    requests.post(
        "http://localhost:8007/api/shield/vulnerabilities/scan",
        json={"target": "all", "scan_type": "quick"}
    )
    
    # Check compliance
    requests.post(
        "http://localhost:8007/api/shield/compliance/assess",
        json={"framework": "SOC2"}
    )

schedule.every().day.at("02:00").do(daily_security_check)
```

---

## 🔄 Webhook Integration

### Configure Webhooks

```bash
POST /api/shield/webhooks
{
  "name": "security-alerts",
  "url": "https://your-app.com/webhooks/shield",
  "events": [
    "threat_detected",
    "incident_created",
    "vulnerability_found"
  ],
  "secret": "webhook-secret"
}
```

### Handle Webhooks

```python
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)

@app.route('/webhooks/shield', methods=['POST'])
def handle_shield_webhook():
    # Verify signature
    signature = request.headers.get('X-Shield-Signature')
    payload = request.get_data()
    
    expected = hmac.new(
        b'webhook-secret',
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if signature != expected:
        return "Invalid signature", 401
    
    # Process event
    event = request.json
    event_type = event['event_type']
    
    if event_type == 'threat_detected':
        handle_threat(event['data'])
    elif event_type == 'incident_created':
        handle_incident(event['data'])
    
    return "OK", 200
```

---

## 🎯 Use Case Examples

### Use Case 1: Protect Web Application

```python
# Add Shield protection to your web app
from flask import Flask, request
import requests

app = Flask(__name__)

def shield_protect(f):
    def wrapper(*args, **kwargs):
        # Check with Shield
        result = requests.post(
            "http://localhost:8007/api/shield/threats/analyze",
            json={
                "source_ip": request.remote_addr,
                "url": request.url,
                "method": request.method,
                "headers": dict(request.headers),
                "body": request.get_data(as_text=True)
            }
        )
        
        if result.json()["blocked"]:
            return "Access Denied", 403
        
        return f(*args, **kwargs)
    
    return wrapper

@app.route('/api/users')
@shield_protect
def get_users():
    return {"users": [...]}
```

### Use Case 2: Automated Compliance Reporting

```python
# Generate monthly compliance reports
import schedule
import requests
from datetime import datetime, timedelta

def monthly_compliance_report():
    frameworks = ["SOC2", "ISO27001", "GDPR", "HIPAA"]
    
    for framework in frameworks:
        # Assess compliance
        assessment = requests.post(
            "http://localhost:8007/api/shield/compliance/assess",
            json={"framework": framework}
        ).json()
        
        # Generate report
        report = requests.get(
            f"http://localhost:8007/api/shield/compliance/report",
            params={
                "framework": framework,
                "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "end_date": datetime.now().isoformat()
            }
        ).json()
        
        # Email to compliance team
        send_email(
            to="compliance@example.com",
            subject=f"{framework} Compliance Report",
            body=format_report(report)
        )

schedule.every().month.do(monthly_compliance_report)
```

### Use Case 3: Real-Time Threat Monitoring

```python
# Monitor threats in real-time
import asyncio
import websockets
import json

async def monitor_threats():
    uri = "ws://localhost:8007/ws/threats"
    
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            threat = json.loads(message)
            
            print(f"🚨 Threat detected: {threat['threat_type']}")
            
            if threat['severity'] == 'critical':
                # Send alert
                send_alert(threat)

asyncio.run(monitor_threats())
```

---

## 🔌 Integration with Existing Tools

### 1. Firewall Integration

**iptables:**

```python
# Sync blocked IPs with firewall
import subprocess

def sync_blocked_ips():
    # Get blocked IPs from Shield
    response = requests.get(
        "http://localhost:8007/api/shield/threats/blocked-ips"
    )
    
    blocked_ips = response.json()["blocked_ips"]
    
    # Add to iptables
    for ip in blocked_ips:
        subprocess.run([
            "iptables", "-A", "INPUT",
            "-s", ip,
            "-j", "DROP"
        ])
```

### 2. Load Balancer Integration

**Nginx:**

```nginx
# nginx.conf
http {
    # Shield protection
    location / {
        # Check with Shield before proxying
        auth_request /shield-check;
        proxy_pass http://backend;
    }
    
    location = /shield-check {
        internal;
        proxy_pass http://localhost:8007/api/shield/threats/analyze;
        proxy_pass_request_body on;
    }
}
```

### 3. Cloud Provider Integration

**AWS:**

```python
# Integrate with AWS Security Hub
import boto3

security_hub = boto3.client('securityhub')

def send_to_security_hub(threat):
    security_hub.batch_import_findings(
        Findings=[
            {
                'SchemaVersion': '2018-10-08',
                'Id': f"shield-{threat['id']}",
                'ProductArn': 'arn:aws:securityhub:...',
                'GeneratorId': 'itechsmart-shield',
                'Title': threat['description'],
                'Severity': {
                    'Label': threat['severity'].upper()
                },
                'Types': ['Software and Configuration Checks/Vulnerabilities']
            }
        ]
    )
```

---

## 📊 Monitoring Integration

### Prometheus Metrics

```python
# Expose metrics for Prometheus
from prometheus_client import Counter, Gauge, Histogram

threats_detected = Counter(
    'shield_threats_detected_total',
    'Total threats detected',
    ['threat_type', 'severity']
)

active_incidents = Gauge(
    'shield_active_incidents',
    'Number of active incidents'
)

response_time = Histogram(
    'shield_response_time_seconds',
    'Incident response time'
)
```

### Grafana Dashboards

```json
// Grafana dashboard JSON
{
  "dashboard": {
    "title": "iTechSmart Shield Security",
    "panels": [
      {
        "title": "Threats Detected",
        "targets": [
          {
            "expr": "rate(shield_threats_detected_total[5m])"
          }
        ]
      },
      {
        "title": "Active Incidents",
        "targets": [
          {
            "expr": "shield_active_incidents"
          }
        ]
      }
    ]
  }
}
```

---

## 🎯 Best Practices

### 1. Start with Monitoring
- Enable Shield monitoring first
- Observe for 1 week
- Tune sensitivity
- Then enable auto-response

### 2. Gradual Rollout
- Start with non-production
- Test thoroughly
- Roll out to production
- Monitor closely

### 3. Regular Updates
- Update threat signatures daily
- Update Shield monthly
- Review configurations quarterly

### 4. Team Training
- Train security team
- Document procedures
- Run drills
- Review incidents

---

## 🐛 Troubleshooting

### Issue: Integration Not Working

**Check:**
1. Hub URL is correct
2. API key is valid
3. Network connectivity
4. Firewall rules

**Solution:**
```bash
# Test connectivity
curl http://localhost:8000/api/integration/status

# Re-register
curl -X POST http://localhost:8000/api/integration/register \
  -d @registration.json
```

### Issue: Events Not Received

**Check:**
1. Event subscription is active
2. Event handler is registered
3. Network connectivity

**Solution:**
```python
# Re-subscribe to events
await adapter.subscribe_to_events()
```

---

## 📞 Support

For integration assistance:
- **Documentation**: https://docs.itechsmart.dev/shield/integration
- **Support**: support@itechsmart.dev
- **Community**: https://community.itechsmart.dev

---

## 🎉 Conclusion

iTechSmart Shield integrates seamlessly with:
- ✅ iTechSmart Enterprise Hub
- ✅ All iTechSmart services
- ✅ External security tools
- ✅ Your existing infrastructure

**Start protecting your entire ecosystem today!** 🛡️