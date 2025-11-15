import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider
} from '@mui/material';
import {
  Warning as WarningIcon,
  TrendingUp as TrendIcon,
  Pattern as PatternIcon,
  Link as CorrelationIcon,
  CheckCircle as CheckIcon,
  ExpandMore as ExpandIcon,
  Lightbulb as RecommendationIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';

interface Insight {
  id: number;
  insight_type: string;
  severity: string;
  title: string;
  description: string;
  affected_metrics: string[];
  statistical_significance: number;
  anomaly_score?: number;
  expected_value?: number;
  actual_value?: number;
  deviation_percentage?: number;
  trend_direction?: string;
  trend_strength?: number;
  pattern_type?: string;
  detection_date: string;
  is_actionable: boolean;
  is_acknowledged: boolean;
}

interface Recommendation {
  id: number;
  recommendation_type: string;
  title: string;
  description: string;
  expected_impact: string;
  estimated_cost_savings: number;
  priority: number;
  urgency: string;
  status: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const InsightsExplorer: React.FC = () => {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedInsight, setSelectedInsight] = useState<Insight | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const tenantId = 1;

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load insights
      const insightsRes = await fetch(`/api/v1/ai/insights?tenant_id=${tenantId}&limit=100`);
      const insightsData = await insightsRes.json();
      setInsights(insightsData);

      // Load recommendations
      const recsRes = await fetch(`/api/v1/ai/recommendations?tenant_id=${tenantId}&limit=50`);
      const recsData = await recsRes.json();
      setRecommendations(recsData);
    } catch (error) {
      console.error('Error loading data:', error);
      showAlert('error', 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const showAlert = (type: 'success' | 'error', message: string) => {
    setAlert({ type, message });
    setTimeout(() => setAlert(null), 5000);
  };

  const handleAcknowledge = async (insightId: number) => {
    try {
      const response = await fetch(`/api/v1/ai/insights/${insightId}/acknowledge?tenant_id=${tenantId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 1 })
      });

      if (response.ok) {
        showAlert('success', 'Insight acknowledged');
        loadData();
      } else {
        showAlert('error', 'Failed to acknowledge insight');
      }
    } catch (error) {
      console.error('Error acknowledging insight:', error);
      showAlert('error', 'Failed to acknowledge insight');
    }
  };

  const handleGenerateRecommendations = async (insightId: number) => {
    try {
      const response = await fetch(`/api/v1/ai/insights/${insightId}/recommendations?tenant_id=${tenantId}`, {
        method: 'POST'
      });

      if (response.ok) {
        showAlert('success', 'Recommendations generated');
        loadData();
      } else {
        showAlert('error', 'Failed to generate recommendations');
      }
    } catch (error) {
      console.error('Error generating recommendations:', error);
      showAlert('error', 'Failed to generate recommendations');
    }
  };

  const handleAcceptRecommendation = async (recId: number) => {
    try {
      const response = await fetch(`/api/v1/ai/recommendations/${recId}/accept?tenant_id=${tenantId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 1 })
      });

      if (response.ok) {
        showAlert('success', 'Recommendation accepted');
        loadData();
      } else {
        showAlert('error', 'Failed to accept recommendation');
      }
    } catch (error) {
      console.error('Error accepting recommendation:', error);
      showAlert('error', 'Failed to accept recommendation');
    }
  };

  const getSeverityColor = (severity: string) => {
    const colors: { [key: string]: 'error' | 'warning' | 'info' | 'default' } = {
      critical: 'error',
      high: 'warning',
      medium: 'info',
      low: 'default',
      info: 'default'
    };
    return colors[severity] || 'default';
  };

  const getInsightIcon = (type: string) => {
    const icons: { [key: string]: JSX.Element } = {
      anomaly: <WarningIcon />,
      trend: <TrendIcon />,
      pattern: <PatternIcon />,
      correlation: <CorrelationIcon />
    };
    return icons[type] || <WarningIcon />;
  };

  const getPriorityColor = (priority: number) => {
    if (priority <= 2) return 'error';
    if (priority <= 3) return 'warning';
    return 'info';
  };

  // Statistics
  const insightsByType = insights.reduce((acc, insight) => {
    acc[insight.insight_type] = (acc[insight.insight_type] || 0) + 1;
    return acc;
  }, {} as { [key: string]: number });

  const insightsBySeverity = insights.reduce((acc, insight) => {
    acc[insight.severity] = (acc[insight.severity] || 0) + 1;
    return acc;
  }, {} as { [key: string]: number });

  const typeChartData = Object.entries(insightsByType).map(([name, value]) => ({ name, value }));
  const severityChartData = Object.entries(insightsBySeverity).map(([name, value]) => ({ name, value }));

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
        <Typography variant="h4" fontWeight="bold">
          AI Insights Explorer
        </Typography>
        <IconButton onClick={loadData} color="primary">
          <RefreshIcon />
        </IconButton>
      </Box>

      {/* Alert */}
      {alert && (
        <Alert severity={alert.type} sx={{ mb: 2 }} onClose={() => setAlert(null)}>
          {alert.message}
        </Alert>
      )}

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Total Insights
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {insights.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Unacknowledged
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="warning.main">
                {insights.filter(i => !i.is_acknowledged).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Critical/High
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="error.main">
                {insights.filter(i => ['critical', 'high'].includes(i.severity)).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Recommendations
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="info.main">
                {recommendations.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Insights by Type
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={typeChartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {typeChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Insights by Severity
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={severityChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <RechartsTooltip />
                  <Bar dataKey="value" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Insights List */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Active Insights
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {insights.map((insight) => (
              <Accordion key={insight.id}>
                <AccordionSummary expandIcon={<ExpandIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                    {getInsightIcon(insight.insight_type)}
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {insight.title}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                        <Chip
                          label={insight.insight_type}
                          size="small"
                          variant="outlined"
                        />
                        <Chip
                          label={insight.severity}
                          size="small"
                          color={getSeverityColor(insight.severity)}
                        />
                        {insight.is_acknowledged && (
                          <Chip
                            label="Acknowledged"
                            size="small"
                            color="success"
                            icon={<CheckIcon />}
                          />
                        )}
                      </Box>
                    </Box>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Typography variant="body2">
                      {insight.description}
                    </Typography>

                    <Divider />

                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Typography variant="caption" color="text.secondary">
                          Affected Metrics:
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
                          {insight.affected_metrics.map((metric, i) => (
                            <Chip key={i} label={metric} size="small" />
                          ))}
                        </Box>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Typography variant="caption" color="text.secondary">
                          Statistical Significance:
                        </Typography>
                        <Typography variant="body2">
                          {(insight.statistical_significance * 100).toFixed(1)}%
                        </Typography>
                      </Grid>
                    </Grid>

                    {insight.insight_type === 'anomaly' && (
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          Anomaly Details:
                        </Typography>
                        <Grid container spacing={1} sx={{ mt: 0.5 }}>
                          <Grid item xs={4}>
                            <Typography variant="body2">
                              Expected: {insight.expected_value?.toFixed(2)}
                            </Typography>
                          </Grid>
                          <Grid item xs={4}>
                            <Typography variant="body2">
                              Actual: {insight.actual_value?.toFixed(2)}
                            </Typography>
                          </Grid>
                          <Grid item xs={4}>
                            <Typography variant="body2" color="error">
                              Deviation: {insight.deviation_percentage?.toFixed(1)}%
                            </Typography>
                          </Grid>
                        </Grid>
                      </Box>
                    )}

                    {insight.insight_type === 'trend' && (
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          Trend Details:
                        </Typography>
                        <Grid container spacing={1} sx={{ mt: 0.5 }}>
                          <Grid item xs={6}>
                            <Typography variant="body2">
                              Direction: {insight.trend_direction}
                            </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="body2">
                              Strength: {(insight.trend_strength || 0 * 100).toFixed(1)}%
                            </Typography>
                          </Grid>
                        </Grid>
                      </Box>
                    )}

                    <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                      {!insight.is_acknowledged && (
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => handleAcknowledge(insight.id)}
                        >
                          Acknowledge
                        </Button>
                      )}
                      <Button
                        size="small"
                        variant="contained"
                        startIcon={<RecommendationIcon />}
                        onClick={() => handleGenerateRecommendations(insight.id)}
                      >
                        Generate Recommendations
                      </Button>
                    </Box>
                  </Box>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Recommendations */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Active Recommendations
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Priority</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Title</TableCell>
                  <TableCell>Impact</TableCell>
                  <TableCell>Cost Savings</TableCell>
                  <TableCell>Urgency</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recommendations.map((rec) => (
                  <TableRow key={rec.id}>
                    <TableCell>
                      <Chip
                        label={rec.priority}
                        size="small"
                        color={getPriorityColor(rec.priority)}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip label={rec.recommendation_type} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>{rec.title}</TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ maxWidth: 200 }}>
                        {rec.expected_impact}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {rec.estimated_cost_savings > 0
                        ? `$${rec.estimated_cost_savings.toLocaleString()}`
                        : 'N/A'}
                    </TableCell>
                    <TableCell>
                      <Chip label={rec.urgency} size="small" />
                    </TableCell>
                    <TableCell>
                      <Chip label={rec.status} size="small" />
                    </TableCell>
                    <TableCell>
                      {rec.status === 'pending' && (
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => handleAcceptRecommendation(rec.id)}
                        >
                          Accept
                        </Button>
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

export default InsightsExplorer;