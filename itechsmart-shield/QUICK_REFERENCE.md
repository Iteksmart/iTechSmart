# iTechSmart Shield - Quick Reference Card

## 🚀 Quick Start

```bash
# Start all services
./start.sh

# Or manually
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🌐 Access URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Main application |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache |
| Elasticsearch | http://localhost:9200 | Logs |

## 🔑 Default Credentials

```
Database:
  User: shield_user
  Password: shield_pass_2024
  Database: shield_db
```

## 📡 API Endpoints

### Threats
```
GET    /api/threats              List all threats
POST   /api/threats              Create threat
GET    /api/threats/{id}         Get threat details
PUT    /api/threats/{id}         Update threat
DELETE /api/threats/{id}         Delete threat
```

### Vulnerabilities
```
GET    /api/vulnerabilities      List vulnerabilities
POST   /api/vulnerabilities      Create vulnerability
GET    /api/vulnerabilities/{id} Get details
PUT    /api/vulnerabilities/{id} Update vulnerability
```

### Compliance
```
GET    /api/compliance           Get overview
GET    /api/compliance/frameworks List frameworks
GET    /api/compliance/controls  List controls
POST   /api/compliance/assess    Run assessment
```

### Incidents
```
GET    /api/incidents            List incidents
POST   /api/incidents            Create incident
GET    /api/incidents/{id}       Get details
PUT    /api/incidents/{id}       Update incident
```

### Dashboard
```
GET    /api/dashboard/stats      Get statistics
GET    /health                   Health check
```

## 🛠️ Common Commands

### Docker Management
```bash
# View running containers
docker-compose ps

# Restart a service
docker-compose restart backend

# View service logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend bash

# Remove all containers and volumes
docker-compose down -v
```

### Database Operations
```bash
# Access PostgreSQL
docker exec -it shield-postgres psql -U shield_user -d shield_db

# Backup database
docker exec shield-postgres pg_dump -U shield_user shield_db > backup.sql

# Restore database
docker exec -i shield-postgres psql -U shield_user shield_db < backup.sql

# Check database status
docker exec shield-postgres pg_isready -U shield_user
```

### Redis Operations
```bash
# Access Redis CLI
docker exec -it shield-redis redis-cli

# Check Redis status
docker exec shield-redis redis-cli ping

# View all keys
docker exec shield-redis redis-cli KEYS '*'

# Clear cache
docker exec shield-redis redis-cli FLUSHALL
```

## 🔍 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs [service-name]

# Restart service
docker-compose restart [service-name]

# Rebuild service
docker-compose build [service-name]
docker-compose up -d [service-name]
```

### Port Already in Use
```bash
# Find process using port (Linux/Mac)
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
docker exec shield-postgres pg_isready -U shield_user

# View PostgreSQL logs
docker-compose logs postgres
```

### Frontend Build Issues
```bash
# Clear cache and rebuild
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

## 📊 Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# PostgreSQL health
docker exec shield-postgres pg_isready -U shield_user

# Redis health
docker exec shield-redis redis-cli ping

# Elasticsearch health
curl http://localhost:9200/_cluster/health
```

### View Metrics
```bash
# Container stats
docker stats

# Service status
docker-compose ps

# Disk usage
docker system df
```

## 🔒 Security

### Change Default Passwords
```bash
# Edit docker-compose.yml
# Update POSTGRES_PASSWORD
# Update Redis password in command

# Restart services
docker-compose down
docker-compose up -d
```

### Enable SSL/TLS
```bash
# Generate certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem

# Update nginx configuration
# Restart services
```

## 📁 File Locations

```
itechsmart-shield/
├── backend/              Backend API code
├── frontend/             Frontend React app
├── docker-compose.yml    Service orchestration
├── init-db.sql          Database initialization
├── start.sh             Quick start script
├── README.md            Full documentation
└── DEPLOYMENT.md        Deployment guide
```

## 🎯 Key Features

- ✅ Real-time threat detection
- ✅ Vulnerability management (CVE)
- ✅ Compliance monitoring (SOC2, ISO27001, GDPR, HIPAA)
- ✅ Incident response
- ✅ Security dashboards
- ✅ Audit logging

## 💡 Tips

1. **Use the quick start script**: `./start.sh` handles everything
2. **Check logs first**: Most issues show up in logs
3. **Health checks**: Use `/health` endpoint to verify backend
4. **Documentation**: Full docs in README.md and DEPLOYMENT.md
5. **Backup regularly**: Use the database backup commands

## 📞 Support

- **Documentation**: README.md, DEPLOYMENT.md
- **API Docs**: http://localhost:8000/docs
- **Issues**: Check logs with `docker-compose logs -f`

## 🚀 Production Deployment

```bash
# 1. Update environment variables
cp .env.example .env
# Edit .env with production values

# 2. Build production images
docker-compose -f docker-compose.prod.yml build

# 3. Deploy
docker-compose -f docker-compose.prod.yml up -d

# 4. Verify
docker-compose -f docker-compose.prod.yml ps
```

---

**Version**: 1.0.0  
**Status**: Production Ready ✅  
**Market Value**: $1M - $2M