#!/bin/bash

# Push and Monitor Build Script
# This script pushes changes to GitHub and monitors the build process

set -e

echo "================================================"
echo "iTechSmart Suite - Push and Monitor Builds"
echo "================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f ".github/workflows/build-all-products.yml" ]; then
    echo -e "${RED}Error: Not in iTechSmart repository root${NC}"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}Warning: You have uncommitted changes${NC}"
    echo "Please commit or stash them first"
    exit 1
fi

# Show what will be pushed
echo "Commits to be pushed:"
git log origin/main..HEAD --oneline
echo ""

# Confirm push
read -p "Push these commits to GitHub? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Push cancelled"
    exit 0
fi

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
if git push origin main; then
    echo -e "${GREEN}✓ Successfully pushed to GitHub${NC}"
else
    echo -e "${RED}✗ Failed to push to GitHub${NC}"
    echo "Please check your network connection and try again"
    exit 1
fi

echo ""
echo "Waiting 10 seconds for GitHub to process..."
sleep 10

# Ask if user wants to monitor builds
echo ""
read -p "Monitor build progress? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting build monitor..."
    echo "Press Ctrl+C to stop monitoring"
    echo ""
    python scripts/monitor_build.py --interval 30
else
    echo ""
    echo "You can monitor builds later with:"
    echo "  python scripts/monitor_build.py --interval 30"
    echo ""
    echo "Or check once with:"
    echo "  python scripts/monitor_build.py --once"
fi

echo ""
echo "================================================"
echo "Next Steps:"
echo "================================================"
echo "1. Monitor builds until all complete successfully"
echo "2. Run: ./scripts/prepare_release.sh 1.0.0"
echo "3. Follow DISTRIBUTION_GUIDE.md for distribution"
echo ""