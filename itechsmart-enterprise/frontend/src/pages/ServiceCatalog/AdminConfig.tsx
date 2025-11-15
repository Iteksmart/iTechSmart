import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Switch,
  FormControlLabel,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  Save as SaveIcon
} from '@mui/icons-material';

interface ServiceItem {
  id: number;
  name: string;
  description: string;
  category: string;
  icon: string;
  form_schema: any;
  requires_approval: boolean;
  automation_enabled: boolean;
  automation_type?: string;
  ai_assisted: boolean;
  sla_hours: number;
  is_active: boolean;
}

const categories = [
  { id: 'access_management', name: '🔐 Access Management' },
  { id: 'it_support', name: '💻 IT Support' },
  { id: 'systems_servers', name: '🖥 Systems & Servers' },
  { id: 'devops_automation', name: '🛠 DevOps & Automation' },
  { id: 'network_requests', name: '🔧 Network Requests' },
  { id: 'software_deployment', name: '📦 Software Deployment' },
  { id: 'hardware_requests', name: '🧾 Hardware Requests' },
  { id: 'hr_onboarding', name: '🧑‍💼 HR / Employee Onboarding' }
];

const automationTypes = [
  'powershell',
  'bash',
  'ssh',
  'python',
  'api_call',
  'webhook',
  'ai_agent'
];

const AdminConfig: React.FC = () => {
  const [serviceItems, setServiceItems] = useState<ServiceItem[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<ServiceItem | null>(null);
  const [formData, setFormData] = useState<any>({
    name: '',
    description: '',
    category: 'it_support',
    icon: '📋',
    requires_approval: true,
    automation_enabled: false,
    ai_assisted: false,
    sla_hours: 24,
    form_schema: { fields: [] }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadServiceItems();
  }, []);

  const loadServiceItems = async () => {
    try {
      const response = await fetch('/api/service-catalog/items?active_only=false');
      const data = await response.json();
      setServiceItems(data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading service items:', error);
      setLoading(false);
    }
  };

  const handleOpenDialog = (item?: ServiceItem) => {
    if (item) {
      setEditingItem(item);
      setFormData(item);
    } else {
      setEditingItem(null);
      setFormData({
        name: '',
        description: '',
        category: 'it_support',
        icon: '📋',
        requires_approval: true,
        automation_enabled: false,
        ai_assisted: false,
        sla_hours: 24,
        form_schema: { fields: [] }
      });
    }
    setDialogOpen(true);
  };

  const handleSave = async () => {
    try {
      const response = await fetch('/api/service-catalog/items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        setDialogOpen(false);
        loadServiceItems();
        alert('Service item saved successfully!');
      } else {
        const data = await response.json();
        alert('Error saving: ' + (data.detail || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error saving service item:', error);
      alert('Error saving service item');
    }
  };

  const handleSeedItems = async () => {
    try {
      const response = await fetch('/api/service-catalog/items/seed', {
        method: 'POST'
      });
      
      const data = await response.json();
      alert(data.message);
      loadServiceItems();
    } catch (error) {
      console.error('Error seeding items:', error);
      alert('Error seeding items');
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h3" gutterBottom fontWeight="bold" color="primary">
            ⚙️ Service Catalog Admin
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Configure service items, workflows, and automation
          </Typography>
        </Box>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            onClick={handleSeedItems}
          >
            Seed Sample Items
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            New Service Item
          </Button>
        </Box>
      </Box>

      {/* Service Items Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
              <TableCell><strong>Service</strong></TableCell>
              <TableCell><strong>Category</strong></TableCell>
              <TableCell><strong>SLA</strong></TableCell>
              <TableCell><strong>Features</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {serviceItems.map((item) => (
              <TableRow key={item.id} hover>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    <span style={{ fontSize: '1.5rem', marginRight: 8 }}>
                      {item.icon}
                    </span>
                    <Box>
                      <Typography variant="body2" fontWeight="bold">
                        {item.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {item.description.substring(0, 60)}...
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={categories.find(c => c.id === item.category)?.name || item.category}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {item.sla_hours}h
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box display="flex" flexDirection="column" gap={0.5}>
                    {item.automation_enabled && (
                      <Chip label="⚡ Auto" size="small" color="success" />
                    )}
                    {item.ai_assisted && (
                      <Chip label="🤖 AI" size="small" color="primary" />
                    )}
                    {item.requires_approval && (
                      <Chip label="✓ Approval" size="small" color="warning" />
                    )}
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={item.is_active ? 'Active' : 'Inactive'}
                    color={item.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => handleOpenDialog(item)}
                  >
                    <EditIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {serviceItems.length === 0 && (
        <Box textAlign="center" py={8}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No service items configured
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleSeedItems}
            sx={{ mt: 2 }}
          >
            Seed Sample Items
          </Button>
        </Box>
      )}

      {/* Create/Edit Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingItem ? 'Edit Service Item' : 'Create Service Item'}
        </DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={3}>
            {/* Basic Info */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom fontWeight="bold">
                Basic Information
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="Service Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Icon (Emoji)"
                value={formData.icon}
                onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={formData.category}
                  label="Category"
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                >
                  {categories.map((cat) => (
                    <MenuItem key={cat.id} value={cat.id}>
                      {cat.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="SLA (Hours)"
                type="number"
                value={formData.sla_hours}
                onChange={(e) => setFormData({ ...formData, sla_hours: parseInt(e.target.value) })}
              />
            </Grid>

            {/* Configuration */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom fontWeight="bold" sx={{ mt: 2 }}>
                Configuration
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.requires_approval}
                    onChange={(e) => setFormData({ ...formData, requires_approval: e.target.checked })}
                  />
                }
                label="Requires Approval"
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.automation_enabled}
                    onChange={(e) => setFormData({ ...formData, automation_enabled: e.target.checked })}
                  />
                }
                label="Automation Enabled"
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.ai_assisted}
                    onChange={(e) => setFormData({ ...formData, ai_assisted: e.target.checked })}
                  />
                }
                label="AI-Assisted"
              />
            </Grid>

            {/* Automation Config */}
            {formData.automation_enabled && (
              <>
                <Grid item xs={12}>
                  <Alert severity="info">
                    <strong>Automation Configuration:</strong> Configure how this service will be automatically fulfilled.
                  </Alert>
                </Grid>
                
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Automation Type</InputLabel>
                    <Select
                      value={formData.automation_type || ''}
                      label="Automation Type"
                      onChange={(e) => setFormData({ ...formData, automation_type: e.target.value })}
                    >
                      {automationTypes.map((type) => (
                        <MenuItem key={type} value={type}>
                          {type.replace(/_/g, ' ').toUpperCase()}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Automation Script/Configuration"
                    multiline
                    rows={6}
                    value={formData.automation_script || ''}
                    onChange={(e) => setFormData({ ...formData, automation_script: e.target.value })}
                    placeholder="Enter script or configuration JSON..."
                    helperText="Use {field_name} to reference form fields"
                  />
                </Grid>
              </>
            )}

            {/* Form Schema */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom fontWeight="bold" sx={{ mt: 2 }}>
                Form Fields (JSON Schema)
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={10}
                value={JSON.stringify(formData.form_schema, null, 2)}
                onChange={(e) => {
                  try {
                    const schema = JSON.parse(e.target.value);
                    setFormData({ ...formData, form_schema: schema });
                  } catch (err) {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='{"fields": [{"name": "field1", "label": "Field 1", "type": "text", "required": true}]}'
                helperText="Define form fields in JSON format"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSave}
          >
            Save Service Item
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default AdminConfig;