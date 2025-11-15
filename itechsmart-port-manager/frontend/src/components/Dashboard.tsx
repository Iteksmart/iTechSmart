import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Chip,
  LinearProgress
} from '@mui/material';
import {
  Storage as StorageIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Speed as SpeedIcon
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';

const API_URL = 'http://localhost:8100/api';

const COLORS = ['#667eea', '#764ba2', '#38ef7d', '#fa709a', '#ffd700'];

interface Statistics {
  total_services: number;
  used_ports: number;
  available_ports: number;
  reserved_ports: number;
  port_range: [number, number];
  conflicts: number;
}

interface ServiceStatus {
  service_id: string;
  port: number;
  status: string;
}

function Dashboard() {
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [serviceStatuses, setServiceStatuses] = useState<ServiceStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, statusRes] = await Promise.all([
        axios.get(`${API_URL}/ports/statistics`),
        axios.get(`${API_URL}/services/status`)
      ]);
      
      setStatistics(statsRes.data.statistics);
      setServiceStatuses(statusRes.data.statuses);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  if (loading || !statistics) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const healthyServices = serviceStatuses.filter(s => s.status === 'healthy').length;
  const unhealthyServices = serviceStatuses.length - healthyServices;

  const portUsageData = [
    { name: 'Used Ports', value: statistics.used_ports },
    { name: 'Available Ports', value: statistics.available_ports },
    { name: 'Reserved Ports', value: statistics.reserved_ports }
  ];

  const serviceHealthData = [
    { name: 'Healthy', value: healthyServices },
    { name: 'Unhealthy', value: unhealthyServices }
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 4, fontWeight: 'bold' }}>
        Port Manager Dashboard
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h3" fontWeight="bold">
                    {statistics.total_services}
                  </Typography>
                  <Typography variant="body2">
                    Total Services
                  </Typography>
                </Box>
                <StorageIcon sx={{ fontSize: 60, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #38ef7d 0%, #11998e 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h3" fontWeight="bold">
                    {healthyServices}
                  </Typography>
                  <Typography variant="body2">
                    Healthy Services
                  </Typography>
                </Box>
                <CheckCircleIcon sx={{ fontSize: 60, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h3" fontWeight="bold">
                    {statistics.conflicts}
                  </Typography>
                  <Typography variant="body2">
                    Port Conflicts
                  </Typography>
                </Box>
                <WarningIcon sx={{ fontSize: 60, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #ffd700 0%, #ff8c00 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h3" fontWeight="bold">
                    {statistics.used_ports}
                  </Typography>
                  <Typography variant="body2">
                    Ports in Use
                  </Typography>
                </Box>
                <SpeedIcon sx={{ fontSize: 60, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Port Usage Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={portUsageData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {portUsageData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Service Health Status
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={serviceHealthData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {serviceHealthData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index === 0 ? '#38ef7d' : '#fa709a'} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Port Range Info */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Port Range Configuration
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Configured Range: {statistics.port_range[0]} - {statistics.port_range[1]}
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                Port Utilization: {((statistics.used_ports / (statistics.port_range[1] - statistics.port_range[0])) * 100).toFixed(1)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={(statistics.used_ports / (statistics.port_range[1] - statistics.port_range[0])) * 100}
                sx={{ height: 10, borderRadius: 5 }}
              />
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <Box sx={{ mt: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <Chip
          label={`${statistics.available_ports} Available Ports`}
          color="success"
          variant="outlined"
        />
        <Chip
          label={`${statistics.reserved_ports} Reserved Ports`}
          color="warning"
          variant="outlined"
        />
        <Chip
          label={`${unhealthyServices} Unhealthy Services`}
          color="error"
          variant="outlined"
        />
      </Box>
    </Box>
  );
}

export default Dashboard;