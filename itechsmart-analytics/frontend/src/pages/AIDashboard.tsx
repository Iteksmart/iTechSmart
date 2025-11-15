import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Psychology as AIIcon,
  TrendingUp as TrendIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Speed as SpeedIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';

interface DashboardStats {
  total_models: number;
  deployed_models: number;
  total_predictions: number;
  total_insights: number;
  active_recommendations: number;
  avg_model_accuracy: number;
  avg_prediction_confidence: number;
}

interface Model {
  id: number;
  name: string;
  model_type: string;
  status: string;
  accuracy: number;
  is_deployed: boolean;
}

interface Insight {
  id: number;
  insight_type: string;
  severity: string;
  title: string;
  detection_date: string;
  is_acknowledged: boolean;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const AIDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    total_models: 0,
    deployed_models: 0,
    total_predictions: 0,
    total_insights: 0,
    active_recommendations: 0,
    avg_model_accuracy: 0,
    avg_prediction_confidence: 0
  });
  const [models, setModels] = useState<Model[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);

  const tenantId = 1; // Would come from auth context

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Load models
      const modelsRes = await fetch(`/api/v1/ai/models?tenant_id=${tenantId}&limit=10`);
      const modelsData = await modelsRes.json();
      setModels(modelsData);

      // Load insights
      const insightsRes = await fetch(`/api/v1/ai/insights?tenant_id=${tenantId}&limit=10`);
      const insightsData = await insightsRes.json();
      setInsights(insightsData);

      // Load prediction stats
      const predStatsRes = await fetch(`/api/v1/ai/predictions/statistics?tenant_id=${tenantId}`);
      const predStats = await predStatsRes.json();

      // Load insight stats
      const insightStatsRes = await fetch(`/api/v1/ai/insights/statistics?tenant_id=${tenantId}`);
      const insightStats = await insightStatsRes.json();

      // Calculate stats
      const deployedCount = modelsData.filter((m: Model) => m.is_deployed).length;
      const avgAccuracy = modelsData.reduce((sum: number, m: Model) => sum + (m.accuracy || 0), 0) / (modelsData.length || 1);

      setStats({
        total_models: modelsData.length,
        deployed_models: deployedCount,
        total_predictions: predStats.total_predictions || 0,
        total_insights: insightStats.total_insights || 0,
        active_recommendations: 0, // Would load from API
        avg_model_accuracy: avgAccuracy,
        avg_prediction_confidence: predStats.avg_confidence || 0
      });
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      deployed: 'success',
      trained: 'info',
      training: 'warning',
      draft: 'default',
      failed: 'error'
    };
    return colors[status] || 'default';
  };

  const getSeverityColor = (severity: string) => {
    const colors: { [key: string]: string } = {
      critical: 'error',
      high: 'warning',
      medium: 'info',
      low: 'default',
      info: 'default'
    };
    return colors[severity] || 'default';
  };

  // Mock data for charts
  const predictionTrendData = [
    { date: '2025-08-01', predictions: 120, accuracy: 0.92 },
    { date: '2025-08-02', predictions: 145, accuracy: 0.91 },
    { date: '2025-08-03', predictions: 132, accuracy: 0.93 },
    { date: '2025-08-04', predictions: 168, accuracy: 0.90 },
    { date: '2025-08-05', predictions: 155, accuracy: 0.94 },
    { date: '2025-08-06', predictions: 178, accuracy: 0.92 },
    { date: '2025-08-07', predictions: 190, accuracy: 0.93 }
  ];

  const modelTypeData = [
    { name: 'Time Series', value: 35 },
    { name: 'Classification', value: 25 },
    { name: 'Regression', value: 20 },
    { name: 'Anomaly Detection', value: 15 },
    { name: 'Forecasting', value: 5 }
  ];

  const insightTypeData = [
    { type: 'Anomaly', count: 12 },
    { type: 'Trend', count: 8 },
    { type: 'Pattern', count: 6 },
    { type: 'Correlation', count: 4 }
  ];

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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <AIIcon sx={{ fontSize: 40, color: 'primary.main' }} />
          <Box>
            <Typography variant="h4" fontWeight="bold">
              AI Insights Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Real-time AI/ML analytics and insights
            </Typography>
          </Box>
        </Box>
        <Tooltip title="Refresh">
          <IconButton onClick={loadDashboardData} color="primary">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <AIIcon color="primary" />
                <Typography variant="body2" color="text.secondary">
                  Total Models
                </Typography>
              </Box>
              <Typography variant="h4" fontWeight="bold">
                {stats.total_models}
              </Typography>
              <Typography variant="caption" color="success.main">
                {stats.deployed_models} deployed
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <SpeedIcon color="info" />
                <Typography variant="body2" color="text.secondary">
                  Predictions
                </Typography>
              </Box>
              <Typography variant="h4" fontWeight="bold">
                {stats.total_predictions.toLocaleString()}
              </Typography>
              <Typography variant="caption" color="info.main">
                {(stats.avg_prediction_confidence * 100).toFixed(1)}% avg confidence
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <WarningIcon color="warning" />
                <Typography variant="body2" color="text.secondary">
                  Active Insights
                </Typography>
              </Box>
              <Typography variant="h4" fontWeight="bold">
                {stats.total_insights}
              </Typography>
              <Typography variant="caption" color="warning.main">
                {insights.filter(i => !i.is_acknowledged).length} unacknowledged
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <CheckIcon color="success" />
                <Typography variant="body2" color="text.secondary">
                  Model Accuracy
                </Typography>
              </Box>
              <Typography variant="h4" fontWeight="bold">
                {(stats.avg_model_accuracy * 100).toFixed(1)}%
              </Typography>
              <Typography variant="caption" color="success.main">
                Average across all models
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Prediction Trend */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Prediction Activity & Accuracy
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={predictionTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <RechartsTooltip />
                  <Legend />
                  <Area
                    yAxisId="left"
                    type="monotone"
                    dataKey="predictions"
                    stroke="#8884d8"
                    fill="#8884d8"
                    fillOpacity={0.6}
                    name="Predictions"
                  />
                  <Area
                    yAxisId="right"
                    type="monotone"
                    dataKey="accuracy"
                    stroke="#82ca9d"
                    fill="#82ca9d"
                    fillOpacity={0.6}
                    name="Accuracy"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Model Types Distribution */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Model Types
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={modelTypeData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {modelTypeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Insights by Type */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Insights by Type
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={insightTypeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="type" />
                  <YAxis />
                  <RechartsTooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Insights */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Insights
              </Typography>
              <TableContainer sx={{ maxHeight: 250 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Type</TableCell>
                      <TableCell>Severity</TableCell>
                      <TableCell>Title</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {insights.slice(0, 5).map((insight) => (
                      <TableRow key={insight.id}>
                        <TableCell>
                          <Chip label={insight.insight_type} size="small" />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={insight.severity}
                            size="small"
                            color={getSeverityColor(insight.severity) as any}
                          />
                        </TableCell>
                        <TableCell>{insight.title}</TableCell>
                        <TableCell>
                          {insight.is_acknowledged ? (
                            <CheckIcon color="success" fontSize="small" />
                          ) : (
                            <WarningIcon color="warning" fontSize="small" />
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Models Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Active Models
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Accuracy</TableCell>
                  <TableCell>Deployed</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {models.map((model) => (
                  <TableRow key={model.id}>
                    <TableCell>{model.name}</TableCell>
                    <TableCell>
                      <Chip label={model.model_type} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={model.status}
                        size="small"
                        color={getStatusColor(model.status) as any}
                      />
                    </TableCell>
                    <TableCell>
                      {model.accuracy ? `${(model.accuracy * 100).toFixed(1)}%` : 'N/A'}
                    </TableCell>
                    <TableCell>
                      {model.is_deployed ? (
                        <CheckIcon color="success" />
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          No
                        </Typography>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AIDashboard;