import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  Alert,
  Tabs,
  Tab
} from '@mui/material';
import {
  Add as AddIcon,
  TrendingUp as ForecastIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';

interface Prediction {
  id: number;
  model_id: number;
  prediction_type: string;
  predicted_value: any;
  confidence_score: number;
  lower_bound: number | null;
  upper_bound: number | null;
  status: string;
  created_at: string;
}

interface Model {
  id: number;
  name: string;
  model_type: string;
  is_deployed: boolean;
}

interface ForecastData {
  period: number;
  forecast_date: string;
  predicted_value: number;
  lower_bound: number;
  upper_bound: number;
  confidence_score: number;
}

const PredictionsView: React.FC = () => {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(true);
  const [predictDialogOpen, setPredictDialogOpen] = useState(false);
  const [forecastDialogOpen, setForecastDialogOpen] = useState(false);
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [forecastData, setForecastData] = useState<ForecastData[]>([]);

  const [newPrediction, setNewPrediction] = useState({
    model_id: '',
    input_data: '{}'
  });

  const [forecastRequest, setForecastRequest] = useState({
    metric_name: '',
    forecast_periods: 30
  });

  const tenantId = 1;

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load predictions
      const predRes = await fetch(`/api/v1/ai/predictions?tenant_id=${tenantId}&limit=50`);
      const predData = await predRes.json();
      setPredictions(predData);

      // Load deployed models
      const modelsRes = await fetch(`/api/v1/ai/models?tenant_id=${tenantId}`);
      const modelsData = await modelsRes.json();
      setModels(modelsData.filter((m: Model) => m.is_deployed));
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

  const handleMakePrediction = async () => {
    try {
      const inputData = JSON.parse(newPrediction.input_data);
      
      const response = await fetch(`/api/v1/ai/predictions?tenant_id=${tenantId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model_id: parseInt(newPrediction.model_id),
          input_data: inputData
        })
      });

      if (response.ok) {
        showAlert('success', 'Prediction created successfully');
        setPredictDialogOpen(false);
        loadData();
        setNewPrediction({ model_id: '', input_data: '{}' });
      } else {
        showAlert('error', 'Failed to create prediction');
      }
    } catch (error) {
      console.error('Error creating prediction:', error);
      showAlert('error', 'Invalid input data format');
    }
  };

  const handleForecast = async () => {
    try {
      // Mock historical data
      const historicalData = Array.from({ length: 90 }, (_, i) => ({
        date: new Date(Date.now() - (90 - i) * 24 * 60 * 60 * 1000).toISOString(),
        [forecastRequest.metric_name]: 100 + Math.random() * 50 + i * 0.5
      }));

      const response = await fetch(`/api/v1/ai/forecast?tenant_id=${tenantId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          metric_name: forecastRequest.metric_name,
          historical_data: historicalData,
          forecast_periods: forecastRequest.forecast_periods
        })
      });

      if (response.ok) {
        const data = await response.json();
        setForecastData(data.forecasts);
        showAlert('success', 'Forecast generated successfully');
        setForecastDialogOpen(false);
      } else {
        showAlert('error', 'Failed to generate forecast');
      }
    } catch (error) {
      console.error('Error generating forecast:', error);
      showAlert('error', 'Failed to generate forecast');
    }
  };

  const getStatusIcon = (status: string) => {
    if (status === 'completed') {
      return <SuccessIcon color="success" fontSize="small" />;
    } else if (status === 'failed') {
      return <ErrorIcon color="error" fontSize="small" />;
    }
    return null;
  };

  const formatPredictedValue = (value: any) => {
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2);
    }
    return value.toString();
  };

  // Mock prediction trend data
  const predictionTrendData = predictions.slice(0, 20).map((p, i) => ({
    index: i + 1,
    confidence: p.confidence_score,
    value: typeof p.predicted_value === 'number' ? p.predicted_value : 0
  }));

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
          Predictions & Forecasting
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<ForecastIcon />}
            onClick={() => setForecastDialogOpen(true)}
          >
            Forecast
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setPredictDialogOpen(true)}
          >
            Make Prediction
          </Button>
        </Box>
      </Box>

      {/* Alert */}
      {alert && (
        <Alert severity={alert.type} sx={{ mb: 2 }} onClose={() => setAlert(null)}>
          {alert.message}
        </Alert>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="Predictions" />
          <Tab label="Forecasts" />
          <Tab label="Statistics" />
        </Tabs>
      </Box>

      {/* Predictions Tab */}
      {tabValue === 0 && (
        <>
          {/* Confidence Trend Chart */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Predictions - Confidence Trend
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={predictionTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="index" label={{ value: 'Prediction #', position: 'insideBottom', offset: -5 }} />
                  <YAxis domain={[0, 1]} label={{ value: 'Confidence', angle: -90, position: 'insideLeft' }} />
                  <RechartsTooltip />
                  <Legend />
                  <Line type="monotone" dataKey="confidence" stroke="#8884d8" name="Confidence Score" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Predictions Table */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Prediction History
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Model</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Predicted Value</TableCell>
                      <TableCell>Confidence</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Created</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {predictions.map((prediction) => (
                      <TableRow key={prediction.id}>
                        <TableCell>{prediction.id}</TableCell>
                        <TableCell>
                          {models.find(m => m.id === prediction.model_id)?.name || `Model ${prediction.model_id}`}
                        </TableCell>
                        <TableCell>
                          <Chip label={prediction.prediction_type} size="small" />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {formatPredictedValue(prediction.predicted_value)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={prediction.confidence_score * 100}
                              sx={{ width: 60 }}
                            />
                            <Typography variant="caption">
                              {(prediction.confidence_score * 100).toFixed(0)}%
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>{getStatusIcon(prediction.status)}</TableCell>
                        <TableCell>
                          {new Date(prediction.created_at).toLocaleString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </>
      )}

      {/* Forecasts Tab */}
      {tabValue === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Forecast Visualization
            </Typography>
            {forecastData.length > 0 ? (
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={forecastData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period" label={{ value: 'Period', position: 'insideBottom', offset: -5 }} />
                  <YAxis label={{ value: 'Value', angle: -90, position: 'insideLeft' }} />
                  <RechartsTooltip />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="upper_bound"
                    stroke="#82ca9d"
                    fill="#82ca9d"
                    fillOpacity={0.2}
                    name="Upper Bound"
                  />
                  <Area
                    type="monotone"
                    dataKey="predicted_value"
                    stroke="#8884d8"
                    fill="#8884d8"
                    fillOpacity={0.6}
                    name="Forecast"
                  />
                  <Area
                    type="monotone"
                    dataKey="lower_bound"
                    stroke="#ffc658"
                    fill="#ffc658"
                    fillOpacity={0.2}
                    name="Lower Bound"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body1" color="text.secondary">
                  No forecast data available. Click "Forecast" to generate predictions.
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* Statistics Tab */}
      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Total Predictions
                </Typography>
                <Typography variant="h3" fontWeight="bold">
                  {predictions.length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Average Confidence
                </Typography>
                <Typography variant="h3" fontWeight="bold">
                  {predictions.length > 0
                    ? (predictions.reduce((sum, p) => sum + p.confidence_score, 0) / predictions.length * 100).toFixed(1)
                    : 0}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Success Rate
                </Typography>
                <Typography variant="h3" fontWeight="bold">
                  {predictions.length > 0
                    ? ((predictions.filter(p => p.status === 'completed').length / predictions.length) * 100).toFixed(1)
                    : 0}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Make Prediction Dialog */}
      <Dialog open={predictDialogOpen} onClose={() => setPredictDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Make Prediction</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Model</InputLabel>
              <Select
                value={newPrediction.model_id}
                label="Model"
                onChange={(e) => setNewPrediction({ ...newPrediction, model_id: e.target.value })}
              >
                {models.map((model) => (
                  <MenuItem key={model.id} value={model.id}>
                    {model.name} ({model.model_type})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              label="Input Data (JSON)"
              value={newPrediction.input_data}
              onChange={(e) => setNewPrediction({ ...newPrediction, input_data: e.target.value })}
              fullWidth
              multiline
              rows={6}
              placeholder='{"feature1": 100, "feature2": 200}'
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPredictDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleMakePrediction}
            variant="contained"
            disabled={!newPrediction.model_id}
          >
            Predict
          </Button>
        </DialogActions>
      </Dialog>

      {/* Forecast Dialog */}
      <Dialog open={forecastDialogOpen} onClose={() => setForecastDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Generate Forecast</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Metric Name"
              value={forecastRequest.metric_name}
              onChange={(e) => setForecastRequest({ ...forecastRequest, metric_name: e.target.value })}
              fullWidth
              placeholder="e.g., sales, revenue, traffic"
            />

            <TextField
              label="Forecast Periods"
              type="number"
              value={forecastRequest.forecast_periods}
              onChange={(e) => setForecastRequest({ ...forecastRequest, forecast_periods: parseInt(e.target.value) })}
              fullWidth
              inputProps={{ min: 1, max: 365 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setForecastDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleForecast}
            variant="contained"
            disabled={!forecastRequest.metric_name}
          >
            Generate
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PredictionsView;