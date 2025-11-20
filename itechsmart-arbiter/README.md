# iTechSmart Arbiter - AI Governance & Safety Layer

## Overview

iTechSmart Arbiter is the "AI Constitution" and governance layer that ensures safe autonomous operations across the entire iTechSmart suite. It acts as a safety proxy that sits between AI agents and infrastructure, enforcing policies, calculating risk scores, and requiring human approval for high-risk operations.

## Key Features

### 🛡️ Constitution Engine
- JSON/YAML-based policy definitions
- Forbidden command blocking
- Business hours restrictions
- Environment-specific rules

### 📊 Risk Scoring System
- Real-time risk assessment (0-100 scale)
- Contextual analysis based on target systems
- Keyword-based threat detection
- Automated approval workflows

### 🎯 Digital Twin Simulation
- Pre-execution dry-run validation
- Virtual environment testing
- Impact prediction
- Failure simulation

### 🔒 Human-in-the-Loop (HITL)
- Slack/Teams integration for approvals
- Multi-factor authentication requirements
- Escalation workflows
- Audit trail maintenance

### ⚡ Kill Switch
- Instant revocation of AI privileges
- Emergency stop functionality
- Global policy enforcement
- Real-time status monitoring

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Agent      │───▶│   iTechSmart    │───▶│  Infrastructure │
│   (Ninja)       │    │   Arbiter       │    │   (Target)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Human         │
                       │   Approval      │
                       │   (HITL)        │
                       └─────────────────┘
```

## Quick Start

### Docker Deployment
```bash
cd itechsmart-arbiter
docker-compose up -d
```

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend
cd frontend
npm install
npm run dev
```

## API Endpoints

### Core Governance
- `POST /api/v1/evaluate` - Evaluate AI action request
- `GET /api/v1/constitution` - Get current policies
- `PUT /api/v1/constitution` - Update policies
- `POST /api/v1/emergency-stop` - Activate kill switch

### Simulation
- `POST /api/v1/simulate` - Run dry-run simulation
- `GET /api/v1/simulation/{id}` - Get simulation results
- `DELETE /api/v1/simulation/{id}` - Clean up simulation

### Monitoring
- `GET /api/v1/status` - System health check
- `GET /api/v1/metrics` - Risk metrics and statistics
- `GET /api/v1/audit-log` - Governance audit trail

## Configuration

### Constitution Example
```yaml
constitution:
  forbidden_commands:
    - "rm -rf /"
    - "drop table"
    - "shutdown -h now"
  
  restricted_hours:
    start: 9
    end: 17
  
  high_risk_keywords:
    - "firewall"
    - "sudo"
    - "delete"
    - "remove"
  
  approval_thresholds:
    auto_approve: 20
    human_approval: 50
    blocked: 80
```

## Integration

### With iTechSmart Ninja
```python
import requests

def safe_execute_command(command, target):
    response = requests.post('http://arbiter:8080/api/v1/evaluate', json={
        'agent_id': 'ninja-bot-01',
        'command': command,
        'target_system': target
    })
    
    decision = response.json()
    if decision['status'] == 'APPROVED':
        return execute_actual_command(command)
    elif decision['status'] == 'PENDING_APPROVAL':
        wait_for_human_approval(decision['approval_id'])
    else:
        log_blocked_action(decision)
```

## Security Features

- **Policy Encryption**: All policies encrypted at rest
- **Audit Logging**: Every decision logged with full context
- **Rate Limiting**: Prevents abuse of approval workflows
- **Multi-tenancy**: Isolated policies per organization
- **Compliance**: SOC2, HIPAA, GDPR ready

## Monitoring & Alerts

- Real-time risk dashboards
- Policy violation alerts
- System health monitoring
- Performance metrics
- Compliance reporting

## Documentation

- [API Documentation](./docs/API_DOCUMENTATION.md)
- [Deployment Guide](./docs/DEPLOYMENT_GUIDE.md)
- [User Guide](./docs/USER_GUIDE.md)
- [Security Guide](./docs/SECURITY_GUIDE.md)

## License

© 2025 iTechSmart. All rights reserved.