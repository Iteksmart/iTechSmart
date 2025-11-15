import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  LinearProgress,
  Tabs,
  Tab,
  Grid,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Visibility,
  CheckCircle,
  Error,
  Schedule,
  PlayArrow,
  Stop,
  ExpandMore,
  Refresh,
} from '@mui/icons-material';

interface Execution {
  id: string;
  workflow_id: string;
  workflow_name: string;
  status: string;
  trigger_type: string;
  started_at: string;
  completed_at: string | null;
  duration: number;
  input_data: Record<string, any>;
  output_data: Record<string, any>;
  error_message: string | null;
}

interface ExecutionLog {
  timestamp: string;
  level: string;
  message: string;
  node_id: string | null;
}

const AutomationOrchestratorExecutions: React.FC = () => {
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [filteredExecutions, setFilteredExecutions] = useState<Execution[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedExecution, setSelectedExecution] = useState<Execution | null>(null);
  const [executionLogs, setExecutionLogs] = useState<ExecutionLog[]>([]);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState('all');

  const statusOptions = ['all', 'pending', 'running', 'completed', 'failed', 'cancelled'];

  useEffect(() => {
    fetchExecutions();
    const interval = setInterval(fetchExecutions, 5000); // Auto-refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    filterExecutions();
  }, [executions, statusFilter]);

  const fetchExecutions = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/automation-orchestrator/executions');
      const data = await response.json();
      setExecutions(data.executions || []);
    } catch (error) {
      console.error('Error fetching executions:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterExecutions = () => {
    if (statusFilter === 'all') {
      setFilteredExecutions(executions);
    } else {
      setFilteredExecutions(executions.filter(e => e.status === statusFilter));
    }
  };

  const handleViewDetails = async (executionId: string) => {
    try {
      const response = await fetch(`/api/automation-orchestrator/executions/${executionId}`);
      const data = await response.json();
      setSelectedExecution(data);

      // Fetch execution logs
      const logsResponse = await fetch(`/api/automation-orchestrator/executions/${executionId}/logs`);
      const logsData = await logsResponse.json();
      setExecutionLogs(logsData.logs || []);

      setDetailsDialogOpen(true);
    } catch (error) {
      console.error('Error fetching execution details:', error);
    }
  };

  const handleCancelExecution = async (executionId: string) => {
    try {
      await fetch(`/api/automation-orchestrator/executions/${executionId}/cancel`, {
        method: 'POST',
      });
      fetchExecutions();
      setDetailsDialogOpen(false);
    } catch (error) {
      console.error('Error cancelling execution:', error);
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

  const getLogLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      DEBUG: '#9e9e9e',
      INFO: '#2196f3',
      WARNING: '#ff9800',
      ERROR: '#f44336',
    };
    return colors[level] || '#9e9e9e';
  };

  if (loading && executions.length === 0) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Workflow Executions
        </Typography>
        <Button startIcon={<Refresh />} onClick={fetchExecutions}>
          Refresh
        </Button>
      </Box>

      {/* Status Filter Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs
          value={statusFilter}
          onChange={(e, newValue) => setStatusFilter(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          {statusOptions.map((status) => (
            <Tab
              key={status}
              label={status.toUpperCase()}
              value={status}
            />
          ))}
        </Tabs>
      </Box>

      {/* Executions Table */}
      <Card>
        <CardContent>
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
                  <TableCell>Completed</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredExecutions.length > 0 ? (
                  filteredExecutions.map((execution) => (
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
                      <TableCell>
                        {execution.completed_at
                          ? new Date(execution.completed_at).toLocaleString()
                          : 'In Progress'}
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => handleViewDetails(execution.id)}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        {execution.status === 'running' && (
                          <Tooltip title="Cancel">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleCancelExecution(execution.id)}
                            >
                              <Stop />
                            </IconButton>
                          </Tooltip>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No executions found
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Execution Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          Execution Details: {selectedExecution?.workflow_name}
        </DialogTitle>
        <DialogContent>
          {selectedExecution && (
            <Box sx={{ mt: 2 }}>
              {/* Status and Metrics */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip
                    icon={getStatusIcon(selectedExecution.status)}
                    label={selectedExecution.status.toUpperCase()}
                    color={getStatusColor(selectedExecution.status)}
                    sx={{ mt: 1 }}
                  />
                </Grid>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Duration
                  </Typography>
                  <Typography variant="h6">
                    {formatDuration(selectedExecution.duration)}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Started At
                  </Typography>
                  <Typography variant="body1">
                    {new Date(selectedExecution.started_at).toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Completed At
                  </Typography>
                  <Typography variant="body1">
                    {selectedExecution.completed_at
                      ? new Date(selectedExecution.completed_at).toLocaleString()
                      : 'In Progress'}
                  </Typography>
                </Grid>
              </Grid>

              {/* Error Message */}
              {selectedExecution.error_message && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  <Typography variant="body2" fontWeight="medium">
                    Error:
                  </Typography>
                  <Typography variant="body2">{selectedExecution.error_message}</Typography>
                </Alert>
              )}

              {/* Input/Output Data */}
              <Accordion sx={{ mb: 2 }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6">Input Data</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Paper variant="outlined" sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
                    <pre style={{ margin: 0, overflow: 'auto' }}>
                      {JSON.stringify(selectedExecution.input_data, null, 2)}
                    </pre>
                  </Paper>
                </AccordionDetails>
              </Accordion>

              <Accordion sx={{ mb: 2 }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6">Output Data</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Paper variant="outlined" sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
                    <pre style={{ margin: 0, overflow: 'auto' }}>
                      {JSON.stringify(selectedExecution.output_data, null, 2)}
                    </pre>
                  </Paper>
                </AccordionDetails>
              </Accordion>

              {/* Execution Logs */}
              <Box>
                <Typography variant="h6" gutterBottom>
                  Execution Logs
                </Typography>
                <Paper
                  variant="outlined"
                  sx={{
                    p: 2,
                    backgroundColor: '#1e1e1e',
                    color: '#fff',
                    maxHeight: 400,
                    overflow: 'auto',
                    fontFamily: 'monospace',
                    fontSize: '0.875rem',
                  }}
                >
                  {executionLogs.length > 0 ? (
                    executionLogs.map((log, index) => (
                      <Box key={index} sx={{ mb: 1 }}>
                        <Typography
                          component="span"
                          sx={{ color: '#888', mr: 1 }}
                        >
                          [{new Date(log.timestamp).toLocaleTimeString()}]
                        </Typography>
                        <Typography
                          component="span"
                          sx={{ color: getLogLevelColor(log.level), mr: 1, fontWeight: 'bold' }}
                        >
                          {log.level}
                        </Typography>
                        {log.node_id && (
                          <Typography
                            component="span"
                            sx={{ color: '#64b5f6', mr: 1 }}
                          >
                            [{log.node_id}]
                          </Typography>
                        )}
                        <Typography component="span">{log.message}</Typography>
                      </Box>
                    ))
                  ) : (
                    <Typography color="text.secondary">No logs available</Typography>
                  )}
                </Paper>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          {selectedExecution?.status === 'running' && (
            <Button
              color="error"
              startIcon={<Stop />}
              onClick={() => handleCancelExecution(selectedExecution.id)}
            >
              Cancel Execution
            </Button>
          )}
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AutomationOrchestratorExecutions;