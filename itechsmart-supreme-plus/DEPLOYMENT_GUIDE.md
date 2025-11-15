# iTechSmart Supreme Plus - Deployment Guide

**AI-Powered Infrastructure Auto-Remediation Platform**

Copyright (c) 2025 iTechSmart Inc.  
Launch Date: August 8, 2025

**Company Information**  
iTechSmart Inc. (C-Corp)  
1130 Ogletown Road, Suite 2  
Newark, DE 19711, USA  
Phone: 310-251-3969  
Website: https://itechsmart.dev  
Support: support@itechsmart.dev

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Methods](#installation-methods)
3. [Docker Deployment](#docker-deployment)
4. [Manual Deployment](#manual-deployment)
5. [Configuration](#configuration)
6. [Database Setup](#database-setup)
7. [Integration Setup](#integration-setup)
8. [Security Configuration](#security-configuration)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **CPU**: 4 cores
- **RAM**: 4GB
- **Disk**: 20GB
- **OS**: Linux (Ubuntu 20.04+, CentOS 8+, Debian 11+)
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### Recommended Requirements
- **CPU**: 8 cores
- **RAM**: 8GB
- **Disk**: 50GB SSD
- **OS**: Ubuntu 22.04 LTS
- **Network**: 1Gbps

### Software Dependencies
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 20+
- Nginx (for production)

## Installation Methods

### Method 1: Docker Compose (Recommended)
Quick deployment using Docker containers.

### Method 2: Manual Installation
Full control over installation and configuration.

### Method 3: Kubernetes
Enterprise-grade orchestration (see separate K8s guide).

## Docker Deployment

### Quick Start

1. **Clone Repository**
```bash
git clone <repository-url>
cd itechsmart-supreme-plus
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start Services**
```bash
docker-compose up -d
```

4. **Verify Deployment**
```bash
docker-compose ps
curl http://localhost:8034/health
curl http://localhost:3034
```

### Docker Compose Configuration

The `docker-compose.yml` includes:
- PostgreSQL database
- Redis cache
- Backend API service
- Frontend web service

### Service Ports
- **Frontend**: 3034
- **Backend**: 8034
- **PostgreSQL**: 5434
- **Redis**: 6379

### Docker Commands

**Start services**:
```bash
docker-compose up -d
```

**Stop services**:
```bash
docker-compose down
```

**View logs**:
```bash
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Restart services**:
```bash
docker-compose restart
```

**Update services**:
```bash
docker-compose pull
docker-compose up -d
```

## Manual Deployment

### Backend Deployment

1. **Install Python Dependencies**
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure Database**
```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/supremeplus"
export REDIS_URL="redis://localhost:6379/4"
```

3. **Initialize Database**
```bash
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
```

4. **Start Backend**
```bash
uvicorn main:app --host 0.0.0.0 --port 8034
```

### Frontend Deployment

1. **Install Node Dependencies**
```bash
cd frontend
npm install
```

2. **Build Frontend**
```bash
npm run build
```

3. **Serve with Nginx**
```bash
sudo cp dist/* /var/www/supremeplus/
sudo systemctl restart nginx
```

### Systemd Service Files

**Backend Service** (`/etc/systemd/system/supremeplus-backend.service`):
```ini
[Unit]
Description=iTechSmart Supreme Plus Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=supremeplus
WorkingDirectory=/opt/supremeplus/backend
Environment="DATABASE_URL=postgresql://user:pass@localhost:5432/supremeplus"
Environment="REDIS_URL=redis://localhost:6379/4"
ExecStart=/opt/supremeplus/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8034
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start**:
```bash
sudo systemctl enable supremeplus-backend
sudo systemctl start supremeplus-backend
```

## Configuration

### Environment Variables

**Backend Configuration**:
```bash
# Database
DATABASE_URL=postgresql://supremeplus:supremeplus@localhost:5432/supremeplus

# Redis
REDIS_URL=redis://localhost:6379/4

# Application
DEBUG=false
AUTO_REMEDIATION_ENABLED=true
REMEDIATION_TIMEOUT=300
MAX_CONCURRENT_REMEDIATIONS=10

# AI Configuration
OPENAI_API_KEY=your-openai-key
AI_MODEL=gpt-4
AI_TEMPERATURE=0.7

# Integration URLs
HUB_URL=http://localhost:8000
NINJA_URL=http://localhost:8001
PROMETHEUS_URL=http://prometheus:9090
WAZUH_URL=http://wazuh:55000

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/supreme_plus.log
```

**Frontend Configuration** (`.env`):
```bash
VITE_API_URL=http://localhost:8034
```

### Configuration Files

**Backend Config** (`backend/config.py`):
- Modify settings as needed
- Update integration URLs
- Configure AI models
- Set security parameters

## Database Setup

### PostgreSQL Installation

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install postgresql-15
```

**Create Database**:
```bash
sudo -u postgres psql
CREATE DATABASE supremeplus;
CREATE USER supremeplus WITH PASSWORD 'supremeplus';
GRANT ALL PRIVILEGES ON DATABASE supremeplus TO supremeplus;
\q
```

### Database Migrations

Initialize tables:
```bash
cd backend
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Redis Installation

**Ubuntu/Debian**:
```bash
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## Integration Setup

### Prometheus Integration

1. Configure Prometheus URL in environment
2. Create integration in UI
3. Test connection
4. Enable integration

**Example Configuration**:
```json
{
  "name": "Production Prometheus",
  "integration_type": "prometheus",
  "config": {
    "url": "http://prometheus:9090",
    "scrape_interval": 60
  }
}
```

### Wazuh Integration

1. Configure Wazuh URL and API key
2. Create integration in UI
3. Test connection
4. Enable integration

**Example Configuration**:
```json
{
  "name": "Wazuh Security",
  "integration_type": "wazuh",
  "config": {
    "url": "http://wazuh:55000",
    "api_key": "your-wazuh-api-key"
  }
}
```

## Security Configuration

### SSL/TLS Setup

**Nginx Configuration** (`/etc/nginx/sites-available/supremeplus`):
```nginx
server {
    listen 443 ssl http2;
    server_name supremeplus.example.com;

    ssl_certificate /etc/ssl/certs/supremeplus.crt;
    ssl_certificate_key /etc/ssl/private/supremeplus.key;

    location / {
        proxy_pass http://localhost:3034;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8034;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Firewall Configuration

**UFW (Ubuntu)**:
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8034/tcp
sudo ufw allow 3034/tcp
sudo ufw enable
```

### Credential Management

Store credentials securely:
- Use environment variables
- Encrypt sensitive data
- Rotate keys regularly
- Use secrets management (Vault, etc.)

## Monitoring & Maintenance

### Health Checks

**Backend Health**:
```bash
curl http://localhost:8034/health
```

**Frontend Health**:
```bash
curl http://localhost:3034
```

### Log Management

**View Logs**:
```bash
# Backend logs
tail -f logs/supreme_plus.log

# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Log Rotation** (`/etc/logrotate.d/supremeplus`):
```
/opt/supremeplus/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 supremeplus supremeplus
}
```

### Backup Procedures

**Database Backup**:
```bash
pg_dump -U supremeplus supremeplus > backup_$(date +%Y%m%d).sql
```

**Automated Backup Script**:
```bash
#!/bin/bash
BACKUP_DIR=/backups/supremeplus
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U supremeplus supremeplus | gzip > $BACKUP_DIR/db_$DATE.sql.gz
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
```

### Updates

**Update Docker Deployment**:
```bash
docker-compose pull
docker-compose up -d
```

**Update Manual Deployment**:
```bash
git pull
cd backend && pip install -r requirements.txt
cd ../frontend && npm install && npm run build
sudo systemctl restart supremeplus-backend
```

## Troubleshooting

### Common Issues

**Issue**: Backend won't start
```bash
# Check logs
docker-compose logs backend

# Verify database connection
psql -U supremeplus -h localhost -d supremeplus

# Check environment variables
docker-compose exec backend env
```

**Issue**: Frontend can't connect to backend
```bash
# Check backend is running
curl http://localhost:8034/health

# Verify CORS settings
# Check nginx configuration
# Review browser console for errors
```

**Issue**: Database connection errors
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify credentials
psql -U supremeplus -h localhost -d supremeplus

# Check DATABASE_URL format
```

**Issue**: Redis connection errors
```bash
# Check Redis is running
sudo systemctl status redis

# Test connection
redis-cli ping

# Verify REDIS_URL
```

### Performance Tuning

**PostgreSQL**:
```sql
-- Increase connection pool
ALTER SYSTEM SET max_connections = 200;

-- Tune memory
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
```

**Redis**:
```bash
# Edit /etc/redis/redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### Support

For additional help:
- Documentation: http://localhost:8034/docs
- Website: https://itechsmart.dev
- Technical Support: support@itechsmart.dev
- Sales Inquiries: sales@itechsmart.dev
- Phone: 310-251-3969

**iTechSmart Inc.**  
1130 Ogletown Road, Suite 2  
Newark, DE 19711, USA

---

**Version**: 1.1.0  
**Last Updated**: August 8, 2025  
**Copyright**: (c) 2025 iTechSmart Inc.