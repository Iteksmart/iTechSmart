# 🚀 Quick Deployment Guide - iTechSmart Portfolio

**Get any project running in under 5 minutes!**

---

## 📋 Prerequisites

Before deploying any project, ensure you have:

- ✅ Docker & Docker Compose installed
- ✅ Git installed
- ✅ 8GB+ RAM available
- ✅ 20GB+ disk space

---

## 🎯 Choose Your Project

### Option 1: ProofLink.AI (Document Verification)
**Best for:** Document verification, blockchain proof-of-existence  
**Market:** Legal, education, certification  
**Revenue Potential:** High  

### Option 2: iTechSmart Ninja (AI Agent Platform)
**Best for:** AI automation, developer tools  
**Market:** Developers, enterprises  
**Revenue Potential:** Very High  

### Option 3: ImpactOS (Impact Measurement)
**Best for:** Non-profits, social enterprises  
**Market:** NGOs, foundations, CSR  
**Revenue Potential:** High  

### Option 4: iTechSmart HL7 (Healthcare Integration)
**Best for:** Healthcare IT, EMR integration  
**Market:** Hospitals, clinics, health tech  
**Revenue Potential:** Very High  

### Option 5: PassPort (Identity Management)
**Best for:** Identity verification, KYC  
**Market:** Fintech, enterprises  
**Revenue Potential:** High  

### Option 6: iTechSmart Supreme (Self-Healing Infrastructure)
**Best for:** DevOps, IT operations  
**Market:** Enterprises, MSPs  
**Revenue Potential:** High  

### Option 7: iTechSmart Enterprise (Enterprise Management)
**Best for:** Business operations, ERP  
**Market:** SMBs, enterprises  
**Revenue Potential:** Medium  

**Best for:** Fashion tech, e-commerce  
**Market:** Consumers, retailers  
**Revenue Potential:** Medium  

---

## 🚀 Deployment Steps (Universal)

### Step 1: Navigate to Project
```bash
cd /workspace/<project-name>
```

**Project Names:**
- `prooflink` - ProofLink.AI
- `itechsmart-ninja` - iTechSmart Ninja
- `itechsmart-impactos` - ImpactOS
- `itechsmart-hl7` - iTechSmart HL7
- `passport` - PassPort
- `itechsmart_supreme` - iTechSmart Supreme
- `itechsmart-enterprise` - iTechSmart Enterprise

### Step 2: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with your settings
nano .env  # or vim .env
```

**Key Variables to Set:**
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `SECRET_KEY` - Generate a secure key
- `API_KEYS` - Third-party service keys

### Step 3: Start Services
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Step 4: Initialize Database
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create admin user (if applicable)
docker-compose exec backend python scripts/create_admin.py
```

### Step 5: Access Application
```bash
# Frontend (Web Apps)
http://localhost:3000

# Backend API
http://localhost:8000

# API Documentation
http://localhost:8000/docs
```

---

## 📦 Project-Specific Instructions

### ProofLink.AI
```bash
cd /workspace/prooflink
cp .env.example .env
# Edit .env with your settings
docker-compose up -d
docker-compose exec backend alembic upgrade head

# Access at:
# Frontend: http://localhost:3000
# API: http://localhost:8000/docs
```

### iTechSmart Ninja
```bash
cd /workspace/itechsmart-ninja
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit .env files
docker-compose up -d

# Create founder account
docker-compose exec backend python scripts/create_founder.py

# Access at:
# Landing: http://localhost:3000
# Dashboard: http://localhost:3000/dashboard.html
# API: http://localhost:8000/docs
```

### ImpactOS
```bash
cd /workspace/itechsmart-impactos
cp .env.example .env
# Edit .env
docker-compose up -d
docker-compose exec backend python manage.py migrate

# Access at:
# Frontend: http://localhost:3000
# API: http://localhost:8000
```

### iTechSmart HL7
```bash
cd /workspace/itechsmart-hl7
cp .env.example .env
# Edit .env with EMR credentials
docker-compose up -d
docker-compose exec backend alembic upgrade head

# Access at:
# Dashboard: http://localhost:3000
# API: http://localhost:8000/docs
# Monitoring: http://localhost:9090 (Prometheus)
# Grafana: http://localhost:3001
```

### PassPort
```bash
cd /workspace/passport
cp .env.example .env
# Edit .env
docker-compose up -d
docker-compose exec backend alembic upgrade head

# Access at:
# Frontend: http://localhost:3000
# API: http://localhost:8000/docs
```

### iTechSmart Supreme (CLI Tool)
```bash
cd /workspace/itechsmart_supreme
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your settings

# Install dependencies
pip install -r requirements.txt

# Run the tool
python main.py

# Or use Docker
docker-compose up -d
```

### iTechSmart Enterprise
```bash
cd /workspace/itechsmart-enterprise
cp .env.example .env
# Edit .env
docker-compose up -d
docker-compose exec backend alembic upgrade head

# Access at:
# Frontend: http://localhost:3000
# API: http://localhost:8000/docs
```

```bash

# Backend
cp backend/.env.example backend/.env
docker-compose up -d backend

# Mobile App (React Native)
cd frontend
npm install
npm start

# For iOS
npm run ios

# For Android
npm run android

# API: http://localhost:8000/docs
```

---

## 🔧 Common Commands

### View Logs
```bash
docker-compose logs -f [service-name]
```

### Restart Services
```bash
docker-compose restart
```

### Stop Services
```bash
docker-compose down
```

### Rebuild Services
```bash
docker-compose up -d --build
```

### Access Database
```bash
docker-compose exec postgres psql -U postgres -d dbname
```

### Access Redis
```bash
docker-compose exec redis redis-cli
```

### Run Tests
```bash
docker-compose exec backend pytest
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart database
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Frontend Not Loading
```bash
# Check if frontend is running
docker-compose ps frontend

# Rebuild frontend
docker-compose up -d --build frontend

# Check logs
docker-compose logs frontend
```

### Permission Errors
```bash
# Fix permissions
sudo chown -R $USER:$USER .

# Or run with sudo
sudo docker-compose up -d
```

---

## 📊 Monitoring & Health Checks

### Check Service Health
```bash
# All services
docker-compose ps

# Specific service
docker-compose ps backend
```

### API Health Check
```bash
curl http://localhost:8000/health
```

### Database Health
```bash
docker-compose exec postgres pg_isready
```

### Redis Health
```bash
docker-compose exec redis redis-cli ping
```

---

## 🔒 Security Checklist

Before deploying to production:

- [ ] Change all default passwords
- [ ] Generate new SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up backup system
- [ ] Enable monitoring/logging
- [ ] Review security settings
- [ ] Update dependencies
- [ ] Configure rate limiting
- [ ] Set up error tracking

---

## 📈 Scaling Tips

### Horizontal Scaling
```yaml
# In docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
```

### Load Balancing
```bash
# Use nginx or traefik
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Database Optimization
```bash
# Increase connection pool
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
```

---

## 🎯 Next Steps After Deployment

1. **Test Everything**
   - Create test accounts
   - Test all features
   - Check API endpoints
   - Verify integrations

2. **Configure Monitoring**
   - Set up alerts
   - Configure logging
   - Enable metrics
   - Set up dashboards

3. **Backup Setup**
   - Database backups
   - File backups
   - Configuration backups
   - Disaster recovery plan

4. **Documentation**
   - Update API docs
   - Create user guides
   - Document processes
   - Train team members

5. **Marketing Launch**
   - Announce launch
   - Reach out to customers
   - Start marketing campaigns
   - Gather feedback

---

## 📞 Support & Resources

### Documentation
- Project README files
- API documentation at `/docs`
- User manuals in `/docs` folder
- Deployment guides

### Community
- GitHub Issues
- Discord/Slack channels
- Email support
- Video tutorials

### Professional Services
- Custom deployment
- Training sessions
- Consulting services
- Priority support

---

## 🎉 Success!

Once deployed, you should see:
- ✅ Frontend accessible at http://localhost:3000
- ✅ Backend API at http://localhost:8000
- ✅ API docs at http://localhost:8000/docs
- ✅ All services running (docker-compose ps)
- ✅ Database connected
- ✅ Redis connected

**Congratulations! Your iTechSmart project is now running!** 🚀

---

*Quick Deployment Guide - iTechSmart Portfolio*  
*Last Updated: November 12, 2025*  
*For detailed instructions, see project-specific README files*