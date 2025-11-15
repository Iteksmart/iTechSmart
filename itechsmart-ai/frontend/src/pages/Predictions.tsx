import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';

export default function Predictions() {
  const [recentPredictions] = useState([
    { id: 1, model: 'Customer Churn Predictor', input: 'Customer ID: 12345', output: 'Low Risk (15%)', confidence: 92.5, timestamp: '2 min ago' },
    { id: 2, model: 'Sentiment Analyzer', input: 'Great product, highly recommend!', output: 'Positive', confidence: 98.2, timestamp: '5 min ago' },
    { id: 3, model: 'Fraud Detector', input: 'Transaction: $5,432.10', output: 'Legitimate', confidence: 99.1, timestamp: '8 min ago' },
    { id: 4, model: 'Sales Forecaster', input: 'Q4 2024', output: '$2.3M', confidence: 87.6, timestamp: '12 min ago' },
  ]);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Predictions
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        Make predictions using deployed models
      </Typography>

      {/* Prediction Form */}
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          New Prediction
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <TextField
              select
              fullWidth
              label="Select Model"
              SelectProps={{
                native: true,
              }}
            >
              <option value="">Choose a model...</option>
              <option value="churn">Customer Churn Predictor</option>
              <option value="sentiment">Sentiment Analyzer</option>
              <option value="fraud">Fraud Detector</option>
              <option value="sales">Sales Forecaster</option>
            </TextField>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Input Data"
              placeholder="Enter input data for prediction..."
              multiline
              rows={1}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<SendIcon />}
              sx={{ height: '56px' }}
            >
              Predict
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Recent Predictions */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Recent Predictions
        </Typography>
        <Grid container spacing={2}>
          {recentPredictions.map((pred) => (
            <Grid item xs={12} md={6} key={pred.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                    <Typography variant="subtitle1" fontWeight="medium">
                      {pred.model}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {pred.timestamp}
                    </Typography>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Input:
                    </Typography>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', bgcolor: 'background.default', p: 1, borderRadius: 1 }}>
                      {pred.input}
                    </Typography>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Output:
                    </Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {pred.output}
                    </Typography>
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Confidence:
                    </Typography>
                    <Chip
                      label={`${pred.confidence}%`}
                      color={pred.confidence >= 95 ? 'success' : pred.confidence >= 85 ? 'primary' : 'warning'}
                      size="small"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Box>
  );
}