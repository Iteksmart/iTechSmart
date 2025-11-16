# iTechSmart License Server - Production Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the iTechSmart License Server to production.

## Prerequisites

### Required Software
- Docker and Docker Compose (v2.0+)
- Node.js 20+ (for local development)
- PostgreSQL 15+ (if not using Docker)
- Git

### Required Accounts
- Domain name for the license server
- SSL certificate (Let's Encrypt recommended)
- SMTP service for email notifications (optional)
- Stripe account for payment processing (optional)

## Deployment Options

### Option 1: Docker Compose (Recommended)

This is the easiest and most reliable deployment method.

#### Step 1: Clone the Repository
```bash
git clone https://github.com/Iteksmart/iTechSmart.git
cd iTechSmart/license-server
```

#### Step 2: Configure Environment Variables
```bash
cp .env.example .env
nano .env
```

Update the following critical variables:
```env
# Database - Use strong password
DATABASE_URL="postgresql://postgres:STRONG_PASSWORD@postgres:5432/itechsmart_licenses?schema=public"

# JWT Secret - Generate with: openssl rand -base64 32
JWT_SECRET=your-generated-secret-key-min-32-chars

# Admin Credentials
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=YourStrongPassword123!

# CORS - Set to your domain
CORS_ORIGIN=https://yourdomain.com

# Optional: Stripe for payments
STRIPE_SECRET_KEY=sk_live_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Optional: Email notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SMTP_FROM=noreply@yourdomain.com
```

#### Step 3: Start the Services
```bash
# Start PostgreSQL and License Server
docker compose up -d

# Check logs
docker compose logs -f license-server

# Verify health
curl http://localhost:3001/health
```

#### Step 4: Initialize the Database
The database migrations run automatically on startup. Verify with:
```bash
docker compose exec license-server npx prisma migrate status
```

#### Step 5: Create Initial Admin User
```bash
# The admin user is created automatically on first startup
# Check logs for confirmation
docker compose logs license-server | grep "Admin user"
```

#### Step 6: Test the API
```bash
# Health check
curl http://localhost:3001/health

# Login as admin
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourdomain.com",
    "password": "YourStrongPassword123!"
  }'
```

### Option 2: Cloud Deployment (AWS, GCP, Azure)

#### AWS Deployment with ECS

1. **Create RDS PostgreSQL Instance**
```bash
aws rds create-db-instance \
  --db-instance-identifier itechsmart-licenses \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password YOUR_PASSWORD \
  --allocated-storage 20
```

2. **Build and Push Docker Image**
```bash
# Build image
docker build -t itechsmart-license-server .

# Tag for ECR
docker tag itechsmart-license-server:latest \
  YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/itechsmart-license-server:latest

# Push to ECR
docker push YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/itechsmart-license-server:latest
```

3. **Create ECS Task Definition**
```json
{
  "family": "itechsmart-license-server",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "license-server",
      "image": "YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/itechsmart-license-server:latest",
      "portMappings": [
        {
          "containerPort": 3001,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://postgres:PASSWORD@RDS_ENDPOINT:5432/itechsmart_licenses"
        },
        {
          "name": "JWT_SECRET",
          "value": "your-secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/itechsmart-license-server",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

4. **Create ECS Service**
```bash
aws ecs create-service \
  --cluster your-cluster \
  --service-name itechsmart-license-server \
  --task-definition itechsmart-license-server \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

#### Google Cloud Platform (GCP) Deployment

1. **Create Cloud SQL PostgreSQL Instance**
```bash
gcloud sql instances create itechsmart-licenses \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1
```

2. **Deploy to Cloud Run**
```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/YOUR_PROJECT/itechsmart-license-server

# Deploy to Cloud Run
gcloud run deploy itechsmart-license-server \
  --image gcr.io/YOUR_PROJECT/itechsmart-license-server \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL="postgresql://..." \
  --set-env-vars JWT_SECRET="your-secret"
```

### Option 3: VPS Deployment (DigitalOcean, Linode, etc.)

1. **Provision VPS**
   - Minimum: 2GB RAM, 1 CPU, 25GB SSD
   - Recommended: 4GB RAM, 2 CPU, 50GB SSD

2. **Install Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

3. **Clone and Deploy**
```bash
git clone https://github.com/Iteksmart/iTechSmart.git
cd iTechSmart/license-server
cp .env.example .env
nano .env  # Configure environment
docker compose up -d
```

4. **Set Up Nginx Reverse Proxy**
```nginx
server {
    listen 80;
    server_name licenses.yourdomain.com;

    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

5. **Install SSL Certificate**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d licenses.yourdomain.com
```

## Post-Deployment Configuration

### 1. Set Up Monitoring

#### Health Check Endpoint
```bash
curl https://licenses.yourdomain.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-11-16T16:30:00.000Z",
  "uptime": 3600,
  "database": "connected"
}
```

#### Set Up Uptime Monitoring
- Use services like UptimeRobot, Pingdom, or StatusCake
- Monitor: https://licenses.yourdomain.com/health
- Alert on: Response time > 5s, Status code != 200

### 2. Configure Backups

#### Database Backups (PostgreSQL)
```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
docker compose exec -T postgres pg_dump -U postgres itechsmart_licenses > "$BACKUP_DIR/backup_$DATE.sql"

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /path/to/backup-script.sh
```

### 3. Set Up Logging

#### Configure Log Rotation
```bash
# /etc/logrotate.d/itechsmart-license-server
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    missingok
    delaycompress
    copytruncate
}
```

#### View Logs
```bash
# Real-time logs
docker compose logs -f license-server

# Last 100 lines
docker compose logs --tail=100 license-server

# Logs from specific time
docker compose logs --since 2024-11-16T10:00:00 license-server
```

### 4. Security Hardening

#### Firewall Configuration
```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

#### Update Environment Variables
- Change default passwords
- Use strong JWT secret (32+ characters)
- Restrict CORS_ORIGIN to your domain
- Enable rate limiting

#### Database Security
```bash
# Change PostgreSQL password
docker compose exec postgres psql -U postgres -c "ALTER USER postgres PASSWORD 'new_strong_password';"

# Update DATABASE_URL in .env
nano .env
docker compose restart license-server
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new organization
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/refresh` - Refresh JWT token

### License Management
- `POST /api/licenses` - Create new license
- `GET /api/licenses/:id` - Get license details
- `POST /api/licenses/validate` - Validate license key
- `PUT /api/licenses/:id` - Update license
- `DELETE /api/licenses/:id` - Revoke license

### Organization Management
- `GET /api/organizations/:id` - Get organization details
- `PUT /api/organizations/:id` - Update organization
- `GET /api/organizations/:id/licenses` - List organization licenses

### Usage Tracking
- `POST /api/usage` - Record usage event
- `GET /api/usage/:licenseId` - Get usage statistics

### Webhooks
- `POST /api/webhooks` - Create webhook
- `GET /api/webhooks` - List webhooks
- `DELETE /api/webhooks/:id` - Delete webhook

## Testing the Deployment

### 1. Create Test Organization
```bash
curl -X POST https://licenses.yourdomain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Company",
    "domain": "testcompany.com",
    "email": "admin@testcompany.com",
    "password": "TestPassword123!"
  }'
```

### 2. Login and Get Token
```bash
curl -X POST https://licenses.yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@testcompany.com",
    "password": "TestPassword123!"
  }'
```

### 3. Create License
```bash
curl -X POST https://licenses.yourdomain.com/api/licenses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "tier": "PROFESSIONAL",
    "maxUsers": 10,
    "maxProducts": 5,
    "expiresAt": "2025-12-31T23:59:59Z"
  }'
```

### 4. Validate License
```bash
curl -X POST https://licenses.yourdomain.com/api/licenses/validate \
  -H "Content-Type: application/json" \
  -d '{
    "licenseKey": "YOUR_LICENSE_KEY",
    "productId": "itechsmart-analytics",
    "machineId": "test-machine-123"
  }'
```

## Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker compose ps postgres

# Check PostgreSQL logs
docker compose logs postgres

# Test database connection
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c "SELECT 1;"
```

### License Server Not Starting
```bash
# Check logs
docker compose logs license-server

# Verify environment variables
docker compose exec license-server env | grep DATABASE_URL

# Restart service
docker compose restart license-server
```

### Migration Issues
```bash
# Check migration status
docker compose exec license-server npx prisma migrate status

# Reset database (CAUTION: This deletes all data)
docker compose exec license-server npx prisma migrate reset

# Apply migrations manually
docker compose exec license-server npx prisma migrate deploy
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Check database performance
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c "
  SELECT pid, usename, application_name, state, query 
  FROM pg_stat_activity 
  WHERE state != 'idle';
"

# Optimize database
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c "VACUUM ANALYZE;"
```

## Scaling Considerations

### Horizontal Scaling
- Deploy multiple license-server instances behind a load balancer
- Use managed PostgreSQL service (AWS RDS, GCP Cloud SQL, Azure Database)
- Implement Redis for session management and caching

### Vertical Scaling
- Increase container resources in docker-compose.yml:
```yaml
license-server:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
      reservations:
        cpus: '1'
        memory: 2G
```

### Database Optimization
- Add indexes for frequently queried fields
- Enable connection pooling
- Use read replicas for analytics queries

## Maintenance

### Regular Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker compose build
docker compose up -d

# Run migrations
docker compose exec license-server npx prisma migrate deploy
```

### Database Maintenance
```bash
# Vacuum and analyze
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c "VACUUM ANALYZE;"

# Check database size
docker compose exec postgres psql -U postgres -d itechsmart_licenses -c "
  SELECT pg_size_pretty(pg_database_size('itechsmart_licenses'));
"
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/Iteksmart/iTechSmart/issues
- Email: support@itechsmart.com
- Documentation: https://docs.itechsmart.com

## License

MIT License - See LICENSE file for details