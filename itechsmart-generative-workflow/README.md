# iTechSmart Generative Workflow - Text-to-Workflow Engine

## Overview

iTechSmart Generative Workflow revolutionizes workflow creation by converting natural language descriptions into fully automated, cross-product workflows. Instead of manually dragging and dropping components, users simply describe what they want to accomplish, and the AI generates a complete workflow across the entire iTechSmart suite.

## Key Features

### 🤖 Natural Language Processing
- Advanced NLP for intent understanding
- Context-aware workflow generation
- Multi-language support
- Conversational workflow refinement

### 🔗 Cross-Product Integration
- Seamless integration with all 42+ iTechSmart products
- Automatic service discovery and connection
- API endpoint mapping and authentication
- Data flow orchestration

### 🎯 Smart Workflow Generation
- AI-powered step optimization
- Best practice implementation
- Error handling and retry logic
- Conditional branching automation

### 📚 Template Library
- Pre-built workflow templates
- Industry-specific patterns
- Customizable workflow blocks
- Version control and sharing

### 🔄 Real-time Execution
- Live workflow monitoring
- Step-by-step progress tracking
- Automatic failure recovery
- Performance analytics

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Natural       │───▶│   AI Workflow   │───▶│   Generated     │
│   Language      │    │   Generator     │    │   Workflow      │
│   Input         │    │                 │    │   Definition    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Service       │    │   Workflow      │
                       │   Discovery     │    │   Execution     │
                       └─────────────────┘    └─────────────────┘
                              │                        │
                              └──────────┬─────────────┘
                                         ▼
                               ┌─────────────────┐
                               │   Cross-Product │
                               │   Integration   │
                               └─────────────────┘
```

## Quick Start

### Docker Deployment
```bash
cd itechsmart-generative-workflow
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

## Usage Examples

### 1. Employee Onboarding
```text
"Create a workflow that onboards a new developer, gives them AWS access, ships a laptop via Port Manager, and adds them to Slack"
```

**Generated Workflow:**
1. Create user account in iTechSmart PassPort
2. Provision AWS credentials via iTechSmart Cloud
3. Order laptop through iTechSmart Port Manager
4. Add to Slack workspace via iTechSmart Connect
5. Send welcome notification via iTechSmart Notify
6. Schedule orientation via iTechSmart Teams

### 2. Incident Response
```text
"When Sentinel detects a critical alert, automatically create incident in Ledger, notify on-call engineer, and start recovery procedures"
```

**Generated Workflow:**
1. Monitor iTechSmart Sentinel alerts
2. Filter for critical severity
3. Create incident record in iTechSmart Ledger
4. Trigger iTechSmart Ninja for automated recovery
5. Notify on-call via iTechSmart Notify
6. Update status dashboard

### 3. Compliance Audit
```text
"Run monthly compliance audit across all systems, generate report, and send to compliance team"
```

**Generated Workflow:**
1. Scan all systems with iTechSmart Shield
2. Check compliance with iTechSmart Compliance
3. Generate audit report
4. Store in iTechSmart Vault
5. Send to team via iTechSmart Connect

## API Endpoints

### Workflow Generation
- `POST /api/v1/generate` - Generate workflow from text
- `POST /api/v1/refine` - Refine existing workflow
- `GET /api/v1/templates` - Get workflow templates

### Workflow Management
- `POST /api/v1/workflows` - Create new workflow
- `GET /api/v1/workflows/{id}` - Get workflow details
- `PUT /api/v1/workflows/{id}` - Update workflow
- `DELETE /api/v1/workflows/{id}` - Delete workflow

### Execution
- `POST /api/v1/workflows/{id}/execute` - Execute workflow
- `GET /api/v1/workflows/{id}/status` - Get execution status
- `POST /api/v1/workflows/{id}/pause` - Pause execution
- `POST /api/v1/workflows/{id}/resume` - Resume execution

## Workflow Definition Format

```json
{
  "id": "wf-employee-onboarding-001",
  "name": "Employee Onboarding Workflow",
  "description": "Automated onboarding for new developers",
  "version": "1.0.0",
  "input_schema": {
    "employee_name": "string",
    "email": "string",
    "role": "string",
    "start_date": "date"
  },
  "steps": [
    {
      "id": "step-1",
      "name": "Create User Account",
      "service": "itechsmart-passport",
      "action": "create_user",
      "input_mapping": {
        "name": "{{employee_name}}",
        "email": "{{email}}",
        "role": "{{role}}"
      },
      "timeout": 30000,
      "retry_policy": {
        "max_retries": 3,
        "backoff": "exponential"
      }
    },
    {
      "id": "step-2",
      "name": "Provision AWS Access",
      "service": "itechsmart-cloud",
      "action": "create_iam_user",
      "depends_on": ["step-1"],
      "input_mapping": {
        "username": "{{email}}",
        "policies": ["developer-access"]
      }
    }
  ],
  "error_handling": {
    "on_failure": "notify_admin",
    "retry_strategy": "automatic"
  }
}
```

## Integration with iTechSmart Products

### Supported Products
- **Identity**: iTechSmart PassPort, Shield
- **Infrastructure**: iTechSmart Cloud, Ninja, Sentinel
- **Collaboration**: iTechSmart Connect, Teams, Notify
- **Management**: iTechSmart Port Manager, Ledger, Vault
- **Security**: iTechSmart Citadel, MDM Agent
- **Data**: iTechSmart Data Platform, DataFlow
- **Analytics**: iTechSmart Analytics, Pulse
- **Automation**: iTechSmart Workflow (existing), Forge, DevOps

### Service Discovery
The system automatically discovers available iTechSmart services and their capabilities:

```python
# Service discovery example
services = await workflow_generator.discover_services()

# Each service provides:
# - Available actions
# - Input/output schemas
# - Authentication requirements
# - Rate limits
# - Error patterns
```

## AI Model Integration

### Natural Language Processing
- **Intent Recognition**: Identify user goals and required actions
- **Entity Extraction**: Extract relevant parameters and context
- **Service Mapping**: Map requirements to iTechSmart services
- **Flow Optimization**: Determine optimal step ordering

### Model Configuration
```yaml
nlp_model:
  provider: "openai"  # or "local", "anthropic", etc.
  model: "gpt-4-turbo"
  temperature: 0.3
  max_tokens: 4000
  
workflow_generation:
  confidence_threshold: 0.85
  max_steps: 50
  timeout_seconds: 60
  
service_discovery:
  refresh_interval: 3600  # 1 hour
  cache_ttl: 86400  # 24 hours
```

## Advanced Features

### Conditional Logic
```text
"If the employee is a senior developer, also grant production access"
```

### Loop Patterns
```text
"For each service in the critical list, run health check and report status"
```

### Error Handling
```text
"If AWS provisioning fails, create a ticket and notify IT team"
```

### Time-based Triggers
```text
"Run this workflow every Monday at 9 AM for compliance reporting"
```

## Monitoring & Analytics

### Execution Metrics
- Success/failure rates
- Average execution time
- Bottleneck identification
- Resource utilization

### AI Performance
- Generation accuracy
- User satisfaction scores
- Refinement frequency
- Template usage statistics

### Dashboard Features
- Real-time workflow monitoring
- Step-by-step execution tracking
- Performance analytics
- Error pattern analysis

## Security & Compliance

### Access Control
- Role-based workflow permissions
- Service-level access validation
- Audit trail maintenance
- Data encryption

### Compliance Features
- SOC2, HIPAA, GDPR compliant
- Data retention policies
- Privacy controls
- Compliance reporting

## Configuration

### Environment Setup
```yaml
generative_workflow:
  max_workflow_complexity: 100
  default_timeout: 300000  # 5 minutes
  max_parallel_executions: 50
  
ai_integration:
  api_endpoint: "https://api.openai.com/v1"
  model: "gpt-4-turbo"
  max_tokens: 4000
  
services:
  discovery_interval: 3600
  health_check_timeout: 10000
  authentication_cache_ttl: 1800
```

## Use Cases

### 1. IT Operations
- Automated incident response
- Infrastructure provisioning
- Compliance reporting
- Backup and recovery

### 2. HR Processes
- Employee onboarding/offboarding
- Performance reviews
- Leave requests
- Training assignments

### 3. DevOps Pipelines
- CI/CD automation
- Deployment orchestration
- Testing workflows
- Release management

### 4. Customer Success
- Customer onboarding
- Support ticket routing
- Health monitoring
- Satisfaction surveys

## Documentation

- [API Documentation](./docs/API_DOCUMENTATION.md)
- [Integration Guide](./docs/INTEGRATION_GUIDE.md)
- [User Guide](./docs/USER_GUIDE.md)
- [Template Guide](./docs/TEMPLATE_GUIDE.md)

## License

© 2025 iTechSmart. All rights reserved.