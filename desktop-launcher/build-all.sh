#!/bin/bash

# iTechSmart Suite Desktop Launcher - Build Script
# This script builds installers for all platforms

set -e

echo "=========================================="
echo "iTechSmart Suite Desktop Launcher Builder"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

# Build the application
echo -e "${GREEN}Building application...${NC}"
npm run build

# Create release directory if it doesn't exist
mkdir -p release

echo ""
echo "=========================================="
echo "Building Installers"
echo "=========================================="
echo ""

# Build Linux packages
echo -e "${GREEN}Building Linux packages...${NC}"
npm run package:linux

echo ""
echo -e "${GREEN}✓ Linux AppImage built successfully!${NC}"

# Note about Windows and macOS builds
echo ""
echo "=========================================="
echo "Build Notes"
echo "=========================================="
echo ""
echo -e "${YELLOW}Windows Build:${NC}"
echo "  - Requires Wine on Linux systems"
echo "  - Run: npm run package:win (with Wine installed)"
echo "  - Or build on Windows natively"
echo ""
echo -e "${YELLOW}macOS Build:${NC}"
echo "  - Requires macOS system"
echo "  - Run: npm run package:mac (on macOS)"
echo ""

# List built files
echo "=========================================="
echo "Built Files"
echo "=========================================="
echo ""
ls -lh release/*.AppImage 2>/dev/null || echo "No AppImage found"
ls -lh release/*.deb 2>/dev/null || echo "No .deb found"
ls -lh release/*.rpm 2>/dev/null || echo "No .rpm found"
ls -lh release/*.exe 2>/dev/null || echo "No .exe found"
ls -lh release/*.dmg 2>/dev/null || echo "No .dmg found"

echo ""
echo -e "${GREEN}Build process completed!${NC}"
echo ""