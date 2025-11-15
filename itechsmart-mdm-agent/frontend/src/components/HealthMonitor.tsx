import { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  LinearProgress,
} from '@mui/material';
import {
  CheckCircle as HealthyIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { monitoringApi } from '../services/api';
import type { HealthStatus, Alert as AlertType } from '../types';

export default function HealthMonitor() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [alerts, setAlerts] = useState<AlertType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadHealthData();
    const interval = setInterval(loadHealthData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadHealthData = async () => {
    try {
      const [healthData, alertsData] = await Promise.all([
        monitoringApi.getOverallHealth(),
        monitoringApi.getActiveAlerts(),
      ]);
      setHealth(healthData);
      setAlerts(alertsData.active_alerts || []);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load health data');
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

  const healthPercentage = health
    ? ((health.healthy / health.total_services) * 100).toFixed(1)
    : 0;

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 700 }}>
        Health Monitor
      </Typography>

      {/* Overall Health */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Overall System Health
          </Typography>
          <Box display="flex" alignItems="center" sx={{ mt: 2 }}>
            <Box sx={{ flexGrow: 1, mr: 2 }}>
              <LinearProgress
                variant="determinate"
                value={Number(healthPercentage)}
                sx={{ height: 10, borderRadius: 5 }}
                color={
                  Number(healthPercentage) > 90
                    ? 'success'
                    : Number(healthPercentage) > 70
                    ? 'warning'
                    : 'error'
                }
              />
            </Box>
            <Typography variant="h6" fontWeight={600}>
              {healthPercentage}%
            </Typography>
          </Box>
          <Box display="flex" justifyContent="space-between" sx={{ mt: 2 }}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Total Services
              </Typography>
              <Typography variant="h6">{health?.total_services || 0}</Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Healthy
              </Typography>
              <Typography variant="h6" color="success.main">
                {health?.healthy || 0}
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Degraded
              </Typography>
              <Typography variant="h6" color="warning.main">
                {health?.degraded || 0}
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Unhealthy
              </Typography>
              <Typography variant="h6" color="error.main">
                {health?.unhealthy || 0}
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Active Alerts */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Active Alerts ({alerts.length})
          </Typography>
          {alerts.length === 0 ? (
            <Alert severity="success" sx={{ mt: 2 }}>
              No active alerts. All systems operational.
            </Alert>
          ) : (
            <Box sx={{ mt: 2 }}>
              {alerts.map((alert) => (
                <Alert
                  key={alert.id}
                  severity={
                    alert.severity === 'critical' || alert.severity === 'error'
                      ? 'error'
                      : alert.severity === 'warning'
                      ? 'warning'
                      : 'info'
                  }
                  sx={{ mb: 2 }}
                >
                  <Typography variant="body2" fontWeight={600}>
                    {alert.service_name}
                  </Typography>
                  <Typography variant="body2">{alert.message}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(alert.timestamp).toLocaleString()}
                  </Typography>
                </Alert>
              ))}
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Service Status Grid */}
      <Grid container spacing={2}>
        {['itechsmart-enterprise', 'itechsmart-ninja', 'itechsmart-analytics', 'legalai-pro'].map(
          (service) => (
            <Grid item xs={12} sm={6} md={3} key={service}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Typography variant="body2" noWrap>
                      {service}
                    </Typography>
                    <HealthyIcon sx={{ color: 'success.main' }} />
                  </Box>
                  <Chip label="Healthy" size="small" color="success" sx={{ mt: 1 }} />
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
                    Response: 45ms
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          )
        )}
      </Grid>
    </Box>
  );
}
