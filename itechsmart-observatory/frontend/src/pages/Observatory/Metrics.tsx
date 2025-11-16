import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  LinearProgress,
  Autocomplete,
  Paper,
  Divider,
  Alert,
} from '@mui/material';
import {
  Search,
  TrendingUp,
  ShowChart,
  Refresh,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface MetricData {
  timestamp: string;
  value: number;
}

interface MetricStatistics {
  count: number;
  min: number;
  max: number;
  avg: number;
  median: number;
  stddev: number;
  p95: number;
  p99: number;
}

const ObservatoryMetrics: React.FC = () => {
  const [services, setServices] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<string[]>([]);
  const [selectedService, setSelectedService] = useState<string>('');
  const [selectedMetric, setSelectedMetric] = useState<string>('');
  const [timeRange, setTimeRange] = useState('1h');
  const [aggregation, setAggregation] = useState('avg');
  const [interval, setInterval] = useState('5m');
  const [metricData, setMetricData] = useState<MetricData[]>([]);
  const [statistics, setStatistics] = useState<MetricStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [chartType, setChartType] = useState<'line' | 'area' | 'bar'>('line');

  useEffect(() => {
    fetchServices();
  }, []);

  useEffect(() => {
    if (selectedService) {
      fetchMetrics();
    }
  }, [selectedService]);

  const fetchServices = async () => {
    try {
      const response = await fetch('/api/observatory/services');
      const data = await response.json();
      setServices(data.services || []);
    } catch (error) {
      console.error('Error fetching services:', error);
    }
  };

  const fetchMetrics = async () => {
    try {
      const response = await fetch(`/api/observatory/metrics/list/${selectedService}`);
      const data = await response.json();
      setMetrics(data.metrics || []);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  const handleQuery = async () => {
    if (!selectedService || !selectedMetric) {
      return;
    }

    setLoading(true);
    try {
      // Calculate time range
      const endTime = new Date();
      const startTime = new Date();
      
      if (timeRange.endsWith('m')) {
        startTime.setMinutes(startTime.getMinutes() - parseInt(timeRange));
      } else if (timeRange.endsWith('h')) {
        startTime.setHours(startTime.getHours() - parseInt(timeRange));
      } else if (timeRange.endsWith('d')) {
        startTime.setDate(startTime.getDate() - parseInt(timeRange));
      }

      // Query metrics
      const queryResponse = await fetch('/api/observatory/metrics/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_id: selectedService,
          metric_name: selectedMetric,
          start_time: startTime.toISOString(),
          end_time: endTime.toISOString(),
          aggregation,
          interval,
        }),
      });
      const queryData = await queryResponse.json();
      setMetricData(queryData.data || []);

      // Get statistics
      const statsResponse = await fetch(
        `/api/observatory/metrics/statistics/${selectedService}/${selectedMetric}?time_range=${timeRange}`
      );
      const statsData = await statsResponse.json();
      setStatistics(statsData.statistics || null);
    } catch (error) {
      console.error('Error querying metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderChart = () => {
    if (metricData.length === 0) {
      return (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <ShowChart sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            No data available
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Select a service and metric, then click Query to view data
          </Typography>
        </Box>
      );
    }

    const ChartComponent = chartType === 'line' ? LineChart : chartType === 'area' ? AreaChart : BarChart;
    const DataComponent: any = chartType === 'line' ? Line : chartType === 'area' ? Area : Bar;

    return (
      <ResponsiveContainer width="100%" height={400}>
        <ChartComponent data={metricData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" />
          <YAxis />
          <Tooltip />
          <Legend />
          <DataComponent
            type="monotone"
            dataKey="value"
            stroke="#8884d8"
            fill="#8884d8"
            fillOpacity={chartType === 'area' ? 0.6 : 1}
            name={selectedMetric}
          />
        </ChartComponent>
      </ResponsiveContainer>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Typography variant="h4" component="h1" sx={{ mb: 3 }}>
        Metrics Explorer
      </Typography>

      {/* Query Builder */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Query Builder
          </Typography>
          <Divider sx={{ mb: 2 }} />

          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Service</InputLabel>
                <Select
                  value={selectedService}
                  label="Service"
                  onChange={(e) => setSelectedService(e.target.value)}
                >
                  {services.map((service) => (
                    <MenuItem key={service.id} value={service.id}>
                      {service.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={3}>
              <Autocomplete
                options={metrics}
                value={selectedMetric}
                onChange={(e, newValue) => setSelectedMetric(newValue || '')}
                renderInput={(params) => <TextField {...params} label="Metric" />}
                disabled={!selectedService}
              />
            </Grid>

            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Time Range</InputLabel>
                <Select
                  value={timeRange}
                  label="Time Range"
                  onChange={(e) => setTimeRange(e.target.value)}
                >
                  <MenuItem value="5m">Last 5 min</MenuItem>
                  <MenuItem value="15m">Last 15 min</MenuItem>
                  <MenuItem value="1h">Last 1 hour</MenuItem>
                  <MenuItem value="6h">Last 6 hours</MenuItem>
                  <MenuItem value="24h">Last 24 hours</MenuItem>
                  <MenuItem value="7d">Last 7 days</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Aggregation</InputLabel>
                <Select
                  value={aggregation}
                  label="Aggregation"
                  onChange={(e) => setAggregation(e.target.value)}
                >
                  <MenuItem value="avg">Average</MenuItem>
                  <MenuItem value="sum">Sum</MenuItem>
                  <MenuItem value="min">Min</MenuItem>
                  <MenuItem value="max">Max</MenuItem>
                  <MenuItem value="p50">P50</MenuItem>
                  <MenuItem value="p95">P95</MenuItem>
                  <MenuItem value="p99">P99</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<Search />}
                onClick={handleQuery}
                disabled={!selectedService || !selectedMetric || loading}
                sx={{ height: '56px' }}
              >
                Query
              </Button>
            </Grid>
          </Grid>

          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Interval</InputLabel>
                <Select
                  value={interval}
                  label="Interval"
                  onChange={(e) => setInterval(e.target.value)}
                >
                  <MenuItem value="1m">1 minute</MenuItem>
                  <MenuItem value="5m">5 minutes</MenuItem>
                  <MenuItem value="15m">15 minutes</MenuItem>
                  <MenuItem value="1h">1 hour</MenuItem>
                  <MenuItem value="1d">1 day</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Chart Type</InputLabel>
                <Select
                  value={chartType}
                  label="Chart Type"
                  onChange={(e) => setChartType(e.target.value as any)}
                >
                  <MenuItem value="line">Line Chart</MenuItem>
                  <MenuItem value="area">Area Chart</MenuItem>
                  <MenuItem value="bar">Bar Chart</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Statistics */}
      {statistics && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={6} sm={4} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  Count
                </Typography>
                <Typography variant="h5">{statistics.count}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={4} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  Average
                </Typography>
                <Typography variant="h5">{statistics.avg.toFixed(2)}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={4} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  Min / Max
                </Typography>
                <Typography variant="h5">
                  {statistics.min.toFixed(2)} / {statistics.max.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={4} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  P95 / P99
                </Typography>
                <Typography variant="h5">
                  {statistics.p95.toFixed(2)} / {statistics.p99.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Chart */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              {selectedMetric || 'Metric Visualization'}
            </Typography>
            {metricData.length > 0 && (
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Chip label={`${metricData.length} data points`} size="small" />
                <Chip label={aggregation.toUpperCase()} color="primary" size="small" />
              </Box>
            )}
          </Box>
          {renderChart()}
        </CardContent>
      </Card>

      {/* Anomalies */}
      {selectedService && selectedMetric && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Anomaly Detection
            </Typography>
            <Alert severity="info">
              Anomaly detection analyzes metric patterns to identify unusual behavior.
              Click "Detect Anomalies" to run analysis on the selected metric.
            </Alert>
            <Button
              variant="outlined"
              sx={{ mt: 2 }}
              onClick={async () => {
                try {
                  const response = await fetch(
                    `/api/observatory/metrics/anomalies/${selectedService}/${selectedMetric}?time_range=${timeRange}`
                  );
                  const data = await response.json();
                  console.log('Anomalies:', data.anomalies);
                } catch (error) {
                  console.error('Error detecting anomalies:', error);
                }
              }}
            >
              Detect Anomalies
            </Button>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default ObservatoryMetrics;