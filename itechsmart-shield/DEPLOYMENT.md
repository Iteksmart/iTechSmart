# iTechSmart Shield - Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Monitoring Setup](#monitoring-setup)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB minimum
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2

### Software Requirements
- Docker 24.0+
- Docker Compose 2.20+
- Git
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

## Local Development

### 1. Clone Repository
```bash
git clone <repository-url>
cd itechsmart-shield
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://shield_user:shield_pass_2024@localhost:5432/shield_db
REDIS_URL=redis://localhost:6379
ELASTICSEARCH_URL=http://localhost:9200
SECRET_KEY=$(openssl rand -hex 32)
ENVIRONMENT=development
EOF

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
REACT_APP_API_URL=http://localhost:8000
EOF

# Start development server
npm start
```

### 4. Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Docker Deployment

### Quick Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Service Health Checks

```bash
# Check service status
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check database connection
docker exec shield-postgres pg_isready -U shield_user

# Check Redis
docker exec shield-redis redis-cli ping

# Check Elasticsearch
curl http://localhost:9200/_cluster/health
```

### Database Management

```bash
# Access PostgreSQL
docker exec -it shield-postgres psql -U shield_user -d shield_db

# Run SQL script
docker exec -i shield-postgres psql -U shield_user -d shield_db < script.sql

# Backup database
docker exec shield-postgres pg_dump -U shield_user shield_db > backup_$(date +%Y%m%d).sql

# Restore database
docker exec -i shield-postgres psql -U shield_user shield_db < backup.sql
```

## Production Deployment

### 1. Environment Configuration

Create production environment file:
```bash
cat > .env.production << EOF
# Database
DATABASE_URL=postgresql://shield_user:STRONG_PASSWORD@postgres:5432/shield_db
REDIS_URL=redis://:REDIS_PASSWORD@redis:6379
ELASTICSEARCH_URL=http://elasticsearch:9200

# Security
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
ENVIRONMENT=production

# CORS
ALLOWED_ORIGINS=https://shield.yourdomain.com

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Monitoring
SENTRY_DSN=your-sentry-dsn
EOF
```

### 2. SSL/TLS Configuration

```bash
# Generate SSL certificates (Let's Encrypt)
certbot certonly --standalone -d shield.yourdomain.com

# Or use existing certificates
cp /path/to/cert.pem ./ssl/
cp /path/to/key.pem ./ssl/
```

### 3. Production Docker Compose

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: shield_db
      POSTGRES_USER: shield_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: always

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    restart: always

volumes:
  postgres_data:
  redis_data:
```

### 4. Deploy to Production

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose -f docker-compose.prod.yml ps
```

## Cloud Deployment

### AWS Deployment

#### Using ECS (Elastic Container Service)

1. **Push images to ECR**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push images
docker tag shield-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/shield-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/shield-backend:latest
```

2. **Create ECS Task Definition**
```json
{
  "family": "shield-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/shield-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://..."
        }
      ]
    }
  ]
}
```

3. **Create ECS Service**
```bash
aws ecs create-service \
  --cluster shield-cluster \
  --service-name shield-backend \
  --task-definition shield-backend \
  --desired-count 2 \
  --launch-type FARGATE
```

### Google Cloud Platform (GCP)

#### Using Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/shield-backend

# Deploy to Cloud Run
gcloud run deploy shield-backend \
  --image gcr.io/PROJECT_ID/shield-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Deployment

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name shield-rg --location eastus

# Create container
az container create \
  --resource-group shield-rg \
  --name shield-backend \
  --image shield-backend:latest \
  --dns-name-label shield-backend \
  --ports 8000
```

## Monitoring Setup

### 1. Prometheus Configuration

Create `prometheus.yml`:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'shield-backend'
    static_configs:
      - targets: ['backend:8000']
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### 2. Grafana Setup

```bash
# Start Grafana
docker run -d \
  --name=grafana \
  -p 3001:3000 \
  -e "GF_SECURITY_ADMIN_PASSWORD=admin" \
  grafana/grafana

# Access Grafana at http://localhost:3001
# Default credentials: admin/admin
```

### 3. Log Aggregation

```bash
# Start ELK Stack
docker-compose -f docker-compose.elk.yml up -d

# Access Kibana at http://localhost:5601
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Test connection
docker exec shield-postgres pg_isready -U shield_user
```

#### 2. Backend Not Starting
```bash
# Check logs
docker-compose logs backend

# Verify environment variables
docker-compose exec backend env | grep DATABASE_URL

# Restart service
docker-compose restart backend
```

#### 3. Frontend Build Errors
```bash
# Clear cache
cd frontend
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

#### 4. Port Already in Use
```bash
# Find process using port
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Create indexes
CREATE INDEX idx_threats_severity ON threats(severity);
CREATE INDEX idx_threats_status ON threats(status);

-- Analyze tables
ANALYZE threats;
ANALYZE vulnerabilities;
```

#### 2. Redis Caching
```python
# Enable caching in backend
CACHE_TTL = 300  # 5 minutes
redis_client.setex(f"threats:{id}", CACHE_TTL, json.dumps(threat))
```

#### 3. Frontend Optimization
```bash
# Build optimized production bundle
npm run build

# Analyze bundle size
npm run analyze
```

### Backup Strategy

#### Automated Backups
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec shield-postgres pg_dump -U shield_user shield_db > backup_$DATE.sql
gzip backup_$DATE.sql
# Upload to S3
aws s3 cp backup_$DATE.sql.gz s3://shield-backups/
EOF

chmod +x backup.sh

# Add to crontab (daily at 2 AM)
0 2 * * * /path/to/backup.sh
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Enable SSL/TLS
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable audit logging
- [ ] Configure backup strategy
- [ ] Set up monitoring alerts
- [ ] Review security headers
- [ ] Enable CORS properly
- [ ] Implement API authentication

## Support

For deployment issues:
- Email: devops@itechsmart.dev
- Slack: #shield-deployment
- Documentation: https://docs.itechsmart.dev/shield/deployment

---

**Last Updated**: January 2024  
**Version**: 1.0.0