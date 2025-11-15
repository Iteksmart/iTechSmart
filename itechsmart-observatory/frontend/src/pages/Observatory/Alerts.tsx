import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  LinearProgress,
  Tabs,
  Tab,
  Alert,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  CheckCircle,
  Error,
  Warning,
  Notifications,
  NotificationsActive,
} from '@mui/icons-material';

interface AlertRule {
  id: string;
  name: string;
  alert_type: string;
  severity: string;
  service_id: string;
  metric_name: string;
  is_active: boolean;
  is_firing: boolean;
  trigger_count: number;
  last_triggered: string | null;
}

interface AlertIncident {
  id: string;
  alert_id: string;
  status: string;
  severity: string;
  started_at: string;
  acknowledged_at: string | null;
  trigger_value: number;
}

interface AlertFormData {
  name: string;
  alert_type: string;
  severity: string;
  service_id: string;
  metric_name: string;
  condition: {
    operator: string;
    threshold: number;
    duration: number;
  };
  notification_channels: string[];
  description: string;
}

const ObservatoryAlerts: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertRule[]>([]);
  const [incidents, setIncidents] = useState<AlertIncident[]>([]);
  const [services, setServices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [alertDialogOpen, setAlertDialogOpen] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<AlertRule | null>(null);
  const [incidentDialogOpen, setIncidentDialogOpen] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState<AlertIncident | null>(null);
  const [formData, setFormData] = useState<AlertFormData>({
    name: '',
    alert_type: 'metric_threshold',
    severity: 'medium',
    service_id: '',
    metric_name: '',
    condition: {
      operator: 'gt',
      threshold: 0,
      duration: 300,
    },
    notification_channels: [],
    description: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);

      // Fetch alerts
      const alertsResponse = await fetch('/api/observatory/alerts');
      const alertsData = await alertsResponse.json();
      setAlerts(alertsData.alerts || []);

      // Fetch active incidents
      const incidentsResponse = await fetch('/api/observatory/alerts/incidents/active');
      const incidentsData = await incidentsResponse.json();
      setIncidents(incidentsData.incidents || []);

      // Fetch services
      const servicesResponse = await fetch('/api/observatory/services');
      const servicesData = await servicesResponse.json();
      setServices(servicesData.services || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAlert = () => {
    setSelectedAlert(null);
    setFormData({
      name: '',
      alert_type: 'metric_threshold',
      severity: 'medium',
      service_id: '',
      metric_name: '',
      condition: {
        operator: 'gt',
        threshold: 0,
        duration: 300,
      },
      notification_channels: [],
      description: '',
    });
    setAlertDialogOpen(true);
  };

  const handleEditAlert = (alert: AlertRule) => {
    setSelectedAlert(alert);
    setFormData({
      name: alert.name,
      alert_type: alert.alert_type,
      severity: alert.severity,
      service_id: alert.service_id,
      metric_name: alert.metric_name,
      condition: {
        operator: 'gt',
        threshold: 0,
        duration: 300,
      },
      notification_channels: [],
      description: '',
    });
    setAlertDialogOpen(true);
  };

  const handleSaveAlert = async () => {
    try {
      const url = selectedAlert
        ? `/api/observatory/alerts/${selectedAlert.id}`
        : '/api/observatory/alerts?created_by=user123';

      const method = selectedAlert ? 'PUT' : 'POST';

      await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      setAlertDialogOpen(false);
      fetchData();
    } catch (error) {
      console.error('Error saving alert:', error);
    }
  };

  const handleDeleteAlert = async (alertId: string) => {
    if (!window.confirm('Are you sure you want to delete this alert?')) return;

    try {
      await fetch(`/api/observatory/alerts/${alertId}`, {
        method: 'DELETE',
      });
      fetchData();
    } catch (error) {
      console.error('Error deleting alert:', error);
    }
  };

  const handleToggleAlert = async (alertId: string, isActive: boolean) => {
    try {
      await fetch(`/api/observatory/alerts/${alertId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !isActive }),
      });
      fetchData();
    } catch (error) {
      console.error('Error toggling alert:', error);
    }
  };

  const handleAcknowledgeIncident = async (incidentId: string) => {
    try {
      await fetch(`/api/observatory/alerts/incidents/${incidentId}/acknowledge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ acknowledged_by: 'user123' }),
      });
      fetchData();
      setIncidentDialogOpen(false);
    } catch (error) {
      console.error('Error acknowledging incident:', error);
    }
  };

  const handleResolveIncident = async (incidentId: string) => {
    try {
      await fetch(`/api/observatory/alerts/incidents/${incidentId}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resolved_by: 'user123',
          resolution_notes: 'Resolved from UI',
        }),
      });
      fetchData();
      setIncidentDialogOpen(false);
    } catch (error) {
      console.error('Error resolving incident:', error);
    }
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'> = {
      critical: 'error',
      high: 'warning',
      medium: 'primary',
      low: 'info',
      info: 'default',
    };
    return colors[severity] || 'default';
  };

  const getSeverityIcon = (severity: string) => {
    const icons: Record<string, React.ReactElement> = {
      critical: <Error />,
      high: <Warning />,
      medium: <Notifications />,
      low: <NotificationsActive />,
    };
    return icons[severity] || <Notifications />;
  };

  if (loading) {
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
          Alerts & Incidents
        </Typography>
        <Button variant="contained" startIcon={<Add />} onClick={handleCreateAlert}>
          Create Alert
        </Button>
      </Box>

      {/* Active Incidents Alert */}
      {incidents.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="body1" fontWeight="medium">
            {incidents.length} active incident{incidents.length > 1 ? 's' : ''} require attention
          </Typography>
        </Alert>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Alert Rules" />
          <Tab label={`Active Incidents (${incidents.length})`} />
        </Tabs>
      </Box>

      {/* Alert Rules Tab */}
      {activeTab === 0 && (
        <Card>
          <CardContent>
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Severity</TableCell>
                    <TableCell>Metric</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Triggers</TableCell>
                    <TableCell>Last Triggered</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {alerts.length > 0 ? (
                    alerts.map((alert) => (
                      <TableRow key={alert.id} hover>
                        <TableCell>
                          <Typography variant="body1" fontWeight="medium">
                            {alert.name}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip label={alert.alert_type} size="small" variant="outlined" />
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={getSeverityIcon(alert.severity)}
                            label={alert.severity.toUpperCase()}
                            color={getSeverityColor(alert.severity)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{alert.metric_name || 'N/A'}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Switch
                              checked={alert.is_active}
                              onChange={() => handleToggleAlert(alert.id, alert.is_active)}
                              size="small"
                            />
                            {alert.is_firing && (
                              <Chip label="FIRING" color="error" size="small" />
                            )}
                          </Box>
                        </TableCell>
                        <TableCell>{alert.trigger_count}</TableCell>
                        <TableCell>
                          {alert.last_triggered
                            ? new Date(alert.last_triggered).toLocaleString()
                            : 'Never'}
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="Edit">
                            <IconButton size="small" onClick={() => handleEditAlert(alert)}>
                              <Edit />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleDeleteAlert(alert.id)}
                            >
                              <Delete />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={8} align="center">
                        <Typography variant="body2" color="text.secondary">
                          No alert rules configured
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Active Incidents Tab */}
      {activeTab === 1 && (
        <Card>
          <CardContent>
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Incident ID</TableCell>
                    <TableCell>Severity</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Trigger Value</TableCell>
                    <TableCell>Started</TableCell>
                    <TableCell>Acknowledged</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {incidents.length > 0 ? (
                    incidents.map((incident) => (
                      <TableRow key={incident.id} hover>
                        <TableCell>
                          <Typography variant="body2" fontFamily="monospace">
                            {incident.id.substring(0, 8)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={getSeverityIcon(incident.severity)}
                            label={incident.severity.toUpperCase()}
                            color={getSeverityColor(incident.severity)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={incident.status.toUpperCase()}
                            color={incident.status === 'firing' ? 'error' : 'warning'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{incident.trigger_value?.toFixed(2) || 'N/A'}</TableCell>
                        <TableCell>
                          {new Date(incident.started_at).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          {incident.acknowledged_at
                            ? new Date(incident.acknowledged_at).toLocaleString()
                            : 'Not acknowledged'}
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="View Details">
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedIncident(incident);
                                setIncidentDialogOpen(true);
                              }}
                            >
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Box sx={{ py: 4 }}>
                          <CheckCircle sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
                          <Typography variant="h6" color="text.secondary">
                            No active incidents
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            All systems are operating normally
                          </Typography>
                        </Box>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Alert Dialog */}
      <Dialog open={alertDialogOpen} onClose={() => setAlertDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedAlert ? 'Edit Alert' : 'Create Alert'}</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Alert Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Alert Type</InputLabel>
                  <Select
                    value={formData.alert_type}
                    label="Alert Type"
                    onChange={(e) => setFormData({ ...formData, alert_type: e.target.value })}
                  >
                    <MenuItem value="metric_threshold">Metric Threshold</MenuItem>
                    <MenuItem value="anomaly">Anomaly Detection</MenuItem>
                    <MenuItem value="error_rate">Error Rate</MenuItem>
                    <MenuItem value="latency">Latency</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Severity</InputLabel>
                  <Select
                    value={formData.severity}
                    label="Severity"
                    onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                  >
                    <MenuItem value="critical">Critical</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="low">Low</MenuItem>
                    <MenuItem value="info">Info</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Service</InputLabel>
                  <Select
                    value={formData.service_id}
                    label="Service"
                    onChange={(e) => setFormData({ ...formData, service_id: e.target.value })}
                  >
                    {services.map((service) => (
                      <MenuItem key={service.id} value={service.id}>
                        {service.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Metric Name"
                  value={formData.metric_name}
                  onChange={(e) => setFormData({ ...formData, metric_name: e.target.value })}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAlertDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveAlert} disabled={!formData.name}>
            {selectedAlert ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Incident Dialog */}
      <Dialog
        open={incidentDialogOpen}
        onClose={() => setIncidentDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Incident Details</DialogTitle>
        <DialogContent>
          {selectedIncident && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Severity
                  </Typography>
                  <Chip
                    icon={getSeverityIcon(selectedIncident.severity)}
                    label={selectedIncident.severity.toUpperCase()}
                    color={getSeverityColor(selectedIncident.severity)}
                    sx={{ mt: 1 }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip
                    label={selectedIncident.status.toUpperCase()}
                    color={selectedIncident.status === 'firing' ? 'error' : 'warning'}
                    sx={{ mt: 1 }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Started At
                  </Typography>
                  <Typography variant="body1">
                    {new Date(selectedIncident.started_at).toLocaleString()}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          {selectedIncident?.status === 'firing' && (
            <Button
              color="warning"
              onClick={() => handleAcknowledgeIncident(selectedIncident.id)}
            >
              Acknowledge
            </Button>
          )}
          {selectedIncident && (
            <Button
              variant="contained"
              color="success"
              onClick={() => handleResolveIncident(selectedIncident.id)}
            >
              Resolve
            </Button>
          )}
          <Button onClick={() => setIncidentDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ObservatoryAlerts;