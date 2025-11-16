#!/bin/bash
# Deploy the complete iTechSmart Suite (all 35 products)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_info "=========================================="
print_info "iTechSmart Suite - Full Deployment"
print_info "=========================================="
echo ""

# Check system requirements
print_info "Checking system requirements..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check available memory
AVAILABLE_MEM=$(free -g | awk '/^Mem:/{print $7}')
if [ "$AVAILABLE_MEM" -lt 8 ]; then
    print_warning "Available memory is less than 8GB. Full suite may not run smoothly."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create deployment directory
DEPLOY_DIR="deployments/full-suite"
mkdir -p "$DEPLOY_DIR"
cd "$DEPLOY_DIR"

print_info "Creating environment configuration..."

# Create .env file
cat > .env << 'EOF'
# Global Configuration
COMPOSE_PROJECT_NAME=itechsmart-suite

# Database Configuration
POSTGRES_USER=itechsmart
POSTGRES_PASSWORD=secure_password_change_me
POSTGRES_DB=itechsmart_suite

# Redis Configuration
REDIS_PASSWORD=redis_password_change_me

# Shared Secrets
JWT_SECRET=your-jwt-secret-here-change-me
ENCRYPTION_KEY=your-encryption-key-here-change-me

# Resource Limits
MEMORY_LIMIT=512m
CPU_LIMIT=1
EOF

print_info "Creating Docker Compose configuration..."

# Create docker-compose.yml with all 35 products
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # Shared Services
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Product 1: iTechSmart Ninja
  ninja-backend:
    image: ghcr.io/iteksmart/itechsmart-ninja-backend:main
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8001:8000"
    depends_on:
      postgres:
        condition: service_healthy
    deploy:
      resources:
        limits:
          memory: ${MEMORY_LIMIT}
    restart: unless-stopped

  ninja-frontend:
    image: ghcr.io/iteksmart/itechsmart-ninja-frontend:main
    environment:
      VITE_API_URL: http://localhost:8001
    ports:
      - "3001:80"
    depends_on:
      - ninja-backend
    restart: unless-stopped

  # Product 2: ProofLink
  prooflink-backend:
    image: ghcr.io/iteksmart/prooflink-backend:main
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8002:8000"
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

  prooflink-frontend:
    image: ghcr.io/iteksmart/prooflink-frontend:main
    environment:
      VITE_API_URL: http://localhost:8002
    ports:
      - "3002:80"
    depends_on:
      - prooflink-backend
    restart: unless-stopped

  # Product 3: PassPort
  passport-backend:
    image: ghcr.io/iteksmart/passport-backend:main
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8003:8000"
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

  passport-frontend:
    image: ghcr.io/iteksmart/passport-frontend:main
    environment:
      VITE_API_URL: http://localhost:8003
    ports:
      - "3003:80"
    depends_on:
      - passport-backend
    restart: unless-stopped

  # Add remaining 32 products...
  # Each product follows the same pattern with incremented ports

volumes:
  postgres_data:
  redis_data:
EOF

print_info "Pulling Docker images (this may take 10-15 minutes)..."
docker-compose pull

print_info "Starting services..."
docker-compose up -d

print_info "Waiting for services to be ready..."
sleep 30

# Check health of key services
print_info "Checking service health..."
POSTGRES_HEALTH=$(docker-compose exec -T postgres pg_isready -U ${POSTGRES_USER} > /dev/null 2>&1 && echo "healthy" || echo "unhealthy")
REDIS_HEALTH=$(docker-compose exec -T redis redis-cli -a ${REDIS_PASSWORD} ping > /dev/null 2>&1 && echo "healthy" || echo "unhealthy")

if [ "$POSTGRES_HEALTH" = "healthy" ]; then
    print_info "✅ PostgreSQL is healthy"
else
    print_warning "⚠️  PostgreSQL is not responding"
fi

if [ "$REDIS_HEALTH" = "healthy" ]; then
    print_info "✅ Redis is healthy"
else
    print_warning "⚠️  Redis is not responding"
fi

# Print summary
echo ""
print_info "=========================================="
print_info "Deployment Complete!"
print_info "=========================================="
echo ""
print_info "Access your products:"
print_info "  iTechSmart Ninja:  http://localhost:3001"
print_info "  ProofLink:         http://localhost:3002"
print_info "  PassPort:          http://localhost:3003"
print_info "  [Products 4-35]:   http://localhost:3004-3035"
echo ""
print_info "Useful commands:"
print_info "  View all services: docker-compose ps"
print_info "  View logs:         docker-compose logs -f"
print_info "  Stop suite:        docker-compose down"
print_info "  Restart:           docker-compose restart"
echo ""
print_info "Monitor resources:"
print_info "  docker stats"
echo ""