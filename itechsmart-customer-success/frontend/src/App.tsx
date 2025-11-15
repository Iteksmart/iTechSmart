import React from 'react';
import { Box, Grid, Card, CardContent, Typography, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, LinearProgress, Avatar } from '@mui/material';
import { People as PeopleIcon, TrendingUp, TrendingDown, Warning } from '@mui/icons-material';

const CustomerSuccessDashboard: React.FC = () => {
  const customers = [
    { name: 'Acme Corp', health: 85, status: 'healthy', mrr: '$12,500', lastContact: '2 days ago', csm: 'John Doe' },
    { name: 'TechStart Inc', health: 45, status: 'at-risk', mrr: '$8,900', lastContact: '15 days ago', csm: 'Jane Smith' },
    { name: 'Global Solutions', health: 92, status: 'healthy', mrr: '$25,000', lastContact: '1 day ago', csm: 'Mike Johnson' },
    { name: 'Innovation Labs', health: 38, status: 'critical', mrr: '$15,600', lastContact: '30 days ago', csm: 'Sarah Williams' }
  ];

  return (
    <Box sx={{ p: 3, bgcolor: '#f5f5f5', minHeight: '100vh' }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <PeopleIcon sx={{ mr: 2, fontSize: 40, color: '#1976d2' }} />
          Customer Success - Customer Success Platform
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Proactive customer health monitoring and engagement
        </Typography>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">247</Typography><Typography color="text.secondary">Total Customers</Typography><Typography variant="body2" color="success.main">↑ +12 this month</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">78.5</Typography><Typography color="text.secondary">Avg Health Score</Typography><Typography variant="body2" color="success.main">↑ +3.2 points</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">2.1%</Typography><Typography color="text.secondary">Churn Rate</Typography><Typography variant="body2" color="success.main">↓ -0.5%</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">$2.1M</Typography><Typography color="text.secondary">Total MRR</Typography><Typography variant="body2" color="success.main">↑ +8.5%</Typography></CardContent></Card></Grid>
      </Grid>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Customer Health Overview</Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Customer</TableCell>
                  <TableCell>Health Score</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>MRR</TableCell>
                  <TableCell>Last Contact</TableCell>
                  <TableCell>CSM</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {customers.map((customer, i) => (
                  <TableRow key={i}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: '#1976d2' }}>{customer.name[0]}</Avatar>
                        <Typography variant="body2">{customer.name}</Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, minWidth: 150 }}>
                        <LinearProgress 
                          variant="determinate" 
                          value={customer.health} 
                          sx={{ flexGrow: 1, height: 8, borderRadius: 1 }}
                          color={customer.health > 70 ? 'success' : customer.health > 50 ? 'warning' : 'error'}
                        />
                        <Typography variant="body2">{customer.health}</Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={customer.status} 
                        color={customer.status === 'healthy' ? 'success' : customer.status === 'at-risk' ? 'warning' : 'error'}
                        size="small"
                        icon={customer.status === 'healthy' ? <TrendingUp /> : customer.status === 'at-risk' ? <Warning /> : <TrendingDown />}
                      />
                    </TableCell>
                    <TableCell>{customer.mrr}</TableCell>
                    <TableCell>{customer.lastContact}</TableCell>
                    <TableCell>{customer.csm}</TableCell>
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
              <Typography variant="h6" gutterBottom>Automated Playbooks</Typography>
              <Box sx={{ mt: 2 }}>
                {[
                  { playbook: 'Onboarding Sequence', active: 12, completed: 45 },
                  { playbook: 'At-Risk Intervention', active: 3, completed: 8 },
                  { playbook: 'Renewal Campaign', active: 18, completed: 67 },
                  { playbook: 'Upsell Opportunity', active: 7, completed: 23 }
                ].map((item, i) => (
                  <Box key={i} sx={{ mb: 2, p: 2, bgcolor: '#e3f2fd', borderRadius: 1 }}>
                    <Typography variant="body2" fontWeight="medium">{item.playbook}</Typography>
                    <Box sx={{ display: 'flex', gap: 2, mt: 0.5 }}>
                      <Chip label={`${item.active} active`} size="small" color="primary" />
                      <Chip label={`${item.completed} completed`} size="small" />
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
              <Typography variant="h6" gutterBottom>Churn Predictions</Typography>
              <Box sx={{ mt: 2 }}>
                {[
                  { customer: 'Innovation Labs', risk: 'High', probability: '78%', action: 'Schedule call' },
                  { customer: 'TechStart Inc', risk: 'Medium', probability: '45%', action: 'Send resources' },
                  { customer: 'Beta Systems', risk: 'Low', probability: '12%', action: 'Monitor' }
                ].map((item, i) => (
                  <Box key={i} sx={{ mb: 2, p: 2, bgcolor: item.risk === 'High' ? '#ffebee' : item.risk === 'Medium' ? '#fff3e0' : '#e8f5e9', borderRadius: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box>
                        <Typography variant="body2" fontWeight="medium">{item.customer}</Typography>
                        <Typography variant="caption" color="text.secondary">{item.action}</Typography>
                      </Box>
                      <Box sx={{ textAlign: 'right' }}>
                        <Chip label={`${item.risk} Risk`} size="small" color={item.risk === 'High' ? 'error' : item.risk === 'Medium' ? 'warning' : 'success'} />
                        <Typography variant="caption" display="block">{item.probability}</Typography>
                      </Box>
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

export default CustomerSuccessDashboard;