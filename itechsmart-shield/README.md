# iTechSmart Shield 🛡️

**Enterprise Security Operations Platform**

iTechSmart Shield is a comprehensive security operations platform that provides real-time threat detection, vulnerability management, compliance monitoring, and incident response capabilities.

## 🌟 Features

### Core Capabilities
- **Agent Security Monitoring** 🆕 - Real-time security monitoring of all deployed agents
- **Security Threat Detection** 🆕 - Automated detection of security issues (firewall, antivirus, updates)
- **Security Score Calculation** 🆕 - Comprehensive security scoring across all agents
- **Threat Intelligence** 🆕 - Intelligent threat classification and recommendations
- **Threat Detection** - Real-time monitoring and detection of security threats
- **Vulnerability Management** - Track and remediate security vulnerabilities with CVE integration
- **Compliance Management** - Monitor compliance across multiple frameworks (SOC2, ISO27001, GDPR, HIPAA)
- **Incident Response** - Manage security incidents from detection to resolution
- **Security Dashboard** - Comprehensive overview of your security posture
- **Settings & Configuration** - Flexible configuration for security policies and integrations

### Technical Features
- Real-time threat intelligence
- Automated vulnerability scanning
- Compliance assessment automation
- Incident timeline tracking
- SIEM integration support
- Multi-framework compliance monitoring
- Role-based access control
- Audit logging
- API-first architecture

## 🏗️ Architecture

### Technology Stack

**Backend:**
- FastAPI (Python 3.11)
- PostgreSQL 15 (Primary database)
- Redis (Caching & session management)
- Elasticsearch (Log aggregation & search)
- SQLAlchemy (ORM)

**Frontend:**
- React 18 with TypeScript
- Tailwind CSS
- React Router
- Lucide Icons
- Recharts (Data visualization)

**Infrastructure:**
- Docker & Docker Compose
- Nginx (Reverse proxy)
- Prometheus (Metrics)
- Grafana (Monitoring dashboards)

## 🚀 Quick Start

### Prerequisites
- Docker 24.0+
- Docker Compose 2.20+
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd itechsmart-shield
```

2. **Start the services**
```bash
docker-compose up -d
```

3. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Development Setup

**Backend Development:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend Development:**
```bash
cd frontend
npm install
npm start
```

## 📊 Database Schema

The platform uses PostgreSQL with the following main tables:
- `threats` - Security threat records
- `vulnerabilities` - CVE and vulnerability tracking
- `compliance_frameworks` - Compliance framework definitions
- `compliance_controls` - Individual compliance controls
- `incidents` - Security incident records
- `security_events` - Real-time security events
- `audit_logs` - System audit trail

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
DATABASE_URL=postgresql://shield_user:shield_pass_2025@localhost:5432/shield_db
REDIS_URL=redis://localhost:6379
ELASTICSEARCH_URL=http://localhost:9200
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development
```

**Frontend (.env):**
```env
REACT_APP_API_URL=http://localhost:8000
```

## 📡 API Endpoints

### Threats
- `GET /api/threats` - List all threats
- `POST /api/threats` - Create new threat
- `GET /api/threats/{id}` - Get threat details
- `PUT /api/threats/{id}` - Update threat
- `DELETE /api/threats/{id}` - Delete threat

### Vulnerabilities
- `GET /api/vulnerabilities` - List all vulnerabilities
- `POST /api/vulnerabilities` - Create new vulnerability
- `GET /api/vulnerabilities/{id}` - Get vulnerability details
- `PUT /api/vulnerabilities/{id}` - Update vulnerability

### Compliance
- `GET /api/compliance` - Get compliance overview
- `GET /api/compliance/frameworks` - List frameworks
- `GET /api/compliance/controls` - List controls
- `POST /api/compliance/assess` - Run compliance assessment

### Incidents
- `GET /api/incidents` - List all incidents
- `POST /api/incidents` - Create new incident
- `GET /api/incidents/{id}` - Get incident details
- `PUT /api/incidents/{id}` - Update incident status

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/recent-activity` - Get recent activity

## 🔐 Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Multi-factor authentication (MFA) support
- Session management with Redis

### Data Protection
- Encrypted data at rest
- TLS/SSL for data in transit
- Secure password hashing (bcrypt)
- API rate limiting
- CORS protection

### Compliance
- SOC2 Type II ready
- ISO 27001 aligned
- GDPR compliant
- HIPAA compatible
- PCI-DSS support

## 📈 Monitoring & Observability

### Metrics
- Prometheus metrics endpoint: `/metrics`
- Custom business metrics
- System health checks
- Performance monitoring

### Logging
- Structured logging with Loguru
- Elasticsearch log aggregation
- Real-time log streaming
- Audit trail logging

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Integration tests
docker-compose -f docker-compose.test.yml up
```

## 📦 Deployment

### Production Deployment

1. **Update environment variables**
```bash
cp .env.example .env
# Edit .env with production values
```

2. **Build production images**
```bash
docker-compose -f docker-compose.prod.yml build
```

3. **Deploy**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment
```bash
kubectl apply -f k8s/
```

## 🔄 Backup & Recovery

### Database Backup
```bash
docker exec shield-postgres pg_dump -U shield_user shield_db > backup.sql
```

### Database Restore
```bash
docker exec -i shield-postgres psql -U shield_user shield_db < backup.sql
```

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Architecture Guide](./docs/architecture.md)
- [Deployment Guide](./docs/deployment.md)
- [Security Best Practices](./docs/security.md)
- [Troubleshooting Guide](./docs/troubleshooting.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.itechsmart.dev/shield](https://docs.itechsmart.dev/shield)
- **Email**: support@itechsmart.dev
- **Issues**: [GitHub Issues](https://github.com/itechsmart/shield/issues)

## 🎯 Roadmap

### Version 2.0 (Q2 2025)
- [ ] AI-powered threat detection
- [ ] Advanced analytics dashboard
- [ ] Mobile application
- [ ] Integration marketplace
- [ ] Custom playbook automation

### Version 2.1 (Q3 2025)
- [ ] Multi-tenant support
- [ ] Advanced reporting engine
- [ ] Threat intelligence feeds
- [ ] Automated remediation
- [ ] Cloud security posture management

## 👥 Team

Developed by the iTechSmart Security Team

## 🙏 Acknowledgments

- FastAPI framework
- React community
- Security research community
- Open source contributors

---

**Market Value**: $1M - $2M  
**Status**: Production Ready  
**Version**: 1.0.0  
**Last Updated**: January 2025

For more information, visit [itechsmart.dev](https://itechsmart.dev)
## 🤖 Agent Integration

This product integrates with the iTechSmart Agent monitoring system through the License Server. The agent system provides:

- Real-time system monitoring
- Performance metrics collection
- Security status tracking
- Automated alerting

### Configuration

Set the License Server URL in your environment:

```bash
LICENSE_SERVER_URL=http://localhost:3000
```

The product will automatically connect to the License Server to access agent data and monitoring capabilities.



## 🚀 Upcoming Features (v1.4.0)

1. **Behavioral analysis and anomaly detection**
2. **Automated threat hunting capabilities**
3. **Integration with SIEM platforms**
4. **Threat intelligence feeds (real-time)**
5. **Advanced malware detection and prevention**
6. **Network traffic analysis and monitoring**
7. **Endpoint detection and response (EDR)**
8. **Security compliance automation**

**Product Value**: $2.5M  
**Tier**: 2  
**Total Features**: 8



## Coming in v1.5.0

**Release Date:** Q1 2025

### New Features

- AI-powered threat prediction
- Advanced behavioral analytics
- Automated incident response
- Enhanced EDR capabilities

### Enhancements

- Performance improvements across all modules
- Enhanced security features and compliance
- Improved user experience and interface
- Extended API capabilities and integrations
