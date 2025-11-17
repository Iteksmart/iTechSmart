# iTechSmart Supreme Plus

**AI-Powered Infrastructure Auto-Remediation Platform**

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

iTechSmart Supreme Plus is an advanced AI-powered infrastructure auto-remediation platform that automatically detects, diagnoses, and fixes infrastructure issues across your entire technology stack. By integrating with monitoring systems like Prometheus and Wazuh, Supreme Plus provides intelligent incident management with automated remediation capabilities.

## Key Features

### 🤖 AI-Powered Analysis
- Automatic incident diagnosis using advanced AI models
- Intelligent remediation recommendations
- Pattern recognition and predictive analytics
- Confidence scoring for remediation actions

### 🔧 Auto-Remediation
- Automated execution of remediation actions
- Support for SSH, PowerShell, WinRM, Telnet, and CLI
- 23+ pre-built remediation templates
- Custom remediation scripts
- Multi-platform support (Linux, Windows, Unix)

### 💻 Workstation Support
- Windows workstation remediation
- Linux desktop support
- Fix common issues: network, display, audio, printers
- User profile management
- Software updates and patches
- Remote troubleshooting

### 🖥️ Server Management
- Comprehensive server diagnostics
- RAID status monitoring
- Resource monitoring (CPU, memory, disk)
- Service health checks
- Log analysis
- Performance optimization
- Automated backups

### 🌐 Network Device Support
- **Cisco IOS/NX-OS**: Full command support
- **Juniper JunOS**: Configuration and monitoring
- **Palo Alto**: Firewall management
- **F5 BIG-IP**: Load balancer operations
- **Arista EOS**: Switch management
- **HP ProCurve**: Network operations
- Configuration backup and restore
- Interface management
- Routing and switching operations

### 📊 Infrastructure Monitoring
- Real-time metrics collection
- CPU, memory, disk, and network monitoring
- Alert rule configuration
- Health status tracking
- Historical metrics analysis

### 🔌 Integration Management
- Prometheus integration
- Wazuh security platform
- Grafana dashboards
- Elasticsearch log aggregation
- Splunk SIEM
- Datadog monitoring
- New Relic APM
- PagerDuty incident management
- Slack notifications
- Generic webhook support

### 🎯 Incident Management
- Centralized incident tracking
- Severity-based prioritization
- Automatic incident creation from alerts
- Incident lifecycle management
- Audit trail and logging

## Architecture

### Backend Components
- **FastAPI Application**: RESTful API server
- **SupremePlusEngine**: Core auto-remediation engine
- **Database Models**: 15 comprehensive models
- **Integration Module**: Cross-product connectivity
- **API Modules**: Incidents, Remediations, Integrations, Monitoring

### Frontend Components
- **React + TypeScript**: Modern web interface
- **5 Main Pages**: Dashboard, Incidents, Remediations, Integrations, Monitoring
- **Real-time Updates**: Live metrics and status updates
- **Responsive Design**: Works on all devices

### Database Schema
- Incidents
- Remediations
- RemediationActions
- Integrations
- InfrastructureNodes
- AlertRules
- RemediationLogs
- Metrics
- RemediationTemplates
- ExecutionHistory
- Notifications
- AIAnalysis
- RemediationSchedules
- AuditLogs
- Credentials

## Technology Stack

### Backend
- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- Paramiko (SSH)
- Requests

### Frontend
- React 18
- TypeScript
- Vite
- TailwindCSS
- Recharts
- Axios
- React Router

### Infrastructure
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7
- Nginx

## Quick Start

### Prerequisites
- Docker and Docker Compose
- 4GB RAM minimum
- 10GB disk space

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd itechsmart-supreme-plus
```

2. Start the services:
```bash
docker-compose up -d
```

3. Access the application:
- Frontend: http://localhost:3034
- Backend API: http://localhost:8034
- API Documentation: http://localhost:8034/docs

### Configuration

Environment variables can be configured in `docker-compose.yml`:

```yaml
environment:
  DATABASE_URL: postgresql://supremeplus:supremeplus@postgres:5432/supremeplus
  REDIS_URL: redis://redis:6379/4
  AUTO_REMEDIATION_ENABLED: "true"
  AI_MODEL: "gpt-4"
  HUB_URL: http://hub:8000
  NINJA_URL: http://ninja:8001
```

## Usage

### Creating an Incident

1. Navigate to the Incidents page
2. Click "Create Incident"
3. Fill in the incident details
4. Submit to create the incident

### AI Analysis

1. Open an incident
2. Click "AI Analyze"
3. Review the AI diagnosis and recommendations
4. Execute recommended remediations

### Auto-Remediation

1. Configure alert rules in Monitoring
2. Enable auto-remediation in settings
3. System automatically creates incidents from alerts
4. AI analyzes and executes remediations
5. Monitor progress in Remediations page

### Adding Integrations

1. Navigate to Integrations page
2. Click "Add Integration"
3. Select integration type
4. Configure connection details
5. Test the integration
6. Enable for use

## API Endpoints

### Incidents
- `POST /api/incidents` - Create incident
- `GET /api/incidents` - List incidents
- `GET /api/incidents/{id}` - Get incident
- `PUT /api/incidents/{id}` - Update incident
- `POST /api/incidents/{id}/analyze` - AI analysis

### Remediations
- `POST /api/remediations` - Create remediation
- `GET /api/remediations` - List remediations
- `POST /api/remediations/{id}/execute` - Execute remediation
- `GET /api/remediations/{id}/logs` - Get logs

### Integrations
- `POST /api/integrations` - Create integration
- `GET /api/integrations` - List integrations
- `POST /api/integrations/{id}/test` - Test integration

### Monitoring
- `POST /api/monitoring/nodes` - Add node
- `GET /api/monitoring/nodes` - List nodes
- `POST /api/monitoring/nodes/{id}/metrics/collect` - Collect metrics
- `GET /api/monitoring/nodes/{id}/metrics` - Get metrics

### Devices (NEW)
- `GET /api/devices/workstation-actions` - List workstation actions
- `POST /api/devices/workstation/remediate` - Execute workstation remediation
- `GET /api/devices/server-actions` - List server actions
- `POST /api/devices/server/diagnostics` - Run server diagnostics
- `GET /api/devices/network-devices/types` - List network device types
- `GET /api/devices/network-devices/commands/{type}` - List device commands
- `POST /api/devices/network-devices/execute` - Execute network device command
- `POST /api/devices/bulk-remediate` - Bulk remediation across devices

## Remediation Templates

Supreme Plus includes 23+ pre-built remediation templates:

### System & Service Management
- **restart_service**: Restart system services
- **clear_disk_space**: Clean temporary files and logs
- **restart_container**: Restart Docker containers
- **scale_service**: Scale services up/down
- **clear_cache**: Clear application caches
- **restart_database**: Restart database services
- **kill_process**: Terminate processes
- **update_firewall**: Update firewall rules

### Workstation Support
- **restart_workstation**: Restart workstation
- **fix_network_adapter**: Reset network adapter
- **clear_dns_cache**: Flush DNS resolver cache
- **fix_printer**: Restart print spooler
- **reset_user_profile**: Reset user profile cache
- **update_software**: Update system packages
- **fix_audio**: Restart audio service

### Server Operations
- **check_server_health**: Comprehensive health check
- **optimize_server**: Optimize server performance
- **backup_server**: Create server backup
- **check_disk_health**: Check disk health status

### Network Device Operations
- **reload_network_device**: Reload device configuration
- **save_network_config**: Save running configuration
- **clear_arp_cache**: Clear ARP table
- **reset_interface**: Reset network interface

## Integration with iTechSmart Suite

Supreme Plus integrates seamlessly with other iTechSmart products:

- **iTechSmart Hub**: Central management and coordination
- **iTechSmart Ninja**: Complex workflow automation
- **iTechSmart Analytics**: Metrics and reporting
- **iTechSmart Shield**: Security incident coordination
- **iTechSmart Notify**: Multi-channel notifications
- **iTechSmart Pulse**: Health monitoring

## Security

- Encrypted credential storage
- Role-based access control
- Audit logging for all actions
- Secure SSH/PowerShell execution
- API key authentication
- HTTPS support

## Monitoring & Metrics

Supreme Plus collects and monitors:
- CPU usage
- Memory usage
- Disk usage
- Network traffic
- Service health
- Application metrics
- Custom metrics

## Support

For support and documentation:
- User Guide: See USER_GUIDE.md
- Deployment Guide: See DEPLOYMENT_GUIDE.md
- API Documentation: http://localhost:8034/docs
- Website: https://itechsmart.dev
- Technical Support: support@itechsmart.dev
- Sales Inquiries: sales@itechsmart.dev
- Phone: 310-251-3969

**iTechSmart Inc.**  
1130 Ogletown Road, Suite 2  
Newark, DE 19711, USA



## 🚀 Upcoming Features (v1.4.0)

1. **Predictive maintenance scheduling with AI**
2. **Advanced trend analysis and forecasting**
3. **Custom report templates and automation**
4. **Mobile app integration (iOS and Android)**
5. **Real-time alerting with smart notifications**
6. **Integration with ITSM platforms**
7. **Advanced data visualization tools**
8. **Automated capacity planning recommendations**

**Product Value**: $2.8M  
**Tier**: 1  
**Total Features**: 8

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

