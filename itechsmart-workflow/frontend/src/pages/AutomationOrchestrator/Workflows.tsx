import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  PlayArrow,
  Stop,
  ContentCopy,
  Visibility,
  Schedule,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface Workflow {
  id: string;
  name: string;
  description: string;
  trigger_type: string;
  is_active: boolean;
  created_at: string;
  last_execution: string | null;
  execution_count: number;
  success_rate: number;
}

const AutomationOrchestratorWorkflows: React.FC = () => {
  const navigate = useNavigate();
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [executeDialogOpen, setExecuteDialogOpen] = useState(false);
  const [executionInput, setExecutionInput] = useState('{}');

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/automation-orchestrator/workflows');
      const data = await response.json();
      setWorkflows(data.workflows || []);
    } catch (error) {
      console.error('Error fetching workflows:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (workflowId: string, isActive: boolean) => {
    try {
      await fetch(`/api/automation-orchestrator/workflows/${workflowId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_active: !isActive }),
      });
      fetchWorkflows();
    } catch (error) {
      console.error('Error toggling workflow:', error);
    }
  };

  const handleExecuteWorkflow = async () => {
    if (!selectedWorkflow) return;

    try {
      const input = JSON.parse(executionInput);
      await fetch(`/api/automation-orchestrator/workflows/${selectedWorkflow.id}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input }),
      });
      setExecuteDialogOpen(false);
      navigate('/automation-orchestrator/executions');
    } catch (error) {
      console.error('Error executing workflow:', error);
    }
  };

  const handleDuplicateWorkflow = async (workflowId: string) => {
    try {
      const response = await fetch(`/api/automation-orchestrator/workflows/${workflowId}/duplicate`, {
        method: 'POST',
      });
      if (response.ok) {
        fetchWorkflows();
      }
    } catch (error) {
      console.error('Error duplicating workflow:', error);
    }
  };

  const handleDeleteWorkflow = async () => {
    if (!selectedWorkflow) return;

    try {
      await fetch(`/api/automation-orchestrator/workflows/${selectedWorkflow.id}`, {
        method: 'DELETE',
      });
      setDeleteDialogOpen(false);
      setSelectedWorkflow(null);
      fetchWorkflows();
    } catch (error) {
      console.error('Error deleting workflow:', error);
    }
  };

  const getTriggerColor = (triggerType: string) => {
    const colors: Record<string, 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'> = {
      manual: 'default',
      schedule: 'primary',
      webhook: 'info',
      event: 'secondary',
      email: 'warning',
      file: 'success',
    };
    return colors[triggerType] || 'default';
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
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Workflows
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => navigate('/automation-orchestrator/builder')}
        >
          Create Workflow
        </Button>
      </Box>

      {/* Workflows Table */}
      <Card>
        <CardContent>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Trigger</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Executions</TableCell>
                  <TableCell>Success Rate</TableCell>
                  <TableCell>Last Run</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {workflows.length > 0 ? (
                  workflows.map((workflow) => (
                    <TableRow key={workflow.id} hover>
                      <TableCell>
                        <Typography variant="body1" fontWeight="medium">
                          {workflow.name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {workflow.description}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={workflow.trigger_type.toUpperCase()}
                          color={getTriggerColor(workflow.trigger_type)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Switch
                          checked={workflow.is_active}
                          onChange={() => handleToggleActive(workflow.id, workflow.is_active)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{workflow.execution_count}</TableCell>
                      <TableCell>
                        <Chip
                          label={`${workflow.success_rate.toFixed(1)}%`}
                          color={workflow.success_rate >= 90 ? 'success' : workflow.success_rate >= 70 ? 'warning' : 'error'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {workflow.last_execution
                          ? new Date(workflow.last_execution).toLocaleDateString()
                          : 'Never'}
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="Execute">
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={() => {
                              setSelectedWorkflow(workflow);
                              setExecuteDialogOpen(true);
                            }}
                          >
                            <PlayArrow />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="View">
                          <IconButton
                            size="small"
                            onClick={() => navigate(`/automation-orchestrator/workflows/${workflow.id}`)}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit">
                          <IconButton
                            size="small"
                            onClick={() => navigate(`/automation-orchestrator/builder?id=${workflow.id}`)}
                          >
                            <Edit />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Duplicate">
                          <IconButton
                            size="small"
                            onClick={() => handleDuplicateWorkflow(workflow.id)}
                          >
                            <ContentCopy />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => {
                              setSelectedWorkflow(workflow);
                              setDeleteDialogOpen(true);
                            }}
                          >
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <Box sx={{ py: 4 }}>
                        <Typography variant="body1" color="text.secondary" gutterBottom>
                          No workflows found
                        </Typography>
                        <Button
                          variant="contained"
                          startIcon={<Add />}
                          onClick={() => navigate('/automation-orchestrator/builder')}
                          sx={{ mt: 2 }}
                        >
                          Create Your First Workflow
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Execute Dialog */}
      <Dialog
        open={executeDialogOpen}
        onClose={() => setExecuteDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Execute Workflow: {selectedWorkflow?.name}</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Alert severity="info" sx={{ mb: 2 }}>
              Provide input data for the workflow execution (JSON format)
            </Alert>
            <TextField
              fullWidth
              multiline
              rows={8}
              label="Input Data (JSON)"
              value={executionInput}
              onChange={(e) => setExecutionInput(e.target.value)}
              placeholder='{"key": "value"}'
              sx={{ fontFamily: 'monospace' }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExecuteDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={handleExecuteWorkflow}
          >
            Execute
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Delete Workflow</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mt: 2 }}>
            Are you sure you want to delete the workflow "{selectedWorkflow?.name}"? This action
            cannot be undone.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button color="error" variant="contained" onClick={handleDeleteWorkflow}>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AutomationOrchestratorWorkflows;