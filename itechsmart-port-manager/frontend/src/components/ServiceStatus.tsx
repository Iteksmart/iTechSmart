import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  CircularProgress,
  Button,
  IconButton
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  RestartAlt as RestartAltIcon
} from '@mui/icons-material';
import axios from 'axios';

const API_URL = 'http://localhost:8100/api';

interface ServiceStatus {
  service_id: string;
  port: number;
  status: string;
  last_checked: string;
}

function ServiceStatus() {
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchServiceStatus();
    const interval = setInterval(fetchServiceStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchServiceStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/services/status`);
      setServices(response.data.statuses);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching service status:', error);
      setLoading(false);
    }
  };

  const handleRestart = async (serviceId: string) => {
    try {
      await axios.post(`${API_URL}/services/restart`, { service_id: serviceId });
      fetchServiceStatus();
    } catch (error) {
      console.error('Error restarting service:', error);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const healthyCount = services.filter(s => s.status === 'healthy').length;
  const unhealthyCount = services.length - healthyCount;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Service Status
        </Typography>
        <Button
          variant="contained"
          startIcon={<RefreshIcon />}
          onClick={fetchServiceStatus}
        >
          Refresh
        </Button>
      </Box>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6}>
          <Card sx={{ background: 'linear-gradient(135deg, #38ef7d 0%, #11998e 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h3" fontWeight="bold">
                {healthyCount}
              </Typography>
              <Typography variant="body2">
                Healthy Services
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6}>
          <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h3" fontWeight="bold">
                {unhealthyCount}
              </Typography>
              <Typography variant="body2">
                Unhealthy Services
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={2}>
        {services.map((service) => (
          <Grid item xs={12} sm={6} md={4} key={service.service_id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                  <Box flex={1}>
                    <Typography variant="h6" gutterBottom noWrap>
                      {service.service_id}
                    </Typography>
                    <Chip
                      icon={service.status === 'healthy' ? <CheckCircleIcon /> : <ErrorIcon />}
                      label={service.status}
                      color={service.status === 'healthy' ? 'success' : 'error'}
                      size="small"
                      sx={{ mb: 1 }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      Port: {service.port}
                    </Typography>
                  </Box>
                  <IconButton
                    size="small"
                    onClick={() => handleRestart(service.service_id)}
                    disabled={service.status === 'healthy'}
                  >
                    <RestartAltIcon />
                  </IconButton>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default ServiceStatus;