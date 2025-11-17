#!/bin/bash

# iTechSmart Suite - Demo Environment Setup Script
# This script sets up the complete demo environment

set -e

echo "=========================================="
echo "iTechSmart Suite - Demo Environment Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p demo-landing
mkdir -p data/postgres
mkdir -p logs

echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Demo Environment Configuration
NODE_ENV=demo
POSTGRES_USER=demo
POSTGRES_PASSWORD=demo123
POSTGRES_DB=license_demo

# License Server
LICENSE_SERVER_PORT=3000
JWT_SECRET=demo-jwt-secret-change-in-production
SECRET_KEY=demo-secret-key-change-in-production

# Demo Credentials
ADMIN_EMAIL=admin@demo.com
ADMIN_PASSWORD=demo123

# API Keys
NINJA_API_KEY=demo-ninja-api-key
SUPREME_API_KEY=demo-supreme-api-key
CITADEL_API_KEY=demo-citadel-api-key
COPILOT_API_KEY=demo-copilot-api-key
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
else
    echo -e "${YELLOW}⚠ .env file already exists, skipping${NC}"
fi
echo ""

# Pull required Docker images
echo "Pulling Docker images..."
docker-compose -f docker-compose.demo.yml pull

echo -e "${GREEN}✓ Docker images pulled${NC}"
echo ""

# Build custom images
echo "Building custom images..."
docker-compose -f docker-compose.demo.yml build

echo -e "${GREEN}✓ Custom images built${NC}"
echo ""

# Start services
echo "Starting demo environment..."
docker-compose -f docker-compose.demo.yml up -d

echo -e "${GREEN}✓ Demo environment started${NC}"
echo ""

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check service health
echo "Checking service health..."
services=("license-server:3000" "ninja-demo:3000" "supreme-demo:3000" "citadel-demo:3000" "copilot-demo:3000")
for service in "${services[@]}"; do
    container=$(echo $service | cut -d: -f1)
    if docker ps | grep -q $container; then
        echo -e "${GREEN}✓ $container is running${NC}"
    else
        echo -e "${RED}✗ $container is not running${NC}"
    fi
done
echo ""

# Initialize database with sample data
echo "Initializing database with sample data..."
docker-compose -f docker-compose.demo.yml exec -T license-server npm run seed:demo 2>/dev/null || echo -e "${YELLOW}⚠ Database seeding skipped (run manually if needed)${NC}"
echo ""

# Display access information
echo "=========================================="
echo -e "${GREEN}Demo Environment Ready!${NC}"
echo "=========================================="
echo ""
echo "Access the demo at: http://localhost"
echo ""
echo "Individual Services:"
echo "  • License Server: http://localhost:3000"
echo "  • iTechSmart Ninja: http://localhost:3001"
echo "  • iTechSmart Supreme: http://localhost:3002"
echo "  • iTechSmart Citadel: http://localhost:3003"
echo "  • iTechSmart Copilot: http://localhost:3004"
echo ""
echo "Demo Credentials:"
echo "  • Admin: admin@demo.com / demo123"
echo "  • Ninja: demo@ninja.com / ninja123"
echo "  • Supreme: demo@supreme.com / supreme123"
echo "  • Citadel: demo@citadel.com / citadel123"
echo "  • Copilot: demo@copilot.com / copilot123"
echo ""
echo "Useful Commands:"
echo "  • View logs: docker-compose -f docker-compose.demo.yml logs -f"
echo "  • Stop demo: docker-compose -f docker-compose.demo.yml down"
echo "  • Restart demo: docker-compose -f docker-compose.demo.yml restart"
echo "  • Clean up: docker-compose -f docker-compose.demo.yml down -v"
echo ""
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="