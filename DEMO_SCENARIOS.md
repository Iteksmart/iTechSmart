# iTechSmart Supreme - Demo Scenarios

This document provides step-by-step demo scenarios to showcase iTechSmart Supreme's capabilities.

## 🎯 Demo Overview

These scenarios demonstrate:
1. High CPU usage detection and resolution
2. Brute force attack mitigation
3. Service down recovery
4. Disk space cleanup
5. Security event handling

## Scenario 1: High CPU Usage Auto-Resolution

### Setup

```bash
# On a test server, create a CPU-intensive script
cat > /tmp/backup.sh << 'EOF'
#!/bin/bash
while true; do
    echo "Processing..." > /dev/null
done
EOF

chmod +x /tmp/backup.sh
```

### Trigger the Issue

```bash
# Start the runaway process
/tmp/backup.sh &
```

### Expected iTechSmart Supreme Response

1. **Detection** (within 30 seconds):
   - Prometheus detects CPU usage > 80%
   - Alert generated: "High CPU usage detected: 95.2%"

2. **Diagnosis** (within 5 seconds):
   - AI identifies: "High CPU usage caused by process: backup.sh"
   - Confidence: 85%
   - Recommended action: `pkill -f "backup.sh"`

3. **Remediation** (within 10 seconds):
   - If auto-remediation enabled: Executes immediately
   - If approval required: Appears in dashboard for approval

4. **Verification**:
   - CPU usage returns to normal
   - Alert marked as resolved
   - Execution logged in audit trail

### Dashboard View

```
🚨 Alert: High CPU usage detected: 95.2%
   Host: server1.example.com
   Severity: HIGH
   Time: 2025-01-15 10:30:45

⚡ Proposed Action:
   Description: Kill runaway backup process
   Command: pkill -f "backup.sh"
   Risk Level: LOW
   
   [✅ Approve] [❌ Reject]
```

### Verification

```bash
# Check CPU usage returned to normal
top -bn1 | grep "Cpu(s)"

# Verify process is killed
ps aux | grep backup.sh

# Check iTechSmart logs
curl http://localhost:5000/api/executions | jq
```

## Scenario 2: Brute Force Attack Mitigation

### Setup

```bash
# Install fail2ban for testing (optional)
sudo apt-get install fail2ban

# Configure SSH to allow testing
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin yes (for testing only!)
sudo systemctl restart sshd
```

### Trigger the Issue

```bash
# Simulate failed login attempts from another machine
for i in {1..10}; do
    sshpass -p "wrongpassword" ssh root@target-server 2>/dev/null
    sleep 1
done
```

### Expected iTechSmart Supreme Response

1. **Detection**:
   - Wazuh detects 10 failed login attempts
   - Alert: "Brute force attack detected from 192.168.1.100: 10 failed attempts"

2. **Diagnosis**:
   - Root cause: "Brute force attack from 192.168.1.100"
   - Confidence: 95%
   - Recommended actions:
     - `iptables -A INPUT -s 192.168.1.100 -j DROP`
     - `fail2ban-client set sshd banip 192.168.1.100`

3. **Remediation**:
   - Blocks attacking IP immediately (if auto-remediation enabled)
   - Logs incident for security review

### Dashboard View

```
🚨 Alert: Brute force attack detected
   Host: server1.example.com
   Source IP: 192.168.1.100
   Failed Attempts: 10
   Severity: HIGH

⚡ Proposed Actions:
   1. Block IP address 192.168.1.100
      Command: iptables -A INPUT -s 192.168.1.100 -j DROP
      Risk Level: LOW
   
   2. Add to fail2ban
      Command: fail2ban-client set sshd banip 192.168.1.100
      Risk Level: LOW
```

### Verification

```bash
# Check iptables rules
sudo iptables -L -n | grep 192.168.1.100

# Try to connect from blocked IP (should fail)
ssh root@target-server

# Check fail2ban status
sudo fail2ban-client status sshd
```

## Scenario 3: Service Down Recovery

### Setup

```bash
# Install nginx for testing
sudo apt-get install nginx
sudo systemctl start nginx
```

### Trigger the Issue

```bash
# Stop nginx to simulate service down
sudo systemctl stop nginx
```

### Expected iTechSmart Supreme Response

1. **Detection**:
   - Prometheus detects service down
   - Alert: "Service down: nginx on server1.example.com"

2. **Diagnosis**:
   - Root cause: "Service nginx is down or unresponsive"
   - Confidence: 85%
   - Recommended actions:
     - Check service status
     - Check service logs
     - Restart service
     - Verify service is running

3. **Remediation**:
   - Executes: `systemctl restart nginx`
   - Verifies: `systemctl is-active nginx`

### Dashboard View

```
🚨 Alert: Service down: nginx
   Host: server1.example.com
   Severity: CRITICAL

⚡ Proposed Actions:
   1. Check status of nginx
      Command: systemctl status nginx
      Risk Level: NONE
   
   2. Restart nginx service
      Command: systemctl restart nginx
      Risk Level: MEDIUM
   
   3. Verify nginx is running
      Command: systemctl is-active nginx
      Risk Level: NONE
```

### Verification

```bash
# Check nginx is running
sudo systemctl status nginx

# Verify web server responds
curl http://localhost

# Check iTechSmart logs
curl http://localhost:5000/api/executions | jq '.[] | select(.command | contains("nginx"))'
```

## Scenario 4: Disk Space Cleanup

### Setup

```bash
# Fill up disk space for testing
sudo dd if=/dev/zero of=/tmp/largefile bs=1M count=5000
```

### Trigger the Issue

```bash
# Check disk usage (should be high)
df -h /
```

### Expected iTechSmart Supreme Response

1. **Detection**:
   - Prometheus detects disk usage > 80%
   - Alert: "High disk usage on /: 92.5%"

2. **Diagnosis**:
   - Root cause: "Critical disk usage on / (92.5%) - cleanup required"
   - Confidence: 80%
   - Recommended actions:
     - Find large directories
     - Clean old logs
     - Clean temporary files

3. **Remediation**:
   - Executes: `journalctl --vacuum-time=7d`
   - Executes: `find /tmp -type f -atime +7 -delete`

### Dashboard View

```
🚨 Alert: High disk usage on /: 92.5%
   Host: server1.example.com
   Severity: HIGH

⚡ Proposed Actions:
   1. Find largest directories
      Command: du -sh /* 2>/dev/null | sort -rh | head -10
      Risk Level: NONE
   
   2. Clean old systemd journal logs
      Command: journalctl --vacuum-time=7d
      Risk Level: LOW
   
   3. Clean old temporary files
      Command: find /tmp -type f -atime +7 -delete
      Risk Level: LOW
```

### Verification

```bash
# Check disk usage improved
df -h /

# Verify cleanup
journalctl --disk-usage

# Clean up test file
sudo rm /tmp/largefile
```

## Scenario 5: Security Event Handling

### Setup

```bash
# Create a test file for FIM monitoring
echo "original content" > /etc/test-monitored-file
```

### Trigger the Issue

```bash
# Modify the monitored file
echo "modified content" > /etc/test-monitored-file
```

### Expected iTechSmart Supreme Response

1. **Detection**:
   - Wazuh FIM detects file modification
   - Alert: "File modified: /etc/test-monitored-file"

2. **Diagnosis**:
   - Root cause: "Unauthorized file modification: /etc/test-monitored-file"
   - Confidence: 85%
   - Recommended actions:
     - Check file details
     - Get file hash
     - Review recent changes

3. **Remediation**:
   - Investigative commands executed
   - Security team notified
   - File changes logged

### Dashboard View

```
🚨 Alert: File modified: /etc/test-monitored-file
   Host: server1.example.com
   Severity: HIGH
   Event: File Integrity Monitoring

⚡ Proposed Actions:
   1. Check file details
      Command: ls -la /etc/test-monitored-file
      Risk Level: NONE
   
   2. Get file hash
      Command: md5sum /etc/test-monitored-file
      Risk Level: NONE
```

## Complete Demo Script

Run this script to demonstrate all scenarios:

```bash
#!/bin/bash

echo "=== iTechSmart Supreme Demo ==="
echo ""

# Scenario 1: High CPU
echo "Scenario 1: High CPU Usage"
echo "Starting CPU-intensive process..."
cat > /tmp/backup.sh << 'EOF'
#!/bin/bash
while true; do echo "Processing..." > /dev/null; done
EOF
chmod +x /tmp/backup.sh
/tmp/backup.sh &
BACKUP_PID=$!
echo "Process started with PID: $BACKUP_PID"
echo "Watch iTechSmart Supreme dashboard for alert..."
sleep 60
echo "Cleaning up..."
kill $BACKUP_PID 2>/dev/null
rm /tmp/backup.sh

echo ""
echo "Scenario 2: Service Down"
echo "Stopping nginx..."
sudo systemctl stop nginx
echo "Watch iTechSmart Supreme dashboard for alert..."
sleep 30
echo "Service should be auto-restarted by iTechSmart Supreme"
sleep 30

echo ""
echo "Scenario 3: Disk Space"
echo "Creating large file..."
sudo dd if=/dev/zero of=/tmp/largefile bs=1M count=5000 2>/dev/null
echo "Watch iTechSmart Supreme dashboard for alert..."
sleep 60
echo "Cleaning up..."
sudo rm /tmp/largefile

echo ""
echo "=== Demo Complete ==="
echo "Check iTechSmart Supreme dashboard at http://localhost:5000"
echo "Review execution history: curl http://localhost:5000/api/executions | jq"
```

## Testing Checklist

- [ ] Prometheus integration working
- [ ] Wazuh integration working
- [ ] High CPU detection and remediation
- [ ] Brute force detection and blocking
- [ ] Service restart working
- [ ] Disk cleanup working
- [ ] Dashboard updates in real-time
- [ ] Approval workflow functioning
- [ ] Audit logs being created
- [ ] Kill switch working

## Demo Tips

1. **Preparation**:
   - Set up test environment separate from production
   - Configure monitoring endpoints
   - Add test hosts to iTechSmart Supreme
   - Enable auto-remediation for demo (disable for production initially)

2. **Presentation**:
   - Open dashboard on large screen
   - Show real-time updates
   - Explain each step as it happens
   - Highlight approval workflow
   - Show audit logs

3. **Safety**:
   - Use test environment only
   - Have rollback plan
   - Keep kill switch accessible
   - Monitor closely during demo

4. **Metrics to Highlight**:
   - Detection time (< 30 seconds)
   - Diagnosis time (< 5 seconds)
   - Remediation time (< 10 seconds)
   - Success rate (> 95%)
   - Zero human intervention required

## Troubleshooting Demo Issues

### Issue: Alerts not appearing

**Solution**:
```bash
# Check monitoring connections
curl http://localhost:5000/api/status

# Verify Prometheus is scraping
curl http://prometheus:9090/api/v1/targets

# Check logs
docker-compose logs -f itechsmart-supreme
```

### Issue: Actions not executing

**Solution**:
```bash
# Check credentials
curl http://localhost:5000/api/hosts

# Test SSH manually
ssh admin@test-server

# Check kill switch status
curl http://localhost:5000/api/killswitch/status
```

### Issue: Dashboard not updating

**Solution**:
```bash
# Check WebSocket connection
# Open browser console and look for connection errors

# Restart application
docker-compose restart itechsmart-supreme
```

---

**Ready to demo? Show the world the end of IT downtime! 🚀**