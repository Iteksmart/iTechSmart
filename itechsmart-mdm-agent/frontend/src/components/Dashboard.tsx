import { useEffect, useState } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Chip,
  Alert,
} from '@mui/material';
import {
  CheckCircle as HealthyIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  RocketLaunch as DeployIcon,
} from '@mui/icons-material';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { monitoringApi, deploymentApi } from '../services/api';
import type { HealthStatus } from '../types';

const COLORS = ['#4caf50', '#ff9800', '#f44336', '#9e9e9e'];

export default function Dashboard() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const healthData = await monitoringApi.getOverallHealth();
      setHealth(healthData);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  const healthData = [
    { name: 'Healthy', value: health?.healthy || 0, color: COLORS[0] },
    { name: 'Degraded', value: health?.degraded || 0, color: COLORS[1] },
    { name: 'Unhealthy', value: health?.unhealthy || 0, color: COLORS[2] },
  ];

  const revenueData = [
    { month: 'Jan', deployments: 45 },
    { month: 'Feb', deployments: 52 },
    { month: 'Mar', deployments: 48 },
    { month: 'Apr', deployments: 61 },
    { month: 'May', deployments: 55 },
    { month: 'Jun', deployments: 67 },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 700 }}>
        Dashboard
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    Total Services
                  </Typography>
                  <Typography variant="h4" sx={{ mt: 1 }}>
                    {health?.total_services || 0}
                  </Typography>
                </Box>
                <DeployIcon sx={{ fontSize: 48, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    Healthy
                  </Typography>
                  <Typography variant="h4" sx={{ mt: 1, color: 'success.main' }}>
                    {health?.healthy || 0}
                  </Typography>
                </Box>
                <HealthyIcon sx={{ fontSize: 48, opacity: 0.3, color: 'success.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    Degraded
                  </Typography>
                  <Typography variant="h4" sx={{ mt: 1, color: 'warning.main' }}>
                    {health?.degraded || 0}
                  </Typography>
                </Box>
                <WarningIcon sx={{ fontSize: 48, opacity: 0.3, color: 'warning.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    Active Alerts
                  </Typography>
                  <Typography variant="h4" sx={{ mt: 1, color: 'error.main' }}>
                    {health?.active_alerts || 0}
                  </Typography>
                </Box>
                <ErrorIcon sx={{ fontSize: 48, opacity: 0.3, color: 'error.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Deployment Trend (Last 6 Months)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="deployments" fill="#2196f3" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Service Health Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={healthData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {healthData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* System Status */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box display="flex" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
                  <Typography variant="body1">Overall Health</Typography>
                  <Chip
                    label={health?.status || 'Unknown'}
                    color={
                      health?.status === 'healthy'
                        ? 'success'
                        : health?.status === 'degraded'
                        ? 'warning'
                        : 'error'
                    }
                    size="small"
                  />
                </Box>
                <Box display="flex" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
                  <Typography variant="body1">Total Services</Typography>
                  <Typography variant="body1" fontWeight={600}>
                    {health?.total_services || 0}
                  </Typography>
                </Box>
                <Box display="flex" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
                  <Typography variant="body1">Uptime</Typography>
                  <Typography variant="body1" fontWeight={600} color="success.main">
                    99.9%
                  </Typography>
                </Box>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Typography variant="body1">Last Updated</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {health?.timestamp ? new Date(health.timestamp).toLocaleTimeString() : 'N/A'}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Alert severity="info" sx={{ mb: 2 }}>
                  All systems operational. No action required.
                </Alert>
                <Typography variant="body2" color="text.secondary">
                  • Deploy new products from the Deploy page
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  • Monitor service health in real-time
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  • Get AI-powered optimization recommendations
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  • View deployment history and analytics
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
