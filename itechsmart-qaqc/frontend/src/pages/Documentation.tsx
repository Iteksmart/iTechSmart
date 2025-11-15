import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  LinearProgress,
} from '@mui/material';
import { Refresh as RefreshIcon, AutoAwesome as AutoIcon } from '@mui/icons-material';

export default function Documentation() {
  const [docs] = useState([
    { id: 1, product: 'iTechSmart Enterprise', type: 'README', status: 'up_to_date', completeness: 98, lastUpdated: '2 days ago' },
    { id: 2, product: 'iTechSmart Enterprise', type: 'API Docs', status: 'up_to_date', completeness: 95, lastUpdated: '1 day ago' },
    { id: 3, product: 'iTechSmart Ninja', type: 'README', status: 'up_to_date', completeness: 100, lastUpdated: '1 day ago' },
    { id: 4, product: 'iTechSmart Analytics', type: 'User Guide', status: 'outdated', completeness: 85, lastUpdated: '45 days ago' },
    { id: 5, product: 'iTechSmart DataFlow', type: 'README', status: 'up_to_date', completeness: 92, lastUpdated: '3 days ago' },
    { id: 6, product: 'iTechSmart Pulse', type: 'API Docs', status: 'incomplete', completeness: 65, lastUpdated: '10 days ago' },
    { id: 7, product: 'iTechSmart Shield', type: 'Security', status: 'up_to_date', completeness: 97, lastUpdated: '1 day ago' },
    { id: 8, product: 'iTechSmart Connect', type: 'README', status: 'outdated', completeness: 78, lastUpdated: '35 days ago' },
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'up_to_date':
        return 'success';
      case 'outdated':
        return 'warning';
      case 'incomplete':
        return 'error';
      case 'missing':
        return 'error';
      default:
        return 'default';
    }
  };

  const getCompletenessColor = (completeness: number) => {
    if (completeness >= 90) return 'success';
    if (completeness >= 70) return 'warning';
    return 'error';
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <div>
          <Typography variant="h4" gutterBottom>
            Documentation
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Monitor and auto-generate documentation across all products
          </Typography>
        </div>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<RefreshIcon />}>
            Check Freshness
          </Button>
          <Button variant="contained" startIcon={<AutoIcon />}>
            Auto-Generate
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {docs.map((doc) => (
          <Grid item xs={12} md={6} lg={4} key={doc.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                  <div>
                    <Typography variant="h6" component="div" gutterBottom>
                      {doc.type}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {doc.product}
                    </Typography>
                  </div>
                  <Chip
                    label={doc.status.replace('_', ' ')}
                    color={getStatusColor(doc.status) as any}
                    size="small"
                  />
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Completeness
                    </Typography>
                    <Typography
                      variant="body2"
                      fontWeight="bold"
                      color={`${getCompletenessColor(doc.completeness)}.main`}
                    >
                      {doc.completeness}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={doc.completeness}
                    color={getCompletenessColor(doc.completeness) as any}
                  />
                </Box>

                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Last updated: {doc.lastUpdated}
                </Typography>

                <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                  <Button size="small" variant="outlined">
                    View
                  </Button>
                  <Button size="small" variant="text">
                    Update
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