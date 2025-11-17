# ProofLink.AI Deployment Runbook

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Monitoring Setup](#monitoring-setup)
6. [Backup & Recovery](#backup--recovery)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)

---

## Prerequisites

### Required Software
- Docker 20.10+
- Docker Compose 2.0+
- kubectl 1.24+ (for Kubernetes)
- Git

### Required Accounts
- Domain registrar (for DNS)
- SSL certificate provider (or Let's Encrypt)
- Stripe account (for payments)
- Email service (SMTP)

### Infrastructure Requirements
- **Minimum:** 2 CPU cores, 4GB RAM, 50GB storage
- **Recommended:** 4 CPU cores, 8GB RAM, 100GB storage
- **Production:** 8+ CPU cores, 16GB+ RAM, 500GB+ storage

---

## Initial Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-org/prooflink.git
cd prooflink
```

### 2. Configure Environment
```bash
# Copy production environment template
cp deployment/production.env .env

# Edit with your values
nano .env
```

**Critical values to change:**
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - Random 32+ character string
- `STRIPE_SECRET_KEY` - Your Stripe secret key
- `SMTP_*` - Email configuration

### 3. Generate Secrets
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate database password
openssl rand -base64 32

# Generate Redis password
openssl rand -base64 32
```

---

## Docker Deployment

### 1. Build Images
```bash
# Build backend
docker build -f Dockerfile.backend -t prooflink/backend:latest .

# Build frontend
docker build -f Dockerfile.frontend -t prooflink/frontend:latest .
```

### 2. Start Services
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Initialize Database
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create admin user
docker-compose exec backend python scripts/create_admin.py
```

### 4. Verify Deployment
```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check API docs
open http://localhost:8000/docs
```

---

## Kubernetes Deployment

### 1. Create Namespace
```bash
kubectl apply -f k8s/namespace.yml
```

### 2. Configure Secrets
```bash
# Edit secrets with your values
nano k8s/secrets.yml

# Apply secrets
kubectl apply -f k8s/secrets.yml
```

### 3. Deploy Database & Cache
```bash
# Deploy PostgreSQL
kubectl apply -f k8s/postgres-statefulset.yml

# Deploy Redis
kubectl apply -f k8s/redis-deployment.yml

# Wait for ready
kubectl wait --for=condition=ready pod -l app=postgres -n prooflink --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n prooflink --timeout=300s
```

### 4. Deploy Application
```bash
# Deploy backend
kubectl apply -f k8s/backend-deployment.yml

# Deploy frontend
kubectl apply -f k8s/frontend-deployment.yml

# Wait for ready
kubectl wait --for=condition=ready pod -l app=backend -n prooflink --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend -n prooflink --timeout=300s
```

### 5. Configure Ingress
```bash
# Install cert-manager (if not already installed)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Apply ingress
kubectl apply -f k8s/ingress.yml
```

### 6. Run Database Migrations
```bash
kubectl exec -it deployment/backend -n prooflink -- alembic upgrade head
```

### 7. Verify Deployment
```bash
# Check all pods
kubectl get pods -n prooflink

# Check services
kubectl get svc -n prooflink

# Check ingress
kubectl get ingress -n prooflink

# View logs
kubectl logs -f deployment/backend -n prooflink
```

---

## Monitoring Setup

### 1. Deploy Prometheus
```bash
# Create monitoring namespace
kubectl create namespace monitoring

# Deploy Prometheus
kubectl apply -f deployment/monitoring/prometheus.yml -n monitoring
```

### 2. Deploy Grafana
```bash
# Deploy Grafana
kubectl apply -f deployment/monitoring/grafana.yml -n monitoring

# Get admin password
kubectl get secret grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode
```

### 3. Import Dashboards
```bash
# Access Grafana
kubectl port-forward svc/grafana 3000:3000 -n monitoring

# Open http://localhost:3000
# Import dashboard from deployment/monitoring/grafana-dashboard.json
```

### 4. Configure Alerts
```bash
# Alerts are configured in deployment/monitoring/alerts.yml
# They will be automatically loaded by Prometheus
```

---

## Backup & Recovery

### 1. Automated Backups
```bash
# Make backup script executable
chmod +x deployment/backup.sh

# Run backup manually
./deployment/backup.sh

# Schedule with cron (daily at 2 AM)
echo "0 2 * * * /path/to/deployment/backup.sh" | crontab -
```

### 2. Manual Backup
```bash
# Database
docker exec prooflink-postgres pg_dump -U prooflink prooflink > backup.sql

# Uploads
docker run --rm -v prooflink_upload_data:/data -v $(pwd):/backup alpine tar czf /backup/uploads.tar.gz -C /data .

# Redis
docker exec prooflink-redis redis-cli SAVE
docker cp prooflink-redis:/data/dump.rdb ./redis-backup.rdb
```

### 3. Restore from Backup
```bash
# Make restore script executable
chmod +x deployment/restore.sh

# List available backups
./deployment/restore.sh

# Restore specific backup
./deployment/restore.sh 20250115_120000
```

---

## Troubleshooting

### Common Issues

#### 1. Backend Not Starting
```bash
# Check logs
docker-compose logs backend

# Common causes:
# - Database connection failed
# - Redis connection failed
# - Missing environment variables

# Verify connections
docker-compose exec backend python -c "from app.db.database import engine; print(engine)"
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready

# Check connection from backend
docker-compose exec backend psql $DATABASE_URL -c "SELECT 1"

# Reset database (WARNING: destroys data)
docker-compose down -v
docker-compose up -d
```

#### 3. High Memory Usage
```bash
# Check container stats
docker stats

# Restart services
docker-compose restart

# Scale down (K8s)
kubectl scale deployment backend --replicas=2 -n prooflink
```

#### 4. SSL Certificate Issues
```bash
# Check certificate status
kubectl describe certificate prooflink-tls -n prooflink

# Force renewal
kubectl delete certificate prooflink-tls -n prooflink
kubectl apply -f k8s/ingress.yml
```

---

## Maintenance

### Regular Tasks

#### Daily
- [ ] Check application logs
- [ ] Monitor error rates
- [ ] Verify backups completed

#### Weekly
- [ ] Review performance metrics
- [ ] Check disk space
- [ ] Update dependencies (if needed)

#### Monthly
- [ ] Security updates
- [ ] Database optimization
- [ ] Review and rotate logs
- [ ] Test backup restoration

### Update Procedure

#### 1. Backup Current State
```bash
./deployment/backup.sh
```

#### 2. Pull Latest Code
```bash
git pull origin main
```

#### 3. Build New Images
```bash
docker-compose build
```

#### 4. Run Database Migrations
```bash
docker-compose exec backend alembic upgrade head
```

#### 5. Rolling Update (K8s)
```bash
kubectl set image deployment/backend backend=prooflink/backend:new-version -n prooflink
kubectl rollout status deployment/backend -n prooflink
```

#### 6. Verify Update
```bash
# Check version
curl https://api.prooflink.ai/health

# Monitor logs
kubectl logs -f deployment/backend -n prooflink
```

#### 7. Rollback (if needed)
```bash
kubectl rollout undo deployment/backend -n prooflink
```

---

## Health Checks

### Endpoints
- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost:3000/api/health`
- Database: `docker-compose exec postgres pg_isready`
- Redis: `docker-compose exec redis redis-cli ping`

### Monitoring URLs
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`
- API Docs: `http://localhost:8000/docs`

---

## Support

For issues not covered in this runbook:
- Email: support@prooflink.ai
- Documentation: https://docs.prooflink.ai
- GitHub Issues: https://github.com/your-org/prooflink/issues