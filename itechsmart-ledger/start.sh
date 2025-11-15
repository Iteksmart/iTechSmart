#!/bin/bash

# iTechSmart Ledger - Quick Start Script
# This script helps you quickly start the iTechSmart Ledger platform

set -e

echo "=========================================="
echo "  iTechSmart Ledger - Quick Start"
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
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Stop any existing containers
echo "Stopping any existing containers..."
docker-compose down 2>/dev/null || true
echo ""

# Build and start services
echo "Building and starting services..."
echo "This may take a few minutes on first run..."
echo ""
docker-compose up -d --build

# Wait for services to be healthy
echo ""
echo "Waiting for services to be ready..."
echo ""

# Wait for PostgreSQL
echo -n "Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U ledger_user -d ledger_db &> /dev/null; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Redis
echo -n "Waiting for Redis..."
for i in {1..30}; do
    if docker-compose exec -T redis redis-cli ping &> /dev/null; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Backend
echo -n "Waiting for Backend API..."
for i in {1..60}; do
    if curl -s http://localhost:8000/health &> /dev/null; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Frontend
echo -n "Waiting for Frontend..."
for i in {1..60}; do
    if curl -s http://localhost:5173 &> /dev/null; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "=========================================="
echo -e "${GREEN}✓ All services are running!${NC}"
echo "=========================================="
echo ""
echo "Access the application:"
echo ""
echo -e "  ${GREEN}Frontend:${NC}     http://localhost:5173"
echo -e "  ${GREEN}Backend API:${NC}  http://localhost:8000"
echo -e "  ${GREEN}API Docs:${NC}     http://localhost:8000/docs"
echo ""
echo "Default credentials:"
echo -e "  ${YELLOW}Email:${NC}     admin@itechsmart.com"
echo -e "  ${YELLOW}Password:${NC}  admin123"
echo ""
echo "=========================================="
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose down"
echo "  Restart services: docker-compose restart"
echo ""
echo "For more information, see README.md"
echo ""