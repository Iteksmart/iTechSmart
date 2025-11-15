#!/bin/bash

################################################################################
#                                                                              #
#           iTechSmart Enterprise - Package and Deploy Script                 #
#                                                                              #
#     This script packages everything into a distributable ZIP file            #
#                                                                              #
################################################################################

set -e

VERSION="1.0.0"
PACKAGE_NAME="itechsmart-enterprise-v${VERSION}"
OUTPUT_DIR="dist"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                                ║${NC}"
echo -e "${CYAN}║     iTechSmart Enterprise - Package Creation                   ║${NC}"
echo -e "${CYAN}║                                                                ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Create output directory
echo -e "${BLUE}Creating output directory...${NC}"
mkdir -p "$OUTPUT_DIR"

# Create temporary packaging directory
TEMP_DIR=$(mktemp -d)
PACKAGE_DIR="$TEMP_DIR/$PACKAGE_NAME"
mkdir -p "$PACKAGE_DIR"

echo -e "${BLUE}Copying files to package directory...${NC}"

# Copy all necessary files
cp -r backend "$PACKAGE_DIR/"
cp -r frontend "$PACKAGE_DIR/"
cp -r infrastructure "$PACKAGE_DIR/"
cp -r integrations "$PACKAGE_DIR/"
cp -r monitoring "$PACKAGE_DIR/"
cp -r scripts "$PACKAGE_DIR/"
cp -r docs "$PACKAGE_DIR/"

# Copy root files
cp README.md "$PACKAGE_DIR/"
cp IMPLEMENTATION_GUIDE.md "$PACKAGE_DIR/"
cp docker-compose.yml "$PACKAGE_DIR/"
cp setup.sh "$PACKAGE_DIR/"
cp .env.example "$PACKAGE_DIR/" 2>/dev/null || touch "$PACKAGE_DIR/.env.example"

# Make scripts executable
chmod +x "$PACKAGE_DIR/setup.sh"
chmod +x "$PACKAGE_DIR"/scripts/**/*.sh 2>/dev/null || true

# Create ZIP archive
echo -e "${BLUE}Creating ZIP archive...${NC}"
cd "$TEMP_DIR"
zip -r "$PACKAGE_NAME.zip" "$PACKAGE_NAME" -q

# Move to output directory
mv "$PACKAGE_NAME.zip" "$OLDPWD/$OUTPUT_DIR/"

# Cleanup
cd "$OLDPWD"
rm -rf "$TEMP_DIR"

# Calculate size
SIZE=$(du -h "$OUTPUT_DIR/$PACKAGE_NAME.zip" | cut -f1)

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║     ✅ Package Created Successfully!                           ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Package Details:${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}File:${NC}     $OUTPUT_DIR/$PACKAGE_NAME.zip"
echo -e "${GREEN}Size:${NC}     $SIZE"
echo -e "${GREEN}Version:${NC}  $VERSION"
echo ""
echo -e "${CYAN}To deploy:${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "1. Extract: ${GREEN}unzip $OUTPUT_DIR/$PACKAGE_NAME.zip${NC}"
echo -e "2. Navigate: ${GREEN}cd $PACKAGE_NAME${NC}"
echo -e "3. Run setup: ${GREEN}./setup.sh${NC}"
echo ""
echo -e "${GREEN}Done! 🚀${NC}"
echo ""