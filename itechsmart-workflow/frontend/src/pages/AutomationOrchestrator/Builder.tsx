import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Divider,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert,
} from '@mui/material';
import {
  Add,
  Delete,
  Save,
  PlayArrow,
  ArrowDownward,
  Settings,
  Schedule,
  Webhook,
  Email,
  Event,
  Code,
  Http,
  Storage,
  Notifications,
} from '@mui/icons-material';
import { useNavigate, useSearchParams } from 'react-router-dom';

interface WorkflowNode {
  id: string;
  type: string;
  config: Record<string, any>;
  position: number;
}

interface WorkflowData {
  name: string;
  description: string;
  trigger_type: string;
  trigger_config: Record<string, any>;
  nodes: WorkflowNode[];
  is_active: boolean;
}

const AutomationOrchestratorBuilder: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const workflowId = searchParams.get('id');

  const [workflowData, setWorkflowData] = useState<WorkflowData>({
    name: '',
    description: '',
    trigger_type: 'manual',
    trigger_config: {},
    nodes: [],
    is_active: false,
  });

  const [nodeDialogOpen, setNodeDialogOpen] = useState(false);
  const [selectedNodeType, setSelectedNodeType] = useState('');
  const [nodeConfig, setNodeConfig] = useState<Record<string, any>>({});
  const [editingNodeIndex, setEditingNodeIndex] = useState<number | null>(null);

  const triggerTypes = [
    { value: 'manual', label: 'Manual', icon: <PlayArrow /> },
    { value: 'schedule', label: 'Schedule', icon: <Schedule /> },
    { value: 'webhook', label: 'Webhook', icon: <Webhook /> },
    { value: 'event', label: 'Event', icon: <Event /> },
    { value: 'email', label: 'Email', icon: <Email /> },
  ];

  const nodeTypes = [
    { value: 'action', label: 'Action', icon: <Code />, description: 'Execute an action' },
    { value: 'condition', label: 'Condition', icon: <Settings />, description: 'Conditional logic' },
    { value: 'loop', label: 'Loop', icon: <ArrowDownward />, description: 'Iterate over items' },
    { value: 'http_request', label: 'HTTP Request', icon: <Http />, description: 'Make API calls' },
    { value: 'data_transform', label: 'Data Transform', icon: <Storage />, description: 'Transform data' },
    { value: 'notification', label: 'Notification', icon: <Notifications />, description: 'Send notifications' },
  ];

  useEffect(() => {
    if (workflowId) {
      fetchWorkflow();
    }
  }, [workflowId]);

  const fetchWorkflow = async () => {
    try {
      const response = await fetch(`/api/automation-orchestrator/workflows/${workflowId}`);
      const data = await response.json();
      setWorkflowData(data);
    } catch (error) {
      console.error('Error fetching workflow:', error);
    }
  };

  const handleAddNode = () => {
    setSelectedNodeType('');
    setNodeConfig({});
    setEditingNodeIndex(null);
    setNodeDialogOpen(true);
  };

  const handleEditNode = (index: number) => {
    const node = workflowData.nodes[index];
    setSelectedNodeType(node.type);
    setNodeConfig(node.config);
    setEditingNodeIndex(index);
    setNodeDialogOpen(true);
  };

  const handleSaveNode = () => {
    const newNode: WorkflowNode = {
      id: editingNodeIndex !== null ? workflowData.nodes[editingNodeIndex].id : `node_${Date.now()}`,
      type: selectedNodeType,
      config: nodeConfig,
      position: editingNodeIndex !== null ? workflowData.nodes[editingNodeIndex].position : workflowData.nodes.length,
    };

    if (editingNodeIndex !== null) {
      const updatedNodes = [...workflowData.nodes];
      updatedNodes[editingNodeIndex] = newNode;
      setWorkflowData({ ...workflowData, nodes: updatedNodes });
    } else {
      setWorkflowData({ ...workflowData, nodes: [...workflowData.nodes, newNode] });
    }

    setNodeDialogOpen(false);
  };

  const handleDeleteNode = (index: number) => {
    const updatedNodes = workflowData.nodes.filter((_, i) => i !== index);
    setWorkflowData({ ...workflowData, nodes: updatedNodes });
  };

  const handleSaveWorkflow = async () => {
    try {
      const url = workflowId
        ? `/api/automation-orchestrator/workflows/${workflowId}`
        : '/api/automation-orchestrator/workflows';
      
      const method = workflowId ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workflowData),
      });

      if (response.ok) {
        navigate('/automation-orchestrator/workflows');
      }
    } catch (error) {
      console.error('Error saving workflow:', error);
    }
  };

  const getNodeIcon = (type: string) => {
    const node = nodeTypes.find(n => n.value === type);
    return node?.icon || <Code />;
  };

  const getNodeLabel = (type: string) => {
    const node = nodeTypes.find(n => n.value === type);
    return node?.label || type;
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          {workflowId ? 'Edit Workflow' : 'Create Workflow'}
        </Typography>
        <Box>
          <Button
            variant="outlined"
            sx={{ mr: 2 }}
            onClick={() => navigate('/automation-orchestrator/workflows')}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={handleSaveWorkflow}
            disabled={!workflowData.name}
          >
            Save Workflow
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Workflow Configuration */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Workflow Configuration
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <TextField
                fullWidth
                label="Workflow Name"
                value={workflowData.name}
                onChange={(e) => setWorkflowData({ ...workflowData, name: e.target.value })}
                sx={{ mb: 2 }}
                required
              />

              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={workflowData.description}
                onChange={(e) => setWorkflowData({ ...workflowData, description: e.target.value })}
                sx={{ mb: 2 }}
              />

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Trigger Type</InputLabel>
                <Select
                  value={workflowData.trigger_type}
                  label="Trigger Type"
                  onChange={(e) => setWorkflowData({ ...workflowData, trigger_type: e.target.value })}
                >
                  {triggerTypes.map((trigger) => (
                    <MenuItem key={trigger.value} value={trigger.value}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {trigger.icon}
                        <Typography sx={{ ml: 1 }}>{trigger.label}</Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {workflowData.trigger_type === 'schedule' && (
                <TextField
                  fullWidth
                  label="Cron Expression"
                  placeholder="0 0 * * *"
                  value={workflowData.trigger_config.cron || ''}
                  onChange={(e) =>
                    setWorkflowData({
                      ...workflowData,
                      trigger_config: { ...workflowData.trigger_config, cron: e.target.value },
                    })
                  }
                  sx={{ mb: 2 }}
                />
              )}

              {workflowData.trigger_type === 'webhook' && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  Webhook URL will be generated after saving
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Available Nodes */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Available Nodes
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <List>
                {nodeTypes.map((node) => (
                  <ListItem
                    key={node.value}
                    button
                    onClick={() => {
                      setSelectedNodeType(node.value);
                      setNodeConfig({});
                      setEditingNodeIndex(null);
                      setNodeDialogOpen(true);
                    }}
                  >
                    <ListItemIcon>{node.icon}</ListItemIcon>
                    <ListItemText primary={node.label} secondary={node.description} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Workflow Canvas */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Workflow Steps</Typography>
                <Button startIcon={<Add />} onClick={handleAddNode}>
                  Add Node
                </Button>
              </Box>
              <Divider sx={{ mb: 2 }} />

              {/* Trigger Node */}
              <Paper
                variant="outlined"
                sx={{
                  p: 2,
                  mb: 2,
                  backgroundColor: '#e3f2fd',
                  border: '2px solid #2196f3',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {triggerTypes.find(t => t.value === workflowData.trigger_type)?.icon}
                    <Box sx={{ ml: 2 }}>
                      <Typography variant="subtitle1" fontWeight="medium">
                        Trigger: {triggerTypes.find(t => t.value === workflowData.trigger_type)?.label}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Workflow starts here
                      </Typography>
                    </Box>
                  </Box>
                  <Chip label="START" color="primary" size="small" />
                </Box>
              </Paper>

              {/* Workflow Nodes */}
              {workflowData.nodes.length > 0 ? (
                workflowData.nodes.map((node, index) => (
                  <Box key={node.id}>
                    <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                      <ArrowDownward color="action" />
                    </Box>
                    <Paper
                      variant="outlined"
                      sx={{
                        p: 2,
                        mb: 2,
                        '&:hover': {
                          backgroundColor: '#f5f5f5',
                        },
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {getNodeIcon(node.type)}
                          <Box sx={{ ml: 2 }}>
                            <Typography variant="subtitle1" fontWeight="medium">
                              {getNodeLabel(node.type)}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Step {index + 1}
                            </Typography>
                          </Box>
                        </Box>
                        <Box>
                          <IconButton size="small" onClick={() => handleEditNode(index)}>
                            <Settings />
                          </IconButton>
                          <IconButton size="small" color="error" onClick={() => handleDeleteNode(index)}>
                            <Delete />
                          </IconButton>
                        </Box>
                      </Box>
                    </Paper>
                  </Box>
                ))
              ) : (
                <Box sx={{ textAlign: 'center', py: 8 }}>
                  <Typography variant="body1" color="text.secondary" gutterBottom>
                    No workflow steps added yet
                  </Typography>
                  <Button startIcon={<Add />} onClick={handleAddNode} sx={{ mt: 2 }}>
                    Add Your First Node
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Node Configuration Dialog */}
      <Dialog open={nodeDialogOpen} onClose={() => setNodeDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingNodeIndex !== null ? 'Edit Node' : 'Add Node'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Node Type</InputLabel>
              <Select
                value={selectedNodeType}
                label="Node Type"
                onChange={(e) => setSelectedNodeType(e.target.value)}
                disabled={editingNodeIndex !== null}
              >
                {nodeTypes.map((node) => (
                  <MenuItem key={node.value} value={node.value}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {node.icon}
                      <Typography sx={{ ml: 1 }}>{node.label}</Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {selectedNodeType && (
              <>
                <TextField
                  fullWidth
                  label="Node Name"
                  value={nodeConfig.name || ''}
                  onChange={(e) => setNodeConfig({ ...nodeConfig, name: e.target.value })}
                  sx={{ mb: 2 }}
                />

                {selectedNodeType === 'http_request' && (
                  <>
                    <TextField
                      fullWidth
                      label="URL"
                      value={nodeConfig.url || ''}
                      onChange={(e) => setNodeConfig({ ...nodeConfig, url: e.target.value })}
                      sx={{ mb: 2 }}
                    />
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>Method</InputLabel>
                      <Select
                        value={nodeConfig.method || 'GET'}
                        label="Method"
                        onChange={(e) => setNodeConfig({ ...nodeConfig, method: e.target.value })}
                      >
                        <MenuItem value="GET">GET</MenuItem>
                        <MenuItem value="POST">POST</MenuItem>
                        <MenuItem value="PUT">PUT</MenuItem>
                        <MenuItem value="DELETE">DELETE</MenuItem>
                      </Select>
                    </FormControl>
                  </>
                )}

                {selectedNodeType === 'condition' && (
                  <TextField
                    fullWidth
                    label="Condition Expression"
                    value={nodeConfig.expression || ''}
                    onChange={(e) => setNodeConfig({ ...nodeConfig, expression: e.target.value })}
                    placeholder="e.g., data.status == 'active'"
                    sx={{ mb: 2 }}
                  />
                )}

                {selectedNodeType === 'notification' && (
                  <>
                    <TextField
                      fullWidth
                      label="Message"
                      multiline
                      rows={3}
                      value={nodeConfig.message || ''}
                      onChange={(e) => setNodeConfig({ ...nodeConfig, message: e.target.value })}
                      sx={{ mb: 2 }}
                    />
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>Channel</InputLabel>
                      <Select
                        value={nodeConfig.channel || 'email'}
                        label="Channel"
                        onChange={(e) => setNodeConfig({ ...nodeConfig, channel: e.target.value })}
                      >
                        <MenuItem value="email">Email</MenuItem>
                        <MenuItem value="slack">Slack</MenuItem>
                        <MenuItem value="teams">Teams</MenuItem>
                      </Select>
                    </FormControl>
                  </>
                )}
              </>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNodeDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSaveNode}
            disabled={!selectedNodeType}
          >
            {editingNodeIndex !== null ? 'Update' : 'Add'} Node
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AutomationOrchestratorBuilder;