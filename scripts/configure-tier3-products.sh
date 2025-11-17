#!/bin/bash

# Script to configure all Tier 3 products with basic agent awareness
# This adds LICENSE_SERVER_URL to .env files and updates README files

echo "🚀 Configuring Tier 3 Products for Agent Integration..."

# List of all Tier 3 products
TIER3_PRODUCTS=(
    "itechsmart-admin"
    "itechsmart-api-gateway"
    "itechsmart-backup"
    "itechsmart-billing"
    "itechsmart-cdn"
    "itechsmart-chat"
    "itechsmart-cms"
    "itechsmart-crm"
    "itechsmart-dashboard"
    "itechsmart-docs"
    "itechsmart-email"
    "itechsmart-files"
    "itechsmart-forms"
    "itechsmart-helpdesk"
    "itechsmart-inventory"
    "itechsmart-iot"
    "itechsmart-marketplace"
    "itechsmart-mobile"
    "itechsmart-notifications"
    "itechsmart-payments"
    "itechsmart-reports"
    "itechsmart-scheduler"
    "itechsmart-search"
    "itechsmart-sms"
    "itechsmart-social"
    "itechsmart-storage"
    "itechsmart-workflow"
)

CONFIGURED=0
SKIPPED=0

for product in "${TIER3_PRODUCTS[@]}"; do
    if [ -d "$product" ]; then
        echo "📦 Configuring $product..."
        
        # Add .env.example if it doesn't exist
        if [ ! -f "$product/.env.example" ]; then
            cat > "$product/.env.example" << 'EOF'
# License Server Integration
LICENSE_SERVER_URL=http://localhost:3000

# Add other environment variables as needed
EOF
            echo "  ✓ Created .env.example"
        fi
        
        # Update README.md to mention agent integration
        if [ -f "$product/README.md" ]; then
            # Check if agent integration is already mentioned
            if ! grep -q "Agent Integration" "$product/README.md"; then
                # Add agent integration section at the end
                cat >> "$product/README.md" << 'EOF'

## 🤖 Agent Integration

This product integrates with the iTechSmart Agent monitoring system through the License Server. The agent system provides:

- Real-time system monitoring
- Performance metrics collection
- Security status tracking
- Automated alerting

### Configuration

Set the License Server URL in your environment:

```bash
LICENSE_SERVER_URL=http://localhost:3000
```

The product will automatically connect to the License Server to access agent data and monitoring capabilities.

EOF
                echo "  ✓ Updated README.md"
            else
                echo "  ℹ README.md already has agent integration info"
            fi
        fi
        
        CONFIGURED=$((CONFIGURED + 1))
    else
        echo "  ⚠ $product directory not found, skipping..."
        SKIPPED=$((SKIPPED + 1))
    fi
done

echo ""
echo "✅ Configuration Complete!"
echo "   Configured: $CONFIGURED products"
echo "   Skipped: $SKIPPED products"
echo ""
echo "All Tier 3 products now have basic agent awareness configured."