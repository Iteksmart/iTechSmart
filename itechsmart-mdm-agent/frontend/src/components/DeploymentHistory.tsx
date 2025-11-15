import { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { deploymentApi } from '../services/api';
import type { Deployment } from '../types';

export default function DeploymentHistory() {
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await deploymentApi.getDeploymentHistory(50, 0);
      setDeployments(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load deployment history');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'info';
      case 'failed':
        return 'error';
      case 'rolled_back':
        return 'warning';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 700 }}>
        Deployment History
      </Typography>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Deployments
          </Typography>

          {deployments.length === 0 ? (
            <Alert severity="info" sx={{ mt: 2 }}>
              No deployment history available.
            </Alert>
          ) : (
            <TableContainer sx={{ mt: 2 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Deployment ID</TableCell>
                    <TableCell>Product</TableCell>
                    <TableCell>Strategy</TableCell>
                    <TableCell>Environment</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Created At</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {deployments.map((deployment) => (
                    <TableRow key={deployment.deployment_id}>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                          {deployment.deployment_id}
                        </Typography>
                      </TableCell>
                      <TableCell>{deployment.product_name}</TableCell>
                      <TableCell>{deployment.strategy}</TableCell>
                      <TableCell>
                        <Chip label={deployment.environment} size="small" />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={deployment.status}
                          size="small"
                          color={getStatusColor(deployment.status) as any}
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(deployment.created_at).toLocaleString()}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
