# Agent Connectivity Testing Guide

**Version**: 1.1.0  
**Date**: November 17, 2025  
**Purpose**: Verify agent integration and connectivity

---

## 🎯 Testing Overview

This guide provides step-by-step instructions for testing agent connectivity and integration across all iTechSmart products.

---

## 📋 Pre-Test Requirements

### Environment Setup
- [ ] License Server running on port 3000
- [ ] At least one agent deployed and running
- [ ] Tier 1 products deployed (Ninja, Enterprise, Supreme, Citadel)
- [ ] Tier 2 products deployed (Analytics, Copilot, Shield, Sentinel, DevOps)
- [ ] Network connectivity between all components

### Tools Required
- `curl` or `wget` for API testing
- Web browser for dashboard testing
- Terminal access to servers
- API testing tool (Postman, Insomnia, or similar)

---

## 🧪 Test Suite 1: License Server Connectivity

### Test 1.1: Health Check
```bash
curl http://localhost:3000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "version": "1.1.0",
  "service": "License Server"
}
```

- [ ] Status is "healthy"
- [ ] Version is "1.1.0"
- [ ] Response time < 100ms

### Test 1.2: Agent Registration
```bash
curl http://localhost:3000/api/agents
```

**Expected Response**:
```json
{
  "agents": [
    {
      "id": "agent-uuid",
      "hostname": "server-1",
      "status": "ACTIVE",
      "lastSeen": "2025-11-17T...",
      "lastMetrics": {
        "cpuUsage": 25.5,
        "memoryUsage": 60.2,
        "diskUsage": 45.8
      }
    }
  ],
  "total": 1
}
```

- [ ] At least one agent listed
- [ ] Agent status is "ACTIVE"
- [ ] lastSeen timestamp is recent (< 1 minute)
- [ ] Metrics are present and valid

### Test 1.3: Agent Details
```bash
curl http://localhost:3000/api/agents/{agent-id}
```

**Expected Response**:
```json
{
  "id": "agent-uuid",
  "hostname": "server-1",
  "status": "ACTIVE",
  "ipAddress": "192.168.1.100",
  "platform": "linux",
  "version": "1.1.0",
  "lastSeen": "2025-11-17T...",
  "lastMetrics": {
    "cpuUsage": 25.5,
    "memoryUsage": 60.2,
    "diskUsage": 45.8,
    "networkIn": 1024,
    "networkOut": 2048
  },
  "security": {
    "firewallEnabled": true,
    "antivirusEnabled": true,
    "updatesAvailable": 0
  }
}
```

- [ ] All fields present
- [ ] Data is accurate
- [ ] Security information included
- [ ] Timestamps are recent

---

## 🧪 Test Suite 2: Tier 1 Product Integration

### Test 2.1: iTechSmart Ninja

#### API Test
```bash
curl http://localhost:8001/api/v1/agents
```

- [ ] Returns agent list
- [ ] Data matches License Server
- [ ] Response time < 200ms

#### Dashboard Test
1. Open http://localhost:8001 in browser
2. Navigate to Agent Monitoring section
3. Verify:
   - [ ] Agent list visible
   - [ ] Real-time metrics updating
   - [ ] Health scores displayed
   - [ ] Charts rendering correctly
   - [ ] Auto-refresh working (30s interval)

### Test 2.2: iTechSmart Enterprise

#### API Test
```bash
curl http://localhost:8002/api/v1/agents/analytics/health-score
```

**Expected Response**:
```json
{
  "healthScore": 95,
  "status": "excellent",
  "totalAgents": 1,
  "timestamp": "2025-11-17T..."
}
```

- [ ] Health score calculated
- [ ] Status determined correctly
- [ ] Agent count accurate

#### Dashboard Test
1. Open http://localhost:8002
2. Navigate to Agent Dashboard
3. Verify:
   - [ ] Health score displayed
   - [ ] Filter tabs working (All, Active, Offline, Error)
   - [ ] Agent cards showing correct status
   - [ ] Metrics visualization working

### Test 2.3: iTechSmart Supreme Plus

#### API Test
```bash
curl http://localhost:8005/api/v1/agents/analytics/trends?hours=24
```

- [ ] Trend data returned
- [ ] CPU, Memory, Disk trends included
- [ ] Data points present

#### Dashboard Test
1. Open http://localhost:8005
2. Check Analytics Dashboard
3. Verify:
   - [ ] Trend charts visible
   - [ ] Historical data displayed
   - [ ] Predictions shown (if available)

### Test 2.4: iTechSmart Citadel

#### API Test
```bash
curl http://localhost:8006/api/v1/agents/security/summary
```

**Expected Response**:
```json
{
  "totalAgents": 1,
  "secureAgents": 1,
  "atRiskAgents": 0,
  "criticalAgents": 0,
  "averageSecurityScore": 100,
  "threats": [],
  "recommendations": ["All agents are secure. Continue monitoring."]
}
```

- [ ] Security summary accurate
- [ ] Threat detection working
- [ ] Recommendations provided

#### Dashboard Test
1. Open http://localhost:8006
2. Check Security Dashboard
3. Verify:
   - [ ] Security score displayed
   - [ ] Threat list visible
   - [ ] Risk classification working
   - [ ] Security recommendations shown

### Test 2.5: Desktop Launcher

#### Application Test
1. Launch Desktop Launcher
2. Open Agent Monitoring
3. Verify:
   - [ ] Agent list in system tray
   - [ ] Status indicators correct
   - [ ] Metrics displayed
   - [ ] Notifications working
   - [ ] IPC communication functional

---

## 🧪 Test Suite 3: Tier 2 Product Integration

### Test 3.1: iTechSmart Analytics

#### API Test
```bash
curl http://localhost:8003/api/v1/agents/stats/summary
```

- [ ] Summary statistics returned
- [ ] Average metrics calculated
- [ ] Agent counts accurate

#### Widget Test
1. Open http://localhost:8003
2. Check Agent Status Widget
3. Verify:
   - [ ] Widget displays agent data
   - [ ] Metrics visualization working
   - [ ] Auto-refresh enabled

### Test 3.2: iTechSmart Copilot

#### API Test
```bash
curl http://localhost:8004/api/v1/agents/ai/insights
```

**Expected Response**:
```json
{
  "insights": [
    {
      "type": "success",
      "title": "All Systems Operational",
      "description": "All agents are healthy...",
      "severity": "low"
    }
  ],
  "recommendations": ["Continue monitoring..."],
  "summary": "System health is excellent.",
  "healthPercentage": 100
}
```

- [ ] AI insights generated
- [ ] Recommendations provided
- [ ] Summary accurate

#### Widget Test
1. Open http://localhost:8004
2. Check AI Insights Widget
3. Verify:
   - [ ] Insights displayed
   - [ ] Recommendations visible
   - [ ] Health percentage shown

### Test 3.3: iTechSmart Shield

#### API Test
```bash
curl http://localhost:8017/api/v1/agents/security/threats
```

- [ ] Threat list returned
- [ ] Severity classification correct
- [ ] Recommendations provided

#### Widget Test
1. Open http://localhost:8017
2. Check Security Widget
3. Verify:
   - [ ] Threats displayed
   - [ ] Security score visible
   - [ ] Filter by severity working

### Test 3.4: iTechSmart Sentinel

#### API Test
```bash
curl http://localhost:8018/api/v1/agents
```

- [ ] Agent list returned
- [ ] Basic monitoring data present

#### Widget Test
1. Open http://localhost:8018
2. Check Monitoring Widget
3. Verify:
   - [ ] Agent status visible
   - [ ] Basic metrics displayed

### Test 3.5: iTechSmart DevOps

#### API Test
```bash
curl http://localhost:8019/api/v1/agents
```

- [ ] Agent list returned
- [ ] Deployment status available

#### Widget Test
1. Open http://localhost:8019
2. Check Deployment Widget
3. Verify:
   - [ ] Agent status in CI/CD context
   - [ ] Deployment health visible

---

## 🧪 Test Suite 4: Real-Time Updates

### Test 4.1: WebSocket Connection
1. Open browser developer console
2. Navigate to any Tier 1 product dashboard
3. Check Network tab for WebSocket connection
4. Verify:
   - [ ] WebSocket connection established
   - [ ] Messages being received
   - [ ] Auto-reconnect on disconnect
   - [ ] No connection errors

### Test 4.2: Live Metrics Update
1. Open Ninja dashboard
2. Watch metrics for 2 minutes
3. Verify:
   - [ ] Metrics update every 30 seconds
   - [ ] Charts animate smoothly
   - [ ] No data gaps
   - [ ] Timestamps accurate

---

## 🧪 Test Suite 5: Alert System

### Test 5.1: Generate Offline Alert
```bash
# Stop agent
sudo systemctl stop itechsmart-agent

# Wait 2 minutes

# Check for alert
curl http://localhost:3000/api/agents/{agent-id}/alerts
```

**Expected Response**:
```json
{
  "alerts": [
    {
      "id": "alert-uuid",
      "type": "agent_offline",
      "severity": "CRITICAL",
      "message": "Agent has gone offline",
      "timestamp": "2025-11-17T...",
      "resolved": false
    }
  ]
}
```

- [ ] Alert generated within 2 minutes
- [ ] Severity is CRITICAL
- [ ] Alert visible in dashboards
- [ ] Notification sent (if configured)

### Test 5.2: Resolve Alert
```bash
# Start agent
sudo systemctl start itechsmart-agent

# Wait 1 minute

# Check alert status
curl http://localhost:3000/api/agents/{agent-id}/alerts
```

- [ ] Agent reconnects
- [ ] Alert auto-resolved
- [ ] Status updated in dashboards

### Test 5.3: High Resource Alert
```bash
# Simulate high CPU usage
stress --cpu 8 --timeout 60s

# Check for alert
curl http://localhost:3000/api/agents/{agent-id}/alerts
```

- [ ] High CPU alert generated
- [ ] Severity appropriate (WARNING or CRITICAL)
- [ ] Recommendation provided

---

## 🧪 Test Suite 6: Performance Testing

### Test 6.1: Response Time
```bash
# Test API response times
for i in {1..10}; do
  time curl -s http://localhost:3000/api/agents > /dev/null
done
```

- [ ] Average response time < 200ms
- [ ] No timeouts
- [ ] Consistent performance

### Test 6.2: Load Testing
```bash
# Use Apache Bench or similar
ab -n 1000 -c 10 http://localhost:3000/api/agents
```

- [ ] Handles 1000 requests successfully
- [ ] No errors
- [ ] Response times acceptable under load

### Test 6.3: Resource Usage
```bash
# Check Docker stats
docker stats --no-stream
```

- [ ] CPU usage < 5% per service
- [ ] Memory usage < 500MB per service
- [ ] No memory leaks
- [ ] Network usage reasonable

---

## 🧪 Test Suite 7: Security Testing

### Test 7.1: Authentication
```bash
# Test without API key
curl http://localhost:3000/api/agents

# Test with invalid API key
curl -H "Authorization: Bearer invalid-key" http://localhost:3000/api/agents
```

- [ ] Unauthorized access blocked
- [ ] Proper error messages returned
- [ ] No sensitive data leaked

### Test 7.2: TLS/SSL
```bash
# Test HTTPS connection
curl -v https://your-domain.com/api/agents
```

- [ ] TLS 1.3 used
- [ ] Certificate valid
- [ ] No SSL errors
- [ ] Grade A+ on SSL Labs

### Test 7.3: Rate Limiting
```bash
# Send many requests quickly
for i in {1..100}; do
  curl http://localhost:3000/api/agents &
done
```

- [ ] Rate limiting active
- [ ] 429 status returned when exceeded
- [ ] Service remains stable

---

## 🧪 Test Suite 8: Data Accuracy

### Test 8.1: Metric Validation
1. Check agent's actual CPU usage: `top`
2. Check reported CPU in dashboard
3. Verify:
   - [ ] Values match within 5%
   - [ ] Updates are timely
   - [ ] No stale data

### Test 8.2: Historical Data
```bash
curl http://localhost:8001/api/v1/agents/{agent-id}/metrics?hours=24
```

- [ ] 24 hours of data available
- [ ] No gaps in data
- [ ] Timestamps sequential
- [ ] Values reasonable

---

## 📊 Test Results Summary

### Overall Status
- [ ] All tests passed
- [ ] No critical issues
- [ ] Performance acceptable
- [ ] Security verified
- [ ] Ready for production

### Issues Found
| Test | Issue | Severity | Status |
|------|-------|----------|--------|
|      |       |          |        |

### Recommendations
1. 
2. 
3. 

---

## ✅ Sign-Off

**Tested By**: _________________  
**Date**: _________________  
**Status**: ☐ PASS ☐ FAIL  
**Notes**: _________________

---

**© 2025 iTechSmart Inc. All rights reserved.**