# Deployment Guide - v1.1.0

**Version**: 1.1.0  
**Release Date**: November 17, 2025  
**Status**: Production Ready ✅

---

## 📋 Overview

This guide provides step-by-step instructions for deploying iTechSmart Suite v1.1.0 with the new agent integration features.

---

## 🎯 Deployment Options

### Option 1: Docker Compose (Recommended)
Best for: Development, staging, and small-scale production deployments

### Option 2: Kubernetes
Best for: Large-scale production deployments with high availability

### Option 3: Standalone Services
Best for: Custom deployments and specific infrastructure requirements

---

## 🚀 Quick Start (Docker Compose)

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space

### Step 1: Clone Repository
```bash
git clone https://github.com/Iteksmart/iTechSmart.git
cd iTechSmart
git checkout v1.1.0
```

### Step 2: Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env
```

**Required Variables**:
```bash
# License Server
LICENSE_SERVER_URL=http://localhost:3000
LICENSE_SERVER_PORT=3000

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/itechsmart

# Redis
REDIS_URL=redis://redis:6379

# Security
JWT_SECRET=your-secret-key-change-in-production
```

### Step 3: Start Services
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 4: Verify Deployment
```bash
# Check License Server
curl http://localhost:3000/health

# Check Ninja
curl http://localhost:8001/health

# Check Enterprise
curl http://localhost:8002/health
```

### Step 5: Deploy Agents
```bash
# Download agent binary
wget https://github.com/Iteksmart/iTechSmart/releases/download/v1.1.0/itechsmart-agent-linux-amd64

# Make executable
chmod +x itechsmart-agent-linux-amd64

# Configure agent
cat > agent-config.yaml << EOF
server_url: http://localhost:3000
api_key: your-api-key
hostname: $(hostname)
collection_interval: 30s
EOF

# Start agent
./itechsmart-agent-linux-amd64 --config agent-config.yaml
```

---

## 🔧 Detailed Deployment Steps

### 1. License Server Deployment

The License Server is the central hub for agent management.

**Docker Compose**:
```yaml
services:
  license-server:
    image: itechsmart/license-server:1.1.0
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/license
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - postgres
      - redis
```

**Standalone**:
```bash
cd license-server
npm install
npm run build
npm start
```

**Verify**:
```bash
curl http://localhost:3000/health
# Expected: {"status":"healthy","version":"1.1.0"}
```

---

### 2. Tier 1 Products Deployment

Deploy products with full agent integration.

#### iTechSmart Ninja
```bash
cd itechsmart-ninja
docker-compose up -d
# Access: http://localhost:8001
```

#### iTechSmart Enterprise
```bash
cd itechsmart-enterprise
docker-compose up -d
# Access: http://localhost:8002
```

#### iTechSmart Supreme Plus
```bash
cd itechsmart-supreme-plus
docker-compose up -d
# Access: http://localhost:8005
```

#### iTechSmart Citadel
```bash
cd itechsmart-citadel
docker-compose up -d
# Access: http://localhost:8006
```

#### Desktop Launcher
```bash
# Download installer for your platform
# Windows: iTechSmart-Setup-1.1.0.exe
# macOS: iTechSmart-1.1.0.dmg
# Linux: iTechSmart-1.1.0.AppImage

# Install and configure
# Set LICENSE_SERVER_URL in settings
```

---

### 3. Tier 2 Products Deployment

Deploy products with display integration.

```bash
# Analytics
cd itechsmart-analytics && docker-compose up -d

# Copilot
cd itechsmart-copilot && docker-compose up -d

# Shield
cd itechsmart-shield && docker-compose up -d

# Sentinel
cd itechsmart-sentinel && docker-compose up -d

# DevOps
cd itechsmart-devops && docker-compose up -d
```

---

### 4. Tier 3 Products Deployment

Deploy remaining products with basic awareness.

```bash
# Deploy all Tier 3 products
for product in itechsmart-*; do
  if [ -d "$product" ] && [ -f "$product/docker-compose.yml" ]; then
    cd "$product"
    docker-compose up -d
    cd ..
  fi
done
```

---

### 5. Agent Deployment

Deploy agents on systems you want to monitor.

#### Linux/macOS
```bash
# Download agent
wget https://github.com/Iteksmart/iTechSmart/releases/download/v1.1.0/itechsmart-agent-linux-amd64

# Install
sudo mv itechsmart-agent-linux-amd64 /usr/local/bin/itechsmart-agent
sudo chmod +x /usr/local/bin/itechsmart-agent

# Create config
sudo mkdir -p /etc/itechsmart
sudo cat > /etc/itechsmart/agent.yaml << EOF
server_url: http://your-license-server:3000
api_key: your-api-key
hostname: $(hostname)
collection_interval: 30s
log_level: info
EOF

# Create systemd service
sudo cat > /etc/systemd/system/itechsmart-agent.service << EOF
[Unit]
Description=iTechSmart Agent
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/itechsmart-agent --config /etc/itechsmart/agent.yaml
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable itechsmart-agent
sudo systemctl start itechsmart-agent

# Check status
sudo systemctl status itechsmart-agent
```

#### Windows
```powershell
# Download agent
Invoke-WebRequest -Uri "https://github.com/Iteksmart/iTechSmart/releases/download/v1.1.0/itechsmart-agent-windows-amd64.exe" -OutFile "itechsmart-agent.exe"

# Install as service
.\itechsmart-agent.exe install --config agent-config.yaml

# Start service
Start-Service iTechSmartAgent

# Check status
Get-Service iTechSmartAgent
```

---

## 🔍 Verification Steps

### 1. Check Service Health
```bash
# License Server
curl http://localhost:3000/health

# All products
for port in 8001 8002 8003 8004 8005 8006 8017 8018 8019; do
  echo "Checking port $port..."
  curl -s http://localhost:$port/health || echo "Port $port not responding"
done
```

### 2. Verify Agent Connectivity
```bash
# Check agents in License Server
curl http://localhost:3000/api/agents

# Expected response:
# {
#   "agents": [
#     {
#       "id": "agent-id",
#       "hostname": "server-1",
#       "status": "ACTIVE",
#       "lastSeen": "2025-11-17T..."
#     }
#   ]
# }
```

### 3. Test Agent Integration
```bash
# Check agent metrics in Ninja
curl http://localhost:8001/api/v1/agents/stats/summary

# Check agent dashboard
# Open browser: http://localhost:8001
# Navigate to Agent Monitoring section
```

### 4. Verify Alerts
```bash
# Check for alerts
curl http://localhost:3000/api/agents/agent-id/alerts

# Test alert generation
# Stop agent service and wait 2 minutes
# Check for offline alert
```

---

## 🔒 Security Configuration

### 1. Enable HTTPS
```bash
# Generate SSL certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/itechsmart.key \
  -out /etc/ssl/certs/itechsmart.crt

# Update nginx configuration
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/certs/itechsmart.crt;
    ssl_certificate_key /etc/ssl/private/itechsmart.key;
    
    location / {
        proxy_pass http://localhost:3000;
    }
}
```

### 2. Configure Firewall
```bash
# Allow required ports
sudo ufw allow 3000/tcp  # License Server
sudo ufw allow 8001/tcp  # Ninja
sudo ufw allow 8002/tcp  # Enterprise
# ... add other ports as needed

# Enable firewall
sudo ufw enable
```

### 3. Set Up Authentication
```bash
# Generate API keys for agents
curl -X POST http://localhost:3000/api/auth/api-keys \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"agent-key-1","permissions":["agent:write"]}'
```

---

## 📊 Monitoring & Maintenance

### 1. Monitor Services
```bash
# Check Docker containers
docker-compose ps

# View logs
docker-compose logs -f license-server

# Check resource usage
docker stats
```

### 2. Database Backups
```bash
# Backup PostgreSQL
docker exec postgres pg_dump -U user itechsmart > backup-$(date +%Y%m%d).sql

# Restore
docker exec -i postgres psql -U user itechsmart < backup-20251117.sql
```

### 3. Update Agents
```bash
# Download new version
wget https://github.com/Iteksmart/iTechSmart/releases/download/v1.2.0/itechsmart-agent-linux-amd64

# Stop service
sudo systemctl stop itechsmart-agent

# Replace binary
sudo mv itechsmart-agent-linux-amd64 /usr/local/bin/itechsmart-agent

# Start service
sudo systemctl start itechsmart-agent
```

---

## 🐛 Troubleshooting

### Agent Not Connecting
```bash
# Check agent logs
sudo journalctl -u itechsmart-agent -f

# Verify network connectivity
curl http://license-server:3000/health

# Check API key
# Ensure API key in agent config matches License Server
```

### Dashboard Not Showing Agents
```bash
# Check License Server logs
docker-compose logs license-server

# Verify agent registration
curl http://localhost:3000/api/agents

# Check product configuration
# Ensure LICENSE_SERVER_URL is set correctly
```

### High Resource Usage
```bash
# Check agent collection interval
# Increase interval in agent config:
collection_interval: 60s  # Instead of 30s

# Limit metric retention
# Configure in License Server:
METRIC_RETENTION_DAYS=7
```

---

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale License Server
docker-compose up -d --scale license-server=3

# Add load balancer
# Use nginx or HAProxy to distribute traffic
```

### Database Scaling
```bash
# Use PostgreSQL replication
# Configure read replicas for better performance

# Use connection pooling
# Configure pgBouncer or similar
```

---

## 🎯 Next Steps

1. ✅ Deploy License Server
2. ✅ Deploy Tier 1 products
3. ✅ Deploy agents on target systems
4. ✅ Verify connectivity
5. ⏳ Configure alerts and notifications
6. ⏳ Set up monitoring dashboards
7. ⏳ Train users on new features
8. ⏳ Monitor performance and optimize

---

## 📞 Support

- **Documentation**: See AGENT_INTEGRATION_COMPLETE.md
- **Issues**: https://github.com/Iteksmart/iTechSmart/issues
- **Email**: support@itechsmart.dev

---

**© 2025 iTechSmart Inc. All rights reserved.**