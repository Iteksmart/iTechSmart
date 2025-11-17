# 🚀 iTechSmart PassPort - Complete Deployment Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
7. [Security Checklist](#security-checklist)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)

---

## 1. Prerequisites

### Required Software
- Docker & Docker Compose (v20.10+)
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)
- PostgreSQL 15+ (for local development)
- Redis 7+ (for local development)

### Required Accounts
- Stripe account (for payments)
- SendGrid account (for emails)
- Domain name (for production)
- SSL certificate (Let's Encrypt recommended)

---

## 2. Local Development

### Backend Setup
```bash
# Navigate to backend
cd passport/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your settings
nano .env

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
# Navigate to frontend
cd passport/frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Edit .env.local
nano .env.local

# Start development server
npm run dev
```

### Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 3. Docker Deployment

### Quick Start
```bash
# Navigate to project root
cd passport

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### Services
- **postgres**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)
- **backend**: FastAPI application (port 8000)
- **frontend**: Next.js application (port 3000)

### Verify Deployment
```bash
# Check service status
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000
```

---

## 4. Production Deployment

### Option 1: Railway (Recommended for Backend)

#### Backend Deployment
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Link to project
railway link

# Deploy backend
cd passport/backend
railway up

# Set environment variables
railway variables set DATABASE_URL=postgresql://...
railway variables set REDIS_URL=redis://...
railway variables set SECRET_KEY=your-secret-key
railway variables set JWT_SECRET_KEY=your-jwt-secret
railway variables set MASTER_KEY=your-master-key
railway variables set VAULT_ENCRYPTION_KEY=your-vault-key
```

#### Database Setup on Railway
```bash
# Add PostgreSQL
railway add postgresql

# Add Redis
railway add redis

# Get connection strings
railway variables
```

### Option 2: Vercel (Recommended for Frontend)

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend
cd passport/frontend

# Deploy
vercel

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://your-backend-url.railway.app

# Deploy to production
vercel --prod
```

### Option 3: AWS (Full Control)

#### Backend on EC2
```bash
# SSH into EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Docker
sudo apt update
sudo apt install docker.io docker-compose -y

# Clone repository
git clone https://github.com/your-repo/passport.git
cd passport

# Copy and configure environment
cp backend/.env.example backend/.env
nano backend/.env

# Start services
docker-compose up -d

# Setup Nginx reverse proxy
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/passport

# Add configuration:
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/passport /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.yourdomain.com
```

#### Frontend on Vercel
Same as Option 2 above.

### Option 4: DigitalOcean App Platform

```bash
# Create app.yaml
cat > app.yaml << EOF
name: passport
services:
  - name: backend
    github:
      repo: your-username/passport
      branch: main
      deploy_on_push: true
    source_dir: /backend
    dockerfile_path: Dockerfile
    envs:
      - key: DATABASE_URL
        value: \${db.DATABASE_URL}
      - key: REDIS_URL
        value: \${redis.REDIS_URL}
    http_port: 8000
    
  - name: frontend
    github:
      repo: your-username/passport
      branch: main
      deploy_on_push: true
    source_dir: /frontend
    dockerfile_path: Dockerfile
    envs:
      - key: NEXT_PUBLIC_API_URL
        value: \${backend.PUBLIC_URL}
    http_port: 3000

databases:
  - name: db
    engine: PG
    version: "15"
  
  - name: redis
    engine: REDIS
    version: "7"
EOF

# Deploy
doctl apps create --spec app.yaml
```

---

## 5. Environment Configuration

### Backend (.env)
```bash
# Application
APP_NAME=iTechSmart PassPort
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=CHANGE_THIS_TO_RANDOM_32_CHAR_STRING
API_V1_PREFIX=/api/v1

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://host:6379/0
REDIS_PASSWORD=
REDIS_DB=0

# JWT
JWT_SECRET_KEY=CHANGE_THIS_TO_RANDOM_32_CHAR_STRING
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Encryption
MASTER_KEY=CHANGE_THIS_TO_RANDOM_32_BYTE_STRING
VAULT_ENCRYPTION_KEY=CHANGE_THIS_TO_RANDOM_32_BYTE_STRING

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_ALLOW_CREDENTIALS=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Email (SendGrid)
SENDGRID_API_KEY=your_sendgrid_api_key
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=iTechSmart PassPort

# Stripe
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
STRIPE_PRICE_ID=price_your_price_id

# Breach Monitoring
HIBP_API_KEY=your_haveibeenpwned_api_key

# AI Services (Optional)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Monitoring
SENTRY_DSN=your_sentry_dsn
PROMETHEUS_PORT=9090

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_key
```

### Generate Secure Keys
```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate MASTER_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate VAULT_ENCRYPTION_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 6. Database Setup

### Create Database
```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE passport;

-- Create user
CREATE USER passport_user WITH PASSWORD 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE passport TO passport_user;

-- Exit
\q
```

### Run Migrations
```bash
cd passport/backend

# Initialize Alembic (if not done)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head

# Rollback (if needed)
alembic downgrade -1
```

### Create Admin User
```python
# create_admin.py
import asyncio
from app.db.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash, VaultEncryption

async def create_admin():
    async with AsyncSessionLocal() as db:
        # Check if admin exists
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == "admin@example.com"))
        if result.scalar_one_or_none():
            print("Admin user already exists")
            return
        
        # Generate vault salt
        vault_salt = VaultEncryption.generate_salt()
        
        # Create admin user
        admin = User(
            email="admin@example.com",
            hashed_password=get_password_hash("Admin123!"),
            full_name="Admin User",
            master_password_hash=get_password_hash("AdminMaster123!"),
            vault_salt=vault_salt.hex(),
            role=UserRole.ADMIN,
            is_verified=True,
            is_active=True
        )
        
        db.add(admin)
        await db.commit()
        print("Admin user created successfully")
        print("Email: admin@example.com")
        print("Password: Admin123!")
        print("Master Password: AdminMaster123!")

if __name__ == "__main__":
    asyncio.run(create_admin())
```

Run:
```bash
python create_admin.py
```

---

## 7. Security Checklist

### Before Production
- [ ] Change all default passwords
- [ ] Generate secure random keys
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Setup firewall rules
- [ ] Enable database backups
- [ ] Setup monitoring
- [ ] Configure logging
- [ ] Review security headers
- [ ] Enable 2FA for admin accounts
- [ ] Setup Stripe webhooks
- [ ] Configure email service
- [ ] Test breach detection
- [ ] Review API permissions
- [ ] Setup error tracking (Sentry)

### Security Headers (Nginx)
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

---

## 8. Monitoring & Maintenance

### Health Checks
```bash
# Backend health
curl https://api.yourdomain.com/health

# Database connection
docker-compose exec postgres pg_isready

# Redis connection
docker-compose exec redis redis-cli ping
```

### Logs
```bash
# View all logs
docker-compose logs -f

# View backend logs
docker-compose logs -f backend

# View frontend logs
docker-compose logs -f frontend

# View last 100 lines
docker-compose logs --tail=100 backend
```

### Backups
```bash
# Backup database
docker-compose exec postgres pg_dump -U passport passport > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T postgres psql -U passport passport < backup_20250115.sql

# Automated daily backups (crontab)
0 2 * * * cd /path/to/passport && docker-compose exec postgres pg_dump -U passport passport > /backups/backup_$(date +\%Y\%m\%d).sql
```

### Updates
```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose build

# Restart services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

---

## 9. Troubleshooting

### Backend Won't Start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database connection failed
#    - Verify DATABASE_URL
#    - Check if postgres is running
#    - Test connection: docker-compose exec postgres psql -U passport

# 2. Redis connection failed
#    - Verify REDIS_URL
#    - Check if redis is running
#    - Test connection: docker-compose exec redis redis-cli ping

# 3. Port already in use
#    - Change port in docker-compose.yml
#    - Or stop conflicting service
```

### Frontend Won't Start
```bash
# Check logs
docker-compose logs frontend

# Common issues:
# 1. API connection failed
#    - Verify NEXT_PUBLIC_API_URL
#    - Check if backend is running
#    - Test: curl http://localhost:8000/health

# 2. Build failed
#    - Clear cache: rm -rf .next
#    - Rebuild: docker-compose build frontend
```

### Database Issues
```bash
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head

# Check database size
docker-compose exec postgres psql -U passport -c "SELECT pg_size_pretty(pg_database_size('passport'));"

# Check active connections
docker-compose exec postgres psql -U passport -c "SELECT count(*) FROM pg_stat_activity;"
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Increase workers (backend)
# Edit docker-compose.yml:
environment:
  WORKERS: 8

# Increase database pool
# Edit .env:
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=20

# Add Redis caching
# Already configured, ensure REDIS_URL is set
```

---

## 🎉 Deployment Complete!

Your iTechSmart PassPort is now deployed and ready to use!

### Next Steps
1. Test all features thoroughly
2. Setup monitoring alerts
3. Configure automated backups
4. Setup CI/CD pipeline
5. Invite beta users
6. Collect feedback
7. Iterate and improve

### Support
- Documentation: https://docs.yourdomain.com
- Email: support@yourdomain.com
- GitHub Issues: https://github.com/your-repo/issues

---

**🚀 Happy Deploying!**