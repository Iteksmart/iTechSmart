# iTechSmart Suite - Integration Testing Guide

## Overview
This guide provides comprehensive testing procedures for the complete iTechSmart Suite, including the License Server and Desktop Launcher integration.

## Table of Contents
1. [Test Environment Setup](#test-environment-setup)
2. [License Server Testing](#license-server-testing)
3. [Desktop Launcher Testing](#desktop-launcher-testing)
4. [Integration Testing](#integration-testing)
5. [Performance Testing](#performance-testing)
6. [Security Testing](#security-testing)
7. [User Acceptance Testing](#user-acceptance-testing)

## Test Environment Setup

### Prerequisites
- Clean test machines for each platform:
  * Windows 10/11 (x64)
  * macOS 10.13+ (Intel and Apple Silicon)
  * Ubuntu 22.04 LTS (x64)
- Docker Desktop installed (or Docker Engine on Linux)
- Internet connection
- Test license keys

### Environment Configuration

#### 1. License Server Setup
```bash
# Clone repository
git clone https://github.com/Iteksmart/iTechSmart.git
cd iTechSmart/license-server

# Configure environment
cp .env.example .env
nano .env  # Update with test configuration

# Start services
docker compose up -d

# Verify health
curl http://localhost:3001/health
```

#### 2. Desktop Launcher Setup
```bash
# Navigate to desktop launcher
cd ../desktop-launcher

# Install dependencies
npm install

# Build application
npm run build

# Create test installer
npm run package
```

## License Server Testing

### Test Suite 1: API Endpoints

#### Test 1.1: Health Check
**Objective:** Verify server is running and healthy

**Steps:**
```bash
curl http://localhost:3001/health
```

**Expected Result:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-16T...",
  "uptime": 3600,
  "database": "connected",
  "version": "1.0.0"
}
```

**Pass Criteria:**
- [ ] Status code: 200
- [ ] Response contains all required fields
- [ ] Database status is "connected"
- [ ] Response time < 100ms

#### Test 1.2: Organization Registration
**Objective:** Create new organization account

**Steps:**
```bash
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Organization",
    "domain": "test.com",
    "email": "admin@test.com",
    "password": "TestPassword123!"
  }'
```

**Expected Result:**
- Organization created successfully
- User account created
- JWT token returned

**Pass Criteria:**
- [ ] Status code: 201
- [ ] Organization ID returned
- [ ] User ID returned
- [ ] Valid JWT token returned
- [ ] Response time < 500ms

#### Test 1.3: User Login
**Objective:** Authenticate existing user

**Steps:**
```bash
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "TestPassword123!"
  }'
```

**Expected Result:**
- Login successful
- JWT token returned
- User details returned

**Pass Criteria:**
- [ ] Status code: 200
- [ ] Valid JWT token returned
- [ ] User details correct
- [ ] Response time < 300ms

#### Test 1.4: License Creation
**Objective:** Create new license

**Steps:**
```bash
TOKEN="<jwt_token_from_login>"

curl -X POST http://localhost:3001/api/licenses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "tier": "PROFESSIONAL",
    "maxUsers": 25,
    "maxProducts": 10,
    "expiresAt": "2025-12-31T23:59:59Z"
  }'
```

**Expected Result:**
- License created successfully
- License key generated
- All limits set correctly

**Pass Criteria:**
- [ ] Status code: 201
- [ ] Valid license key format (ITSM-XXXX-XXXX-XXXX-XXXX)
- [ ] All fields match request
- [ ] Response time < 500ms

#### Test 1.5: License Validation
**Objective:** Validate license key

**Steps:**
```bash
LICENSE_KEY="<license_key_from_creation>"

curl -X POST http://localhost:3001/api/licenses/validate \
  -H "Content-Type: application/json" \
  -d '{
    "licenseKey": "'$LICENSE_KEY'",
    "productId": "itechsmart-analytics",
    "machineId": "test-machine-123"
  }'
```

**Expected Result:**
- License validated successfully
- License details returned
- Usage information included

**Pass Criteria:**
- [ ] Status code: 200
- [ ] valid: true
- [ ] License details correct
- [ ] Usage stats included
- [ ] Response time < 200ms

### Test Suite 2: Error Handling

#### Test 2.1: Invalid License Key
**Steps:**
```bash
curl -X POST http://localhost:3001/api/licenses/validate \
  -H "Content-Type: application/json" \
  -d '{
    "licenseKey": "INVALID-KEY",
    "productId": "itechsmart-analytics"
  }'
```

**Expected Result:**
- Error response returned
- Clear error message

**Pass Criteria:**
- [ ] Status code: 400 or 404
- [ ] Error code: "INVALID_LICENSE"
- [ ] Error message clear and helpful

#### Test 2.2: Expired License
**Steps:**
```bash
# Create expired license first
curl -X POST http://localhost:3001/api/licenses \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "tier": "TRIAL",
    "expiresAt": "2020-01-01T00:00:00Z"
  }'

# Try to validate
curl -X POST http://localhost:3001/api/licenses/validate \
  -H "Content-Type: application/json" \
  -d '{
    "licenseKey": "<expired_key>",
    "productId": "itechsmart-analytics"
  }'
```

**Expected Result:**
- Validation fails
- Expiration reason provided

**Pass Criteria:**
- [ ] Status code: 400
- [ ] valid: false
- [ ] Reason: "expired"
- [ ] Expiration date included

#### Test 2.3: Rate Limiting
**Steps:**
```bash
# Make 150 requests rapidly
for i in {1..150}; do
  curl http://localhost:3001/health
done
```

**Expected Result:**
- First 100 requests succeed
- Subsequent requests rate limited

**Pass Criteria:**
- [ ] First 100: Status 200
- [ ] After 100: Status 429
- [ ] Retry-After header present
- [ ] Rate limit resets after window

### Test Suite 3: Database Operations

#### Test 3.1: Data Persistence
**Objective:** Verify data persists across restarts

**Steps:**
1. Create organization and license
2. Stop license server
3. Start license server
4. Verify data still exists

**Pass Criteria:**
- [ ] Organization data intact
- [ ] License data intact
- [ ] No data loss

#### Test 3.2: Concurrent Operations
**Objective:** Test concurrent license validations

**Steps:**
```bash
# Run 50 concurrent validations
for i in {1..50}; do
  curl -X POST http://localhost:3001/api/licenses/validate \
    -H "Content-Type: application/json" \
    -d '{
      "licenseKey": "'$LICENSE_KEY'",
      "productId": "itechsmart-analytics"
    }' &
done
wait
```

**Pass Criteria:**
- [ ] All requests succeed
- [ ] No database errors
- [ ] Response times consistent
- [ ] No data corruption

## Desktop Launcher Testing

### Test Suite 4: Installation

#### Test 4.1: Windows Installation
**Platform:** Windows 10/11

**Steps:**
1. Download iTechSmart-Suite-Setup-1.0.0.exe
2. Run installer
3. Follow installation wizard
4. Launch application

**Pass Criteria:**
- [ ] Installer runs without errors
- [ ] Application installs to correct location
- [ ] Desktop shortcut created
- [ ] Start menu entry created
- [ ] Application launches successfully

#### Test 4.2: macOS Installation
**Platform:** macOS 10.13+

**Steps:**
1. Download iTechSmart-Suite-1.0.0.dmg
2. Open DMG file
3. Drag to Applications folder
4. Launch application

**Pass Criteria:**
- [ ] DMG mounts successfully
- [ ] Application copies to Applications
- [ ] Application launches without security warnings
- [ ] Icon displays correctly

#### Test 4.3: Linux Installation
**Platform:** Ubuntu 22.04

**Steps:**
```bash
# AppImage
chmod +x iTechSmart-Suite-1.0.0.AppImage
./iTechSmart-Suite-1.0.0.AppImage

# Or DEB
sudo dpkg -i itechsmart-suite_1.0.0_amd64.deb
itechsmart-suite
```

**Pass Criteria:**
- [ ] AppImage runs without dependencies
- [ ] DEB installs successfully
- [ ] Application launches
- [ ] Desktop entry created

### Test Suite 5: License Activation

#### Test 5.1: First Launch
**Objective:** Test initial license activation

**Steps:**
1. Launch application for first time
2. Enter license key
3. Click "Activate"
4. Wait for validation

**Pass Criteria:**
- [ ] License activation screen appears
- [ ] License key input accepts valid format
- [ ] Activation succeeds
- [ ] Dashboard loads after activation
- [ ] License info displayed correctly

#### Test 5.2: Invalid License Key
**Objective:** Test error handling

**Steps:**
1. Enter invalid license key
2. Click "Activate"

**Pass Criteria:**
- [ ] Error message displayed
- [ ] Message is clear and helpful
- [ ] User can try again
- [ ] No application crash

#### Test 5.3: Offline Activation
**Objective:** Test offline mode

**Steps:**
1. Disconnect from internet
2. Launch application
3. Observe behavior

**Pass Criteria:**
- [ ] Application launches
- [ ] Cached license used
- [ ] Warning about offline mode shown
- [ ] Core functionality available

### Test Suite 6: Docker Integration

#### Test 6.1: Docker Detection
**Objective:** Verify Docker detection

**Steps:**
1. Ensure Docker is running
2. Launch application
3. Check Docker status

**Pass Criteria:**
- [ ] Docker detected automatically
- [ ] Docker version displayed
- [ ] No error messages

#### Test 6.2: Docker Not Installed
**Objective:** Test Docker installation guidance

**Steps:**
1. Stop Docker
2. Launch application
3. Follow installation prompts

**Pass Criteria:**
- [ ] Warning displayed
- [ ] Installation instructions clear
- [ ] Link to Docker download provided
- [ ] Application doesn't crash

#### Test 6.3: Product Start
**Objective:** Start a product container

**Steps:**
1. Select "iTechSmart Analytics"
2. Click "Start"
3. Wait for container to start
4. Click "Open"

**Pass Criteria:**
- [ ] Container starts successfully
- [ ] Status updates in real-time
- [ ] Product UI opens in browser
- [ ] Product is accessible

#### Test 6.4: Product Stop
**Objective:** Stop a running product

**Steps:**
1. Start a product
2. Click "Stop"
3. Confirm action

**Pass Criteria:**
- [ ] Container stops successfully
- [ ] Status updates immediately
- [ ] Resources released
- [ ] No errors

#### Test 6.5: Multiple Products
**Objective:** Run multiple products simultaneously

**Steps:**
1. Start 5 different products
2. Verify all are running
3. Stop all products

**Pass Criteria:**
- [ ] All products start successfully
- [ ] No port conflicts
- [ ] System remains responsive
- [ ] All products stop cleanly

### Test Suite 7: User Interface

#### Test 7.1: Dashboard
**Objective:** Test main dashboard

**Pass Criteria:**
- [ ] All products displayed
- [ ] Categories organized correctly
- [ ] Status indicators accurate
- [ ] Search functionality works
- [ ] Filters work correctly

#### Test 7.2: Product Cards
**Objective:** Test product card functionality

**Pass Criteria:**
- [ ] Product info displayed correctly
- [ ] Start/Stop buttons work
- [ ] Open button works
- [ ] Status updates in real-time
- [ ] Icons display correctly

#### Test 7.3: Settings
**Objective:** Test settings panel

**Pass Criteria:**
- [ ] License info displayed
- [ ] Docker settings accessible
- [ ] Update preferences work
- [ ] Changes persist
- [ ] Cancel button works

#### Test 7.4: System Tray
**Objective:** Test system tray integration

**Pass Criteria:**
- [ ] Tray icon appears
- [ ] Menu opens on click
- [ ] Quick actions work
- [ ] Minimize to tray works
- [ ] Restore from tray works

## Integration Testing

### Test Suite 8: End-to-End Workflows

#### Test 8.1: Complete User Journey
**Objective:** Test full user workflow

**Steps:**
1. Install application
2. Activate license
3. Start a product
4. Use the product
5. Stop the product
6. Close application

**Pass Criteria:**
- [ ] All steps complete successfully
- [ ] No errors encountered
- [ ] Data persists correctly
- [ ] Resources cleaned up

#### Test 8.2: License Server Integration
**Objective:** Test launcher-server communication

**Steps:**
1. Start license server
2. Launch desktop application
3. Activate license
4. Verify server receives validation
5. Check server logs

**Pass Criteria:**
- [ ] License validation succeeds
- [ ] Server logs show validation
- [ ] Machine ID recorded
- [ ] Usage tracked

#### Test 8.3: Multi-Machine Licensing
**Objective:** Test license machine binding

**Steps:**
1. Activate license on Machine A
2. Try to activate same license on Machine B
3. Verify behavior

**Pass Criteria:**
- [ ] Machine A activation succeeds
- [ ] Machine B activation fails (if limit reached)
- [ ] Error message clear
- [ ] Machine limit enforced

#### Test 8.4: License Expiration
**Objective:** Test expired license handling

**Steps:**
1. Use license with near expiration
2. Wait for expiration
3. Try to use products

**Pass Criteria:**
- [ ] Warning shown before expiration
- [ ] Products stop after expiration
- [ ] Clear renewal instructions
- [ ] No data loss

## Performance Testing

### Test Suite 9: Performance Benchmarks

#### Test 9.1: Application Startup
**Objective:** Measure startup time

**Metrics:**
- Cold start: < 3 seconds
- Warm start: < 1 second

**Pass Criteria:**
- [ ] Meets startup time targets
- [ ] UI responsive immediately
- [ ] No blocking operations

#### Test 9.2: License Validation Performance
**Objective:** Measure validation speed

**Steps:**
```bash
# Measure 100 validations
time for i in {1..100}; do
  curl -X POST http://localhost:3001/api/licenses/validate \
    -H "Content-Type: application/json" \
    -d '{"licenseKey":"'$LICENSE_KEY'","productId":"test"}'
done
```

**Metrics:**
- Average response time: < 200ms
- 95th percentile: < 500ms
- 99th percentile: < 1000ms

**Pass Criteria:**
- [ ] Meets response time targets
- [ ] No timeouts
- [ ] Consistent performance

#### Test 9.3: Resource Usage
**Objective:** Monitor resource consumption

**Metrics:**
- Idle CPU: < 5%
- Idle RAM: < 200MB
- Active CPU: < 20%
- Active RAM: < 500MB

**Pass Criteria:**
- [ ] Meets resource targets
- [ ] No memory leaks
- [ ] CPU usage reasonable

#### Test 9.4: Docker Operations
**Objective:** Measure Docker operation speed

**Metrics:**
- Container start: < 10 seconds
- Container stop: < 5 seconds
- Status check: < 1 second

**Pass Criteria:**
- [ ] Meets timing targets
- [ ] Operations don't block UI
- [ ] Progress indicators accurate

## Security Testing

### Test Suite 10: Security Validation

#### Test 10.1: SQL Injection
**Objective:** Test SQL injection prevention

**Steps:**
```bash
curl -X POST http://localhost:3001/api/licenses/validate \
  -H "Content-Type: application/json" \
  -d '{
    "licenseKey": "ITSM-TEST&quot;; DROP TABLE licenses; --",
    "productId": "test"
  }'
```

**Pass Criteria:**
- [ ] Request handled safely
- [ ] No database modification
- [ ] Error returned
- [ ] Logs show attempt

#### Test 10.2: XSS Prevention
**Objective:** Test XSS attack prevention

**Steps:**
1. Enter `<script>alert('XSS')</script>` in license key field
2. Submit form

**Pass Criteria:**
- [ ] Script not executed
- [ ] Input sanitized
- [ ] No security warning

#### Test 10.3: JWT Token Security
**Objective:** Test token handling

**Steps:**
1. Obtain valid JWT token
2. Modify token
3. Try to use modified token

**Pass Criteria:**
- [ ] Modified token rejected
- [ ] 401 Unauthorized returned
- [ ] No access granted

#### Test 10.4: Rate Limiting
**Objective:** Test rate limit enforcement

**Steps:**
```bash
# Rapid-fire requests
for i in {1..200}; do
  curl http://localhost:3001/api/licenses/validate \
    -H "Content-Type: application/json" \
    -d '{"licenseKey":"test"}' &
done
```

**Pass Criteria:**
- [ ] Rate limit enforced
- [ ] 429 status returned
- [ ] Service remains available
- [ ] Legitimate requests still work

## User Acceptance Testing

### Test Suite 11: User Experience

#### Test 11.1: First-Time User
**Objective:** Test new user experience

**Scenario:**
New user with no technical background

**Tasks:**
1. Install application
2. Activate license
3. Start first product
4. Access product UI

**Pass Criteria:**
- [ ] User completes all tasks
- [ ] No confusion
- [ ] No errors
- [ ] User satisfied

#### Test 11.2: Power User
**Objective:** Test advanced user workflows

**Scenario:**
Technical user managing multiple products

**Tasks:**
1. Start 10 products simultaneously
2. Monitor resource usage
3. Configure custom settings
4. Use keyboard shortcuts

**Pass Criteria:**
- [ ] All tasks complete efficiently
- [ ] Advanced features work
- [ ] Performance acceptable
- [ ] User satisfied

#### Test 11.3: Error Recovery
**Objective:** Test error handling UX

**Scenario:**
User encounters various errors

**Tasks:**
1. Handle invalid license
2. Recover from Docker failure
3. Deal with network issues
4. Resolve port conflicts

**Pass Criteria:**
- [ ] Error messages clear
- [ ] Recovery steps provided
- [ ] User can resolve issues
- [ ] No data loss

## Test Execution

### Test Environment Matrix

| Platform | OS Version | Docker | License Server | Status |
|----------|-----------|--------|----------------|--------|
| Windows | 10 Pro | Desktop 4.25 | Local | ⏳ |
| Windows | 11 Pro | Desktop 4.25 | Local | ⏳ |
| macOS | 13 Ventura (Intel) | Desktop 4.25 | Local | ⏳ |
| macOS | 14 Sonoma (M1) | Desktop 4.25 | Local | ⏳ |
| Ubuntu | 22.04 LTS | Engine 24.0 | Local | ⏳ |
| Ubuntu | 24.04 LTS | Engine 24.0 | Local | ⏳ |

### Test Execution Schedule

**Week 1: Core Functionality**
- Day 1-2: License Server API Testing
- Day 3-4: Desktop Launcher Installation
- Day 5: Docker Integration

**Week 2: Integration & Performance**
- Day 1-2: End-to-End Integration
- Day 3-4: Performance Testing
- Day 5: Security Testing

**Week 3: User Acceptance**
- Day 1-3: UAT with test users
- Day 4: Bug fixes
- Day 5: Final verification

### Bug Reporting

**Bug Report Template:**
```markdown
## Bug Report

**Title:** [Brief description]

**Severity:** Critical / High / Medium / Low

**Environment:**
- OS: [Windows/macOS/Linux version]
- Application Version: [1.0.0]
- Docker Version: [version]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Screenshots:**
[Attach screenshots]

**Logs:**
[Attach relevant logs]

**Additional Context:**
[Any other relevant information]
```

### Test Sign-Off

**Criteria for Release:**
- [ ] All critical bugs fixed
- [ ] 95%+ test pass rate
- [ ] Performance targets met
- [ ] Security audit passed
- [ ] UAT approved
- [ ] Documentation complete

## Support

For testing support:
- **GitHub Issues:** https://github.com/Iteksmart/iTechSmart/issues
- **Email:** testing@itechsmart.com
- **Slack:** #testing channel

---

**Document Version:** 1.0
**Last Updated:** November 16, 2025
**Status:** Ready for Testing