#!/bin/bash

echo "🚀 Configuring All Remaining Products for Agent Integration..."
echo "=============================================================="

# Get all product directories
ALL_PRODUCTS=$(ls -d itechsmart-* 2>/dev/null)

# Already completed Tier 1 products
TIER1_COMPLETE=(
    "itechsmart-ninja"
    "itechsmart-enterprise"
    "itechsmart-supreme-plus"
    "itechsmart-citadel"
    "desktop-launcher"
)

# Already completed Tier 2 products
TIER2_COMPLETE=(
    "itechsmart-analytics"
    "itechsmart-copilot"
    "itechsmart-shield"
)

# Tier 2 products to complete
TIER2_REMAINING=(
    "itechsmart-sentinel"
    "itechsmart-devops"
)

CONFIGURED=0
SKIPPED=0

# Function to check if product is already completed
is_completed() {
    local product=$1
    for completed in "${TIER1_COMPLETE[@]}" "${TIER2_COMPLETE[@]}"; do
        if [ "$product" = "$completed" ]; then
            return 0
        fi
    done
    return 1
}

# Function to configure a product
configure_product() {
    local product=$1
    
    # Skip if already completed
    if is_completed "$product"; then
        echo "  ℹ $product already completed, skipping..."
        SKIPPED=$((SKIPPED + 1))
        return
    fi
    
    echo "📦 Configuring $product..."
    
    # Add .env.example if it doesn't exist
    if [ ! -f "$product/.env.example" ]; then
        cat > "$product/.env.example" << 'ENVEOF'
# License Server Integration
LICENSE_SERVER_URL=http://localhost:3000

# Add other environment variables as needed
ENVEOF
        echo "  ✓ Created .env.example"
    fi
    
    # Update README.md to mention agent integration
    if [ -f "$product/README.md" ]; then
        # Check if agent integration is already mentioned
        if ! grep -q "Agent Integration" "$product/README.md" 2>/dev/null; then
            # Add agent integration section
            cat >> "$product/README.md" << 'READMEEOF'

## 🤖 Agent Integration

This product integrates with the iTechSmart Agent monitoring system through the License Server.

### Configuration

Set the License Server URL in your environment:

```bash
LICENSE_SERVER_URL=http://localhost:3000
```

The product will automatically connect to the License Server to access agent data and monitoring capabilities.

READMEEOF
            echo "  ✓ Updated README.md"
        fi
    fi
    
    CONFIGURED=$((CONFIGURED + 1))
}

# Configure all products
for product in $ALL_PRODUCTS; do
    if [ -d "$product" ]; then
        configure_product "$product"
    fi
done

echo ""
echo "✅ Configuration Complete!"
echo "   Configured: $CONFIGURED products"
echo "   Skipped: $SKIPPED products (already completed)"
echo ""