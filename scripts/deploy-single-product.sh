#!/bin/bash
# Deploy a single iTechSmart product

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if product name is provided
if [ -z "$1" ]; then
    print_error "Usage: ./deploy-single-product.sh <product-name>"
    echo "Example: ./deploy-single-product.sh itechsmart-ninja"
    echo ""
    echo "Available products:"
    echo "  - itechsmart-ninja, itechsmart-enterprise, itechsmart-analytics"
    echo "  - prooflink, passport, itechsmart-impactos"
    echo "  - legalai-pro, itechsmart-dataflow, itechsmart-pulse"
    echo "  - And 26 more..."
    exit 1
fi

PRODUCT_NAME=$1
BACKEND_PORT=${2:-8000}
FRONTEND_PORT=${3:-3000}

print_info "Deploying $PRODUCT_NAME..."
print_info "Backend Port: $BACKEND_PORT"
print_info "Frontend Port: $FRONTEND_PORT"

# Create deployment directory
DEPLOY_DIR="deployments/$PRODUCT_NAME"
mkdir -p "$DEPLOY_DIR"
cd "$DEPLOY_DIR"

# Create .env file
print_info "Creating environment file..."
cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://itechsmart:secure_password@localhost:5432/itechsmart_db
POSTGRES_USER=itechsmart
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=itechsmart_db

# Backend Configuration
BACKEND_PORT=$BACKEND_PORT
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

# Frontend Configuration
FRONTEND_PORT=$FRONTEND_PORT
VITE_API_URL=http://localhost:$BACKEND_PORT
REACT_APP_API_URL=http://localhost:$BACKEND_PORT

# Redis Configuration
REDIS_URL=redis://localhost:6379
EOF

# Create docker-compose.yml
print_info "Creating Docker Compose file..."
cat > docker-compose.yml << EOF
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: \${POSTGRES_USER}
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
      POSTGRES_DB: \${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    image: ghcr.io/iteksmart/${PRODUCT_NAME}-backend:main
    environment:
      DATABASE_URL: \${DATABASE_URL}
      SECRET_KEY: \${SECRET_KEY}
      JWT_SECRET: \${JWT_SECRET}
    ports:
      - "\${BACKEND_PORT}:8000"
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  frontend:
    image: ghcr.io/iteksmart/${PRODUCT_NAME}-frontend:main
    environment:
      VITE_API_URL: http://localhost:\${BACKEND_PORT}
      REACT_APP_API_URL: http://localhost:\${BACKEND_PORT}
    ports:
      - "\${FRONTEND_PORT}:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
EOF

# Pull images
print_info "Pulling Docker images..."
docker-compose pull

# Start services
print_info "Starting services..."
docker-compose up -d

# Wait for services to be healthy
print_info "Waiting for services to be ready..."
sleep 10

# Check health
print_info "Checking service health..."
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$BACKEND_PORT/health || echo "000")
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$FRONTEND_PORT || echo "000")

if [ "$BACKEND_HEALTH" = "200" ]; then
    print_info "✅ Backend is healthy"
else
    print_warning "⚠️  Backend health check returned: $BACKEND_HEALTH"
fi

if [ "$FRONTEND_HEALTH" = "200" ]; then
    print_info "✅ Frontend is healthy"
else
    print_warning "⚠️  Frontend health check returned: $FRONTEND_HEALTH"
fi

# Print access information
echo ""
print_info "=========================================="
print_info "Deployment Complete!"
print_info "=========================================="
echo ""
print_info "Access your application:"
print_info "  Frontend: http://localhost:$FRONTEND_PORT"
print_info "  Backend:  http://localhost:$BACKEND_PORT"
print_info "  API Docs: http://localhost:$BACKEND_PORT/docs"
echo ""
print_info "Useful commands:"
print_info "  View logs:    docker-compose logs -f"
print_info "  Stop:         docker-compose down"
print_info "  Restart:      docker-compose restart"
print_info "  Status:       docker-compose ps"
echo ""