#!/bin/bash

# iTechSmart Suite Desktop Launcher - macOS Build Script
# This script must be run on a macOS system

set -e

echo "=========================================="
echo "iTechSmart Suite - macOS Build Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}ERROR: This script must be run on macOS!${NC}"
    echo "Current OS: $OSTYPE"
    echo ""
    echo "To build macOS installers, you need:"
    echo "  1. A macOS system (macOS 10.13 or later)"
    echo "  2. Xcode Command Line Tools installed"
    echo "  3. Node.js 20.x installed"
    echo ""
    exit 1
fi

# Check if Xcode Command Line Tools are installed
if ! xcode-select -p &> /dev/null; then
    echo -e "${RED}ERROR: Xcode Command Line Tools not installed!${NC}"
    echo ""
    echo "Install with: xcode-select --install"
    echo ""
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}ERROR: Node.js not installed!${NC}"
    echo ""
    echo "Install Node.js 20.x from: https://nodejs.org/"
    echo ""
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo -e "${YELLOW}WARNING: Node.js version should be 20.x or higher${NC}"
    echo "Current version: $(node -v)"
    echo ""
fi

echo -e "${GREEN}✓ Running on macOS${NC}"
echo -e "${GREEN}✓ Xcode Command Line Tools installed${NC}"
echo -e "${GREEN}✓ Node.js installed: $(node -v)${NC}"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
    echo ""
fi

# Build the application
echo -e "${GREEN}Building application...${NC}"
npm run build
echo ""

# Create release directory if it doesn't exist
mkdir -p release

echo ""
echo "=========================================="
echo "Building macOS Installers"
echo "=========================================="
echo ""

# Build macOS packages
echo -e "${GREEN}Building macOS DMG and PKG installers...${NC}"
echo "This may take several minutes..."
echo ""

npm run package:mac

echo ""
echo -e "${GREEN}✓ macOS build completed successfully!${NC}"
echo ""

# List built files
echo "=========================================="
echo "Built Files"
echo "=========================================="
echo ""
ls -lh release/*.dmg 2>/dev/null || echo "No .dmg found"
ls -lh release/*.pkg 2>/dev/null || echo "No .pkg found"
ls -lh release/*.zip 2>/dev/null || echo "No .zip found"

echo ""
echo "=========================================="
echo "Build Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}macOS installers have been built successfully!${NC}"
echo ""
echo "Next steps:"
echo "  1. Test the installers on macOS"
echo "  2. Sign the installers (optional, for distribution)"
echo "  3. Notarize with Apple (optional, for distribution)"
echo "  4. Upload to GitHub releases"
echo ""
echo -e "${GREEN}Build process completed!${NC}"
echo ""