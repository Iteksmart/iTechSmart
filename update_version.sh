#!/bin/bash

echo "Updating all package.json files to version 1.4.0..."

# Find all package.json files (excluding node_modules and release directories)
find iTechSmart -name "package.json" -type f \
  ! -path "*/node_modules/*" \
  ! -path "*/release/*" \
  ! -path "*/.next/*" \
  ! -path "*/dist/*" \
  ! -path "*/build/*" | while read file; do
  
  # Update version using sed
  sed -i 's/"version": "1\.[0-9]\.[0-9]"/"version": "1.4.0"/g' "$file"
  echo "Updated: $file"
done

echo "Version update complete!"
