import { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
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
  TrendingDown,
  Timeline as TimelineIcon,
  Notifications as NotificationsIcon,
  Description as DescriptionIcon,
  Warning as WarningIcon,
  Speed as SpeedIcon,
  CheckCircle,
  Error,
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

// Mock data - replace with actual API calls
const mockStats = {
  traces: { total: 45234, change: 12.5, trend: 'up' },
  alerts: { total: 23, change: -8.3, trend: 'down' },
  logs: { total: 892456, change: 5.2, trend: 'up' },
  incidents: { total: 5, change: -20.0, trend: 'down' },
  slos: { healthy: 12, warning: 2, critical: 1, breached: 0 },
};

const mockTraceData = [
  { time: '00:00', traces: 4200, errors: 120 },
  { time: '04:00', traces: 3800, errors: 95 },
  { time: '08:00', traces: 5600, errors: 180 },
  { time: '12:00', traces: 6800, errors: 220 },
  { time: '16:00', traces: 7200, errors: 195 },
  { time: '20:00', traces: 5400, errors: 145 },
];

const mockAlertData = [
  { name: 'Critical', value: 3, color: '#f44336' },
  { name: 'High', value: 8, color: '#ff9800' },
  { name: 'Medium', value: 9, color: '#ffc107' },
  { name: 'Low', value: 3, color: '#4caf50' },
];

const mockServiceHealth = [
  { service: 'itechsmart-enterprise', status: 'healthy', uptime: 99.9, latency: 45 },
  { service: 'itechsmart-ninja', status: 'healthy', uptime: 99.8, latency: 52 },
  { service: 'itechsmart-analytics', status: 'warning', uptime: 98.5, latency: 180 },
  { service: 'itechsmart-dataflow', status: 'healthy', uptime: 99.7, latency: 68 },
  { service: 'legalai-pro', status: 'healthy', uptime: 99.6, latency: 95 },
];

const mockActiveIncidents = [
  { id: 'INC-20241201-0001', title: 'High latency in Analytics service', severity: 'high', age: '2h 15m' },
  { id: 'INC-20241201-0002', title: 'Database connection pool exhausted', severity: 'critical', age: '45m' },
  { id: 'INC-20241201-0003', title: 'Increased error rate in API gateway', severity: 'medium', age: '1h 30m' },
];

export default function Dashboard() {
  const [loading, setLoading] = useState(false);

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 1000);
  };

  const StatCard = ({ title, value, change, trend, icon, color }: any) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography color="text.secondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" fontWeight={700}>
              {value.toLocaleString()}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
              {trend === 'up' ? (
                <TrendingUp sx={{ fontSize: 20, color: color === 'error' ? 'error.main' : 'success.main', mr: 0.5 }} />
              ) : (
                <TrendingDown sx={{ fontSize: 20, color: color === 'error' ? 'success.main' : 'error.main', mr: 0.5 }} />
              )}
              <Typography variant="body2" color={color === 'error' && trend === 'up' ? 'error.main' : 'success.main'}>
                {Math.abs(change)}% vs last hour
              </Typography>
            </Box>
          </Box>
          <Box
            sx={{
              bgcolor: `${color}.main`,
              borderRadius: 2,
              p: 1.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Observability Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Real-time monitoring across all 30 iTechSmart products
          </Typography>
        </Box>
        <Tooltip title="Refresh data">
          <IconButton onClick={handleRefresh} disabled={loading}>
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Traces (24h)"
            value={mockStats.traces.total}
            change={mockStats.traces.change}
            trend={mockStats.traces.trend}
            icon={<TimelineIcon sx={{ color: 'white' }} />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Alerts"
            value={mockStats.alerts.total}
            change={mockStats.alerts.change}
            trend={mockStats.alerts.trend}
            icon={<NotificationsIcon sx={{ color: 'white' }} />}
            color="error"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Logs (24h)"
            value={mockStats.logs.total}
            change={mockStats.logs.change}
            trend={mockStats.logs.trend}
            icon={<DescriptionIcon sx={{ color: 'white' }} />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Open Incidents"
            value={mockStats.incidents.total}
            change={mockStats.incidents.change}
            trend={mockStats.incidents.trend}
            icon={<WarningIcon sx={{ color: 'white' }} />}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Trace Volume Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Trace Volume & Error Rate (24h)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={mockTraceData}>
                  <defs>
                    <linearGradient id="colorTraces" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00bcd4" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#00bcd4" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorErrors" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f44336" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#f44336" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="time" stroke="rgba(255,255,255,0.5)" />
                  <YAxis stroke="rgba(255,255,255,0.5)" />
                  <RechartsTooltip
                    contentStyle={{ backgroundColor: '#132f4c', border: 'none', borderRadius: 8 }}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="traces"
                    stroke="#00bcd4"
                    fillOpacity={1}
                    fill="url(#colorTraces)"
                  />
                  <Area
                    type="monotone"
                    dataKey="errors"
                    stroke="#f44336"
                    fillOpacity={1}
                    fill="url(#colorErrors)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Alert Distribution */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Alert Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={mockAlertData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {mockAlertData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip
                    contentStyle={{ backgroundColor: '#132f4c', border: 'none', borderRadius: 8 }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Service Health & Incidents */}
      <Grid container spacing={3}>
        {/* Service Health */}
        <Grid item xs={12} md={7}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Service Health
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Service</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="right">Uptime</TableCell>
                      <TableCell align="right">Latency (ms)</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {mockServiceHealth.map((service) => (
                      <TableRow key={service.service}>
                        <TableCell>{service.service}</TableCell>
                        <TableCell>
                          <Chip
                            icon={service.status === 'healthy' ? <CheckCircle /> : <Error />}
                            label={service.status}
                            size="small"
                            color={service.status === 'healthy' ? 'success' : 'warning'}
                          />
                        </TableCell>
                        <TableCell align="right">{service.uptime}%</TableCell>
                        <TableCell align="right">
                          <Chip
                            label={service.latency}
                            size="small"
                            color={service.latency < 100 ? 'success' : service.latency < 200 ? 'warning' : 'error'}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Active Incidents */}
        <Grid item xs={12} md={5}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Active Incidents
              </Typography>
              <Box sx={{ mt: 2 }}>
                {mockActiveIncidents.map((incident) => (
                  <Box
                    key={incident.id}
                    sx={{
                      p: 2,
                      mb: 1,
                      borderRadius: 2,
                      bgcolor: 'rgba(255,255,255,0.05)',
                      '&:hover': { bgcolor: 'rgba(255,255,255,0.08)' },
                      cursor: 'pointer',
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Typography variant="body2" fontWeight={600}>
                        {incident.id}
                      </Typography>
                      <Chip
                        label={incident.severity}
                        size="small"
                        color={
                          incident.severity === 'critical'
                            ? 'error'
                            : incident.severity === 'high'
                            ? 'warning'
                            : 'info'
                        }
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {incident.title}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Open for {incident.age}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* SLO Status */}
      <Grid container spacing={3} sx={{ mt: 0 }}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                SLO Compliance Status
              </Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} sm={3}>
                  <Box sx={{ textAlign: 'center', p: 2, borderRadius: 2, bgcolor: 'rgba(76, 175, 80, 0.1)' }}>
                    <SpeedIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                    <Typography variant="h4" fontWeight={700} color="success.main">
                      {mockStats.slos.healthy}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Healthy
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={3}>
                  <Box sx={{ textAlign: 'center', p: 2, borderRadius: 2, bgcolor: 'rgba(255, 193, 7, 0.1)' }}>
                    <SpeedIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                    <Typography variant="h4" fontWeight={700} color="warning.main">
                      {mockStats.slos.warning}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Warning
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={3}>
                  <Box sx={{ textAlign: 'center', p: 2, borderRadius: 2, bgcolor: 'rgba(255, 152, 0, 0.1)' }}>
                    <SpeedIcon sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
                    <Typography variant="h4" fontWeight={700} color="error.main">
                      {mockStats.slos.critical}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Critical
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={3}>
                  <Box sx={{ textAlign: 'center', p: 2, borderRadius: 2, bgcolor: 'rgba(244, 67, 54, 0.1)' }}>
                    <SpeedIcon sx={{ fontSize: 40, color: 'error.dark', mb: 1 }} />
                    <Typography variant="h4" fontWeight={700} color="error.dark">
                      {mockStats.slos.breached}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Breached
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}