import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import axios from 'axios';
import 'leaflet/dist/leaflet.css';

const FleetDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState({
    fleetLocations: [],
    performanceMetrics: [],
    maintenanceAlerts: [],
    fuelEfficiency: [],
    utilizationRates: [],
    sensorData: []
  });

  useEffect(() => {
    fetchFleetData();
    const interval = setInterval(fetchFleetData, 15000); // Real-time updates
    return () => clearInterval(interval);
  }, []);

  const fetchFleetData = async () => {
    try {
      const response = await axios.get('/api/fleet/dashboard');
      setData(response.data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
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
    return <Alert severity="error">Error loading fleet data: {error}</Alert>;
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        IoT Fleet Management Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Fleet Map */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: 500 }}>
            <Typography variant="h6" gutterBottom>
              Real-time Fleet Location
            </Typography>
            <MapContainer
              center={[40.7128, -74.0060]}
              zoom={10}
              style={{ height: 420, width: '100%' }}
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              />
              {data.fleetLocations.map((vehicle, index) => (
                <Marker key={index} position={[vehicle.lat, vehicle.lng]}>
                  <Popup>
                    <Typography variant="subtitle2">
                      {vehicle.name}
                    </Typography>
                    <Typography variant="body2">
                      Status: {vehicle.status}
                    </Typography>
                    <Typography variant="body2">
                      Speed: {vehicle.speed} km/h
                    </Typography>
                    <Typography variant="body2">
                      Fuel: {vehicle.fuelLevel}%
                    </Typography>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </Paper>
        </Grid>

        {/* Performance Metrics */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: 500 }}>
            <Typography variant="h6" gutterBottom>
              Fleet Performance
            </Typography>
            <ResponsiveContainer width="100%" height={420}>
              <BarChart data={data.performanceMetrics} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="metric" type="category" width={80} />
                <Tooltip />
                <Bar dataKey="value" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Fuel Efficiency Trends */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Fuel Efficiency Trends
            </Typography>
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={data.fuelEfficiency}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="actual"
                  stroke="#8884d8"
                  strokeWidth={2}
                  name="Actual (L/100km)"
                />
                <Line
                  type="monotone"
                  dataKey="target"
                  stroke="#82ca9d"
                  strokeWidth={2}
                  name="Target (L/100km)"
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Maintenance Alerts */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Maintenance Alerts
            </Typography>
            <ResponsiveContainer width="100%" height={320}>
              <AreaChart data={data.maintenanceAlerts}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="critical"
                  stackId="1"
                  stroke="#ff7c7c"
                  fill="#ff7c7c"
                  name="Critical"
                />
                <Area
                  type="monotone"
                  dataKey="warning"
                  stackId="1"
                  stroke="#ffb347"
                  fill="#ffb347"
                  name="Warning"
                />
                <Area
                  type="monotone"
                  dataKey="info"
                  stackId="1"
                  stroke="#87ceeb"
                  fill="#87ceeb"
                  name="Info"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Utilization Rates */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Fleet Utilization Rates
            </Typography>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={data.utilizationRates}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="vehicle" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="utilization" fill="#8884d8" name="Utilization %" />
                <Bar dataKey="idle" fill="#82ca9d" name="Idle %" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Sensor Data */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Sensor Health Status
            </Typography>
            <ResponsiveContainer width="100%" height={320}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="vibration" name="Vibration" />
                <YAxis dataKey="temperature" name="Temperature" />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Scatter
                  name="Sensor Data"
                  data={data.sensorData}
                  fill="#8884d8"
                />
              </ScatterChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default FleetDashboard;