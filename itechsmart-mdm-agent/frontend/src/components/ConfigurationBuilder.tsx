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
} from '@mui/material';
import { Settings as ConfigIcon } from '@mui/icons-material';
import { configApi } from '../services/api';

const PRODUCTS = [
  'itechsmart-enterprise',
  'itechsmart-ninja',
  'itechsmart-analytics',
  'legalai-pro',
];

export default function ConfigurationBuilder() {
  const [productName, setProductName] = useState('');
  const [environment, setEnvironment] = useState('production');
  const [loading, setLoading] = useState(false);
  const [template, setTemplate] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleLoadTemplate = async () => {
    if (!productName) return;

    setLoading(true);
    setError(null);

    try {
      const data = await configApi.getTemplate(productName, environment);
      setTemplate(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load template');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 700 }}>
        Configuration Builder
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Select Product
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
                fullWidth
                startIcon={loading ? <CircularProgress size={20} /> : <ConfigIcon />}
                onClick={handleLoadTemplate}
                disabled={loading || !productName}
                sx={{ mt: 3 }}
              >
                {loading ? 'Loading...' : 'Load Template'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Configuration Template
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}

              {template && (
                <Box sx={{ mt: 2 }}>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    Configuration template loaded successfully
                  </Alert>
                  <TextField
                    fullWidth
                    multiline
                    rows={20}
                    value={JSON.stringify(template, null, 2)}
                    variant="outlined"
                    InputProps={{
                      readOnly: true,
                      sx: { fontFamily: 'monospace', fontSize: '0.875rem' },
                    }}
                  />
                </Box>
              )}

              {!template && !error && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Select a product and environment to load the configuration template.
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
