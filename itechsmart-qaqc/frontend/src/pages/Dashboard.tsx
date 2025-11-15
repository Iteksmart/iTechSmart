import { useEffect, useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const COLORS = ['#4caf50', '#f44336', '#ff9800', '#2196f3'];

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalProducts: 28,
    activeProducts: 28,
    totalChecks: 1120,
    passedChecks: 1054,
    failedChecks: 42,
    warningChecks: 24,
    overallScore: 94.1,
    openAlerts: 15,
  });

  const [productScores] = useState([
    { name: 'Enterprise', score: 98 },
    { name: 'Ninja', score: 99 },
    { name: 'Analytics', score: 96 },
    { name: 'DataFlow', score: 95 },
    { name: 'Pulse', score: 94 },
    { name: 'Shield', score: 97 },
  ]);

  const [checkDistribution] = useState([
    { name: 'Passed', value: 1054, color: '#4caf50' },
    { name: 'Failed', value: 42, color: '#f44336' },
    { name: 'Warning', value: 24, color: '#ff9800' },
  ]);

  const [recentScans] = useState([
    { id: 1, type: 'Full Suite', status: 'completed', score: 94.1, time: '2 hours ago' },
    { id: 2, type: 'Security', status: 'completed', score: 97.2, time: '5 hours ago' },
    { id: 3, type: 'Performance', status: 'running', score: null, time: 'In progress' },
  ]);

  const [recentAlerts] = useState([
    { id: 1, severity: 'high', message: 'API response time exceeded threshold', product: 'DataFlow' },
    { id: 2, severity: 'medium', message: 'Documentation outdated', product: 'Connect' },
    { id: 3, severity: 'low', message: 'Code coverage below 80%', product: 'Vault' },
  ]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        Real-time overview of QA/QC system status
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Active Products
              </Typography>
              <Typography variant="h3">
                {stats.activeProducts}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                of {stats.totalProducts} total
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Overall QA Score
              </Typography>
              <Typography variant="h3" color="success.main">
                {stats.overallScore}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={stats.overallScore}
                sx={{ mt: 1 }}
                color="success"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Checks
              </Typography>
              <Typography variant="h3">
                {stats.totalChecks}
              </Typography>
              <Typography variant="body2" color="success.main">
                {stats.passedChecks} passed
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Open Alerts
              </Typography>
              <Typography variant="h3" color="warning.main">
                {stats.openAlerts}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Requires attention
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Product QA Scores
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={productScores}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="score" fill="#2196f3" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Check Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={checkDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {checkDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Activity */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Scans
            </Typography>
            <List>
              {recentScans.map((scan) => (
                <ListItem key={scan.id}>
                  <ListItemIcon>
                    {scan.status === 'completed' ? (
                      <CheckIcon color="success" />
                    ) : (
                      <TrendingUpIcon color="primary" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={scan.type}
                    secondary={
                      <>
                        {scan.score && `Score: ${scan.score}% • `}
                        {scan.time}
                      </>
                    }
                  />
                  <Chip
                    label={scan.status}
                    color={scan.status === 'completed' ? 'success' : 'primary'}
                    size="small"
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Alerts
            </Typography>
            <List>
              {recentAlerts.map((alert) => (
                <ListItem key={alert.id}>
                  <ListItemIcon>
                    {alert.severity === 'high' ? (
                      <ErrorIcon color="error" />
                    ) : alert.severity === 'medium' ? (
                      <WarningIcon color="warning" />
                    ) : (
                      <WarningIcon color="info" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={alert.message}
                    secondary={alert.product}
                  />
                  <Chip
                    label={alert.severity}
                    color={getSeverityColor(alert.severity) as any}
                    size="small"
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}