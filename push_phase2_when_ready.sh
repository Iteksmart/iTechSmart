#!/bin/bash

# Script to push Phase 2 changes when network connectivity is restored
# Run this script when you can connect to GitHub again

echo "=========================================="
echo "Phase 2 - Pushing Next.js Dockerfile Fixes"
echo "=========================================="
echo ""

cd /workspace/iTechSmart || exit 1

echo "Current commit status:"
git log --oneline -1
echo ""

echo "Files changed:"
git show --stat HEAD
echo ""

echo "Attempting to push to GitHub..."
if git push origin main; then
    echo ""
    echo "✅ SUCCESS! Phase 2 changes pushed to GitHub"
    echo ""
    echo "Next steps:"
    echo "1. Trigger a new build: gh workflow run docker-build.yml"
    echo "2. Monitor the build: gh run list --workflow=docker-build.yml --limit 1"
    echo "3. Wait for build to complete (~10-15 minutes)"
    echo "4. Check results and proceed to Phase 3 if needed"
    echo ""
else
    echo ""
    echo "❌ FAILED to push. Network issues persist."
    echo "Please try again later or check your network connection."
    echo ""
    exit 1
fi