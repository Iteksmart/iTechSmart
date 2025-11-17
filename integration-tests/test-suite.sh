#!/bin/bash

# iTechSmart Suite - Integration Test Suite
# Tests all services and their integrations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Function to print test header
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Function to print test result
print_result() {
    local test_name=$1
    local result=$2
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✓ PASS${NC} - $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC} - $test_name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Function to test HTTP endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response_code" = "$expected_code" ]; then
        print_result "$name" "PASS"
        return 0
    else
        print_result "$name (Expected: $expected_code, Got: $response_code)" "FAIL"
        return 1
    fi
}

# Function to test JSON API endpoint
test_json_api() {
    local name=$1
    local url=$2
    local expected_field=$3
    
    local response=$(curl -s "$url" 2>/dev/null || echo "{}")
    
    if echo "$response" | grep -q "$expected_field"; then
        print_result "$name" "PASS"
        return 0
    else
        print_result "$name (Field '$expected_field' not found)" "FAIL"
        return 1
    fi
}

# Function to test Docker service
test_docker_service() {
    local name=$1
    local container=$2
    
    if docker ps | grep -q "$container"; then
        print_result "$name" "PASS"
        return 0
    else
        print_result "$name (Container not running)" "FAIL"
        return 1
    fi
}

# Main test execution
print_header "iTechSmart Suite - Integration Test Suite"

echo "Starting integration tests..."
echo "Test environment: Demo"
echo "Base URL: http://localhost"
echo ""

# Test 1: Docker Services
print_header "Test Suite 1: Docker Services"

test_docker_service "License Server Container" "itechsmart-license-demo"
test_docker_service "PostgreSQL Container" "itechsmart-demo-db"
test_docker_service "Nginx Proxy Container" "itechsmart-demo-proxy"
test_docker_service "Ninja Container" "itechsmart-ninja-demo"
test_docker_service "Supreme Container" "itechsmart-supreme-demo"
test_docker_service "Citadel Container" "itechsmart-citadel-demo"
test_docker_service "Copilot Container" "itechsmart-copilot-demo"

# Test 2: Health Endpoints
print_header "Test Suite 2: Health Endpoints"

test_endpoint "Nginx Proxy Health" "http://localhost/health"
test_endpoint "License Server Health" "http://localhost:3000/health"
test_endpoint "Ninja Health" "http://localhost:3001/health"
test_endpoint "Supreme Health" "http://localhost:3002/health"
test_endpoint "Citadel Health" "http://localhost:3003/health"
test_endpoint "Copilot Health" "http://localhost:3004/health"

# Test 3: Web Interfaces
print_header "Test Suite 3: Web Interfaces"

test_endpoint "Demo Landing Page" "http://localhost/"
test_endpoint "License Server UI" "http://localhost:3000/"
test_endpoint "Ninja UI" "http://localhost:3001/"
test_endpoint "Supreme UI" "http://localhost:3002/"
test_endpoint "Citadel UI" "http://localhost:3003/"
test_endpoint "Copilot UI" "http://localhost:3004/"

# Test 4: API Endpoints
print_header "Test Suite 4: API Endpoints"

test_json_api "License Server API" "http://localhost:3000/api/health" "status"
test_json_api "Ninja API" "http://localhost:3001/api/health" "status"
test_json_api "Supreme API" "http://localhost:3002/api/health" "status"
test_json_api "Citadel API" "http://localhost:3003/api/health" "status"
test_json_api "Copilot API" "http://localhost:3004/api/health" "status"

# Test 5: Database Connectivity
print_header "Test Suite 5: Database Connectivity"

# Test PostgreSQL connection
if docker exec itechsmart-demo-db psql -U demo -d license_demo -c "SELECT 1;" > /dev/null 2>&1; then
    print_result "PostgreSQL Connection" "PASS"
else
    print_result "PostgreSQL Connection" "FAIL"
fi

# Test License Server DB connection
if curl -s http://localhost:3000/api/health | grep -q "database"; then
    print_result "License Server DB Connection" "PASS"
else
    print_result "License Server DB Connection" "FAIL"
fi

# Test 6: Reverse Proxy Routing
print_header "Test Suite 6: Reverse Proxy Routing"

test_endpoint "Proxy to License Server" "http://localhost/license/health"
test_endpoint "Proxy to Ninja" "http://localhost/ninja/health"
test_endpoint "Proxy to Supreme" "http://localhost/supreme/health"
test_endpoint "Proxy to Citadel" "http://localhost/citadel/health"
test_endpoint "Proxy to Copilot" "http://localhost/copilot/health"

# Test 7: Authentication (if applicable)
print_header "Test Suite 7: Authentication"

# Test License Server authentication endpoint
test_endpoint "License Server Auth Endpoint" "http://localhost:3000/api/auth/login" "405"

# Test API key validation endpoint
test_endpoint "License Server Validation Endpoint" "http://localhost:3000/api/licenses/validate" "405"

# Test 8: Resource Usage
print_header "Test Suite 8: Resource Usage"

# Check CPU usage
cpu_usage=$(docker stats --no-stream --format "{{.CPUPerc}}" | head -1 | sed 's/%//')
if (( $(echo "$cpu_usage < 80" | bc -l) )); then
    print_result "CPU Usage (<80%)" "PASS"
else
    print_result "CPU Usage (${cpu_usage}% - High!)" "FAIL"
fi

# Check memory usage
mem_usage=$(docker stats --no-stream --format "{{.MemPerc}}" | head -1 | sed 's/%//')
if (( $(echo "$mem_usage < 80" | bc -l) )); then
    print_result "Memory Usage (<80%)" "PASS"
else
    print_result "Memory Usage (${mem_usage}% - High!)" "FAIL"
fi

# Test 9: Network Connectivity
print_header "Test Suite 9: Network Connectivity"

# Test inter-service communication
if docker exec itechsmart-ninja-demo curl -s http://license-server:3000/health > /dev/null 2>&1; then
    print_result "Ninja → License Server" "PASS"
else
    print_result "Ninja → License Server" "FAIL"
fi

if docker exec itechsmart-supreme-demo curl -s http://license-server:3000/health > /dev/null 2>&1; then
    print_result "Supreme → License Server" "PASS"
else
    print_result "Supreme → License Server" "FAIL"
fi

# Test 10: Logs and Errors
print_header "Test Suite 10: Logs and Errors"

# Check for errors in logs
error_count=$(docker-compose -f demo-environment/docker-compose.demo.yml logs --tail=100 2>&1 | grep -i "error" | wc -l)
if [ "$error_count" -lt 5 ]; then
    print_result "Error Count in Logs (<5)" "PASS"
else
    print_result "Error Count in Logs ($error_count - High!)" "FAIL"
fi

# Check for warnings in logs
warning_count=$(docker-compose -f demo-environment/docker-compose.demo.yml logs --tail=100 2>&1 | grep -i "warning" | wc -l)
if [ "$warning_count" -lt 10 ]; then
    print_result "Warning Count in Logs (<10)" "PASS"
else
    print_result "Warning Count in Logs ($warning_count - High!)" "FAIL"
fi

# Print summary
print_header "Test Summary"

echo "Total Tests: $TESTS_TOTAL"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}ALL TESTS PASSED! ✓${NC}"
    echo -e "${GREEN}========================================${NC}"
    exit 0
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}SOME TESTS FAILED! ✗${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi