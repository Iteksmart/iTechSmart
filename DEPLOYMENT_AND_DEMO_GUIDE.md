# 🚀 iTechSmart Suite - Complete Deployment & Demo Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Individual Product Deployment](#individual-product-deployment)
3. [Individual Product Demos](#individual-product-demos)
4. [Full Suite Deployment](#full-suite-deployment)
5. [Full Suite Demo](#full-suite-demo)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- Docker Desktop (latest version)
- Docker Compose v2.0+
- Git
- Web browser (Chrome/Firefox recommended)

### System Requirements
- **RAM**: Minimum 8GB (16GB recommended for full suite)
- **Storage**: 50GB free space
- **CPU**: 4+ cores recommended
- **OS**: Windows 10+, macOS 10.15+, or Linux

### GitHub Access
```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Or use personal access token
docker login ghcr.io
Username: your-github-username
Password: your-personal-access-token
```

---

## Individual Product Deployment

### Step 1: Choose a Product

Available products (35 total):
- iTechSmart Enterprise, Ninja, Analytics, Supreme Plus, HL7
- ProofLink, PassPort, ImpactOS, LegalAI Pro
- iTechSmart DataFlow, Pulse, Connect, Vault, Notify
- iTechSmart Ledger, Copilot, Shield, Workflow, Marketplace
- iTechSmart Cloud, DevOps, Mobile, AI, Compliance
- iTechSmart Data Platform, Customer Success, Port Manager
- iTechSmart MDM Agent, QA/QC, Think-Tank, Sentinel
- iTechSmart Forge, Sandbox, Citadel, Observatory

### Step 2: Pull Docker Images

```bash
# Replace {product} with actual product name (e.g., itechsmart-ninja)
docker pull ghcr.io/iteksmart/{product}-backend:main
docker pull ghcr.io/iteksmart/{product}-frontend:main
```

**Example for iTechSmart Ninja:**
```bash
docker pull ghcr.io/iteksmart/itechsmart-ninja-backend:main
docker pull ghcr.io/iteksmart/itechsmart-ninja-frontend:main
```

### Step 3: Create Environment File

Create `.env` file:
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
POSTGRES_USER=itechsmart
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=itechsmart_db

# Backend Configuration
BACKEND_PORT=8000
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Frontend Configuration
FRONTEND_PORT=3000
VITE_API_URL=http://localhost:8000
REACT_APP_API_URL=http://localhost:8000

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379
```

### Step 4: Create Docker Compose File

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  # Database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend
  backend:
    image: ghcr.io/iteksmart/{product}-backend:main
    environment:
      DATABASE_URL: ${DATABASE_URL}
      SECRET_KEY: ${SECRET_KEY}
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "${BACKEND_PORT}:8000"
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend
  frontend:
    image: ghcr.io/iteksmart/{product}-frontend:main
    environment:
      VITE_API_URL: http://localhost:${BACKEND_PORT}
      REACT_APP_API_URL: http://localhost:${BACKEND_PORT}
    ports:
      - "${FRONTEND_PORT}:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Step 5: Deploy the Product

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Step 6: Verify Deployment

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# View all running containers
docker ps
```

### Step 7: Access the Application

Open your browser:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Individual Product Demos

### Demo Template for Each Product

#### 1. iTechSmart Ninja - AI Agent Demo

**Access**: http://localhost:3000

**Demo Steps**:
1. **Login/Register**
   - Navigate to login page
   - Create account or use demo credentials
   - Verify authentication works

2. **Dashboard Overview**
   - View main dashboard
   - Check all widgets load correctly
   - Verify data displays properly

3. **Core Features**
   - Test AI chat functionality
   - Create a new task/project
   - Run AI analysis
   - View results and insights

4. **Settings & Configuration**
   - Update user profile
   - Configure AI settings
   - Test integrations

5. **Export/Reports**
   - Generate a report
   - Export data
   - Verify downloads work

**Expected Results**:
- ✅ All pages load without errors
- ✅ AI responses are generated
- ✅ Data persists correctly
- ✅ UI is responsive

#### 2. ProofLink - Document Verification Demo

**Access**: http://localhost:3000

**Demo Steps**:
1. **Upload Document**
   - Click "Upload" button
   - Select a test document
   - Verify upload progress

2. **Verification Process**
   - Start verification
   - Monitor progress
   - View verification results

3. **Blockchain Recording**
   - Check blockchain hash
   - Verify timestamp
   - View transaction details

4. **Share Proof**
   - Generate shareable link
   - Test link access
   - Verify proof validity

**Expected Results**:
- ✅ Documents upload successfully
- ✅ Verification completes
- ✅ Blockchain hash generated
- ✅ Proof links work

#### 3. PassPort - Identity Management Demo

**Access**: http://localhost:3000

**Demo Steps**:
1. **Create Identity**
   - Fill identity form
   - Upload documents
   - Submit for verification

2. **Identity Verification**
   - Check verification status
   - View verification steps
   - Complete KYC process

3. **Access Management**
   - Grant access permissions
   - Revoke access
   - View access logs

4. **Identity Sharing**
   - Generate QR code
   - Share identity proof
   - Verify shared identity

**Expected Results**:
- ✅ Identity created successfully
- ✅ Verification process works
- ✅ Access controls function
- ✅ QR codes generate

### Demo Checklist for All Products

For each product, verify:
- [ ] Application loads without errors
- [ ] Authentication works (login/logout)
- [ ] Main dashboard displays correctly
- [ ] Core features are functional
- [ ] Data persists across sessions
- [ ] API endpoints respond correctly
- [ ] UI is responsive on different screen sizes
- [ ] No console errors in browser
- [ ] Health checks pass
- [ ] Database connections work

---

## Full Suite Deployment

### Step 1: Clone Repository

```bash
git clone https://github.com/Iteksmart/iTechSmart.git
cd iTechSmart
```

### Step 2: Create Master Environment File

Create `.env.suite`:
```bash
# Global Configuration
COMPOSE_PROJECT_NAME=itechsmart-suite

# Database Configuration
POSTGRES_USER=itechsmart
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=itechsmart_suite

# Redis Configuration
REDIS_PASSWORD=redis_password_here

# Shared Secrets
JWT_SECRET=your-jwt-secret-here
ENCRYPTION_KEY=your-encryption-key-here

# Port Ranges
BACKEND_PORT_START=8000
FRONTEND_PORT_START=3000

# Resource Limits
MEMORY_LIMIT=512m
CPU_LIMIT=1
```

### Step 3: Create Full Suite Docker Compose

Create `docker-compose.suite.yml`:
```yaml
version: '3.8'

services:
  # Shared Services
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Product 1: iTechSmart Ninja
  ninja-backend:
    image: ghcr.io/iteksmart/itechsmart-ninja-backend:main
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8001:8000"
    depends_on:
      postgres:
        condition: service_healthy
    deploy:
      resources:
        limits:
          memory: ${MEMORY_LIMIT}
          cpus: '${CPU_LIMIT}'

  ninja-frontend:
    image: ghcr.io/iteksmart/itechsmart-ninja-frontend:main
    environment:
      VITE_API_URL: http://localhost:8001
    ports:
      - "3001:80"
    depends_on:
      - ninja-backend

  # Product 2: ProofLink
  prooflink-backend:
    image: ghcr.io/iteksmart/prooflink-backend:main
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8002:8000"
    depends_on:
      postgres:
        condition: service_healthy

  prooflink-frontend:
    image: ghcr.io/iteksmart/prooflink-frontend:main
    environment:
      VITE_API_URL: http://localhost:8002
    ports:
      - "3002:80"
    depends_on:
      - prooflink-backend

  # Product 3: PassPort
  passport-backend:
    image: ghcr.io/iteksmart/passport-backend:main
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8003:8000"
    depends_on:
      postgres:
        condition: service_healthy

  passport-frontend:
    image: ghcr.io/iteksmart/passport-frontend:main
    environment:
      VITE_API_URL: http://localhost:8003
    ports:
      - "3003:80"
    depends_on:
      - passport-backend

  # Add remaining 32 products following the same pattern...
  # Each product gets unique ports (8004-8035 for backends, 3004-3035 for frontends)

  # Nginx Reverse Proxy (Optional)
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - ninja-frontend
      - prooflink-frontend
      - passport-frontend

volumes:
  postgres_data:
  redis_data:
```

### Step 4: Create Nginx Configuration

Create `nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream ninja {
        server ninja-frontend:80;
    }

    upstream prooflink {
        server prooflink-frontend:80;
    }

    upstream passport {
        server passport-frontend:80;
    }

    server {
        listen 80;
        server_name localhost;

        location /ninja {
            proxy_pass http://ninja;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /prooflink {
            proxy_pass http://prooflink;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /passport {
            proxy_pass http://passport;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # Add routes for remaining products...
    }
}
```

### Step 5: Deploy Full Suite

```bash
# Load environment variables
source .env.suite

# Pull all images (this may take 10-15 minutes)
docker-compose -f docker-compose.suite.yml pull

# Start all services
docker-compose -f docker-compose.suite.yml up -d

# Check status
docker-compose -f docker-compose.suite.yml ps

# View logs
docker-compose -f docker-compose.suite.yml logs -f

# Scale specific services if needed
docker-compose -f docker-compose.suite.yml up -d --scale ninja-backend=3
```

### Step 6: Verify Full Suite

```bash
# Check all services are running
docker ps | grep itechsmart

# Test health endpoints
for port in {8001..8035}; do
  echo "Testing port $port..."
  curl -f http://localhost:$port/health || echo "Port $port failed"
done

# Check resource usage
docker stats

# View network
docker network ls
docker network inspect itechsmart-suite_default
```

---

## Full Suite Demo

### Suite Dashboard Access

**Main Entry Point**: http://localhost

**Individual Product Access**:
- iTechSmart Ninja: http://localhost/ninja or http://localhost:3001
- ProofLink: http://localhost/prooflink or http://localhost:3002
- PassPort: http://localhost/passport or http://localhost:3003
- [Continue for all 35 products...]

### Comprehensive Demo Flow

#### Phase 1: Suite Overview (10 minutes)

1. **Access Main Dashboard**
   ```bash
   open http://localhost
   ```

2. **View All Products**
   - Navigate to product catalog
   - See all 35 products listed
   - Check status indicators (all should be green)

3. **System Health Check**
   - View system metrics
   - Check resource usage
   - Verify all services running

#### Phase 2: Individual Product Demos (5 minutes each)

For each of the 35 products:

1. **Navigate to Product**
   - Click product tile
   - Verify page loads

2. **Quick Feature Test**
   - Login/authentication
   - Main dashboard view
   - One core feature test
   - Logout

3. **Move to Next Product**

**Total Time**: ~3 hours for all 35 products

#### Phase 3: Integration Demo (15 minutes)

1. **Cross-Product Integration**
   - Create user in PassPort
   - Use same credentials in iTechSmart Ninja
   - Verify SSO works across products

2. **Data Flow**
   - Create data in one product
   - Access from another product
   - Verify data consistency

3. **API Integration**
   - Test API calls between products
   - Verify webhooks work
   - Check event streaming

#### Phase 4: Performance Demo (10 minutes)

1. **Load Testing**
   ```bash
   # Install Apache Bench
   apt-get install apache2-utils

   # Test each product
   ab -n 1000 -c 10 http://localhost:3001/
   ```

2. **Resource Monitoring**
   ```bash
   # Monitor in real-time
   docker stats

   # Check logs
   docker-compose -f docker-compose.suite.yml logs --tail=100
   ```

3. **Scaling Demo**
   ```bash
   # Scale up
   docker-compose -f docker-compose.suite.yml up -d --scale ninja-backend=5

   # Verify load balancing
   for i in {1..10}; do curl http://localhost:8001/health; done
   ```

### Demo Checklist

#### Pre-Demo Setup
- [ ] All Docker images pulled
- [ ] Environment variables configured
- [ ] Database initialized
- [ ] All services started
- [ ] Health checks passing
- [ ] Test data loaded

#### During Demo
- [ ] Main dashboard accessible
- [ ] All 35 products load correctly
- [ ] Authentication works
- [ ] Core features functional
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] Integrations work

#### Post-Demo
- [ ] Collect feedback
- [ ] Document issues
- [ ] Export demo data
- [ ] Clean up resources

---

## Troubleshooting

### Common Issues

#### Issue 1: Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in .env file
BACKEND_PORT=8100
```

#### Issue 2: Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### Issue 3: Out of Memory
```bash
# Check memory usage
docker stats

# Increase Docker memory limit
# Docker Desktop > Settings > Resources > Memory

# Or reduce number of running services
docker-compose stop <service-name>
```

#### Issue 4: Image Pull Failed
```bash
# Re-authenticate
docker login ghcr.io

# Pull specific image
docker pull ghcr.io/iteksmart/{product}-backend:main

# Check image exists
docker images | grep itechsmart
```

#### Issue 5: Frontend Not Loading
```bash
# Check backend is running
curl http://localhost:8000/health

# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --force-recreate frontend
```

### Debug Commands

```bash
# View all logs
docker-compose logs

# Follow specific service logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend bash

# Check container details
docker inspect <container-id>

# View network details
docker network inspect <network-name>

# Check disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

### Performance Optimization

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Use layer caching
docker-compose build --parallel

# Limit resources per container
docker-compose up -d --scale backend=2 --memory="512m" --cpus="1"

# Monitor performance
docker stats --no-stream
```

---

## Quick Reference

### Port Mapping
```
Shared Services:
- PostgreSQL: 5432
- Redis: 6379
- Nginx: 80, 443

Products (Backend: 8001-8035, Frontend: 3001-3035):
- iTechSmart Ninja: 8001, 3001
- ProofLink: 8002, 3002
- PassPort: 8003, 3003
- [Continue for all 35 products...]
```

### Useful Commands
```bash
# Start suite
docker-compose -f docker-compose.suite.yml up -d

# Stop suite
docker-compose -f docker-compose.suite.yml down

# View status
docker-compose -f docker-compose.suite.yml ps

# View logs
docker-compose -f docker-compose.suite.yml logs -f

# Restart service
docker-compose -f docker-compose.suite.yml restart <service>

# Scale service
docker-compose -f docker-compose.suite.yml up -d --scale backend=3

# Update images
docker-compose -f docker-compose.suite.yml pull
docker-compose -f docker-compose.suite.yml up -d
```

---

## Next Steps

1. **Production Deployment**
   - Set up Kubernetes cluster
   - Configure load balancers
   - Set up monitoring (Prometheus/Grafana)
   - Configure logging (ELK stack)

2. **Security Hardening**
   - Enable HTTPS
   - Configure firewalls
   - Set up secrets management
   - Enable audit logging

3. **Backup & Recovery**
   - Set up automated backups
   - Test restore procedures
   - Configure disaster recovery

4. **Monitoring & Alerting**
   - Set up health checks
   - Configure alerts
   - Create dashboards
   - Set up log aggregation

---

**Last Updated**: 2025-11-16  
**Version**: 1.0.0  
**Status**: Production Ready ✅