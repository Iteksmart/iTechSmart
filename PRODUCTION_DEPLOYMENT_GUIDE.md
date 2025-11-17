# 🚀 iTechSmart Suite - Production Deployment Guide

**Version**: 1.0.0  
**Date**: November 17, 2025  
**Status**: Production Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Pre-Deployment Checklist](#pre-deployment-checklist)
4. [Deployment Methods](#deployment-methods)
5. [Security Configuration](#security-configuration)
6. [Database Setup](#database-setup)
7. [Environment Configuration](#environment-configuration)
8. [Service Deployment](#service-deployment)
9. [Load Balancing & Scaling](#load-balancing--scaling)
10. [Monitoring & Logging](#monitoring--logging)
11. [Backup & Recovery](#backup--recovery)
12. [Maintenance Procedures](#maintenance-procedures)
13. [Troubleshooting](#troubleshooting)
14. [Support & Resources](#support--resources)

---

## 🎯 Overview

This guide provides comprehensive instructions for deploying the iTechSmart Suite in production environments. It covers all 37 products and ensures secure, scalable, and maintainable deployments.

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer (Nginx)                    │
│                         Port 80/443                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Reverse Proxy Layer                       │
│              SSL Termination & Request Routing               │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   License    │    │  Application │    │   Database   │
│   Server     │    │   Services   │    │   Cluster    │
│  (Port 3000) │    │ (Ports 3001+)│    │ (Port 5432)  │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## 💻 System Requirements

### Minimum Requirements (Small Deployment)
- **CPU**: 4 cores (8 threads)
- **RAM**: 16 GB
- **Storage**: 100 GB SSD
- **Network**: 100 Mbps
- **OS**: Ubuntu 22.04 LTS, RHEL 8+, or Debian 11+

### Recommended Requirements (Medium Deployment)
- **CPU**: 8 cores (16 threads)
- **RAM**: 32 GB
- **Storage**: 500 GB SSD (NVMe preferred)
- **Network**: 1 Gbps
- **OS**: Ubuntu 22.04 LTS

### Enterprise Requirements (Large Deployment)
- **CPU**: 16+ cores (32+ threads)
- **RAM**: 64+ GB
- **Storage**: 1+ TB SSD (NVMe RAID)
- **Network**: 10 Gbps
- **OS**: Ubuntu 22.04 LTS with enterprise support

### Software Requirements
- **Docker**: 24.0+ or Docker Engine 20.10+
- **Docker Compose**: 2.20+
- **PostgreSQL**: 15+ (for License Server and data-intensive products)
- **Node.js**: 20.x LTS (for development/build)
- **Nginx**: 1.24+ (for reverse proxy)
- **SSL Certificates**: Valid certificates for HTTPS

---

## ✅ Pre-Deployment Checklist

### Infrastructure Preparation
- [ ] Server provisioned with adequate resources
- [ ] Operating system updated and hardened
- [ ] Firewall configured (ports 80, 443, 22 open)
- [ ] DNS records configured
- [ ] SSL certificates obtained and validated
- [ ] Backup storage configured
- [ ] Monitoring tools installed

### Security Preparation
- [ ] SSH key-based authentication configured
- [ ] Root login disabled
- [ ] Fail2ban or similar intrusion prevention installed
- [ ] Security updates automated
- [ ] Audit logging enabled
- [ ] Secrets management system configured

### Database Preparation
- [ ] PostgreSQL installed and configured
- [ ] Database backups automated
- [ ] Connection pooling configured
- [ ] Performance tuning completed
- [ ] Replication configured (if applicable)

### Network Preparation
- [ ] Load balancer configured
- [ ] CDN configured (if applicable)
- [ ] DDoS protection enabled
- [ ] Rate limiting configured
- [ ] Network monitoring enabled

---

## 🚀 Deployment Methods

### Method 1: Docker Compose (Recommended for Single Server)

**Best for**: Small to medium deployments, development, testing

```bash
# 1. Clone repository
git clone https://github.com/Iteksmart/iTechSmart.git
cd iTechSmart

# 2. Configure environment
cp .env.example .env
nano .env  # Edit with your settings

# 3. Deploy services
cd demo-environment
./setup-demo.sh

# 4. Verify deployment
docker-compose ps
docker-compose logs -f
```

### Method 2: Kubernetes (Recommended for Enterprise)

**Best for**: Large deployments, high availability, auto-scaling

```bash
# 1. Create namespace
kubectl create namespace itechsmart

# 2. Apply configurations
kubectl apply -f k8s/configmaps/
kubectl apply -f k8s/secrets/
kubectl apply -f k8s/deployments/
kubectl apply -f k8s/services/

# 3. Verify deployment
kubectl get pods -n itechsmart
kubectl get services -n itechsmart
```

### Method 3: Manual Installation

**Best for**: Custom deployments, specific requirements

See individual product deployment guides in each product directory.

---

## 🔒 Security Configuration

### SSL/TLS Configuration

```nginx
# /etc/nginx/sites-available/itechsmart

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/ssl/certs/yourdomain.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Firewalld (RHEL/CentOS)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### Environment Variables Security

```bash
# Never commit .env files to version control
# Use secrets management for production

# Example .env structure
DATABASE_URL=postgresql://user:password@localhost:5432/itechsmart
JWT_SECRET=your-super-secret-jwt-key-here
API_KEY=your-api-key-here
ENCRYPTION_KEY=your-encryption-key-here

# Set proper permissions
chmod 600 .env
chown root:root .env
```

---

## 🗄️ Database Setup

### PostgreSQL Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql-15 postgresql-contrib

# RHEL/CentOS
sudo dnf install postgresql15-server postgresql15-contrib
sudo postgresql-15-setup initdb
sudo systemctl enable postgresql-15
sudo systemctl start postgresql-15
```

### Database Configuration

```sql
-- Create database and user
CREATE DATABASE itechsmart_license;
CREATE USER itechsmart WITH ENCRYPTED PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE itechsmart_license TO itechsmart;

-- Create databases for other products as needed
CREATE DATABASE itechsmart_ninja;
CREATE DATABASE itechsmart_supreme;
-- ... etc
```

### Performance Tuning

```bash
# Edit /etc/postgresql/15/main/postgresql.conf

# Memory settings
shared_buffers = 4GB              # 25% of RAM
effective_cache_size = 12GB       # 75% of RAM
maintenance_work_mem = 1GB
work_mem = 64MB

# Connection settings
max_connections = 200
max_worker_processes = 8
max_parallel_workers = 8

# WAL settings
wal_buffers = 16MB
checkpoint_completion_target = 0.9
```

### Backup Configuration

```bash
# Automated backup script
cat > /usr/local/bin/backup-itechsmart-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup all databases
pg_dumpall -U postgres | gzip > $BACKUP_DIR/all_databases_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /usr/local/bin/backup-itechsmart-db.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /usr/local/bin/backup-itechsmart-db.sh" | crontab -
```

---

## ⚙️ Environment Configuration

### License Server Configuration

```env
# License Server Environment Variables
NODE_ENV=production
PORT=3000
DATABASE_URL=postgresql://itechsmart:password@localhost:5432/itechsmart_license
JWT_SECRET=your-jwt-secret-here
JWT_EXPIRATION=7d
CORS_ORIGIN=https://yourdomain.com
LOG_LEVEL=info
MAX_LICENSES_PER_ORG=1000
LICENSE_CHECK_INTERVAL=3600000
```

### Application Services Configuration

```env
# Common configuration for all services
NODE_ENV=production
LICENSE_SERVER_URL=https://license.yourdomain.com
API_TIMEOUT=30000
MAX_REQUEST_SIZE=10mb
RATE_LIMIT_WINDOW=900000
RATE_LIMIT_MAX=100
```

---

## 🎯 Service Deployment

### Deploy License Server

```bash
cd license-server

# Build Docker image
docker build -t itechsmart/license-server:1.0.0 .

# Run container
docker run -d \
  --name license-server \
  --restart unless-stopped \
  -p 3000:3000 \
  --env-file .env \
  -v /var/log/itechsmart:/app/logs \
  itechsmart/license-server:1.0.0

# Verify
docker logs -f license-server
curl http://localhost:3000/health
```

### Deploy Application Services

```bash
# Deploy all services using Docker Compose
cd demo-environment
docker-compose up -d

# Verify all services
docker-compose ps
docker-compose logs -f

# Check health endpoints
curl http://localhost:3001/health  # Ninja
curl http://localhost:3002/health  # Supreme
curl http://localhost:3003/health  # Citadel
```

---

## ⚖️ Load Balancing & Scaling

### Nginx Load Balancer Configuration

```nginx
upstream license_server {
    least_conn;
    server 10.0.1.10:3000 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:3000 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:3000 max_fails=3 fail_timeout=30s;
}

upstream app_servers {
    least_conn;
    server 10.0.2.10:3001 max_fails=3 fail_timeout=30s;
    server 10.0.2.11:3001 max_fails=3 fail_timeout=30s;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    location /api/license {
        proxy_pass http://license_server;
        proxy_next_upstream error timeout http_502 http_503 http_504;
    }
    
    location / {
        proxy_pass http://app_servers;
        proxy_next_upstream error timeout http_502 http_503 http_504;
    }
}
```

### Horizontal Scaling

```bash
# Scale services with Docker Compose
docker-compose up -d --scale ninja=3 --scale supreme=2

# Scale with Kubernetes
kubectl scale deployment ninja --replicas=3 -n itechsmart
kubectl scale deployment supreme --replicas=2 -n itechsmart
```

---

## 📊 Monitoring & Logging

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'license-server'
    static_configs:
      - targets: ['localhost:3000']
  
  - job_name: 'app-services'
    static_configs:
      - targets: ['localhost:3001', 'localhost:3002', 'localhost:3003']
```

### Grafana Dashboards

```bash
# Install Grafana
docker run -d \
  --name grafana \
  -p 3100:3000 \
  -v grafana-storage:/var/lib/grafana \
  grafana/grafana

# Access at http://localhost:3100
# Default credentials: admin/admin
```

### Centralized Logging

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
  
  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5000:5000"
  
  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
```

---

## 💾 Backup & Recovery

### Automated Backup Strategy

```bash
#!/bin/bash
# /usr/local/bin/backup-itechsmart.sh

BACKUP_DIR="/var/backups/itechsmart"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR/$DATE

# Backup databases
pg_dumpall -U postgres | gzip > $BACKUP_DIR/$DATE/databases.sql.gz

# Backup Docker volumes
docker run --rm \
  -v itechsmart_data:/data \
  -v $BACKUP_DIR/$DATE:/backup \
  alpine tar czf /backup/volumes.tar.gz /data

# Backup configuration files
tar czf $BACKUP_DIR/$DATE/configs.tar.gz \
  /etc/nginx \
  /opt/itechsmart/.env \
  /opt/itechsmart/docker-compose.yml

# Upload to S3 (optional)
aws s3 sync $BACKUP_DIR/$DATE s3://your-backup-bucket/itechsmart/$DATE/

# Keep only last 30 days locally
find $BACKUP_DIR -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;

echo "Backup completed: $DATE"
```

### Recovery Procedures

```bash
# Restore from backup
RESTORE_DATE="20251117_020000"
BACKUP_DIR="/var/backups/itechsmart"

# Stop services
docker-compose down

# Restore databases
gunzip < $BACKUP_DIR/$RESTORE_DATE/databases.sql.gz | psql -U postgres

# Restore volumes
docker run --rm \
  -v itechsmart_data:/data \
  -v $BACKUP_DIR/$RESTORE_DATE:/backup \
  alpine tar xzf /backup/volumes.tar.gz -C /

# Restore configurations
tar xzf $BACKUP_DIR/$RESTORE_DATE/configs.tar.gz -C /

# Start services
docker-compose up -d

echo "Recovery completed from: $RESTORE_DATE"
```

---

## 🔧 Maintenance Procedures

### Regular Maintenance Tasks

```bash
# Daily tasks
- Check service health
- Review error logs
- Monitor disk space
- Verify backups

# Weekly tasks
- Update security patches
- Review performance metrics
- Clean up old logs
- Test backup restoration

# Monthly tasks
- Review access logs
- Update SSL certificates (if needed)
- Performance optimization
- Capacity planning review
```

### Update Procedures

```bash
# Update iTechSmart Suite
cd /opt/itechsmart

# Pull latest changes
git pull origin main

# Backup current state
./backup-itechsmart.sh

# Update services
docker-compose pull
docker-compose up -d

# Verify update
docker-compose ps
docker-compose logs -f

# Rollback if needed
git checkout <previous-commit>
docker-compose up -d
```

---

## 🔍 Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check logs
docker-compose logs service-name

# Check resource usage
docker stats

# Check port conflicts
netstat -tulpn | grep :3000

# Restart service
docker-compose restart service-name
```

#### Database Connection Issues

```bash
# Test database connection
psql -U itechsmart -h localhost -d itechsmart_license

# Check PostgreSQL status
systemctl status postgresql

# Review PostgreSQL logs
tail -f /var/log/postgresql/postgresql-15-main.log
```

#### Performance Issues

```bash
# Check system resources
htop
df -h
free -m

# Check Docker resources
docker stats

# Review slow queries
psql -U postgres -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

### Emergency Contacts

- **Technical Support**: support@itechsmart.dev
- **Emergency Hotline**: +1-XXX-XXX-XXXX
- **Documentation**: https://github.com/Iteksmart/iTechSmart
- **Community Forum**: https://community.itechsmart.dev

---

## 📚 Support & Resources

### Documentation
- [User Guides](./docs/user-guides/)
- [API Documentation](./docs/api/)
- [Deployment Guides](./docs/deployment/)
- [Troubleshooting](./docs/troubleshooting/)

### Community
- [GitHub Repository](https://github.com/Iteksmart/iTechSmart)
- [Issue Tracker](https://github.com/Iteksmart/iTechSmart/issues)
- [Discussions](https://github.com/Iteksmart/iTechSmart/discussions)

### Professional Support
- Email: support@itechsmart.dev
- Enterprise Support: enterprise@itechsmart.dev
- Training: training@itechsmart.dev

---

## 📝 Deployment Checklist

### Pre-Production
- [ ] All system requirements met
- [ ] Security hardening completed
- [ ] SSL certificates installed
- [ ] Database configured and optimized
- [ ] Backups automated and tested
- [ ] Monitoring configured
- [ ] Load testing completed
- [ ] Documentation reviewed

### Production Launch
- [ ] DNS records updated
- [ ] Services deployed
- [ ] Health checks passing
- [ ] SSL working correctly
- [ ] Backups verified
- [ ] Monitoring active
- [ ] Team trained
- [ ] Support contacts documented

### Post-Production
- [ ] Monitor for 24 hours
- [ ] Review logs daily for first week
- [ ] Gather user feedback
- [ ] Performance optimization
- [ ] Documentation updates
- [ ] Team retrospective

---

**Document Version**: 1.0.0  
**Last Updated**: November 17, 2025  
**Maintained By**: iTechSmart Inc

For the latest version of this guide, visit: https://github.com/Iteksmart/iTechSmart/blob/main/PRODUCTION_DEPLOYMENT_GUIDE.md