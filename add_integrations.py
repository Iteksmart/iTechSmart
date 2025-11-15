#!/usr/bin/env python3
"""
Script to add integration sections to all iTechSmart product README files.
Preserves existing content and adds integration documentation.
"""

import os
import re

# Product configurations
PRODUCTS = {
    "itechsmart-ninja": {
        "name": "iTechSmart Ninja",
        "capabilities": ["self_healing", "monitoring", "optimization"],
        "integrations": ["Enterprise Hub", "All 26 Products"],
        "special_note": "Ninja monitors and fixes all other products in the suite."
    },
    "itechsmart-analytics": {
        "name": "iTechSmart Analytics",
        "capabilities": ["ml_analytics", "forecasting", "anomaly_detection"],
        "integrations": ["DataFlow", "Pulse", "All Products"],
        "special_note": "Provides ML-powered analytics for all products."
    },
    "itechsmart_supreme": {
        "name": "iTechSmart Supreme",
        "capabilities": ["healthcare_management", "ehr", "patient_portal"],
        "integrations": ["HL7", "Analytics", "Workflow"],
        "special_note": "Healthcare-specific integrations with HL7 and medical systems."
    },
    "itechsmart-hl7": {
        "name": "iTechSmart HL7",
        "capabilities": ["hl7_v2", "hl7_v3", "fhir", "medical_integration"],
        "integrations": ["Supreme", "DataFlow", "Ledger"],
        "special_note": "Medical data integration with HL7 standards."
    },
    "prooflink": {
        "name": "ProofLink.AI",
        "capabilities": ["document_verification", "blockchain_proof"],
        "integrations": ["Ledger", "Vault", "Notify"],
        "special_note": "Document verification with blockchain integration."
    },
    "passport": {
        "name": "PassPort",
        "capabilities": ["identity_management", "sso", "mfa"],
        "integrations": ["All Products", "Enterprise Hub"],
        "special_note": "Provides authentication for all iTechSmart products."
    },
    "itechsmart-impactos": {
        "name": "ImpactOS",
        "capabilities": ["impact_measurement", "esg_tracking"],
        "integrations": ["Analytics", "Pulse", "DataFlow"],
        "special_note": "Impact measurement and ESG tracking."
    },
    "fitsnap-ai": {
        "name": "FitSnap.AI",
        "capabilities": ["fitness_tracking", "ai_coaching"],
        "integrations": ["Analytics", "Notify", "Mobile"],
        "special_note": "AI-powered fitness tracking and coaching."
    },
    "itechsmart-shield": {
        "name": "iTechSmart Shield",
        "capabilities": ["cybersecurity", "threat_detection", "siem"],
        "integrations": ["Vault", "Compliance", "Ledger"],
        "special_note": "Security monitoring for all iTechSmart products."
    },
    "itechsmart-mobile": {
        "name": "iTechSmart Mobile",
        "capabilities": ["mobile_platform", "cross_platform"],
        "integrations": ["All Products", "Notify", "PassPort"],
        "special_note": "Mobile access to all iTechSmart products."
    },
    "itechsmart-workflow": {
        "name": "iTechSmart Workflow",
        "capabilities": ["process_automation", "low_code"],
        "integrations": ["All Products", "Notify", "Copilot"],
        "special_note": "Workflow automation across all products."
    },
    "itechsmart-ai": {
        "name": "iTechSmart Inc.",
        "capabilities": ["ai_ml_platform", "model_training"],
        "integrations": ["Analytics", "Copilot", "DataFlow"],
        "special_note": "AI/ML platform for all iTechSmart products."
    }
}

INTEGRATION_TEMPLATE = """
---

## 🔗 Integration Points

### Enterprise Hub Integration

{product_name} integrates with iTechSmart Enterprise Hub for:

- **Centralized Management**: Register and manage from Hub dashboard
- **Health Monitoring**: Real-time health checks every 30 seconds
- **Metrics Reporting**: Send performance metrics to Hub
- **Configuration Updates**: Receive configuration from Hub
- **Cross-Product Workflows**: Participate in multi-product workflows
- **Unified Authentication**: Use PassPort for authentication via Hub

#### Hub Registration

On startup, {product_name} automatically registers with Enterprise Hub:

```python
# Automatic registration on startup
{{
  "product_id": "{product_id}",
  "product_name": "{product_name}",
  "version": "1.0.0",
  "api_endpoint": "http://{product_id}:8080",
  "health_endpoint": "http://{product_id}:8080/health",
  "capabilities": {capabilities},
  "status": "healthy"
}}
```

### Ninja Integration

{product_name} is monitored and managed by iTechSmart Ninja for:

- **Self-Healing**: Automatic detection and recovery from errors
- **Performance Optimization**: Continuous performance monitoring and optimization
- **Auto-Scaling**: Automatic scaling based on load
- **Error Detection**: Real-time error detection and alerting
- **Dependency Management**: Automatic dependency updates and patches
- **Resource Optimization**: Memory and CPU optimization

{special_note}

### Standalone Mode

{product_name} can operate independently without Hub connection:

**Standalone Features:**
- ✅ Core functionality available
- ✅ Local configuration management
- ✅ File-based settings
- ✅ Offline operation
- ❌ No cross-product workflows
- ❌ No centralized monitoring
- ❌ Manual configuration updates

**Enable Standalone Mode:**
```bash
export {env_prefix}_HUB_ENABLED=false
export {env_prefix}_STANDALONE_MODE=true
```

---

## 🌐 Cross-Product Integration

### Integrated With

{product_name} integrates with the following iTechSmart products:

**Core Integrations:**
- **Enterprise Hub**: Central management and monitoring
- **Ninja**: Self-healing and optimization
- **PassPort**: Authentication and authorization
- **Vault**: Secrets management

**Product-Specific Integrations:**
{product_integrations}

---
"""

def get_env_prefix(product_id):
    """Convert product ID to environment variable prefix."""
    return product_id.upper().replace("-", "_").replace("ITECHSMART_", "")

def add_integration_section(product_id, config):
    """Add integration section to product README."""
    readme_path = f"{product_id}/README.md"
    
    if not os.path.exists(readme_path):
        print(f"❌ {readme_path} not found")
        return False
    
    # Read existing README
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Check if integration section already exists
    if "## 🔗 Integration Points" in content:
        print(f"✅ {product_id} already has integration section")
        return True
    
    # Find insertion point (before Contributing or at end)
    insertion_patterns = [
        r'(## 🤝 Contributing)',
        r'(## 📝 License)',
        r'(## 🆘 Support)',
        r'(---\n\n\*\*.*\*\* -)'  # Before final tagline
    ]
    
    insertion_point = None
    for pattern in insertion_patterns:
        match = re.search(pattern, content)
        if match:
            insertion_point = match.start()
            break
    
    if insertion_point is None:
        # Add at end
        insertion_point = len(content)
    
    # Prepare integration content
    env_prefix = get_env_prefix(product_id)
    capabilities_str = str(config['capabilities'])
    integrations_str = "\n".join([f"- **{i}**" for i in config['integrations']])
    
    integration_content = INTEGRATION_TEMPLATE.format(
        product_name=config['name'],
        product_id=product_id,
        capabilities=capabilities_str,
        special_note=config['special_note'],
        env_prefix=env_prefix,
        product_integrations=integrations_str
    )
    
    # Insert integration section
    new_content = content[:insertion_point] + integration_content + content[insertion_point:]
    
    # Backup original
    backup_path = f"{readme_path}.backup"
    with open(backup_path, 'w') as f:
        f.write(content)
    
    # Write updated README
    with open(readme_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated {product_id}")
    return True

def main():
    """Main function to update all products."""
    print("🚀 Adding integration sections to all products...\n")
    
    updated = 0
    skipped = 0
    failed = 0
    
    for product_id, config in PRODUCTS.items():
        try:
            if add_integration_section(product_id, config):
                updated += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Error updating {product_id}: {e}")
            failed += 1
    
    print(f"\n📊 Summary:")
    print(f"  ✅ Updated: {updated}")
    print(f"  ⏭️  Skipped: {skipped}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📝 Total: {len(PRODUCTS)}")

if __name__ == "__main__":
    main()