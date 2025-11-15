import React, { useEffect, useState } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box
} from '@mui/material';
import axios from 'axios';

function Dashboard() {
  const [stats, setStats] = useState({
    totalTickets: 0,
    openTickets: 0,
    integrations: 9,
    uptime: '99.9%'
  });

  useEffect(() => {
    // Fetch dashboard stats
    axios.get('/api/v1/info')
      .then(response => {
        console.log('API Info:', response.data);
      })
      .catch(error => {
        console.error('Error fetching stats:', error);
      });
  }, []);

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Tickets
              </Typography>
              <Typography variant="h4">
                {stats.totalTickets}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Open Tickets
              </Typography>
              <Typography variant="h4">
                {stats.openTickets}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Integrations
              </Typography>
              <Typography variant="h4">
                {stats.integrations}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                System Uptime
              </Typography>
              <Typography variant="h4">
                {stats.uptime}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Main Content */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Welcome to iTechSmart Enterprise
            </Typography>
            <Typography variant="body1" paragraph>
              Your production-ready infrastructure platform with AI integration and 
              multi-system connectivity.
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="textSecondary">
                • ServiceNow Integration: ✅ Active
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • Zendesk Integration: ✅ Active
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • IT Glue Integration: ✅ Active
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • N-able Integration: ✅ Active
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • ConnectWise Integration: ✅ Active
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • Jira Integration: ✅ Active
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • Slack/Teams Integration: ✅ Active
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • Prometheus Integration: ✅ Active
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • Wazuh Integration: ✅ Active
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard;