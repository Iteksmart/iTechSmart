import React from 'react';
import { Box, Grid, Card, CardContent, Typography, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, IconButton } from '@mui/material';
import { Code as DevOpsIcon, PlayArrow, Stop, Refresh, CheckCircle, Error } from '@mui/icons-material';

const DevOpsDashboard: React.FC = () => {
  const pipelines = [
    { name: 'Frontend Build', status: 'success', duration: '3m 45s', branch: 'main', commit: 'a1b2c3d', lastRun: '5 min ago' },
    { name: 'Backend Deploy', status: 'running', duration: '2m 12s', branch: 'develop', commit: 'e4f5g6h', lastRun: 'Running' },
    { name: 'Integration Tests', status: 'success', duration: '8m 30s', branch: 'main', commit: 'a1b2c3d', lastRun: '15 min ago' },
    { name: 'Security Scan', status: 'failed', duration: '1m 05s', branch: 'feature/auth', commit: 'i7j8k9l', lastRun: '1 hour ago' }
  ];

  return (
    <Box sx={{ p: 3, bgcolor: '#f5f5f5', minHeight: '100vh' }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <DevOpsIcon sx={{ mr: 2, fontSize: 40, color: '#1976d2' }} />
            DevOps - CI/CD Automation Platform
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Continuous integration and deployment automation
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<PlayArrow />} size="large">Run Pipeline</Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">24</Typography><Typography color="text.secondary">Active Pipelines</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">156</Typography><Typography color="text.secondary">Builds Today</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">94.2%</Typography><Typography color="text.secondary">Success Rate</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">4m 32s</Typography><Typography color="text.secondary">Avg Duration</Typography></CardContent></Card></Grid>
      </Grid>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>CI/CD Pipelines</Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Pipeline</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Branch</TableCell>
                  <TableCell>Commit</TableCell>
                  <TableCell>Last Run</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {pipelines.map((pipeline, i) => (
                  <TableRow key={i}>
                    <TableCell>{pipeline.name}</TableCell>
                    <TableCell>
                      <Chip 
                        label={pipeline.status} 
                        color={pipeline.status === 'success' ? 'success' : pipeline.status === 'running' ? 'info' : 'error'}
                        size="small"
                        icon={pipeline.status === 'success' ? <CheckCircle /> : pipeline.status === 'failed' ? <Error /> : undefined}
                      />
                    </TableCell>
                    <TableCell>{pipeline.duration}</TableCell>
                    <TableCell><Chip label={pipeline.branch} size="small" variant="outlined" /></TableCell>
                    <TableCell><Typography variant="body2" fontFamily="monospace">{pipeline.commit}</Typography></TableCell>
                    <TableCell>{pipeline.lastRun}</TableCell>
                    <TableCell align="right">
                      <IconButton size="small" color="primary"><PlayArrow fontSize="small" /></IconButton>
                      <IconButton size="small" color="error"><Stop fontSize="small" /></IconButton>
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
              <Typography variant="h6" gutterBottom>Deployment Environments</Typography>
              <Box sx={{ mt: 2 }}>
                {[
                  { env: 'Production', status: 'healthy', version: 'v2.1.0', deployed: '2 hours ago' },
                  { env: 'Staging', status: 'healthy', version: 'v2.2.0-rc1', deployed: '30 min ago' },
                  { env: 'Development', status: 'healthy', version: 'v2.2.0-dev', deployed: '5 min ago' }
                ].map((item, i) => (
                  <Box key={i} sx={{ display: 'flex', justifyContent: 'space-between', mb: 2, p: 2, bgcolor: '#e8f5e9', borderRadius: 1 }}>
                    <Box>
                      <Typography variant="body2" fontWeight="medium">{item.env}</Typography>
                      <Typography variant="caption" color="text.secondary">{item.version}</Typography>
                    </Box>
                    <Box sx={{ textAlign: 'right' }}>
                      <Chip label={item.status} color="success" size="small" />
                      <Typography variant="caption" display="block" color="text.secondary">{item.deployed}</Typography>
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
              <Typography variant="h6" gutterBottom>Recent Deployments</Typography>
              <Box sx={{ mt: 2 }}>
                {[
                  'Frontend v2.1.0 deployed to production',
                  'Backend API v1.8.5 deployed to staging',
                  'Database migration completed',
                  'Security patches applied',
                  'Configuration updated'
                ].map((activity, i) => (
                  <Typography key={i} variant="body2" sx={{ mb: 1.5 }} color="text.secondary">
                    ✓ {activity}
                  </Typography>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DevOpsDashboard;