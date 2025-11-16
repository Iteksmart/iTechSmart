# 🚀 iTechSmart Suite - Quick Start Guide

## ✅ Prerequisites Check

Before starting, ensure you have:
- [ ] Docker Desktop installed and running
- [ ] Docker Compose v2.0+
- [ ] 8GB+ RAM available
- [ ] 50GB+ free disk space
- [ ] GitHub account with access to ghcr.io

---

## 🎯 Quick Start Options

### Option 1: Deploy Single Product (5 minutes)

**Step 1: Login to GitHub Container Registry**
```bash
docker login ghcr.io
# Username: your-github-username
# Password: your-personal-access-token
```

**Step 2: Run deployment script**
```bash
# Clone repository
git clone https://github.com/Iteksmart/iTechSmart.git
cd iTechSmart

# Make scripts executable
chmod +x scripts/*.sh

# Deploy a product (example: iTechSmart Ninja)
./scripts/deploy-single-product.sh itechsmart-ninja 8001 3001
```

**Step 3: Access your product**
- Frontend: http://localhost:3001
- Backend: http://localhost:8001
- API Docs: http://localhost:8001/docs

---

### Option 2: Test All Products (2 minutes)

**Verify all 35 products have Docker images:**
```bash
./scripts/test-all-products.sh
```

This will check if all Docker images are available and generate a test report.

---

### Option 3: Deploy Full Suite (20 minutes)

**Deploy all 35 products at once:**
```bash
./scripts/deploy-full-suite.sh
```

**Access products:**
- iTechSmart Ninja: http://localhost:3001
- ProofLink: http://localhost:3002
- PassPort: http://localhost:3003
- [Products 4-35]: http://localhost:3004-3035

---

### Option 4: Run Product Demo (3 minutes)

**Automated demo for any product:**
```bash
./scripts/demo-product.sh itechsmart-ninja 3001
```

This will:
1. Start the product if not running
2. Open frontend in browser
3. Test backend health
4. Show API documentation
5. Display logs

---

## 📚 Available Products (35 Total)

### Core Products
1. **iTechSmart Ninja** - AI Agent (Port 3001)
2. **ProofLink** - Document Verification (Port 3002)
3. **PassPort** - Identity Management (Port 3003)
4. **ImpactOS** - Impact Measurement (Port 3004)
5. **LegalAI Pro** - Legal Software (Port 3005)

### Integration & Data
6. **iTechSmart Enterprise** - Integration Hub (Port 3006)
7. **iTechSmart HL7** - Medical Data Integration (Port 3007)
8. **iTechSmart DataFlow** - Data Pipeline (Port 3008)
9. **iTechSmart Connect** - API Management (Port 3009)
10. **iTechSmart Data Platform** - Data Governance (Port 3010)

### Analytics & Monitoring
11. **iTechSmart Analytics** - ML Analytics (Port 3011)
12. **iTechSmart Pulse** - Real-Time Analytics (Port 3012)
13. **iTechSmart Observatory** - APM Platform (Port 3013)
14. **iTechSmart Sentinel** - Observability (Port 3014)

### Security & Compliance
15. **iTechSmart Shield** - Cybersecurity (Port 3015)
16. **iTechSmart Vault** - Secrets Management (Port 3016)
17. **iTechSmart Compliance** - Compliance Management (Port 3017)
18. **iTechSmart Citadel** - Digital Infrastructure (Port 3018)

### Development & Operations
19. **iTechSmart DevOps** - CI/CD Automation (Port 3019)
20. **iTechSmart Cloud** - Multi-Cloud Management (Port 3020)
21. **iTechSmart Forge** - Low-Code Builder (Port 3021)
22. **iTechSmart Sandbox** - Code Execution (Port 3022)
23. **iTechSmart Mobile** - Mobile Development (Port 3023)

### AI & Automation
24. **iTechSmart AI** - AI/ML Platform (Port 3024)
25. **iTechSmart Copilot** - AI Assistant (Port 3025)
26. **iTechSmart Workflow** - Process Automation (Port 3026)

### Business Operations
27. **iTechSmart Marketplace** - App Store (Port 3027)
28. **iTechSmart Customer Success** - Customer Success (Port 3028)
29. **iTechSmart Notify** - Omnichannel Notifications (Port 3029)
30. **iTechSmart Ledger** - Blockchain & Audit (Port 3030)

### Specialized Tools
31. **iTechSmart Supreme Plus** - Auto-Remediation (Port 3031)
32. **iTechSmart Port Manager** - Port Management (Port 3032)
33. **iTechSmart MDM Agent** - Deployment Orchestrator (Port 3033)
34. **iTechSmart QA/QC** - Quality Assurance (Port 3034)
35. **iTechSmart Think-Tank** - Internal Development (Port 3035)

---

## 🛠️ Common Commands

### View Running Services
```bash
docker ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Stop Services
```bash
# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Restart Services
```bash
docker-compose restart
```

### Check Resource Usage
```bash
docker stats
```

---

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Out of Memory
```bash
# Check memory usage
docker stats

# Increase Docker memory limit
# Docker Desktop > Settings > Resources > Memory
```

### Image Pull Failed
```bash
# Re-authenticate
docker login ghcr.io

# Pull specific image
docker pull ghcr.io/iteksmart/itechsmart-ninja-backend:main
```

### Service Not Starting
```bash
# Check logs
docker-compose logs backend

# Restart service
docker-compose restart backend

# Rebuild and restart
docker-compose up -d --force-recreate backend
```

---

## 📖 Full Documentation

For complete documentation, see:
- **[DEPLOYMENT_AND_DEMO_GUIDE.md](DEPLOYMENT_AND_DEMO_GUIDE.md)** - Complete deployment guide
- **[SUCCESS_REPORT_100_PERCENT.md](SUCCESS_REPORT_100_PERCENT.md)** - Build system status
- **[COMPLETE_PRODUCT_STATUS_REPORT.md](COMPLETE_PRODUCT_STATUS_REPORT.md)** - Product status

---

## 🎉 Success Indicators

Your deployment is successful when:
- [ ] Docker containers are running (`docker ps`)
- [ ] Frontend loads in browser (http://localhost:3001)
- [ ] Backend health check passes (http://localhost:8001/health)
- [ ] API docs are accessible (http://localhost:8001/docs)
- [ ] No errors in logs (`docker-compose logs`)

---

## 🆘 Need Help?

1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs: `docker-compose logs -f`
3. Verify system requirements
4. Check GitHub Issues: https://github.com/Iteksmart/iTechSmart/issues

---

## 🚀 Next Steps

After successful deployment:
1. ✅ Test core features
2. ✅ Configure integrations
3. ✅ Set up monitoring
4. ✅ Deploy to production
5. ✅ Scale as needed

---

**Last Updated**: 2025-11-16  
**Version**: 1.0.0  
**Status**: Production Ready ✅