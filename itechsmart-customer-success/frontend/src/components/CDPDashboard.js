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
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import axios from 'axios';

const CDPDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState({
    customerMetrics: [],
    journeyAnalytics: [],
    segmentationData: [],
    realTimeEvents: [],
    performanceMetrics: []
  });

  useEffect(() => {
    fetchCDPData();
    const interval = setInterval(fetchCDPData, 30000); // Real-time updates
    return () => clearInterval(interval);
  }, []);

  const fetchCDPData = async () => {
    try {
      const response = await axios.get('/api/cdp/dashboard');
      setData(response.data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">Error loading CDP data: {error}</Alert>;
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Customer Data Platform Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Customer Metrics */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Customer Growth Trends
            </Typography>
            <ResponsiveContainer width="100%" height={320}>
              <AreaChart data={data.customerMetrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="newCustomers"
                  stackId="1"
                  stroke="#8884d8"
                  fill="#8884d8"
                  name="New Customers"
                />
                <Area
                  type="monotone"
                  dataKey="activeCustomers"
                  stackId="1"
                  stroke="#82ca9d"
                  fill="#82ca9d"
                  name="Active Customers"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Segmentation Overview */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Customer Segments
            </Typography>
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie
                  data={data.segmentationData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {data.segmentationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Journey Analytics */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Customer Journey Performance
            </Typography>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={data.journeyAnalytics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="stage" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="completionRate" fill="#8884d8" name="Completion Rate %" />
                <Bar dataKey="conversionRate" fill="#82ca9d" name="Conversion Rate %" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Real-time Events */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Real-time Event Stream
            </Typography>
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={data.realTimeEvents}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="events"
                  stroke="#8884d8"
                  strokeWidth={2}
                  name="Events/Minute"
                />
                <Line
                  type="monotone"
                  dataKey="conversions"
                  stroke="#82ca9d"
                  strokeWidth={2}
                  name="Conversions/Minute"
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Performance Metrics */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Platform Performance
            </Typography>
            <Grid container spacing={2}>
              {data.performanceMetrics.map((metric, index) => (
                <Grid item xs={12} sm={6} md={3} key={index}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography color="textSecondary" gutterBottom>
                        {metric.name}
                      </Typography>
                      <Typography variant="h5">
                        {metric.value}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {metric.unit}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CDPDashboard;