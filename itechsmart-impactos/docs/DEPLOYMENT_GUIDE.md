# 🚀 iTechSmart ImpactOS - Deployment Guide

## Quick Deployment Options

### Option 1: Docker Compose (Recommended for Development/Small Production)
### Option 2: Kubernetes (Recommended for Production)
### Option 3: Manual Installation

---

## Option 1: Docker Compose Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space

### Step 1: Clone Repository
```bash
git clone https://github.com/itechsmart/impactos.git
cd impactos
```

### Step 2: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql://impactos:CHANGE_ME@postgres:5432/impactos_db

# Redis
REDIS_URL=redis://redis:6379/0

# Security (CHANGE THESE!)
SECRET_KEY=your-super-secret-key-min-32-chars
NEXTAUTH_SECRET=your-nextauth-secret-min-32-chars

# AI APIs (Optional but recommended)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=...

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
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

### Step 4: Initialize Database
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create super admin
docker-compose exec backend python -c "
from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
admin = User(
    email='admin@example.com',
    username='admin',
    full_name='Admin User',
    hashed_password=get_password_hash('Admin123!'),
    is_superuser=True,
    is_verified=True
)
db.add(admin)
db.commit()
print('Admin user created!')
"
```

### Step 5: Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs

**Default Login:**
- Email: admin@example.com
- Password: Admin123!

### Step 6: SSL/HTTPS Setup (Production)
```bash
# Install certbot
sudo apt-get install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d app.yourdomain.com -d api.yourdomain.com

# Update nginx.conf with SSL paths
# Restart nginx
docker-compose restart nginx
```

---

## Option 2: Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (1.24+)
- kubectl configured
- Helm 3.0+ (optional)
- 8GB RAM minimum per node
- 50GB disk space

### Step 1: Create Namespace
```bash
kubectl create namespace impactos
kubectl config set-context --current --namespace=impactos
```

### Step 2: Create Secrets
```bash
# Create database secret
kubectl create secret generic impactos-secrets \
  --from-literal=database-url='postgresql://user:pass@postgres:5432/impactos_db' \
  --from-literal=redis-url='redis://redis:6379/0' \
  --from-literal=secret-key='your-secret-key' \
  --from-literal=nextauth-secret='your-nextauth-secret' \
  --from-literal=openai-api-key='your-openai-key' \
  --from-literal=anthropic-api-key='your-anthropic-key' \
  --from-literal=google-ai-api-key='your-google-key' \
  --from-literal=postgres-user='impactos' \
  --from-literal=postgres-password='secure-password'
```

### Step 3: Deploy PostgreSQL
```bash
kubectl apply -f k8s/deployment.yml
```

### Step 4: Deploy Services
```bash
kubectl apply -f k8s/service.yml
```

### Step 5: Deploy Ingress
```bash
# Install nginx ingress controller (if not already installed)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Deploy ingress
kubectl apply -f k8s/ingress.yml
```

### Step 6: Install Cert-Manager (for SSL)
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### Step 7: Verify Deployment
```bash
# Check pods
kubectl get pods

# Check services
kubectl get services

# Check ingress
kubectl get ingress

# View logs
kubectl logs -f deployment/impactos-backend
```

### Step 8: Initialize Database
```bash
# Run migrations
kubectl exec -it deployment/impactos-backend -- alembic upgrade head

# Create admin user
kubectl exec -it deployment/impactos-backend -- python create_admin.py
```

### Step 9: Access Application
- **Frontend**: https://app.yourdomain.com
- **Backend API**: https://api.yourdomain.com
- **API Docs**: https://api.yourdomain.com/api/v1/docs

---

## Option 3: Manual Installation

### Prerequisites
- Ubuntu 22.04 LTS
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Nginx

### Step 1: Install Dependencies
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python
sudo apt-get install python3.11 python3.11-venv python3-pip -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install nodejs -y

# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib -y

# Install Redis
sudo apt-get install redis-server -y

# Install Nginx
sudo apt-get install nginx -y
```

### Step 2: Setup Database
```bash
# Create database and user
sudo -u postgres psql <<EOF
CREATE DATABASE impactos_db;
CREATE USER impactos WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE impactos_db TO impactos;
\q
EOF
```

### Step 3: Setup Backend
```bash
# Clone repository
git clone https://github.com/itechsmart/impactos.git
cd impactos/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env

# Run migrations
alembic upgrade head

# Create systemd service
sudo nano /etc/systemd/system/impactos-backend.service
```

**Backend Service File:**
```ini
[Unit]
Description=iTechSmart ImpactOS Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/impactos/backend
Environment="PATH=/var/www/impactos/backend/venv/bin"
ExecStart=/var/www/impactos/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable impactos-backend
sudo systemctl start impactos-backend
```

### Step 4: Setup Frontend
```bash
cd ../frontend

# Install dependencies
npm install

# Build application
npm run build

# Create systemd service
sudo nano /etc/systemd/system/impactos-frontend.service
```

**Frontend Service File:**
```ini
[Unit]
Description=iTechSmart ImpactOS Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/impactos/frontend
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable impactos-frontend
sudo systemctl start impactos-frontend
```

### Step 5: Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/impactos
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name app.yourdomain.com api.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/app.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/impactos /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## Post-Deployment Checklist

### Security
- [ ] Change all default passwords
- [ ] Configure SSL/TLS certificates
- [ ] Enable firewall (UFW)
- [ ] Set up fail2ban
- [ ] Configure security headers
- [ ] Enable rate limiting
- [ ] Set up monitoring alerts

### Performance
- [ ] Configure database connection pooling
- [ ] Enable Redis caching
- [ ] Set up CDN (optional)
- [ ] Configure gzip compression
- [ ] Optimize database indexes
- [ ] Set up load balancing (if needed)

### Monitoring
- [ ] Set up Prometheus
- [ ] Configure Grafana dashboards
- [ ] Enable error tracking (Sentry)
- [ ] Set up uptime monitoring
- [ ] Configure log aggregation
- [ ] Set up backup monitoring

### Backup
- [ ] Configure automated database backups
- [ ] Set up off-site backup storage
- [ ] Test backup restoration
- [ ] Document recovery procedures
- [ ] Set up backup monitoring

---

## Scaling Considerations

### Horizontal Scaling
- Add more backend replicas
- Use load balancer (Nginx, HAProxy)
- Implement session storage in Redis
- Use managed database service

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Implement caching strategies
- Use CDN for static assets

### Database Scaling
- Read replicas for read-heavy workloads
- Connection pooling
- Query optimization
- Partitioning (if needed)

---

## Troubleshooting

### Common Issues

**Services won't start**
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Check ports
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :3000
```

**Database connection errors**
```bash
# Test connection
docker-compose exec postgres psql -U impactos -d impactos_db

# Check credentials in .env
cat .env | grep DATABASE_URL
```

**SSL certificate issues**
```bash
# Renew certificate
sudo certbot renew

# Check certificate
sudo certbot certificates
```

---

## Support

**Documentation**: https://docs.impactos.com
**Email**: support@itechsmart.dev
**Phone**: 1-800-IMPACT-OS

---

**Version 1.0 | Last Updated: January 2025**