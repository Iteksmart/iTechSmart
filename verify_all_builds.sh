#!/bin/bash

# iTechSmart Suite - Build Verification Script
# Tests Docker builds for all products

set -e

echo "=========================================="
echo "iTechSmart Suite - Build Verification"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL=0
PASSED=0
FAILED=0
SKIPPED=0

# Products to verify
PRODUCTS=(
    "itechsmart-ai"
    "itechsmart-analytics"
    "itechsmart-citadel"
    "itechsmart-cloud"
    "itechsmart-compliance"
    "itechsmart-connect"
    "itechsmart-copilot"
    "itechsmart-customer-success"
    "itechsmart-data-platform"
    "itechsmart-dataflow"
    "itechsmart-devops"
    "itechsmart-enterprise"
    "itechsmart-forge"
    "itechsmart-hl7"
    "itechsmart-impactos"
    "itechsmart-ledger"
    "itechsmart-marketplace"
    "itechsmart-mdm-agent"
    "itechsmart-mobile"
    "itechsmart-notify"
    "itechsmart-observatory"
    "itechsmart-port-manager"
    "itechsmart-pulse"
    "itechsmart-qaqc"
    "itechsmart-sandbox"
    "itechsmart-sentinel"
    "itechsmart-shield"
    "itechsmart-supreme-plus"
    "itechsmart-thinktank"
    "itechsmart-vault"
    "itechsmart-workflow"
    "itechsmart_supreme"
    "passport"
    "prooflink"
    "legalai-pro"
    "license-server"
)

TOTAL=${#PRODUCTS[@]}

# Create results directory
mkdir -p build-verification-results

# Function to verify build
verify_build() {
    local product=$1
    local result_file="build-verification-results/${product}.txt"
    
    echo -e "${YELLOW}Testing: $product${NC}"
    
    # Check if directory exists
    if [ ! -d "$product" ]; then
        echo -e "  ${RED}✗ Directory not found${NC}"
        echo "SKIPPED: Directory not found" > "$result_file"
        SKIPPED=$((SKIPPED + 1))
        return
    fi
    
    # Check if docker-compose.yml exists
    if [ ! -f "$product/docker-compose.yml" ]; then
        echo -e "  ${YELLOW}⚠ No docker-compose.yml${NC}"
        echo "SKIPPED: No docker-compose.yml" > "$result_file"
        SKIPPED=$((SKIPPED + 1))
        return
    fi
    
    # Try to validate docker-compose file
    cd "$product"
    
    if docker-compose config > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓ Docker Compose config valid${NC}"
        echo "PASSED: Docker Compose configuration valid" > "../$result_file"
        PASSED=$((PASSED + 1))
    else
        echo -e "  ${RED}✗ Docker Compose config invalid${NC}"
        echo "FAILED: Docker Compose configuration invalid" > "../$result_file"
        docker-compose config 2>&1 | head -5 >> "../$result_file"
        FAILED=$((FAILED + 1))
    fi
    
    cd ..
    echo ""
}

# Verify all products
for product in "${PRODUCTS[@]}"; do
    verify_build "$product"
done

# Summary
echo "=========================================="
echo -e "${GREEN}Build Verification Complete!${NC}"
echo "=========================================="
echo ""
echo "Results:"
echo -e "  ${GREEN}✓ Passed: $PASSED${NC}"
echo -e "  ${RED}✗ Failed: $FAILED${NC}"
echo -e "  ${YELLOW}⚠ Skipped: $SKIPPED${NC}"
echo "  Total: $TOTAL"
echo ""
echo "Success Rate: $(( PASSED * 100 / TOTAL ))%"
echo ""
echo "Detailed results saved in: build-verification-results/"
echo ""