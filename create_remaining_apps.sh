#!/bin/bash

echo "Creating App.tsx files for remaining products..."

# Create Connect App
cat > itechsmart-connect/frontend/src/App.tsx << 'EOF'
import React from 'react';
import { Box, Grid, Card, CardContent, Typography, Button, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { Api as ApiIcon, Speed as SpeedIcon, Security as SecurityIcon, Code as CodeIcon } from '@mui/icons-material';

const ConnectDashboard: React.FC = () => {
  const apis = [
    { name: 'User API', version: 'v2.1', calls: '1.2M', latency: '45ms', status: 'healthy' },
    { name: 'Payment API', version: 'v1.5', calls: '850K', latency: '120ms', status: 'healthy' },
    { name: 'Analytics API', version: 'v3.0', calls: '2.1M', latency: '35ms', status: 'healthy' }
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
        <ApiIcon sx={{ mr: 2, fontSize: 40, color: '#1976d2' }} />
        Connect - API Management Platform
      </Typography>
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">45</Typography><Typography color="text.secondary">Active APIs</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">5.2M</Typography><Typography color="text.secondary">API Calls Today</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">65ms</Typography><Typography color="text.secondary">Avg Latency</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">99.9%</Typography><Typography color="text.secondary">Uptime</Typography></CardContent></Card></Grid>
      </Grid>
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Active APIs</Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>API Name</TableCell>
                  <TableCell>Version</TableCell>
                  <TableCell>Calls Today</TableCell>
                  <TableCell>Avg Latency</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {apis.map((api, i) => (
                  <TableRow key={i}>
                    <TableCell>{api.name}</TableCell>
                    <TableCell>{api.version}</TableCell>
                    <TableCell>{api.calls}</TableCell>
                    <TableCell>{api.latency}</TableCell>
                    <TableCell><Chip label={api.status} color="success" size="small" /></TableCell>
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

export default ConnectDashboard;
EOF

# Create Vault App
cat > itechsmart-vault/frontend/src/App.tsx << 'EOF'
import React from 'react';
import { Box, Grid, Card, CardContent, Typography, Button, Chip, List, ListItem, ListItemText } from '@mui/material';
import { Lock as LockIcon, Key as KeyIcon, VpnKey as VpnKeyIcon, Security as SecurityIcon } from '@mui/icons-material';

const VaultDashboard: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
        <LockIcon sx={{ mr: 2, fontSize: 40, color: '#1976d2' }} />
        Vault - Secrets & Configuration Management
      </Typography>
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">247</Typography><Typography color="text.secondary">Secrets Stored</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">45</Typography><Typography color="text.secondary">API Keys</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">12</Typography><Typography color="text.secondary">Certificates</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">AES-256</Typography><Typography color="text.secondary">Encryption</Typography></CardContent></Card></Grid>
      </Grid>
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Recent Activity</Typography>
              <List>
                {['Secret "db-password" rotated', 'New API key created', 'Certificate renewed', 'Access granted to user@example.com'].map((activity, i) => (
                  <ListItem key={i}><ListItemText primary={activity} secondary="2 hours ago" /></ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Security Status</Typography>
              <Box sx={{ mt: 2 }}>
                <Chip label="All Secrets Encrypted" color="success" sx={{ mr: 1, mb: 1 }} />
                <Chip label="Auto-Rotation Enabled" color="success" sx={{ mr: 1, mb: 1 }} />
                <Chip label="Audit Logging Active" color="success" sx={{ mr: 1, mb: 1 }} />
                <Chip label="Multi-Cloud Sync" color="info" sx={{ mr: 1, mb: 1 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default VaultDashboard;
EOF

# Create Notify App
cat > itechsmart-notify/frontend/src/App.tsx << 'EOF'
import React from 'react';
import { Box, Grid, Card, CardContent, Typography, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { Notifications as NotificationsIcon } from '@mui/icons-material';

const NotifyDashboard: React.FC = () => {
  const campaigns = [
    { name: 'Welcome Email', channel: 'Email', sent: '12.5K', delivered: '12.3K', opened: '8.2K', rate: '66%' },
    { name: 'Push Promo', channel: 'Push', sent: '45K', delivered: '43K', opened: '12K', rate: '28%' },
    { name: 'SMS Alert', channel: 'SMS', sent: '5.2K', delivered: '5.1K', opened: '4.8K', rate: '94%' }
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
        <NotificationsIcon sx={{ mr: 2, fontSize: 40, color: '#1976d2' }} />
        Notify - Omnichannel Notification Platform
      </Typography>
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">62.7K</Typography><Typography color="text.secondary">Sent Today</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">60.4K</Typography><Typography color="text.secondary">Delivered</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">25.0K</Typography><Typography color="text.secondary">Opened</Typography></CardContent></Card></Grid>
        <Grid item xs={3}><Card><CardContent><Typography variant="h4">96.3%</Typography><Typography color="text.secondary">Delivery Rate</Typography></CardContent></Card></Grid>
      </Grid>
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Active Campaigns</Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Campaign</TableCell>
                  <TableCell>Channel</TableCell>
                  <TableCell>Sent</TableCell>
                  <TableCell>Delivered</TableCell>
                  <TableCell>Opened</TableCell>
                  <TableCell>Open Rate</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {campaigns.map((c, i) => (
                  <TableRow key={i}>
                    <TableCell>{c.name}</TableCell>
                    <TableCell><Chip label={c.channel} size="small" /></TableCell>
                    <TableCell>{c.sent}</TableCell>
                    <TableCell>{c.delivered}</TableCell>
                    <TableCell>{c.opened}</TableCell>
                    <TableCell>{c.rate}</TableCell>
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

export default NotifyDashboard;
EOF

echo "✅ Created 3 more App.tsx files"
echo "Continuing with remaining products..."

# Create more apps in next batch...
EOF

chmod +x create_remaining_apps.sh
./create_remaining_apps.sh