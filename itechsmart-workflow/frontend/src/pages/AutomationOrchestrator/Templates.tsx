import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  ContentCopy,
  Visibility,
  Schedule,
  Webhook,
  Email,
  Event,
  Security,
  CloudUpload,
  BugReport,
  Backup,
  Notifications,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  trigger_type: string;
  node_count: number;
  estimated_time: string;
  use_count: number;
}

const AutomationOrchestratorTemplates: React.FC = () => {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTemplate, setSelectedTemplate] = useState<WorkflowTemplate | null>(null);
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [workflowName, setWorkflowName] = useState('');

  const categoryIcons: Record<string, React.ReactElement> = {
    'incident-response': <Security />,
    'deployment': <CloudUpload />,
    'monitoring': <Notifications />,
    'backup': <Backup />,
    'testing': <BugReport />,
  };

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/automation-orchestrator/templates');
      const data = await response.json();
      setTemplates(data.templates || []);
    } catch (error) {
      console.error('Error fetching templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePreviewTemplate = async (template: WorkflowTemplate) => {
    setSelectedTemplate(template);
    setPreviewDialogOpen(true);
  };

  const handleUseTemplate = (template: WorkflowTemplate) => {
    setSelectedTemplate(template);
    setWorkflowName(`${template.name} - Copy`);
    setCreateDialogOpen(true);
  };

  const handleCreateFromTemplate = async () => {
    if (!selectedTemplate) return;

    try {
      const response = await fetch(`/api/automation-orchestrator/templates/${selectedTemplate.id}/use`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: workflowName }),
      });

      if (response.ok) {
        const data = await response.json();
        navigate(`/automation-orchestrator/builder?id=${data.workflow_id}`);
      }
    } catch (error) {
      console.error('Error creating workflow from template:', error);
    }
  };

  const getTriggerColor = (triggerType: string) => {
    const colors: Record<string, 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'> = {
      manual: 'default',
      schedule: 'primary',
      webhook: 'info',
      event: 'secondary',
      email: 'warning',
    };
    return colors[triggerType] || 'default';
  };

  const getCategoryIcon = (category: string) => {
    return categoryIcons[category] || <Event />;
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
      <Typography variant="h4" component="h1" sx={{ mb: 3 }}>
        Workflow Templates
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        Start with pre-built workflow templates to quickly automate common tasks. Customize them to fit your needs.
      </Alert>

      {/* Templates Grid */}
      <Grid container spacing={3}>
        {templates.length > 0 ? (
          templates.map((template) => (
            <Grid item xs={12} sm={6} md={4} key={template.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {getCategoryIcon(template.category)}
                    <Chip
                      label={template.category.toUpperCase().replace('-', ' ')}
                      size="small"
                      color="primary"
                      variant="outlined"
                      sx={{ ml: 1 }}
                    />
                  </Box>

                  <Typography variant="h6" gutterBottom>
                    {template.name}
                  </Typography>

                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {template.description}
                  </Typography>

                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Schedule fontSize="small" color="action" />
                    <Typography variant="body2" color="text.secondary" sx={{ ml: 0.5 }}>
                      Est. {template.estimated_time}
                    </Typography>
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      {template.node_count} steps
                    </Typography>
                  </Box>

                  <Chip
                    label={`Trigger: ${template.trigger_type.toUpperCase()}`}
                    color={getTriggerColor(template.trigger_type)}
                    size="small"
                    sx={{ mt: 1 }}
                  />

                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
                    Used {template.use_count} times
                  </Typography>
                </CardContent>

                <CardActions>
                  <Button
                    size="small"
                    startIcon={<Visibility />}
                    onClick={() => handlePreviewTemplate(template)}
                  >
                    Preview
                  </Button>
                  <Button
                    size="small"
                    variant="contained"
                    startIcon={<ContentCopy />}
                    onClick={() => handleUseTemplate(template)}
                  >
                    Use Template
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))
        ) : (
          <Grid item xs={12}>
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <Typography variant="h6" color="text.secondary">
                No templates available
              </Typography>
            </Box>
          </Grid>
        )}
      </Grid>

      {/* Preview Dialog */}
      <Dialog
        open={previewDialogOpen}
        onClose={() => setPreviewDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Template Preview: {selectedTemplate?.name}</DialogTitle>
        <DialogContent>
          {selectedTemplate && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body1" paragraph>
                {selectedTemplate.description}
              </Typography>

              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Category
                  </Typography>
                  <Chip
                    label={selectedTemplate.category.toUpperCase().replace('-', ' ')}
                    size="small"
                    color="primary"
                    sx={{ mt: 1 }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Trigger Type
                  </Typography>
                  <Chip
                    label={selectedTemplate.trigger_type.toUpperCase()}
                    color={getTriggerColor(selectedTemplate.trigger_type)}
                    size="small"
                    sx={{ mt: 1 }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Number of Steps
                  </Typography>
                  <Typography variant="h6">{selectedTemplate.node_count}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Estimated Time
                  </Typography>
                  <Typography variant="h6">{selectedTemplate.estimated_time}</Typography>
                </Grid>
              </Grid>

              <Alert severity="info">
                This template has been used {selectedTemplate.use_count} times by other users.
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewDialogOpen(false)}>Close</Button>
          <Button
            variant="contained"
            startIcon={<ContentCopy />}
            onClick={() => {
              setPreviewDialogOpen(false);
              if (selectedTemplate) {
                handleUseTemplate(selectedTemplate);
              }
            }}
          >
            Use This Template
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create from Template Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create Workflow from Template</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Alert severity="info" sx={{ mb: 2 }}>
              Creating a new workflow based on: <strong>{selectedTemplate?.name}</strong>
            </Alert>
            <TextField
              fullWidth
              label="Workflow Name"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              required
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreateFromTemplate}
            disabled={!workflowName}
          >
            Create Workflow
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AutomationOrchestratorTemplates;