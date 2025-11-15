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
  TextField,
  MenuItem,
} from '@mui/material';
import { PlayArrow as RunIcon } from '@mui/icons-material';

export default function QAChecks() {
  const [category, setCategory] = useState('all');
  const [checks] = useState([
    { id: 1, name: 'Code Quality - Linting', category: 'code_quality', severity: 'medium', autoFix: true, lastRun: '2 hours ago', status: 'passed' },
    { id: 2, name: 'Security - Dependency Scan', category: 'security', severity: 'high', autoFix: false, lastRun: '1 hour ago', status: 'passed' },
    { id: 3, name: 'Performance - API Response Time', category: 'performance', severity: 'high', autoFix: false, lastRun: '30 min ago', status: 'warning' },
    { id: 4, name: 'Documentation - README Freshness', category: 'documentation', severity: 'low', autoFix: true, lastRun: '3 hours ago', status: 'passed' },
    { id: 5, name: 'API - Endpoint Health', category: 'api', severity: 'critical', autoFix: false, lastRun: '15 min ago', status: 'passed' },
    { id: 6, name: 'Database - Connection Pool', category: 'database', severity: 'high', autoFix: false, lastRun: '1 hour ago', status: 'passed' },
  ]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed':
        return 'success';
      case 'failed':
        return 'error';
      case 'warning':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <div>
          <Typography variant="h4" gutterBottom>
            QA Checks
          </Typography>
          <Typography variant="body2" color="text.secondary">
            40+ automated quality checks across 10 categories
          </Typography>
        </div>
        <Button variant="contained" startIcon={<RunIcon />}>
          Run All Checks
        </Button>
      </Box>

      <Box sx={{ mb: 3 }}>
        <TextField
          select
          label="Filter by Category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          sx={{ minWidth: 200 }}
        >
          <MenuItem value="all">All Categories</MenuItem>
          <MenuItem value="code_quality">Code Quality</MenuItem>
          <MenuItem value="security">Security</MenuItem>
          <MenuItem value="performance">Performance</MenuItem>
          <MenuItem value="documentation">Documentation</MenuItem>
          <MenuItem value="api">API</MenuItem>
          <MenuItem value="database">Database</MenuItem>
        </TextField>
      </Box>

      <Grid container spacing={3}>
        {checks.map((check) => (
          <Grid item xs={12} md={6} key={check.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                  <Typography variant="h6" component="div">
                    {check.name}
                  </Typography>
                  <Chip
                    label={check.status}
                    color={getStatusColor(check.status) as any}
                    size="small"
                  />
                </Box>
                
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Chip
                    label={check.category.replace('_', ' ')}
                    size="small"
                    variant="outlined"
                  />
                  <Chip
                    label={check.severity}
                    color={getSeverityColor(check.severity) as any}
                    size="small"
                  />
                  {check.autoFix && (
                    <Chip
                      label="Auto-fix"
                      color="success"
                      size="small"
                      variant="outlined"
                    />
                  )}
                </Box>

                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Last run: {check.lastRun}
                </Typography>

                <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                  <Button size="small" variant="outlined" startIcon={<RunIcon />}>
                    Run Check
                  </Button>
                  <Button size="small" variant="text">
                    View History
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