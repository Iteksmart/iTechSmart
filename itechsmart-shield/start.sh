#!/bin/bash

# iTechSmart Shield - Quick Start Script
# This script helps you get iTechSmart Shield up and running quickly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Print banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║           iTechSmart Shield 🛡️                            ║"
    echo "║     Enterprise Security Operations Platform               ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose is installed"
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    print_success "Docker daemon is running"
}

# Check if services are already running
check_running_services() {
    print_info "Checking for running services..."
    
    if docker-compose ps | grep -q "Up"; then
        print_warning "Some services are already running"
        read -p "Do you want to restart them? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Stopping existing services..."
            docker-compose down
        else
            print_info "Keeping existing services running"
            return 1
        fi
    fi
    return 0
}

# Start services
start_services() {
    print_info "Starting iTechSmart Shield services..."
    
    # Pull latest images
    print_info "Pulling Docker images..."
    docker-compose pull
    
    # Build images
    print_info "Building Docker images..."
    docker-compose build
    
    # Start services
    print_info "Starting services..."
    docker-compose up -d
    
    print_success "Services started successfully!"
}

# Wait for services to be healthy
wait_for_services() {
    print_info "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    print_info "Waiting for PostgreSQL..."
    timeout=60
    counter=0
    until docker-compose exec -T postgres pg_isready -U shield_user &> /dev/null; do
        sleep 2
        counter=$((counter + 2))
        if [ $counter -ge $timeout ]; then
            print_error "PostgreSQL failed to start within $timeout seconds"
            exit 1
        fi
    done
    print_success "PostgreSQL is ready"
    
    # Wait for Redis
    print_info "Waiting for Redis..."
    counter=0
    until docker-compose exec -T redis redis-cli ping &> /dev/null; do
        sleep 2
        counter=$((counter + 2))
        if [ $counter -ge $timeout ]; then
            print_error "Redis failed to start within $timeout seconds"
            exit 1
        fi
    done
    print_success "Redis is ready"
    
    # Wait for Elasticsearch
    print_info "Waiting for Elasticsearch..."
    counter=0
    until curl -s http://localhost:9200/_cluster/health &> /dev/null; do
        sleep 2
        counter=$((counter + 2))
        if [ $counter -ge $timeout ]; then
            print_error "Elasticsearch failed to start within $timeout seconds"
            exit 1
        fi
    done
    print_success "Elasticsearch is ready"
    
    # Wait for Backend
    print_info "Waiting for Backend API..."
    counter=0
    until curl -s http://localhost:8000/health &> /dev/null; do
        sleep 2
        counter=$((counter + 2))
        if [ $counter -ge $timeout ]; then
            print_error "Backend API failed to start within $timeout seconds"
            exit 1
        fi
    done
    print_success "Backend API is ready"
    
    # Wait for Frontend
    print_info "Waiting for Frontend..."
    counter=0
    until curl -s http://localhost:3000 &> /dev/null; do
        sleep 2
        counter=$((counter + 2))
        if [ $counter -ge $timeout ]; then
            print_error "Frontend failed to start within $timeout seconds"
            exit 1
        fi
    done
    print_success "Frontend is ready"
}

# Display service information
display_info() {
    echo ""
    print_success "iTechSmart Shield is now running!"
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Access URLs:${NC}"
    echo -e "  ${BLUE}Frontend:${NC}        http://localhost:3000"
    echo -e "  ${BLUE}Backend API:${NC}     http://localhost:8000"
    echo -e "  ${BLUE}API Docs:${NC}        http://localhost:8000/docs"
    echo -e "  ${BLUE}PostgreSQL:${NC}      localhost:5432"
    echo -e "  ${BLUE}Redis:${NC}           localhost:6379"
    echo -e "  ${BLUE}Elasticsearch:${NC}   http://localhost:9200"
    echo ""
    echo -e "${GREEN}Default Credentials:${NC}"
    echo -e "  ${BLUE}Database:${NC}        shield_user / shield_pass_2024"
    echo ""
    echo -e "${GREEN}Useful Commands:${NC}"
    echo -e "  ${BLUE}View logs:${NC}       docker-compose logs -f"
    echo -e "  ${BLUE}Stop services:${NC}   docker-compose down"
    echo -e "  ${BLUE}Restart:${NC}         docker-compose restart"
    echo -e "  ${BLUE}Status:${NC}          docker-compose ps"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Show logs
show_logs() {
    print_info "Showing service logs (Ctrl+C to exit)..."
    docker-compose logs -f
}

# Main execution
main() {
    print_banner
    
    # Check prerequisites
    check_prerequisites
    
    # Check running services
    if ! check_running_services; then
        display_info
        read -p "Do you want to view logs? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            show_logs
        fi
        exit 0
    fi
    
    # Start services
    start_services
    
    # Wait for services
    wait_for_services
    
    # Display information
    display_info
    
    # Ask if user wants to see logs
    read -p "Do you want to view logs? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        show_logs
    fi
}

# Run main function
main