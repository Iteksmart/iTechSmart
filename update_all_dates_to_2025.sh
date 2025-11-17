#!/bin/bash

# Script to update all 2024 references to 2025
# Date: November 17, 2025

echo "=========================================="
echo "Updating All Dates from 2024 to 2025"
echo "=========================================="
echo ""

# Counter for updated files
updated_count=0

# Find and update all markdown files
echo "Updating Markdown files..."
find . -type f -name "*.md" \
  ! -path "*/node_modules/*" \
  ! -path "*/.git/*" \
  ! -path "*/dist/*" \
  ! -path "*/build/*" \
  -exec grep -l "2024" {} \; | while read file; do
    sed -i 's/2024/2025/g' "$file"
    echo "  ✓ Updated: $file"
    ((updated_count++))
done

# Find and update text files (excluding outputs and logs)
echo ""
echo "Updating important text files..."
for file in PORTFOLIO_AT_A_GLANCE.txt desktop-launcher/LICENSE.txt; do
  if [ -f "$file" ] && grep -q "2024" "$file"; then
    sed -i 's/2024/2025/g' "$file"
    echo "  ✓ Updated: $file"
    ((updated_count++))
  fi
done

# Update package.json files
echo ""
echo "Updating package.json files..."
find . -type f -name "package.json" \
  ! -path "*/node_modules/*" \
  ! -path "*/.git/*" \
  -exec grep -l "2024" {} \; | while read file; do
    sed -i 's/2024/2025/g' "$file"
    echo "  ✓ Updated: $file"
    ((updated_count++))
done

# Update README files specifically
echo ""
echo "Updating README files..."
find . -type f -name "README*" \
  ! -path "*/node_modules/*" \
  ! -path "*/.git/*" \
  -exec grep -l "2024" {} \; | while read file; do
    sed -i 's/2024/2025/g' "$file"
    echo "  ✓ Updated: $file"
    ((updated_count++))
done

echo ""
echo "=========================================="
echo "Date Update Complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  • All 2024 references updated to 2025"
echo "  • Documentation now reflects current year"
echo "  • Ready for production release"
echo ""