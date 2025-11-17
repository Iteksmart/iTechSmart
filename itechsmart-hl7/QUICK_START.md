# iTechSmart HL7 - Quick Start Guide

Get up and running with iTechSmart HL7 in under 10 minutes!

---

## 🚀 **Fastest Way to Start (5 minutes)**

### Prerequisites
- Docker Desktop installed
- 8GB RAM available
- 10GB disk space

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-org/itechsmart-hl7.git
cd itechsmart-hl7

# 2. Start all services
cd deployment
docker-compose up -d

# 3. Wait for services to start (30 seconds)
docker-compose ps

# 4. Open your browser
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

### Default Login
- **Username:** `admin`
- **Password:** `admin123`

**That's it! You're running iTechSmart HL7!** 🎉

---

## 📋 **What's Running?**

After `docker-compose up -d`, you have:

✅ **PostgreSQL** - Database (port 5432)  
✅ **Redis** - Cache (port 6379)  
✅ **Backend API** - FastAPI (port 8000)  
✅ **Frontend** - React app (port 3000)  
✅ **Nginx** - Reverse proxy (port 80)  
✅ **Prometheus** - Metrics (port 9090)  
✅ **Grafana** - Dashboards (port 3001)  
✅ **Backup Service** - Automated backups  

---

## 🎯 **First Steps**

### 1. Explore the Dashboard
- Go to http://localhost:3000
- Login with admin/admin123
- View the main dashboard

### 2. Check API Documentation
- Go to http://localhost:8000/docs
- Browse 62+ API endpoints
- Try the interactive API explorer

### 3. View Monitoring
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3001 (admin/admin123)

### 4. Test Features

**Add a Patient:**
```bash
curl -X POST http://localhost:8000/api/patients \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mrn": "MRN-123456",
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1980-01-01",
    "gender": "male"
  }'
```

**Check Drug Interactions:**
```bash
curl -X POST http://localhost:8000/api/clinicals/drug-check \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "new_medication": "warfarin",
    "current_medications": ["aspirin"],
    "allergies": ["penicillin"]
  }'
```

---

## 🧪 **Generate Test Data**

```bash
# Generate 50 test patients with complete medical records
cd scripts
python generate_test_data.py

# This creates:
# - test_data_complete.json (all data)
# - test_data_patients.json (patient demographics)
# - test_data_hl7_messages.txt (HL7 messages)
# - test_data_fhir_bundle.json (FHIR resources)
```

---

## ⚡ **Run Load Tests**

```bash
cd scripts
python load_test.py

# Tests:
# - Light load (10 concurrent requests)
# - Medium load (50 concurrent requests)
# - Heavy load (100 concurrent requests)
# - Stress test (200 concurrent requests)
```

---

## 🛠️ **Common Commands**

### Docker Compose

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Restart a service
docker-compose restart backend

# Check status
docker-compose ps

# View resource usage
docker stats
```

### Database

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U itechsmart -d itechsmart_hl7

# Run migrations
docker-compose exec backend alembic upgrade head

# Create backup
docker-compose exec backup /backup.sh

# Restore backup
./deployment/restore.sh /backups/postgres_20250115.sql.gz
```

### Logs

```bash
# Backend logs
docker-compose logs -f backend

# All logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100 backend
```

---

## 🔧 **Configuration**

### Environment Variables

Edit `deployment/.env`:

```bash
# Database
DATABASE_PASSWORD=your-secure-password

# Redis
REDIS_PASSWORD=your-secure-password

# Security
SECRET_KEY=your-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-min-32-chars

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# EMR Credentials
EPIC_CLIENT_ID=your-epic-client-id
EPIC_CLIENT_SECRET=your-epic-client-secret
```

### Restart After Changes

```bash
docker-compose down
docker-compose up -d
```

---

## 🐛 **Troubleshooting**

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Check disk space
df -h

# Check Docker resources
docker system df

# Clean up
docker system prune -a
```

### Can't Connect to Database

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Frontend Not Loading

```bash
# Check if frontend is running
docker-compose ps frontend

# Check logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend
```

### API Errors

```bash
# Check backend logs
docker-compose logs backend

# Check if backend is healthy
curl http://localhost:8000/health

# Restart backend
docker-compose restart backend
```

---

## 📚 **Next Steps**

### Learn More
1. **[User Guide](docs/USER_GUIDE.md)** - Complete user manual
2. **[API Documentation](docs/API_DOCUMENTATION.md)** - API reference
3. **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Production deployment

### Configure EMR Connections
1. Go to http://localhost:3000/connections
2. Click "Add Connection"
3. Select EMR system (Epic, Cerner, etc.)
4. Enter credentials
5. Test connection

### Set Up Workflows
1. Go to http://localhost:3000/workflows
2. Click "Create Workflow"
3. Select template (Admission, Discharge, Sepsis)
4. Enter patient ID
5. Start workflow

### Configure Monitoring
1. Go to http://localhost:3001 (Grafana)
2. Login: admin/admin123
3. Import dashboards from `deployment/grafana/dashboards/`
4. Configure alerts

---

## 🎓 **Key Features to Try**

### 1. Drug Interaction Checking
- Navigate to "Drug Checker"
- Enter a medication
- Add current medications and allergies
- View interaction results

### 2. AI Clinical Insights
- Navigate to "AI Insights"
- Select "Sepsis Risk Prediction"
- Enter vital signs and lab results
- View risk assessment

### 3. Clinical Workflows
- Navigate to "Workflows"
- Create a new workflow
- Complete workflow steps
- Track progress

### 4. Care Coordination
- Navigate to "Care Coordination"
- Create tasks
- Assign to team members
- Create handoffs

---

## 💡 **Tips**

### Performance
- Use Redis caching for frequently accessed data
- Enable connection pooling for database
- Monitor resource usage with Grafana

### Security
- Change default passwords immediately
- Use strong passwords (12+ characters)
- Enable HTTPS in production
- Rotate secrets every 90 days

### Backup
- Backups run daily at 2 AM
- 30-day retention by default
- Test restore procedures regularly
- Store backups offsite

---

## 🆘 **Getting Help**

### Documentation
- **User Guide:** [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- **API Docs:** [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- **Deployment:** [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

### Support
- **Email:** support@itechsmart.dev
- **Phone:** 1-800-ITECH-HL7
- **Chat:** Available 24/7 in app
- **Docs:** https://docs.itechsmart.dev

### Community
- **GitHub:** https://github.com/itechsmart/hl7
- **Slack:** #itechsmart-community
- **Forum:** https://community.itechsmart.dev

---

## ✅ **Checklist**

Before going to production:

- [ ] Change all default passwords
- [ ] Configure EMR connections
- [ ] Set up SSL/TLS certificates
- [ ] Configure backup schedule
- [ ] Set up monitoring alerts
- [ ] Test disaster recovery
- [ ] Train users
- [ ] Review security checklist
- [ ] Load test the system
- [ ] Document custom configurations

---

## 🎉 **You're Ready!**

You now have a fully functional healthcare integration platform running locally!

**Next:** Deploy to production using the [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)

---

**Questions?** Contact support@itechsmart.dev

**Last Updated:** January 15, 2025