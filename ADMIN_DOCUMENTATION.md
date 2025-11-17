# iTechSmart Suite - Administrator Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [License Server Administration](#license-server-administration)
4. [Desktop Launcher Management](#desktop-launcher-management)
5. [User Management](#user-management)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Security & Compliance](#security--compliance)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)
10. [API Reference](#api-reference)

---

## Introduction

### Purpose

This document provides comprehensive guidance for administrators responsible for deploying, managing, and maintaining the iTechSmart Suite in enterprise environments.

### Audience

- **System Administrators:** Infrastructure and operations
- **DevOps Engineers:** Deployment and automation
- **Security Teams:** Security and compliance
- **Support Teams:** User assistance and troubleshooting

### Prerequisites

**Required Knowledge:**
- Linux/Unix system administration
- Docker and containerization
- Web server configuration
- Database management
- Network security

**Required Access:**
- Root/Administrator access to servers
- Database credentials
- SSL certificates
- Cloud platform access (if applicable)

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    iTechSmart Suite                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │  Desktop Launcher │◄───────►│  License Server  │     │
│  │   (Electron App)  │  HTTPS  │   (Node.js API)  │     │
│  └──────────────────┘         └──────────────────┘     │
│           │                             │                │
│           │                             │                │
│           ▼                             ▼                │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │  Docker Engine   │         │   PostgreSQL     │     │
│  │  (35 Products)   │         │   (License DB)   │     │
│  └──────────────────┘         └──────────────────┘     │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. License Server
- **Technology:** Node.js + Express + Prisma
- **Database:** PostgreSQL 15+
- **Port:** 3001 (configurable)
- **Purpose:** License validation, user management, usage tracking

#### 2. Desktop Launcher
- **Technology:** Electron + React + TypeScript
- **Platforms:** Windows, macOS, Linux
- **Purpose:** Product management, Docker orchestration, UI

#### 3. Product Containers
- **Technology:** Docker containers
- **Count:** 35 products
- **Ports:** Various (3000-9000 range)
- **Purpose:** Individual iTechSmart applications

#### 4. Database
- **Technology:** PostgreSQL 15
- **Port:** 5432
- **Purpose:** License data, user accounts, usage metrics

### Network Architecture

```
Internet
    │
    ▼
┌─────────────────┐
│  Load Balancer  │
│   (Optional)    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Reverse Proxy  │
│  (Nginx/Apache) │
└─────────────────┘
    │
    ├──────────────────┐
    │                  │
    ▼                  ▼
┌──────────────┐  ┌──────────────┐
│License Server│  │  Products    │
│  Port 3001   │  │ Ports 3000+  │
└──────────────┘  └──────────────┘
    │
    ▼
┌──────────────┐
│  PostgreSQL  │
│  Port 5432   │
└──────────────┘
```

---

## License Server Administration

### Deployment

#### Production Deployment (Docker Compose)

**1. Server Preparation**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin -y
```

**2. Clone Repository**
```bash
git clone https://github.com/Iteksmart/iTechSmart.git
cd iTechSmart/license-server
```

**3. Configure Environment**
```bash
cp .env.example .env
nano .env
```

**Required Configuration:**
```env
# Database
DATABASE_URL="postgresql://postgres:STRONG_PASSWORD@postgres:5432/itechsmart_licenses"

# JWT Secret (generate with: openssl rand -base64 32)
JWT_SECRET="your-generated-secret-key-min-32-chars"

# Server
PORT=3001
NODE_ENV=production

# Admin Account
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=YourStrongPassword123!

# CORS
CORS_ORIGIN=https://yourdomain.com

# Optional: Stripe
STRIPE_SECRET_KEY=sk_live_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret

# Optional: Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

**4. Start Services**
```bash
docker compose up -d
```

**5. Verify Deployment**
```bash
# Check services
docker compose ps

# Check logs
docker compose logs -f license-server

# Test health endpoint
curl http://localhost:3001/health
```

#### Cloud Deployment

**AWS (ECS + RDS)**
```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier itechsmart-licenses \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password YOUR_PASSWORD \
  --allocated-storage 20

# Build and push Docker image
docker build -t itechsmart-license-server .
docker tag itechsmart-license-server:latest \
  YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/itechsmart-license-server:latest
docker push YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/itechsmart-license-server:latest

# Create ECS service (use AWS Console or CLI)
```

**GCP (Cloud Run + Cloud SQL)**
```bash
# Create Cloud SQL instance
gcloud sql instances create itechsmart-licenses \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Deploy to Cloud Run
gcloud builds submit --tag gcr.io/YOUR_PROJECT/itechsmart-license-server
gcloud run deploy itechsmart-license-server \
  --image gcr.io/YOUR_PROJECT/itechsmart-license-server \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Configuration Management

#### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | - | PostgreSQL connection string |
| JWT_SECRET | Yes | - | Secret for JWT tokens (32+ chars) |
| PORT | No | 3001 | Server port |
| NODE_ENV | No | development | Environment (production/development) |
| ADMIN_EMAIL | Yes | - | Admin account email |
| ADMIN_PASSWORD | Yes | - | Admin account password |
| CORS_ORIGIN | No | * | Allowed CORS origins |
| API_RATE_LIMIT | No | 100 | Requests per window |
| API_RATE_WINDOW | No | 15 | Rate limit window (minutes) |
| LOG_LEVEL | No | info | Logging level |

#### Database Configuration

**Connection Pooling:**
```javascript
// In Prisma schema
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// Connection pool settings
DATABASE_URL="postgresql://user:pass@host:5432/db?connection_limit=10&pool_timeout=20"
```

**Backup Configuration:**
```bash
# Automated daily backups
0 2 * * * /usr/local/bin/backup-database.sh
```

### License Management

#### Creating Licenses

**Via API:**
```bash
# Login as admin
TOKEN=$(curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@yourdomain.com","password":"YourPassword"}' \
  | jq -r '.data.token')

# Create license
curl -X POST http://localhost:3001/api/licenses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "tier": "PROFESSIONAL",
    "maxUsers": 25,
    "maxProducts": 10,
    "expiresAt": "2025-12-31T23:59:59Z",
    "allowedProducts": [
      "itechsmart-analytics",
      "itechsmart-shield",
      "itechsmart-pulse"
    ]
  }'
```

**Via Database:**
```sql
-- Direct database insert (not recommended for production)
INSERT INTO "License" (
  id, "licenseKey", "organizationId", tier, status,
  "maxUsers", "maxProducts", "expiresAt"
) VALUES (
  gen_random_uuid(),
  'ITSM-PROF-XXXX-XXXX-XXXX-XXXX',
  'org_id_here',
  'PROFESSIONAL',
  'ACTIVE',
  25,
  10,
  '2025-12-31 23:59:59'
);
```

#### License Tiers

| Tier | Max Users | Max Products | Max API Calls/Day | Max Storage |
|------|-----------|--------------|-------------------|-------------|
| TRIAL | 5 | 3 | 1,000 | 1 GB |
| STARTER | 10 | 5 | 10,000 | 10 GB |
| PROFESSIONAL | 25 | 10 | 100,000 | 100 GB |
| ENTERPRISE | 100 | 20 | 1,000,000 | 1 TB |
| UNLIMITED | ∞ | 35 | ∞ | ∞ |

#### Revoking Licenses

```bash
# Revoke license
curl -X DELETE http://localhost:3001/api/licenses/LICENSE_ID \
  -H "Authorization: Bearer $TOKEN"
```

#### Extending Licenses

```bash
# Update expiration date
curl -X PUT http://localhost:3001/api/licenses/LICENSE_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "expiresAt": "2026-12-31T23:59:59Z"
  }'
```

---

## Desktop Launcher Management

### Distribution

#### Building Installers

**Prerequisites:**
```bash
cd desktop-launcher
npm install
```

**Build for All Platforms:**
```bash
npm run package:all
```

**Platform-Specific Builds:**
```bash
# Windows
npm run package:win

# macOS
npm run package:mac

# Linux
npm run package:linux
```

**Output Location:**
```
desktop-launcher/release/
├── iTechSmart-Suite-Setup-1.0.0.exe      # Windows NSIS
├── iTechSmart-Suite-1.0.0.msi            # Windows MSI
├── iTechSmart-Suite-1.0.0.dmg            # macOS DMG
├── iTechSmart-Suite-1.0.0.pkg            # macOS PKG
├── iTechSmart-Suite-1.0.0.AppImage       # Linux AppImage
├── itechsmart-suite_1.0.0_amd64.deb      # Debian/Ubuntu
└── itechsmart-suite-1.0.0.x86_64.rpm     # RedHat/Fedora
```

#### Code Signing

**Windows:**
```bash
# Requires code signing certificate
npm run package:win -- --sign
```

**macOS:**
```bash
# Requires Apple Developer certificate
export CSC_LINK=/path/to/certificate.p12
export CSC_KEY_PASSWORD=certificate_password
npm run package:mac
```

**Linux:**
```bash
# GPG signing
gpg --detach-sign --armor iTechSmart-Suite.AppImage
```

#### Distribution Channels

**1. GitHub Releases**
```bash
# Create release
gh release create v1.0.0 \
  release/iTechSmart-Suite-Setup-1.0.0.exe \
  release/iTechSmart-Suite-1.0.0.dmg \
  release/iTechSmart-Suite-1.0.0.AppImage \
  --title "iTechSmart Suite v1.0.0" \
  --notes "Release notes here"
```

**2. Direct Download**
- Host on CDN or web server
- Provide download links on website
- Track downloads with analytics

**3. Package Managers**
```bash
# Homebrew (macOS)
brew tap itechsmart/tap
brew install itechsmart-suite

# Chocolatey (Windows)
choco install itechsmart-suite

# Snap (Linux)
snap install itechsmart-suite
```

### Auto-Update Configuration

**Update Server Setup:**
```javascript
// In package.json
"build": {
  "publish": {
    "provider": "github",
    "owner": "Iteksmart",
    "repo": "iTechSmart"
  }
}
```

**Update Channels:**
- **Stable:** Production releases
- **Beta:** Pre-release testing
- **Alpha:** Development builds

**Update Policy:**
```javascript
// In update-manager.ts
{
  autoDownload: true,
  autoInstallOnAppQuit: true,
  checkForUpdatesOnStart: true,
  allowDowngrade: false
}
```

### Configuration Management

**Global Configuration:**
```json
// %APPDATA%/iTechSmart Suite/config.json (Windows)
// ~/Library/Application Support/iTechSmart Suite/config.json (macOS)
// ~/.config/iTechSmart Suite/config.json (Linux)
{
  "licenseServer": "https://licenses.yourdomain.com",
  "autoUpdate": true,
  "theme": "auto",
  "logLevel": "info"
}
```

**Enterprise Deployment:**
```bash
# Deploy with pre-configured settings
iTechSmart-Suite-Setup.exe /S /LICENSE_SERVER=https://licenses.company.com
```

---

## User Management

### Organization Management

#### Creating Organizations

```bash
# Via API
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation",
    "domain": "acme.com",
    "email": "admin@acme.com",
    "password": "SecurePassword123!",
    "phone": "+1-555-0100",
    "address": "123 Main St, San Francisco, CA",
    "country": "USA"
  }'
```

#### Managing Users

**Add User to Organization:**
```sql
INSERT INTO "User" (
  id, email, "passwordHash", name, role, "organizationId"
) VALUES (
  gen_random_uuid(),
  'user@acme.com',
  '$2a$10$hashed_password',
  'John Doe',
  'user',
  'org_id_here'
);
```

**User Roles:**
- **admin:** Full access, can manage licenses and users
- **user:** Standard access, can use products
- **viewer:** Read-only access, can view but not modify

#### API Keys

**Generate API Key:**
```bash
curl -X POST http://localhost:3001/api/organizations/ORG_ID/api-keys \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Production API Key",
    "scopes": ["read", "write"]
  }'
```

**Revoke API Key:**
```bash
curl -X DELETE http://localhost:3001/api/organizations/ORG_ID/api-keys/KEY_ID \
  -H "Authorization: Bearer $TOKEN"
```

---

## Monitoring & Maintenance

### Health Monitoring

**Health Check Endpoint:**
```bash
curl http://localhost:3001/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-16T17:00:00.000Z",
  "uptime": 3600,
  "database": "connected",
  "version": "1.0.0"
}
```

**Monitoring Tools:**
- **UptimeRobot:** External monitoring
- **Prometheus:** Metrics collection
- **Grafana:** Visualization
- **ELK Stack:** Log aggregation

### Performance Monitoring

**Key Metrics:**
```bash
# Response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:3001/health

# Database connections
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c \
  "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

# Container stats
docker stats --no-stream
```

**Performance Targets:**
- API response time: < 200ms (average)
- Database query time: < 100ms
- CPU usage: < 50%
- Memory usage: < 2GB
- Disk I/O: < 100 MB/s

### Log Management

**View Logs:**
```bash
# License server logs
docker compose logs -f license-server

# Last 100 lines
docker compose logs --tail=100 license-server

# Specific time range
docker compose logs --since 2025-11-16T10:00:00 license-server
```

**Log Rotation:**
```bash
# Configure logrotate
cat > /etc/logrotate.d/docker-containers << EOF
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=10M
    missingok
    delaycompress
    copytruncate
}
EOF
```

### Database Maintenance

**Regular Maintenance Tasks:**
```bash
# Vacuum and analyze
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c \
  "VACUUM ANALYZE;"

# Reindex
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c \
  "REINDEX DATABASE itechsmart_licenses;"

# Check database size
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c \
  "SELECT pg_size_pretty(pg_database_size('itechsmart_licenses'));"
```

**Maintenance Schedule:**
- **Daily:** Vacuum analyze
- **Weekly:** Check slow queries
- **Monthly:** Reindex, optimize
- **Quarterly:** Full backup test

---

## Security & Compliance

### Security Best Practices

**1. Network Security**
```bash
# Firewall configuration
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

**2. SSL/TLS Configuration**
```nginx
# Nginx SSL configuration
server {
    listen 443 ssl http2;
    server_name licenses.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**3. Database Security**
```bash
# Change default password
docker compose exec postgres psql -U postgres -c \
  "ALTER USER postgres PASSWORD 'new_strong_password';"

# Restrict network access
# In docker-compose.yml:
postgres:
  networks:
    - internal
```

**4. API Security**
- Rate limiting enabled (100 requests/15 minutes)
- JWT token expiration (7 days)
- CORS restrictions
- Input validation
- SQL injection prevention

### Compliance

**GDPR Compliance:**
- User data encryption
- Right to be forgotten (delete user data)
- Data export capability
- Audit logging

**SOC 2 Compliance:**
- Access controls
- Encryption at rest and in transit
- Audit trails
- Incident response procedures

**HIPAA Compliance (if applicable):**
- PHI encryption
- Access logging
- Business Associate Agreements
- Security risk assessments

### Audit Logging

**Enable Audit Logging:**
```javascript
// In license server
{
  auditLog: {
    enabled: true,
    events: [
      'license.created',
      'license.validated',
      'license.revoked',
      'user.login',
      'user.logout',
      'api.key.created'
    ]
  }
}
```

**View Audit Logs:**
```sql
SELECT * FROM "LicenseValidation"
WHERE "validatedAt" > NOW() - INTERVAL '7 days'
ORDER BY "validatedAt" DESC;
```

---

## Backup & Recovery

### Backup Strategy

**Automated Backups:**
```bash
#!/bin/bash
# /usr/local/bin/backup-database.sh

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/itechsmart_licenses_$DATE.sql"

# Create backup
docker compose exec -T postgres pg_dump -U postgres itechsmart_licenses > "$BACKUP_FILE"

# Compress
gzip "$BACKUP_FILE"

# Upload to S3 (optional)
aws s3 cp "${BACKUP_FILE}.gz" s3://your-bucket/backups/

# Keep only last 30 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

**Schedule Backups:**
```bash
# Add to crontab
0 2 * * * /usr/local/bin/backup-database.sh
```

### Recovery Procedures

**Restore from Backup:**
```bash
#!/bin/bash
# restore-database.sh

BACKUP_FILE=$1

# Stop license server
docker compose stop license-server

# Decompress backup
gunzip -c "$BACKUP_FILE" > /tmp/restore.sql

# Drop and recreate database
docker compose exec postgres psql -U postgres -c \
  "DROP DATABASE IF EXISTS itechsmart_licenses;"
docker compose exec postgres psql -U postgres -c \
  "CREATE DATABASE itechsmart_licenses;"

# Restore backup
docker compose exec -T postgres psql -U postgres itechsmart_licenses < /tmp/restore.sql

# Cleanup
rm /tmp/restore.sql

# Start license server
docker compose start license-server

echo "Database restored successfully"
```

### Disaster Recovery

**Recovery Time Objective (RTO):** 4 hours  
**Recovery Point Objective (RPO):** 24 hours

**DR Checklist:**
- [ ] Backup verified and accessible
- [ ] Secondary server provisioned
- [ ] DNS failover configured
- [ ] SSL certificates available
- [ ] Recovery procedures documented
- [ ] Team trained on recovery process

---

## Troubleshooting

### Common Issues

#### Issue: License Server Won't Start

**Symptoms:**
- Container exits immediately
- Database connection errors
- Port already in use

**Solutions:**
```bash
# Check logs
docker compose logs license-server

# Verify database
docker compose exec postgres psql -U postgres -l

# Check port availability
sudo netstat -tulpn | grep 3001

# Restart services
docker compose restart
```

#### Issue: High Memory Usage

**Symptoms:**
- Server becomes slow
- Out of memory errors
- Container restarts

**Solutions:**
```bash
# Check memory usage
docker stats

# Increase memory limit in docker-compose.yml
services:
  license-server:
    deploy:
      resources:
        limits:
          memory: 2G

# Optimize database
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c \
  "VACUUM FULL ANALYZE;"
```

#### Issue: Slow API Responses

**Symptoms:**
- Response times > 1 second
- Timeouts
- User complaints

**Solutions:**
```bash
# Check slow queries
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c \
  "SELECT query, calls, total_time, mean_time 
   FROM pg_stat_statements 
   ORDER BY mean_time DESC 
   LIMIT 10;"

# Add indexes
# Optimize queries
# Scale horizontally
```

### Debug Mode

**Enable Debug Logging:**
```bash
# In .env
LOG_LEVEL=debug

# Restart
docker compose restart license-server
```

**View Debug Logs:**
```bash
docker compose logs -f license-server | grep DEBUG
```

---

## API Reference

### Authentication

**POST /api/auth/register**
- Create new organization
- Returns: Organization, User, JWT token

**POST /api/auth/login**
- Authenticate user
- Returns: JWT token, User details

**POST /api/auth/refresh**
- Refresh JWT token
- Returns: New JWT token

### License Management

**POST /api/licenses**
- Create new license
- Requires: Admin JWT token
- Returns: License details with key

**GET /api/licenses/:id**
- Get license details
- Requires: JWT token
- Returns: License information

**POST /api/licenses/validate**
- Validate license key
- Public endpoint
- Returns: Validation result

**PUT /api/licenses/:id**
- Update license
- Requires: Admin JWT token
- Returns: Updated license

**DELETE /api/licenses/:id**
- Revoke license
- Requires: Admin JWT token
- Returns: Success message

### Organization Management

**GET /api/organizations/:id**
- Get organization details
- Requires: JWT token
- Returns: Organization info

**PUT /api/organizations/:id**
- Update organization
- Requires: Admin JWT token
- Returns: Updated organization

**GET /api/organizations/:id/licenses**
- List organization licenses
- Requires: JWT token
- Returns: Array of licenses

### Usage Tracking

**POST /api/usage**
- Record usage event
- Requires: JWT token
- Returns: Usage record

**GET /api/usage/:licenseId**
- Get usage statistics
- Requires: JWT token
- Returns: Usage data

### Webhooks

**POST /api/webhooks**
- Create webhook
- Requires: JWT token
- Returns: Webhook details

**GET /api/webhooks**
- List webhooks
- Requires: JWT token
- Returns: Array of webhooks

**DELETE /api/webhooks/:id**
- Delete webhook
- Requires: JWT token
- Returns: Success message

### Health

**GET /health**
- Health check
- Public endpoint
- Returns: Server status

---

## Support

### Administrator Resources

**Documentation:**
- License Server: `license-server/README.md`
- API Guide: `license-server/API_TESTING_GUIDE.md`
- Deployment: `license-server/PRODUCTION_DEPLOYMENT_GUIDE.md`
- Monitoring: `license-server/MONITORING_GUIDE.md`

**Support Channels:**
- **Email:** admin-support@itechsmart.com
- **Slack:** #admin-support
- **Phone:** 1-800-ITECH-ADMIN
- **Portal:** https://admin.itechsmart.com

**Emergency Contact:**
- **24/7 Hotline:** 1-800-ITECH-911
- **Email:** emergency@itechsmart.com
- **Response Time:** < 1 hour for critical issues

---

**Document Version:** 1.0  
**Last Updated:** November 16, 2025  
**For:** iTechSmart Suite v1.0.0

For the latest documentation, visit: https://docs.itechsmart.com/admin