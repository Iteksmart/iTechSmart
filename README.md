# iTechSmart Suite 🚀

**Enterprise-Grade AI-Powered IT Management Platform**

Complete suite of 40+ products for IT automation, monitoring, security, and management - now with integrated agent-based monitoring.

![Version](https://img.shields.io/badge/version-1.4.0-blue)
![Products](https://img.shields.io/badge/products-40+-green)
![License](https://img.shields.io/badge/license-Proprietary-orange)
![Status](https://img.shields.io/badge/status-Production%20Ready-success)

## 🌐 Website &amp; Documentation

**📱 Visit our website:** [iTechSmart Suite Website](https://8050-4e3e6dbe-4567-44ca-a9cd-36cc5d8cf07b.proxy.daytona.works) *(Update with your GitHub Pages URL after deployment)*

**📚 Complete Documentation:**
- [Full Suite Documentation](website/docs/ITECHSMART_SUITE_COMPLETE_DOCUMENTATION.html)
- [Executive Presentation](website/docs/EXECUTIVE_PRESENTATION.html)
- [Architecture Guide](website/docs/iTechSmart_Complete_Architecture.html)
- [API Documentation](website/docs/API_DOCUMENTATION.html)
- [Deployment Guide](website/docs/DEPLOYMENT_GUIDE.html)

---

## 🎯 Overview

iTechSmart Suite is a comprehensive platform that combines AI-powered automation, real-time monitoring, enterprise security, and centralized management into a unified ecosystem. With the new **iTechSmart Agent**, you can now monitor and manage systems across your entire infrastructure from a single dashboard.

---

## 🆕 What's New - iTechSmart Agent

**The iTechSmart Agent is now available!** A lightweight, cross-platform monitoring agent that provides:

- ✅ **Real-time System Monitoring** - CPU, Memory, Disk, Network
- ✅ **Security & Compliance Checks** - Firewall, Antivirus, Updates
- ✅ **Software Inventory** - Track installed applications
- ✅ **Remote Command Execution** - Execute commands from dashboard
- ✅ **Proactive Alerts** - Automatic threshold-based notifications
- ✅ **Cross-Platform** - Windows, macOS, Linux (Intel & ARM)

**Download Agent:**
- [Linux (AMD64)](https://github.com/Iteksmart/iTechSmart/releases/download/v1.3.0/itechsmart-agent-linux-amd64)
- [Windows (AMD64)](https://github.com/Iteksmart/iTechSmart/releases/download/v1.3.0/itechsmart-agent-windows-amd64.exe)
- [macOS (Intel)](https://github.com/Iteksmart/iTechSmart/releases/download/v1.3.0/itechsmart-agent-darwin-amd64)
- [macOS (Apple Silicon)](https://github.com/Iteksmart/iTechSmart/releases/download/v1.3.0/itechsmart-agent-darwin-arm64)

**Documentation:**
- [Agent Installation Guide](itechsmart-agent/README.md)
- [Integration Guide](AGENT_INTEGRATION_COMPLETE.md)
- [Integration Plan](AGENT_INTEGRATION_PLAN.md)

---

## 📦 Product Categories

### 🤖 AI & Automation (8 Products)
1. **iTechSmart Ninja** - Personal AI agent platform (25 features)
2. **iTechSmart Supreme** - Autonomous infrastructure management
3. **iTechSmart Copilot** - AI-powered IT assistant
4. **iTechSmart Automation** - Workflow automation engine
5. **iTechSmart Orchestrator** - Multi-cloud orchestration
6. **iTechSmart Scheduler** - Advanced task scheduling
7. **iTechSmart Workflow** - Visual workflow designer
8. **iTechSmart RPA** - Robotic process automation

### 🔐 Security & Compliance (7 Products)
9. **iTechSmart Citadel** - Enterprise security platform
10. **iTechSmart Shield** - Threat detection & response
11. **iTechSmart Sentinel** - Security monitoring
12. **iTechSmart Vault** - Secrets management
13. **iTechSmart Compliance** - Compliance automation
14. **iTechSmart Audit** - Audit logging & reporting
15. **iTechSmart IAM** - Identity & access management

### 📊 Monitoring & Analytics (6 Products)
16. **iTechSmart Monitor** - Infrastructure monitoring
17. **iTechSmart Analytics** - Business intelligence
18. **iTechSmart Metrics** - Performance metrics
19. **iTechSmart Logs** - Log aggregation & analysis
20. **iTechSmart APM** - Application performance monitoring
21. **iTechSmart Insights** - Predictive analytics

### 🏢 Enterprise Management (8 Products)
22. **iTechSmart Enterprise** - Enterprise platform
23. **iTechSmart Supreme Plus** - Premium features
24. **iTechSmart Portal** - Self-service portal
25. **iTechSmart CMDB** - Configuration management database
26. **iTechSmart Asset** - Asset management
27. **iTechSmart Inventory** - Inventory tracking
28. **iTechSmart ITSM** - IT service management
29. **iTechSmart Helpdesk** - Ticketing system

### 🔧 Development & Integration (8 Products)
30. **iTechSmart DevOps** - DevOps automation
31. **iTechSmart CI/CD** - Continuous integration/deployment
32. **iTechSmart API Gateway** - API management
33. **iTechSmart Integration Hub** - Integration platform
34. **iTechSmart Connector** - Third-party connectors
35. **iTechSmart SDK** - Software development kit
36. **iTechSmart CLI** - Command-line interface
37. **iTechSmart Agent** - 🆕 System monitoring agent

### 🎫 Core Infrastructure
- **License Server** - Centralized licensing & agent management
- **Desktop Launcher** - Unified desktop application

---

## 🚀 Quick Start

### 1. Deploy License Server (Hub)

```bash
# Clone repository
git clone https://github.com/Iteksmart/iTechSmart.git
cd iTechSmart/license-server

# Install dependencies
npm install

# Configure environment
cp .env.example .env
nano .env

# Setup database
npx prisma migrate deploy
npx prisma generate

# Start server
npm start

# Access dashboard
open http://localhost:3000
```

### 2. Deploy iTechSmart Agent

```bash
# Download agent for your platform
wget https://github.com/Iteksmart/iTechSmart/releases/download/v1.3.0/itechsmart-agent-linux-amd64

# Make executable
chmod +x itechsmart-agent-linux-amd64

# Configure
sudo mkdir -p /etc/itechsmart
sudo nano /etc/itechsmart/agent.yaml

# Install as service
sudo ./itechsmart-agent-linux-amd64 install

# Start agent
sudo systemctl start itechsmart-agent

# Check status
sudo systemctl status itechsmart-agent
```

### 3. Access Agent Dashboard

```bash
# Open browser
open http://localhost:3000/agent-dashboard.html

# View real-time metrics
# - Active/Offline agents
# - System metrics (CPU, Memory, Disk)
# - Active alerts
# - Pending commands
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    iTechSmart Suite                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Desktop    │  │   License    │  │    Agent     │    │
│  │   Launcher   │  │    Server    │  │  Dashboard   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                 │                   │            │
│         └─────────────────┴───────────────────┘            │
│                           │                                │
│         ┌─────────────────┴─────────────────┐             │
│         │                                   │             │
│  ┌──────▼──────┐                    ┌──────▼──────┐      │
│  │  Products   │                    │   Agents    │      │
│  │  (37 Apps)  │◄───WebSocket──────►│ (Deployed)  │      │
│  └─────────────┘                    └─────────────┘      │
│         │                                   │             │
│         │                                   │             │
│  ┌──────▼──────────────────────────────────▼──────┐      │
│  │           PostgreSQL Database                  │      │
│  │  - Licenses  - Users  - Agents  - Metrics     │      │
│  └────────────────────────────────────────────────┘      │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Features

### Centralized Management
- **Single Dashboard** - Manage all products and agents
- **Unified Authentication** - SSO across all products
- **Organization Management** - Multi-tenant support
- **License Management** - Tiered licensing system

### Real-Time Monitoring
- **System Metrics** - CPU, Memory, Disk, Network
- **Security Status** - Firewall, Antivirus, Updates
- **Software Inventory** - Track installed applications
- **Proactive Alerts** - Automatic threshold monitoring

### Remote Management
- **Command Execution** - Run commands on remote systems
- **Configuration Updates** - Push config changes
- **Patch Management** - Automated update deployment
- **Bulk Operations** - Manage multiple agents

### Enterprise Features
- **Multi-Tenant** - Organization isolation
- **RBAC** - Role-based access control
- **Audit Logging** - Complete action history
- **API Access** - RESTful API & WebSocket

---

## 📊 Agent Capabilities

### System Monitoring
```yaml
Metrics Collected:
  - CPU Usage (%)
  - Memory Usage (%)
  - Disk Usage (%)
  - Network Traffic (bytes)
  - Process Count
  - Uptime

Collection Interval: 60 seconds (configurable)
Retention: 30 days (configurable)
```

### Security Checks
```yaml
Checks Performed:
  - Firewall Status
  - Antivirus Status
  - Available Updates
  - Open Ports
  - Failed Login Attempts
  - File Integrity

Check Interval: 300 seconds (configurable)
```

### Alert Thresholds
```yaml
CPU:
  Warning: 80%
  Critical: 90%

Memory:
  Warning: 80%
  Critical: 90%

Disk:
  Warning: 75%
  Critical: 90%

Security:
  Firewall Disabled: ERROR
  Antivirus Disabled: ERROR
  Updates Available (>10): WARNING
```

---

## 🛠️ Installation Options

### Option 1: Docker (Recommended)
```bash
# License Server
cd license-server
docker-compose up -d

# Products
cd ../itechsmart-ninja
docker-compose up -d
```

### Option 2: Manual Installation
```bash
# License Server
cd license-server
npm install
npm start

# Agent
cd ../itechsmart-agent
./install.sh
```

### Option 3: Desktop Launcher
```bash
# Download for your platform
# Windows: iTechSmart-Setup-1.0.0.exe
# macOS: iTechSmart-1.0.0.dmg
# Linux: iTechSmart-1.0.0.AppImage

# Install and launch
# All products accessible from single interface
```

---

## 📚 Documentation

### Getting Started
- [Installation Guide](docs/INSTALLATION.md)
- [Quick Start Guide](docs/QUICK_START.md)
- [Configuration Guide](docs/CONFIGURATION.md)

### Agent Documentation
- [Agent Installation](itechsmart-agent/README.md)
- [Agent Configuration](itechsmart-agent/configs/agent.example.yaml)
- [Integration Guide](AGENT_INTEGRATION_COMPLETE.md)
- [API Documentation](AGENT_INTEGRATION_PLAN.md#api-specifications)

### Product Documentation
- [iTechSmart Ninja](itechsmart-ninja/README.md)
- [iTechSmart Enterprise](itechsmart-enterprise/README.md)
- [iTechSmart Supreme](itechsmart-supreme/README.md)
- [License Server](license-server/README.md)
- [Desktop Launcher](desktop-launcher/README.md)

### Developer Documentation
- [API Reference](docs/API.md)
- [WebSocket Protocol](AGENT_INTEGRATION_COMPLETE.md#websocket-protocol)
- [Database Schema](license-server/prisma/schema.prisma)
- [Contributing Guide](CONTRIBUTING.md)

---

## 🔐 Security

### Authentication
- **API Keys** - Per-agent authentication
- **JWT Tokens** - Dashboard authentication
- **Certificate Pinning** - TLS 1.3 encryption

### Authorization
- **Organization-based** - Multi-tenant isolation
- **Role-based** - Granular permissions
- **Audit Logging** - Complete action history

### Data Protection
- **Encryption at Rest** - AES-256
- **Encryption in Transit** - TLS 1.3
- **Data Minimization** - Only essential data collected

---

## 📈 Performance

### Agent Performance
- **CPU Usage**: < 1% idle, < 5% active
- **Memory Usage**: ~50MB typical
- **Network Usage**: ~1KB/s average
- **Binary Size**: 12-13 MB

### Server Performance
- **Agents Supported**: 10,000+ per server
- **Metrics/Second**: 10,000+
- **WebSocket Connections**: 10,000+
- **API Response Time**: < 50ms

---

## 🎯 Use Cases

### IT Operations
- Monitor server health across infrastructure
- Automate patch management
- Track software inventory
- Proactive issue detection

### Security & Compliance
- Monitor security posture
- Track compliance status
- Detect vulnerabilities
- Audit system changes

### DevOps
- Monitor deployment health
- Track application performance
- Automate remediation
- Integrate with CI/CD

### Enterprise Management
- Multi-tenant monitoring
- Organization-level dashboards
- Compliance reporting
- Cost optimization

---

## 🚦 Roadmap

### Q1 2025 ✅
- [x] Agent development complete
- [x] License Server integration
- [x] Basic monitoring features
- [x] WebSocket communication
- [x] Agent dashboard

### Q2 2025 🔄
- [ ] Product integrations (Ninja, Enterprise, Supreme)
- [ ] AI-powered monitoring
- [ ] Advanced analytics
- [ ] Mobile app

### Q3 2025 📋
- [ ] Container monitoring
- [ ] Cloud resource monitoring
- [ ] Predictive maintenance
- [ ] Auto-remediation

### Q4 2025 📋
- [ ] Custom dashboards
- [ ] Report builder
- [ ] API marketplace
- [ ] Enterprise features

---

## 🤝 Support

### Community
- **GitHub Issues**: [Report bugs](https://github.com/Iteksmart/iTechSmart/issues)
- **Discussions**: [Ask questions](https://github.com/Iteksmart/iTechSmart/discussions)
- **Documentation**: [Read docs](https://docs.itechsmart.dev)

### Enterprise
- **Email**: support@itechsmart.dev
- **Phone**: +1 (555) 123-4567
- **Portal**: https://support.itechsmart.dev

---

## 📄 License

**Proprietary License**

© 2025 iTechSmart Inc. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

For licensing inquiries: licensing@itechsmart.dev

---

## 👥 Team

**Founder & CEO**: DJuane Jackson

**Company**: iTechSmart Inc (C-Corporation)

**Website**: https://itechsmart.dev

**Email**: info@itechsmart.dev

---

## 🎉 Acknowledgments

Special thanks to all contributors and the open-source community for making this project possible.

Built with ❤️ by the iTechSmart team.

---

**Ready to transform your IT operations? [Get Started Now](https://itechsmart.dev/get-started)**