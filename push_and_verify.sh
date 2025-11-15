#!/bin/bash

# Push and Verify Build Script
# This script pushes changes to GitHub and monitors the build status

set -e

echo "=========================================="
echo "iTechSmart Suite - Push and Verify Build"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -d ".git" ]; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Show current status
echo "Current Git Status:"
git status --short
echo ""

# Show commits to be pushed
echo "Commits to be pushed:"
git log origin/main..HEAD --oneline
echo ""

# Confirm push
read -p "Push these changes to GitHub? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Push cancelled"
    exit 0
fi

# Push changes
echo ""
echo "Pushing to GitHub..."
if git push origin main; then
    echo "✅ Push successful!"
else
    echo "❌ Push failed. Please check your network connection and try again."
    exit 1
fi

echo ""
echo "Waiting 10 seconds for GitHub Actions to start..."
sleep 10

# Monitor build
echo ""
echo "Monitoring build status..."
echo "You can also view the build at:"
echo "https://github.com/Iteksmart/iTechSmart/actions"
echo ""

# Check if gh CLI is available
if command -v gh &> /dev/null; then
    echo "Fetching latest workflow run..."
    gh run list --workflow=docker-build.yml --limit 1
    
    echo ""
    read -p "Watch build in real-time? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Get the latest run ID
        RUN_ID=$(gh run list --workflow=docker-build.yml --limit 1 --json databaseId --jq '.[0].databaseId')
        echo "Watching run $RUN_ID..."
        gh run watch $RUN_ID
    fi
else
    echo "GitHub CLI (gh) not found. Install it to monitor builds automatically."
    echo "Visit: https://cli.github.com/"
fi

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo "1. Monitor the build at: https://github.com/Iteksmart/iTechSmart/actions"
echo "2. Verify all 6 products build successfully"
echo "3. Check Docker images at: https://github.com/orgs/Iteksmart/packages"
echo ""
echo "Products being built:"
echo "  - itechsmart-hl7"
echo "  - itechsmart-impactos"
echo "  - itechsmart-enterprise"
echo "  - itechsmart-ninja"
echo "  - passport"
echo "  - prooflink"
echo ""
echo "All fixes have been applied. Builds should succeed! 🎉"