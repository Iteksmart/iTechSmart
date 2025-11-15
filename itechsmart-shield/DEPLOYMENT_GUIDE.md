# 🚀 iTechSmart Shield - Deployment Guide

## 📋 Prerequisites

### System Requirements:
- **OS:** Linux (Ubuntu 20.04+ recommended)
- **Python:** 3.11+
- **Database:** PostgreSQL 14+
- **Memory:** 4GB minimum, 8GB recommended
- **CPU:** 2 cores minimum, 4 cores recommended
- **Storage:** 50GB minimum

### Dependencies:
- Docker & Docker Compose (for containerized deployment)
- PostgreSQL
- Redis (for caching)
- Python packages (see requirements.txt)

---

## 🔧 Installation

### 1. Clone Repository

```bash
git clone https://github.com/itechsmart/shield.git
cd itechsmart-shield
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/shield

# Service Configuration
SERVICE_NAME=shield-main
SERVICE_PORT=8007
API_KEY=your-secure-api-key

# Integration (for integrated mode)
HUB_URL=http://localhost:8000
STANDALONE_MODE=false

# Security
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key

# AI Configuration
AI_PROVIDER=openai
AI_API_KEY=your-ai-api-key

# Threat Detection
AUTO_BLOCK_ENABLED=true
AUTO_RESPONSE_ENABLED=true
DETECTION_SENSITIVITY=0.7

# Compliance
COMPLIANCE_FRAMEWORKS=SOC2,ISO27001,GDPR,HIPAA
```

### 4. Initialize Database

```bash
# Run migrations
alembic upgrade head

# Seed initial data (optional)
python scripts/seed_data.py
```

---

## 🐳 Docker Deployment

### Standalone Mode

```yaml
# docker-compose.yml
version: '3.8'

services:
  shield:
    image: itechsmart/shield:latest
    ports:
      - "8007:8000"
    environment:
      - STANDALONE_MODE=true
      - DATABASE_URL=postgresql://shield:password@db:5432/shield
    depends_on:
      - db
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=shield
      - POSTGRES_USER=shield
      - POSTGRES_PASSWORD=password
    volumes:
      - shield_data:/var/lib/postgresql/data

volumes:
  shield_data:
```

Run:
```bash
docker-compose up -d
```

### Integrated Mode

```yaml
# docker-compose.yml
version: '3.8'

services:
  shield:
    image: itechsmart/shield:latest
    ports:
      - "8007:8000"
    environment:
      - STANDALONE_MODE=false
      - HUB_URL=http://enterprise-hub:8000
      - DATABASE_URL=postgresql://shield:password@db:5432/shield
    depends_on:
      - db
      - enterprise-hub
  
  enterprise-hub:
    image: itechsmart/enterprise:latest
    ports:
      - "8000:8000"
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=shield
      - POSTGRES_USER=shield
      - POSTGRES_PASSWORD=password
    volumes:
      - shield_data:/var/lib/postgresql/data

volumes:
  shield_data:
```

---

## ☸️ Kubernetes Deployment

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: itechsmart-shield
spec:
  replicas: 3
  selector:
    matchLabels:
      app: itechsmart-shield
  template:
    metadata:
      labels:
        app: itechsmart-shield
    spec:
      containers:
      - name: shield
        image: itechsmart/shield:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: shield-secrets
              key: database-url
        - name: HUB_URL
          value: "http://enterprise-hub:8000"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: itechsmart-shield
spec:
  selector:
    app: itechsmart-shield
  ports:
  - port: 8007
    targetPort: 8000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f k8s/deployment.yaml
```

---

## 🔧 Configuration

### Threat Detection Configuration

```python
{
  "enabled": true,
  "detection_interval": 1,        # seconds
  "alert_threshold": 0.7,         # confidence threshold
  "auto_block": true,
  "auto_response": true
}
```

### AI Anomaly Detection Configuration

```python
{
  "enabled": true,
  "sensitivity": 0.7,             # 0-1
  "learning_period_days": 7,
  "min_samples": 100,
  "anomaly_threshold": 2.5        # standard deviations
}
```

### Incident Response Configuration

```python
{
  "auto_response_enabled": true,
  "auto_containment": true,
  "auto_remediation": false,      # requires approval
  "escalation_threshold": "high",
  "response_timeout": 300         # seconds
}
```

---

## 🔌 Integration Setup

### Register with Enterprise Hub

```bash
curl -X POST http://localhost:8000/api/integration/register \
  -H "Content-Type: application/json" \
  -d '{
    "service_type": "itechsmart-shield",
    "service_name": "shield-main",
    "base_url": "http://localhost:8007",
    "api_key": "shield-service-key",
    "capabilities": [
      "threat-detection",
      "vulnerability-scanning",
      "compliance-management"
    ]
  }'
```

### Enable Ninja Control

Shield automatically accepts Ninja control commands when integrated with the hub.

---

## 🧪 Testing

### Run Tests

```bash
# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration

# All tests
pytest
```

### Test Coverage

```bash
pytest --cov=app --cov-report=html
```

---

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8007/api/shield/health
```

### Dashboard Stats

```bash
curl http://localhost:8007/api/shield/dashboard/stats
```

### Threat Trends

```bash
curl http://localhost:8007/api/shield/dashboard/threat-trends?days=7
```

---

## 🔒 Security Best Practices

### 1. API Key Management
- Use strong, unique API keys
- Rotate keys regularly
- Store keys securely (use Vault)

### 2. Database Security
- Use strong passwords
- Enable SSL/TLS
- Regular backups
- Encrypt at rest

### 3. Network Security
- Use firewall rules
- Enable HTTPS only
- Restrict access by IP
- Use VPN for admin access

### 4. Monitoring
- Enable audit logging
- Monitor for anomalies
- Set up alerts
- Regular security reviews

---

## 🐛 Troubleshooting

### Issue: Service won't start

```bash
# Check logs
docker-compose logs shield

# Check database connection
psql -h localhost -U shield -d shield

# Verify environment variables
docker-compose config
```

### Issue: High false positive rate

```bash
# Adjust sensitivity
curl -X PUT http://localhost:8007/api/shield/config \
  -H "Content-Type: application/json" \
  -d '{"detection_sensitivity": 0.5}'
```

### Issue: Integration not working

```bash
# Verify hub connection
curl http://localhost:8000/api/integration/status

# Re-register with hub
curl -X POST http://localhost:8000/api/integration/register \
  -d @registration.json
```

---

## 📈 Performance Tuning

### For High Traffic:

```yaml
# Increase replicas
replicas: 5

# Increase resources
resources:
  requests:
    memory: "4Gi"
    cpu: "2000m"
  limits:
    memory: "8Gi"
    cpu: "4000m"

# Enable caching
REDIS_URL=redis://redis:6379
CACHE_ENABLED=true
```

### For Better Detection:

```python
# Increase sensitivity
detection_sensitivity: 0.8

# Reduce detection interval
detection_interval: 0.5  # seconds

# Enable deep scanning
deep_scan: true
```

---

## 🔄 Maintenance

### Regular Tasks:

1. **Update Threat Signatures** (Daily)
```bash
curl -X POST http://localhost:8007/api/shield/update-signatures
```

2. **Run Vulnerability Scans** (Weekly)
```bash
curl -X POST http://localhost:8007/api/shield/vulnerabilities/scan \
  -d '{"target": "all", "scan_type": "comprehensive"}'
```

3. **Compliance Assessment** (Monthly)
```bash
curl -X POST http://localhost:8007/api/shield/compliance/assess \
  -d '{"framework": "SOC2"}'
```

4. **Review Incidents** (Daily)
```bash
curl http://localhost:8007/api/shield/incidents?status=open
```

---

## 📞 Support

For deployment assistance:
- **Documentation**: https://docs.itechsmart.dev/shield
- **Support**: support@itechsmart.dev
- **Community**: https://community.itechsmart.dev

---

## 🎉 Conclusion

iTechSmart Shield is now deployed and protecting your infrastructure!

**Next Steps:**
1. ✅ Verify health status
2. ✅ Run initial vulnerability scan
3. ✅ Configure compliance frameworks
4. ✅ Set up monitoring and alerts
5. ✅ Integrate with other iTechSmart services

**Your infrastructure is now secured with enterprise-grade protection!** 🛡️