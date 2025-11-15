# iTechSmart Sandbox - Deployment Guide

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Local Development](#local-development)
4. [Docker Deployment](#docker-deployment)
5. [Production Deployment](#production-deployment)
6. [Configuration](#configuration)
7. [Monitoring](#monitoring)
8. [Backup & Recovery](#backup--recovery)
9. [Scaling](#scaling)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers deploying iTechSmart Sandbox in various environments, from local development to production.

### Architecture Components

- **Frontend**: React + TypeScript (Port 3033)
- **Backend**: FastAPI + Python (Port 8033)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Container Runtime**: Docker

---

## Prerequisites

### System Requirements

#### Minimum Requirements
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disk**: 50 GB SSD
- **OS**: Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)

#### Recommended Requirements
- **CPU**: 8+ cores
- **RAM**: 16+ GB
- **Disk**: 100+ GB SSD
- **OS**: Ubuntu 22.04 LTS
- **GPU**: Optional (NVIDIA with CUDA support)

### Software Requirements

- Docker 24.0+
- Docker Compose 2.20+
- Git 2.30+
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Network Requirements

- Ports 3033 (frontend), 8033 (backend) available
- Internet access for pulling Docker images
- Firewall configured to allow required ports

---

## Local Development

### Backend Setup

```bash
# Navigate to backend directory
cd itechsmart-sandbox/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn main:app --host 0.0.0.0 --port 8033 --reload
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd itechsmart-sandbox/frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start the development server
npm run dev
```

### Database Setup

```bash
# Start PostgreSQL with Docker
docker run -d \
  --name sandbox-postgres \
  -e POSTGRES_USER=sandbox_user \
  -e POSTGRES_PASSWORD=sandbox_pass \
  -e POSTGRES_DB=sandbox_db \
  -p 5432:5432 \
  postgres:15-alpine

# Start Redis with Docker
docker run -d \
  --name sandbox-redis \
  -p 6379:6379 \
  redis:7-alpine
```

---

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Navigate to project root
cd itechsmart-sandbox

# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### Individual Container Deployment

#### Backend

```bash
cd itechsmart-sandbox/backend

# Build image
docker build -t itechsmart-sandbox-backend .

# Run container
docker run -d \
  --name sandbox-backend \
  -p 8033:8033 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REDIS_URL=redis://host:6379 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  itechsmart-sandbox-backend
```

#### Frontend

```bash
cd itechsmart-sandbox/frontend

# Build image
docker build -t itechsmart-sandbox-frontend .

# Run container
docker run -d \
  --name sandbox-frontend \
  -p 3033:3033 \
  -e VITE_API_URL=http://localhost:8033 \
  itechsmart-sandbox-frontend
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Update all environment variables
- [ ] Configure SSL/TLS certificates
- [ ] Set up database backups
- [ ] Configure monitoring and logging
- [ ] Review security settings
- [ ] Test disaster recovery procedures
- [ ] Document deployment process

### Environment Variables

Create a `.env.production` file:

```env
# Backend Configuration
DATABASE_URL=postgresql://user:password@db-host:5432/sandbox_db
REDIS_URL=redis://redis-host:6379
SECRET_KEY=your-super-secret-key-change-this
ENVIRONMENT=production
DEBUG=false

# Security
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com

# Docker Configuration
DOCKER_HOST=unix:///var/run/docker.sock
MAX_SANDBOXES=100
DEFAULT_TTL=3600

# Frontend Configuration
VITE_API_URL=https://api.yourdomain.com
VITE_ENV=production
```

### SSL/TLS Configuration

#### Using Nginx as Reverse Proxy

```nginx
# /etc/nginx/sites-available/sandbox

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Frontend
    location / {
        proxy_pass http://localhost:3033;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8033;
        proxy_http_version 1.1;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Database Configuration

#### PostgreSQL Production Settings

```sql
-- Create production database
CREATE DATABASE sandbox_db;
CREATE USER sandbox_user WITH ENCRYPTED PASSWORD 'strong-password';
GRANT ALL PRIVILEGES ON DATABASE sandbox_db TO sandbox_user;

-- Performance tuning
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET work_mem = '10MB';
ALTER SYSTEM SET min_wal_size = '1GB';
ALTER SYSTEM SET max_wal_size = '4GB';

-- Restart PostgreSQL
SELECT pg_reload_conf();
```

### Systemd Service Files

#### Backend Service

```ini
# /etc/systemd/system/sandbox-backend.service

[Unit]
Description=iTechSmart Sandbox Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=sandbox
WorkingDirectory=/opt/itechsmart-sandbox/backend
Environment="PATH=/opt/itechsmart-sandbox/backend/venv/bin"
ExecStart=/opt/itechsmart-sandbox/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8033
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Frontend Service

```ini
# /etc/systemd/system/sandbox-frontend.service

[Unit]
Description=iTechSmart Sandbox Frontend
After=network.target

[Service]
Type=simple
User=sandbox
WorkingDirectory=/opt/itechsmart-sandbox/frontend
ExecStart=/usr/bin/npm run preview -- --port 3033 --host 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start services:

```bash
sudo systemctl enable sandbox-backend sandbox-frontend
sudo systemctl start sandbox-backend sandbox-frontend
sudo systemctl status sandbox-backend sandbox-frontend
```

---

## Configuration

### Backend Configuration

Key configuration files:
- `backend/config.py`: Application settings
- `backend/database.py`: Database connection
- `backend/.env`: Environment variables

### Frontend Configuration

Key configuration files:
- `frontend/vite.config.ts`: Build configuration
- `frontend/nginx.conf`: Nginx settings
- `frontend/.env`: Environment variables

### Docker Configuration

Key configuration files:
- `docker-compose.yml`: Multi-container setup
- `backend/Dockerfile`: Backend image
- `frontend/Dockerfile`: Frontend image

---

## Monitoring

### Health Checks

```bash
# Backend health check
curl http://localhost:8033/health

# Frontend health check
curl http://localhost:3033/

# Database health check
docker exec sandbox-postgres pg_isready
```

### Logging

#### Backend Logs

```bash
# Docker logs
docker logs -f sandbox-backend

# Systemd logs
sudo journalctl -u sandbox-backend -f
```

#### Frontend Logs

```bash
# Docker logs
docker logs -f sandbox-frontend

# Systemd logs
sudo journalctl -u sandbox-frontend -f
```

### Metrics Collection

Recommended tools:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **ELK Stack**: Log aggregation
- **Sentry**: Error tracking

---

## Backup & Recovery

### Database Backup

```bash
# Create backup
docker exec sandbox-postgres pg_dump -U sandbox_user sandbox_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker exec -i sandbox-postgres psql -U sandbox_user sandbox_db < backup.sql
```

### Automated Backups

```bash
#!/bin/bash
# /opt/scripts/backup-sandbox.sh

BACKUP_DIR="/opt/backups/sandbox"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker exec sandbox-postgres pg_dump -U sandbox_user sandbox_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup Redis
docker exec sandbox-redis redis-cli SAVE
docker cp sandbox-redis:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Remove old backups (keep last 7 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +7 -delete

echo "Backup completed: $DATE"
```

Add to crontab:

```bash
# Run daily at 2 AM
0 2 * * * /opt/scripts/backup-sandbox.sh
```

---

## Scaling

### Horizontal Scaling

#### Backend Scaling

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

#### Load Balancer Configuration

```nginx
upstream backend {
    least_conn;
    server backend1:8033;
    server backend2:8033;
    server backend3:8033;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

### Vertical Scaling

Increase resources in docker-compose.yml:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
```

---

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port
sudo lsof -i :8033
sudo lsof -i :3033

# Kill process
sudo kill -9 <PID>
```

#### Database Connection Failed

```bash
# Check PostgreSQL status
docker exec sandbox-postgres pg_isready

# Check connection
psql -h localhost -U sandbox_user -d sandbox_db
```

#### Docker Socket Permission Denied

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Restart session
newgrp docker
```

#### Out of Disk Space

```bash
# Check disk usage
df -h

# Clean Docker
docker system prune -a --volumes

# Remove old images
docker image prune -a
```

---

## Security Considerations

### Best Practices

1. **Use Strong Passwords**: Generate secure passwords for all services
2. **Enable SSL/TLS**: Always use HTTPS in production
3. **Regular Updates**: Keep all dependencies up to date
4. **Firewall Rules**: Restrict access to necessary ports only
5. **Backup Encryption**: Encrypt backup files
6. **Access Control**: Implement proper authentication and authorization
7. **Audit Logs**: Enable and monitor audit logs
8. **Security Scanning**: Regularly scan for vulnerabilities

### Firewall Configuration

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow backend (if needed externally)
sudo ufw allow 8033/tcp

# Enable firewall
sudo ufw enable
```

---

## Support

For deployment assistance:
- Email: support@itechsmart.ai
- Documentation: https://docs.itechsmart.ai
- GitHub Issues: https://github.com/itechsmart/sandbox/issues

---

**Last Updated**: August 8, 2025  
**Version**: 1.0.0  
**Copyright**: © 2025 iTechSmart Inc.. All rights reserved.