#!/bin/bash

# Update all version numbers to 1.2.0
echo "Updating all version numbers to 1.2.0..."

# Update package.json files
find . -name "package.json" -type f -not -path "*/node_modules/*" -exec sed -i 's/"version": "1.0.0"/"version": "1.2.0"/g' {} \;
find . -name "package.json" -type f -not -path "*/node_modules/*" -exec sed -i 's/"version": "1.1.0"/"version": "1.2.0"/g' {} \;

# Update Docker tags
find . -name "docker-compose*.yml" -type f -exec sed -i 's/:1.0.0/:1.2.0/g' {} \;
find . -name "docker-compose*.yml" -type f -exec sed -i 's/:1.1.0/:1.2.0/g' {} \;
find . -name "docker-compose*.yml" -type f -exec sed -i 's/:latest/:1.2.0/g' {} \;

# Update Dockerfiles
find . -name "Dockerfile" -type f -not -path "*/node_modules/*" -exec sed -i 's/VERSION=1.0.0/VERSION=1.2.0/g' {} \;
find . -name "Dockerfile" -type f -not -path "*/node_modules/*" -exec sed -i 's/VERSION=1.1.0/VERSION=1.2.0/g' {} \;

# Update README files
find . -name "README.md" -type f -not -path "*/node_modules/*" -exec sed -i 's/Version: 1.0.0/Version: 1.2.0/g' {} \;
find . -name "README.md" -type f -not -path "*/node_modules/*" -exec sed -i 's/Version: 1.1.0/Version: 1.2.0/g' {} \;
find . -name "README.md" -type f -not -path "*/node_modules/*" -exec sed -i 's/v1.0.0/v1.2.0/g' {} \;
find . -name "README.md" -type f -not -path "*/node_modules/*" -exec sed -i 's/v1.1.0/v1.2.0/g' {} \;

echo "Version update complete!"
echo "All versions updated to 1.2.0"