# iTechSmart License Server

Production-ready SaaS licensing system with API-based validation, tiered pricing, and organization/domain-based licensing.

## Features

- ✅ **Multi-tier Licensing**: Trial, Starter, Professional, Enterprise, Unlimited
- ✅ **Organization Management**: Domain-based licensing with user management
- ✅ **API Key Authentication**: Secure programmatic access
- ✅ **Usage Tracking**: Comprehensive metering and analytics
- ✅ **Machine Locking**: Optional device-based license enforcement
- ✅ **Webhook Support**: Real-time event notifications
- ✅ **Rate Limiting**: Built-in protection against abuse
- ✅ **Audit Logging**: Complete validation history
- ✅ **RESTful API**: Clean, documented endpoints
- ✅ **PostgreSQL Database**: Reliable data persistence
- ✅ **Docker Support**: Easy deployment

## Quick Start

### 1. Prerequisites

- Node.js 20+
- PostgreSQL 15+
- Redis 7+ (optional, for caching)
- Docker & Docker Compose (for containerized deployment)

### 2. Installation

```bash
# Clone repository
git clone https://github.com/Iteksmart/iTechSmart.git
cd iTechSmart/license-server

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 3. Database Setup

```bash
# Generate Prisma Client
npx prisma generate

# Run migrations
npx prisma migrate deploy

# (Optional) Seed database
npx prisma db seed
```

### 4. Start Server

**Development:**
```bash
npm run dev
```

**Production:**
```bash
npm run build
npm start
```

**Docker:**
```bash
docker-compose up -d
```

## API Documentation

### Base URL
```
http://localhost:3000/api
```

### Authentication

**JWT Token:**
```bash
Authorization: Bearer <token>
```

**API Key:**
```bash
X-API-Key: itsk_<key>
```

### Endpoints

#### 1. Authentication

**Register Organization**
```http
POST /api/auth/register
Content-Type: application/json

{
  "organizationName": "Acme Corp",
  "domain": "acme.com",
  "email": "admin@acme.com",
  "password": "SecurePass123!",
  "name": "John Doe",
  "phone": "+1234567890",
  "country": "USA"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid",
    "email": "admin@acme.com",
    "name": "John Doe",
    "role": "admin"
  },
  "organization": {
    "id": "uuid",
    "name": "Acme Corp",
    "domain": "acme.com"
  },
  "license": {
    "licenseKey": "XXXX-XXXX-XXXX-XXXX-XXXX",
    "tier": "TRIAL",
    "trialEndsAt": "2025-02-15T00:00:00.000Z"
  }
}
```

**Login**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "admin@acme.com",
  "password": "SecurePass123!"
}
```

#### 2. License Validation

**Validate License**
```http
POST /api/licenses/validate
Content-Type: application/json

{
  "licenseKey": "XXXX-XXXX-XXXX-XXXX-XXXX",
  "productId": "itechsmart-ninja",
  "machineId": "optional-machine-id"
}
```

**Response (Valid):**
```json
{
  "valid": true,
  "license": {
    "tier": "PROFESSIONAL",
    "organization": "Acme Corp",
    "maxUsers": 100,
    "maxProducts": 15,
    "allowedProducts": ["itechsmart-ninja", "itechsmart-enterprise", ...],
    "features": {
      "priority_support": true,
      "custom_branding": true
    },
    "expiresAt": "2026-01-15T00:00:00.000Z",
    "isTrial": false
  }
}
```

**Response (Invalid):**
```json
{
  "valid": false,
  "reason": "License expired"
}
```

#### 3. License Management

**Create License (Admin)**
```http
POST /api/licenses/create
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "organizationId": "uuid",
  "tier": "PROFESSIONAL",
  "maxUsers": 100,
  "maxProducts": 15,
  "allowedProducts": ["itechsmart-ninja", "itechsmart-enterprise"],
  "expiresAt": "2026-01-15T00:00:00.000Z"
}
```

**Get License Details**
```http
GET /api/licenses/:id
Authorization: Bearer <token>
```

**List Organization Licenses**
```http
GET /api/licenses
Authorization: Bearer <token>
```

**Update License Status (Admin)**
```http
PATCH /api/licenses/:id/status
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "status": "SUSPENDED"
}
```

#### 4. Organization Management

**Get Organization Details**
```http
GET /api/organizations/me
Authorization: Bearer <token>
```

**Update Organization**
```http
PATCH /api/organizations/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Acme Corporation",
  "phone": "+1234567890",
  "address": "123 Main St, City, State 12345"
}
```

**Get API Keys**
```http
GET /api/organizations/me/api-keys
Authorization: Bearer <token>
```

**Create API Key**
```http
POST /api/organizations/me/api-keys
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Production API Key",
  "scopes": ["read", "write"],
  "expiresAt": "2026-01-15T00:00:00.000Z"
}
```

**Delete API Key**
```http
DELETE /api/organizations/me/api-keys/:id
Authorization: Bearer <token>
```

#### 5. Usage Tracking

**Record Usage**
```http
POST /api/usage/record
X-API-Key: itsk_<key>
Content-Type: application/json

{
  "licenseKey": "XXXX-XXXX-XXXX-XXXX-XXXX",
  "productId": "itechsmart-ninja",
  "eventType": "api_call",
  "quantity": 1,
  "metadata": {
    "endpoint": "/api/issues/resolve",
    "duration_ms": 150
  }
}
```

**Get Usage Summary**
```http
GET /api/usage/summary?period=month
Authorization: Bearer <token>
```

#### 6. Webhooks

**List Webhooks**
```http
GET /api/webhooks
Authorization: Bearer <token>
```

**Create Webhook**
```http
POST /api/webhooks
Authorization: Bearer <token>
Content-Type: application/json

{
  "url": "https://your-app.com/webhooks/license",
  "events": ["license.activated", "license.expired", "license.suspended"]
}
```

**Delete Webhook**
```http
DELETE /api/webhooks/:id
Authorization: Bearer <token>
```

#### 7. Health Check

**Check Server Health**
```http
GET /api/health
```

## Pricing Tiers

### Trial
- **Price**: Free
- **Duration**: 30 days
- **Users**: 5
- **Products**: 3
- **API Calls**: 1,000/day
- **Storage**: 10 GB
- **Features**: Demo watermark

### Starter ($99/month)
- **Users**: 25
- **Products**: 5
- **API Calls**: 10,000/day
- **Storage**: 100 GB
- **Features**: Email support

### Professional ($499/month)
- **Users**: 100
- **Products**: 15
- **API Calls**: 50,000/day
- **Storage**: 500 GB
- **Features**: Priority support, custom branding

### Enterprise ($2,499/month)
- **Users**: 1,000
- **Products**: All 35
- **API Calls**: 1,000,000/day
- **Storage**: 2 TB
- **Features**: 24/7 support, SLA, audit logs, custom branding

### Unlimited ($9,999/month)
- **Users**: Unlimited
- **Products**: All 35
- **API Calls**: Unlimited
- **Storage**: 10 TB
- **Features**: White-label, custom integrations, dedicated support, custom development

## Environment Variables

```bash
# Server
NODE_ENV=production
PORT=3000
HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/itechsmart_licenses

# Security
JWT_SECRET=your-secret-key
ENCRYPTION_KEY=your-encryption-key

# CORS
CORS_ORIGIN=https://your-app.com

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# Stripe (optional)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
EMAIL_FROM=noreply@itechsmart.dev

# Redis (optional)
REDIS_URL=redis://localhost:6379
```

## Deployment

### Docker Deployment

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f license-server

# Stop
docker-compose down
```

### Production Deployment

1. **Set up PostgreSQL database**
2. **Configure environment variables**
3. **Run database migrations**
4. **Start the server**
5. **Set up reverse proxy (nginx)**
6. **Enable SSL/TLS**
7. **Configure monitoring**

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name license.itechsmart.dev;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name license.itechsmart.dev;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Security Best Practices

1. **Use strong JWT secrets** (32+ characters)
2. **Enable HTTPS** in production
3. **Rotate API keys** regularly
4. **Monitor rate limits**
5. **Review audit logs**
6. **Keep dependencies updated**
7. **Use environment variables** for secrets
8. **Enable database backups**
9. **Implement IP whitelisting** for admin endpoints
10. **Use strong passwords** (enforce policy)

## Monitoring

### Health Check
```bash
curl http://localhost:3000/api/health
```

### Database Status
```bash
docker-compose exec postgres pg_isready
```

### Logs
```bash
# Application logs
tail -f logs/license-server.log

# Error logs
tail -f logs/error.log

# Docker logs
docker-compose logs -f
```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U postgres -d itechsmart_licenses -c "SELECT 1"
```

### Migration Issues
```bash
# Reset database (WARNING: deletes all data)
npx prisma migrate reset

# Apply migrations
npx prisma migrate deploy
```

### Port Already in Use
```bash
# Find process using port 3000
lsof -i :3000

# Kill process
kill -9 <PID>
```

## Support

- **Email**: support@itechsmart.dev
- **Documentation**: https://docs.itechsmart.dev
- **GitHub Issues**: https://github.com/Iteksmart/iTechSmart/issues

## License

Copyright © 2025 iTechSmart Inc. All rights reserved.