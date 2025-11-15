# Quick Reference: Workflows & Notifications

## 🎯 Quick Access Guide

### Available Workflow Templates

| # | Template Name | Purpose | Trigger |
|---|---------------|---------|---------|
| 1 | High CPU Remediation | Auto-resolve CPU spikes | CPU > 80% |
| 2 | Service Restart | Graceful service restart | Service down |
| 3 | Security Incident | Security threat response | Critical Wazuh alert |
| 4 | Disk Space Cleanup | Free up disk space | Disk > 85% |
| 5 | **Database Optimization** | **DB performance tuning** | **Query time > 5s** |

### Configured Notification Channels

| # | Channel | Status | Use Case |
|---|---------|--------|----------|
| 1 | 💬 Slack | ✅ Ready | Team collaboration |
| 2 | 📧 Email | ✅ Ready | Documentation |
| 3 | 📟 PagerDuty | ✅ Ready | Critical alerts |
| 4 | 👥 Teams | ✅ Ready | Enterprise teams |
| 5 | 🤖 Telegram | ✅ Ready | Mobile alerts |
| 6 | 📱 SMS | ⚠️ Needs setup | Emergency only |
| 7 | 🔗 Webhooks | ✅ Ready | Custom integrations |

---

## 🆕 Template #5: Database Performance Optimization

### Overview
Automatically detects and resolves database performance issues with DBA approval.

### Key Features
- ✅ Identifies slow queries
- ✅ Checks connection pool status
- ✅ Analyzes missing indexes
- ✅ Requires DBA approval
- ✅ Runs VACUUM ANALYZE
- ✅ Verifies performance improvement
- ✅ Creates detailed reports

### Workflow Steps (17 total)
1. Identify slow queries
2. Check connection pool
3. Analyze table statistics
4. Check table bloat
5. Notify DBA team
6. **Wait for approval** (10 min timeout)
7. Run VACUUM ANALYZE (if approved)
8. Update statistics
9. Check index usage
10. Restart connection pool (if needed)
11. Wait for stabilization
12. Verify performance
13. Verify connection pool
14. Create performance report
15. Log to database
16. Notify success
17. Notify failure (if needed)

### When to Use
- Query response time > 5 seconds
- Connection pool > 80% utilized
- Database performance degradation
- After major data imports
- Scheduled maintenance windows

---

## 📢 Notification Channel Details

### 1. Slack - Team Collaboration
**Best for:** Real-time team alerts, collaboration

**Setup:**
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Features:**
- Rich formatting
- Instant delivery (< 1s)
- Thread support
- Emoji indicators

---

### 2. Email - Documentation
**Best for:** Audit trail, detailed reports

**Setup:**
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=alerts@itechsmart.dev
EMAIL_RECIPIENTS=admin@company.com,ops@company.com
```

**Features:**
- HTML formatting
- Multiple recipients
- Attachments
- Searchable history

---

### 3. PagerDuty - Critical Alerts
**Best for:** On-call escalation, critical incidents

**Setup:**
```bash
PAGERDUTY_API_KEY=your-integration-key
PAGERDUTY_SERVICE_ID=your-service-id
```

**Features:**
- Incident management
- Escalation policies
- 99.99% reliability
- Mobile app

---

### 4. Microsoft Teams - Enterprise
**Best for:** Enterprise teams, Office 365 users

**Setup:**
```bash
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/YOUR/WEBHOOK/URL
```

**Features:**
- Adaptive cards
- Color coding
- Action buttons
- Office 365 integration

---

### 5. Telegram - Mobile Alerts
**Best for:** Personal notifications, mobile-first

**Setup:**
```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

**Features:**
- Instant messaging
- Bot commands
- Group support
- Global delivery

---

### 6. SMS - Emergency Only
**Best for:** Critical alerts when other channels fail

**Setup:**
```bash
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_FROM_NUMBER=+1234567890
SMS_RECIPIENTS=+1234567890
```

**Features:**
- 160 character limit
- Global reach
- High reliability
- Delivery receipts

---

### 7. Custom Webhooks - Integrations
**Best for:** Custom systems, logging, integrations

**Setup:**
```bash
CUSTOM_WEBHOOK_URL=https://your-service.com/webhook
CUSTOM_WEBHOOK_SECRET=your-secret-key
```

**Features:**
- JSON payload
- Custom headers
- Retry logic
- Flexible format

---

## 🎯 Smart Routing Examples

### Critical Database Issue
```
Channels: PagerDuty + Slack + Email
Reason: Immediate response needed + team awareness + documentation
```

### High CPU Alert
```
Channels: Slack + Email
Reason: Team collaboration + audit trail
```

### Security Incident
```
Channels: PagerDuty + Slack + SMS
Reason: Critical response + team alert + backup notification
```

### Routine Maintenance
```
Channels: Email + Teams
Reason: Documentation + team notification
```

---

## 🚀 Quick Start Commands

### Test Notification Channels
```bash
# Test Slack
curl -X POST $SLACK_WEBHOOK_URL -d '{"text":"Test from iTechSmart"}'

# Test Email (using Python)
python -c "from itechsmart_supreme.features.notification_manager import NotificationManager; import asyncio; asyncio.run(NotificationManager(config).send_test_email())"
```

### Create Workflow from Template #5
```python
from itechsmart_supreme.features.workflow_engine import WorkflowEngine

engine = WorkflowEngine()

# Create from template
workflow = engine.create_workflow_from_template(
    template_name='database_optimization',
    parameters={
        'host': 'db-server-01',
        'database': 'production'
    }
)

# Execute workflow
result = await engine.execute_workflow(
    workflow_id=workflow.id,
    context={'host': 'db-server-01'}
)
```

### Send Multi-Channel Alert
```python
from itechsmart_supreme.features.notification_manager import NotificationManager, NotificationChannel

notifier = NotificationManager(config)

await notifier.send_alert_notification(
    alert=alert,
    channels=[
        NotificationChannel.SLACK,
        NotificationChannel.EMAIL,
        NotificationChannel.PAGERDUTY
    ]
)
```

---

## 📊 Performance Metrics

### Notification Delivery Times
- Slack: < 1 second ⚡
- PagerDuty: < 2 seconds ⚡
- Telegram: < 3 seconds ⚡
- Teams: < 5 seconds ⚡
- Email: < 30 seconds ✅

### Workflow Execution Times
- Template #1 (High CPU): ~2-5 minutes
- Template #2 (Service Restart): ~1-2 minutes
- Template #3 (Security): ~5-10 minutes
- Template #5 (Database): ~10-15 minutes

---

## 🔧 Configuration Checklist

- [ ] Configure at least 2 notification channels
- [ ] Set up PagerDuty for critical alerts
- [ ] Configure email for documentation
- [ ] Test all channels before production
- [ ] Set up escalation policies
- [ ] Configure notification routing rules
- [ ] Enable rate limiting
- [ ] Set up monitoring for notification delivery

---

## 📝 Common Use Cases

### Use Case 1: Database Performance Issue
1. Alert triggers (query time > 5s)
2. Template #5 executes automatically
3. DBA team notified via Slack + Email
4. Approval requested (10 min timeout)
5. VACUUM ANALYZE runs (if approved)
6. Performance verified
7. Success notification sent

### Use Case 2: Security Breach
1. Wazuh detects intrusion
2. Template #3 executes
3. Host isolated immediately
4. Evidence collected
5. Security team paged via PagerDuty
6. P1 ticket created
7. Manual investigation begins

### Use Case 3: Service Outage
1. Service down detected
2. Template #2 executes
3. Config backed up
4. Service restarted gracefully
5. Health check performed
6. Team notified via Slack
7. Incident logged

---

## 🆘 Quick Troubleshooting

### Workflow Not Executing
- Check trigger conditions
- Verify workflow is enabled
- Review logs: `/var/log/itechsmart/workflows.log`

### Notifications Not Sending
- Verify channel configuration
- Check network connectivity
- Test webhook URLs manually
- Review notification logs

### Approval Timeout
- Default: 5 minutes (300 seconds)
- Increase timeout in workflow parameters
- Configure backup approvers

---

**For detailed documentation, see:** `WORKFLOW_TEMPLATES_AND_NOTIFICATIONS.md`

**For full feature guide, see:** `ENHANCED_FEATURES.md`