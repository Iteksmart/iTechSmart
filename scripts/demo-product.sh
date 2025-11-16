#!/bin/bash
# Run automated demo for a single product

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

print_demo() {
    echo -e "${BLUE}[DEMO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

if [ -z "$1" ]; then
    echo "Usage: ./demo-product.sh <product-name> <frontend-port>"
    echo "Example: ./demo-product.sh itechsmart-ninja 3001"
    exit 1
fi

PRODUCT_NAME=$1
FRONTEND_PORT=${2:-3000}
BACKEND_PORT=$((FRONTEND_PORT + 5000))

print_info "=========================================="
print_info "Demo: $PRODUCT_NAME"
print_info "=========================================="
echo ""

# Check if product is running
print_info "Checking if product is running..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$FRONTEND_PORT || echo "000")
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$BACKEND_PORT/health || echo "000")

if [ "$FRONTEND_STATUS" != "200" ]; then
    print_info "Frontend not running. Starting product..."
    cd "deployments/$PRODUCT_NAME" 2>/dev/null || {
        echo "Product not deployed. Run: ./deploy-single-product.sh $PRODUCT_NAME"
        exit 1
    }
    docker-compose up -d
    sleep 10
fi

print_demo "Step 1: Opening frontend..."
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:$FRONTEND_PORT"
elif command -v open &> /dev/null; then
    open "http://localhost:$FRONTEND_PORT"
else
    print_info "Please open: http://localhost:$FRONTEND_PORT"
fi

sleep 2

print_demo "Step 2: Testing backend health..."
HEALTH_RESPONSE=$(curl -s http://localhost:$BACKEND_PORT/health)
if [ $? -eq 0 ]; then
    print_success "✅ Backend is healthy"
    echo "Response: $HEALTH_RESPONSE"
else
    print_info "⚠️  Backend health check failed"
fi

sleep 2

print_demo "Step 3: Testing API documentation..."
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:$BACKEND_PORT/docs"
elif command -v open &> /dev/null; then
    open "http://localhost:$BACKEND_PORT/docs"
else
    print_info "API Docs: http://localhost:$BACKEND_PORT/docs"
fi

sleep 2

print_demo "Step 4: Checking logs..."
cd "deployments/$PRODUCT_NAME"
docker-compose logs --tail=20

echo ""
print_info "=========================================="
print_info "Demo Complete!"
print_info "=========================================="
echo ""
print_info "Manual testing steps:"
print_info "1. Login/Register at http://localhost:$FRONTEND_PORT"
print_info "2. Navigate through the dashboard"
print_info "3. Test core features"
print_info "4. Check data persistence"
print_info "5. Test API endpoints at http://localhost:$BACKEND_PORT/docs"
echo ""
print_info "View live logs: docker-compose logs -f"
echo ""