import { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  LinearProgress,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

export default function Experiments() {
  const [experiments] = useState([
    {
      id: 1,
      name: 'Churn Prediction Optimization',
      description: 'Testing different algorithms for customer churn prediction',
      runs: 12,
      bestAccuracy: 96.2,
      status: 'completed',
      algorithm: 'Random Forest',
    },
    {
      id: 2,
      name: 'Image Classification Tuning',
      description: 'Hyperparameter tuning for CNN model',
      runs: 8,
      bestAccuracy: 97.3,
      status: 'running',
      algorithm: 'CNN',
    },
    {
      id: 3,
      name: 'NLP Model Comparison',
      description: 'Comparing BERT, GPT, and RoBERTa for sentiment analysis',
      runs: 15,
      bestAccuracy: 95.1,
      status: 'completed',
      algorithm: 'BERT',
    },
    {
      id: 4,
      name: 'Fraud Detection Enhancement',
      description: 'Testing ensemble methods for fraud detection',
      runs: 6,
      bestAccuracy: 98.5,
      status: 'running',
      algorithm: 'Ensemble',
    },
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'primary';
      case 'failed':
        return 'error';
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
            Experiments
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Track and compare ML experiments
          </Typography>
        </div>
        <Button variant="contained" startIcon={<AddIcon />}>
          New Experiment
        </Button>
      </Box>

      <Grid container spacing={3}>
        {experiments.map((exp) => (
          <Grid item xs={12} md={6} key={exp.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                  <div>
                    <Typography variant="h6" gutterBottom>
                      {exp.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {exp.description}
                    </Typography>
                  </div>
                  <Chip
                    label={exp.status}
                    color={getStatusColor(exp.status) as any}
                    size="small"
                  />
                </Box>

                <Grid container spacing={2} sx={{ mb: 2 }}>
                  <Grid item xs={4}>
                    <Typography variant="body2" color="text.secondary">
                      Runs
                    </Typography>
                    <Typography variant="h6">{exp.runs}</Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2" color="text.secondary">
                      Best Accuracy
                    </Typography>
                    <Typography variant="h6" color={`${getAccuracyColor(exp.bestAccuracy)}.main`}>
                      {exp.bestAccuracy}%
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2" color="text.secondary">
                      Algorithm
                    </Typography>
                    <Typography variant="h6" sx={{ fontSize: '0.9rem' }}>
                      {exp.algorithm}
                    </Typography>
                  </Grid>
                </Grid>

                {exp.status === 'running' && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Current Run Progress
                    </Typography>
                    <LinearProgress />
                  </Box>
                )}

                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button size="small" variant="outlined">
                    View Details
                  </Button>
                  <Button size="small" variant="text">
                    Compare Runs
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}