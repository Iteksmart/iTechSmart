# iTechSmart Ninja - Deployment Guide

## 🚀 Complete Deployment Guide for Production

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Cloud Deployments](#cloud-deployments)
6. [Database Setup](#database-setup)
7. [Security Configuration](#security-configuration)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)

---

## 1. Prerequisites

### System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB SSD
- Network: 100Mbps

**Recommended:**
- CPU: 8+ cores
- RAM: 16GB+
- Storage: 200GB+ SSD
- Network: 1Gbps

### Software Requirements

- Docker 24.0+
- Docker Compose 2.20+
- Kubernetes 1.28+ (for K8s deployment)
- PostgreSQL 14+
- Redis 7+
- Python 3.11+

---

## 2. Environment Setup

### Environment Variables

Create `.env` file:

```bash
# Application
APP_NAME=iTechSmart Ninja
APP_ENV=production
DEBUG=false
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/itechsmart_ninja
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50

# API Keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_AI_API_KEY=your-google-key

# AWS (for S3 storage)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET=itechsmart-ninja-storage

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password

# Security
JWT_SECRET=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# Monitoring
SENTRY_DSN=your-sentry-dsn
PROMETHEUS_PORT=9090
```

---

## 3. Docker Deployment

### Docker Compose Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: itechsmart_ninja
      POSTGRES_USER: ninja_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ninja_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Application
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://ninja_user:${DB_PASSWORD}@postgres:5432/itechsmart_ninja
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./workspace:/workspace
    restart: unless-stopped

  # Celery Worker
  celery_worker:
    build: .
    command: celery -A app.celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://ninja_user:${DB_PASSWORD}@postgres:5432/itechsmart_ninja
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create workspace directory
RUN mkdir -p /workspace

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Deploy with Docker Compose

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale workers
docker-compose up -d --scale celery_worker=4

# Stop services
docker-compose down
```

---

## 4. Kubernetes Deployment

### Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: itechsmart-ninja
```

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: itechsmart-ninja
data:
  APP_ENV: "production"
  DEBUG: "false"
  REDIS_URL: "redis://redis-service:6379/0"
```

### Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: itechsmart-ninja
type: Opaque
stringData:
  DATABASE_URL: "postgresql://user:password@postgres:5432/db"
  SECRET_KEY: "your-secret-key"
  OPENAI_API_KEY: "your-openai-key"
```

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: itechsmart-ninja
  namespace: itechsmart-ninja
spec:
  replicas: 3
  selector:
    matchLabels:
      app: itechsmart-ninja
  template:
    metadata:
      labels:
        app: itechsmart-ninja
    spec:
      containers:
      - name: app
        image: itechsmart-ninja:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DATABASE_URL
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: REDIS_URL
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: itechsmart-ninja-service
  namespace: itechsmart-ninja
spec:
  selector:
    app: itechsmart-ninja
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: itechsmart-ninja-ingress
  namespace: itechsmart-ninja
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.itechsmart-ninja.com
    secretName: tls-secret
  rules:
  - host: api.itechsmart-ninja.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: itechsmart-ninja-service
            port:
              number: 80
```

### Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Check status
kubectl get pods -n itechsmart-ninja
kubectl get services -n itechsmart-ninja

# View logs
kubectl logs -f deployment/itechsmart-ninja -n itechsmart-ninja

# Scale deployment
kubectl scale deployment itechsmart-ninja --replicas=5 -n itechsmart-ninja
```

---

## 5. Cloud Deployments

### AWS Deployment

#### ECS with Fargate

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name itechsmart-ninja

# Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster itechsmart-ninja \
  --service-name ninja-service \
  --task-definition ninja-task \
  --desired-count 3 \
  --launch-type FARGATE
```

#### RDS Setup

```bash
# Create PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier ninja-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username admin \
  --master-user-password ${DB_PASSWORD} \
  --allocated-storage 100
```

### GCP Deployment

#### GKE Setup

```bash
# Create GKE cluster
gcloud container clusters create itechsmart-ninja \
  --num-nodes=3 \
  --machine-type=n1-standard-4 \
  --zone=us-central1-a

# Deploy application
kubectl apply -f k8s/
```

#### Cloud SQL

```bash
# Create PostgreSQL instance
gcloud sql instances create ninja-db \
  --database-version=POSTGRES_14 \
  --tier=db-n1-standard-2 \
  --region=us-central1
```

### Azure Deployment

#### AKS Setup

```bash
# Create AKS cluster
az aks create \
  --resource-group ninja-rg \
  --name itechsmart-ninja \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3

# Get credentials
az aks get-credentials \
  --resource-group ninja-rg \
  --name itechsmart-ninja
```

---

## 6. Database Setup

### PostgreSQL Configuration

```sql
-- Create database
CREATE DATABASE itechsmart_ninja;

-- Create user
CREATE USER ninja_user WITH PASSWORD 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE itechsmart_ninja TO ninja_user;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

### Run Migrations

```bash
# Install Alembic
pip install alembic

# Initialize migrations
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

---

## 7. Security Configuration

### SSL/TLS Setup

```bash
# Generate SSL certificate with Let's Encrypt
certbot certonly --standalone -d api.itechsmart-ninja.com

# Configure Nginx
server {
    listen 443 ssl http2;
    server_name api.itechsmart-ninja.com;
    
    ssl_certificate /etc/letsencrypt/live/api.itechsmart-ninja.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.itechsmart-ninja.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```

### Firewall Rules

```bash
# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow SSH (from specific IP)
ufw allow from YOUR_IP to any port 22

# Enable firewall
ufw enable
```

---

## 8. Monitoring & Logging

### Prometheus Setup

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'itechsmart-ninja'
    static_configs:
      - targets: ['app:8000']
```

### Grafana Dashboard

```bash
# Install Grafana
docker run -d -p 3000:3000 grafana/grafana

# Access: http://localhost:3000
# Default credentials: admin/admin
```

### ELK Stack

```yaml
# docker-compose.yml for ELK
services:
  elasticsearch:
    image: elasticsearch:8.10.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: logstash:8.10.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: kibana:8.10.0
    ports:
      - "5601:5601"
```

---

## 9. Backup & Recovery

### Database Backup

```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
pg_dump -h localhost -U ninja_user itechsmart_ninja > \
  $BACKUP_DIR/db_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/db_backup_$DATE.sql.gz \
  s3://ninja-backups/database/

# Keep only last 30 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete
```

### Restore Database

```bash
# Download from S3
aws s3 cp s3://ninja-backups/database/db_backup_20250101.sql.gz .

# Decompress
gunzip db_backup_20250101.sql.gz

# Restore
psql -h localhost -U ninja_user itechsmart_ninja < db_backup_20250101.sql
```

---

## 10. Troubleshooting

### Common Issues

**Issue: Database connection failed**
```bash
# Check database status
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Test connection
psql -h localhost -U ninja_user -d itechsmart_ninja
```

**Issue: High memory usage**
```bash
# Check memory usage
docker stats

# Restart services
docker-compose restart

# Scale down if needed
docker-compose up -d --scale celery_worker=2
```

**Issue: Slow API responses**
```bash
# Check Redis connection
redis-cli ping

# Monitor queries
docker-compose exec postgres psql -U ninja_user -d itechsmart_ninja \
  -c "SELECT * FROM pg_stat_activity;"

# Enable query logging
# In postgresql.conf: log_min_duration_statement = 1000
```

---

## 📞 Support

For deployment assistance:
- Email: devops@itechsmart-ninja.com
- Documentation: https://docs.itechsmart-ninja.com/deployment
- Community: https://community.itechsmart-ninja.com

---

**Last Updated:** 2025  
**Version:** 1.0.0