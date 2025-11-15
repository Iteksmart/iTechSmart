import { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import { Psychology as AIIcon } from '@mui/icons-material';
import { aiApi } from '../services/api';

const PRODUCTS = [
  'itechsmart-enterprise',
  'itechsmart-ninja',
  'itechsmart-analytics',
  'legalai-pro',
];

export default function AIOptimizer() {
  const [productName, setProductName] = useState('');
  const [optimizationType, setOptimizationType] = useState('resources');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleOptimize = async () => {
    if (!productName) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let response;
      if (optimizationType === 'resources') {
        response = await aiApi.optimizeResources({
          product_name: productName,
          current_resources: {
            cpu: 2,
            memory: 4096,
            replicas: 3,
          },
        });
      } else if (optimizationType === 'strategy') {
        response = await aiApi.optimizeStrategy({
          products: [productName],
          environment: 'production',
        });
      } else {
        response = await aiApi.optimizeConfig({
          product_name: productName,
          current_config: {
            workers: 4,
            log_level: 'debug',
          },
        });
      }
      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Optimization failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 700 }}>
        AI Optimizer
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Optimization Settings
              </Typography>

              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>Product</InputLabel>
                <Select
                  value={productName}
                  label="Product"
                  onChange={(e) => setProductName(e.target.value)}
                >
                  {PRODUCTS.map((product) => (
                    <MenuItem key={product} value={product}>
                      {product}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>Optimization Type</InputLabel>
                <Select
                  value={optimizationType}
                  label="Optimization Type"
                  onChange={(e) => setOptimizationType(e.target.value)}
                >
                  <MenuItem value="resources">Resource Optimization</MenuItem>
                  <MenuItem value="strategy">Deployment Strategy</MenuItem>
                  <MenuItem value="config">Configuration Tuning</MenuItem>
                </Select>
              </FormControl>

              <Button
                variant="contained"
                fullWidth
                startIcon={loading ? <CircularProgress size={20} /> : <AIIcon />}
                onClick={handleOptimize}
                disabled={loading || !productName}
                sx={{ mt: 3 }}
              >
                {loading ? 'Analyzing...' : 'Get AI Recommendations'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                AI Recommendations
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}

              {result && (
                <Box sx={{ mt: 2 }}>
                  <Alert severity="success" sx={{ mb: 2 }}>
                    AI analysis completed successfully
                  </Alert>

                  {optimizationType === 'resources' && (
                    <Box>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Confidence Score
                        </Typography>
                        <Chip
                          label={`${(result.confidence_score * 100).toFixed(0)}%`}
                          color="primary"
                          size="small"
                        />
                      </Box>

                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Current Resources
                        </Typography>
                        <Typography variant="body2">
                          CPU: {result.current_resources?.cpu || 'N/A'}
                        </Typography>
                        <Typography variant="body2">
                          Memory: {result.current_resources?.memory || 'N/A'} MB
                        </Typography>
                      </Box>

                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Recommended Resources
                        </Typography>
                        <Typography variant="body2" color="success.main">
                          CPU: {result.recommended_resources?.cpu || 'N/A'}
                        </Typography>
                        <Typography variant="body2" color="success.main">
                          Memory: {result.recommended_resources?.memory || 'N/A'} MB
                        </Typography>
                      </Box>

                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Estimated Savings
                        </Typography>
                        <Typography variant="body2">
                          {result.estimated_savings?.cost_savings || 'N/A'}
                        </Typography>
                      </Box>

                      <Box>
                        <Typography variant="subtitle2" gutterBottom>
                          AI Reasoning
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {result.reasoning}
                        </Typography>
                      </Box>
                    </Box>
                  )}

                  {optimizationType === 'strategy' && (
                    <Box>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Recommended Strategy
                        </Typography>
                        <Chip label={result.recommended_strategy} color="primary" />
                      </Box>

                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Confidence Score
                        </Typography>
                        <Chip
                          label={`${(result.confidence_score * 100).toFixed(0)}%`}
                          color="success"
                          size="small"
                        />
                      </Box>

                      <Box>
                        <Typography variant="subtitle2" gutterBottom>
                          Reasoning
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {result.reasoning}
                        </Typography>
                      </Box>
                    </Box>
                  )}

                  {optimizationType === 'config' && (
                    <Box>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Recommendations ({result.total_recommendations || 0})
                        </Typography>
                        {result.recommendations?.map((rec: any, index: number) => (
                          <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                            <Typography variant="body2" fontWeight={600}>
                              {rec.parameter}
                            </Typography>
                            <Typography variant="body2">
                              Current: {rec.current_value} → Recommended: {rec.recommended_value}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {rec.reason}
                            </Typography>
                          </Box>
                        ))}
                      </Box>

                      <Box>
                        <Typography variant="subtitle2" gutterBottom>
                          Expected Improvement
                        </Typography>
                        <Typography variant="body2" color="success.main">
                          {result.estimated_improvement}
                        </Typography>
                      </Box>
                    </Box>
                  )}
                </Box>
              )}

              {!result && !error && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Select a product and optimization type to get AI-powered recommendations.
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    <strong>Resource Optimization:</strong> Get recommendations for CPU, memory, and replica allocation to reduce costs while maintaining performance.
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    <strong>Deployment Strategy:</strong> Get AI recommendations for the best deployment strategy based on your environment and requirements.
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Configuration Tuning:</strong> Get recommendations for optimizing configuration parameters to improve performance and reliability.
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
