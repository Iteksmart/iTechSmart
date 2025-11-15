import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ShoppingCart,
  Assignment,
  CheckCircle,
  Schedule,
  Cancel,
  TrendingUp,
  Visibility,
  Edit,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface DashboardStats {
  total_services: number;
  active_requests: number;
  pending_approvals: number;
  completed_today: number;
  avg_fulfillment_time: number;
  popular_services: Array<{
    id: string;
    name: string;
    request_count: number;
  }>;
}

interface RecentRequest {
  id: string;
  service_name: string;
  status: string;
  created_at: string;
  requester_name: string;
}

const ServiceCatalogDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentRequests, setRecentRequests] = useState<RecentRequest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch dashboard stats
      const statsResponse = await fetch('/api/service-catalog/dashboard/stats');
      const statsData = await statsResponse.json();
      setStats(statsData);

      // Fetch recent requests
      const requestsResponse = await fetch('/api/service-catalog/requests?limit=10');
      const requestsData = await requestsResponse.json();
      setRecentRequests(requestsData.requests || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'> = {
      draft: 'default',
      submitted: 'info',
      pending_approval: 'warning',
      approved: 'primary',
      in_progress: 'secondary',
      fulfilled: 'success',
      rejected: 'error',
      cancelled: 'error',
    };
    return colors[status] || 'default';
  };

  const getStatusIcon = (status: string) => {
    const icons: Record<string, React.ReactElement> = {
      draft: <Edit />,
      submitted: <Assignment />,
      pending_approval: <Schedule />,
      approved: <CheckCircle />,
      in_progress: <TrendingUp />,
      fulfilled: <CheckCircle />,
      rejected: <Cancel />,
      cancelled: <Cancel />,
    };
    return icons[status] || <Assignment />;
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Service Catalog Dashboard
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<ShoppingCart />}
          onClick={() => navigate('/service-catalog/browse')}
        >
          Browse Services
        </Button>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <ShoppingCart color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Services</Typography>
              </Box>
              <Typography variant="h3">{stats?.total_services || 0}</Typography>
              <Typography variant="body2" color="text.secondary">
                Available in catalog
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Assignment color="info" sx={{ mr: 1 }} />
                <Typography variant="h6">Active Requests</Typography>
              </Box>
              <Typography variant="h3">{stats?.active_requests || 0}</Typography>
              <Typography variant="body2" color="text.secondary">
                In progress
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Schedule color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Pending Approvals</Typography>
              </Box>
              <Typography variant="h3">{stats?.pending_approvals || 0}</Typography>
              <Typography variant="body2" color="text.secondary">
                Awaiting review
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckCircle color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Completed Today</Typography>
              </Box>
              <Typography variant="h3">{stats?.completed_today || 0}</Typography>
              <Typography variant="body2" color="text.secondary">
                Fulfilled requests
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Popular Services */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Popular Services
              </Typography>
              {stats?.popular_services && stats.popular_services.length > 0 ? (
                <Box>
                  {stats.popular_services.map((service, index) => (
                    <Box
                      key={service.id}
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        mb: 2,
                        pb: 2,
                        borderBottom: index < stats.popular_services.length - 1 ? '1px solid #e0e0e0' : 'none',
                      }}
                    >
                      <Box>
                        <Typography variant="body1" fontWeight="medium">
                          {service.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {service.request_count} requests
                        </Typography>
                      </Box>
                      <Button
                        size="small"
                        onClick={() => navigate(`/service-catalog/browse?service=${service.id}`)}
                      >
                        View
                      </Button>
                    </Box>
                  ))}
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Performance Metrics
              </Typography>
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Average Fulfillment Time
                </Typography>
                <Typography variant="h4">
                  {stats?.avg_fulfillment_time ? `${stats.avg_fulfillment_time.toFixed(1)} hours` : 'N/A'}
                </Typography>
              </Box>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => navigate('/service-catalog/analytics')}
              >
                View Detailed Analytics
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Requests */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Recent Requests</Typography>
            <Button size="small" onClick={() => navigate('/service-catalog/requests')}>
              View All
            </Button>
          </Box>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Request ID</TableCell>
                  <TableCell>Service</TableCell>
                  <TableCell>Requester</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recentRequests.length > 0 ? (
                  recentRequests.map((request) => (
                    <TableRow key={request.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {request.id.substring(0, 8)}
                        </Typography>
                      </TableCell>
                      <TableCell>{request.service_name}</TableCell>
                      <TableCell>{request.requester_name}</TableCell>
                      <TableCell>
                        <Chip
                          icon={getStatusIcon(request.status)}
                          label={request.status.replace(/_/g, ' ').toUpperCase()}
                          color={getStatusColor(request.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(request.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => navigate(`/service-catalog/requests/${request.id}`)}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No recent requests
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ServiceCatalogDashboard;