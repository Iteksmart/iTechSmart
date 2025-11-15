import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  Speed,
  Error,
  CheckCircle,
  Warning,
  Visibility,
  Refresh,
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
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useNavigate } from 'react-router-dom';

interface DashboardStats {
  total_services: number;
  active_alerts: number;
  total_traces: number;
  error_rate: number;
  avg_response_time: number;
  healthy_services: number;
  degraded_services: number;
  unhealthy_services: number;
}

interface ServiceHealth {
  id: string;
  name: string;
  health_status: string;
  last_seen: string;
  error_count: number;
  avg_latency: number;
}

const ObservatoryDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [services, setServices] = useState<ServiceHealth[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('1h');
  const [metricsData, setMetricsData] = useState<any[]>([]);
  const [errorRateData, setErrorRateData] = useState<any[]>([]);

  const COLORS = ['#00C49F', '#FFBB28', '#FF8042', '#0088FE', '#8884D8'];

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch dashboard stats
      const statsResponse = await fetch('/api/observatory/dashboard/stats');
      const statsData = await statsResponse.json();
      setStats(statsData);

      // Fetch services
      const servicesResponse = await fetch('/api/observatory/services');
      const servicesData = await servicesResponse.json();
      setServices(servicesData.services || []);

      // Generate mock time-series data (replace with actual API calls)
      generateMockData();
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = () => {
    // Mock metrics data
    const metrics = Array.from({ length: 20 }, (_, i) => ({
      time: `${i}:00`,
      requests: Math.floor(Math.random() * 1000) + 500,
      latency: Math.floor(Math.random() * 200) + 50,
      errors: Math.floor(Math.random() * 50),
    }));
    setMetricsData(metrics);

    // Mock error rate data
    const errorRate = Array.from({ length: 20 }, (_, i) => ({
      time: `${i}:00`,
      rate: Math.random() * 5,
    }));
    setErrorRateData(errorRate);
  };

  const getHealthColor = (status: string) => {
    const colors: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
      healthy: 'success',
      degraded: 'warning',
      unhealthy: 'error',
      unknown: 'default',
    };
    return colors[status] || 'default';
  };

  const getHealthIcon = (status: string) => {
    const icons: Record<string, React.ReactElement> = {
      healthy: <CheckCircle />,
      degraded: <Warning />,
      unhealthy: <Error />,
    };
    return icons[status] || <CheckCircle />;
  };

  if (loading && !stats) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Observatory Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value)}
              size="small"
            >
              <MenuItem value="5m">Last 5 min</MenuItem>
              <MenuItem value="15m">Last 15 min</MenuItem>
              <MenuItem value="1h">Last 1 hour</MenuItem>
              <MenuItem value="6h">Last 6 hours</MenuItem>
              <MenuItem value="24h">Last 24 hours</MenuItem>
              <MenuItem value="7d">Last 7 days</MenuItem>
            </Select>
          </FormControl>
          <IconButton onClick={fetchDashboardData}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckCircle color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Services</Typography>
              </Box>
              <Typography variant="h3">{stats?.total_services || 0}</Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                <Chip label={`${stats?.healthy_services || 0} Healthy`} color="success" size="small" />
                <Chip label={`${stats?.degraded_services || 0} Degraded`} color="warning" size="small" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Warning color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Active Alerts</Typography>
              </Box>
              <Typography variant="h3">{stats?.active_alerts || 0}</Typography>
              <Typography variant="body2" color="text.secondary">
                Requires attention
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Speed color="info" sx={{ mr: 1 }} />
                <Typography variant="h6">Avg Response Time</Typography>
              </Box>
              <Typography variant="h3">
                {stats?.avg_response_time ? `${stats.avg_response_time.toFixed(0)}ms` : 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Across all services
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Error color="error" sx={{ mr: 1 }} />
                <Typography variant="h6">Error Rate</Typography>
              </Box>
              <Typography variant="h3">
                {stats?.error_rate ? `${stats.error_rate.toFixed(2)}%` : '0%'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last {timeRange}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Request Volume */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Request Volume & Latency
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={metricsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <RechartsTooltip />
                  <Legend />
                  <Area
                    yAxisId="left"
                    type="monotone"
                    dataKey="requests"
                    stroke="#8884d8"
                    fill="#8884d8"
                    fillOpacity={0.6}
                    name="Requests"
                  />
                  <Area
                    yAxisId="right"
                    type="monotone"
                    dataKey="latency"
                    stroke="#82ca9d"
                    fill="#82ca9d"
                    fillOpacity={0.6}
                    name="Latency (ms)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Service Health Distribution */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Service Health
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Healthy', value: stats?.healthy_services || 0 },
                      { name: 'Degraded', value: stats?.degraded_services || 0 },
                      { name: 'Unhealthy', value: stats?.unhealthy_services || 0 },
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {[0, 1, 2].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Error Rate Trend */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Error Rate Trend
              </Typography>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={errorRateData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="rate"
                    stroke="#ff7300"
                    strokeWidth={2}
                    name="Error Rate (%)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Services Table */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Services Overview</Typography>
            <Chip label={`${services.length} Services`} color="primary" />
          </Box>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Service Name</TableCell>
                  <TableCell>Health Status</TableCell>
                  <TableCell>Avg Latency</TableCell>
                  <TableCell>Error Count</TableCell>
                  <TableCell>Last Seen</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {services.length > 0 ? (
                  services.slice(0, 10).map((service) => (
                    <TableRow key={service.id} hover>
                      <TableCell>
                        <Typography variant="body1" fontWeight="medium">
                          {service.name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={getHealthIcon(service.health_status)}
                          label={service.health_status.toUpperCase()}
                          color={getHealthColor(service.health_status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{service.avg_latency ? `${service.avg_latency}ms` : 'N/A'}</TableCell>
                      <TableCell>
                        <Chip
                          label={service.error_count || 0}
                          color={service.error_count > 0 ? 'error' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {service.last_seen
                          ? new Date(service.last_seen).toLocaleString()
                          : 'Never'}
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => navigate(`/observatory/services/${service.id}`)}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No services registered
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ObservatoryDashboard;