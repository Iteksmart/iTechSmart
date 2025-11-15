# LegalAI Pro - iTechSmart Suite Integration

## Overview

LegalAI Pro is now a full member of the **iTechSmart Suite**, providing seamless integration with all 25 other products in the ecosystem.

## Integration Features

### 🔗 Enterprise Hub Integration
- **Automatic Registration**: LegalAI Pro registers with the Hub on startup
- **Health Monitoring**: Reports health status every 30 seconds
- **Metrics Collection**: Sends performance metrics every 60 seconds
- **Service Discovery**: Can discover and communicate with other iTechSmart products
- **Unified Authentication**: Single sign-on via iTechSmart PassPort

### 🛡️ Ninja Self-Healing Integration
- **Error Detection**: Automatically reports errors to Ninja
- **Auto-Fix**: Ninja analyzes and fixes common issues automatically
- **Performance Monitoring**: Continuous performance tracking
- **Health Checks**: Regular health verification
- **Dependency Management**: Automatic dependency updates

### 🌐 Cross-Product Communication
LegalAI Pro can now communicate with all iTechSmart products:

**Analytics Integration**
- Send case data for outcome prediction
- Get settlement value recommendations
- Analyze historical case patterns

**Compliance Integration**
- Verify document compliance with legal standards
- Check contracts for regulatory compliance
- Automated compliance reporting

**Vault Integration**
- Secure storage of sensitive client data
- Encryption key management
- Secrets management for API keys

**Ledger Integration**
- Immutable audit trails for all actions
- Blockchain verification of documents
- Compliance audit logs

**Notify Integration**
- Client notifications (email, SMS, push)
- Court date reminders
- Deadline alerts

**PassPort Integration**
- Single sign-on across all products
- Unified user management
- Role-based access control

## Quick Start with iTechSmart Suite

### 1. Start the Full Suite

```bash
# Start all iTechSmart products including LegalAI Pro
cd /workspace
docker-compose -f itechsmart-suite-compose.yml up -d
```

### 2. Access LegalAI Pro

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 3. Access Other Suite Products

- **Enterprise Hub**: http://localhost:8001
- **Ninja Console**: http://localhost:8002
- **Analytics**: http://localhost:8003
- **And 22 more products...**

## Integration Examples

### Example 1: Case Outcome Prediction

```python
from app.integrations.integration import get_integration

# Get integration instance
integration = get_integration()

# Call Analytics service for case prediction
case_data = {
    "case_type": "Personal Injury",
    "jurisdiction": "California",
    "damages_claimed": 500000,
    "evidence_strength": "strong"
}

prediction = await integration.call_service(
    service_id="itechsmart-analytics",
    endpoint="/api/v1/predict",
    method="POST",
    data=case_data
)

print(f"Predicted outcome: {prediction['outcome']}")
print(f"Confidence: {prediction['confidence']}%")
```

### Example 2: Document Compliance Check

```python
# Check document compliance
document_data = {
    "document_type": "contract",
    "industry": "healthcare",
    "content": document_content
}

compliance = await integration.call_service(
    service_id="itechsmart-compliance",
    endpoint="/api/v1/check",
    method="POST",
    data=document_data
)

if not compliance['compliant']:
    print(f"Issues: {compliance['issues']}")
```

### Example 3: Error Reporting to Ninja

```python
# Report error for self-healing
try:
    # Your code here
    process_document(doc_id)
except Exception as e:
    result = await integration.report_error(
        error=e,
        severity="high",
        context={"document_id": doc_id}
    )
    
    if result and result.get("auto_fix_available"):
        print(f"Ninja will fix: {result['fix_description']}")
```

## Configuration

### Environment Variables

```bash
# Hub Configuration
HUB_URL=http://itechsmart-enterprise:8000
ENABLE_HUB=true

# Ninja Configuration
NINJA_URL=http://itechsmart-ninja:8000
ENABLE_NINJA=true

# Service Configuration
SERVICE_ID=legalai-pro
SERVICE_NAME=LegalAI Pro
```

### Docker Compose

```yaml
services:
  legalai-pro:
    build: ./legalai-pro/backend
    environment:
      - HUB_URL=http://itechsmart-enterprise:8000
      - NINJA_URL=http://itechsmart-ninja:8000
      - ENABLE_HUB=true
      - ENABLE_NINJA=true
    depends_on:
      - itechsmart-enterprise
      - itechsmart-ninja
    networks:
      - itechsmart-network
```

## Benefits

### For Law Firms
- **Unified Dashboard**: View all metrics in one place
- **Cross-Product Workflows**: Automate complex processes
- **Single Sign-On**: One login for all products
- **Automated Compliance**: Leverage suite-wide compliance

### For Administrators
- **Centralized Monitoring**: Monitor from Enterprise Hub
- **Self-Healing**: Automatic error recovery
- **Performance Optimization**: AI-powered tuning
- **Unified Deployment**: Deploy entire suite together

### For Developers
- **Service Discovery**: Easy integration with other products
- **Standardized APIs**: Consistent patterns
- **Shared Libraries**: Reuse common functionality
- **Comprehensive Docs**: Full suite documentation

## Monitoring

### Health Dashboard
Access LegalAI Pro metrics from Enterprise Hub:
```
http://itechsmart-enterprise:8000/dashboard/services/legalai-pro
```

### Available Metrics
- CPU Usage
- Memory Usage
- Active Connections
- Request Count
- Error Rate
- Response Times
- AI Queries Processed
- Documents Processed
- Active Cases
- Billable Hours

## Support

- **Documentation**: https://docs.itechsmart.dev/legalai-pro
- **Hub Dashboard**: http://itechsmart-enterprise:8000
- **Ninja Console**: http://itechsmart-ninja:8000
- **Community**: https://community.itechsmart.dev

---

**LegalAI Pro** - Now part of the world's most comprehensive enterprise software suite!