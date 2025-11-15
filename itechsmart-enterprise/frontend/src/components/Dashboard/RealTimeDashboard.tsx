"""
iTechSmart Enterprise - Real-Time Dashboard Component
React component for displaying real-time suite monitoring and analytics
"""

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Badge
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  CheckCircle as HealthyIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  Sync as SyncIcon,
  Notifications as NotificationsIcon
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface DashboardData {
  timestamp: string;
  products: {
    total_products: number;
    active_products: number;
    inactive_products: number;
    products: Array<{
      id: number;
      name: string;
      type: string;
      status: string;
      version: string;
      uptime: string;
      health_score: number;
    }>;
  };
  health: {
    overall_status: string;
    healthy_services: number;
    degraded_services: number;
    unhealthy_services: number;
    average_response_time: number;
  };
  activity: {
    total_events_24h: number;
    events_by_type: Record<string, number>;
    total_syncs_24h: number;
    successful_syncs: number;
    failed_syncs: number;
    active_workflows: number;
    data_transferred_mb: number;
  };
  performance: {
    average_response_time: number;
    p95_response_time: number;
    p99_response_time: number;
    error_rate: number;
  };
  alerts: Array<{
    severity: string;
    type: string;
    service: string;
    message: string;
    timestamp: string;
  }>;
  trends: {
    health_trend: Record<string, any>;
    sync_trend: Record<string, any>;
  };
}

const COLORS = {
  healthy: '#4caf50',
  degraded: '#ff9800',
  unhealthy: '#f44336',
  primary: '#2196f3',
  secondary: '#9c27b0'
};

export const RealTimeDashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/dashboard/overview');
      const result = await response.json();
      setData(result);
      setLastUpdate(new Date());
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  // WebSocket connection for real-time updates
  useEffect(() => {
    fetchDashboardData();

    if (autoRefresh) {
      const ws = new WebSocket('ws://localhost:8000/api/dashboard/ws/realtime');
      
      ws.onmessage = (event) => {
        const update = JSON.parse(event.data);
        if (update.type === 'metrics_update') {
          // Update real-time metrics without full refresh
          setLastUpdate(new Date());
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      return () => {
        ws.close();
      };
    }
  }, [autoRefresh]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchDashboardData, 30000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  if (loading || !data) {
    return (
      <Box sx={{ width: '100%', p: 3 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2 }}>Loading dashboard...</Typography>
      </Box>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <HealthyIcon sx={{ color: COLORS.healthy }} />;
      case 'degraded':
        return <WarningIcon sx={{ color: COLORS.degraded }} />;
      case 'unhealthy':
      case 'critical':
        return <ErrorIcon sx={{ color: COLORS.unhealthy }} />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'active':
        return COLORS.healthy;
      case 'degraded':
        return COLORS.degraded;
      case 'unhealthy':
      case 'critical':
      case 'inactive':
        return COLORS.unhealthy;
      default:
        return '#757575';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          iTechSmart Suite Dashboard
        </Typography>
        <Box>
          <Typography variant="caption" sx={{ mr: 2 }}>
            Last updated: {lastUpdate.toLocaleTimeString()}
          </Typography>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchDashboardData} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Overall Health Status */}
      <Alert
        severity={
          data.health.overall_status === 'healthy' ? 'success' :
          data.health.overall_status === 'degraded' ? 'warning' : 'error'
        }
        icon={getStatusIcon(data.health.overall_status)}
        sx={{ mb: 3 }}
      >
        <Typography variant="h6">
          System Status: {data.health.overall_status.toUpperCase()}
        </Typography>
        <Typography variant="body2">
          {data.products.active_products} of {data.products.total_products} products active
        </Typography>
      </Alert>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <HealthyIcon sx={{ color: COLORS.healthy, mr: 1 }} />
                <Typography variant="h6">Products</Typography>
              </Box>
              <Typography variant="h3">{data.products.active_products}</Typography>
              <Typography variant="body2" color="text.secondary">
                {data.products.total_products} total
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <SpeedIcon sx={{ color: COLORS.primary, mr: 1 }} />
                <Typography variant="h6">Response Time</Typography>
              </Box>
              <Typography variant="h3">
                {data.performance.average_response_time}ms
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Average
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <SyncIcon sx={{ color: COLORS.secondary, mr: 1 }} />
                <Typography variant="h6">Syncs (24h)</Typography>
              </Box>
              <Typography variant="h3">{data.activity.total_syncs_24h}</Typography>
              <Typography variant="body2" color="text.secondary">
                {data.activity.successful_syncs} successful
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Badge badgeContent={data.alerts.length} color="error">
                  <NotificationsIcon sx={{ color: COLORS.degraded, mr: 1 }} />
                </Badge>
                <Typography variant="h6">Alerts</Typography>
              </Box>
              <Typography variant="h3">{data.alerts.length}</Typography>
              <Typography variant="body2" color="text.secondary">
                Active issues
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Products Table */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Integrated Products
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Product</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Version</TableCell>
                  <TableCell>Health Score</TableCell>
                  <TableCell>Uptime</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.products.products.map((product) => (
                  <TableRow key={product.id}>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {product.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={product.type} size="small" />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={product.status}
                        size="small"
                        sx={{
                          backgroundColor: getStatusColor(product.status),
                          color: 'white'
                        }}
                      />
                    </TableCell>
                    <TableCell>{product.version}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box sx={{ width: '100%', mr: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={product.health_score}
                            sx={{
                              backgroundColor: '#e0e0e0',
                              '& .MuiLinearProgress-bar': {
                                backgroundColor: getStatusColor(
                                  product.health_score > 80 ? 'healthy' :
                                  product.health_score > 50 ? 'degraded' : 'unhealthy'
                                )
                              }
                            }}
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {product.health_score}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{product.uptime}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Health Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Health Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Healthy', value: data.health.healthy_services },
                      { name: 'Degraded', value: data.health.degraded_services },
                      { name: 'Unhealthy', value: data.health.unhealthy_services }
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    <Cell fill={COLORS.healthy} />
                    <Cell fill={COLORS.degraded} />
                    <Cell fill={COLORS.unhealthy} />
                  </Pie>
                  <ChartTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Activity Overview */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Activity Overview (24h)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={Object.entries(data.activity.events_by_type).map(([key, value]) => ({
                    name: key,
                    count: value
                  }))}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <ChartTooltip />
                  <Bar dataKey="count" fill={COLORS.primary} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Active Alerts */}
      {data.alerts.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Active Alerts
            </Typography>
            {data.alerts.map((alert, index) => (
              <Alert
                key={index}
                severity={
                  alert.severity === 'critical' ? 'error' :
                  alert.severity === 'warning' ? 'warning' : 'info'
                }
                sx={{ mb: 1 }}
              >
                <Typography variant="body2" fontWeight="bold">
                  {alert.service} - {alert.type}
                </Typography>
                <Typography variant="body2">{alert.message}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(alert.timestamp).toLocaleString()}
                </Typography>
              </Alert>
            ))}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default RealTimeDashboard;