import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Button,
  LinearProgress,
} from '@mui/material';
import {
  PlayArrow as DeployIcon,
  Stop as StopIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

export default function Models() {
  const [models] = useState([
    { id: 1, name: 'Customer Churn Predictor', type: 'Classification', algorithm: 'Random Forest', accuracy: 96.2, status: 'deployed', version: 'v2.1' },
    { id: 2, name: 'Sales Forecaster', type: 'Regression', algorithm: 'XGBoost', accuracy: 92.5, status: 'training', version: 'v1.3' },
    { id: 3, name: 'Image Classifier', type: 'Computer Vision', algorithm: 'CNN', accuracy: 97.3, status: 'deployed', version: 'v3.0' },
    { id: 4, name: 'Sentiment Analyzer', type: 'NLP', algorithm: 'BERT', accuracy: 95.1, status: 'deployed', version: 'v1.8' },
    { id: 5, name: 'Fraud Detector', type: 'Classification', algorithm: 'Neural Network', accuracy: 98.5, status: 'deployed', version: 'v2.5' },
    { id: 6, name: 'Recommendation Engine', type: 'Collaborative Filtering', algorithm: 'Matrix Factorization', accuracy: 89.3, status: 'idle', version: 'v1.2' },
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'deployed':
        return 'success';
      case 'training':
        return 'primary';
      case 'idle':
        return 'default';
      default:
        return 'default';
    }
  };

  const getAccuracyColor = (accuracy: number) => {
    if (accuracy >= 95) return 'success';
    if (accuracy >= 85) return 'warning';
    return 'error';
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <div>
          <Typography variant="h4" gutterBottom>
            ML Models
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage and deploy machine learning models
          </Typography>
        </div>
        <Button variant="contained" startIcon={<RefreshIcon />}>
          New Model
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Model Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Algorithm</TableCell>
              <TableCell>Version</TableCell>
              <TableCell>Accuracy</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {models.map((model) => (
              <TableRow key={model.id} hover>
                <TableCell>
                  <Typography variant="body1" fontWeight="medium">
                    {model.name}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip label={model.type} size="small" variant="outlined" />
                </TableCell>
                <TableCell>{model.algorithm}</TableCell>
                <TableCell>{model.version}</TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography
                      variant="body2"
                      fontWeight="bold"
                      color={`${getAccuracyColor(model.accuracy)}.main`}
                    >
                      {model.accuracy}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={model.accuracy}
                      sx={{ width: 80 }}
                      color={getAccuracyColor(model.accuracy) as any}
                    />
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={model.status}
                    color={getStatusColor(model.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell align="right">
                  <IconButton size="small" color="primary">
                    {model.status === 'deployed' ? <StopIcon /> : <DeployIcon />}
                  </IconButton>
                  <IconButton size="small" color="error">
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}