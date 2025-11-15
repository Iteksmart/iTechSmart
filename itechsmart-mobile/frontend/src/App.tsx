import React from 'react';
import { Box, Grid, Card, CardContent, Typography, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, LinearProgress, IconButton } from '@mui/material';
import { PhoneAndroid as MobileIcon, PlayArrow as PlayIcon, Pause as PauseIcon, Build as BuildIcon, CloudUpload as UploadIcon } from '@mui/icons-material';

const MobileDashboard: React.FC = () => {
  const apps = [
    { name: 'iTechSmart Mobile App', platform: 'iOS', version: '2.1.0', status: 'production', users: '125K', builds: 45 },
    { name: 'Customer Portal', platform: 'Android', version: '1.8.5', status: 'production', users: '89K', builds: 38 },
    { name: 'Admin Dashboard', platform: 'React Native', version: '3.0.2', status: 'staging', users: '2.5K', builds: 67 },
    { name: 'Analytics App', platform: 'Flutter', version: '1.5.0', status: 'development', users: '0', builds: 12 }
  ];

  return (
    <Box sx={{ p: 3, bgcolor: '#f5f5f5', minHeight: '100vh' }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <MobileIcon sx={{ mr: 2, fontSize: 40, color: '#1976d2' }} />
            Mobile - Mobile Application Platform
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Multi-platform mobile development and deployment
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<BuildIcon />} size="large">New Build</Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">12</Typography><Typography color="text.secondary">Active Apps</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">216K</Typography><Typography color="text.secondary">Total Users</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">162</Typography><Typography color="text.secondary">Total Builds</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">98.5%</Typography><Typography color="text.secondary">Success Rate</Typography></CardContent></Card></Grid>
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>Mobile Applications</Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>App Name</TableCell>
                  <TableCell>Platform</TableCell>
                  <TableCell>Version</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Users</TableCell>
                  <TableCell>Builds</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {apps.map((app, i) => (
                  <TableRow key={i}>
                    <TableCell>{app.name}</TableCell>
                    <TableCell><Chip label={app.platform} size="small" /></TableCell>
                    <TableCell>{app.version}</TableCell>
                    <TableCell><Chip label={app.status} color={app.status === 'production' ? 'success' : app.status === 'staging' ? 'warning' : 'default'} size="small" /></TableCell>
                    <TableCell>{app.users}</TableCell>
                    <TableCell>{app.builds}</TableCell>
                    <TableCell align="right">
                      <IconButton size="small" color="primary"><BuildIcon fontSize="small" /></IconButton>
                      <IconButton size="small"><UploadIcon fontSize="small" /></IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default MobileDashboard;