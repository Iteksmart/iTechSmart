# iTechSmart Ninja - Deployment Checklist for Founder

## 🎯 Pre-Deployment Checklist

### 1. Environment Configuration ✅
- [ ] Copy `.env.example` to `.env`
- [ ] Set `FOUNDER_EMAIL` to your email
- [ ] Set `FOUNDER_NAME` to your name
- [ ] Change `SECRET_KEY` to a random secure key
- [ ] Change `JWT_SECRET_KEY` to a random secure key
- [ ] Add your `OPENAI_API_KEY`
- [ ] Add your `ANTHROPIC_API_KEY` (optional)
- [ ] Add your `GOOGLE_API_KEY` (optional)
- [ ] Set `ENVIRONMENT=production`

### 2. Security Configuration ✅
- [ ] Generate strong SECRET_KEY: `openssl rand -hex 32`
- [ ] Generate strong JWT_SECRET_KEY: `openssl rand -hex 32`
- [ ] Review CORS settings in `.env`
- [ ] Ensure database password is strong
- [ ] Review rate limiting settings

### 3. Integration Setup (Optional) ✅
- [ ] Configure GitHub token for code integration
- [ ] Configure Slack tokens for notifications
- [ ] Configure Google Drive credentials
- [ ] Configure cloud provider credentials (AWS/GCP/Azure)
- [ ] Configure other integrations as needed

### 4. System Requirements ✅
- [ ] Docker installed (version 20.10+)
- [ ] Docker Compose installed (version 2.0+)
- [ ] 8GB RAM minimum (16GB recommended)
- [ ] 20GB disk space minimum (50GB recommended)
- [ ] Stable internet connection

## 🚀 Deployment Steps

### Step 1: Initial Setup
```bash
# Navigate to project directory
cd itechsmart-ninja

# Make quick start script executable
chmod +x QUICK_START.sh

# Run quick start
./QUICK_START.sh
```

### Step 2: Create Founder Account
```bash
# Create your founder account
docker exec -it ninja-backend python scripts/create_founder.py

# Follow the prompts to set up your account
```

### Step 3: Verify Deployment
```bash
# Check all services are running
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check frontend is accessible
curl http://localhost:3000
```

### Step 4: First Login
1. Open browser to http://localhost:3000
2. Click "Login"
3. Enter your founder credentials
4. Verify dashboard loads correctly

## 🔧 Post-Deployment Configuration

### 1. Configure AI Providers
- [ ] Test OpenAI integration
- [ ] Test Anthropic integration (if configured)
- [ ] Test Google AI integration (if configured)
- [ ] Verify vision analysis works

### 2. Set Up Integrations
- [ ] Connect GitHub account
- [ ] Connect Slack workspace
- [ ] Connect Google Drive
- [ ] Connect other services as needed

### 3. Configure Workflows
- [ ] Create your first workflow
- [ ] Test workflow execution
- [ ] Set up automated tasks

### 4. Test Core Features
- [ ] Create and run a task with AI agent
- [ ] Upload and parse a file
- [ ] Execute code in sandbox
- [ ] Create a calendar event
- [ ] Test terminal access
- [ ] Test vision analysis

## 📊 Monitoring & Maintenance

### Daily Checks
```bash
# Check service status
docker-compose ps

# View recent logs
docker-compose logs --tail=100

# Check disk space
df -h

# Check memory usage
free -h
```

### Weekly Maintenance
```bash
# Backup database
docker exec ninja-postgres pg_dump -U ninja ninja > backup_$(date +%Y%m%d).sql

# Backup uploads
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz backend/uploads/

# Clean up old logs
find backend/logs -name "*.log" -mtime +30 -delete

# Update Docker images
docker-compose pull
docker-compose up -d
```

### Monthly Tasks
- [ ] Review and rotate API keys
- [ ] Check for security updates
- [ ] Review resource usage and optimize
- [ ] Clean up old data and files
- [ ] Test backup restoration

## 🔐 Security Best Practices

### 1. Access Control
- [ ] Use strong passwords (16+ characters)
- [ ] Enable 2FA if available
- [ ] Regularly rotate API keys
- [ ] Review access logs

### 2. Data Protection
- [ ] Enable encryption at rest
- [ ] Use HTTPS in production
- [ ] Regular backups (daily recommended)
- [ ] Test backup restoration monthly

### 3. Network Security
- [ ] Use firewall rules
- [ ] Limit exposed ports
- [ ] Use VPN for remote access
- [ ] Monitor for suspicious activity

## 🚨 Troubleshooting

### Services Won't Start
```bash
# Check Docker daemon
sudo systemctl status docker

# Check port conflicts
netstat -tulpn | grep -E "3000|8000|5432|6379"

# Force recreate
docker-compose down -v
docker-compose up -d --force-recreate
```

### Can't Login
```bash
# Reset password
docker exec -it ninja-backend python scripts/create_founder.py reset

# Check user exists
docker exec -it ninja-backend python -c "
from app.core.database import SessionLocal
from app.models.user import User
db = SessionLocal()
users = db.query(User).all()
for u in users:
    print(f'{u.email} - {u.username} - {u.role}')
"
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Increase resources in docker-compose.yml
# Add under backend service:
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G

# Restart services
docker-compose restart
```

### Database Issues
```bash
# Check database connection
docker exec ninja-postgres psql -U ninja -c "SELECT version();"

# Check database size
docker exec ninja-postgres psql -U ninja -c "
SELECT pg_size_pretty(pg_database_size('ninja'));
"

# Vacuum database
docker exec ninja-postgres psql -U ninja -c "VACUUM ANALYZE;"
```

## 📈 Performance Optimization

### 1. Database Optimization
```bash
# Add indexes for common queries
docker exec -it ninja-backend python -c "
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_user_email ON users(email);'))
    conn.execute(text('CREATE INDEX IF NOT EXISTS idx_task_status ON tasks(status);'))
    conn.commit()
"
```

### 2. Cache Configuration
Edit `.env`:
```bash
CACHE_ENABLED=true
CACHE_TTL=3600
REDIS_MAX_MEMORY=1gb
```

### 3. Worker Scaling
Edit `docker-compose.yml`:
```yaml
backend:
  environment:
    - WORKERS=4  # Increase for better performance
```

## 🎉 You're Ready!

Your iTechSmart Ninja platform is now deployed and ready for use!

### Quick Access
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Next Steps
1. Explore all 25 features
2. Set up your workflows
3. Connect your integrations
4. Start building with AI agents

### Support
- Documentation: `FOUNDER_SETUP.md`
- API Reference: http://localhost:8000/docs
- Logs: `docker-compose logs -f`

---

**iTechSmart Ninja** - Your Personal AI Agent Platform
Built exclusively for the founder of iTechSmart Inc.