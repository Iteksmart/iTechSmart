# iTechSmart Supreme - Complete User Manual

**Version 1.0.0** | **Last Updated: January 2025**

---

## 📖 Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started](#2-getting-started)
3. [Dashboard Guide](#3-dashboard-guide)
4. [Monitoring Configuration](#4-monitoring-configuration)
5. [Alert Management](#5-alert-management)
6. [Remediation Actions](#6-remediation-actions)
7. [Workflow Management](#7-workflow-management)
8. [Notification Setup](#8-notification-setup)
9. [Security & Credentials](#9-security--credentials)
10. [API Usage](#10-api-usage)
11. [Troubleshooting](#11-troubleshooting)
12. [Best Practices](#12-best-practices)
13. [Advanced Features](#13-advanced-features)
14. [FAQ](#14-faq)

---

## 1. Introduction

### 1.1 What is iTechSmart Supreme?

iTechSmart Supreme is an **autonomous IT infrastructure healing platform** that:
- **Detects** issues in real-time across your infrastructure
- **Diagnoses** root causes using AI-powered analysis
- **Resolves** problems automatically with secure command execution
- **Notifies** your team through multiple channels
- **Logs** everything for compliance and audit

### 1.2 Key Benefits

✅ **Reduce Downtime** - Resolve issues in seconds, not hours  
✅ **Save Time** - Automate repetitive troubleshooting tasks  
✅ **Improve Security** - Rapid response to security threats  
✅ **Ensure Compliance** - Complete audit trail of all actions  
✅ **Scale Operations** - Manage thousands of servers effortlessly  

### 1.3 Who Should Use This Manual?

- **IT Operations Teams** - Day-to-day monitoring and management
- **System Administrators** - Configuration and deployment
- **DevOps Engineers** - Integration and automation
- **Security Teams** - Security monitoring and incident response
- **IT Managers** - Oversight and reporting

---

## 2. Getting Started

### 2.1 System Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB
- Disk: 20GB
- OS: Linux (Ubuntu 20.04+, CentOS 8+, Debian 11+)

**Recommended for Production:**
- CPU: 4+ cores
- RAM: 8GB+
- Disk: 50GB+ SSD
- Network: 1Gbps

### 2.2 Installation Methods

#### Option A: Docker (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/itechsmart-supreme.git
cd itechsmart-supreme

# 2. Configure environment
cp .env.example .env
nano .env

# 3. Start application
docker-compose up -d

# 4. Verify installation
docker-compose ps
docker-compose logs -f
```

#### Option B: Manual Installation

```bash
# 1. Install Python 3.11+
sudo apt update
sudo apt install python3.11 python3-pip

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
nano .env

# 4. Run application
python main.py
```

### 2.3 First-Time Setup

1. **Access Dashboard**: Open `http://localhost:5000` in your browser
2. **Set Master Password**: Create a strong master password for credential encryption
3. **Add First Host**: Add your first monitored server
4. **Configure Monitoring**: Connect to Prometheus/Wazuh
5. **Test Alert**: Trigger a test alert to verify setup

### 2.4 Quick Verification

```bash
# Check health
curl http://localhost:5000/api/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600
}
```

---

## 3. Dashboard Guide

### 3.1 Dashboard Overview

The iTechSmart Supreme dashboard provides real-time visibility into your infrastructure:

**Main Sections:**
1. **System Status** - Overall health indicator
2. **Active Alerts** - Current issues requiring attention
3. **Recent Actions** - Latest remediation actions
4. **Pending Approvals** - Actions awaiting approval
5. **Audit Log** - Complete action history

### 3.2 Dashboard Features

#### Real-Time Updates
- **WebSocket Connection** - Live updates without page refresh
- **Auto-Refresh** - Configurable refresh intervals
- **Status Indicators** - Color-coded health status

#### Alert Cards
Each alert displays:
- **Severity** - Critical, High, Medium, Low
- **Source** - Prometheus, Wazuh, GitHub, etc.
- **Host** - Affected server/service
- **Message** - Alert description
- **Timestamp** - When detected
- **Actions** - Available remediation options

#### Action Buttons
- **Approve** - Approve pending action
- **Reject** - Reject proposed action
- **View Details** - See full alert information
- **Manual Action** - Execute custom command

### 3.3 Navigation

**Top Menu:**
- **Dashboard** - Main overview
- **Alerts** - Alert management
- **Actions** - Action history
- **Hosts** - Managed servers
- **Settings** - Configuration
- **Logs** - Audit logs

**Quick Actions:**
- **Kill Switch** - Emergency stop button
- **Refresh** - Manual refresh
- **Filter** - Filter by severity/source
- **Search** - Search alerts/actions

### 3.4 Status Indicators

| Color | Status | Meaning |
|-------|--------|---------|
| 🟢 Green | Healthy | All systems operational |
| 🟡 Yellow | Warning | Minor issues detected |
| 🟠 Orange | Degraded | Performance issues |
| 🔴 Red | Critical | Immediate attention required |
| ⚫ Gray | Unknown | No data available |

---

## 4. Monitoring Configuration

### 4.1 Prometheus Integration

#### Setup Steps

1. **Configure Prometheus Endpoint**
```bash
# In .env file
PROMETHEUS_ENDPOINTS=http://prometheus:9090
```

2. **Add Prometheus Alerts**
```yaml
# prometheus.yml
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['itechsmart:5000']
```

3. **Configure Alert Rules**
```yaml
# alert_rules.yml
groups:
  - name: itechsmart
    rules:
      - alert: HighCPU
        expr: cpu_usage > 80
        for: 5m
        annotations:
          summary: "High CPU on {{ $labels.instance }}"
```

#### Monitored Metrics

- **CPU Usage** - Processor utilization
- **Memory Usage** - RAM consumption
- **Disk Usage** - Storage capacity
- **Network Traffic** - Bandwidth utilization
- **Service Status** - Application health

### 4.2 Wazuh Integration

#### Setup Steps

1. **Configure Wazuh Endpoint**
```bash
# In .env file
WAZUH_ENDPOINTS=https://wazuh:55000
WAZUH_USERNAME=admin
WAZUH_PASSWORD=your-password
```

2. **Enable Wazuh Alerts**
```xml
<!-- ossec.conf -->
<integration>
  <name>custom-webhook</name>
  <hook_url>http://itechsmart:5000/webhook/wazuh</hook_url>
  <level>7</level>
  <alert_format>json</alert_format>
</integration>
```

#### Monitored Events

- **Authentication Failures** - Brute force detection
- **File Integrity** - Unauthorized file changes
- **Rootkit Detection** - Malware scanning
- **Vulnerability Detection** - Security patches
- **Log Analysis** - Suspicious patterns

### 4.3 GitHub Integration

#### Setup Steps

1. **Create Webhook**
   - Go to GitHub repository → Settings → Webhooks
   - Add webhook URL: `http://your-server:5000/webhook/github`
   - Select events: Workflow runs, Issues, Pull requests

2. **Configure Secret**
```bash
# In .env file
GITHUB_WEBHOOK_SECRET=your-secret-key
```

#### Monitored Events

- **Workflow Failures** - CI/CD pipeline issues
- **Deployment Failures** - Failed deployments
- **Security Alerts** - Dependabot alerts
- **Infrastructure Changes** - Terraform/IaC changes

### 4.4 Custom Monitoring

#### Add Custom Webhook

```bash
# Send custom alert
curl -X POST http://localhost:5000/webhook/custom \
  -H "Content-Type: application/json" \
  -d '{
    "severity": "high",
    "host": "web-server-01",
    "message": "Custom alert message",
    "source": "custom-monitor"
  }'
```

---

## 5. Alert Management

### 5.1 Understanding Alerts

#### Alert Lifecycle

1. **Detection** - Issue detected by monitoring system
2. **Reception** - Alert received by iTechSmart
3. **Diagnosis** - AI analyzes root cause
4. **Action Planning** - Remediation action proposed
5. **Approval** - Manual approval (if required)
6. **Execution** - Action executed
7. **Verification** - Success verified
8. **Notification** - Team notified
9. **Logging** - Audit log created

#### Alert Severity Levels

**Critical** 🔴
- Immediate action required
- Service outages
- Security breaches
- Data loss risk

**High** 🟠
- Urgent attention needed
- Performance degradation
- Failed backups
- Authentication issues

**Medium** 🟡
- Should be addressed soon
- Resource warnings
- Configuration issues
- Minor errors

**Low** 🟢
- Informational
- Routine events
- Successful actions
- Status updates

### 5.2 Alert Actions

#### View Alert Details

1. Click on alert card in dashboard
2. Review full alert information:
   - Source system
   - Affected host
   - Diagnostic analysis
   - Recommended actions
   - Historical context

#### Approve Action

```bash
# Via API
curl -X POST http://localhost:5000/api/actions/{action_id}/approve \
  -H "Authorization: Bearer YOUR_TOKEN"

# Via Dashboard
Click "Approve" button on action card
```

#### Reject Action

```bash
# Via API
curl -X POST http://localhost:5000/api/actions/{action_id}/reject \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"reason": "Not appropriate at this time"}'

# Via Dashboard
Click "Reject" button and provide reason
```

#### Manual Intervention

If automatic remediation isn't appropriate:

1. Click "Manual Action" on alert
2. Review diagnostic information
3. Execute commands manually via SSH/RDP
4. Mark alert as resolved
5. Document actions taken

### 5.3 Alert Filtering

#### Filter by Severity

```bash
# Dashboard filter
Select severity: Critical, High, Medium, Low

# API filter
GET /api/alerts?severity=critical
```

#### Filter by Source

```bash
# Dashboard filter
Select source: Prometheus, Wazuh, GitHub

# API filter
GET /api/alerts?source=prometheus
```

#### Filter by Time

```bash
# Last 24 hours
GET /api/alerts?since=24h

# Last 7 days
GET /api/alerts?since=7d

# Custom range
GET /api/alerts?start=2025-01-01&end=2025-01-31
```

### 5.4 Alert Notifications

Configure where alerts are sent:

```bash
# In .env file
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
PAGERDUTY_API_KEY=your-key
EMAIL_RECIPIENTS=admin@company.com,ops@company.com
```

See [Section 8: Notification Setup](#8-notification-setup) for details.

---

## 6. Remediation Actions

### 6.1 Action Types

#### Command Execution
Execute shell commands on remote systems:

```python
# SSH (Linux/Unix)
action = {
    "type": "ssh",
    "host": "web-server-01",
    "command": "systemctl restart nginx"
}

# WinRM (Windows)
action = {
    "type": "winrm",
    "host": "win-server-01",
    "command": "Restart-Service IIS"
}

# Telnet (Network Devices)
action = {
    "type": "telnet",
    "host": "switch-01",
    "command": "reload"
}
```

#### Service Management
Restart, stop, or start services:

```bash
# Restart service
systemctl restart nginx

# Stop service
systemctl stop apache2

# Start service
systemctl start postgresql
```

#### Process Management
Kill problematic processes:

```bash
# Kill by PID
kill -9 12345

# Kill by name
pkill -9 java

# Kill all instances
killall -9 chrome
```

#### File Operations
Clean up disk space:

```bash
# Remove old logs
find /var/log -name "*.log" -mtime +30 -delete

# Clean temp files
rm -rf /tmp/*

# Rotate logs
logrotate -f /etc/logrotate.conf
```

### 6.2 Action Safety

#### Risk Levels

**Low Risk** 🟢
- Read-only operations
- Status checks
- Log viewing
- No approval required

**Medium Risk** 🟡
- Service restarts
- Log rotation
- Configuration changes
- Approval recommended

**High Risk** 🔴
- Process termination
- File deletion
- Network changes
- Approval required

**Critical Risk** ⚫
- System reboots
- Data deletion
- Security changes
- Multiple approvals required

#### Safety Checks

iTechSmart validates all commands:

```python
# Dangerous patterns blocked
DANGEROUS_PATTERNS = [
    r'rm\s+-rf\s+/',      # Delete root
    r'dd\s+if=',          # Disk operations
    r'mkfs\.',            # Format disk
    r'shutdown',          # System shutdown
    r'reboot',            # System reboot
]
```

### 6.3 Approval Workflows

#### Automatic Approval

For low-risk actions:

```bash
# In .env file
AUTO_REMEDIATION=true
AUTO_APPROVE_LOW_RISK=true
```

#### Manual Approval

For high-risk actions:

1. Action proposed
2. Notification sent to approvers
3. Approver reviews action
4. Approver approves/rejects
5. Action executed (if approved)

#### Multi-Level Approval

For critical actions:

```python
approval_config = {
    "required_approvals": 2,
    "approvers": ["admin", "senior-ops"],
    "timeout": 600  # 10 minutes
}
```

### 6.4 Action Execution

#### Execution Flow

1. **Validation** - Command safety check
2. **Credential Retrieval** - Get encrypted credentials
3. **Connection** - Establish secure connection
4. **Execution** - Run command
5. **Output Capture** - Capture stdout/stderr
6. **Verification** - Verify success
7. **Logging** - Log to audit trail
8. **Notification** - Notify team

#### Execution Results

```json
{
  "success": true,
  "exit_code": 0,
  "stdout": "Service restarted successfully",
  "stderr": "",
  "duration": 2.5,
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### 6.5 Rollback Procedures

If action fails:

1. **Automatic Rollback** - Restore previous state
2. **Notification** - Alert team of failure
3. **Manual Intervention** - Provide rollback instructions
4. **Incident Creation** - Create incident ticket

---

## 7. Workflow Management

### 7.1 Built-in Workflows

iTechSmart includes 5 pre-built workflows:

#### Workflow #1: High CPU Remediation
**Trigger:** CPU > 80%  
**Steps:**
1. Identify top CPU processes
2. Notify team
3. Wait for approval
4. Kill process (if approved)
5. Verify CPU normalized
6. Log incident

#### Workflow #2: Service Restart
**Trigger:** Service down  
**Steps:**
1. Check service status
2. Backup configuration
3. Stop service
4. Wait 5 seconds
5. Start service
6. Verify service running
7. Notify success

#### Workflow #3: Security Incident
**Trigger:** Critical Wazuh alert  
**Steps:**
1. Isolate host
2. Collect evidence
3. Notify security team
4. Create P1 ticket
5. Wait for investigation

#### Workflow #4: Disk Space Cleanup
**Trigger:** Disk > 85%  
**Steps:**
1. Analyze disk usage
2. Clean temp files
3. Rotate logs
4. Verify space freed
5. Notify team

#### Workflow #5: Database Optimization
**Trigger:** Query time > 5s  
**Steps:**
1. Identify slow queries
2. Check connection pool
3. Analyze table statistics
4. Notify DBA team
5. Wait for approval
6. Run VACUUM ANALYZE
7. Verify performance
8. Create report

### 7.2 Creating Custom Workflows

#### YAML Definition

```yaml
name: Custom Workflow
description: My custom automation workflow
trigger:
  type: alert
  condition: metric_name > threshold

steps:
  - name: Step 1
    action_type: command
    parameters:
      command: "echo 'Starting workflow'"
    
  - name: Step 2
    action_type: notification
    parameters:
      channels: ['slack']
      message: "Workflow started"
    
  - name: Step 3
    action_type: approval
    parameters:
      timeout: 300
      approvers: ['admin']
```

#### Python API

```python
from itechsmart_supreme.features.workflow_engine import WorkflowEngine

engine = WorkflowEngine()

# Create workflow
workflow = engine.create_workflow(
    name="My Workflow",
    description="Custom workflow",
    trigger={"type": "alert"},
    steps=[
        {
            "name": "Check Status",
            "action_type": "command",
            "parameters": {"command": "uptime"}
        }
    ]
)

# Execute workflow
result = await engine.execute_workflow(
    workflow_id=workflow.id,
    context={"host": "server-01"}
)
```

### 7.3 Workflow Templates

Use templates for common scenarios:

```python
# Create from template
workflow = engine.create_workflow_from_template(
    template_name='high_cpu_remediation',
    parameters={
        'cpu_threshold': 90,
        'approval_timeout': 600
    }
)
```

### 7.4 Workflow Monitoring

Track workflow execution:

```bash
# List running workflows
GET /api/workflows/running

# Get workflow status
GET /api/workflows/{workflow_id}/status

# View workflow history
GET /api/workflows/history
```

---

## 8. Notification Setup

### 8.1 Supported Channels

iTechSmart supports 7 notification channels:

1. **Slack** - Team collaboration
2. **Email** - Documentation and audit
3. **PagerDuty** - On-call escalation
4. **Microsoft Teams** - Enterprise teams
5. **Telegram** - Mobile notifications
6. **SMS** - Emergency alerts
7. **Webhooks** - Custom integrations

### 8.2 Slack Configuration

```bash
# 1. Create Slack webhook
# Go to: https://api.slack.com/messaging/webhooks

# 2. Configure in .env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# 3. Test notification
curl -X POST $SLACK_WEBHOOK_URL \
  -d '{"text":"Test from iTechSmart"}'
```

**Features:**
- Rich message formatting
- Thread support
- Emoji indicators
- Instant delivery

### 8.3 Email Configuration

```bash
# Configure SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=alerts@itechsmart.dev
EMAIL_RECIPIENTS=admin@company.com,ops@company.com
```

**Gmail Setup:**
1. Enable 2-factor authentication
2. Generate app password
3. Use app password in configuration

### 8.4 PagerDuty Configuration

```bash
# 1. Create PagerDuty integration
# Go to: Services → Your Service → Integrations

# 2. Configure in .env
PAGERDUTY_API_KEY=your-integration-key
PAGERDUTY_SERVICE_ID=your-service-id

# 3. Test incident
curl -X POST https://events.pagerduty.com/v2/enqueue \
  -d '{
    "routing_key": "YOUR_KEY",
    "event_action": "trigger",
    "payload": {
      "summary": "Test from iTechSmart",
      "severity": "error",
      "source": "itechsmart"
    }
  }'
```

### 8.5 Microsoft Teams Configuration

```bash
# 1. Create Teams webhook
# Go to: Channel → Connectors → Incoming Webhook

# 2. Configure in .env
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/YOUR/WEBHOOK/URL

# 3. Test message
curl -X POST $TEAMS_WEBHOOK_URL \
  -d '{
    "@type": "MessageCard",
    "title": "Test from iTechSmart",
    "text": "This is a test message"
  }'
```

### 8.6 Telegram Configuration

```bash
# 1. Create Telegram bot
# Talk to @BotFather on Telegram

# 2. Get chat ID
# Send message to bot, then:
curl https://api.telegram.org/bot<TOKEN>/getUpdates

# 3. Configure in .env
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

### 8.7 Notification Routing

Configure smart routing by severity:

```python
notification_rules = {
    "critical": ["pagerduty", "slack", "sms"],
    "high": ["slack", "email", "teams"],
    "medium": ["slack", "email"],
    "low": ["email"]
}
```

---

## 9. Security & Credentials

### 9.1 Credential Management

#### Adding Credentials

```bash
# Via API
curl -X POST http://localhost:5000/api/credentials \
  -H "Content-Type: application/json" \
  -d '{
    "host": "web-server-01",
    "username": "admin",
    "password": "secure-password",
    "protocol": "ssh"
  }'

# Via Dashboard
1. Go to Settings → Credentials
2. Click "Add Credential"
3. Fill in details
4. Click "Save"
```

#### Credential Storage

All credentials are:
- **Encrypted** using Fernet encryption
- **Salted** with PBKDF2 key derivation
- **Protected** by master password
- **Stored** in encrypted database

#### Credential Retrieval

```python
from itechsmart_supreme.security.credential_manager import CredentialManager

manager = CredentialManager(master_password)

# Get credentials
creds = manager.get_credentials(
    host="web-server-01",
    protocol="ssh"
)
```

### 9.2 Authentication

#### API Authentication

```bash
# Get token
curl -X POST http://localhost:5000/api/auth/login \
  -d '{"username":"admin","password":"password"}'

# Use token
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5000/api/alerts
```

#### Session Management

- **Session Timeout:** 30 minutes
- **Token Expiry:** 24 hours
- **Refresh Tokens:** Supported
- **Multi-Factor:** Optional

### 9.3 Zero Trust Security

iTechSmart implements zero trust principles:

**Never Trust, Always Verify:**
- Continuous authentication
- Risk-based access control
- Least privilege access
- Complete audit logging

**Trust Levels:**
- **VERIFIED** - Full access
- **HIGH** - Most operations
- **MEDIUM** - Limited operations
- **LOW** - Read-only
- **UNTRUSTED** - No access

### 9.4 Audit Logging

All actions are logged:

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "user": "admin",
  "action": "execute_command",
  "host": "web-server-01",
  "command": "systemctl restart nginx",
  "result": "success",
  "ip_address": "192.168.1.100"
}
```

View audit logs:

```bash
# Via API
GET /api/audit/logs

# Via Dashboard
Navigate to Logs → Audit Trail
```

### 9.5 Kill Switch

Emergency stop for all automation:

```bash
# Enable kill switch
curl -X POST http://localhost:5000/api/killswitch/enable

# Disable kill switch
curl -X POST http://localhost:5000/api/killswitch/disable

# Check status
curl http://localhost:5000/api/killswitch/status
```

When enabled:
- ❌ No automatic actions
- ❌ No command execution
- ✅ Monitoring continues
- ✅ Alerts still received
- ✅ Manual actions allowed

---

## 10. API Usage

### 10.1 API Overview

iTechSmart provides a RESTful API for all operations.

**Base URL:** `http://localhost:5000/api`

**Authentication:** Bearer token

**Content-Type:** `application/json`

### 10.2 Core Endpoints

#### Health Check

```bash
GET /api/health

Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600
}
```

#### System Status

```bash
GET /api/status

Response:
{
  "monitoring": {
    "prometheus": "connected",
    "wazuh": "connected"
  },
  "active_alerts": 5,
  "pending_actions": 2,
  "kill_switch": false
}
```

### 10.3 Alert Endpoints

#### List Alerts

```bash
GET /api/alerts?severity=critical&limit=10

Response:
{
  "alerts": [
    {
      "id": "alert-123",
      "severity": "critical",
      "host": "web-server-01",
      "message": "High CPU usage",
      "timestamp": "2025-01-15T10:30:00Z"
    }
  ],
  "total": 5,
  "page": 1
}
```

#### Get Alert Details

```bash
GET /api/alerts/{alert_id}

Response:
{
  "id": "alert-123",
  "severity": "critical",
  "host": "web-server-01",
  "message": "High CPU usage",
  "diagnosis": {
    "root_cause": "Runaway process",
    "confidence": 0.95
  },
  "recommended_actions": [...]
}
```

### 10.4 Action Endpoints

#### List Actions

```bash
GET /api/actions?status=pending

Response:
{
  "actions": [
    {
      "id": "action-456",
      "description": "Kill process 12345",
      "risk_level": "high",
      "status": "pending_approval"
    }
  ]
}
```

#### Approve Action

```bash
POST /api/actions/{action_id}/approve

Response:
{
  "success": true,
  "action_id": "action-456",
  "status": "approved",
  "execution_scheduled": true
}
```

#### Reject Action

```bash
POST /api/actions/{action_id}/reject
Content-Type: application/json

{
  "reason": "Not appropriate at this time"
}

Response:
{
  "success": true,
  "action_id": "action-456",
  "status": "rejected"
}
```

### 10.5 Workflow Endpoints

#### List Workflows

```bash
GET /api/workflows

Response:
{
  "workflows": [
    {
      "id": "workflow-789",
      "name": "High CPU Remediation",
      "status": "running",
      "current_step": 3
    }
  ]
}
```

#### Execute Workflow

```bash
POST /api/workflows/{workflow_id}/execute
Content-Type: application/json

{
  "context": {
    "host": "web-server-01"
  }
}

Response:
{
  "success": true,
  "workflow_id": "workflow-789",
  "execution_id": "exec-123"
}
```

### 10.6 Webhook Endpoints

#### Prometheus Webhook

```bash
POST /webhook/prometheus
Content-Type: application/json

{
  "alerts": [
    {
      "status": "firing",
      "labels": {
        "alertname": "HighCPU",
        "instance": "web-server-01"
      },
      "annotations": {
        "summary": "High CPU usage detected"
      }
    }
  ]
}
```

#### Wazuh Webhook

```bash
POST /webhook/wazuh
Content-Type: application/json

{
  "rule": {
    "level": 10,
    "description": "Authentication failure"
  },
  "agent": {
    "name": "web-server-01"
  }
}
```

---

## 11. Troubleshooting

### 11.1 Common Issues

#### Dashboard Not Loading

**Symptoms:**
- Blank page
- Connection refused
- 502 Bad Gateway

**Solutions:**
```bash
# Check if service is running
docker-compose ps

# Check logs
docker-compose logs -f itechsmart-supreme

# Restart service
docker-compose restart itechsmart-supreme

# Check port availability
netstat -tulpn | grep 5000
```

#### Alerts Not Appearing

**Symptoms:**
- No alerts in dashboard
- Monitoring connected but no data

**Solutions:**
```bash
# Verify monitoring endpoints
curl http://prometheus:9090/api/v1/query?query=up

# Check webhook configuration
curl -X POST http://localhost:5000/webhook/test

# Review logs
tail -f itechsmart_supreme.log | grep "alert"

# Test alert manually
curl -X POST http://localhost:5000/webhook/custom \
  -d '{"severity":"high","message":"Test alert"}'
```

#### Actions Not Executing

**Symptoms:**
- Actions stuck in pending
- Execution failures
- Timeout errors

**Solutions:**
```bash
# Check credentials
curl http://localhost:5000/api/credentials/test

# Verify SSH connectivity
ssh user@target-host

# Check action logs
GET /api/actions/{action_id}/logs

# Review execution history
GET /api/actions/history?status=failed
```

#### Notifications Not Sending

**Symptoms:**
- No Slack messages
- Emails not received
- PagerDuty not triggered

**Solutions:**
```bash
# Test Slack webhook
curl -X POST $SLACK_WEBHOOK_URL \
  -d '{"text":"Test"}'

# Test email configuration
python -c "from itechsmart_supreme.features.notification_manager import NotificationManager; NotificationManager(config).test_email()"

# Check notification logs
grep "notification" itechsmart_supreme.log

# Verify channel configuration
GET /api/notifications/channels
```

### 11.2 Performance Issues

#### High CPU Usage

```bash
# Check process usage
top -p $(pgrep -f itechsmart)

# Review monitoring frequency
# Reduce polling intervals in .env
PROMETHEUS_POLL_INTERVAL=60
WAZUH_POLL_INTERVAL=60
```

#### High Memory Usage

```bash
# Check memory usage
docker stats itechsmart-supreme

# Clear cache
curl -X POST http://localhost:5000/api/cache/clear

# Adjust memory limits
# In docker-compose.yml
mem_limit: 2g
```

#### Slow Response Times

```bash
# Enable debug mode
export FLASK_DEBUG=1

# Check database performance
sqlite3 itechsmart.db "ANALYZE;"

# Review slow queries
GET /api/debug/slow-queries
```

### 11.3 Connection Issues

#### SSH Connection Failures

```bash
# Test SSH manually
ssh -v user@host

# Check SSH key permissions
chmod 600 ~/.ssh/id_rsa

# Verify known_hosts
ssh-keyscan host >> ~/.ssh/known_hosts

# Check firewall rules
sudo iptables -L | grep 22
```

#### WinRM Connection Failures

```bash
# Test WinRM
winrs -r:http://host:5985 -u:user -p:pass ipconfig

# Enable WinRM on Windows
Enable-PSRemoting -Force

# Check WinRM configuration
winrm get winrm/config
```

### 11.4 Debug Mode

Enable detailed logging:

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Or in .env file
LOG_LEVEL=DEBUG

# View debug logs
tail -f itechsmart_supreme.log | grep DEBUG
```

### 11.5 Getting Help

**Documentation:**
- README.md - Complete feature guide
- DEPLOYMENT_GUIDE.md - Deployment instructions
- This manual - User guide

**Logs:**
- Application logs: `itechsmart_supreme.log`
- Docker logs: `docker-compose logs`
- System logs: `/var/log/syslog`

**Support:**
- GitHub Issues: Report bugs
- Documentation: Comprehensive guides
- Community: User forums

---

## 12. Best Practices

### 12.1 Security Best Practices

1. **Use Strong Master Password**
   - Minimum 16 characters
   - Mix of letters, numbers, symbols
   - Store securely (password manager)

2. **Enable Multi-Factor Authentication**
   ```bash
   MFA_ENABLED=true
   MFA_METHOD=totp
   ```

3. **Rotate Credentials Regularly**
   - Change passwords every 90 days
   - Update API keys quarterly
   - Review access logs monthly

4. **Limit Auto-Remediation**
   ```bash
   AUTO_REMEDIATION=false
   AUTO_APPROVE_LOW_RISK=true
   AUTO_APPROVE_HIGH_RISK=false
   ```

5. **Enable Audit Logging**
   ```bash
   AUDIT_LOGGING=true
   AUDIT_LOG_RETENTION=365
   ```

### 12.2 Operational Best Practices

1. **Start with Monitoring Only**
   - Disable auto-remediation initially
   - Observe alerts for 1-2 weeks
   - Gradually enable automation

2. **Test in Non-Production First**
   - Deploy to dev/staging environment
   - Run demo scenarios
   - Verify all integrations

3. **Configure Approval Workflows**
   - Require approval for high-risk actions
   - Set appropriate timeouts
   - Define clear approver roles

4. **Set Up Notifications**
   - Configure multiple channels
   - Test all notification methods
   - Set up escalation policies

5. **Regular Maintenance**
   - Review audit logs weekly
   - Update credentials monthly
   - Check system health daily

### 12.3 Performance Best Practices

1. **Optimize Polling Intervals**
   ```bash
   PROMETHEUS_POLL_INTERVAL=60  # 1 minute
   WAZUH_POLL_INTERVAL=60       # 1 minute
   ```

2. **Limit Alert History**
   ```bash
   ALERT_RETENTION_DAYS=30
   ACTION_RETENTION_DAYS=90
   ```

3. **Use Database Indexing**
   ```sql
   CREATE INDEX idx_alerts_timestamp ON alerts(timestamp);
   CREATE INDEX idx_actions_status ON actions(status);
   ```

4. **Enable Caching**
   ```bash
   CACHE_ENABLED=true
   CACHE_TTL=300  # 5 minutes
   ```

### 12.4 Monitoring Best Practices

1. **Monitor iTechSmart Itself**
   - Set up health checks
   - Monitor resource usage
   - Alert on failures

2. **Regular Testing**
   - Test workflows monthly
   - Verify integrations weekly
   - Run demo scenarios quarterly

3. **Documentation**
   - Document custom workflows
   - Maintain runbooks
   - Update procedures regularly

---

## 13. Advanced Features

### 13.1 Multi-AI Provider Support

iTechSmart supports multiple AI providers:

```bash
# Configure AI providers
AI_PROVIDERS=openai,gemini,claude,ollama
AI_FALLBACK_CHAIN=openai,gemini,claude,ollama

# OpenAI
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4

# Google Gemini
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini-pro

# Anthropic Claude
ANTHROPIC_API_KEY=your-key
ANTHROPIC_MODEL=claude-3-opus

# Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### 13.2 Custom Integrations

#### Create Custom Monitor

```python
from itechsmart_supreme.monitoring.base_monitor import BaseMonitor

class CustomMonitor(BaseMonitor):
    def __init__(self, config):
        super().__init__(config)
        
    async def collect_metrics(self):
        # Your custom logic
        metrics = await self.fetch_data()
        return self.process_metrics(metrics)
```

#### Create Custom Action

```python
from itechsmart_supreme.execution.base_executor import BaseExecutor

class CustomExecutor(BaseExecutor):
    async def execute(self, action):
        # Your custom execution logic
        result = await self.run_custom_action(action)
        return result
```

### 13.3 Integration with External Tools

#### Ansible Integration

```python
from itechsmart_supreme.integrations.ansible_integration import AnsibleIntegration

ansible = AnsibleIntegration(config)

# Run playbook
result = await ansible.run_playbook(
    playbook_path="site.yml",
    inventory="hosts",
    extra_vars={"target": "web-servers"}
)
```

#### SaltStack Integration

```python
from itechsmart_supreme.integrations.saltstack_integration import SaltStackIntegration

salt = SaltStackIntegration(config)

# Execute state
result = await salt.execute_state(
    target="web-*",
    state="nginx.restart"
)
```

### 13.4 Advanced Workflows

#### Conditional Branching

```yaml
steps:
  - name: Check Condition
    action_type: check
    parameters:
      metric: cpu_usage
      condition: "> 80"
    on_success: High CPU Path
    on_failure: Normal Path
    
  - name: High CPU Path
    action_type: command
    parameters:
      command: "kill -9 {pid}"
      
  - name: Normal Path
    action_type: notification
    parameters:
      message: "CPU normal"
```

#### Parallel Execution

```yaml
steps:
  - name: Parallel Tasks
    action_type: parallel
    tasks:
      - name: Task 1
        action_type: command
        parameters:
          command: "task1.sh"
      - name: Task 2
        action_type: command
        parameters:
          command: "task2.sh"
```

### 13.5 Custom Dashboards

Create custom Grafana dashboards:

```json
{
  "dashboard": {
    "title": "iTechSmart Metrics",
    "panels": [
      {
        "title": "Alert Rate",
        "targets": [
          {
            "expr": "rate(itechsmart_alerts_total[5m])"
          }
        ]
      }
    ]
  }
}
```

---

## 14. FAQ

### 14.1 General Questions

**Q: What is iTechSmart Supreme?**  
A: An autonomous IT infrastructure healing platform that detects, diagnoses, and resolves issues automatically.

**Q: Is it safe to use in production?**  
A: Yes, with proper configuration. Start with monitoring only, then gradually enable automation with approval workflows.

**Q: What systems does it support?**  
A: Linux, Windows, network devices, cloud platforms, and any system with SSH/WinRM/Telnet access.

**Q: Does it require internet access?**  
A: No, it can run in offline mode using the built-in rule-based diagnosis engine.

### 14.2 Technical Questions

**Q: How does AI diagnosis work?**  
A: It uses multiple AI providers (OpenAI, Gemini, Claude, Ollama) with automatic fallback, or offline rule-based analysis.

**Q: Can I customize workflows?**  
A: Yes, you can create custom workflows using YAML or Python API.

**Q: How are credentials stored?**  
A: All credentials are encrypted using Fernet encryption with PBKDF2 key derivation.

**Q: What happens if iTechSmart fails?**  
A: Monitoring systems continue to operate independently. iTechSmart is designed for high availability with automatic recovery.

### 14.3 Operational Questions

**Q: How long does remediation take?**  
A: Typically 10-30 seconds from detection to resolution, depending on action complexity.

**Q: Can I rollback actions?**  
A: Yes, failed actions trigger automatic rollback procedures.

**Q: How do I handle false positives?**  
A: Use approval workflows, adjust alert thresholds, and create custom filters.

**Q: What's the learning curve?**  
A: Basic usage: 1 day. Advanced features: 1 week. Full mastery: 1 month.

### 14.4 Pricing & Licensing

**Q: What's the license?**  
A: MIT License - free for commercial and personal use.

**Q: Are there any costs?**  
A: Only if using external AI providers (OpenAI, etc.). Offline mode is completely free.

**Q: Can I modify the code?**  
A: Yes, it's open source under MIT license.

---

## 📚 Additional Resources

### Documentation
- **README.md** - Complete feature documentation
- **DEPLOYMENT_GUIDE.md** - Production deployment guide
- **DEMO_SCENARIOS.md** - Interactive demo scenarios
- **INTEGRATIONS_GUIDE.md** - Tool integration guide
- **ENHANCED_FEATURES.md** - Advanced features guide
- **WORKFLOW_TEMPLATES_AND_NOTIFICATIONS.md** - Workflow and notification guide

### Quick References
- **QUICK_START.md** - 5-minute quick start
- **QUICK_REFERENCE_WORKFLOWS_NOTIFICATIONS.md** - Workflow quick reference
- **INDEX.md** - Documentation index

### Configuration
- **.env.example** - Environment configuration template
- **docker-compose.yml** - Docker deployment
- **prometheus.yml** - Prometheus configuration

---

## 📞 Support & Contact

### Getting Help
1. **Documentation** - Check this manual and other guides
2. **Logs** - Review application and system logs
3. **GitHub Issues** - Report bugs and request features
4. **Community** - Join user discussions

### Reporting Issues
When reporting issues, include:
- iTechSmart version
- Operating system
- Error messages
- Steps to reproduce
- Relevant logs

---

**iTechSmart Supreme User Manual v1.0.0**  
**Last Updated: January 2025**  
**© 2025 NinjaTech AI. All rights reserved.**

---

*The End of IT Downtime. Forever.* 🚀