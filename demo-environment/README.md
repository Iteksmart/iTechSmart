# 🚀 iTechSmart Suite - Demo Environment

Complete demo environment for testing and evaluating the iTechSmart Suite.

---

## 📋 Overview

This demo environment provides:
- **License Server** - Centralized licensing and authentication
- **iTechSmart Ninja** - AI-powered IT automation
- **iTechSmart Supreme** - Enterprise platform
- **iTechSmart Citadel** - HL7 healthcare integration
- **iTechSmart Copilot** - AI assistant
- **Demo Landing Page** - Central access point with documentation

---

## 🎯 Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 1.29+
- 4GB RAM minimum (8GB recommended)
- 10GB free disk space

### Installation

```bash
# Navigate to demo environment directory
cd demo-environment

# Run setup script
./setup-demo.sh
```

The script will:
1. Check prerequisites
2. Create necessary directories
3. Generate configuration files
4. Pull and build Docker images
5. Start all services
6. Initialize sample data

### Access Demo

Once setup is complete, access the demo at:

**Main Demo Portal**: http://localhost

**Individual Services**:
- License Server: http://localhost:3000
- iTechSmart Ninja: http://localhost:3001
- iTechSmart Supreme: http://localhost:3002
- iTechSmart Citadel: http://localhost:3003
- iTechSmart Copilot: http://localhost:3004

---

## 🔐 Demo Credentials

### License Server Admin
- **Email**: admin@demo.com
- **Password**: demo123
- **API Key**: demo-api-key-12345

### Product Accounts

| Product | Email | Password |
|---------|-------|----------|
| **Ninja** | demo@ninja.com | ninja123 |
| **Supreme** | demo@supreme.com | supreme123 |
| **Citadel** | demo@citadel.com | citadel123 |
| **Copilot** | demo@copilot.com | copilot123 |

---

## 📚 Demo Features

### License Server
- Multi-tier licensing (Trial, Starter, Pro, Enterprise, Unlimited)
- Organization management
- User management
- API key generation
- Usage tracking
- Analytics dashboard

### iTechSmart Ninja
- AI-powered troubleshooting
- Automated incident resolution
- Knowledge base integration
- Ticket management
- Performance monitoring

### iTechSmart Supreme
- Enterprise dashboard
- Advanced analytics
- Custom workflows
- Integration hub
- Reporting tools

### iTechSmart Citadel
- HL7 v2.x message processing
- FHIR resource management
- Healthcare data exchange
- Compliance monitoring
- Audit logging

### iTechSmart Copilot
- AI-powered assistance
- Code generation
- Documentation help
- Troubleshooting guidance
- Best practices recommendations

---

## 🛠️ Management Commands

### Start Demo
```bash
docker-compose -f docker-compose.demo.yml up -d
```

### Stop Demo
```bash
docker-compose -f docker-compose.demo.yml down
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.demo.yml logs -f

# Specific service
docker-compose -f docker-compose.demo.yml logs -f license-server
```

### Restart Services
```bash
# All services
docker-compose -f docker-compose.demo.yml restart

# Specific service
docker-compose -f docker-compose.demo.yml restart license-server
```

### Check Status
```bash
docker-compose -f docker-compose.demo.yml ps
```

### Clean Up (Remove all data)
```bash
docker-compose -f docker-compose.demo.yml down -v
```

---

## 📊 Sample Data

The demo environment includes:

### Organizations
- **Demo Corp** (Enterprise tier)
  - 50 users
  - All products enabled
  - Full feature access

- **Test Inc** (Pro tier)
  - 25 users
  - Selected products
  - Standard features

### Users
- Admin users with full access
- Regular users with limited access
- API-only service accounts

### Sample Tickets/Issues
- Open incidents
- Resolved tickets
- Knowledge base articles
- Automation workflows

### HL7 Messages (Citadel)
- ADT messages (patient admission/discharge)
- ORU messages (lab results)
- ORM messages (orders)
- Sample FHIR resources

---

## 🔧 Configuration

### Environment Variables

Edit `.env` file to customize:

```env
# Database
POSTGRES_USER=demo
POSTGRES_PASSWORD=demo123
POSTGRES_DB=license_demo

# License Server
LICENSE_SERVER_PORT=3000
JWT_SECRET=your-jwt-secret
SECRET_KEY=your-secret-key

# Demo Credentials
ADMIN_EMAIL=admin@demo.com
ADMIN_PASSWORD=demo123
```

### Port Configuration

Default ports:
- 80: Nginx proxy (main access)
- 3000: License Server
- 3001: iTechSmart Ninja
- 3002: iTechSmart Supreme
- 3003: iTechSmart Citadel
- 3004: iTechSmart Copilot

To change ports, edit `docker-compose.demo.yml`:

```yaml
services:
  ninja-demo:
    ports:
      - "3001:3000"  # Change 3001 to your preferred port
```

---

## 🐛 Troubleshooting

### Services Won't Start

**Check Docker**:
```bash
docker --version
docker-compose --version
```

**Check logs**:
```bash
docker-compose -f docker-compose.demo.yml logs
```

**Restart Docker**:
```bash
# Linux
sudo systemctl restart docker

# macOS/Windows
# Restart Docker Desktop
```

### Port Conflicts

If ports are already in use:

1. Check what's using the port:
```bash
# Linux/macOS
lsof -i :3000

# Windows
netstat -ano | findstr :3000
```

2. Either stop the conflicting service or change the port in `docker-compose.demo.yml`

### Database Connection Issues

**Reset database**:
```bash
docker-compose -f docker-compose.demo.yml down -v
docker-compose -f docker-compose.demo.yml up -d
```

**Check database logs**:
```bash
docker-compose -f docker-compose.demo.yml logs demo-db
```

### Service Health Checks

**Check if services are responding**:
```bash
# License Server
curl http://localhost:3000/health

# Ninja
curl http://localhost:3001/health

# Supreme
curl http://localhost:3002/health
```

### Memory Issues

If services are slow or crashing:

1. **Check available memory**:
```bash
docker stats
```

2. **Increase Docker memory limit**:
   - Docker Desktop → Settings → Resources → Memory
   - Increase to at least 4GB (8GB recommended)

3. **Stop unnecessary services**:
```bash
# Stop specific service
docker-compose -f docker-compose.demo.yml stop copilot-demo
```

---

## 📈 Performance Optimization

### For Development
```bash
# Use development mode (faster rebuilds)
docker-compose -f docker-compose.demo.yml up --build
```

### For Production Testing
```bash
# Use production mode (optimized)
NODE_ENV=production docker-compose -f docker-compose.demo.yml up -d
```

### Resource Limits

Edit `docker-compose.demo.yml` to set limits:

```yaml
services:
  license-server:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

---

## 🔒 Security Notes

### Demo Environment Only

⚠️ **This is a demo environment with default credentials**

**DO NOT use in production!**

For production deployment:
1. Change all passwords
2. Generate secure API keys
3. Use environment-specific secrets
4. Enable SSL/TLS
5. Configure firewall rules
6. Set up proper authentication
7. Enable audit logging

### Secure Production Setup

See production deployment guides:
- [License Server Deployment](../license-server/docs/DEPLOYMENT_GUIDE.md)
- [Desktop Launcher Deployment](../desktop-launcher/docs/DEPLOYMENT_GUIDE.md)
- [Product-specific guides](../docs/)

---

## 📞 Support

### Documentation
- **Main Docs**: [GitHub Repository](https://github.com/Iteksmart/iTechSmart)
- **API Docs**: Available at `/api/docs` for each service
- **User Guides**: In each product's `/docs` folder

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/Iteksmart/iTechSmart/issues)
- **Email**: support@itechsmart.com
- **Sales**: sales@itechsmart.com

---

## 🎯 Next Steps

After exploring the demo:

1. **Review Documentation**
   - Read user guides for products of interest
   - Check API documentation
   - Review deployment guides

2. **Test Integrations**
   - Try API calls
   - Test authentication flows
   - Explore product features

3. **Plan Deployment**
   - Identify requirements
   - Plan infrastructure
   - Review security needs

4. **Contact Sales**
   - Discuss licensing
   - Get pricing information
   - Schedule implementation

---

## 📝 Demo Limitations

This demo environment has the following limitations:

- **Data Reset**: All data resets every 24 hours
- **Performance**: Not optimized for production load
- **Features**: Some enterprise features may be limited
- **Scale**: Limited to single-server deployment
- **Security**: Uses demo credentials (not production-ready)
- **Support**: Community support only

For production deployment, contact sales@itechsmart.com

---

## 🎉 Enjoy the Demo!

Explore the iTechSmart Suite and discover how it can transform your IT operations!

---

**Last Updated**: November 17, 2025  
**Version**: 1.0.0  
**Status**: Production Ready

---

**END OF README**