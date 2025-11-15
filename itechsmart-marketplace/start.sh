#!/bin/bash

# iTechSmart Marketplace - Startup Script
# This script starts all services and initializes the application

set -e

echo "=========================================="
echo "iTechSmart Marketplace - Startup Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Docker is installed
print_status "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_success "Docker is installed"

# Check if Docker Compose is installed
print_status "Checking Docker Compose installation..."
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
print_success "Docker Compose is installed"

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose down 2>/dev/null || true
print_success "Existing containers stopped"

# Remove old volumes (optional - uncomment to reset database)
# print_warning "Removing old volumes..."
# docker-compose down -v
# print_success "Old volumes removed"

# Build and start services
print_status "Building and starting services..."
docker-compose up -d --build

# Wait for services to be healthy
print_status "Waiting for services to be ready..."
echo ""

# Wait for PostgreSQL
print_status "Waiting for PostgreSQL..."
timeout=60
counter=0
until docker-compose exec -T postgres pg_isready -U marketplace_user -d marketplace_db &> /dev/null; do
    counter=$((counter + 1))
    if [ $counter -gt $timeout ]; then
        print_error "PostgreSQL failed to start within $timeout seconds"
        docker-compose logs postgres
        exit 1
    fi
    echo -n "."
    sleep 1
done
echo ""
print_success "PostgreSQL is ready"

# Wait for Redis
print_status "Waiting for Redis..."
counter=0
until docker-compose exec -T redis redis-cli ping &> /dev/null; do
    counter=$((counter + 1))
    if [ $counter -gt $timeout ]; then
        print_error "Redis failed to start within $timeout seconds"
        docker-compose logs redis
        exit 1
    fi
    echo -n "."
    sleep 1
done
echo ""
print_success "Redis is ready"

# Wait for Backend
print_status "Waiting for Backend API..."
counter=0
until curl -f http://localhost:8000/health &> /dev/null; do
    counter=$((counter + 1))
    if [ $counter -gt $timeout ]; then
        print_error "Backend API failed to start within $timeout seconds"
        docker-compose logs backend
        exit 1
    fi
    echo -n "."
    sleep 1
done
echo ""
print_success "Backend API is ready"

# Wait for Frontend
print_status "Waiting for Frontend..."
counter=0
until curl -f http://localhost:5173 &> /dev/null; do
    counter=$((counter + 1))
    if [ $counter -gt $timeout ]; then
        print_error "Frontend failed to start within $timeout seconds"
        docker-compose logs frontend
        exit 1
    fi
    echo -n "."
    sleep 1
done
echo ""
print_success "Frontend is ready"

echo ""
echo "=========================================="
print_success "All services are running!"
echo "=========================================="
echo ""
echo "Access the application:"
echo "  Frontend:        ${GREEN}http://localhost:5173${NC}"
echo "  Backend API:     ${GREEN}http://localhost:8000${NC}"
echo "  API Docs:        ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo "Default credentials:"
echo "  Admin:     ${YELLOW}admin@itechsmart.com / password${NC}"
echo "  Developer: ${YELLOW}developer@itechsmart.com / password${NC}"
echo ""
echo "Useful commands:"
echo "  View logs:       ${BLUE}docker-compose logs -f${NC}"
echo "  Stop services:   ${BLUE}docker-compose down${NC}"
echo "  Restart:         ${BLUE}docker-compose restart${NC}"
echo ""
echo "=========================================="