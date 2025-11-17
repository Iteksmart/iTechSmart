#!/bin/bash

# Configure all products with agent integration awareness

echo "🚀 Configuring All Products for Agent Integration..."
echo ""

CONFIGURED=0
ALREADY_CONFIGURED=0

for product_dir in itechsmart-*; do
    if [ -d "$product_dir" ]; then
        echo "📦 Processing $product_dir..."
        
        # Add .env.example if it doesn't exist
        if [ ! -f "$product_dir/.env.example" ]; then
            cat > "$product_dir/.env.example" << 'EOF'
# License Server Integration
LICENSE_SERVER_URL=http://localhost:3000

# Add other environment variables as needed
EOF
            echo "  ✓ Created .env.example"
            CONFIGURED=$((CONFIGURED + 1))
        else
            # Check if LICENSE_SERVER_URL is in .env.example
            if ! grep -q "LICENSE_SERVER_URL" "$product_dir/.env.example"; then
                echo "" >> "$product_dir/.env.example"
                echo "# License Server Integration" >> "$product_dir/.env.example"
                echo "LICENSE_SERVER_URL=http://localhost:3000" >> "$product_dir/.env.example"
                echo "  ✓ Added LICENSE_SERVER_URL to .env.example"
                CONFIGURED=$((CONFIGURED + 1))
            else
                echo "  ℹ .env.example already configured"
                ALREADY_CONFIGURED=$((ALREADY_CONFIGURED + 1))
            fi
        fi
        
        # Update README.md to mention agent integration
        if [ -f "$product_dir/README.md" ]; then
            if ! grep -q "Agent Integration" "$product_dir/README.md"; then
                cat >> "$product_dir/README.md" << 'EOF'

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
        
        echo ""
    fi
done

echo "✅ Configuration Complete!"
echo "   Newly configured: $CONFIGURED products"
echo "   Already configured: $ALREADY_CONFIGURED products"
echo "   Total: $((CONFIGURED + ALREADY_CONFIGURED)) products"
echo ""