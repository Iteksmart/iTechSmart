# iTechSmart Supreme - Deployment Guide

## 🚀 Quick Deployment Guide

This guide will help you deploy iTechSmart Supreme's self-healing infrastructure in your environment.

---

## Prerequisites

### System Requirements
- **OS:** Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+, RHEL 8+)
- **Python:** 3.11 or higher
- **RAM:** 4GB minimum (8GB recommended)
- **Disk:** 20GB minimum
- **Network:** Stable internet connection

### Required Services
- **Prometheus:** Metrics monitoring server
- **Wazuh:** Security monitoring and SIEM
- **Docker:** (Optional) For VM provisioning
- **Active Directory:** (Optional) For Windows environments

---

## Installation

### Step 1: Install Dependencies

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python 3.11
sudo apt-get install python3.11 python3.11-venv python3-pip -y

# Install system dependencies
sudo apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    git
```

### Step 2: Install iTechSmart Supreme

```bash
# Clone repository (or extract package)
cd /opt
git clone https://github.com/itechsmart/itechsmart-supreme.git
cd itechsmart-supreme

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Install Additional Libraries

```bash
# For network device management
pip install netmiko paramiko

# For cloud providers (optional)
pip install boto3 google-cloud-compute azure-mgmt-compute

# For Active Directory (optional)
pip install pywinrm ldap3

# For monitoring
pip install prometheus-api-client
```

---

## Configuration

### Step 1: Create Configuration File

```bash
cp config/config.example.yaml config/config.yaml
nano config/config.yaml
```

### Step 2: Configure Monitoring

```yaml
# config/config.yaml

monitoring:
  prometheus:
    endpoints:
      - http://prometheus-server:9090
  
  wazuh:
    endpoints:
      - url: https://wazuh-server:55000
        username: admin
        password: your_password
```

### Step 3: Configure Cloud Providers (Optional)

```yaml
cloud:
  aws:
    region: us-east-1
    access_key: YOUR_AWS_ACCESS_KEY
    secret_key: YOUR_AWS_SECRET_KEY
  
  gcp:
    project_id: your-project-id
    credentials_file: /path/to/service-account.json
  
  azure:
    subscription_id: your-subscription-id
    tenant_id: your-tenant-id
    client_id: your-client-id
    client_secret: your-client-secret
```

### Step 4: Configure Domain (For Windows)

```yaml
domain:
  domain_controller: dc.example.com
  domain: example.com
  admin_username: administrator
  admin_password: your_password
  remediation_ou: OU=ServiceAccounts,DC=example,DC=com
```

---

## Running iTechSmart Supreme

### Method 1: Direct Execution

```python
# run.py
import asyncio
from itechsmart_supreme.core.auto_remediation_engine import (
    AutoRemediationEngine,
    RemediationMode
)

async def main():
    # Initialize engine
    engine = AutoRemediationEngine(
        prometheus_endpoints=['http://prometheus:9090'],
        wazuh_endpoints=[{
            'url': 'https://wazuh:55000',
            'username': 'admin',
            'password': 'admin'
        }],
        mode=RemediationMode.SEMI_AUTO  # or MANUAL, FULL_AUTO
    )
    
    # Start self-healing
    await engine.start()

if __name__ == '__main__':
    asyncio.run(main())
```

```bash
python run.py
```

### Method 2: Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/itechsmart-supreme.service
```

```ini
[Unit]
Description=iTechSmart Supreme Self-Healing Engine
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/itechsmart-supreme
Environment="PATH=/opt/itechsmart-supreme/venv/bin"
ExecStart=/opt/itechsmart-supreme/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable itechsmart-supreme
sudo systemctl start itechsmart-supreme

# Check status
sudo systemctl status itechsmart-supreme

# View logs
sudo journalctl -u itechsmart-supreme -f
```

---

## Testing

### Test 1: Verify Monitoring Integration

```python
# test_monitoring.py
import asyncio
from itechsmart_supreme.monitoring.prometheus_monitor import PrometheusMonitor

async def test_prometheus():
    monitor = PrometheusMonitor(
        endpoints=['http://prometheus:9090'],
        alert_callback=lambda alert: print(f"Alert: {alert.message}")
    )
    
    # Test query
    result = await monitor.query_custom_metric('up')
    print(f"Prometheus query result: {result}")

asyncio.run(test_prometheus())
```

### Test 2: Test Command Execution

```python
# test_execution.py
import asyncio
from itechsmart_supreme.execution.command_executor import SecureCommandExecutor
from itechsmart_supreme.core.models import RemediationAction, HostCredentials, Platform

async def test_execution():
    executor = SecureCommandExecutor()
    
    # Create test action
    action = RemediationAction(
        id='test-1',
        alert_id='alert-1',
        command='echo "Hello from iTechSmart Supreme"',
        platform=Platform.LINUX,
        requires_approval=False
    )
    
    # Create credentials
    credentials = HostCredentials(
        host='localhost',
        username='root',
        password='',
        platform=Platform.LINUX
    )
    
    # Execute
    result = await executor.execute_remediation(action, credentials)
    print(f"Execution result: {result.stdout}")

asyncio.run(test_execution())
```

### Test 3: Test Use Cases

```python
# test_use_cases.py
import asyncio
from itechsmart_supreme.use_cases.use_case_manager import UseCaseManager
from itechsmart_supreme.core.models import Alert, AlertSource, SeverityLevel

async def test_use_cases():
    manager = UseCaseManager()
    
    # Test high CPU alert
    alert = Alert(
        source=AlertSource.PROMETHEUS,
        severity=SeverityLevel.HIGH,
        message="High CPU usage detected: 95%",
        host="web-server-01",
        metrics={'cpu_usage': 95, 'metric_type': 'cpu'}
    )
    
    diagnosis = await manager.diagnose_and_remediate(alert)
    print(f"Diagnosis: {diagnosis.root_cause}")
    print(f"Recommendations: {len(diagnosis.recommendations)}")

asyncio.run(test_use_cases())
```

---

## Monitoring & Maintenance

### View Statistics

```python
# Get engine statistics
stats = engine.get_statistics()
print(f"Total alerts: {stats['total_alerts']}")
print(f"Auto-remediated: {stats['auto_remediated']}")
print(f"Success rate: {stats['avg_resolution_time']}")
```

### View Pending Approvals

```python
# Get pending approvals
approvals = engine.get_pending_approvals()
for approval in approvals:
    print(f"Action: {approval['description']}")
    print(f"Command: {approval['command']}")
    print(f"Risk: {approval['risk_level']}")
```

### Approve Actions

```python
# Approve an action
await engine.approve_action(
    action_id='action-123',
    approved_by='admin@itechsmart.dev'
)
```

### Emergency Stop

```python
# Enable global kill-switch
engine.enable_global_kill_switch()

# Disable when safe
engine.disable_global_kill_switch()
```

---

## Security Best Practices

### 1. Credential Management
- Store credentials in secure vault (HashiCorp Vault, AWS Secrets Manager)
- Rotate credentials regularly
- Use least privilege access
- Enable MFA where possible

### 2. Network Security
- Use VPN for remote access
- Implement firewall rules
- Enable TLS/SSL for all connections
- Isolate monitoring network

### 3. Audit Logging
- Enable comprehensive logging
- Store logs in immutable storage
- Regular log review
- Set up alerts for suspicious activity

### 4. Access Control
- Implement RBAC
- Regular access reviews
- Separate dev/prod environments
- Use approval workflows for high-risk actions

---

## Troubleshooting

### Issue: Can't connect to Prometheus

```bash
# Check Prometheus is running
curl http://prometheus:9090/-/healthy

# Check network connectivity
ping prometheus

# Check firewall rules
sudo iptables -L | grep 9090
```

### Issue: Can't connect to Wazuh

```bash
# Check Wazuh API is running
curl -k https://wazuh:55000/

# Verify credentials
curl -k -u admin:password https://wazuh:55000/security/user/authenticate
```

### Issue: Commands not executing

```bash
# Check SSH connectivity
ssh user@target-host

# Verify credentials
# Check executor logs
tail -f /var/log/itechsmart-supreme/executor.log
```

---

## Performance Tuning

### Optimize Alert Processing

```python
# Increase worker threads
engine.config['workers'] = 4

# Adjust queue size
engine.config['queue_size'] = 1000
```

### Optimize Database Queries

```python
# Enable query caching
engine.config['cache_enabled'] = True
engine.config['cache_ttl'] = 300
```

---

## Backup & Recovery

### Backup Configuration

```bash
# Backup configuration
tar -czf supreme-config-$(date +%Y%m%d).tar.gz config/

# Backup logs
tar -czf supreme-logs-$(date +%Y%m%d).tar.gz logs/
```

### Restore Configuration

```bash
# Restore configuration
tar -xzf supreme-config-20240112.tar.gz -C /opt/itechsmart-supreme/
```

---

## Support

### Documentation
- Implementation Summary: `IMPLEMENTATION_SUMMARY.md`
- API Documentation: `docs/api.md`
- Use Cases: `docs/use_cases.md`

### Logs
- Application logs: `/var/log/itechsmart-supreme/`
- Execution logs: `/var/log/itechsmart-supreme/executor.log`
- Audit logs: `/var/log/itechsmart-supreme/audit.log`

### Contact
- Email: support@itechsmart.dev
- Website: https://itechsmart.dev/supreme

---

## Next Steps

1. ✅ Complete installation
2. ✅ Configure monitoring
3. ✅ Test basic functionality
4. ✅ Deploy to production
5. ✅ Monitor and optimize

**Your self-healing infrastructure is ready!** 🎉