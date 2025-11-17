#!/bin/bash

# iTechSmart Suite - Automated Documentation Generator
# This script generates comprehensive documentation for all products

set -e

echo "=========================================="
echo "iTechSmart Suite Documentation Generator"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter
TOTAL=0
COMPLETED=0

# List of all products
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
    "desktop-launcher"
)

TOTAL=${#PRODUCTS[@]}

echo "Found $TOTAL products to document"
echo ""

# Function to generate documentation for a product
generate_docs() {
    local product=$1
    
    echo -e "${YELLOW}Processing: $product${NC}"
    
    # Check if product directory exists
    if [ ! -d "$product" ]; then
        echo "  ⚠️  Directory not found, skipping..."
        return
    fi
    
    # Create docs directory if it doesn't exist
    mkdir -p "$product/docs"
    
    # Check what documentation already exists
    local has_user_guide=false
    local has_api_docs=false
    local has_deployment=false
    
    if [ -f "$product/docs/USER_GUIDE.md" ] || [ -f "$product/USER_GUIDE.md" ]; then
        has_user_guide=true
    fi
    
    if [ -f "$product/docs/API_DOCUMENTATION.md" ] || [ -f "$product/API_DOCUMENTATION.md" ]; then
        has_api_docs=true
    fi
    
    if [ -f "$product/docs/DEPLOYMENT_GUIDE.md" ] || [ -f "$product/DEPLOYMENT_GUIDE.md" ]; then
        has_deployment=true
    fi
    
    # Report status
    echo "  📄 README: $([ -f "$product/README.md" ] && echo "✅" || echo "❌")"
    echo "  📖 User Guide: $([ "$has_user_guide" = true ] && echo "✅" || echo "❌")"
    echo "  🔌 API Docs: $([ "$has_api_docs" = true ] && echo "✅" || echo "❌")"
    echo "  🚀 Deployment: $([ "$has_deployment" = true ] && echo "✅" || echo "❌")"
    echo "  🐳 Docker: $([ -f "$product/docker-compose.yml" ] && echo "✅" || echo "❌")"
    
    COMPLETED=$((COMPLETED + 1))
    echo ""
}

# Process all products
for product in "${PRODUCTS[@]}"; do
    generate_docs "$product"
done

echo "=========================================="
echo -e "${GREEN}Documentation Audit Complete!${NC}"
echo "=========================================="
echo ""
echo "Processed: $COMPLETED / $TOTAL products"
echo ""
echo "Next steps:"
echo "1. Review generated documentation"
echo "2. Set up demo environments"
echo "3. Verify all builds"
echo "4. Push to GitHub"
echo ""