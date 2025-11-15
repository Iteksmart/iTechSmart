# 🔧 iTechSmart ImpactOS - Administrator Guide

## Table of Contents
1. [System Administration](#system-administration)
2. [User Management](#user-management)
3. [Organization Management](#organization-management)
4. [Security & Compliance](#security--compliance)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Backup & Recovery](#backup--recovery)
7. [API Management](#api-management)
8. [Troubleshooting](#troubleshooting)

---

## 1. System Administration

### Installation & Setup

**Prerequisites**
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
- 4GB RAM minimum
- 20GB disk space

**Quick Installation**
```bash
# Clone repository
git clone https://github.com/itechsmart/impactos.git
cd impactos

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**Initial Configuration**
1. Access admin panel: http://localhost:8000/admin
2. Create super admin account
3. Configure email settings
4. Set up OAuth providers (optional)
5. Configure AI API keys

### System Requirements

**Production Environment**
- CPU: 4+ cores
- RAM: 8GB minimum, 16GB recommended
- Storage: 100GB+ SSD
- Network: 100Mbps+
- OS: Ubuntu 22.04 LTS or similar

**Recommended Stack**
- Load Balancer: Nginx
- Database: PostgreSQL 15 (managed service recommended)
- Cache: Redis 7 (managed service recommended)
- Container Orchestration: Kubernetes
- Monitoring: Prometheus + Grafana

---

## 2. User Management

### Creating Admin Users

**Via Command Line**
```bash
docker-compose exec backend python manage.py createsuperuser
```

**Via Admin Panel**
1. Login as super admin
2. Navigate to Users section
3. Click "Create User"
4. Fill in details
5. Assign "Super Admin" role
6. Click "Create"

### User Roles & Permissions

**Role Hierarchy**
1. **Super Admin** - Full system access
   - Manage all organizations
   - Manage all users
   - System settings
   - Billing management

2. **Organization Admin** - Organization-level access
   - Manage organization
   - Manage org users
   - Manage programs
   - View analytics

3. **Program Manager** - Program-level access
   - Manage programs
   - Create reports
   - Manage evidence

4. **Grant Writer** - Grant-specific access
   - Create proposals
   - Submit grants
   - View grant analytics

5. **Data Analyst** - Read-only analytics
   - View all analytics
   - Create reports
   - Export data

6. **Volunteer** - Limited access
   - View programs
   - Submit evidence

7. **Donor** - Public access
   - View impact reports
   - View public analytics

### Managing User Accounts

**Activating/Deactivating Users**
```bash
# Via CLI
docker-compose exec backend python manage.py activate_user user@example.com
docker-compose exec backend python manage.py deactivate_user user@example.com
```

**Resetting Passwords**
```bash
docker-compose exec backend python manage.py reset_password user@example.com
```

**Bulk User Import**
```bash
# Prepare CSV file with columns: email, username, full_name, role
docker-compose exec backend python manage.py import_users users.csv
```

---

## 3. Organization Management

### Creating Organizations

**Via Admin Panel**
1. Navigate to Organizations
2. Click "Create Organization"
3. Enter details:
   - Name
   - Slug (URL-friendly)
   - Mission
   - Contact info
   - Tax ID
4. Set subscription tier
5. Click "Create"

**Via API**
```bash
curl -X POST http://localhost:8000/api/v1/organizations \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example Nonprofit",
    "slug": "example-nonprofit",
    "mission": "Making a difference",
    "email": "info@example.org"
  }'
```

### Subscription Management

**Subscription Tiers**
- **Free**: 1 organization, 5 users, 10 programs
- **Basic** ($49/mo): 3 organizations, 20 users, 50 programs
- **Pro** ($149/mo): 10 organizations, 100 users, unlimited programs
- **Enterprise** (Custom): Unlimited everything + dedicated support

**Changing Subscriptions**
1. Navigate to organization settings
2. Click "Subscription"
3. Select new tier
4. Confirm payment
5. Changes take effect immediately

---

## 4. Security & Compliance

### Security Configuration

**JWT Settings**
```python
# In .env file
SECRET_KEY=your-very-secure-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**OAuth Configuration**
```python
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback/google

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:3000/auth/callback/github
```

### SSL/TLS Configuration

**Using Let's Encrypt**
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d app.impactos.com -d api.impactos.com

# Auto-renewal
sudo certbot renew --dry-run
```

**Nginx SSL Configuration**
```nginx
server {
    listen 443 ssl http2;
    server_name app.impactos.com;
    
    ssl_certificate /etc/letsencrypt/live/app.impactos.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.impactos.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # ... rest of configuration
}
```

### Audit Logging

**Viewing Audit Logs**
```bash
# Via CLI
docker-compose exec backend python manage.py view_audit_logs --days 7

# Via database
docker-compose exec postgres psql -U impactos -d impactos_db
SELECT * FROM audit_logs WHERE created_at > NOW() - INTERVAL '7 days';
```

**Audit Log Retention**
- Default: 6 years (HIPAA requirement)
- Configurable in settings
- Automatic archival to cold storage

---

## 5. Monitoring & Maintenance

### Health Checks

**System Health**
```bash
# Check all services
curl http://localhost:8000/health

# Check database
docker-compose exec postgres pg_isready

# Check Redis
docker-compose exec redis redis-cli ping
```

**Monitoring Endpoints**
- `/health` - Overall system health
- `/metrics` - Prometheus metrics
- `/api/v1/stats` - API statistics

### Performance Monitoring

**Using Prometheus**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'impactos-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
```

**Key Metrics to Monitor**
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (%)
- Database connections
- Cache hit rate
- AI API usage
- Disk usage
- Memory usage

### Log Management

**Viewing Logs**
```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend

# Database logs
docker-compose logs -f postgres

# All logs
docker-compose logs -f
```

**Log Rotation**
```bash
# Configure in docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## 6. Backup & Recovery

### Database Backup

**Manual Backup**
```bash
# Create backup
docker-compose exec postgres pg_dump -U impactos impactos_db > backup_$(date +%Y%m%d).sql

# Compress backup
gzip backup_$(date +%Y%m%d).sql
```

**Automated Backup Script**
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="impactos_backup_$DATE.sql.gz"

# Create backup
docker-compose exec -T postgres pg_dump -U impactos impactos_db | gzip > "$BACKUP_DIR/$FILENAME"

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR/$FILENAME" s3://impactos-backups/

# Delete old backups (keep last 30 days)
find "$BACKUP_DIR" -name "impactos_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $FILENAME"
```

**Schedule with Cron**
```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup.sh
```

### Database Restore

**From Backup File**
```bash
# Stop services
docker-compose stop backend

# Restore database
gunzip -c backup_20240115.sql.gz | docker-compose exec -T postgres psql -U impactos impactos_db

# Start services
docker-compose start backend
```

### Disaster Recovery Plan

**Recovery Time Objective (RTO): 1 hour**
**Recovery Point Objective (RPO): 24 hours**

**Steps:**
1. Identify failure point
2. Spin up new infrastructure
3. Restore latest backup
4. Verify data integrity
5. Update DNS records
6. Monitor system health

---

## 7. API Management

### API Keys

**Creating API Keys**
```bash
docker-compose exec backend python manage.py create_api_key \
  --name "Integration Key" \
  --organization "example-nonprofit" \
  --permissions "read,write"
```

**Revoking API Keys**
```bash
docker-compose exec backend python manage.py revoke_api_key <key_id>
```

### Rate Limiting

**Configuration**
```python
# In .env
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

**Monitoring Rate Limits**
```bash
# View rate limit stats
curl http://localhost:8000/api/v1/stats/rate-limits \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### API Documentation

**Accessing Docs**
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc
- OpenAPI JSON: http://localhost:8000/api/v1/openapi.json

---

## 8. Troubleshooting

### Common Issues

**Database Connection Errors**
```bash
# Check database status
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U impactos -d impactos_db -c "SELECT 1;"

# Restart database
docker-compose restart postgres
```

**Redis Connection Errors**
```bash
# Check Redis status
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping

# Restart Redis
docker-compose restart redis
```

**High Memory Usage**
```bash
# Check memory usage
docker stats

# Restart services
docker-compose restart

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

**Slow Performance**
```bash
# Check database queries
docker-compose exec postgres psql -U impactos -d impactos_db
SELECT * FROM pg_stat_activity WHERE state = 'active';

# Analyze slow queries
SELECT query, mean_exec_time 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

# Rebuild indexes
docker-compose exec backend python manage.py rebuild_indexes
```

### Emergency Procedures

**System Down**
1. Check all services: `docker-compose ps`
2. View logs: `docker-compose logs`
3. Restart services: `docker-compose restart`
4. If persists, restore from backup

**Data Corruption**
1. Stop services immediately
2. Create emergency backup
3. Identify corrupted data
4. Restore from last good backup
5. Replay transactions if possible

**Security Breach**
1. Isolate affected systems
2. Change all passwords and keys
3. Review audit logs
4. Notify affected users
5. Implement additional security measures

---

## Maintenance Schedule

### Daily
- Monitor system health
- Check error logs
- Review security alerts

### Weekly
- Review performance metrics
- Check disk space
- Update dependencies (if needed)

### Monthly
- Full system backup verification
- Security audit
- Performance optimization
- User access review

### Quarterly
- Disaster recovery drill
- Capacity planning
- Security penetration testing
- Documentation updates

---

## Support Contacts

**Technical Support**
- Email: support@itechsmart.dev
- Phone: 1-800-IMPACT-OS
- Emergency: +1-555-EMERGENCY

**Security Issues**
- Email: security@itechsmart.dev
- PGP Key: Available on website

---

**Version 1.0 | Last Updated: January 2024**