#!/bin/bash
# Test all iTechSmart products

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

# All 35 products
PRODUCTS=(
    "itechsmart-enterprise"
    "itechsmart-ninja"
    "itechsmart-analytics"
    "itechsmart-supreme-plus"
    "itechsmart-hl7"
    "prooflink"
    "passport"
    "itechsmart-impactos"
    "legalai-pro"
    "itechsmart-dataflow"
    "itechsmart-pulse"
    "itechsmart-connect"
    "itechsmart-vault"
    "itechsmart-notify"
    "itechsmart-ledger"
    "itechsmart-copilot"
    "itechsmart-shield"
    "itechsmart-workflow"
    "itechsmart-marketplace"
    "itechsmart-cloud"
    "itechsmart-devops"
    "itechsmart-mobile"
    "itechsmart-ai"
    "itechsmart-compliance"
    "itechsmart-data-platform"
    "itechsmart-customer-success"
    "itechsmart-port-manager"
    "itechsmart-mdm-agent"
    "itechsmart-qaqc"
    "itechsmart-thinktank"
    "itechsmart-sentinel"
    "itechsmart-forge"
    "itechsmart-sandbox"
    "itechsmart-citadel"
    "itechsmart-observatory"
)

# Test results
PASSED=0
FAILED=0
TOTAL=${#PRODUCTS[@]}

# Create test report
REPORT_FILE="test-report-$(date +%Y%m%d-%H%M%S).txt"
echo "iTechSmart Suite - Product Test Report" > $REPORT_FILE
echo "Generated: $(date)" >> $REPORT_FILE
echo "========================================" >> $REPORT_FILE
echo "" >> $REPORT_FILE

print_info "Testing all $TOTAL products..."
echo ""

for PRODUCT in "${PRODUCTS[@]}"; do
    print_test "Testing $PRODUCT..."
    
    # Test backend image exists
    BACKEND_IMAGE="ghcr.io/iteksmart/${PRODUCT}-backend:main"
    FRONTEND_IMAGE="ghcr.io/iteksmart/${PRODUCT}-frontend:main"
    
    BACKEND_EXISTS=$(docker manifest inspect $BACKEND_IMAGE > /dev/null 2>&1 && echo "yes" || echo "no")
    FRONTEND_EXISTS=$(docker manifest inspect $FRONTEND_IMAGE > /dev/null 2>&1 && echo "yes" || echo "no")
    
    if [ "$BACKEND_EXISTS" = "yes" ] && [ "$FRONTEND_EXISTS" = "yes" ]; then
        print_success "✅ $PRODUCT - Images exist"
        echo "✅ PASS - $PRODUCT" >> $REPORT_FILE
        ((PASSED++))
    else
        print_error "❌ $PRODUCT - Images missing"
        echo "❌ FAIL - $PRODUCT" >> $REPORT_FILE
        if [ "$BACKEND_EXISTS" = "no" ]; then
            echo "  - Backend image not found" >> $REPORT_FILE
        fi
        if [ "$FRONTEND_EXISTS" = "no" ]; then
            echo "  - Frontend image not found" >> $REPORT_FILE
        fi
        ((FAILED++))
    fi
done

# Summary
echo "" >> $REPORT_FILE
echo "========================================" >> $REPORT_FILE
echo "SUMMARY" >> $REPORT_FILE
echo "========================================" >> $REPORT_FILE
echo "Total Products: $TOTAL" >> $REPORT_FILE
echo "Passed: $PASSED" >> $REPORT_FILE
echo "Failed: $FAILED" >> $REPORT_FILE
echo "Success Rate: $(( PASSED * 100 / TOTAL ))%" >> $REPORT_FILE

echo ""
print_info "=========================================="
print_info "TEST SUMMARY"
print_info "=========================================="
print_info "Total Products: $TOTAL"
print_success "Passed: $PASSED"
if [ $FAILED -gt 0 ]; then
    print_error "Failed: $FAILED"
else
    print_success "Failed: $FAILED"
fi
print_info "Success Rate: $(( PASSED * 100 / TOTAL ))%"
echo ""
print_info "Full report saved to: $REPORT_FILE"
echo ""

if [ $FAILED -eq 0 ]; then
    print_success "🎉 All products passed!"
    exit 0
else
    print_error "⚠️  Some products failed"
    exit 1
fi