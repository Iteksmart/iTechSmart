# iTechSmart Customer Data Platform - CRM Integration Guide

## Overview

The iTechSmart CDP provides seamless integration with major CRM platforms including Salesforce, HubSpot, and Marketo. This guide walks you through setting up and managing these integrations.

## Supported CRM Platforms

### 1. Salesforce
- **Integration Type**: REST API with OAuth 2.0
- **Supported Features**: Contacts, Opportunities, Accounts, Lead Scoring
- **Data Sync**: Real-time and incremental sync options

### 2. HubSpot
- **Integration Type**: Private App API
- **Supported Features**: Contacts, Companies, Deals, Lifecycle Stages
- **Data Sync**: Real-time and incremental sync options

### 3. Marketo
- **Integration Type**: REST API with OAuth 2.0
- **Supported Features**: Leads, Opportunities, Companies, Campaign Data
- **Data Sync**: Real-time and incremental sync options

## Configuration Setup

### 1. Salesforce Configuration

#### Prerequisites
- Salesforce Sales Cloud or Service Cloud instance
- API access enabled
- Connected App configured

#### Setup Steps

1. **Create Connected App in Salesforce**
   ```
   Go to Setup → Apps → App Manager → New Connected App
   - Enable OAuth Settings
   - Set Callback URL: https://your-domain.com/callback
   - Scopes: Full access (full)
   - Save and note Consumer Key and Secret
   ```

2. **Create API User**
   ```
   - Create a dedicated user for API access
   - Assign appropriate permissions
   - Generate Security Token
   ```

3. **Configure iTechSmart CDP**
   ```python
   crm_config = {
       'salesforce': {
           'client_id': 'your_consumer_key',
           'client_secret': 'your_consumer_secret',
           'username': 'your_api_username',
           'password': 'your_password_and_security_token'
       }
   }
   ```

### 2. HubSpot Configuration

#### Prerequisites
- HubSpot Professional or Enterprise account
- Private App access

#### Setup Steps

1. **Create Private App in HubSpot**
   ```
   Go to Settings → Integrations → Private Apps
   - Click "Create private app"
   - Set app name and description
   - Configure scopes:
     * crm.objects.contacts.read
     * crm.objects.contacts.write
     * crm.objects.companies.read
     * crm.objects.companies.write
     * crm.objects.deals.read
     * crm.objects.deals.write
   - Generate access token
   ```

2. **Configure iTechSmart CDP**
   ```python
   crm_config = {
       'hubspot': {
           'access_token': 'your_private_app_access_token'
       }
   }
   ```

### 3. Marketo Configuration

#### Prerequisites
- Marketo Enterprise or Premium account
- API access enabled
- Admin permissions

#### Setup Steps

1. **Create Custom Service in Marketo**
   ```
   Go to Admin → Integration → LaunchPoint → New → New Service
   - Service Type: Custom
   - Display Name: iTechSmart CDP
   - Description: Customer Data Platform Integration
   - Note Client ID and Client Secret
   ```

2. **Configure API User Permissions**
   ```
   - Assign appropriate permissions to the API user
   - Ensure access to Leads, Opportunities, and Companies
   ```

3. **Configure iTechSmart CDP**
   ```python
   crm_config = {
       'marketo': {
           'endpoint': 'https://xxx-xxx-xxx.mktorest.com',
           'client_id': 'your_client_id',
           'client_secret': 'your_client_secret'
       }
   }
   ```

## Data Mapping

### Standardized Contact Fields

| iTechSmart Field | Salesforce | HubSpot | Marketo |
|------------------|------------|---------|---------|
| customer_id | Id | id | id |
| email | Email | email | email |
| first_name | FirstName | firstname | firstName |
| last_name | LastName | lastname | lastName |
| phone | Phone | phone | phone |
| company | Company | company | company |
| title | Title | jobtitle | title |
| lead_score | LeadScore | hs_lead_score | leadScore |
| source | LeadSource | lifecyclestage | leadSource |
| created_date | CreatedDate | createdate | createdAt |
| last_updated | LastModifiedDate | lastmodifieddate | updatedAt |

### Standardized Opportunity Fields

| iTechSmart Field | Salesforce | HubSpot | Marketo |
|------------------|------------|---------|---------|
| id | Id | id | id |
| contact_id | ContactId | (via associations) | leadId |
| name | Name | dealname | name |
| stage | StageName | dealstage | stage |
| value | Amount | amount | amount |
| probability | Probability | (custom) | probability |
| close_date | CloseDate | closedate | closeDate |

## API Usage

### Initialize CRM Integration

```python
from app.crm_integrations.manager import CRMIntegrationManager

# Configuration
crm_configs = {
    'salesforce': {...},
    'hubspot': {...},
    'marketo': {...}
}

# Initialize manager
async with CRMIntegrationManager(crm_configs) as crm_manager:
    # Test connections
    status = await crm_manager.test_all_connections()
    print(f"Connection status: {status}")
    
    # Sync data
    sync_report = await crm_manager.sync_all_crms()
    print(f"Sync report: {sync_report}")
```

### Get Unified Contacts

```python
# Get all contacts
contacts = await crm_manager.get_unified_contacts()

# Filter contacts
filtered_contacts = await crm_manager.get_unified_contacts({
    'source_system': 'salesforce',
    'lead_score__gt': 50
})
```

### Create/Update Contacts

```python
from app.crm_integrations.base_crm import CRMContact

# Create new contact
contact = CRMContact(
    email='john@example.com',
    first_name='John',
    last_name='Doe',
    company='Example Corp'
)

result = await crm_manager.create_contact_in_all_crms(contact)
print(f"Created contacts: {result}")

# Update existing contact
update_data = {'lead_score': 75}
update_result = await crm_manager.update_contact_in_all_crms(
    contact_id='contact_123', 
    data=update_data
)
```

## Sync Strategies

### 1. Initial Full Sync
- Performs complete data extraction from all CRM systems
- Recommended for first-time setup
- May take significant time for large datasets

### 2. Incremental Sync
- Only syncs data changed since last sync
- Runs automatically on schedule
- Optimized for performance

### 3. Real-time Sync
- Syncs data immediately on changes
- Uses webhooks where available
- Requires additional configuration

## Monitoring & Troubleshooting

### Sync Status Monitoring

```python
# Get current sync status
status = await cdp_engine.get_crm_sync_status()
print(f"Sync status: {status}")

# Test CRM connections
connections = await cdp_engine.test_crm_connections()
print(f"Connection tests: {connections}")
```

### Common Issues

1. **Authentication Failures**
   - Check API credentials
   - Verify token expiration
   - Ensure proper permissions

2. **Rate Limiting**
   - Implement exponential backoff
   - Monitor API usage limits
   - Use bulk operations where possible

3. **Data Mapping Issues**
   - Review field mapping configuration
   - Check for custom field discrepancies
   - Validate data types

4. **Sync Performance**
   - Use incremental sync for large datasets
   - Implement pagination for large result sets
   - Monitor memory usage

## Security Considerations

### Data Protection
- All API communications use HTTPS/TLS
- Sensitive data is encrypted at rest
- Access tokens are stored securely

### Access Control
- Implement principle of least privilege
- Use dedicated API users
- Regular token rotation

### Compliance
- GDPR-compliant data handling
- Audit logging for all data operations
- Data retention policies

## Best Practices

1. **Configuration Management**
   - Store credentials securely
   - Use environment variables for sensitive data
   - Implement configuration validation

2. **Error Handling**
   - Implement retry logic with exponential backoff
   - Log all sync operations
   - Set up alerts for failures

3. **Performance Optimization**
   - Use batch operations where possible
   - Implement caching for frequently accessed data
   - Monitor API usage limits

4. **Data Quality**
   - Implement data validation rules
   - Regular data deduplication
   - Monitor data consistency

## Support

For technical support:
- Documentation: [Internal Wiki]
- Issues: [GitHub Issues]
- Support: support@itechsmart.com