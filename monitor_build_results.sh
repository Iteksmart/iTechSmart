#!/bin/bash

# Script to monitor build results after Phase 2 & 3 fixes

echo "=========================================="
echo "Phase 2 & 3 Build Monitor"
echo "=========================================="
echo ""

cd /workspace/iTechSmart || exit 1

BUILD_ID="19400434716"

echo "Monitoring build: $BUILD_ID"
echo ""

# Check current status
echo "Current status:"
gh run list --workflow=docker-build.yml --limit 1
echo ""

# Wait for build to complete
echo "Waiting for build to complete..."
echo "(This may take 10-15 minutes)"
echo ""

# Check status every 30 seconds
while true; do
    STATUS=$(gh run view $BUILD_ID --json status --jq '.status')
    
    if [ "$STATUS" = "completed" ]; then
        echo ""
        echo "✅ Build completed!"
        echo ""
        
        # Get conclusion
        CONCLUSION=$(gh run view $BUILD_ID --json conclusion --jq '.conclusion')
        
        if [ "$CONCLUSION" = "success" ]; then
            echo "🎉 BUILD SUCCESS!"
            echo ""
            echo "Fetching results..."
            gh run view $BUILD_ID
            echo ""
            echo "Next steps:"
            echo "1. Review build logs: gh run view $BUILD_ID --log"
            echo "2. Check published images: gh api /orgs/Iteksmart/packages?package_type=container"
            echo "3. Verify all 34 products built successfully"
            echo ""
        else
            echo "❌ Build failed with conclusion: $CONCLUSION"
            echo ""
            echo "Fetching failure logs..."
            gh run view $BUILD_ID --log-failed
            echo ""
        fi
        
        break
    else
        echo -n "."
        sleep 30
    fi
done