# iTechSmart Suite - Production Deployment Guide

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Infrastructure Setup](#infrastructure-setup)
4. [Database Configuration](#database-configuration)
5. [Service Deployment](#service-deployment)
6. [Monitoring & Logging](#monitoring--logging)
7. [Security Hardening](#security-hardening)
8. [Backup & Recovery](#backup--recovery)
9. [Scaling Strategy](#scaling-strategy)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- Docker 24.0+
- Docker Compose 2.20+
- Kubernetes 1.28+ (for production)
- PostgreSQL 15+
- Redis 7+
- Apache Kafka 3.5+ (optional, for Analytics)
- Node.js 20+ (for frontend)
- Python 3.11+

### Cloud Provider Requirements
- **AWS**: ECS/EKS, RDS, ElastiCache, S3
- **Azure**: AKS, Azure Database, Azure Cache, Blob Storage
- **GCP**: GKE, Cloud SQL, Memorystore, Cloud Storage

### Domain & SSL
- Domain name configured
- SSL certificates (Let's Encrypt or commercial)
- DNS records configured

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer (NGINX)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
┌───────────────▼──────────────┐  ┌────────▼─────────────────┐
│   iTechSmart Enterprise      │  │  iTechSmart Analytics    │
│   (Integration Hub)          │  │  (Analytics Platform)    │
└───────────────┬──────────────┘  └────────┬─────────────────┘
                │                           │
    ┌───────────┼───────────────────────────┼───────────┐
    │           │                           │           │
┌───▼───┐  ┌───▼───┐  ┌────────┐  ┌───────▼───┐  ┌────▼────┐
│ Ninja │  │Supreme│  │  HL7   │  │ ProofLink │  │ PassPort│
└───────┘  └───────┘  └────────┘  └───────────┘  └─────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼────┐ ┌───▼────┐ ┌───▼────┐
│ImpactOS│ │FitSnap │ │ Future │
└────────┘ └────────┘ └────────┘

┌─────────────────────────────────────────────────────────────┐
│              Shared Infrastructure Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PostgreSQL│  │  Redis   │  │  Kafka   │  │   S3     │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Infrastructure Setup

### 1. Docker Compose (Development/Staging)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: itechsmart
      POSTGRES_USER: itechsmart
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U itechsmart"]
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

  # Apache Kafka (Optional)
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
    ports:
      - "9092:9092"
    depends_on:
      - zookeeper

  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    ports:
      - "2181:2181"

  # iTechSmart Enterprise
  enterprise:
    build: ./itechsmart-enterprise
    environment:
      DATABASE_URL: postgresql://itechsmart:${DB_PASSWORD}@postgres:5432/itechsmart
      REDIS_URL: redis://redis:6379
      SECRET_KEY: ${SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # iTechSmart Analytics
  analytics:
    build: ./itechsmart-analytics
    environment:
      DATABASE_URL: postgresql://itechsmart:${DB_PASSWORD}@postgres:5432/itechsmart
      REDIS_URL: redis://redis:6379
      KAFKA_BROKERS: kafka:9092
      ENTERPRISE_API_URL: http://enterprise:8000
      SECRET_KEY: ${SECRET_KEY}
    ports:
      - "8001:8000"
    depends_on:
      - postgres
      - redis
      - kafka
      - enterprise

  # iTechSmart Ninja
  ninja:
    build: ./itechsmart-ninja
    environment:
      DATABASE_URL: postgresql://itechsmart:${DB_PASSWORD}@postgres:5432/itechsmart
      ENTERPRISE_API_URL: http://enterprise:8000
      SECRET_KEY: ${SECRET_KEY}
    ports:
      - "8002:8000"
    depends_on:
      - enterprise

  # NGINX Load Balancer
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - enterprise
      - analytics

volumes:
  postgres_data:
  redis_data:
```

### 2. Kubernetes Deployment (Production)

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: itechsmart-enterprise
  namespace: itechsmart
spec:
  replicas: 3
  selector:
    matchLabels:
      app: enterprise
  template:
    metadata:
      labels:
        app: enterprise
    spec:
      containers:
      - name: enterprise
        image: itechsmart/enterprise:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: itechsmart-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: itechsmart-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: enterprise-service
  namespace: itechsmart
spec:
  selector:
    app: enterprise
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## Database Configuration

### 1. PostgreSQL Setup

```sql
-- Create database
CREATE DATABASE itechsmart;

-- Create user
CREATE USER itechsmart WITH PASSWORD 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE itechsmart TO itechsmart;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "timescaledb";
```

### 2. Database Migrations

```bash
# Run migrations for each service
cd itechsmart-enterprise/backend
alembic upgrade head

cd itechsmart-analytics/backend
alembic upgrade head
```

### 3. Database Backup

```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/itechsmart_$DATE.sql"

pg_dump -h localhost -U itechsmart itechsmart > $BACKUP_FILE
gzip $BACKUP_FILE

# Upload to S3
aws s3 cp $BACKUP_FILE.gz s3://itechsmart-backups/postgres/
```

---

## Service Deployment

### 1. Build Docker Images

```bash
# Build all services
docker-compose build

# Or build individually
docker build -t itechsmart/enterprise:latest ./itechsmart-enterprise
docker build -t itechsmart/analytics:latest ./itechsmart-analytics
docker build -t itechsmart/ninja:latest ./itechsmart-ninja
```

### 2. Deploy Services

```bash
# Using Docker Compose
docker-compose up -d

# Using Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

### 3. Verify Deployment

```bash
# Check service health
curl http://localhost:8000/health
curl http://localhost:8001/health

# Check Kubernetes pods
kubectl get pods -n itechsmart
kubectl logs -f <pod-name> -n itechsmart
```

---

## Monitoring & Logging

### 1. Prometheus Setup

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'itechsmart-enterprise'
    static_configs:
      - targets: ['enterprise:8000']
  
  - job_name: 'itechsmart-analytics'
    static_configs:
      - targets: ['analytics:8000']
```

### 2. Grafana Dashboards

Import pre-built dashboards for:
- System metrics (CPU, Memory, Disk)
- Application metrics (Request rate, Response time, Error rate)
- Database metrics (Connections, Query performance)
- Business metrics (User activity, Revenue, Conversions)

### 3. Logging with ELK Stack

```yaml
# filebeat.yml
filebeat.inputs:
- type: container
  paths:
    - '/var/lib/docker/containers/*/*.log'

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

---

## Security Hardening

### 1. SSL/TLS Configuration

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name itechsmart.dev;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://enterprise:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Firewall Rules

```bash
# Allow only necessary ports
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable
```

### 3. Secret Management

```bash
# Using AWS Secrets Manager
aws secretsmanager create-secret \
    --name itechsmart/database \
    --secret-string '{"username":"itechsmart","password":"secure_password"}'
```

---

## Backup & Recovery

### 1. Automated Backups

```bash
# Cron job for daily backups
0 2 * * * /scripts/backup.sh
```

### 2. Disaster Recovery Plan

1. **Database Recovery**: Restore from latest backup
2. **Service Recovery**: Redeploy from Docker images
3. **Data Recovery**: Restore from S3 backups
4. **RTO**: 4 hours
5. **RPO**: 24 hours

---

## Scaling Strategy

### 1. Horizontal Scaling

```bash
# Scale services in Kubernetes
kubectl scale deployment enterprise --replicas=5 -n itechsmart
kubectl scale deployment analytics --replicas=3 -n itechsmart
```

### 2. Auto-scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: enterprise-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: itechsmart-enterprise
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database connectivity
   psql -h localhost -U itechsmart -d itechsmart
   ```

2. **Service Not Starting**
   ```bash
   # Check logs
   docker-compose logs enterprise
   kubectl logs <pod-name> -n itechsmart
   ```

3. **High Memory Usage**
   ```bash
   # Check resource usage
   docker stats
   kubectl top pods -n itechsmart
   ```

---

## Support

For deployment assistance:
- Email: devops@itechsmart.dev
- Slack: #itechsmart-deployment
- Documentation: https://docs.itechsmart.dev/deployment