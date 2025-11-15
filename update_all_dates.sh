#!/bin/bash

echo "Updating all dates to iTechSmart launch date: August 8, 2025"
echo "================================================================"

# Date patterns to replace
declare -A DATE_PATTERNS=(
    ["2024"]="2025"
    ["December 2024"]="August 2025"
    ["December 13, 2024"]="August 8, 2025"
    ["Nov 2024"]="August 2025"
    ["October 2024"]="August 2025"
    ["September 2024"]="August 2025"
)

# Find all markdown files
find /workspace -type f -name "*.md" -not -path "*/node_modules/*" -not -path "*/.git/*" | while read file; do
    # Update copyright years
    sed -i 's/Copyright © 2024/Copyright © 2025/g' "$file"
    sed -i 's/©2024/©2025/g' "$file"
    
    # Update date references
    sed -i 's/December 13, 2024/August 8, 2025/g' "$file"
    sed -i 's/December 2024/August 2025/g' "$file"
    sed -i 's/Nov 2024/August 2025/g' "$file"
    sed -i 's/October 2024/August 2025/g' "$file"
    sed -i 's/September 2024/August 2025/g' "$file"
    
    # Update version dates
    sed -i 's/Date:\*\* December/Date:** August/g' "$file"
    sed -i 's/\*\*Date:\*\* December/\*\*Date:\*\* August/g' "$file"
done

# Update HTML files
find /workspace -type f -name "*.html" -not -path "*/node_modules/*" | while read file; do
    sed -i 's/2024/2025/g' "$file"
    sed -i 's/December 13, 2024/August 8, 2025/g' "$file"
    sed -i 's/December 2024/August 2025/g' "$file"
done

# Update Python files with copyright
find /workspace -type f -name "*.py" -not -path "*/node_modules/*" | while read file; do
    sed -i 's/Copyright © 2024/Copyright © 2025/g' "$file"
    sed -i 's/2024 iTechSmart/2025 iTechSmart/g' "$file"
done

# Update TypeScript/JavaScript files
find /workspace -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) -not -path "*/node_modules/*" | while read file; do
    sed -i 's/Copyright © 2024/Copyright © 2025/g' "$file"
    sed -i 's/2024 iTechSmart/2025 iTechSmart/g' "$file"
done

echo ""
echo "✅ Date updates complete!"
echo ""
echo "Updated patterns:"
echo "  - Copyright © 2024 → Copyright © 2025"
echo "  - December 13, 2024 → August 8, 2025"
echo "  - December 2024 → August 2025"
echo "  - All other 2024 references → 2025"
