# iTechSmart Citadel

**Sovereign Digital Infrastructure Platform**

Copyright (c) 2025 iTechSmart Inc.  
Launch Date: August 8, 2025

**Company Information**  
iTechSmart Inc. (C-Corp)  
1130 Ogletown Road, Suite 2  
Newark, DE 19711, USA  
Phone: 310-251-3969  
Website: https://itechsmart.dev  
Email: support@itechsmart.dev

**Leadership**  
Founder & CEO: DJuane Jackson

## Overview

iTechSmart Citadel is a sovereign digital infrastructure platform featuring post-quantum cryptography, immutable OS, SIEM/XDR capabilities, zero trust architecture, and comprehensive compliance management. Built for organizations requiring the highest levels of security and data sovereignty.

## Key Features

### 🔐 Post-Quantum Cryptography
- CRYSTALS-Kyber key encapsulation
- CRYSTALS-Dilithium digital signatures
- Quantum-resistant encryption algorithms
- Automated key rotation and management

### 🛡️ SIEM/XDR Integration
- Real-time security event monitoring
- Extended detection and response
- Automated threat correlation
- Incident response automation

### ✅ Compliance Management
- HIPAA, PCI-DSS, SOC2, ISO27001
- NIST Cybersecurity Framework
- GDPR compliance
- Automated compliance checking
- Real-time compliance scoring

### 🎯 Zero Trust Architecture
- Multi-factor authentication required
- Continuous verification
- Least privilege access
- Micro-segmentation
- Session timeout controls

### 🔍 Threat Intelligence
- Real-time threat indicator tracking
- Vulnerability management
- CVE tracking and scoring
- Automated threat feed updates
- Confidence-based threat scoring

### 💾 Immutable Backup
- Ransomware-proof backups
- AES-256 encryption
- 90-day retention
- Automated backup scheduling
- Point-in-time recovery

### 🌐 Network Security
- IDS/IPS integration
- Deep packet inspection
- Network flow analysis
- Suspicious activity detection
- Automated blocking

## Architecture

### Backend Components
- **FastAPI Application**: RESTful API server
- **CitadelEngine**: Core security engine
- **Database Models**: 15 comprehensive models
- **Integration Module**: Cross-product connectivity
- **API Modules**: Security, Compliance, Threats, Monitoring

### Frontend Components
- **React + TypeScript**: Modern web interface
- **5 Main Pages**: Dashboard, Security, Compliance, Threats, Infrastructure
- **Real-time Updates**: Live security monitoring
- **Dark Theme**: Security-focused UI design

### Database Schema
- SecurityEvent
- ThreatIntelligence
- CompliancePolicy
- ComplianceCheck
- InfrastructureAsset
- Vulnerability
- SecurityControl
- IncidentResponse
- AuditLog
- EncryptionKey
- NetworkFlow
- BackupJob
- SIEMAlert
- ZeroTrustPolicy
- HardwareSecurityModule

## Technology Stack

### Backend
- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis

### Frontend
- React 18
- TypeScript
- Vite
- TailwindCSS
- Recharts
- Axios

### Infrastructure
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7
- Nginx

## Quick Start

### Prerequisites
- Docker and Docker Compose
- 4GB RAM minimum
- 20GB disk space

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd itechsmart-citadel
```

2. Start the services:
```bash
docker-compose up -d
```

3. Access the application:
- Frontend: http://localhost:3035
- Backend API: http://localhost:8035
- API Documentation: http://localhost:8035/docs

## Configuration

Environment variables in `docker-compose.yml`:

```yaml
environment:
  DATABASE_URL: postgresql://citadel:citadel@postgres:5432/citadel
  REDIS_URL: redis://redis:6379/5
  PQC_ENABLED: "true"
  SIEM_ENABLED: "true"
  XDR_ENABLED: "true"
  ZERO_TRUST_ENABLED: "true"
  MFA_REQUIRED: "true"
  IMMUTABLE_BACKUP_ENABLED: "true"
```

## API Endpoints

### Security
- `POST /api/security/events` - Create security event
- `GET /api/security/events` - List security events
- `POST /api/security/events/{id}/respond` - Create incident response
- `GET /api/security/controls` - List security controls

### Compliance
- `POST /api/compliance/policies` - Create compliance policy
- `GET /api/compliance/policies` - List compliance policies
- `POST /api/compliance/policies/{id}/check` - Run compliance check
- `GET /api/compliance/frameworks/{framework}/score` - Get compliance score

### Threats
- `POST /api/threats/indicators` - Add threat indicator
- `GET /api/threats/indicators` - List threat indicators
- `GET /api/threats/indicators/check/{indicator}` - Check threat indicator
- `POST /api/threats/vulnerabilities` - Add vulnerability
- `GET /api/threats/vulnerabilities` - List vulnerabilities

### Monitoring
- `POST /api/monitoring/assets` - Create infrastructure asset
- `GET /api/monitoring/assets` - List infrastructure assets
- `POST /api/monitoring/network-flows` - Analyze network flow
- `POST /api/monitoring/backups` - Create backup job
- `POST /api/monitoring/encryption-keys/generate` - Generate encryption key

## Security Features

### Post-Quantum Algorithms
- **CRYSTALS-Kyber**: Key encapsulation mechanism
- **CRYSTALS-Dilithium**: Digital signature scheme
- **FALCON**: Compact digital signatures
- **SPHINCS+**: Stateless hash-based signatures

### Compliance Frameworks
- **HIPAA**: Healthcare data protection
- **PCI-DSS**: Payment card security
- **SOC2**: Service organization controls
- **ISO27001**: Information security management
- **NIST**: Cybersecurity framework
- **GDPR**: Data protection regulation

### Security Controls
- Firewall management
- IDS/IPS integration
- Web application firewall (WAF)
- Data loss prevention (DLP)
- Encryption at rest and in transit
- Multi-factor authentication
- SIEM integration
- EDR/XDR capabilities

## Integration with iTechSmart Suite

Citadel integrates with:
- **iTechSmart Hub**: Central management
- **iTechSmart Shield**: Security coordination
- **iTechSmart Supreme Plus**: Infrastructure remediation
- **iTechSmart Analytics**: Security metrics
- **iTechSmart Notify**: Alert notifications
- **iTechSmart Vault**: Key management

## Support

For support and documentation:
- User Guide: See USER_GUIDE.md
- Deployment Guide: See DEPLOYMENT_GUIDE.md
- Security Guide: See SECURITY_GUIDE.md
- API Documentation: http://localhost:8035/docs
- Website: https://itechsmart.dev
- Technical Support: support@itechsmart.dev
- Sales Inquiries: sales@itechsmart.dev
- Phone: 310-251-3969

**iTechSmart Inc.**  
1130 Ogletown Road, Suite 2  
Newark, DE 19711, USA



## 🚀 Upcoming Features (v1.4.0)

1. **Threat intelligence integration (MITRE ATT&CK)**
2. **Automated incident response playbooks**
3. **Zero-trust architecture implementation**
4. **Advanced forensics and investigation tools**
5. **Security orchestration and automation (SOAR)**
6. **Compliance automation for multiple frameworks**
7. **Vulnerability management and patching**
8. **Security posture scoring and benchmarking**

**Product Value**: $3.5M  
**Tier**: 1  
**Total Features**: 8



## Coming in v1.5.0

**Release Date:** Q1 2025

### New Features

- AI-powered threat hunting
- Advanced behavioral analytics
- Automated penetration testing
- Enhanced SOAR capabilities with 50+ integrations

### Enhancements

- Performance improvements across all modules
- Enhanced security features and compliance
- Improved user experience and interface
- Extended API capabilities and integrations

## License

Copyright (c) 2025 iTechSmart Inc. All rights reserved.

## Version

Version 1.0.0 - Launch Date: August 8, 2025
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

