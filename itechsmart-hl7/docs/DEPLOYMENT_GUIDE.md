# iTechSmart HL7 Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying iTechSmart HL7 in various environments, from local development to production Kubernetes clusters.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Configuration](#configuration)
6. [Database Setup](#database-setup)
7. [SSL/TLS Configuration](#ssltls-configuration)
8. [Monitoring Setup](#monitoring-setup)
9. [Backup Configuration](#backup-configuration)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum Requirements:**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 50 GB
- OS: Linux (Ubuntu 20.04+, CentOS 8+, Debian 11+)

**Recommended for Production:**
- CPU: 8+ cores
- RAM: 16+ GB
- Storage: 200+ GB SSD
- OS: Linux (Ubuntu 22.04 LTS)

### Software Requirements

**Required:**
- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.24+ (for K8s deployment)
- kubectl 1.24+
- Git

**Optional:**
- Helm 3.0+ (for Kubernetes)
- Terraform (for infrastructure provisioning)
- Ansible (for configuration management)

### Network Requirements

**Ports:**
- 80 (HTTP)
- 443 (HTTPS)
- 5432 (PostgreSQL - internal)
- 6379 (Redis - internal)
- 8000 (Backend API)
- 3000 (Frontend)
- 9090 (Prometheus - monitoring)
- 3001 (Grafana - monitoring)

**Firewall Rules:**
- Allow inbound: 80, 443
- Allow outbound: 443 (for EMR API calls)
- Internal: 5432, 6379, 8000, 3000

---

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/itechsmart-hl7.git
cd itechsmart-hl7
```

### 2. Install Backend Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 4. Configure Environment

Create `.env` file in the backend directory:

```bash
# Database
DATABASE_URL=postgresql://itechsmart:changeme123@localhost:5432/itechsmart_hl7

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-change-in-production

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# CORS
CORS_ORIGINS=http://localhost:3000
```

### 5. Start Services

**Option A: Using Docker Compose (Recommended)**

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Run database migrations
cd backend
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in another terminal)
cd frontend
npm run dev
```

**Option B: Manual Setup**

```bash
# Install and start PostgreSQL
sudo apt-get install postgresql-15
sudo systemctl start postgresql

# Install and start Redis
sudo apt-get install redis-server
sudo systemctl start redis

# Create database
sudo -u postgres psql
CREATE DATABASE itechsmart_hl7;
CREATE USER itechsmart WITH PASSWORD 'changeme123';
GRANT ALL PRIVILEGES ON DATABASE itechsmart_hl7 TO itechsmart;
\q

# Run migrations
cd backend
alembic upgrade head

# Start services
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
cd frontend && npm run dev
```

### 6. Access Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

---

## Docker Deployment

### 1. Build Images

```bash
# Build backend image
docker build -t itechsmart/hl7-backend:latest -f deployment/Dockerfile .

# Build frontend image
cd frontend
docker build -t itechsmart/hl7-frontend:latest .
```

### 2. Configure Environment

Create `.env` file in the deployment directory:

```bash
# Database
POSTGRES_PASSWORD=your-secure-password

# Redis
REDIS_PASSWORD=your-secure-password

# Security
SECRET_KEY=your-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-min-32-chars

# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=https://yourdomain.com

# EMR Credentials
EPIC_CLIENT_ID=your-epic-client-id
EPIC_CLIENT_SECRET=your-epic-client-secret
CERNER_CLIENT_ID=your-cerner-client-id
CERNER_CLIENT_SECRET=your-cerner-client-secret

# Monitoring
GRAFANA_USER=admin
GRAFANA_PASSWORD=your-grafana-password

# Backup
S3_BACKUP_BUCKET=your-s3-bucket
AWS_REGION=us-east-1
BACKUP_SCHEDULE=0 2 * * *
```

### 3. Start Services

```bash
cd deployment
docker-compose up -d
```

### 4. Verify Deployment

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend

# Check health
curl http://localhost:8000/health
```

### 5. Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create admin user (if needed)
docker-compose exec backend python -m app.scripts.create_admin
```

### 6. Access Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3001

---

## Kubernetes Deployment

### 1. Prerequisites

**Install kubectl:**
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

**Configure kubectl:**
```bash
# For AWS EKS
aws eks update-kubeconfig --region us-east-1 --name your-cluster-name

# For GKE
gcloud container clusters get-credentials your-cluster-name --region us-central1

# For Azure AKS
az aks get-credentials --resource-group your-rg --name your-cluster-name
```

### 2. Prepare Secrets

**Generate base64 encoded secrets:**
```bash
echo -n "your-password" | base64
```

**Update secrets.yaml:**
```bash
cd deployment/kubernetes
vi secrets.yaml
# Replace base64 encoded values with your actual secrets
```

**Important Secrets to Update:**
- `DATABASE_PASSWORD`
- `REDIS_PASSWORD`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `EPIC_CLIENT_ID` and `EPIC_CLIENT_SECRET`
- `CERNER_CLIENT_ID` and `CERNER_CLIENT_SECRET`

### 3. Update ConfigMap

Edit `configmap.yaml` with your configuration:
```bash
vi configmap.yaml
```

Update:
- `CORS_ORIGINS` - Your domain(s)
- `DATABASE_HOST` - If using external database
- `REDIS_HOST` - If using external Redis

### 4. Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Apply configuration
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml

# Deploy database and cache
kubectl apply -f postgres-deployment.yaml
kubectl apply -f redis-deployment.yaml

# Wait for database to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n itechsmart-hl7 --timeout=300s

# Deploy application
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml

# Configure ingress
kubectl apply -f ingress.yaml
```

### 5. Verify Deployment

```bash
# Check pod status
kubectl get pods -n itechsmart-hl7

# Check services
kubectl get svc -n itechsmart-hl7

# Check ingress
kubectl get ingress -n itechsmart-hl7

# View logs
kubectl logs -f deployment/backend -n itechsmart-hl7

# Check rollout status
kubectl rollout status deployment/backend -n itechsmart-hl7
```

### 6. Run Database Migrations

```bash
# Get backend pod name
BACKEND_POD=$(kubectl get pods -n itechsmart-hl7 -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Run migrations
kubectl exec -it $BACKEND_POD -n itechsmart-hl7 -- alembic upgrade head
```

### 7. Access Application

**Get Ingress IP:**
```bash
kubectl get ingress -n itechsmart-hl7
```

**Update DNS:**
- Point your domain to the ingress IP
- Wait for DNS propagation

**Access:**
- https://yourdomain.com

### 8. Configure SSL/TLS

**Option A: Let's Encrypt (Recommended)**

Install cert-manager:
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

Create ClusterIssuer:
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

Apply:
```bash
kubectl apply -f cluster-issuer.yaml
```

**Option B: Custom Certificate**

Create TLS secret:
```bash
kubectl create secret tls itechsmart-tls \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key \
  -n itechsmart-hl7
```

---

## Configuration

### Environment Variables

**Database Configuration:**
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
```

**Redis Configuration:**
```bash
REDIS_URL=redis://:password@host:6379/0
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5
```

**Security Configuration:**
```bash
SECRET_KEY=min-32-character-secret-key
JWT_SECRET_KEY=min-32-character-jwt-secret
JWT_EXPIRATION=3600
PASSWORD_MIN_LENGTH=12
```

**Application Configuration:**
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
API_VERSION=v1
```

**CORS Configuration:**
```bash
CORS_ORIGINS=https://app.example.com,https://admin.example.com
CORS_ALLOW_CREDENTIALS=true
```

**Rate Limiting:**
```bash
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

### EMR Configuration

**Epic:**
```bash
EPIC_BASE_URL=https://fhir.epic.com
EPIC_CLIENT_ID=your-client-id
EPIC_CLIENT_SECRET=your-client-secret
EPIC_TIMEOUT=30
```

**Cerner:**
```bash
CERNER_BASE_URL=https://fhir.cerner.com
CERNER_CLIENT_ID=your-client-id
CERNER_CLIENT_SECRET=your-client-secret
CERNER_TIMEOUT=30
```

---

## Database Setup

### PostgreSQL Configuration

**Recommended Settings (postgresql.conf):**
```ini
# Connection Settings
max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10MB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 4
max_parallel_workers_per_gather = 2
max_parallel_workers = 4
```

### Database Backup

**Automated Backup:**
```bash
# Using provided script
docker-compose exec backup /backup.sh

# Manual backup
docker-compose exec postgres pg_dump -U itechsmart itechsmart_hl7 | gzip > backup.sql.gz
```

**Restore from Backup:**
```bash
# Using provided script
./deployment/restore.sh /backups/postgres_20240115_120000.sql.gz

# Manual restore
gunzip -c backup.sql.gz | docker-compose exec -T postgres psql -U itechsmart itechsmart_hl7
```

### Database Maintenance

**Vacuum:**
```bash
docker-compose exec postgres psql -U itechsmart -d itechsmart_hl7 -c "VACUUM ANALYZE;"
```

**Reindex:**
```bash
docker-compose exec postgres psql -U itechsmart -d itechsmart_hl7 -c "REINDEX DATABASE itechsmart_hl7;"
```

---

## SSL/TLS Configuration

### Nginx SSL Configuration

Create `ssl.conf`:
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_stapling on;
ssl_stapling_verify on;

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Certificate Management

**Let's Encrypt:**
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

**Custom Certificate:**
```bash
# Place certificates
sudo cp your-cert.crt /etc/ssl/certs/
sudo cp your-key.key /etc/ssl/private/

# Update nginx configuration
ssl_certificate /etc/ssl/certs/your-cert.crt;
ssl_certificate_key /etc/ssl/private/your-key.key;
```

---

## Monitoring Setup

### Prometheus Configuration

**Scrape Targets:**
```yaml
scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Grafana Setup

**Access Grafana:**
- URL: http://localhost:3001
- Default: admin / admin123

**Import Dashboards:**
1. Login to Grafana
2. Click "+" → "Import"
3. Upload dashboard JSON from `deployment/grafana/dashboards/`

**Configure Data Source:**
1. Configuration → Data Sources
2. Add Prometheus
3. URL: http://prometheus:9090
4. Save & Test

### Alert Configuration

**Slack Notifications:**
```yaml
# alertmanager.yml
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts'
        title: 'iTechSmart HL7 Alert'
```

---

## Backup Configuration

### Automated Backups

**Configure Backup Schedule:**
```bash
# Edit docker-compose.yml
environment:
  BACKUP_SCHEDULE: "0 2 * * *"  # Daily at 2 AM
  RETENTION_DAYS: 30
```

**S3 Backup:**
```bash
# Configure AWS credentials
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BACKUP_BUCKET=your-bucket-name
AWS_REGION=us-east-1
```

### Disaster Recovery

**Recovery Time Objective (RTO):** < 1 hour  
**Recovery Point Objective (RPO):** < 24 hours

**Recovery Steps:**
1. Provision new infrastructure
2. Deploy application
3. Restore database from backup
4. Verify data integrity
5. Update DNS
6. Test functionality

---

## Troubleshooting

### Common Issues

**Pods Not Starting:**
```bash
# Check pod status
kubectl describe pod <pod-name> -n itechsmart-hl7

# Check logs
kubectl logs <pod-name> -n itechsmart-hl7

# Check events
kubectl get events -n itechsmart-hl7 --sort-by='.lastTimestamp'
```

**Database Connection Issues:**
```bash
# Test connection
kubectl exec -it <backend-pod> -n itechsmart-hl7 -- psql $DATABASE_URL

# Check service
kubectl get svc postgres-service -n itechsmart-hl7

# Check network policy
kubectl get networkpolicy -n itechsmart-hl7
```

**Performance Issues:**
```bash
# Check resource usage
kubectl top pods -n itechsmart-hl7
kubectl top nodes

# Check HPA status
kubectl get hpa -n itechsmart-hl7

# View metrics
kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes
```

### Logs

**View Logs:**
```bash
# Backend logs
kubectl logs -f deployment/backend -n itechsmart-hl7

# All pods
kubectl logs -f -l app=backend -n itechsmart-hl7

# Previous pod instance
kubectl logs <pod-name> -n itechsmart-hl7 --previous
```

**Export Logs:**
```bash
kubectl logs deployment/backend -n itechsmart-hl7 > backend.log
```

### Health Checks

**Check Application Health:**
```bash
curl http://localhost:8000/health
```

**Check Database:**
```bash
kubectl exec -it <postgres-pod> -n itechsmart-hl7 -- pg_isready
```

**Check Redis:**
```bash
kubectl exec -it <redis-pod> -n itechsmart-hl7 -- redis-cli ping
```

---

## Production Checklist

### Pre-Deployment

- [ ] Update all secrets in `secrets.yaml`
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure backup schedule
- [ ] Set up monitoring and alerting
- [ ] Configure log aggregation
- [ ] Review resource limits
- [ ] Test disaster recovery procedure
- [ ] Document custom configurations
- [ ] Train operations team

### Post-Deployment

- [ ] Verify all pods are running
- [ ] Test application functionality
- [ ] Verify EMR connections
- [ ] Test backup and restore
- [ ] Verify monitoring and alerts
- [ ] Check SSL certificate
- [ ] Review security settings
- [ ] Load test application
- [ ] Document deployment
- [ ] Schedule maintenance windows

---

## Support

For deployment support:
- **Email:** devops@itechsmart.dev
- **Documentation:** https://docs.itechsmart.dev/deployment
- **Slack:** #deployment-support

---

**Last Updated:** January 15, 2024  
**Version:** 1.0.0