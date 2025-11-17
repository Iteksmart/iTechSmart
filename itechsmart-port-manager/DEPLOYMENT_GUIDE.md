# iTechSmart Port Manager - Deployment Guide

## Overview

This guide covers deploying iTechSmart Port Manager in various environments.

---

## Deployment Options

1. **Docker Compose** (Recommended for development/staging)
2. **Kubernetes** (Recommended for production)
3. **Manual Deployment** (For custom setups)

---

## Docker Compose Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

### Step 1: Create docker-compose.yml

```yaml
version: '3.8'

services:
  port-manager-backend:
    build: ./backend
    container_name: itechsmart-port-manager-backend
    ports:
      - "8100:8100"
    environment:
      - PORT=8100
      - HUB_URL=http://itechsmart-enterprise:8001
      - NINJA_URL=http://itechsmart-ninja:8002
      - ENABLE_HUB=true
      - ENABLE_NINJA=true
    volumes:
      - ./data:/app/data
    networks:
      - itechsmart-network
    restart: unless-stopped

  port-manager-frontend:
    build: ./frontend
    container_name: itechsmart-port-manager-frontend
    ports:
      - "3000:80"
    depends_on:
      - port-manager-backend
    networks:
      - itechsmart-network
    restart: unless-stopped

networks:
  itechsmart-network:
    external: true
```

### Step 2: Create Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8100

CMD ["python", "-m", "app.main"]
```

### Step 3: Create Frontend Dockerfile

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Step 4: Deploy

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build
```

---

## Kubernetes Deployment

### Prerequisites
- Kubernetes 1.24+
- kubectl configured
- Helm 3.0+ (optional)

### Step 1: Create Namespace

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: itechsmart-port-manager
```

```bash
kubectl apply -f namespace.yaml
```

### Step 2: Create ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: port-manager-config
  namespace: itechsmart-port-manager
data:
  PORT: "8100"
  HUB_URL: "http://itechsmart-enterprise:8001"
  NINJA_URL: "http://itechsmart-ninja:8002"
  ENABLE_HUB: "true"
  ENABLE_NINJA: "true"
```

```bash
kubectl apply -f configmap.yaml
```

### Step 3: Create Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: port-manager-backend
  namespace: itechsmart-port-manager
spec:
  replicas: 2
  selector:
    matchLabels:
      app: port-manager-backend
  template:
    metadata:
      labels:
        app: port-manager-backend
    spec:
      containers:
      - name: backend
        image: itechsmart/port-manager-backend:latest
        ports:
        - containerPort: 8100
        envFrom:
        - configMapRef:
            name: port-manager-config
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8100
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8100
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: port-manager-frontend
  namespace: itechsmart-port-manager
spec:
  replicas: 2
  selector:
    matchLabels:
      app: port-manager-frontend
  template:
    metadata:
      labels:
        app: port-manager-frontend
    spec:
      containers:
      - name: frontend
        image: itechsmart/port-manager-frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

```bash
kubectl apply -f deployment.yaml
```

### Step 4: Create Service

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: port-manager-backend
  namespace: itechsmart-port-manager
spec:
  selector:
    app: port-manager-backend
  ports:
  - protocol: TCP
    port: 8100
    targetPort: 8100
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: port-manager-frontend
  namespace: itechsmart-port-manager
spec:
  selector:
    app: port-manager-frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: LoadBalancer
```

```bash
kubectl apply -f service.yaml
```

### Step 5: Create Ingress (Optional)

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: port-manager-ingress
  namespace: itechsmart-port-manager
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - port-manager.itechsmart.dev
    secretName: port-manager-tls
  rules:
  - host: port-manager.itechsmart.dev
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: port-manager-frontend
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: port-manager-backend
            port:
              number: 8100
```

```bash
kubectl apply -f ingress.yaml
```

### Step 6: Verify Deployment

```bash
# Check pods
kubectl get pods -n itechsmart-port-manager

# Check services
kubectl get svc -n itechsmart-port-manager

# Check logs
kubectl logs -f deployment/port-manager-backend -n itechsmart-port-manager

# Get external IP
kubectl get svc port-manager-frontend -n itechsmart-port-manager
```

---

## Manual Deployment

### Backend Deployment

```bash
# 1. Install dependencies
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
export PORT=8100
export HUB_URL=http://itechsmart-enterprise:8001
export NINJA_URL=http://itechsmart-ninja:8002

# 3. Run with gunicorn (production)
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8100 \
  --access-logfile - \
  --error-logfile -

# Or run with uvicorn (development)
uvicorn app.main:app --host 0.0.0.0 --port 8100 --reload
```

### Frontend Deployment

```bash
# 1. Install dependencies
cd frontend
npm install

# 2. Build for production
npm run build

# 3. Serve with nginx
# Copy dist/ to /var/www/html/port-manager

# 4. Configure nginx
cat > /etc/nginx/sites-available/port-manager << 'EOF'
server {
    listen 80;
    server_name port-manager.itechsmart.dev;
    
    root /var/www/html/port-manager;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8100;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    location /ws {
        proxy_pass http://localhost:8100;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
EOF

# 5. Enable site
ln -s /etc/nginx/sites-available/port-manager /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

---

## Production Configuration

### Backend Production Settings

```python
# app/config.py
import os

class ProductionConfig:
    PORT = int(os.getenv('PORT', 8100))
    HOST = os.getenv('HOST', '0.0.0.0')
    WORKERS = int(os.getenv('WORKERS', 4))
    
    # Hub/Ninja
    HUB_URL = os.getenv('HUB_URL', 'http://itechsmart-enterprise:8001')
    NINJA_URL = os.getenv('NINJA_URL', 'http://itechsmart-ninja:8002')
    ENABLE_HUB = os.getenv('ENABLE_HUB', 'true').lower() == 'true'
    ENABLE_NINJA = os.getenv('ENABLE_NINJA', 'true').lower() == 'true'
    
    # Port Range
    PORT_RANGE_START = int(os.getenv('PORT_RANGE_START', 8000))
    PORT_RANGE_END = int(os.getenv('PORT_RANGE_END', 9000))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Security
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
```

### Systemd Service (Linux)

```ini
# /etc/systemd/system/port-manager.service
[Unit]
Description=iTechSmart Port Manager
After=network.target

[Service]
Type=simple
User=itechsmart
WorkingDirectory=/opt/itechsmart-port-manager/backend
Environment="PATH=/opt/itechsmart-port-manager/backend/venv/bin"
ExecStart=/opt/itechsmart-port-manager/backend/venv/bin/gunicorn \
  app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8100
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
systemctl enable port-manager
systemctl start port-manager
systemctl status port-manager
```

---

## Monitoring & Logging

### Prometheus Metrics

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'port-manager'
    static_configs:
      - targets: ['localhost:8100']
    metrics_path: '/metrics'
```

### Grafana Dashboard

Import dashboard JSON from `/monitoring/grafana-dashboard.json`

### Log Aggregation

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/port-manager/*.log
  fields:
    service: port-manager
    
output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

---

## Backup & Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/port-manager"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup via API
curl -X POST http://localhost:8100/api/ports/backup

# Copy to backup directory
cp port_config_backup_*.json $BACKUP_DIR/backup_$DATE.json

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.json" -mtime +30 -delete
```

### Cron Job

```bash
# Add to crontab
0 2 * * * /opt/itechsmart-port-manager/backup.sh
```

### Recovery

```bash
# List backups
ls -lh /backups/port-manager/

# Restore from backup
curl -X POST "http://localhost:8100/api/ports/restore?backup_file=/backups/port-manager/backup_20251212_020000.json"
```

---

## Security Hardening

### 1. Enable HTTPS

```nginx
server {
    listen 443 ssl http2;
    server_name port-manager.itechsmart.dev;
    
    ssl_certificate /etc/ssl/certs/port-manager.crt;
    ssl_certificate_key /etc/ssl/private/port-manager.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # ... rest of config
}
```

### 2. Firewall Rules

```bash
# Allow only necessary ports
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8100/tcp  # Backend (internal only)
ufw enable
```

### 3. Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://localhost:8100;
}
```

---

## Performance Tuning

### Backend Optimization

```python
# Increase workers
gunicorn app.main:app \
  --workers 8 \
  --worker-class uvicorn.workers.UvicornWorker \
  --worker-connections 1000 \
  --max-requests 10000 \
  --max-requests-jitter 1000
```

### Database Optimization

```python
# Use connection pooling
# Enable caching for frequently accessed data
# Index commonly queried fields
```

### Frontend Optimization

```bash
# Enable gzip compression
# Use CDN for static assets
# Implement caching headers
# Minify and bundle assets
```

---

## Troubleshooting

### Backend Not Starting

```bash
# Check logs
journalctl -u port-manager -f

# Check port availability
netstat -tulpn | grep 8100

# Test configuration
python -m app.main --test
```

### Frontend Not Loading

```bash
# Check nginx status
systemctl status nginx

# Check nginx logs
tail -f /var/log/nginx/error.log

# Test nginx config
nginx -t
```

### WebSocket Issues

```bash
# Check WebSocket connection
wscat -c ws://localhost:8100/ws/updates

# Verify nginx WebSocket config
# Ensure Upgrade headers are set
```

---

## Scaling

### Horizontal Scaling

```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: port-manager-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: port-manager-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Load Balancing

```nginx
upstream port_manager_backend {
    least_conn;
    server backend1:8100;
    server backend2:8100;
    server backend3:8100;
}

server {
    location /api {
        proxy_pass http://port_manager_backend;
    }
}
```

---

## Summary

iTechSmart Port Manager can be deployed in multiple ways:
- ✅ Docker Compose for quick setup
- ✅ Kubernetes for production scale
- ✅ Manual deployment for custom needs
- ✅ Full monitoring and logging
- ✅ Automated backups
- ✅ Security hardening
- ✅ Performance optimization

**Status:** 🎉 **Production Ready** 🎉