# Passport - Deployment Guide

**Version**: 1.0.0  
**Last Updated**: November 17, 2025  
**Deployment Type**: Docker, Kubernetes, Manual

---

## 📚 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Manual Deployment](#manual-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Scaling](#scaling)
7. [Monitoring](#monitoring)
8. [Backup & Recovery](#backup--recovery)
9. [Security](#security)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Production Environment**:
- CPU: 8+ cores
- RAM: 16+ GB
- Storage: 100+ GB SSD
- Network: 1 Gbps
- OS: Ubuntu 22.04 LTS or similar

### Software Requirements

- Docker 24.0+
- Docker Compose 2.20+
- Kubernetes 1.28+ (for K8s deployment)
- PostgreSQL 15+ (if external)
- Redis 7+ (if external)

---

## Docker Deployment

### Quick Start

```bash
# Clone repository
git clone https://github.com/Iteksmart/iTechSmart.git
cd iTechSmart/passport

# Configure environment
cp .env.example .env
nano .env

# Start services
docker-compose up -d

# Verify deployment
docker-compose ps
docker-compose logs -f
```

### Production Configuration

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  passport:
    image: itechsmart/Passport:latest
    restart: always
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    networks:
      - itechsmart-network
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      - POSTGRES_DB=$passport
      - POSTGRES_USER=$postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - itechsmart-network

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis-data:/data
    networks:
      - itechsmart-network

volumes:
  postgres-data:
  redis-data:

networks:
  itechsmart-network:
    driver: bridge
```

### Deploy to Production

```bash
# Build images
docker-compose -f docker-compose.production.yml build

# Start services
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

---

## Kubernetes Deployment

### Namespace Setup

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: passport
```

### Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: Passport
  namespace: passport
spec:
  replicas: 3
  selector:
    matchLabels:
      app: Passport
  template:
    metadata:
      labels:
        app: Passport
    spec:
      containers:
      - name: Passport
        image: itechsmart/Passport:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: Passport-secrets
              key: database-url
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
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
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: Passport
  namespace: passport
spec:
  selector:
    app: Passport
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: Passport
  namespace: passport
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - passport.itechsmart.com
    secretName: Passport-tls
  rules:
  - host: passport.itechsmart.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: Passport
            port:
              number: 80
```

### Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f namespace.yaml
kubectl apply -f secrets.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Check status
kubectl get pods -n passport
kubectl get svc -n passport
kubectl get ingress -n passport

# View logs
kubectl logs -f deployment/Passport -n passport
```

---

## Manual Deployment

### Install Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip postgresql-client

# Install runtime
pip install -r requirements.txt
```

### Build Application

```bash
# Clone repository
git clone https://github.com/Iteksmart/iTechSmart.git
cd iTechSmart/passport

# Install dependencies
pip install -r requirements.txt

# Build application
# No build needed for Python
```

### Configure Service

```bash
# Create systemd service
sudo nano /etc/systemd/system/Passport.service
```

```ini
[Unit]
Description=Passport Service
After=network.target

[Service]
Type=simple
User=passport
WorkingDirectory=/opt/Passport
ExecStart=/usr/bin/python3 /opt/passport/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable Passport

# Start service
sudo systemctl start Passport

# Check status
sudo systemctl status Passport
```

---

## Environment Configuration

### Required Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Application
NODE_ENV=production
PORT=8000
SECRET_KEY=your-secret-key-here

# API Keys
# Add API keys if needed

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Storage
STORAGE_TYPE=local|s3|gcs
STORAGE_PATH=/data/files

# Security
JWT_SECRET=your-jwt-secret
JWT_EXPIRATION=3600
ENABLE_2FA=true
```

### Optional Variables

```env
# Monitoring
SENTRY_DSN=https://...
DATADOG_API_KEY=...

# Feature Flags
ENABLE_FEATURE_X=true
ENABLE_FEATURE_Y=false

# Performance
MAX_WORKERS=4
CACHE_TTL=3600
RATE_LIMIT=100
```

---

## Scaling

### Horizontal Scaling

```bash
# Docker Compose
docker-compose up -d --scale passport=5

# Kubernetes
kubectl scale deployment/Passport --replicas=5 -n passport
```

### Auto-Scaling (Kubernetes)

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: Passport
  namespace: passport
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: Passport
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Monitoring

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health

# Check readiness
curl http://localhost:8000/ready
```

### Prometheus Metrics

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'Passport'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics
```

### Logging

```bash
# Docker logs
docker-compose logs -f passport

# Kubernetes logs
kubectl logs -f deployment/Passport -n passport

# System logs
sudo journalctl -u Passport -f
```

---

## Backup & Recovery

### Database Backup

```bash
# Backup PostgreSQL
docker exec passport-postgres pg_dump -U postgres passport > backup.sql

# Restore PostgreSQL
docker exec -i passport-postgres psql -U postgres passport < backup.sql
```

### File Backup

```bash
# Backup files
tar -czf backup-$(date +%Y%m%d).tar.gz /path/to/data

# Restore files
tar -xzf backup-20251117.tar.gz -C /path/to/restore
```

### Automated Backups

```bash
# Create backup script
cat > /opt/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups

# Backup database
docker exec postgres pg_dump -U user dbname > $BACKUP_DIR/db_$DATE.sql

# Backup files
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /data

# Remove old backups (keep 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /opt/backup.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /opt/backup.sh
```

---

## Security

### SSL/TLS Configuration

```bash
# Generate SSL certificate with Let's Encrypt
sudo certbot certonly --standalone -d passport.itechsmart.com

# Configure nginx
server {
    listen 443 ssl http2;
    server_name passport.itechsmart.com;
    
    ssl_certificate /etc/letsencrypt/live/passport.itechsmart.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/passport.itechsmart.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Firewall Configuration

```bash
# Configure UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Security Headers

```nginx
# Add security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000" always;
```

---

## Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check logs
docker-compose logs passport

# Check configuration
docker-compose config

# Verify environment variables
docker-compose exec passport env
```

#### Database Connection Failed

```bash
# Check database status
docker-compose ps postgres

# Test connection
docker-compose exec passport psql -h postgres -U user -d dbname

# Check network
docker network ls
docker network inspect passport-network
```

#### High Memory Usage

```bash
# Check resource usage
docker stats

# Adjust memory limits
# Edit docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
```

### Performance Optimization

```bash
# Enable caching
REDIS_URL=redis://redis:6379/0

# Increase workers
MAX_WORKERS=8

# Enable compression
ENABLE_GZIP=true
```

---

## Support

- **Documentation**: https://docs.itechsmart.com
- **Status Page**: https://status.itechsmart.com
- **Support Email**: support@itechsmart.com
- **GitHub Issues**: https://github.com/Iteksmart/iTechSmart/issues

---

**End of Deployment Guide**