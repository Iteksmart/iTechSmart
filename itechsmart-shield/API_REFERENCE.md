# 📚 iTechSmart Shield - Complete API Reference

## 🎯 Base URL

```
http://localhost:8007/api/shield
```

---

## 🔐 Authentication

All API requests require authentication:

```bash
# API Key in header
X-API-Key: your-api-key

# Or JWT token
Authorization: Bearer your-jwt-token
```

---

## 📋 API Endpoints

### 🚨 Threat Detection Endpoints

#### 1. Analyze Request for Threats

```http
POST /threats/analyze
```

**Request Body:**
```json
{
  "source_ip": "192.168.1.100",
  "url": "/api/users?id=1",
  "method": "GET",
  "headers": {},
  "body": ""
}
```

**Response:**
```json
{
  "blocked": false,
  "threats": [
    {
      "type": "sql_injection",
      "severity": "high",
      "confidence": 0.85,
      "description": "SQL injection pattern detected"
    }
  ],
  "threat_count": 1
}
```

#### 2. Analyze Login Attempt

```http
POST /threats/login-attempt
```

**Request Body:**
```json
{
  "username": "john.doe",
  "source_ip": "192.168.1.100",
  "success": false
}
```

**Response:**
```json
{
  "threat_detected": true,
  "blocked": true,
  "threat": {
    "type": "brute_force",
    "severity": "high",
    "confidence": 0.9,
    "description": "Brute force attack detected: 5 failed attempts"
  }
}
```

#### 3. Analyze Network Traffic

```http
POST /threats/network-traffic
```

**Request Body:**
```json
{
  "source_ip": "192.168.1.100",
  "dest_ip": "10.0.0.50",
  "protocol": "TCP",
  "payload": null
}
```

**Response:**
```json
{
  "threats": [],
  "threat_count": 0
}
```

#### 4. List Threats

```http
GET /threats?limit=100&severity=high&status=detected
```

**Response:**
```json
{
  "threats": [
    {
      "id": 1,
      "timestamp": "2025-01-15T10:30:00Z",
      "threat_type": "sql_injection",
      "severity": "high",
      "status": "detected",
      "source_ip": "192.168.1.100",
      "confidence_score": 0.85
    }
  ],
  "count": 1
}
```

#### 5. Get Threat Details

```http
GET /threats/{threat_id}
```

**Response:**
```json
{
  "id": 1,
  "timestamp": "2025-01-15T10:30:00Z",
  "threat_type": "sql_injection",
  "severity": "high",
  "status": "detected",
  "source_ip": "192.168.1.100",
  "target_ip": "10.0.0.50",
  "description": "SQL injection attempt detected",
  "indicators": {},
  "confidence_score": 0.85,
  "automated_response": true,
  "response_actions": []
}
```

#### 6. Get Blocked IPs

```http
GET /threats/blocked-ips
```

**Response:**
```json
{
  "blocked_ips": ["192.168.1.100", "10.0.0.200"],
  "count": 2
}
```

#### 7. Block IP Address

```http
POST /threats/block-ip?ip=192.168.1.100&reason=Manual+block
```

**Response:**
```json
{
  "success": true,
  "ip": "192.168.1.100",
  "reason": "Manual block"
}
```

#### 8. Unblock IP Address

```http
POST /threats/unblock-ip?ip=192.168.1.100
```

**Response:**
```json
{
  "success": true,
  "ip": "192.168.1.100"
}
```

---

### 🤖 AI Anomaly Detection Endpoints

#### 9. Analyze User Behavior

```http
POST /anomaly/user-behavior
```

**Request Body:**
```json
{
  "user_id": "user123",
  "action": "delete_database",
  "context": {
    "location": "New York",
    "device": "laptop",
    "time": "2025-01-15T02:00:00Z"
  }
}
```

**Response:**
```json
{
  "anomaly_detected": true,
  "anomaly_score": 3.5,
  "severity": "high",
  "deviations": [
    "Unusual time: 2:00",
    "High-risk action: delete_database"
  ]
}
```

#### 10. Analyze API Usage

```http
POST /anomaly/api-usage
```

**Request Body:**
```json
{
  "user_id": "user123",
  "endpoint": "/api/admin/users",
  "method": "DELETE",
  "response_time": 150.5
}
```

**Response:**
```json
{
  "anomaly_detected": false,
  "anomaly_score": 1.2
}
```

#### 11. Detect Zero-Day Threats

```http
POST /anomaly/zero-day
```

**Request Body:**
```json
{
  "event_type": "file_execution",
  "file_hash": "abc123...",
  "behavior": "network_connection"
}
```

**Response:**
```json
{
  "zero_day_detected": true,
  "threat_score": 0.85,
  "confidence": 0.85,
  "recommendation": "Immediate investigation required"
}
```

---

### 🚨 Incident Response Endpoints

#### 12. List Incidents

```http
GET /incidents?limit=50&status=open&severity=high
```

**Response:**
```json
{
  "incidents": [
    {
      "incident_id": "INC-20250115-ABC123",
      "created_at": "2025-01-15T10:30:00Z",
      "incident_type": "malware",
      "severity": "critical",
      "status": "open",
      "title": "MALWARE detected from 192.168.1.100",
      "automated_response": true
    }
  ],
  "count": 1
}
```

#### 13. Get Incident Details

```http
GET /incidents/{incident_id}
```

**Response:**
```json
{
  "incident_id": "INC-20250115-ABC123",
  "created_at": "2025-01-15T10:30:00Z",
  "incident_type": "malware",
  "severity": "critical",
  "status": "contained",
  "title": "MALWARE detected from 192.168.1.100",
  "description": "Malware detected in network traffic",
  "affected_systems": ["10.0.0.50"],
  "timeline": [
    {
      "timestamp": "2025-01-15T10:30:00Z",
      "event": "Incident created"
    },
    {
      "timestamp": "2025-01-15T10:31:00Z",
      "event": "Automated response executed"
    }
  ],
  "response_actions": [
    {
      "action": "isolate_system",
      "target": "10.0.0.50",
      "result": {"success": true}
    }
  ]
}
```

#### 14. Respond to Incident

```http
POST /incidents/{incident_id}/respond
```

**Request Body:**
```json
{
  "incident_id": "INC-20250115-ABC123",
  "response_type": "auto"
}
```

**Response:**
```json
{
  "success": true,
  "actions": [
    {
      "action": "isolate_system",
      "result": {"success": true}
    }
  ],
  "message": "Incident contained"
}
```

---

### 🔍 Vulnerability Scanning Endpoints

#### 15. Scan System

```http
POST /vulnerabilities/scan
```

**Request Body:**
```json
{
  "target": "192.168.1.50",
  "scan_type": "comprehensive"
}
```

**Response:**
```json
{
  "target": "192.168.1.50",
  "scan_type": "comprehensive",
  "vulnerabilities_found": 5,
  "critical": 1,
  "high": 2,
  "medium": 2,
  "low": 0,
  "vulnerabilities": [...]
}
```

#### 16. List Vulnerabilities

```http
GET /vulnerabilities?limit=100&severity=high&status=open
```

**Response:**
```json
{
  "vulnerabilities": [
    {
      "id": 1,
      "discovered_at": "2025-01-15T10:30:00Z",
      "cve_id": "CVE-2025-1234",
      "vulnerability_type": "sql_injection",
      "severity": "high",
      "affected_asset": "192.168.1.50",
      "cvss_score": 7.5,
      "status": "open"
    }
  ],
  "count": 1
}
```

#### 17. Get Vulnerability Report

```http
GET /vulnerabilities/report?asset=192.168.1.50
```

**Response:**
```json
{
  "total_vulnerabilities": 5,
  "critical": 1,
  "high": 2,
  "medium": 2,
  "low": 0,
  "vulnerabilities": [...]
}
```

---

### ✅ Compliance Endpoints

#### 18. Assess Compliance

```http
POST /compliance/assess
```

**Request Body:**
```json
{
  "framework": "SOC2"
}
```

**Response:**
```json
{
  "framework": "SOC2",
  "compliance_score": 95.5,
  "total_controls": 20,
  "compliant": 19,
  "non_compliant": 1,
  "gaps": [
    {
      "control_id": "CC6.1",
      "control_name": "Access Controls",
      "status": "non_compliant",
      "gaps": ["MFA not enabled for all users"]
    }
  ]
}
```

#### 19. Get Compliance Report

```http
GET /compliance/report?framework=SOC2&start_date=2025-01-01&end_date=2025-01-31
```

**Response:**
```json
{
  "framework": "SOC2",
  "period": {
    "start": "2025-01-01T00:00:00Z",
    "end": "2025-01-31T23:59:59Z"
  },
  "total_checks": 100,
  "compliant": 95,
  "compliance_rate": 0.95,
  "checks": [...]
}
```

#### 20. List Compliance Checks

```http
GET /compliance/checks?framework=SOC2&limit=100
```

**Response:**
```json
{
  "checks": [
    {
      "id": 1,
      "timestamp": "2025-01-15T10:30:00Z",
      "framework": "SOC2",
      "control_id": "CC6.1",
      "control_name": "Access Controls",
      "status": "compliant",
      "compliance_score": 100
    }
  ],
  "count": 1
}
```

---

### 🔔 Alert Endpoints

#### 21. List Alerts

```http
GET /alerts?limit=100&severity=high&acknowledged=false
```

**Response:**
```json
{
  "alerts": [
    {
      "id": 1,
      "timestamp": "2025-01-15T10:30:00Z",
      "alert_type": "sql_injection",
      "severity": "high",
      "title": "SQL injection attempt detected",
      "acknowledged": false
    }
  ],
  "count": 1
}
```

#### 22. Acknowledge Alert

```http
POST /alerts/{alert_id}/acknowledge?acknowledged_by=admin@example.com
```

**Response:**
```json
{
  "success": true,
  "alert_id": 1,
  "acknowledged_by": "admin@example.com"
}
```

---

### 📊 Dashboard & Analytics Endpoints

#### 23. Get Dashboard Stats

```http
GET /dashboard/stats
```

**Response:**
```json
{
  "threats_detected_24h": 127,
  "incidents_24h": 5,
  "open_vulnerabilities": 12,
  "unacknowledged_alerts": 3,
  "timestamp": "2025-01-15T10:30:00Z"
}
```

#### 24. Get Threat Trends

```http
GET /dashboard/threat-trends?days=7
```

**Response:**
```json
{
  "period_days": 7,
  "trends": {
    "2025-01-09": 45,
    "2025-01-10": 52,
    "2025-01-11": 38,
    "2025-01-12": 67,
    "2025-01-13": 41,
    "2025-01-14": 55,
    "2025-01-15": 127
  }
}
```

---

### ⚙️ Configuration Endpoints

#### 25. Get Configuration

```http
GET /config
```

**Response:**
```json
{
  "threat_detection": {
    "enabled": true,
    "detection_interval": 1,
    "alert_threshold": 0.7,
    "auto_block": true,
    "auto_response": true
  },
  "anomaly_detection": {
    "enabled": true,
    "sensitivity": 0.7,
    "learning_period_days": 7
  },
  "incident_response": {
    "auto_response_enabled": true,
    "auto_containment": true,
    "auto_remediation": false
  }
}
```

#### 26. Update Configuration

```http
PUT /config
```

**Request Body:**
```json
{
  "threat_detection": {
    "alert_threshold": 0.8
  },
  "anomaly_detection": {
    "sensitivity": 0.6
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Configuration updated",
  "config": {...}
}
```

---

### 🏥 Health & Status Endpoints

#### 27. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "itechsmart-shield",
  "version": "1.0.0",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

#### 28. Get Detailed Status

```http
GET /status
```

**Response:**
```json
{
  "service": "itechsmart-shield",
  "status": "operational",
  "version": "1.0.0",
  "uptime_hours": 720,
  "threat_detection": "active",
  "anomaly_detection": "active",
  "incident_response": "active",
  "vulnerability_scanning": "active",
  "compliance_monitoring": "active",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## 🔄 Integration Endpoints

### For Enterprise Hub Integration

#### Service Info

```http
GET /api/service-info
```

**Response:**
```json
{
  "name": "iTechSmart Shield",
  "version": "1.0.0",
  "type": "cybersecurity-platform",
  "capabilities": [
    "threat-detection",
    "vulnerability-scanning",
    "compliance-management"
  ],
  "api_key": "shield-service-key"
}
```

#### Ninja Control

```http
POST /api/ninja-control
```

**Request Body:**
```json
{
  "command": "fix",
  "parameters": {
    "issue_type": "security_vulnerability",
    "vulnerability_id": 123
  }
}
```

**Response:**
```json
{
  "success": true,
  "action": "patched_vulnerability",
  "vulnerability_id": 123,
  "patch_applied": true
}
```

#### Event Handler

```http
POST /api/events
```

**Request Body:**
```json
{
  "event_type": "user.login",
  "event_data": {
    "user_id": "user123",
    "source_ip": "192.168.1.100"
  },
  "source_service": "itechsmart-passport"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Event processed"
}
```

---

## 📊 Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

---

## 🔒 Security

### Rate Limiting

```
100 requests per minute per IP
1000 requests per hour per API key
```

### Authentication

```bash
# API Key
X-API-Key: your-api-key

# JWT Token
Authorization: Bearer eyJhbGc...
```

---

## 📈 Best Practices

### 1. Error Handling

Always check response status:

```python
response = requests.post(url, json=data)
if response.status_code == 200:
    result = response.json()
else:
    print(f"Error: {response.status_code}")
```

### 2. Pagination

Use limit and offset for large datasets:

```http
GET /threats?limit=100&offset=0
```

### 3. Filtering

Use query parameters for filtering:

```http
GET /threats?severity=high&status=detected&limit=50
```

### 4. Async Operations

Long-running operations return immediately:

```json
{
  "message": "Scan started",
  "status": "in_progress",
  "scan_id": "SCAN-123"
}
```

Check status later:

```http
GET /scans/{scan_id}/status
```

---

## 🎯 Common Use Cases

### Use Case 1: Monitor Web Traffic

```python
import requests

# Analyze each request
def analyze_request(request_data):
    response = requests.post(
        "http://localhost:8007/api/shield/threats/analyze",
        json=request_data
    )
    
    result = response.json()
    
    if result["blocked"]:
        # Block the request
        return {"status": 403, "message": "Blocked by Shield"}
    
    return {"status": 200, "message": "Allowed"}
```

### Use Case 2: Automated Vulnerability Scanning

```python
import requests
import schedule

def daily_scan():
    # Scan all systems
    targets = ["192.168.1.50", "192.168.1.51", "192.168.1.52"]
    
    for target in targets:
        requests.post(
            "http://localhost:8007/api/shield/vulnerabilities/scan",
            json={"target": target, "scan_type": "comprehensive"}
        )

# Schedule daily scans
schedule.every().day.at("02:00").do(daily_scan)
```

### Use Case 3: Compliance Monitoring

```python
import requests

def check_compliance():
    frameworks = ["SOC2", "ISO27001", "GDPR", "HIPAA"]
    
    for framework in frameworks:
        response = requests.post(
            "http://localhost:8007/api/shield/compliance/assess",
            json={"framework": framework}
        )
        
        result = response.json()
        
        if result["compliance_score"] < 90:
            # Alert on low compliance
            print(f"⚠️ {framework} compliance low: {result['compliance_score']}")
```

---

## 🎉 Conclusion

The iTechSmart Shield API provides comprehensive security capabilities through a simple, RESTful interface.

**28+ endpoints covering:**
- ✅ Threat detection
- ✅ Anomaly detection
- ✅ Incident response
- ✅ Vulnerability scanning
- ✅ Compliance management
- ✅ Security analytics

**Start protecting your infrastructure today!** 🛡️