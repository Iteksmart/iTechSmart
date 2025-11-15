#!/bin/bash

# iTechSmart Connect - Startup Script
# This script starts all services and provides helpful information

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Print banner
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║         iTechSmart Connect - Startup Script              ║"
echo "║          API Management Platform                         ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check prerequisites
print_info "Checking prerequisites..."

if ! command_exists docker; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_success "Docker is installed"

if ! command_exists docker-compose; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
print_success "Docker Compose is installed"

# Stop any existing containers
print_info "Stopping any existing containers..."
docker-compose down 2>/dev/null || true
print_success "Existing containers stopped"

# Pull latest images
print_info "Pulling latest images..."
docker-compose pull

# Build containers
print_info "Building containers..."
docker-compose build

# Start services
print_info "Starting services..."
docker-compose up -d

# Wait for services to be healthy
print_info "Waiting for services to be healthy..."
sleep 10

# Check service health
print_info "Checking service health..."

services=("postgres" "redis" "backend" "frontend")
all_healthy=true

for service in "${services[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        print_success "$service is running"
    else
        print_error "$service is not running"
        all_healthy=false
    fi
done

echo ""
if [ "$all_healthy" = true ]; then
    print_success "All services are running!"
else
    print_warning "Some services are not running. Check logs with: docker-compose logs"
fi

# Print access information
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                    Access Information                     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Frontend Application:"
echo "  URL: http://localhost:5173"
echo ""
echo "Backend API:"
echo "  URL: http://localhost:8000"
echo "  Docs: http://localhost:8000/docs"
echo "  ReDoc: http://localhost:8000/redoc"
echo ""
echo "Default Login Credentials:"
echo "  Admin:"
echo "    Email: admin@itechsmart.com"
echo "    Password: password"
echo ""
echo "  Developer:"
echo "    Email: developer@itechsmart.com"
echo "    Password: password"
echo ""
echo "  Viewer:"
echo "    Email: viewer@itechsmart.com"
echo "    Password: password"
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                    Useful Commands                        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "View logs:"
echo "  docker-compose logs -f"
echo ""
echo "View specific service logs:"
echo "  docker-compose logs -f backend"
echo ""
echo "Stop all services:"
echo "  docker-compose down"
echo ""
echo "Stop and remove volumes:"
echo "  docker-compose down -v"
echo ""
echo "Restart a service:"
echo "  docker-compose restart backend"
echo ""
echo "Check service status:"
echo "  docker-compose ps"
echo ""
echo "Access backend shell:"
echo "  docker-compose exec backend bash"
echo ""
echo "Access database:"
echo "  docker-compose exec postgres psql -U connect_user -d connect"
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                  Deployment Complete!                     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
print_success "iTechSmart Connect is now running!"
print_info "Open http://localhost:5173 in your browser to get started."
echo ""