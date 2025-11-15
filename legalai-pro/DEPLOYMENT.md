# LegalAI Pro - Deployment Guide

## 🚀 Quick Start (Development)

### Option 1: Manual Setup

#### Backend
```bash
cd legalai-pro/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend will be available at: http://localhost:8000

#### Frontend
```bash
cd legalai-pro/frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:3000

### Option 2: Docker Compose (Recommended)

```bash
cd legalai-pro
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Backend API on port 8000
- Frontend on port 3000

## 📦 Production Deployment

### Prerequisites
- Server with Ubuntu 20.04+ or similar
- Docker and Docker Compose installed
- Domain name (optional)
- SSL certificate (recommended)

### Step 1: Clone Repository
```bash
git clone <your-repo-url>
cd legalai-pro
```

### Step 2: Configure Environment
```bash
# Backend environment
cp backend/.env.example backend/.env
# Edit backend/.env with your production settings

# Frontend environment
cp frontend/.env.example frontend/.env
# Edit frontend/.env with your production API URL
```

### Step 3: Build and Deploy
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Step 4: Set Up Nginx (Optional)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Step 5: SSL with Let's Encrypt
```bash
sudo certbot --nginx -d your-domain.com
```

## 🔧 Configuration

### Backend Configuration (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/legalai_pro
SECRET_KEY=your-super-secret-key-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### Frontend Configuration (.env)
```env
VITE_API_URL=http://localhost:8000
```

## 🗄️ Database Setup

### Create Database
```bash
# Using PostgreSQL
createdb legalai_pro

# Or using psql
psql -U postgres
CREATE DATABASE legalai_pro;
```

### Run Migrations
```bash
cd backend
alembic upgrade head
```

### Create Admin User
```bash
python scripts/create_admin.py
```

## 🔐 Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong database passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up firewall rules
- [ ] Enable database backups
- [ ] Configure rate limiting
- [ ] Set up monitoring

## 📊 Monitoring

### Health Check Endpoints
- Backend: http://localhost:8000/health
- API Docs: http://localhost:8000/docs

### Logs
```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Application logs
tail -f backend/logs/app.log
```

## 🔄 Updates

### Pull Latest Changes
```bash
git pull origin main
```

### Rebuild and Restart
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## 💾 Backup

### Database Backup
```bash
# Backup
docker-compose exec db pg_dump -U legalai legalai_pro > backup.sql

# Restore
docker-compose exec -T db psql -U legalai legalai_pro < backup.sql
```

### File Backup
```bash
# Backup documents
tar -czf documents-backup.tar.gz backend/documents/
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Verify database connection
docker-compose exec backend python -c "from app.core.database import engine; print(engine)"
```

### Frontend won't start
```bash
# Check logs
docker-compose logs frontend

# Rebuild node_modules
docker-compose exec frontend npm install
```

### Database connection issues
```bash
# Check database is running
docker-compose ps db

# Test connection
docker-compose exec db psql -U legalai -d legalai_pro
```

## 📈 Performance Optimization

### Backend
- Use Gunicorn with multiple workers
- Enable Redis for caching
- Configure database connection pooling
- Use CDN for static files

### Frontend
- Build for production: `npm run build`
- Enable gzip compression
- Use CDN for assets
- Implement code splitting

## 🌐 Scaling

### Horizontal Scaling
```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      replicas: 3
    
  frontend:
    deploy:
      replicas: 2
```

### Load Balancing
Use Nginx or HAProxy for load balancing multiple instances.

## 📞 Support

For deployment support:
- Email: support@legalai.pro
- Documentation: https://docs.legalai.pro
- GitHub Issues: https://github.com/your-repo/issues

---

**Happy Deploying! 🚀**