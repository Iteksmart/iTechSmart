# iTechSmart Ninja - Founder In-House Setup Guide

## 🎯 Overview
This is your personal AI agent platform, optimized for single-user (founder-only) deployment. All multi-tenant features have been simplified for your exclusive use.

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Docker & Docker Compose installed
- Git installed
- 8GB RAM minimum
- 20GB disk space

### Step 1: Clone & Configure
```bash
cd itechsmart-ninja

# Create your personal environment file
cp .env.example .env

# Edit with your personal settings
nano .env
```

### Step 2: Configure Your Personal Settings
Edit `.env` with your details:
```bash
# Your Personal API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here

# Your Personal Database (auto-created)
DATABASE_URL=postgresql+asyncpg://ninja:ninja123@postgres:5432/ninja

# Your Personal Security
SECRET_KEY=your_super_secret_key_here_change_this
JWT_SECRET_KEY=your_jwt_secret_here_change_this

# Your Personal Settings
FOUNDER_EMAIL=your_email@itechsmart.dev
FOUNDER_NAME=Your Name
ENVIRONMENT=production
```

### Step 3: Launch Your Platform
```bash
# Start everything with one command
docker-compose up -d

# Wait 30 seconds for initialization
sleep 30

# Check status
docker-compose ps
```

### Step 4: Access Your Platform
- **Frontend UI:** http://localhost:3000
- **API Documentation:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/health

## 🔐 First Login

### Create Your Founder Account
```bash
# Access the backend container
docker exec -it ninja-backend bash

# Create your founder account
python -c "
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
founder = User(
    email='your_email@itechsmart.dev',
    username='founder',
    full_name='Your Name',
    hashed_password=get_password_hash('your_secure_password'),
    is_active=True,
    is_superuser=True,
    role='founder'
)
db.add(founder)
db.commit()
print('Founder account created!')
"
```

### Login to Your Platform
1. Go to http://localhost:3000
2. Click "Login"
3. Enter your credentials
4. Start using your AI agent platform!

## 🎨 Your Platform Features

### 1. AI Agents (5 Specialized Agents)
- **Coder Agent:** Write, debug, and optimize code
- **Researcher Agent:** Deep research and analysis
- **Writer Agent:** Content creation and editing
- **Analyst Agent:** Data analysis and insights
- **Debugger Agent:** Find and fix bugs

### 2. Vision Analysis
- OCR and text extraction
- Object detection
- Code detection from screenshots
- Diagram analysis
- UI/UX analysis
- Visual Q&A

### 3. Sandbox Environments
- 9 programming languages
- Isolated execution
- Resource limits
- Safe testing

### 4. Virtual Machines
- 6 cloud providers
- Auto-scaling
- Multiple OS options
- Full control

### 5. File Processing
- 15+ file formats
- Content extraction
- Batch processing
- Smart parsing

### 6. Terminal Access
- Full shell access
- Command history
- WebSocket support
- Real-time execution

### 7. Workflow Automation
- 5 trigger types
- 10 action types
- Conditional logic
- Scheduled execution

### 8. Calendar & Scheduling
- Event management
- Recurring events
- Availability checking
- Reminders

### 9. Application Hosting
- Container orchestration
- Auto-scaling
- Domain management
- SSL/TLS support

### 10. Knowledge Graph
- 9 entity types
- 11 relationship types
- Path finding
- Clustering

### 11. Image Editing
- 8 filters
- 4 enhancements
- Batch processing
- Format conversion

### 12. Performance Analytics
- System monitoring
- API metrics
- User tracking
- Resource usage

### 13. Chat & Collaboration
- Real-time messaging
- Threads
- Reactions
- File sharing

### 14. Plugin Ecosystem
- Marketplace
- Version management
- Safe execution
- Custom plugins

### 15. Integrations (12 Types)
- Google Drive
- Slack
- GitHub
- Jira
- Gmail
- Trello
- Asana
- Notion
- Dropbox
- OneDrive
- Zoom
- Calendar

### 16. Privacy & Security
- GDPR compliance
- End-to-end encryption
- Data export/deletion
- Consent management

### 17. Action History
- Undo/Redo
- State snapshots
- Rollback
- Audit trail

## 🛠️ Daily Operations

### Start Your Platform
```bash
docker-compose up -d
```

### Stop Your Platform
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Backup Your Data
```bash
# Backup database
docker exec ninja-postgres pg_dump -U ninja ninja > backup_$(date +%Y%m%d).sql

# Backup uploads
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz backend/uploads/
```

### Restore Your Data
```bash
# Restore database
cat backup_20250112.sql | docker exec -i ninja-postgres psql -U ninja ninja

# Restore uploads
tar -xzf uploads_backup_20250112.tar.gz
```

## 🔧 Troubleshooting

### Platform Won't Start
```bash
# Check Docker
docker --version
docker-compose --version

# Check ports
netstat -an | grep -E "3000|8000|5432|6379"

# Restart everything
docker-compose down
docker-compose up -d --force-recreate
```

### Can't Login
```bash
# Reset your password
docker exec -it ninja-backend python -c "
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
user = db.query(User).filter(User.email=='your_email@itechsmart.dev').first()
user.hashed_password = get_password_hash('new_password')
db.commit()
print('Password reset!')
"
```

### Database Issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d
# Wait 30 seconds, then recreate founder account
```

## 📊 Monitoring Your Platform

### Health Check
```bash
curl http://localhost:8000/health
```

### API Status
```bash
curl http://localhost:8000/api/v1/status
```

### Database Status
```bash
docker exec ninja-postgres psql -U ninja -c "SELECT version();"
```

### Redis Status
```bash
docker exec ninja-redis redis-cli ping
```

## 🎯 Advanced Configuration

### Custom Domain
Edit `docker-compose.yml`:
```yaml
frontend:
  environment:
    - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### SSL/TLS
Add nginx reverse proxy:
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com
```

### Performance Tuning
Edit `.env`:
```bash
# Increase workers
WORKERS=4

# Increase memory
MAX_MEMORY=4096

# Enable caching
CACHE_ENABLED=true
```

## 📱 Mobile Access

### Access from Phone/Tablet
1. Find your computer's IP: `ifconfig` or `ipconfig`
2. Access from mobile: `http://YOUR_IP:3000`
3. Bookmark for quick access

### Remote Access (Advanced)
Use ngrok or similar:
```bash
# Install ngrok
npm install -g ngrok

# Expose frontend
ngrok http 3000

# Expose backend
ngrok http 8000
```

## 🎉 You're All Set!

Your personal AI agent platform is ready. Access it at:
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs

Need help? Check the troubleshooting section or review the logs.

---

**iTechSmart Ninja** - Your Personal AI Agent Platform
Built exclusively for the founder of iTechSmart Inc.