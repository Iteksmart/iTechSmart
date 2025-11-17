# 🧪 Integration Testing Suite

Comprehensive integration tests for the iTechSmart Suite demo environment.

---

## 📋 Overview

This test suite validates:
- Docker service health
- HTTP endpoint availability
- API functionality
- Database connectivity
- Reverse proxy routing
- Authentication endpoints
- Resource usage
- Inter-service communication
- Log analysis

---

## 🚀 Quick Start

### Prerequisites

- Demo environment running
- Docker and Docker Compose installed
- `curl` and `bc` utilities available

### Run All Tests

```bash
cd iTechSmart/integration-tests
./test-suite.sh
```

### Expected Output

```
========================================
iTechSmart Suite - Integration Test Suite
========================================

Starting integration tests...
Test environment: Demo
Base URL: http://localhost

========================================
Test Suite 1: Docker Services
========================================

✓ PASS - License Server Container
✓ PASS - PostgreSQL Container
✓ PASS - Nginx Proxy Container
...

========================================
Test Summary
========================================

Total Tests: 45
Passed: 45
Failed: 0

========================================
ALL TESTS PASSED! ✓
========================================
```

---

## 📊 Test Suites

### Suite 1: Docker Services (7 tests)
Verifies all Docker containers are running:
- License Server
- PostgreSQL Database
- Nginx Proxy
- iTechSmart Ninja
- iTechSmart Supreme
- iTechSmart Citadel
- iTechSmart Copilot

### Suite 2: Health Endpoints (6 tests)
Tests health check endpoints:
- Nginx proxy health
- License Server health
- All product health endpoints

### Suite 3: Web Interfaces (6 tests)
Validates web UI accessibility:
- Demo landing page
- License Server UI
- All product UIs

### Suite 4: API Endpoints (5 tests)
Tests API availability:
- License Server API
- Product APIs
- JSON response validation

### Suite 5: Database Connectivity (2 tests)
Verifies database connections:
- PostgreSQL direct connection
- License Server DB connection

### Suite 6: Reverse Proxy Routing (5 tests)
Tests Nginx routing:
- Proxy to License Server
- Proxy to all products

### Suite 7: Authentication (2 tests)
Validates auth endpoints:
- Login endpoint
- License validation endpoint

### Suite 8: Resource Usage (2 tests)
Monitors system resources:
- CPU usage (<80%)
- Memory usage (<80%)

### Suite 9: Network Connectivity (2 tests)
Tests inter-service communication:
- Product to License Server
- Service mesh connectivity

### Suite 10: Logs and Errors (2 tests)
Analyzes logs:
- Error count (<5)
- Warning count (<10)

---

## 🔧 Individual Test Commands

### Test Docker Services

```bash
# Check if container is running
docker ps | grep itechsmart-license-demo

# Check all containers
docker-compose -f demo-environment/docker-compose.demo.yml ps
```

### Test Health Endpoints

```bash
# Test License Server
curl http://localhost:3000/health

# Test Ninja
curl http://localhost:3001/health

# Test all services
for port in 3000 3001 3002 3003 3004; do
    echo "Testing port $port..."
    curl -s http://localhost:$port/health
done
```

### Test API Endpoints

```bash
# Test License Server API
curl http://localhost:3000/api/health

# Test with JSON parsing
curl -s http://localhost:3000/api/health | jq .
```

### Test Database

```bash
# Direct PostgreSQL connection
docker exec itechsmart-demo-db psql -U demo -d license_demo -c "SELECT 1;"

# Check database from License Server
curl http://localhost:3000/api/health | grep database
```

### Test Reverse Proxy

```bash
# Test proxy routing
curl http://localhost/license/health
curl http://localhost/ninja/health
curl http://localhost/supreme/health
```

### Test Inter-Service Communication

```bash
# From Ninja to License Server
docker exec itechsmart-ninja-demo curl http://license-server:3000/health

# From Supreme to License Server
docker exec itechsmart-supreme-demo curl http://license-server:3000/health
```

### Check Resource Usage

```bash
# Real-time stats
docker stats

# One-time stats
docker stats --no-stream
```

### Check Logs

```bash
# All services
docker-compose -f demo-environment/docker-compose.demo.yml logs

# Specific service
docker-compose -f demo-environment/docker-compose.demo.yml logs license-server

# Follow logs
docker-compose -f demo-environment/docker-compose.demo.yml logs -f

# Search for errors
docker-compose -f demo-environment/docker-compose.demo.yml logs | grep -i error
```

---

## 🐛 Troubleshooting

### Tests Failing

**Check if demo is running**:
```bash
cd demo-environment
docker-compose -f docker-compose.demo.yml ps
```

**Restart services**:
```bash
docker-compose -f docker-compose.demo.yml restart
```

**Check logs for errors**:
```bash
docker-compose -f docker-compose.demo.yml logs --tail=50
```

### Specific Test Failures

**Docker Service Tests Fail**:
- Ensure demo environment is started
- Check Docker daemon is running
- Verify no port conflicts

**Health Endpoint Tests Fail**:
- Wait for services to fully start (30-60 seconds)
- Check service logs for startup errors
- Verify network connectivity

**Database Tests Fail**:
- Check PostgreSQL container is running
- Verify database credentials
- Check License Server can connect

**Resource Usage Tests Fail**:
- Close unnecessary applications
- Increase Docker memory limit
- Stop unused containers

**Network Tests Fail**:
- Check Docker network configuration
- Verify services are on same network
- Check firewall rules

---

## 📈 Performance Benchmarks

### Expected Response Times

| Endpoint | Expected | Acceptable |
|----------|----------|------------|
| Health checks | <50ms | <200ms |
| API calls | <100ms | <500ms |
| Web UI | <200ms | <1s |
| Database queries | <50ms | <200ms |

### Resource Usage Targets

| Resource | Target | Maximum |
|----------|--------|---------|
| CPU | <50% | <80% |
| Memory | <60% | <80% |
| Disk I/O | <50% | <80% |
| Network | <50% | <80% |

---

## 🔄 Continuous Integration

### GitHub Actions Integration

Add to `.github/workflows/integration-tests.yml`:

```yaml
name: Integration Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Start Demo Environment
      run: |
        cd demo-environment
        ./setup-demo.sh
    
    - name: Wait for Services
      run: sleep 30
    
    - name: Run Integration Tests
      run: |
        cd integration-tests
        ./test-suite.sh
    
    - name: Stop Demo Environment
      if: always()
      run: |
        cd demo-environment
        docker-compose -f docker-compose.demo.yml down
```

---

## 📊 Test Reports

### Generate HTML Report

```bash
# Run tests and save output
./test-suite.sh > test-results.txt 2>&1

# Convert to HTML (requires ansi2html)
cat test-results.txt | ansi2html > test-results.html
```

### Generate JSON Report

```bash
# Create custom JSON reporter
./test-suite.sh --json > test-results.json
```

---

## 🎯 Best Practices

### Before Running Tests

1. Ensure demo environment is running
2. Wait for all services to be ready (30-60 seconds)
3. Check no port conflicts exist
4. Verify sufficient system resources

### During Tests

1. Don't modify services while testing
2. Monitor resource usage
3. Check logs for errors
4. Note any warnings

### After Tests

1. Review test results
2. Investigate failures
3. Check logs for issues
4. Document findings

---

## 📝 Adding New Tests

### Test Template

```bash
# Function to test new feature
test_new_feature() {
    local name=$1
    local url=$2
    
    # Test logic here
    local result=$(curl -s "$url")
    
    if [ condition ]; then
        print_result "$name" "PASS"
        return 0
    else
        print_result "$name" "FAIL"
        return 1
    fi
}

# Add to test suite
print_header "Test Suite X: New Feature"
test_new_feature "Feature Name" "http://localhost:3000/feature"
```

### Test Guidelines

1. **Clear naming**: Use descriptive test names
2. **Single purpose**: One test per function
3. **Error handling**: Catch and report errors
4. **Cleanup**: Clean up test data
5. **Documentation**: Document test purpose

---

## 🔍 Advanced Testing

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 http://localhost:3000/health
```

### Security Testing

```bash
# Check for common vulnerabilities
docker run --rm -v $(pwd):/target aquasec/trivy fs /target

# Check SSL/TLS configuration
testssl.sh https://localhost
```

### Performance Profiling

```bash
# Profile API endpoint
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:3000/api/health

# Monitor resource usage
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

---

## 📞 Support

### Issues
- **GitHub**: https://github.com/Iteksmart/iTechSmart/issues
- **Email**: support@itechsmart.com

### Documentation
- **Main Docs**: [GitHub Repository](https://github.com/Iteksmart/iTechSmart)
- **Demo Guide**: [demo-environment/README.md](../demo-environment/README.md)

---

## ✅ Checklist

Before running tests:
- [ ] Demo environment is running
- [ ] All services are healthy
- [ ] No port conflicts
- [ ] Sufficient resources available

After running tests:
- [ ] All tests passed
- [ ] No errors in logs
- [ ] Resource usage acceptable
- [ ] Results documented

---

**Last Updated**: November 17, 2025  
**Version**: 1.0.0  
**Status**: Production Ready

---

**END OF README**