#!/bin/bash

# iTechSmart Suite - Deployment Script
# This script automates the deployment process for all environments

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check kubectl for production
    if [ "$ENVIRONMENT" = "production" ]; then
        if ! command -v kubectl &> /dev/null; then
            log_error "kubectl is not installed"
            exit 1
        fi
    fi
    
    log_success "All prerequisites met"
}

load_environment() {
    log_info "Loading environment configuration for: $ENVIRONMENT"
    
    ENV_FILE="$PROJECT_ROOT/.env.$ENVIRONMENT"
    
    if [ ! -f "$ENV_FILE" ]; then
        log_error "Environment file not found: $ENV_FILE"
        exit 1
    fi
    
    export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
    log_success "Environment loaded"
}

backup_database() {
    log_info "Creating database backup..."
    
    BACKUP_DIR="$PROJECT_ROOT/backups"
    mkdir -p "$BACKUP_DIR"
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/itechsmart_${ENVIRONMENT}_${TIMESTAMP}.sql"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        # Production backup using AWS RDS
        aws rds create-db-snapshot \
            --db-instance-identifier itechsmart-prod \
            --db-snapshot-identifier itechsmart-prod-$TIMESTAMP
        log_success "Production database snapshot created"
    else
        # Local backup
        docker-compose exec -T postgres pg_dump -U itechsmart itechsmart > "$BACKUP_FILE"
        gzip "$BACKUP_FILE"
        log_success "Database backup created: ${BACKUP_FILE}.gz"
    fi
}

build_images() {
    log_info "Building Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Build all services
    docker-compose -f docker-compose.production.yml build \
        --build-arg VERSION=$VERSION \
        --no-cache
    
    log_success "Docker images built successfully"
}

run_tests() {
    log_info "Running tests..."
    
    # Unit tests
    log_info "Running unit tests..."
    docker-compose -f docker-compose.test.yml run --rm test-runner pytest tests/unit/ -v
    
    # Integration tests
    log_info "Running integration tests..."
    docker-compose -f docker-compose.test.yml run --rm test-runner pytest tests/integration/ -v
    
    # Security audit
    log_info "Running security audit..."
    docker-compose -f docker-compose.test.yml run --rm test-runner python tests/security/security_audit.py
    
    log_success "All tests passed"
}

deploy_staging() {
    log_info "Deploying to staging environment..."
    
    cd "$PROJECT_ROOT"
    
    # Stop existing containers
    docker-compose -f docker-compose.production.yml down
    
    # Start new containers
    docker-compose -f docker-compose.production.yml up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 30
    
    # Health checks
    check_health "http://localhost:8000/health" "Enterprise"
    check_health "http://localhost:8001/health" "Analytics"
    check_health "http://localhost:8002/health" "Ninja"
    
    log_success "Staging deployment completed"
}

deploy_production() {
    log_info "Deploying to production environment..."
    
    # Confirm production deployment
    read -p "Are you sure you want to deploy to PRODUCTION? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log_warning "Production deployment cancelled"
        exit 0
    fi
    
    # Create backup
    backup_database
    
    # Apply Kubernetes configurations
    log_info "Applying Kubernetes configurations..."
    kubectl apply -f "$PROJECT_ROOT/k8s/production/deployment.yaml"
    
    # Wait for rollout
    log_info "Waiting for rollout to complete..."
    kubectl rollout status deployment/enterprise -n itechsmart-production
    kubectl rollout status deployment/analytics -n itechsmart-production
    kubectl rollout status deployment/ninja -n itechsmart-production
    
    # Health checks
    log_info "Running health checks..."
    sleep 30
    check_health "https://itechsmart.com/health" "Production Enterprise"
    check_health "https://api.itechsmart.com/analytics/health" "Production Analytics"
    
    log_success "Production deployment completed"
}

check_health() {
    local url=$1
    local service=$2
    local max_attempts=10
    local attempt=1
    
    log_info "Checking health of $service..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null; then
            log_success "$service is healthy"
            return 0
        fi
        
        log_warning "Attempt $attempt/$max_attempts: $service not ready yet..."
        sleep 5
        ((attempt++))
    done
    
    log_error "$service health check failed"
    return 1
}

run_migrations() {
    log_info "Running database migrations..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        kubectl exec -it deployment/enterprise -n itechsmart-production -- \
            python -m alembic upgrade head
    else
        docker-compose exec enterprise python -m alembic upgrade head
    fi
    
    log_success "Database migrations completed"
}

rollback() {
    log_warning "Rolling back deployment..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        kubectl rollout undo deployment/enterprise -n itechsmart-production
        kubectl rollout undo deployment/analytics -n itechsmart-production
        kubectl rollout undo deployment/ninja -n itechsmart-production
        log_success "Production rollback completed"
    else
        docker-compose -f docker-compose.production.yml down
        docker-compose -f docker-compose.production.yml up -d
        log_success "Staging rollback completed"
    fi
}

show_logs() {
    log_info "Showing logs for $ENVIRONMENT..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        kubectl logs -f deployment/enterprise -n itechsmart-production
    else
        docker-compose -f docker-compose.production.yml logs -f
    fi
}

cleanup() {
    log_info "Cleaning up old images and containers..."
    
    docker system prune -af --volumes
    
    log_success "Cleanup completed"
}

# Main deployment flow
main() {
    echo "=========================================="
    echo "iTechSmart Suite Deployment"
    echo "=========================================="
    echo "Environment: $ENVIRONMENT"
    echo "Version: $VERSION"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    load_environment
    
    case "$ENVIRONMENT" in
        staging)
            build_images
            run_tests
            deploy_staging
            ;;
        production)
            build_images
            run_tests
            deploy_production
            ;;
        *)
            log_error "Invalid environment: $ENVIRONMENT"
            echo "Usage: $0 {staging|production} [version]"
            exit 1
            ;;
    esac
    
    log_success "Deployment completed successfully!"
    echo ""
    echo "=========================================="
    echo "Next steps:"
    echo "1. Monitor logs: $0 logs $ENVIRONMENT"
    echo "2. Check health: curl https://$ENVIRONMENT.itechsmart.com/health"
    echo "3. View metrics: https://grafana.itechsmart.com"
    echo "=========================================="
}

# Handle script arguments
case "${3:-deploy}" in
    deploy)
        main
        ;;
    rollback)
        rollback
        ;;
    logs)
        show_logs
        ;;
    cleanup)
        cleanup
        ;;
    migrations)
        run_migrations
        ;;
    *)
        echo "Usage: $0 {staging|production} [version] {deploy|rollback|logs|cleanup|migrations}"
        exit 1
        ;;
esac