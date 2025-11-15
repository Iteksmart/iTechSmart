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
import { RocketLaunch as DeployIcon } from '@mui/icons-material';
import { deploymentApi } from '../services/api';

const PRODUCTS = [
  'itechsmart-enterprise',
  'itechsmart-ninja',
  'itechsmart-analytics',
  'itechsmart-supreme',
  'itechsmart-hl7',
  'prooflink',
  'passport',
  'itechsmart-impactos',
  'legalai-pro',
  'itechsmart-dataflow',
  'itechsmart-pulse',
  'itechsmart-connect',
  'itechsmart-vault',
  'itechsmart-notify',
  'itechsmart-ledger',
  'itechsmart-copilot',
  'itechsmart-shield',
  'itechsmart-workflow',
  'itechsmart-marketplace',
  'itechsmart-cloud',
  'itechsmart-devops',
  'itechsmart-mobile',
  'itechsmart-ai',
  'itechsmart-compliance',
  'itechsmart-data-platform',
  'itechsmart-customer-success',
  'itechsmart-port-manager',
];

export default function DeploymentManager() {
  const [deploymentType, setDeploymentType] = useState<'product' | 'suite'>('product');
  const [productName, setProductName] = useState('');
  const [strategy, setStrategy] = useState('docker_compose');
  const [environment, setEnvironment] = useState('development');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDeploy = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let response;
      if (deploymentType === 'product') {
        if (!productName) {
          throw new Error('Please select a product');
        }
        response = await deploymentApi.deployProduct({
          product_name: productName,
          strategy,
          environment,
        });
      } else {
        response = await deploymentApi.deploySuite({
          strategy,
          environment,
        });
      }
      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Deployment failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 700 }}>
        Deploy Services
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Deployment Configuration
              </Typography>

              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>Deployment Type</InputLabel>
                <Select
                  value={deploymentType}
                  label="Deployment Type"
                  onChange={(e) => setDeploymentType(e.target.value as 'product' | 'suite')}
                >
                  <MenuItem value="product">Single Product</MenuItem>
                  <MenuItem value="suite">Entire Suite (27 Products)</MenuItem>
                </Select>
              </FormControl>

              {deploymentType === 'product' && (
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
              )}

              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>Deployment Strategy</InputLabel>
                <Select
                  value={strategy}
                  label="Deployment Strategy"
                  onChange={(e) => setStrategy(e.target.value)}
                >
                  <MenuItem value="docker_compose">Docker Compose</MenuItem>
                  <MenuItem value="kubernetes">Kubernetes</MenuItem>
                  <MenuItem value="manual">Manual</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>Environment</InputLabel>
                <Select
                  value={environment}
                  label="Environment"
                  onChange={(e) => setEnvironment(e.target.value)}
                >
                  <MenuItem value="development">Development</MenuItem>
                  <MenuItem value="staging">Staging</MenuItem>
                  <MenuItem value="production">Production</MenuItem>
                </Select>
              </FormControl>

              <Button
                variant="contained"
                size="large"
                fullWidth
                startIcon={loading ? <CircularProgress size={20} /> : <DeployIcon />}
                onClick={handleDeploy}
                disabled={loading || (deploymentType === 'product' && !productName)}
                sx={{ mt: 3 }}
              >
                {loading ? 'Deploying...' : 'Deploy Now'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Deployment Information
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}

              {result && (
                <Box sx={{ mt: 2 }}>
                  <Alert severity="success" sx={{ mb: 2 }}>
                    Deployment initiated successfully!
                  </Alert>

                  {deploymentType === 'product' ? (
                    <Box>
                      <Box display="flex" justifyContent="space-between" sx={{ mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Deployment ID:
                        </Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {result.deployment_id}
                        </Typography>
                      </Box>
                      <Box display="flex" justifyContent="space-between" sx={{ mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Product:
                        </Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {result.product_name}
                        </Typography>
                      </Box>
                      <Box display="flex" justifyContent="space-between" sx={{ mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Status:
                        </Typography>
                        <Chip label={result.status} size="small" color="info" />
                      </Box>
                      <Box display="flex" justifyContent="space-between" sx={{ mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Strategy:
                        </Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {result.strategy}
                        </Typography>
                      </Box>
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body2" color="text.secondary">
                          Environment:
                        </Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {result.environment}
                        </Typography>
                      </Box>
                    </Box>
                  ) : (
                    <Box>
                      <Box display="flex" justifyContent="space-between" sx={{ mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Suite Deployment ID:
                        </Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {result.suite_deployment_id}
                        </Typography>
                      </Box>
                      <Box display="flex" justifyContent="space-between" sx={{ mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Total Products:
                        </Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {result.total_products}
                        </Typography>
                      </Box>
                      <Box display="flex" justifyContent="space-between" sx={{ mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Status:
                        </Typography>
                        <Chip label={result.status} size="small" color="info" />
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                        Deployment Order:
                      </Typography>
                      <Box sx={{ mt: 1, maxHeight: 200, overflow: 'auto' }}>
                        {result.products?.map((product: string, index: number) => (
                          <Typography key={index} variant="body2" sx={{ ml: 2 }}>
                            {index + 1}. {product}
                          </Typography>
                        ))}
                      </Box>
                    </Box>
                  )}
                </Box>
              )}

              {!result && !error && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Configure your deployment settings and click "Deploy Now" to start the deployment process.
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    <strong>Docker Compose:</strong> Best for development and staging environments. Simple setup and easy debugging.
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    <strong>Kubernetes:</strong> Best for production environments. Provides auto-scaling, self-healing, and high availability.
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Manual:</strong> For custom environments with specific requirements. Provides full control over the deployment process.
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
