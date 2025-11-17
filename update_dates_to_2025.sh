#!/bin/bash

# Script to update all dates from 2024 to 2025
# This ensures all documentation reflects the correct year

echo "=========================================="
echo "Updating all dates from 2024 to 2025"
echo "=========================================="
echo ""

# Counter for files updated
FILES_UPDATED=0

# Find and update all markdown files
echo "Updating Markdown files..."
find . -type f -name "*.md" -not -path "./.git/*" -not -path "./node_modules/*" | while read file; do
    if grep -q "2024" "$file"; then
        sed -i 's/2024/2025/g' "$file"
        echo "✓ Updated: $file"
        FILES_UPDATED=$((FILES_UPDATED + 1))
    fi
done

# Find and update JSON files
echo ""
echo "Updating JSON files..."
find . -type f -name "*.json" -not -path "./.git/*" -not -path "./node_modules/*" | while read file; do
    if grep -q "2024" "$file"; then
        sed -i 's/2024/2025/g' "$file"
        echo "✓ Updated: $file"
        FILES_UPDATED=$((FILES_UPDATED + 1))
    fi
done

# Find and update YAML files
echo ""
echo "Updating YAML files..."
find . -type f \( -name "*.yml" -o -name "*.yaml" \) -not -path "./.git/*" -not -path "./node_modules/*" | while read file; do
    if grep -q "2024" "$file"; then
        sed -i 's/2024/2025/g' "$file"
        echo "✓ Updated: $file"
        FILES_UPDATED=$((FILES_UPDATED + 1))
    fi
done

# Find and update HTML files
echo ""
echo "Updating HTML files..."
find . -type f -name "*.html" -not -path "./.git/*" -not -path "./node_modules/*" | while read file; do
    if grep -q "2024" "$file"; then
        sed -i 's/2024/2025/g' "$file"
        echo "✓ Updated: $file"
        FILES_UPDATED=$((FILES_UPDATED + 1))
    fi
done

# Find and update package.json files
echo ""
echo "Updating package.json files..."
find . -type f -name "package.json" -not -path "./.git/*" -not -path "./node_modules/*" | while read file; do
    if grep -q "2024" "$file"; then
        sed -i 's/2024/2025/g' "$file"
        echo "✓ Updated: $file"
        FILES_UPDATED=$((FILES_UPDATED + 1))
    fi
done

echo ""
echo "=========================================="
echo "Update Complete!"
echo "=========================================="
echo ""
echo "All dates have been updated from 2024 to 2025"
echo ""
echo "Next steps:"
echo "1. Review changes: git diff"
echo "2. Commit changes: git add -A && git commit -m 'Update all dates to 2025'"
echo "3. Push changes: git push origin main"
echo ""