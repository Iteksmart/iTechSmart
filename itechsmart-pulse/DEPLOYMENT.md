# iTechSmart Pulse - Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [Running Services](#running-services)
6. [Production Deployment](#production-deployment)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **RAM**: Minimum 8GB, Recommended 16GB+
- **Storage**: Minimum 20GB free space
- **CPU**: 4+ cores recommended

### Required Software
- Docker 24.0+ and Docker Compose 2.0+
- Git 2.30+
- Node.js 20.x (for frontend development)
- Python 3.11+ (for backend development)

### Installation

#### Docker & Docker Compose
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Node.js
```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20
```

#### Python
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

---

## Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd itechsmart-pulse
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit configuration (see Configuration section)
nano .env
```

### 3. Start All Services
```bash
# Build and start all containers
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Access Applications
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672
- **MinIO Console**: http://localhost:9001
- **ClickHouse**: http://localhost:8123

### 5. Default Credentials
```
Admin User:
  Email: admin@itechsmart.dev
  Password: password

Analyst User:
  Email: analyst@itechsmart.dev
  Password: password

Viewer User:
  Email: viewer@itechsmart.dev
  Password: password

RabbitMQ:
  Username: pulse_user
  Password: pulse_password

MinIO:
  Access Key: pulse_user
  Secret Key: pulse_password
```

---

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database - PostgreSQL
DATABASE_URL=postgresql://pulse_user:pulse_password@postgres:5432/pulse
POSTGRES_DB=pulse
POSTGRES_USER=pulse_user
POSTGRES_PASSWORD=pulse_password

# ClickHouse (Analytics)
CLICKHOUSE_HOST=clickhouse
CLICKHOUSE_PORT=9000
CLICKHOUSE_USER=pulse_user
CLICKHOUSE_PASSWORD=pulse_password
CLICKHOUSE_DATABASE=analytics

# Redis (Cache)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=pulse_password

# RabbitMQ (Message Queue)
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=pulse_user
RABBITMQ_PASSWORD=pulse_password

# MinIO (Object Storage)
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=pulse_user
MINIO_SECRET_KEY=pulse_password
MINIO_SECURE=false

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### Security Configuration (Production)

For production deployments, ensure:

1. **Strong Secret Key**: Generate using:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Strong Passwords**: Change all default passwords
3. **CORS Origins**: Restrict to your domain
4. **SSL/TLS**: Enable HTTPS
5. **Firewall**: Configure appropriate rules

---

## Database Setup

### Automatic Initialization

The PostgreSQL database is automatically initialized with:
- 15 tables with proper indexes
- Sample data (3 users, 5 data sources, etc.)
- Triggers for timestamp updates
- Views for analytics

### Manual Database Operations

#### Connect to PostgreSQL
```bash
docker-compose exec postgres psql -U pulse_user -d pulse
```

#### Backup Database
```bash
docker-compose exec postgres pg_dump -U pulse_user pulse > backup.sql
```

#### Restore Database
```bash
docker-compose exec -T postgres psql -U pulse_user pulse < backup.sql
```

#### Reset Database
```bash
docker-compose down -v
docker-compose up -d
```

### ClickHouse Setup

ClickHouse is automatically initialized with:
- 8 analytics tables
- 3 materialized views for aggregations
- Sample event data

#### Connect to ClickHouse
```bash
docker-compose exec clickhouse clickhouse-client
```

---

## Running Services

### Development Mode

#### Start All Services
```bash
docker-compose up -d
```

#### Start Specific Service
```bash
docker-compose up -d postgres redis
```

#### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

#### Restart Service
```bash
docker-compose restart backend
```

#### Stop All Services
```bash
docker-compose down
```

#### Stop and Remove Volumes
```bash
docker-compose down -v
```

### Backend Development

#### Run Backend Locally (without Docker)
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Run Tests
```bash
cd backend
pytest
pytest --cov=. --cov-report=html
```

### Frontend Development

#### Run Frontend Locally (without Docker)
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

#### Run Tests
```bash
cd frontend
npm test
npm run test:coverage
```

---

## Production Deployment

### Docker Compose Production

1. **Update docker-compose.prod.yml**:
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      ENVIRONMENT: production
      DEBUG: "false"
    restart: always
    
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    restart: always
```

2. **Deploy**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

1. **Create Kubernetes manifests** (see `k8s/` directory)
2. **Deploy**:
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml
```

### Cloud Deployment

#### AWS ECS
```bash
# Build and push images
docker build -t pulse-backend:latest ./backend
docker tag pulse-backend:latest <ecr-repo>/pulse-backend:latest
docker push <ecr-repo>/pulse-backend:latest

# Deploy using ECS CLI or CloudFormation
```

#### Google Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/<project-id>/pulse-backend
gcloud run deploy pulse-backend --image gcr.io/<project-id>/pulse-backend
```

#### Azure Container Instances
```bash
# Build and push
az acr build --registry <registry-name> --image pulse-backend:latest ./backend

# Deploy
az container create --resource-group <rg> --name pulse-backend \
  --image <registry-name>.azurecr.io/pulse-backend:latest
```

### Reverse Proxy Setup (Nginx)

```nginx
server {
    listen 80;
    server_name pulse.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name pulse.yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/pulse.crt;
    ssl_certificate_key /etc/ssl/private/pulse.key;
    
    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready -U pulse_user

# Redis health
docker-compose exec redis redis-cli ping

# ClickHouse health
docker-compose exec clickhouse clickhouse-client --query "SELECT 1"
```

### Monitoring Tools

#### Prometheus Metrics
```bash
# Backend exposes metrics at /metrics
curl http://localhost:8000/metrics
```

#### Log Aggregation
```bash
# View aggregated logs
docker-compose logs -f --tail=100

# Export logs
docker-compose logs > logs.txt
```

### Backup Strategy

#### Automated Backups
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# PostgreSQL backup
docker-compose exec -T postgres pg_dump -U pulse_user pulse > "$BACKUP_DIR/postgres_$DATE.sql"

# ClickHouse backup
docker-compose exec -T clickhouse clickhouse-client --query "BACKUP DATABASE analytics TO Disk('backups', '$DATE')"

# Compress backups
tar -czf "$BACKUP_DIR/pulse_backup_$DATE.tar.gz" "$BACKUP_DIR"/*_$DATE.*

# Remove old backups (keep last 30 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

#### Restore from Backup
```bash
# PostgreSQL restore
docker-compose exec -T postgres psql -U pulse_user pulse < backup.sql

# ClickHouse restore
docker-compose exec clickhouse clickhouse-client --query "RESTORE DATABASE analytics FROM Disk('backups', 'backup_name')"
```

### Performance Tuning

#### PostgreSQL
```sql
-- Analyze tables
ANALYZE;

-- Vacuum tables
VACUUM ANALYZE;

-- Check slow queries
SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
```

#### ClickHouse
```sql
-- Optimize tables
OPTIMIZE TABLE analytics.events;

-- Check query performance
SELECT * FROM system.query_log ORDER BY query_duration_ms DESC LIMIT 10;
```

#### Redis
```bash
# Check memory usage
docker-compose exec redis redis-cli INFO memory

# Clear cache
docker-compose exec redis redis-cli FLUSHALL
```

---

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :8000
sudo netstat -tulpn | grep :8000

# Kill process
kill -9 <PID>
```

#### Container Won't Start
```bash
# Check logs
docker-compose logs <service-name>

# Rebuild container
docker-compose build --no-cache <service-name>
docker-compose up -d <service-name>
```

#### Database Connection Failed
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U pulse_user -d pulse -c "SELECT 1"

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### Out of Memory
```bash
# Check Docker memory
docker stats

# Increase Docker memory limit (Docker Desktop)
# Settings > Resources > Memory > Increase limit

# Clear unused resources
docker system prune -a
```

#### Frontend Build Fails
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Clear cache
npm cache clean --force
```

### Debug Mode

#### Enable Debug Logging
```bash
# Backend
export DEBUG=true
export LOG_LEVEL=DEBUG

# Frontend
export VITE_DEBUG=true
```

#### Access Container Shell
```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend sh

# PostgreSQL
docker-compose exec postgres bash
```

### Performance Issues

#### Slow Queries
```sql
-- PostgreSQL: Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();

-- View slow queries
SELECT * FROM pg_stat_statements 
WHERE mean_exec_time > 1000 
ORDER BY mean_exec_time DESC;
```

#### High Memory Usage
```bash
# Check container memory
docker stats

# Limit container memory
docker-compose up -d --scale backend=1 --memory="2g"
```

### Getting Help

- **Documentation**: Check README.md and API docs at /docs
- **Logs**: Always check logs first: `docker-compose logs -f`
- **GitHub Issues**: Report bugs and request features
- **Community**: Join our Slack/Discord channel
- **Support**: Email support@itechsmart.dev

---

## Appendix

### Useful Commands

```bash
# View all containers
docker-compose ps

# View resource usage
docker stats

# Clean up everything
docker-compose down -v
docker system prune -a

# Export/Import images
docker save pulse-backend:latest | gzip > pulse-backend.tar.gz
docker load < pulse-backend.tar.gz

# Database migrations
docker-compose exec backend alembic upgrade head
docker-compose exec backend alembic revision --autogenerate -m "description"

# Run specific tests
docker-compose exec backend pytest tests/test_api.py -v

# Check code quality
docker-compose exec backend black .
docker-compose exec backend flake8 .
docker-compose exec backend mypy .
```

### Port Reference

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 5173 | React development server |
| Backend | 8000 | FastAPI application |
| PostgreSQL | 5432 | Main database |
| ClickHouse | 9000, 8123 | Analytics database |
| Redis | 6379 | Cache server |
| RabbitMQ | 5672, 15672 | Message queue |
| MinIO | 9090, 9001 | Object storage |

### Directory Structure

```
itechsmart-pulse/
├── backend/              # Backend API
│   ├── main.py          # FastAPI application
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── database.py      # Database configuration
│   ├── init-db.sql      # Database initialization
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Backend container
├── frontend/            # Frontend application
│   ├── src/            # React source code
│   ├── public/         # Static assets
│   ├── package.json    # Node dependencies
│   └── Dockerfile      # Frontend container
├── clickhouse/         # ClickHouse configuration
│   └── init.sql        # ClickHouse initialization
├── docker-compose.yml  # Docker orchestration
├── .env               # Environment variables
├── README.md          # Project documentation
└── DEPLOYMENT.md      # This file
```

---

**Last Updated**: January 2024  
**Version**: 1.0.0  
**Maintainer**: iTechSmart Team