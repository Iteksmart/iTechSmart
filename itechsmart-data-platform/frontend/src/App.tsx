import React from 'react';
import { Box, Grid, Card, CardContent, Typography, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, LinearProgress } from '@mui/material';
import { Storage as DataIcon, CheckCircle, Warning, Error, Refresh } from '@mui/icons-material';

const DataPlatformDashboard: React.FC = () => {
  const datasets = [
    { name: 'Customer Data', records: '2.5M', quality: 98, status: 'healthy', owner: 'Sales Team', lastUpdated: '2 hours ago' },
    { name: 'Product Catalog', records: '125K', quality: 95, status: 'healthy', owner: 'Product Team', lastUpdated: '1 day ago' },
    { name: 'Transaction History', records: '8.9M', quality: 87, status: 'warning', owner: 'Finance Team', lastUpdated: '30 min ago' },
    { name: 'User Analytics', records: '15.2M', quality: 72, status: 'critical', owner: 'Analytics Team', lastUpdated: '5 days ago' }
  ];

  return (
    <Box sx={{ p: 3, bgcolor: '#f5f5f5', minHeight: '100vh' }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <DataIcon sx={{ mr: 2, fontSize: 40, color: '#1976d2' }} />
            Data Platform - Data Governance Platform
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Enterprise data governance, quality, and lineage
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<Refresh />} size="large">Run Quality Check</Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">127</Typography><Typography color="text.secondary">Total Datasets</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">27.1M</Typography><Typography color="text.secondary">Total Records</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">92.5%</Typography><Typography color="text.secondary">Avg Quality Score</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">98.2%</Typography><Typography color="text.secondary">Compliance Rate</Typography></CardContent></Card></Grid>
      </Grid>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Dataset Overview</Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Dataset Name</TableCell>
                  <TableCell>Records</TableCell>
                  <TableCell>Quality Score</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Owner</TableCell>
                  <TableCell>Last Updated</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {datasets.map((dataset, i) => (
                  <TableRow key={i}>
                    <TableCell>{dataset.name}</TableCell>
                    <TableCell>{dataset.records}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, minWidth: 150 }}>
                        <LinearProgress 
                          variant="determinate" 
                          value={dataset.quality} 
                          sx={{ flexGrow: 1, height: 8, borderRadius: 1 }}
                          color={dataset.quality > 90 ? 'success' : dataset.quality > 80 ? 'warning' : 'error'}
                        />
                        <Typography variant="body2">{dataset.quality}%</Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={dataset.status} 
                        color={dataset.status === 'healthy' ? 'success' : dataset.status === 'warning' ? 'warning' : 'error'}
                        size="small"
                        icon={dataset.status === 'healthy' ? <CheckCircle /> : dataset.status === 'warning' ? <Warning /> : <Error />}
                      />
                    </TableCell>
                    <TableCell>{dataset.owner}</TableCell>
                    <TableCell>{dataset.lastUpdated}</TableCell>
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
              <Typography variant="h6" gutterBottom>Data Quality Issues</Typography>
              <Box sx={{ mt: 2 }}>
                {[
                  { issue: 'Missing values in User Analytics', severity: 'high', affected: '2.1M records' },
                  { issue: 'Duplicate entries in Transaction History', severity: 'medium', affected: '45K records' },
                  { issue: 'Format inconsistency in Customer Data', severity: 'low', affected: '1.2K records' }
                ].map((item, i) => (
                  <Box key={i} sx={{ mb: 2, p: 2, bgcolor: item.severity === 'high' ? '#ffebee' : item.severity === 'medium' ? '#fff3e0' : '#e8f5e9', borderRadius: 1 }}>
                    <Typography variant="body2" fontWeight="medium">{item.issue}</Typography>
                    <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                      <Chip label={item.severity} size="small" color={item.severity === 'high' ? 'error' : item.severity === 'medium' ? 'warning' : 'success'} />
                      <Typography variant="caption" color="text.secondary">{item.affected}</Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Data Lineage</Typography>
              <Box sx={{ mt: 2 }}>
                {[
                  { source: 'CRM System', arrow: '→', target: 'Customer Data Warehouse' },
                  { source: 'E-commerce Platform', arrow: '→', target: 'Transaction Database' },
                  { source: 'Analytics Engine', arrow: '→', target: 'Reporting Dashboard' },
                  { source: 'Mobile App', arrow: '→', target: 'User Behavior DB' }
                ].map((item, i) => (
                  <Box key={i} sx={{ mb: 2, p: 2, bgcolor: '#e3f2fd', borderRadius: 1 }}>
                    <Typography variant="body2">
                      <strong>{item.source}</strong> {item.arrow} <strong>{item.target}</strong>
                    </Typography>
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

export default DataPlatformDashboard;