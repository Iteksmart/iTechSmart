# LegalAI Pro - iTechSmart Suite Integration

## Overview

LegalAI Pro is now a full member of the iTechSmart Suite, seamlessly integrated with **iTechSmart Enterprise Hub** and **iTechSmart Ninja** for centralized management, monitoring, and self-healing capabilities.

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  iTechSmart Enterprise Hub                   │
│              (Central Coordination & Routing)                │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
                    ┌───────┴───────┐
                    │               │
            ┌───────▼──────┐ ┌─────▼──────┐
            │  LegalAI Pro │ │   Ninja    │
            │   Service    │ │ Monitoring │
            └──────────────┘ └────────────┘
                    │               │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │  Self-Healing │
                    │   & Alerts    │
                    └───────────────┘
```

## Key Integration Features

### 1. Enterprise Hub Integration

**Automatic Service Registration**
- LegalAI Pro automatically registers with the Hub on startup
- Provides service metadata, capabilities, and endpoints
- Enables service discovery by other iTechSmart products

**Health Reporting (Every 30 seconds)**
- Status: healthy, degraded, or unhealthy
- Real-time metrics: uptime, database connectivity, AI service availability
- Issue tracking and alerting

**Metrics Reporting (Every 60 seconds)**
- System metrics: CPU usage, memory usage, active connections
- Application metrics: request count, error count, response times
- Legal-specific metrics:
  - AI queries processed
  - Documents processed
  - Active cases
  - Billable hours tracked

**Cross-Product Communication**
- Call other iTechSmart services via Hub routing
- Service discovery to find available products
- Unified authentication via PassPort
- Data sharing across the suite

### 2. Ninja Integration

**Error Detection & Reporting**
- Automatic error detection and reporting to Ninja
- Severity levels: low, medium, high, critical
- Full stack traces and context information

**Self-Healing Capabilities**
- Ninja analyzes errors and provides auto-fix suggestions
- Automatic recovery from common issues
- Dependency management and updates

**Performance Monitoring (Every 60 seconds)**
- Endpoint response times
- Status code tracking
- Error rate monitoring
- Performance degradation alerts

**Continuous Health Checks**
- Database connectivity
- AI service availability
- External API health
- Resource utilization

### 3. Standalone Mode

**Graceful Degradation**
- LegalAI Pro can operate without Hub/Ninja connection
- Local configuration management
- File-based settings fallback
- Automatic reconnection attempts

## Integration API

### Service Registration

```python
from app.integrations.integration import get_integration

# Get integration instance
integration = get_integration()

# Initialize integration
await integration.initialize()
```

### Error Reporting

```python
# Report error to Ninja for self-healing
try:
    # Your code here
    pass
except Exception as e:
    result = await integration.report_error(
        error=e,
        severity="high",
        context={"user_id": user_id, "action": "document_processing"}
    )
    
    if result and result.get("auto_fix_available"):
        print(f"Ninja will attempt auto-fix: {result['fix_description']}")
```

### Cross-Product Communication

```python
# Call another iTechSmart service
result = await integration.call_service(
    service_id="itechsmart-analytics",
    endpoint="/api/v1/analyze",
    method="POST",
    data={"case_id": case_id, "metrics": ["outcome_prediction"]}
)

# Discover available services
services = await integration.discover_services()
for service in services:
    print(f"{service['service_name']}: {service['capabilities']}")
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

### Docker Compose Integration

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

## Integration Benefits

### For Law Firms

1. **Unified Dashboard**: View LegalAI Pro metrics alongside other iTechSmart products
2. **Cross-Product Workflows**: Integrate legal data with analytics, compliance, and reporting
3. **Centralized Authentication**: Single sign-on across all iTechSmart products
4. **Automated Compliance**: Leverage iTechSmart Compliance for legal industry standards

### For Administrators

1. **Centralized Monitoring**: Monitor LegalAI Pro health from Enterprise Hub
2. **Self-Healing**: Automatic error recovery via Ninja
3. **Performance Optimization**: AI-powered performance tuning
4. **Unified Deployment**: Deploy as part of the iTechSmart Suite

### For Developers

1. **Service Discovery**: Easily find and integrate with other iTechSmart products
2. **Standardized APIs**: Consistent API patterns across the suite
3. **Shared Libraries**: Reuse common functionality from the suite
4. **Comprehensive Documentation**: Access to full suite documentation

## Integration Workflows

### Example 1: Legal Analytics Integration

```python
# LegalAI Pro → iTechSmart Analytics
# Analyze case outcomes and predict success rates

case_data = {
    "case_type": "Personal Injury",
    "jurisdiction": "California",
    "damages_claimed": 500000,
    "evidence_strength": "strong",
    "opposing_counsel": "Smith & Associates"
}

prediction = await integration.call_service(
    service_id="itechsmart-analytics",
    endpoint="/api/v1/predict",
    method="POST",
    data=case_data
)

print(f"Predicted outcome: {prediction['outcome']}")
print(f"Confidence: {prediction['confidence']}%")
print(f"Recommended settlement: ${prediction['settlement_range']}")
```

### Example 2: Document Compliance Check

```python
# LegalAI Pro → iTechSmart Compliance
# Verify document compliance with legal standards

document_data = {
    "document_type": "contract",
    "industry": "healthcare",
    "jurisdiction": "federal",
    "content": document_content
}

compliance_check = await integration.call_service(
    service_id="itechsmart-compliance",
    endpoint="/api/v1/check",
    method="POST",
    data=document_data
)

if not compliance_check['compliant']:
    print(f"Compliance issues found: {compliance_check['issues']}")
    print(f"Recommendations: {compliance_check['recommendations']}")
```

### Example 3: Automated Billing Integration

```python
# LegalAI Pro → iTechSmart Enterprise
# Sync billing data with enterprise financial systems

billing_data = {
    "client_id": client_id,
    "invoice_number": invoice_number,
    "amount": total_amount,
    "billable_hours": hours,
    "services": services_rendered
}

result = await integration.call_service(
    service_id="itechsmart-enterprise",
    endpoint="/api/v1/billing/sync",
    method="POST",
    data=billing_data
)

print(f"Billing synced: {result['status']}")
```

## Monitoring & Alerts

### Health Dashboard

Access LegalAI Pro health metrics from Enterprise Hub:
- http://itechsmart-enterprise:8000/dashboard/services/legalai-pro

### Metrics Available

**System Metrics**
- CPU Usage
- Memory Usage
- Active Connections
- Request Count
- Error Rate
- Response Times

**Legal Metrics**
- AI Queries Processed
- Documents Processed
- Active Cases
- Billable Hours
- Client Portal Usage
- Document Auto-Fill Success Rate

### Alert Configuration

Configure alerts in Enterprise Hub for:
- High error rates (>5%)
- Slow response times (>500ms)
- Low AI service availability (<95%)
- Database connectivity issues
- High resource usage (>80%)

## Security

### Authentication

- JWT-based authentication via PassPort
- Service-to-service authentication via Hub
- API key management via iTechSmart Vault
- Role-based access control (RBAC)

### Data Security

- TLS 1.3 encryption for all communications
- Secrets stored in iTechSmart Vault
- Audit trails via iTechSmart Ledger
- Compliance with legal industry standards (ABA, HIPAA for medical cases)

## Troubleshooting

### Integration Not Working

1. **Check Hub connectivity**:
   ```bash
   curl http://itechsmart-enterprise:8000/health
   ```

2. **Check Ninja connectivity**:
   ```bash
   curl http://itechsmart-ninja:8000/health
   ```

3. **View integration logs**:
   ```bash
   docker logs legalai-pro | grep "Integration"
   ```

### Service Not Registered

1. Check environment variables are set correctly
2. Verify Hub URL is accessible
3. Check network connectivity between containers
4. Review startup logs for registration errors

### Performance Issues

1. Check Ninja dashboard for performance alerts
2. Review metrics in Enterprise Hub
3. Check for self-healing actions in Ninja logs
4. Verify resource allocation (CPU, memory)

## Next Steps

1. **Explore Cross-Product Features**: Try integrating with iTechSmart Analytics for case predictions
2. **Configure Alerts**: Set up custom alerts in Enterprise Hub
3. **Review Metrics**: Monitor LegalAI Pro performance via Hub dashboard
4. **Enable Self-Healing**: Configure Ninja auto-fix rules for common errors
5. **Integrate with Compliance**: Connect with iTechSmart Compliance for automated compliance checking

## Support

For integration support:
- **Documentation**: https://docs.itechsmart.dev/legalai-pro
- **Hub Dashboard**: http://itechsmart-enterprise:8000
- **Ninja Console**: http://itechsmart-ninja:8000
- **Community**: https://community.itechsmart.dev

---

**LegalAI Pro** is now fully integrated with the iTechSmart Suite, providing law firms with the most comprehensive, AI-powered, self-healing legal management platform available.