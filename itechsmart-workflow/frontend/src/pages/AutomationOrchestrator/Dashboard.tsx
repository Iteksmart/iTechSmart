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
  PlayArrow,
  Stop,
  CheckCircle,
  Error,
  Schedule,
  TrendingUp,
  Visibility,
  Add,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface DashboardStats {
  total_workflows: number;
  active_workflows: number;
  total_executions: number;
  success_rate: number;
  avg_execution_time: number;
  executions_today: number;
}

interface RecentExecution {
  id: string;
  workflow_name: string;
  status: string;
  started_at: string;
  duration: number;
  trigger_type: string;
}

const AutomationOrchestratorDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentExecutions, setRecentExecutions] = useState<RecentExecution[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch dashboard stats
      const statsResponse = await fetch('/api/automation-orchestrator/dashboard/stats');
      const statsData = await statsResponse.json();
      setStats(statsData);

      // Fetch recent executions
      const executionsResponse = await fetch('/api/automation-orchestrator/executions?limit=10');
      const executionsData = await executionsResponse.json();
      setRecentExecutions(executionsData.executions || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'> = {
      pending: 'default',
      running: 'info',
      completed: 'success',
      failed: 'error',
      cancelled: 'warning',
    };
    return colors[status] || 'default';
  };

  const getStatusIcon = (status: string) => {
    const icons: Record<string, React.ReactElement> = {
      pending: <Schedule />,
      running: <PlayArrow />,
      completed: <CheckCircle />,
      failed: <Error />,
      cancelled: <Stop />,
    };
    return icons[status] || <Schedule />;
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
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
          Automation Orchestrator Dashboard
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<Add />}
          onClick={() => navigate('/automation-orchestrator/builder')}
        >
          Create Workflow
        </Button>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <PlayArrow color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Workflows</Typography>
              </Box>
              <Typography variant="h3">{stats?.total_workflows || 0}</Typography>
              <Typography variant="body2" color="text.secondary">
                {stats?.active_workflows || 0} active
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp color="info" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Executions</Typography>
              </Box>
              <Typography variant="h3">{stats?.total_executions || 0}</Typography>
              <Typography variant="body2" color="text.secondary">
                {stats?.executions_today || 0} today
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckCircle color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Success Rate</Typography>
              </Box>
              <Typography variant="h3">
                {stats?.success_rate ? `${stats.success_rate.toFixed(1)}%` : '0%'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last 30 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Schedule color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Avg Execution Time</Typography>
              </Box>
              <Typography variant="h3">
                {stats?.avg_execution_time ? formatDuration(stats.avg_execution_time) : 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Average duration
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card sx={{ cursor: 'pointer' }} onClick={() => navigate('/automation-orchestrator/workflows')}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Manage Workflows
              </Typography>
              <Typography variant="body2" color="text.secondary">
                View, edit, and manage all your automation workflows
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ cursor: 'pointer' }} onClick={() => navigate('/automation-orchestrator/templates')}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Browse Templates
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Start with pre-built workflow templates
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ cursor: 'pointer' }} onClick={() => navigate('/automation-orchestrator/executions')}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                View Executions
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Monitor workflow execution history and logs
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Executions */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Recent Executions</Typography>
            <Button size="small" onClick={() => navigate('/automation-orchestrator/executions')}>
              View All
            </Button>
          </Box>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Execution ID</TableCell>
                  <TableCell>Workflow</TableCell>
                  <TableCell>Trigger</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Started</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recentExecutions.length > 0 ? (
                  recentExecutions.map((execution) => (
                    <TableRow key={execution.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {execution.id.substring(0, 8)}
                        </Typography>
                      </TableCell>
                      <TableCell>{execution.workflow_name}</TableCell>
                      <TableCell>
                        <Chip
                          label={execution.trigger_type.toUpperCase()}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={getStatusIcon(execution.status)}
                          label={execution.status.toUpperCase()}
                          color={getStatusColor(execution.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{formatDuration(execution.duration)}</TableCell>
                      <TableCell>
                        {new Date(execution.started_at).toLocaleString()}
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => navigate(`/automation-orchestrator/executions/${execution.id}`)}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No recent executions
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

export default AutomationOrchestratorDashboard;