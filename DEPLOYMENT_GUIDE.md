# iTechSmart Suite - Deployment Guide
## Version 2.0 - Feature Enhancements

**Document Version:** 2.0  
**Release Date:** August 8, 2025  
**Company:** iTechSmart Inc.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Deployment Options](#deployment-options)
5. [Docker Deployment](#docker-deployment)
6. [Kubernetes Deployment](#kubernetes-deployment)
7. [Database Setup](#database-setup)
8. [Configuration](#configuration)
9. [Post-Deployment](#post-deployment)
10. [Monitoring](#monitoring)
11. [Troubleshooting](#troubleshooting)
12. [Rollback Procedures](#rollback-procedures)

---

## Overview

This guide covers the deployment of iTechSmart Suite Version 2.0, which includes 5 major enhancements:

1. **Compliance Center** (Product #19) - Multi-framework compliance management
2. **Service Catalog** (Product #1) - Self-service IT portal
3. **Automation Orchestrator** (Product #23) - Workflow automation
4. **Observatory** (Product #36) - APM and observability
5. **AI Insights** (Product #3) - AI/ML analytics

### What's New in Version 2.0

- **150+ new API endpoints**
- **50+ new database models**
- **5 new frontend applications**
- **20+ integration points**
- **100+ new features**

### Deployment Scope

- **Products Updated:** 5 products
- **New Services:** 5 services
- **Database Changes:** 50+ new tables
- **Configuration Updates:** Required
- **Downtime:** ~30 minutes (with proper planning)

---

## Prerequisites

### System Requirements

#### Hardware Requirements (Per Service)
```
Minimum:
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB
- Network: 1Gbps

Recommended:
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB SSD
- Network: 10Gbps
```

#### Software Requirements
```
- Docker: 24.0+
- Docker Compose: 2.20+
- PostgreSQL: 14+
- Redis: 7+
- Node.js: 20+ (for frontend builds)
- Python: 3.11+
```

### Network Requirements

#### Ports Required
```
Product #1 (Enterprise):        8002 (backend), 3002 (frontend)
Product #3 (Analytics):         8003 (backend), 3003 (frontend)
Product #19 (Compliance):       8019 (backend), 3019 (frontend)
Product #23 (Workflow):         8023 (backend), 3023 (frontend)
Product #36 (Observatory):      8036 (backend), 3036 (frontend)

Supporting Services:
- PostgreSQL: 5432
- Redis: 6379
- Hub: 8001
```

---

## Docker Deployment

### Complete Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # Database
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: itechsmart
      POSTGRES_USER: itechsmart
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U itechsmart"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Hub (Central coordination)
  hub:
    image: itechsmart/hub:2.0
    environment:
      - DATABASE_URL=postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@postgres:5432/${DATABASE_NAME}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    ports:
      - "8001:8001"
    depends_on:
      - postgres
      - redis

  # Compliance Center
  compliance:
    image: itechsmart/compliance:2.0
    environment:
      - DATABASE_URL=postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@postgres:5432/${DATABASE_NAME}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/1
      - HUB_URL=http://hub:8001
      - SECRET_KEY=${SECRET_KEY}
    ports:
      - "8019:8019"
      - "3019:3019"
    depends_on:
      - postgres
      - redis
      - hub

  # Service Catalog (Enterprise)
  enterprise:
    image: itechsmart/enterprise:2.0
    environment:
      - DATABASE_URL=postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@postgres:5432/${DATABASE_NAME}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/2
      - HUB_URL=http://hub:8001
      - SECRET_KEY=${SECRET_KEY}
    ports:
      - "8002:8002"
      - "3002:3002"
    depends_on:
      - postgres
      - redis
      - hub

  # Automation Orchestrator (Workflow)
  workflow:
    image: itechsmart/workflow:2.0
    environment:
      - DATABASE_URL=postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@postgres:5432/${DATABASE_NAME}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/3
      - HUB_URL=http://hub:8001
      - SECRET_KEY=${SECRET_KEY}
    ports:
      - "8023:8023"
      - "3023:3023"
    depends_on:
      - postgres
      - redis
      - hub

  # Observatory
  observatory:
    image: itechsmart/observatory:2.0
    environment:
      - DATABASE_URL=postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@postgres:5432/${DATABASE_NAME}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/4
      - HUB_URL=http://hub:8001
      - SECRET_KEY=${SECRET_KEY}
    ports:
      - "8036:8036"
      - "3036:3036"
    depends_on:
      - postgres
      - redis
      - hub

  # AI Insights (Analytics)
  analytics:
    image: itechsmart/analytics:2.0
    environment:
      - DATABASE_URL=postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@postgres:5432/${DATABASE_NAME}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/5
      - HUB_URL=http://hub:8001
      - SECRET_KEY=${SECRET_KEY}
    ports:
      - "8003:8003"
      - "3003:3003"
    depends_on:
      - postgres
      - redis
      - hub

volumes:
  postgres_data:
  redis_data:
```

### Deploy Services

```bash
# Pull images
docker-compose pull

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

---

## Database Setup

### Run Migrations

```bash
# Compliance Center
docker-compose exec compliance python -m alembic upgrade head

# Service Catalog
docker-compose exec enterprise python -m alembic upgrade head

# Automation Orchestrator
docker-compose exec workflow python -m alembic upgrade head

# Observatory
docker-compose exec observatory python -m alembic upgrade head

# AI Insights
docker-compose exec analytics python -m alembic upgrade head
```

---

## Post-Deployment

### Verify Services

```bash
# Check health endpoints
curl http://localhost:8001/health  # Hub
curl http://localhost:8019/health  # Compliance
curl http://localhost:8002/health  # Enterprise
curl http://localhost:8023/health  # Workflow
curl http://localhost:8036/health  # Observatory
curl http://localhost:8003/health  # Analytics
```

---

## Troubleshooting

### Common Issues

#### Service won't start
```bash
# Check logs
docker-compose logs <service-name>

# Verify database connection
docker-compose exec <service-name> python -c "from database import engine; engine.connect()"
```

#### Database connection errors
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check credentials
docker-compose exec postgres psql -U itechsmart -d itechsmart
```

---

## Rollback Procedures

### Docker Compose Rollback

```bash
# Stop current version
docker-compose down

# Restore previous version
docker-compose -f docker-compose.v1.yml up -d

# Restore database backup
docker-compose exec postgres psql -U itechsmart -d itechsmart < backup.sql
```

---

## Support

### Contact
- **Company:** iTechSmart Inc.
- **Website:** https://itechsmart.dev
- **Email:** support@itechsmart.dev
- **Phone:** 310-251-3969

---

**© 2025 iTechSmart Inc. All rights reserved.**