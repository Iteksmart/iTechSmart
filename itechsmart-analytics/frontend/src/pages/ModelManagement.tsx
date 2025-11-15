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
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  Tooltip,
  Alert
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as TrainIcon,
  CloudUpload as DeployIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Assessment as MetricsIcon,
  Edit as EditIcon
} from '@mui/icons-material';

interface Model {
  id: number;
  name: string;
  description: string;
  model_type: string;
  status: string;
  algorithm: string;
  accuracy: number | null;
  precision: number | null;
  recall: number | null;
  f1_score: number | null;
  rmse: number | null;
  is_deployed: boolean;
  created_at: string;
  last_trained_at: string | null;
}

const ModelManagement: React.FC = () => {
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [trainDialogOpen, setTrainDialogOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState<Model | null>(null);
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const [newModel, setNewModel] = useState({
    name: '',
    description: '',
    model_type: 'time_series',
    algorithm: 'ARIMA',
    features: '',
    target_variable: ''
  });

  const tenantId = 1;

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/ai/models?tenant_id=${tenantId}`);
      const data = await response.json();
      setModels(data);
    } catch (error) {
      console.error('Error loading models:', error);
      showAlert('error', 'Failed to load models');
    } finally {
      setLoading(false);
    }
  };

  const showAlert = (type: 'success' | 'error', message: string) => {
    setAlert({ type, message });
    setTimeout(() => setAlert(null), 5000);
  };

  const handleCreateModel = async () => {
    try {
      const response = await fetch(`/api/v1/ai/models?tenant_id=${tenantId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newModel,
          features: newModel.features.split(',').map(f => f.trim()).filter(f => f)
        })
      });

      if (response.ok) {
        showAlert('success', 'Model created successfully');
        setCreateDialogOpen(false);
        loadModels();
        setNewModel({
          name: '',
          description: '',
          model_type: 'time_series',
          algorithm: 'ARIMA',
          features: '',
          target_variable: ''
        });
      } else {
        showAlert('error', 'Failed to create model');
      }
    } catch (error) {
      console.error('Error creating model:', error);
      showAlert('error', 'Failed to create model');
    }
  };

  const handleTrainModel = async (modelId: number) => {
    try {
      // Mock training data - in production, would come from user input or dataset
      const trainingData = Array.from({ length: 100 }, (_, i) => ({
        feature1: Math.random() * 100,
        feature2: Math.random() * 100,
        target: Math.random() * 100
      }));

      const response = await fetch(`/api/v1/ai/models/${modelId}/train?tenant_id=${tenantId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          training_data: trainingData,
          validation_split: 0.2
        })
      });

      if (response.ok) {
        showAlert('success', 'Model training started');
        loadModels();
      } else {
        showAlert('error', 'Failed to train model');
      }
    } catch (error) {
      console.error('Error training model:', error);
      showAlert('error', 'Failed to train model');
    }
  };

  const handleDeployModel = async (modelId: number) => {
    try {
      const response = await fetch(`/api/v1/ai/models/${modelId}/deploy?tenant_id=${tenantId}`, {
        method: 'POST'
      });

      if (response.ok) {
        showAlert('success', 'Model deployed successfully');
        loadModels();
      } else {
        showAlert('error', 'Failed to deploy model');
      }
    } catch (error) {
      console.error('Error deploying model:', error);
      showAlert('error', 'Failed to deploy model');
    }
  };

  const handleDeleteModel = async (modelId: number) => {
    if (!window.confirm('Are you sure you want to delete this model?')) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/ai/models/${modelId}?tenant_id=${tenantId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        showAlert('success', 'Model deleted successfully');
        loadModels();
      } else {
        showAlert('error', 'Failed to delete model');
      }
    } catch (error) {
      console.error('Error deleting model:', error);
      showAlert('error', 'Failed to delete model');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: 'success' | 'info' | 'warning' | 'default' | 'error' } = {
      deployed: 'success',
      trained: 'info',
      training: 'warning',
      draft: 'default',
      failed: 'error'
    };
    return colors[status] || 'default';
  };

  const modelTypeOptions = [
    { value: 'time_series', label: 'Time Series' },
    { value: 'classification', label: 'Classification' },
    { value: 'regression', label: 'Regression' },
    { value: 'clustering', label: 'Clustering' },
    { value: 'anomaly_detection', label: 'Anomaly Detection' },
    { value: 'forecasting', label: 'Forecasting' }
  ];

  const algorithmOptions: { [key: string]: string[] } = {
    time_series: ['ARIMA', 'Prophet', 'LSTM'],
    classification: ['RandomForest', 'XGBoost', 'LogisticRegression'],
    regression: ['LinearRegression', 'RandomForest', 'XGBoost'],
    clustering: ['KMeans', 'DBSCAN', 'HierarchicalClustering'],
    anomaly_detection: ['IsolationForest', 'OneClassSVM', 'AutoEncoder'],
    forecasting: ['Prophet', 'ARIMA', 'ExponentialSmoothing']
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          Model Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Create Model
        </Button>
      </Box>

      {/* Alert */}
      {alert && (
        <Alert severity={alert.type} sx={{ mb: 2 }} onClose={() => setAlert(null)}>
          {alert.message}
        </Alert>
      )}

      {/* Models Grid */}
      <Grid container spacing={3}>
        {models.map((model) => (
          <Grid item xs={12} md={6} lg={4} key={model.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      {model.name}
                    </Typography>
                    <Chip
                      label={model.status}
                      size="small"
                      color={getStatusColor(model.status)}
                      sx={{ mr: 1 }}
                    />
                    {model.is_deployed && (
                      <Chip label="Deployed" size="small" color="success" />
                    )}
                  </Box>
                  <IconButton
                    size="small"
                    onClick={() => handleDeleteModel(model.id)}
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {model.description || 'No description'}
                </Typography>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    Type: {model.model_type}
                  </Typography>
                  <br />
                  <Typography variant="caption" color="text.secondary">
                    Algorithm: {model.algorithm}
                  </Typography>
                </Box>

                {/* Performance Metrics */}
                {model.accuracy && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" fontWeight="bold">
                      Performance Metrics:
                    </Typography>
                    <Grid container spacing={1} sx={{ mt: 0.5 }}>
                      {model.accuracy && (
                        <Grid item xs={6}>
                          <Typography variant="caption">
                            Accuracy: {(model.accuracy * 100).toFixed(1)}%
                          </Typography>
                        </Grid>
                      )}
                      {model.precision && (
                        <Grid item xs={6}>
                          <Typography variant="caption">
                            Precision: {(model.precision * 100).toFixed(1)}%
                          </Typography>
                        </Grid>
                      )}
                      {model.recall && (
                        <Grid item xs={6}>
                          <Typography variant="caption">
                            Recall: {(model.recall * 100).toFixed(1)}%
                          </Typography>
                        </Grid>
                      )}
                      {model.f1_score && (
                        <Grid item xs={6}>
                          <Typography variant="caption">
                            F1: {(model.f1_score * 100).toFixed(1)}%
                          </Typography>
                        </Grid>
                      )}
                    </Grid>
                  </Box>
                )}

                {/* Actions */}
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {model.status === 'draft' && (
                    <Button
                      size="small"
                      variant="outlined"
                      startIcon={<TrainIcon />}
                      onClick={() => handleTrainModel(model.id)}
                      fullWidth
                    >
                      Train
                    </Button>
                  )}
                  {model.status === 'trained' && !model.is_deployed && (
                    <Button
                      size="small"
                      variant="contained"
                      startIcon={<DeployIcon />}
                      onClick={() => handleDeployModel(model.id)}
                      fullWidth
                    >
                      Deploy
                    </Button>
                  )}
                  {model.is_deployed && (
                    <Button
                      size="small"
                      variant="outlined"
                      startIcon={<MetricsIcon />}
                      fullWidth
                    >
                      View Metrics
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Create Model Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Model</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Model Name"
              value={newModel.name}
              onChange={(e) => setNewModel({ ...newModel, name: e.target.value })}
              fullWidth
              required
            />

            <TextField
              label="Description"
              value={newModel.description}
              onChange={(e) => setNewModel({ ...newModel, description: e.target.value })}
              fullWidth
              multiline
              rows={2}
            />

            <FormControl fullWidth>
              <InputLabel>Model Type</InputLabel>
              <Select
                value={newModel.model_type}
                label="Model Type"
                onChange={(e) => setNewModel({ ...newModel, model_type: e.target.value })}
              >
                {modelTypeOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Algorithm</InputLabel>
              <Select
                value={newModel.algorithm}
                label="Algorithm"
                onChange={(e) => setNewModel({ ...newModel, algorithm: e.target.value })}
              >
                {algorithmOptions[newModel.model_type]?.map((algo) => (
                  <MenuItem key={algo} value={algo}>
                    {algo}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              label="Features (comma-separated)"
              value={newModel.features}
              onChange={(e) => setNewModel({ ...newModel, features: e.target.value })}
              fullWidth
              placeholder="feature1, feature2, feature3"
            />

            <TextField
              label="Target Variable"
              value={newModel.target_variable}
              onChange={(e) => setNewModel({ ...newModel, target_variable: e.target.value })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateModel}
            variant="contained"
            disabled={!newModel.name || !newModel.model_type}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ModelManagement;