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
  LinearProgress,
  Button,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';

export default function Products() {
  const [products] = useState([
    { id: 1, name: 'iTechSmart Enterprise', status: 'healthy', qaScore: 98, checks: 40, passed: 39, failed: 1, warning: 0 },
    { id: 2, name: 'iTechSmart Ninja', status: 'healthy', qaScore: 99, checks: 40, passed: 40, failed: 0, warning: 0 },
    { id: 3, name: 'iTechSmart Analytics', status: 'healthy', qaScore: 96, checks: 40, passed: 38, failed: 1, warning: 1 },
    { id: 4, name: 'iTechSmart DataFlow', status: 'warning', qaScore: 95, checks: 40, passed: 37, failed: 2, warning: 1 },
    { id: 5, name: 'iTechSmart Pulse', status: 'healthy', qaScore: 94, checks: 40, passed: 37, failed: 2, warning: 1 },
    { id: 6, name: 'iTechSmart Shield', status: 'healthy', qaScore: 97, checks: 40, passed: 39, failed: 0, warning: 1 },
    { id: 7, name: 'iTechSmart Connect', status: 'healthy', qaScore: 93, checks: 40, passed: 36, failed: 3, warning: 1 },
    { id: 8, name: 'iTechSmart Vault', status: 'healthy', qaScore: 96, checks: 40, passed: 38, failed: 1, warning: 1 },
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'warning':
        return 'warning';
      case 'critical':
        return 'error';
      default:
        return 'default';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 95) return 'success';
    if (score >= 85) return 'warning';
    return 'error';
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <div>
          <Typography variant="h4" gutterBottom>
            Products
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Monitor QA status across all iTechSmart Suite products
          </Typography>
        </div>
        <Button variant="contained" startIcon={<RefreshIcon />}>
          Refresh All
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Product Name</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>QA Score</TableCell>
              <TableCell align="center">Total Checks</TableCell>
              <TableCell align="center">Passed</TableCell>
              <TableCell align="center">Failed</TableCell>
              <TableCell align="center">Warning</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {products.map((product) => (
              <TableRow key={product.id} hover>
                <TableCell>
                  <Typography variant="body1" fontWeight="medium">
                    {product.name}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={product.status}
                    color={getStatusColor(product.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography
                      variant="body2"
                      fontWeight="bold"
                      color={`${getScoreColor(product.qaScore)}.main`}
                    >
                      {product.qaScore}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={product.qaScore}
                      sx={{ width: 100 }}
                      color={getScoreColor(product.qaScore) as any}
                    />
                  </Box>
                </TableCell>
                <TableCell align="center">{product.checks}</TableCell>
                <TableCell align="center">
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                    <CheckIcon fontSize="small" color="success" />
                    {product.passed}
                  </Box>
                </TableCell>
                <TableCell align="center">
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                    <ErrorIcon fontSize="small" color="error" />
                    {product.failed}
                  </Box>
                </TableCell>
                <TableCell align="center">
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                    <WarningIcon fontSize="small" color="warning" />
                    {product.warning}
                  </Box>
                </TableCell>
                <TableCell align="right">
                  <IconButton size="small" color="primary">
                    <RefreshIcon />
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