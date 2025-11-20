import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Typography,
  Grid,
  Button,
  Chip,
  Switch,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Alert,
  AlertTitle,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Tooltip,
} from '@mui/material';
import {
  Refresh,
  Add,
  Edit,
  Delete,
  Security,
  Speed,
  Settings,
  Visibility,
  Code,
  Http,
  Assessment,
  Warning,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import { LoadingButton } from '@mui/lab';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

interface GatewayConfig {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  rateLimit: {
    requests: number;
    window: number;
  };
  authentication: {
    type: 'none' | 'basic' | 'jwt' | 'oauth2';
    config: Record<string, any>;
  };
  routes: RouteConfig[];
  createdAt: string;
  updatedAt: string;
}

interface RouteConfig {
  id: string;
  path: string;
  method: string[];
  upstream: string;
  stripPath: boolean;
  timeout: number;
  retries: number;
  plugins: PluginConfig[];
}

interface PluginConfig {
  name: string;
  enabled: boolean;
  config: Record<string, any>;
}

interface Metric {
  timestamp: string;
  requests: number;
  errors: number;
  latency: number;
  throughput: number;
}

interface GatewayStats {
  totalRequests: number;
  totalErrors: number;
  avgLatency: number;
  uptime: number;
  activeConnections: number;
  blockedRequests: number;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`gateway-tabpanel-${index}`}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

const GatewayAdminDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [gatewayConfigs, setGatewayConfigs] = useState<GatewayConfig[]>([]);
  const [selectedConfig, setSelectedConfig] = useState<GatewayConfig | null>(null);
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [stats, setStats] = useState<GatewayStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [editingConfig, setEditingConfig] = useState<GatewayConfig | null>(null);

  // Colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  // Load initial data
  useEffect(() => {
    loadGatewayConfigs();
    loadMetrics();
    loadStats();
  }, []);

  const loadGatewayConfigs = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setGatewayConfigs([
        {
          id: '1',
          name: 'iTechSmart API Gateway',
          description: 'Main API gateway for iTechSmart services',
          enabled: true,
          rateLimit: { requests: 1000, window: 60 },
          authentication: {
            type: 'jwt',
            config: { secretKey: 'jwt-secret-key' },
          },
          routes: [
            {
              id: 'r1',
              path: '/api/v1/*',
              method: ['GET', 'POST', 'PUT', 'DELETE'],
              upstream: 'http://api-service:8080',
              stripPath: true,
              timeout: 30000,
              retries: 3,
              plugins: [
                { name: 'rate-limiting', enabled: true, config: { minute: 60, hour: 1000 } },
                { name: 'cors', enabled: true, config: { origins: ['*'] } },
              ],
            },
          ],
          createdAt: '2024-01-15T10:00:00Z',
          updatedAt: '2024-01-20T15:30:00Z',
        },
        {
          id: '2',
          name: 'Internal Services Gateway',
          description: 'Gateway for internal microservices communication',
          enabled: true,
          rateLimit: { requests: 5000, window: 60 },
          authentication: {
            type: 'oauth2',
            config: { clientId: 'internal-client' },
          },
          routes: [
            {
              id: 'r2',
              path: '/internal/*',
              method: ['*'],
              upstream: 'http://internal-service:8081',
              stripPath: false,
              timeout: 60000,
              retries: 5,
              plugins: [],
            },
          ],
          createdAt: '2024-01-10T09:00:00Z',
          updatedAt: '2024-01-18T12:00:00Z',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const loadMetrics = async () => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      const now = Date.now();
      const mockMetrics: Metric[] = Array.from({ length: 24 }, (_, i) => ({
        timestamp: new Date(now - (23 - i) * 3600000).toISOString(),
        requests: Math.floor(Math.random() * 1000) + 500,
        errors: Math.floor(Math.random() * 50),
        latency: Math.floor(Math.random() * 200) + 50,
        throughput: Math.floor(Math.random() * 100) + 50,
      }));
      setMetrics(mockMetrics);
    } catch (error) {
      console.error('Failed to load metrics:', error);
    }
  };

  const loadStats = async () => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      setStats({
        totalRequests: 45678,
        totalErrors: 234,
        avgLatency: 125,
        uptime: 99.98,
        activeConnections: 156,
        blockedRequests: 89,
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleRefresh = useCallback(() => {
    loadGatewayConfigs();
    loadMetrics();
    loadStats();
  }, []);

  const handleToggleConfig = async (configId: string, enabled: boolean) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      setGatewayConfigs(prev =>
        prev.map(config =>
          config.id === configId ? { ...config, enabled } : config
        )
      );
    } catch (error) {
      console.error('Failed to toggle config:', error);
    }
  };

  const handleDeleteConfig = async (configId: string) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      setGatewayConfigs(prev => prev.filter(config => config.id !== configId));
    } catch (error) {
      console.error('Failed to delete config:', error);
    }
  };

  const handleSaveConfig = async (config: GatewayConfig) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      if (editingConfig) {
        setGatewayConfigs(prev =>
          prev.map(c => (c.id === config.id ? { ...config, updatedAt: new Date().toISOString() } : c))
        );
      } else {
        setGatewayConfigs(prev => [
          ...prev,
          { ...config, id: Date.now().toString(), createdAt: new Date().toISOString() },
        ]);
      }
      setConfigDialogOpen(false);
      setEditingConfig(null);
    } catch (error) {
      console.error('Failed to save config:', error);
    }
  };

  const getStatusColor = (enabled: boolean) => {
    return enabled ? 'success' : 'error';
  };

  const getStatusIcon = (enabled: boolean) => {
    return enabled ? <CheckCircle color="success" /> : <Error color="error" />;
  };

  return (
    <Box sx={{ width: '100%', height: '100vh', overflow: 'hidden' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h4" component="h1">
            iTechSmart Gateway Admin
          </Typography>
          <LoadingButton
            loading={loading}
            onClick={handleRefresh}
            startIcon={<Refresh />}
            variant="outlined"
          >
            Refresh
          </LoadingButton>
        </Stack>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab icon={<Assessment />} label="Overview" />
          <Tab icon={<Settings />} label="Configurations" />
          <Tab icon={<Speed />} label="Metrics" />
          <Tab icon={<Security />} label="Security" />
          <Tab icon={<Code />} label="API Routes" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          {/* Stats Cards */}
          {stats && (
            <>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Stack direction="row" alignItems="center" spacing={2}>
                      <Http color="primary" />
                      <Box>
                        <Typography variant="h4">{stats.totalRequests.toLocaleString()}</Typography>
                        <Typography color="text.secondary">Total Requests</Typography>
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Stack direction="row" alignItems="center" spacing={2}>
                      <Error color="error" />
                      <Box>
                        <Typography variant="h4">{stats.totalErrors}</Typography>
                        <Typography color="text.secondary">Total Errors</Typography>
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Stack direction="row" alignItems="center" spacing={2}>
                      <Speed color="info" />
                      <Box>
                        <Typography variant="h4">{stats.avgLatency}ms</Typography>
                        <Typography color="text.secondary">Avg Latency</Typography>
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Stack direction="row" alignItems="center" spacing={2}>
                      <CheckCircle color="success" />
                      <Box>
                        <Typography variant="h4">{stats.uptime}%</Typography>
                        <Typography color="text.secondary">Uptime</Typography>
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            </>
          )}

          {/* Request Trends Chart */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardHeader title="Request Trends (Last 24 Hours)" />
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={metrics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="timestamp" />
                    <YAxis />
                    <RechartsTooltip />
                    <Line type="monotone" dataKey="requests" stroke="#8884d8" name="Requests" />
                    <Line type="monotone" dataKey="errors" stroke="#82ca9d" name="Errors" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Latency Distribution */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardHeader title="Latency Distribution" />
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={metrics.slice(-12)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="timestamp" />
                    <YAxis />
                    <RechartsTooltip />
                    <Bar dataKey="latency" fill="#ffc658" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Box>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="h5">Gateway Configurations</Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => {
                setEditingConfig(null);
                setConfigDialogOpen(true);
              }}
            >
              Add Configuration
            </Button>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Rate Limit</TableCell>
                  <TableCell>Auth Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {gatewayConfigs.map((config) => (
                  <TableRow key={config.id}>
                    <TableCell>
                      <Stack direction="row" alignItems="center" spacing={1}>
                        {getStatusIcon(config.enabled)}
                        <Typography fontWeight="bold">{config.name}</Typography>
                      </Stack>
                    </TableCell>
                    <TableCell>{config.description}</TableCell>
                    <TableCell>
                      {config.rateLimit.requests}/{config.rateLimit.window}s
                    </TableCell>
                    <TableCell>
                      <Chip label={config.authentication.type} size="small" />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={config.enabled ? 'Enabled' : 'Disabled'}
                        color={getStatusColor(config.enabled)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Stack direction="row" spacing={1}>
                        <Switch
                          checked={config.enabled}
                          onChange={(e) => handleToggleConfig(config.id, e.target.checked)}
                          size="small"
                        />
                        <Tooltip title="Edit">
                          <IconButton
                            size="small"
                            onClick={() => {
                              setEditingConfig(config);
                              setConfigDialogOpen(true);
                            }}
                          >
                            <Edit />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDeleteConfig(config.id)}
                          >
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Throughput (RPS)" />
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={metrics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="timestamp" />
                    <YAxis />
                    <RechartsTooltip />
                    <Line type="monotone" dataKey="throughput" stroke="#0088fe" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Error Rate" />
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={metrics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="timestamp" />
                    <YAxis />
                    <RechartsTooltip />
                    <Line type="monotone" dataKey="errors" stroke="#ff7300" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Alert severity="info">
          <AlertTitle>Security Status</AlertTitle>
          All security protocols are active and functioning normally. Rate limiting and authentication
          mechanisms are protecting the gateway from unauthorized access and abuse.
        </Alert>
      </TabPanel>

      <TabPanel value={tabValue} index={4}>
        <Typography variant="h5" gutterBottom>
          API Routes Configuration
        </Typography>
        <Alert severity="info">
          API routes are automatically configured based on the gateway configurations above.
        </Alert>
      </TabPanel>

      {/* Configuration Dialog */}
      <Dialog
        open={configDialogOpen}
        onClose={() => setConfigDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingConfig ? 'Edit Configuration' : 'Add Configuration'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Name"
              defaultValue={editingConfig?.name || ''}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Description"
              defaultValue={editingConfig?.description || ''}
              margin="normal"
              multiline
              rows={2}
            />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Rate Limit (requests)"
                  type="number"
                  defaultValue={editingConfig?.rateLimit.requests || 1000}
                  margin="normal"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Window (seconds)"
                  type="number"
                  defaultValue={editingConfig?.rateLimit.window || 60}
                  margin="normal"
                />
              </Grid>
            </Grid>
            <FormControl fullWidth margin="normal">
              <InputLabel>Authentication Type</InputLabel>
              <Select
                defaultValue={editingConfig?.authentication.type || 'none'}
              >
                <MenuItem value="none">None</MenuItem>
                <MenuItem value="basic">Basic Auth</MenuItem>
                <MenuItem value="jwt">JWT</MenuItem>
                <MenuItem value="oauth2">OAuth2</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialogOpen(false)}>Cancel</Button>
          <LoadingButton
            onClick={() => {
              const config = editingConfig || {
                id: '',
                name: '',
                description: '',
                enabled: true,
                rateLimit: { requests: 1000, window: 60 },
                authentication: { type: 'none', config: {} },
                routes: [],
                createdAt: '',
                updatedAt: '',
              };
              handleSaveConfig(config);
            }}
            variant="contained"
          >
            {editingConfig ? 'Update' : 'Create'}
          </LoadingButton>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default GatewayAdminDashboard;