import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Box
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import axios from 'axios';

function Integrations() {
  const [integrations, setIntegrations] = useState([
    {
      id: 'servicenow',
      name: 'ServiceNow',
      status: 'active',
      type: 'Bi-directional',
      auth: 'OAuth 2.0',
      description: 'ITSM platform integration for incident and change management',
      production_ready: true
    },
    {
      id: 'zendesk',
      name: 'Zendesk',
      status: 'active',
      type: 'Bi-directional',
      auth: 'OAuth 2.0',
      description: 'Support ticket management and customer service',
      production_ready: true
    },
    {
      id: 'itglue',
      name: 'IT Glue',
      status: 'active',
      type: 'Uni-directional',
      auth: 'API Key',
      description: 'IT documentation and asset management',
      production_ready: true
    },
    {
      id: 'nable',
      name: 'N-able',
      status: 'active',
      type: 'Bi-directional',
      auth: 'JWT',
      description: 'Remote monitoring and management platform',
      production_ready: true
    },
    {
      id: 'connectwise',
      name: 'ConnectWise',
      status: 'active',
      type: 'Bi-directional',
      auth: 'OAuth 2.0',
      description: 'PSA and business management platform',
      production_ready: true
    },
    {
      id: 'jira',
      name: 'Jira',
      status: 'active',
      type: 'Bi-directional',
      auth: 'OAuth 2.0',
      description: 'Project and issue tracking',
      production_ready: true
    },
    {
      id: 'slack',
      name: 'Slack',
      status: 'active',
      type: 'Webhooks',
      auth: 'OAuth 2.0',
      description: 'Team collaboration and notifications',
      production_ready: true
    },
    {
      id: 'teams',
      name: 'Microsoft Teams',
      status: 'active',
      type: 'Webhooks',
      auth: 'OAuth 2.0',
      description: 'Team collaboration and notifications',
      production_ready: true
    },
    {
      id: 'prometheus',
      name: 'Prometheus',
      status: 'active',
      type: 'Metrics',
      auth: 'Bearer Token',
      description: 'Monitoring and metrics collection',
      production_ready: true
    },
    {
      id: 'wazuh',
      name: 'Wazuh',
      status: 'active',
      type: 'Security Events',
      auth: 'API Key',
      description: 'Security monitoring and threat detection',
      production_ready: true
    },
    {
      id: 'sap',
      name: 'SAP',
      status: 'beta',
      type: 'Bi-directional',
      auth: 'SAML 2.0',
      description: 'ERP integration',
      production_ready: false
    },
    {
      id: 'salesforce',
      name: 'Salesforce',
      status: 'beta',
      type: 'Bi-directional',
      auth: 'OAuth 2.0',
      description: 'CRM integration',
      production_ready: false
    },
    {
      id: 'workday',
      name: 'Workday',
      status: 'beta',
      type: 'Uni-directional',
      auth: 'OAuth 2.0',
      description: 'HR management system',
      production_ready: false
    }
  ]);

  const handleTest = async (integrationId) => {
    try {
      const response = await axios.post(`/api/integrations/${integrationId}/test`);
      alert(`Test successful: ${response.data.message}`);
    } catch (error) {
      alert(`Test failed: ${error.message}`);
    }
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Integrations
      </Typography>
      <Typography variant="body1" paragraph color="textSecondary">
        Manage your system integrations and connections
      </Typography>

      <Grid container spacing={3}>
        {integrations.map((integration) => (
          <Grid item xs={12} sm={6} md={4} key={integration.id}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                  <Typography variant="h6">
                    {integration.name}
                  </Typography>
                  {integration.status === 'active' ? (
                    <CheckCircleIcon color="success" />
                  ) : (
                    <WarningIcon color="warning" />
                  )}
                </Box>
                
                <Box mb={2}>
                  <Chip 
                    label={integration.status.toUpperCase()} 
                    color={integration.status === 'active' ? 'success' : 'warning'}
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  <Chip 
                    label={integration.type} 
                    size="small"
                    variant="outlined"
                    sx={{ mr: 1 }}
                  />
                  {integration.production_ready && (
                    <Chip 
                      label="Production" 
                      size="small"
                      color="primary"
                    />
                  )}
                </Box>

                <Typography variant="body2" color="textSecondary" paragraph>
                  {integration.description}
                </Typography>

                <Typography variant="caption" display="block">
                  Auth: {integration.auth}
                </Typography>
              </CardContent>
              
              <CardActions>
                <Button size="small">Configure</Button>
                <Button size="small" onClick={() => handleTest(integration.id)}>
                  Test
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}

export default Integrations;