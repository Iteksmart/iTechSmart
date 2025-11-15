# iTechSmart DataFlow - Quick Reference

## 🚀 Quick Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart Services
```bash
docker-compose restart
docker-compose restart backend
```

### Check Status
```bash
docker-compose ps
```

---

## 🌐 Access URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **MinIO Console**: http://localhost:9001
  - Username: minioadmin
  - Password: minioadmin

---

## 📡 API Quick Reference

### Health Check
```bash
curl http://localhost:8000/health
```

### List Pipelines
```bash
curl http://localhost:8000/api/v1/pipelines
```

### Create Pipeline
```bash
curl -X POST http://localhost:8000/api/v1/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Pipeline",
    "type": "batch",
    "source": {
      "type": "postgresql",
      "config": {"host": "localhost", "database": "test"}
    },
    "destination": {
      "type": "s3",
      "config": {"bucket": "test-bucket"}
    }
  }'
```

### List Connectors
```bash
curl http://localhost:8000/api/v1/connectors
```

### Get Metrics
```bash
curl http://localhost:8000/api/v1/monitoring/metrics
```

---

## 🔧 Configuration

### Backend Environment
Edit `backend/.env`:
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/dataflow
REDIS_URL=redis://redis:6379/0
KAFKA_BOOTSTRAP_SERVERS=["kafka:9092"]
```

### Frontend Environment
Frontend uses Vite environment variables:
```bash
VITE_API_URL=http://localhost:8000
```

---

## 🐛 Troubleshooting

### Services Won't Start
```bash
docker-compose down -v
docker-compose up -d
```

### Check Logs
```bash
docker-compose logs backend
docker-compose logs postgres
```

### Database Issues
```bash
docker exec -it dataflow-postgres psql -U dataflow
```

### Clear Everything
```bash
docker-compose down -v
docker system prune -a
docker-compose up -d
```

---

## 📊 Monitoring

### Check Service Health
```bash
curl http://localhost:8000/health
```

### View Metrics
```bash
curl http://localhost:8000/api/v1/monitoring/metrics
```

### Check Resource Usage
```bash
docker stats
```

---

## 🔐 Security

### Change Default Passwords
Edit `backend/.env`:
```bash
SECRET_KEY=your-strong-secret-key
DATABASE_PASSWORD=strong-password
```

### Enable SSL
Use nginx or traefik as reverse proxy with SSL certificates.

---

## 📚 Documentation

- **Full README**: README.md
- **Deployment Guide**: DEPLOYMENT.md
- **Architecture**: ../ARCHITECTURE_INTEGRATION_PLAN.md
- **API Docs**: http://localhost:8000/docs

---

## 🆘 Support

- **Email**: support@itechsmart.dev
- **Docs**: http://localhost:8000/docs
- **GitHub**: https://github.com/itechsmart

---

**Quick Reference v1.0**