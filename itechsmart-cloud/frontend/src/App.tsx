import React from 'react';
import { Box, Grid, Card, CardContent, Typography, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, IconButton } from '@mui/material';
import { Cloud as CloudIcon, Add as AddIcon, Settings as SettingsIcon, TrendingUp as TrendingUpIcon } from '@mui/icons-material';

const CloudDashboard: React.FC = () => {
  const resources = [
    { name: 'Production Cluster', provider: 'AWS', type: 'EKS', region: 'us-east-1', status: 'running', cost: '$1,245/mo' },
    { name: 'Database Primary', provider: 'Azure', type: 'SQL', region: 'eastus', status: 'running', cost: '$890/mo' },
    { name: 'Storage Bucket', provider: 'GCP', type: 'Cloud Storage', region: 'us-central1', status: 'running', cost: '$156/mo' },
    { name: 'CDN Distribution', provider: 'AWS', type: 'CloudFront', region: 'global', status: 'running', cost: '$234/mo' }
  ];

  return (
    <Box sx={{ p: 3, bgcolor: '#f5f5f5', minHeight: '100vh' }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <CloudIcon sx={{ mr: 2, fontSize: 40, color: '#1976d2' }} />
            Cloud - Multi-Cloud Management Platform
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage AWS, Azure, GCP, and more from one dashboard
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} size="large">Add Resource</Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">87</Typography><Typography color="text.secondary">Total Resources</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">$4.2K</Typography><Typography color="text.secondary">Monthly Cost</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">3</Typography><Typography color="text.secondary">Cloud Providers</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">99.9%</Typography><Typography color="text.secondary">Uptime</Typography></CardContent></Card></Grid>
      </Grid>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Active Resources</Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Resource Name</TableCell>
                  <TableCell>Provider</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Region</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Monthly Cost</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {resources.map((resource, i) => (
                  <TableRow key={i}>
                    <TableCell>{resource.name}</TableCell>
                    <TableCell><Chip label={resource.provider} size="small" color="primary" /></TableCell>
                    <TableCell>{resource.type}</TableCell>
                    <TableCell>{resource.region}</TableCell>
                    <TableCell><Chip label={resource.status} color="success" size="small" /></TableCell>
                    <TableCell>{resource.cost}</TableCell>
                    <TableCell align="right">
                      <IconButton size="small"><SettingsIcon fontSize="small" /></IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        <Grid item xs={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Cost Optimization</Typography>
              <Box sx={{ mt: 2 }}>
                {[
                  { recommendation: 'Use reserved instances for production', savings: '$450/mo' },
                  { recommendation: 'Downsize dev environment', savings: '$180/mo' },
                  { recommendation: 'Enable auto-scaling', savings: '$220/mo' }
                ].map((item, i) => (
                  <Box key={i} sx={{ mb: 2, p: 2, bgcolor: '#e3f2fd', borderRadius: 1 }}>
                    <Typography variant="body2">{item.recommendation}</Typography>
                    <Typography variant="body2" color="success.main" fontWeight="bold">Save {item.savings}</Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Provider Distribution</Typography>
              <Box sx={{ mt: 2 }}>
                {[
                  { provider: 'AWS', resources: 45, cost: '$2.1K' },
                  { provider: 'Azure', resources: 28, cost: '$1.5K' },
                  { provider: 'GCP', resources: 14, cost: '$600' }
                ].map((item, i) => (
                  <Box key={i} sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="body2">{item.provider}</Typography>
                    <Box>
                      <Chip label={`${item.resources} resources`} size="small" sx={{ mr: 1 }} />
                      <Chip label={item.cost} size="small" color="primary" />
                    </Box>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CloudDashboard;