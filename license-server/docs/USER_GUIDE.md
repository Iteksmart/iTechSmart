# License Server - Administrator Guide

**Version**: 1.0.0  
**Last Updated**: November 17, 2024  
**Product Type**: SaaS Licensing System  
**Audience**: System Administrators, License Managers

---

## 📚 Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [License Management](#license-management)
4. [Organization Management](#organization-management)
5. [User Management](#user-management)
6. [API Key Management](#api-key-management)
7. [Usage Tracking](#usage-tracking)
8. [Reporting and Analytics](#reporting-and-analytics)
9. [Configuration](#configuration)
10. [Troubleshooting](#troubleshooting)
11. [FAQ](#faq)
12. [Best Practices](#best-practices)

---

## Introduction

### What is License Server?

The iTechSmart License Server is a production-ready SaaS licensing system that provides centralized license management, validation, and usage tracking for all iTechSmart Suite products. It enables organizations to control access, monitor usage, and manage subscriptions across their entire deployment.

### Key Features

- 🔐 **API-Based Validation** - Secure, token-based license validation
- 🏢 **Organization Management** - Multi-tenant architecture with organization isolation
- 📊 **Usage Tracking** - Real-time monitoring and metering of product usage
- 💰 **Tiered Pricing** - Support for multiple license tiers (Trial, Starter, Pro, Enterprise, Unlimited)
- 🌐 **Domain-Based Licensing** - Automatic license assignment based on email domains
- 📈 **Analytics Dashboard** - Comprehensive reporting and insights
- 🔄 **Auto-Renewal** - Automated subscription renewal and billing integration
- 🚨 **Alerts & Notifications** - Proactive monitoring and alerting
- 🔒 **Security** - Enterprise-grade security with encryption and audit logging

### System Requirements

#### Minimum Requirements
- **CPU**: 2 cores (2.0 GHz or faster)
- **RAM**: 4 GB
- **Storage**: 20 GB
- **Database**: PostgreSQL 12+
- **OS**: Linux (Ubuntu 20.04+, CentOS 8+, or equivalent)
- **Network**: 10 Mbps internet connection

#### Recommended Requirements (Production)
- **CPU**: 4+ cores (2.5 GHz or faster)
- **RAM**: 8+ GB
- **Storage**: 50+ GB SSD
- **Database**: PostgreSQL 14+ with replication
- **OS**: Linux with latest security patches
- **Network**: 100+ Mbps with redundancy
- **Load Balancer**: For high availability
- **Backup**: Automated daily backups

---

## Getting Started

### Installation

#### Prerequisites

1. **Docker and Docker Compose**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install docker.io docker-compose
   
   # CentOS/RHEL
   sudo yum install docker docker-compose
   
   # Start Docker service
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

2. **PostgreSQL Database**
   ```bash
   # Option 1: Use Docker (recommended for testing)
   docker run -d \
     --name license-db \
     -e POSTGRES_PASSWORD=secure_password \
     -e POSTGRES_DB=license_server \
     -p 5432:5432 \
     postgres:14
   
   # Option 2: Install locally
   sudo apt-get install postgresql-14
   ```

#### Quick Start

1. **Clone Repository**
   ```bash
   git clone https://github.com/Iteksmart/iTechSmart.git
   cd iTechSmart/license-server
   ```

2. **Configure Environment**
   ```bash
   # Copy example configuration
   cp .env.example .env
   
   # Edit configuration
   nano .env
   ```

3. **Configure Database**
   ```env
   # Database Configuration
   DATABASE_URL=postgresql://postgres:password@localhost:5432/license_server
   
   # Application Configuration
   NODE_ENV=production
   PORT=3000
   SECRET_KEY=your-secret-key-here-change-this
   
   # JWT Configuration
   JWT_SECRET=your-jwt-secret-here-change-this
   JWT_EXPIRY=24h
   
   # Email Configuration (optional)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASS=your-app-password
   ```

4. **Initialize Database**
   ```bash
   # Run migrations
   npm run migrate
   
   # Seed initial data (optional)
   npm run seed
   ```

5. **Start Server**
   ```bash
   # Using Docker Compose (recommended)
   docker-compose up -d
   
   # Or run directly
   npm install
   npm run build
   npm start
   ```

6. **Verify Installation**
   ```bash
   # Check server health
   curl http://localhost:3000/health
   
   # Expected response:
   # {"status":"ok","database":"connected","version":"1.0.0"}
   ```

### First-Time Setup

#### 1. Create Admin Account

```bash
# Using CLI tool
npm run create-admin

# Or via API
curl -X POST http://localhost:3000/api/admin/setup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourdomain.com",
    "password": "SecurePassword123!",
    "name": "System Administrator"
  }'
```

#### 2. Login to Admin Panel

1. Navigate to `http://localhost:3000/admin`
2. Enter admin credentials
3. Complete initial setup wizard:
   - Configure organization settings
   - Set up license tiers
   - Configure email notifications
   - Review security settings

#### 3. Create First Organization

1. Go to **Organizations** → **Create New**
2. Fill in organization details:
   - **Name**: Organization name
   - **Domain**: Email domain (e.g., `company.com`)
   - **License Tier**: Select tier
   - **Max Users**: Set user limit
   - **Expiry Date**: Set expiration
3. Click **Create Organization**
4. Note the generated **API Key** (shown once)

---

## License Management

### License Tiers

The License Server supports five license tiers:

| Tier | Features | Max Users | Max Products | Price |
|------|----------|-----------|--------------|-------|
| **Trial** | Basic features, 30-day limit | 5 | 3 | Free |
| **Starter** | Core features | 25 | 10 | $99/month |
| **Pro** | Advanced features | 100 | 20 | $299/month |
| **Enterprise** | All features + support | 500 | All | $999/month |
| **Unlimited** | Everything + custom | Unlimited | All | Custom |

### Creating Licenses

#### Via Admin Panel

1. **Navigate to Licenses**
   - Click **Licenses** in sidebar
   - Click **Create New License**

2. **Fill License Details**
   ```
   Organization: Select organization
   License Tier: Select tier
   Products: Select allowed products
   Max Users: Set user limit
   Start Date: Set start date
   Expiry Date: Set expiration
   Auto-Renew: Enable/disable
   ```

3. **Generate License**
   - Click **Generate License**
   - Copy the license key
   - Share with organization admin

#### Via API

```bash
# Create license via API
curl -X POST http://localhost:3000/api/licenses \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "organizationId": "org-123",
    "tier": "pro",
    "products": ["ninja", "supreme", "citadel"],
    "maxUsers": 100,
    "expiryDate": "2025-12-31",
    "autoRenew": true
  }'
```

### Validating Licenses

#### API Validation

```bash
# Validate license
curl -X POST http://localhost:3000/api/licenses/validate \
  -H "Content-Type: application/json" \
  -d '{
    "apiKey": "org-api-key",
    "product": "ninja",
    "userId": "user@company.com"
  }'

# Response:
{
  "valid": true,
  "tier": "pro",
  "expiryDate": "2025-12-31",
  "features": ["feature1", "feature2"],
  "limits": {
    "maxUsers": 100,
    "currentUsers": 45
  }
}
```

#### Validation Flow

1. **Client Request** → License Server
2. **Server Checks**:
   - API key validity
   - Organization status
   - License expiration
   - User limits
   - Product access
3. **Server Response** → Client
4. **Client Action** based on response

### Managing Licenses

#### Viewing Licenses

```bash
# List all licenses
GET /api/licenses

# Get specific license
GET /api/licenses/:id

# Filter licenses
GET /api/licenses?tier=pro&status=active
```

#### Updating Licenses

```bash
# Update license
PATCH /api/licenses/:id
{
  "tier": "enterprise",
  "maxUsers": 500,
  "expiryDate": "2026-12-31"
}
```

#### Revoking Licenses

```bash
# Revoke license
POST /api/licenses/:id/revoke
{
  "reason": "Contract terminated",
  "notifyUsers": true
}
```

#### Renewing Licenses

```bash
# Renew license
POST /api/licenses/:id/renew
{
  "duration": "1 year",
  "tier": "pro"
}
```

---

## Organization Management

### Creating Organizations

#### Via Admin Panel

1. **Navigate to Organizations**
2. **Click "Create Organization"**
3. **Fill Organization Details**:
   ```
   Name: Company Name
   Domain: company.com
   Contact Email: admin@company.com
   License Tier: Pro
   Max Users: 100
   ```
4. **Configure Settings**:
   - Enable/disable features
   - Set usage limits
   - Configure notifications
5. **Generate API Key**
6. **Save Organization**

#### Via API

```bash
curl -X POST http://localhost:3000/api/organizations \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation",
    "domain": "acme.com",
    "contactEmail": "admin@acme.com",
    "tier": "enterprise",
    "maxUsers": 500
  }'
```

### Organization Settings

#### General Settings
- Organization name and description
- Primary contact information
- Billing information
- Time zone and locale

#### License Settings
- Default license tier
- Auto-renewal preferences
- Grace period configuration
- Upgrade/downgrade policies

#### Security Settings
- API key rotation policy
- IP whitelist/blacklist
- Two-factor authentication
- Session timeout
- Password policies

#### Notification Settings
- Email notifications
- Webhook endpoints
- Alert thresholds
- Notification preferences

### Managing Organizations

#### Viewing Organizations

```bash
# List all organizations
GET /api/organizations

# Get organization details
GET /api/organizations/:id

# Get organization statistics
GET /api/organizations/:id/stats
```

#### Updating Organizations

```bash
# Update organization
PATCH /api/organizations/:id
{
  "name": "New Name",
  "tier": "enterprise",
  "maxUsers": 1000
}
```

#### Suspending Organizations

```bash
# Suspend organization
POST /api/organizations/:id/suspend
{
  "reason": "Payment overdue",
  "notifyUsers": true
}

# Reactivate organization
POST /api/organizations/:id/activate
```

---

## User Management

### Adding Users

#### Via Admin Panel

1. **Navigate to Users**
2. **Click "Add User"**
3. **Enter User Details**:
   ```
   Email: user@company.com
   Name: John Doe
   Role: User/Admin
   Organization: Select organization
   Products: Select allowed products
   ```
4. **Send Invitation Email**
5. **User Activates Account**

#### Via API

```bash
curl -X POST http://localhost:3000/api/users \
  -H "Authorization: Bearer ORG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@company.com",
    "name": "John Doe",
    "role": "user",
    "products": ["ninja", "supreme"]
  }'
```

### User Roles

| Role | Permissions |
|------|-------------|
| **Super Admin** | Full system access, manage all organizations |
| **Org Admin** | Manage organization, users, licenses |
| **User** | Access assigned products only |
| **Viewer** | Read-only access to organization data |

### Managing Users

#### Viewing Users

```bash
# List organization users
GET /api/organizations/:orgId/users

# Get user details
GET /api/users/:id

# Search users
GET /api/users?search=john&role=admin
```

#### Updating Users

```bash
# Update user
PATCH /api/users/:id
{
  "name": "John Smith",
  "role": "admin",
  "products": ["ninja", "supreme", "citadel"]
}
```

#### Deactivating Users

```bash
# Deactivate user
POST /api/users/:id/deactivate

# Reactivate user
POST /api/users/:id/activate
```

---

## API Key Management

### Generating API Keys

#### Organization API Keys

```bash
# Generate new API key
POST /api/organizations/:id/api-keys
{
  "name": "Production Key",
  "permissions": ["read", "validate"],
  "expiryDate": "2025-12-31"
}

# Response:
{
  "apiKey": "org_live_abc123...",
  "name": "Production Key",
  "createdAt": "2024-11-17T00:00:00Z"
}
```

#### User API Keys

```bash
# Generate user API key
POST /api/users/:id/api-keys
{
  "name": "Personal Access Token",
  "scopes": ["read:licenses", "validate:licenses"]
}
```

### Managing API Keys

#### Listing API Keys

```bash
# List organization API keys
GET /api/organizations/:id/api-keys

# List user API keys
GET /api/users/:id/api-keys
```

#### Rotating API Keys

```bash
# Rotate API key
POST /api/api-keys/:id/rotate

# Old key is invalidated
# New key is returned
```

#### Revoking API Keys

```bash
# Revoke API key
DELETE /api/api-keys/:id
```

### API Key Security

**Best Practices:**
1. **Never commit API keys** to version control
2. **Use environment variables** for API keys
3. **Rotate keys regularly** (every 90 days recommended)
4. **Use different keys** for different environments
5. **Monitor API key usage** for suspicious activity
6. **Revoke unused keys** immediately
7. **Use scoped keys** with minimal permissions

---

## Usage Tracking

### Tracking Metrics

The License Server automatically tracks:

- **License Validations**: Number of validation requests
- **Active Users**: Unique users per organization
- **Product Usage**: Usage per product
- **API Calls**: API request volume
- **Error Rates**: Failed validations and errors
- **Response Times**: API performance metrics

### Viewing Usage Data

#### Via Admin Panel

1. **Navigate to Analytics**
2. **Select Organization**
3. **Choose Date Range**
4. **View Metrics**:
   - Usage graphs
   - User activity
   - Product popularity
   - Trend analysis

#### Via API

```bash
# Get usage statistics
GET /api/organizations/:id/usage?from=2024-01-01&to=2024-12-31

# Response:
{
  "totalValidations": 150000,
  "activeUsers": 87,
  "productUsage": {
    "ninja": 45000,
    "supreme": 35000,
    "citadel": 25000
  },
  "averageResponseTime": "45ms"
}
```

### Usage Alerts

#### Configuring Alerts

```bash
# Create usage alert
POST /api/alerts
{
  "organizationId": "org-123",
  "type": "usage_limit",
  "threshold": 90,
  "action": "email",
  "recipients": ["admin@company.com"]
}
```

#### Alert Types

- **Usage Limit**: Alert when approaching user/validation limits
- **License Expiry**: Alert before license expiration
- **Unusual Activity**: Alert on suspicious usage patterns
- **Performance**: Alert on slow response times
- **Errors**: Alert on high error rates

---

## Reporting and Analytics

### Built-in Reports

#### License Report
- Active licenses
- Expiring licenses
- License utilization
- Revenue by tier

#### Usage Report
- Validations per day/week/month
- Active users trend
- Product usage breakdown
- Peak usage times

#### Organization Report
- Organization growth
- User distribution
- Tier distribution
- Churn analysis

### Generating Reports

#### Via Admin Panel

1. **Navigate to Reports**
2. **Select Report Type**
3. **Configure Parameters**:
   - Date range
   - Organizations
   - Filters
4. **Generate Report**
5. **Export** (PDF, CSV, Excel)

#### Via API

```bash
# Generate report
POST /api/reports/generate
{
  "type": "usage",
  "format": "pdf",
  "dateRange": {
    "from": "2024-01-01",
    "to": "2024-12-31"
  },
  "organizations": ["org-123", "org-456"]
}

# Download report
GET /api/reports/:id/download
```

### Custom Reports

```bash
# Create custom report
POST /api/reports/custom
{
  "name": "Monthly Executive Summary",
  "metrics": [
    "totalRevenue",
    "activeOrganizations",
    "newUsers",
    "churnRate"
  ],
  "schedule": "monthly",
  "recipients": ["exec@company.com"]
}
```

---

## Configuration

### Server Configuration

#### Environment Variables

```env
# Server
NODE_ENV=production
PORT=3000
HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
DATABASE_POOL_MIN=2
DATABASE_POOL_MAX=10

# Security
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret
JWT_EXPIRY=24h
BCRYPT_ROUNDS=12

# Rate Limiting
RATE_LIMIT_WINDOW=15m
RATE_LIMIT_MAX=100

# CORS
CORS_ORIGIN=https://yourdomain.com
CORS_CREDENTIALS=true

# Logging
LOG_LEVEL=info
LOG_FORMAT=json

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email
SMTP_PASS=your-password
EMAIL_FROM=noreply@itechsmart.com

# Monitoring
SENTRY_DSN=your-sentry-dsn
PROMETHEUS_PORT=9090
```

### Database Configuration

#### PostgreSQL Tuning

```sql
-- Recommended settings for production
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET work_mem = '10MB';
ALTER SYSTEM SET min_wal_size = '1GB';
ALTER SYSTEM SET max_wal_size = '4GB';
```

### Security Configuration

#### SSL/TLS

```bash
# Generate SSL certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/license-server.key \
  -out /etc/ssl/certs/license-server.crt

# Configure in .env
SSL_KEY=/etc/ssl/private/license-server.key
SSL_CERT=/etc/ssl/certs/license-server.crt
```

#### Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 22/tcp   # SSH (restrict to specific IPs)
sudo ufw enable
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Database Connection Failed

**Symptoms:**
- Server won't start
- "Cannot connect to database" error

**Solutions:**

1. **Check Database Status**
   ```bash
   # Check if PostgreSQL is running
   sudo systemctl status postgresql
   
   # Start if not running
   sudo systemctl start postgresql
   ```

2. **Verify Connection String**
   ```bash
   # Test connection
   psql postgresql://user:pass@host:5432/db
   ```

3. **Check Firewall**
   ```bash
   # Ensure port 5432 is accessible
   sudo ufw allow 5432/tcp
   ```

#### Issue 2: License Validation Fails

**Symptoms:**
- Validation requests return errors
- "Invalid API key" messages

**Solutions:**

1. **Verify API Key**
   ```bash
   # Check API key in database
   SELECT * FROM api_keys WHERE key = 'your-api-key';
   ```

2. **Check Organization Status**
   ```bash
   # Ensure organization is active
   SELECT status FROM organizations WHERE id = 'org-id';
   ```

3. **Review Logs**
   ```bash
   # Check server logs
   docker-compose logs -f license-server
   ```

#### Issue 3: High Response Times

**Symptoms:**
- Slow API responses
- Timeouts

**Solutions:**

1. **Check Database Performance**
   ```sql
   -- Find slow queries
   SELECT query, mean_exec_time 
   FROM pg_stat_statements 
   ORDER BY mean_exec_time DESC 
   LIMIT 10;
   ```

2. **Add Database Indexes**
   ```sql
   -- Add indexes for common queries
   CREATE INDEX idx_licenses_org ON licenses(organization_id);
   CREATE INDEX idx_validations_date ON validations(created_at);
   ```

3. **Scale Resources**
   - Increase server CPU/RAM
   - Add database replicas
   - Implement caching (Redis)

---

## FAQ

**Q: How many organizations can the License Server handle?**  
A: The server can handle thousands of organizations. Performance depends on your infrastructure.

**Q: Can I integrate with my existing billing system?**  
A: Yes, the License Server provides webhooks and APIs for billing integration.

**Q: How is data backed up?**  
A: Implement automated PostgreSQL backups. See DEPLOYMENT_GUIDE.md for details.

**Q: Can I run multiple License Servers for high availability?**  
A: Yes, you can run multiple instances behind a load balancer with a shared database.

**Q: How do I migrate from another licensing system?**  
A: Use the import API to bulk import licenses and organizations. Contact support for assistance.

---

## Best Practices

### Security
1. Use strong, unique API keys
2. Enable SSL/TLS in production
3. Implement rate limiting
4. Regular security audits
5. Keep software updated

### Performance
1. Use database connection pooling
2. Implement caching for frequent queries
3. Monitor and optimize slow queries
4. Scale horizontally when needed
5. Use CDN for static assets

### Monitoring
1. Set up health checks
2. Monitor key metrics
3. Configure alerts
4. Review logs regularly
5. Track error rates

### Maintenance
1. Regular database backups
2. Test disaster recovery
3. Update dependencies
4. Review and rotate API keys
5. Clean up old data

---

## Additional Resources

- **API Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Demo Setup**: [DEMO_SETUP.md](DEMO_SETUP.md)
- **GitHub**: https://github.com/Iteksmart/iTechSmart
- **Support**: support@itechsmart.com

---

**Last Updated**: November 17, 2024  
**Document Version**: 1.0  
**Maintained by**: iTechSmart Team

---

**End of Administrator Guide**