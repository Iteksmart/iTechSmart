# iTechSmart Platform - Quick Start Guide

## 🚀 Getting Started with the Expanded Platform

This guide will help you quickly understand and deploy the iTechSmart platform with all 18 products.

---

## 📦 What's Included

### Existing Products (8)
1. **Enterprise Hub** - Central management
2. **Ninja** - AI autonomous agent
3. **Supreme** - Infrastructure orchestration
4. **PassPort** - Identity & access management
5. **ProofLink** - Blockchain verification
6. **ImpactOS** - Analytics & insights
7. **HL7** - Healthcare integration

### New Products (10)
1. **DataFlow** ✅ - Data pipeline & ETL (COMPLETE)
2. **Shield** 🔄 - Cybersecurity (IN DEVELOPMENT)
3. **Pulse** ⏳ - Real-time analytics
4. **Connect** ⏳ - API management
5. **Workflow** ⏳ - Business automation
6. **Vault** ⏳ - Secrets management
7. **Notify** ⏳ - Notifications
8. **Ledger** ⏳ - Blockchain & audit
9. **Copilot** ⏳ - AI assistant
10. **Marketplace** ⏳ - App store

---

## 🏃 Quick Start - DataFlow (Available Now)

### Prerequisites
```bash
# Required
- Docker & Docker Compose
- 8GB RAM minimum
- 20GB disk space

# Optional
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
```

### Installation

1. **Navigate to DataFlow**
```bash
cd itechsmart-dataflow
```

2. **Start Services**
```bash
docker-compose up -d
```

3. **Access Applications**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

### First Pipeline

1. **Open Dashboard**
   - Navigate to http://localhost:3000

2. **Create Pipeline**
   - Click "Create Pipeline"
   - Name: "My First Pipeline"
   - Source: PostgreSQL
   - Destination: S3
   - Click "Save"

3. **Run Pipeline**
   - Click "Run" button
   - Monitor progress in real-time
   - View results in dashboard

---

## 🔧 Configuration

### Environment Variables

Create `.env` file in each product directory:

```bash
# DataFlow Example
APP_NAME=iTechSmart DataFlow
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@localhost:5432/dataflow
REDIS_URL=redis://localhost:6379/0

# Integration URLs
PASSPORT_API_URL=http://passport:8001/api/v1
ENTERPRISE_HUB_URL=http://enterprise-hub:8002/api/v1
NINJA_API_URL=http://ninja:8003/api/v1
```

### Database Setup

```bash
# PostgreSQL
docker exec -it dataflow-postgres psql -U dataflow

# Create tables
\i schema.sql

# Verify
\dt
```

---

## 🔗 Integration Setup

### 1. Connect to Passport (Authentication)

```python
# In your product's config
PASSPORT_API_URL = "http://passport:8001/api/v1"
PASSPORT_API_KEY = "your-api-key"

# Test connection
curl http://passport:8001/api/v1/health
```

### 2. Connect to Enterprise Hub (Monitoring)

```python
# In your product's config
ENTERPRISE_HUB_URL = "http://enterprise-hub:8002/api/v1"
ENTERPRISE_HUB_API_KEY = "your-api-key"

# Send metrics
curl -X POST http://enterprise-hub:8002/api/v1/metrics \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"product": "dataflow", "metric": "pipelines_active", "value": 10}'
```

### 3. Connect to Ninja (Auto-healing)

```python
# In your product's config
NINJA_API_URL = "http://ninja:8003/api/v1"
NINJA_API_KEY = "your-api-key"

# Register for auto-healing
curl -X POST http://ninja:8003/api/v1/register \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"product": "dataflow", "endpoints": ["/health", "/metrics"]}'
```

---

## 📊 Monitoring

### Health Checks

```bash
# Check all services
docker-compose ps

# Check specific service
curl http://localhost:8000/health

# Check logs
docker-compose logs -f backend
```

### Metrics

```bash
# View metrics
curl http://localhost:8000/api/v1/monitoring/metrics

# Prometheus metrics
curl http://localhost:9090/metrics
```

### Alerts

Configure alerts in Enterprise Hub:
```json
{
  "alert": "pipeline_failure",
  "condition": "status == 'failed'",
  "action": "notify_team",
  "channels": ["email", "slack"]
}
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Integration Tests

```bash
# Run all integration tests
docker-compose -f docker-compose.test.yml up
```

---

## 🚢 Deployment

### Development

```bash
# Start in development mode
docker-compose up
```

### Production

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to Kubernetes
kubectl apply -f k8s/
```

### Cloud Deployment

```bash
# AWS
aws ecs create-cluster --cluster-name itechsmart

# Azure
az aks create --name itechsmart --resource-group rg

# GCP
gcloud container clusters create itechsmart
```

---

## 📚 Documentation

### Product Documentation
- **DataFlow**: `/itechsmart-dataflow/README.md`
- **Architecture**: `/ARCHITECTURE_INTEGRATION_PLAN.md`
- **Progress**: `/EXPANSION_PROGRESS_REPORT.md`
- **Portfolio**: `/PORTFOLIO_SHOWCASE.md`

### API Documentation
- **DataFlow API**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### User Guides
- **Getting Started**: This document
- **User Manual**: `/docs/user-manual.md`
- **Developer Guide**: `/docs/developer-guide.md`

---

## 🆘 Troubleshooting

### Common Issues

**Issue**: Services won't start
```bash
# Solution: Check Docker resources
docker system df
docker system prune

# Restart services
docker-compose down
docker-compose up -d
```

**Issue**: Database connection failed
```bash
# Solution: Check database status
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

**Issue**: API returns 500 error
```bash
# Solution: Check logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Getting Help

1. **Check Logs**
   ```bash
   docker-compose logs -f
   ```

2. **Check Documentation**
   - README files in each product
   - API documentation at /docs

3. **Contact Support**
   - Email: support@itechsmart.dev
   - Slack: https://itechsmart.slack.com
   - GitHub Issues: https://github.com/itechsmart

---

## 🎓 Learning Resources

### Video Tutorials
- **DataFlow Overview**: 10 minutes
- **Creating Pipelines**: 15 minutes
- **Integration Setup**: 20 minutes
- **Advanced Features**: 30 minutes

### Webinars
- **Platform Overview**: Weekly on Tuesdays
- **Deep Dives**: Monthly on first Friday
- **Q&A Sessions**: Bi-weekly on Thursdays

### Certification
- **iTechSmart Certified User**: 2 hours
- **iTechSmart Certified Developer**: 8 hours
- **iTechSmart Certified Architect**: 16 hours

---

## 🔐 Security

### Best Practices

1. **Change Default Passwords**
   ```bash
   # Update .env file
   DATABASE_PASSWORD=strong-password-here
   REDIS_PASSWORD=strong-password-here
   ```

2. **Enable SSL/TLS**
   ```bash
   # Use HTTPS in production
   SSL_CERT=/path/to/cert.pem
   SSL_KEY=/path/to/key.pem
   ```

3. **Configure Firewall**
   ```bash
   # Allow only necessary ports
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw enable
   ```

4. **Regular Updates**
   ```bash
   # Update Docker images
   docker-compose pull
   docker-compose up -d
   ```

---

## 📈 Performance Optimization

### Database Optimization
```sql
-- Create indexes
CREATE INDEX idx_pipeline_status ON pipelines(status);
CREATE INDEX idx_pipeline_created ON pipelines(created_at);

-- Analyze tables
ANALYZE pipelines;
```

### Caching
```python
# Enable Redis caching
REDIS_CACHE_TTL = 3600  # 1 hour
ENABLE_CACHE = True
```

### Load Balancing
```yaml
# nginx.conf
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

---

## 🎯 Next Steps

### For Users
1. ✅ Complete DataFlow setup
2. 🔄 Create your first pipeline
3. ⏳ Explore integrations
4. ⏳ Set up monitoring
5. ⏳ Configure alerts

### For Developers
1. ✅ Review architecture documentation
2. 🔄 Set up development environment
3. ⏳ Explore API documentation
4. ⏳ Build custom connectors
5. ⏳ Contribute to marketplace

### For Administrators
1. ✅ Deploy infrastructure
2. 🔄 Configure security
3. ⏳ Set up monitoring
4. ⏳ Configure backups
5. ⏳ Plan scaling strategy

---

## 📞 Support & Community

### Support Channels
- **Email**: support@itechsmart.dev
- **Phone**: +1 (555) 123-4567
- **Portal**: https://support.itechsmart.dev

### Community
- **Slack**: https://itechsmart.slack.com
- **Forum**: https://community.itechsmart.dev
- **GitHub**: https://github.com/itechsmart

### Social Media
- **Twitter**: @iTechSmart
- **LinkedIn**: iTechSmart
- **YouTube**: iTechSmart Channel

---

## 🎉 Success!

You're now ready to use the iTechSmart platform! Start with DataFlow and explore the power of integrated enterprise software.

**Need help?** Contact us at support@itechsmart.dev

**Want to contribute?** Visit https://github.com/itechsmart

**Stay updated?** Follow us on Twitter @iTechSmart

---

**© 2025 iTechSmart. All rights reserved.**

**Happy Building! 🚀**