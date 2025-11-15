import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Chip,
  LinearProgress,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  CheckCircle,
  Cancel,
} from '@mui/icons-material';

interface Service {
  id: string;
  name: string;
  description: string;
  category: string;
  price: number;
  estimated_delivery_hours: number;
  is_active: boolean;
  requires_approval: boolean;
  approval_chain: string[];
  form_schema: any;
}

interface ApprovalRequest {
  id: string;
  request_id: string;
  service_name: string;
  requester_name: string;
  priority: string;
  business_justification: string;
  status: string;
  created_at: string;
}

const ServiceCatalogAdmin: React.FC = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [approvalRequests, setApprovalRequests] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [serviceDialogOpen, setServiceDialogOpen] = useState(false);
  const [approvalDialogOpen, setApprovalDialogOpen] = useState(false);
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [selectedApproval, setSelectedApproval] = useState<ApprovalRequest | null>(null);
  const [approvalComments, setApprovalComments] = useState('');
  const [serviceFormData, setServiceFormData] = useState<Partial<Service>>({
    name: '',
    description: '',
    category: 'hardware',
    price: 0,
    estimated_delivery_hours: 24,
    is_active: true,
    requires_approval: false,
    approval_chain: [],
    form_schema: { fields: [] },
  });

  const categories = [
    'hardware',
    'software',
    'access',
    'cloud',
    'network',
    'support',
    'training',
    'other',
  ];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch services
      const servicesResponse = await fetch('/api/service-catalog/services');
      const servicesData = await servicesResponse.json();
      setServices(servicesData.services || []);

      // Fetch pending approvals
      const approvalsResponse = await fetch('/api/service-catalog/approvals/pending');
      const approvalsData = await approvalsResponse.json();
      setApprovalRequests(approvalsData.approvals || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateService = () => {
    setSelectedService(null);
    setServiceFormData({
      name: '',
      description: '',
      category: 'hardware',
      price: 0,
      estimated_delivery_hours: 24,
      is_active: true,
      requires_approval: false,
      approval_chain: [],
      form_schema: { fields: [] },
    });
    setServiceDialogOpen(true);
  };

  const handleEditService = (service: Service) => {
    setSelectedService(service);
    setServiceFormData(service);
    setServiceDialogOpen(true);
  };

  const handleSaveService = async () => {
    try {
      const url = selectedService
        ? `/api/service-catalog/services/${selectedService.id}`
        : '/api/service-catalog/services';
      
      const method = selectedService ? 'PUT' : 'POST';

      await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(serviceFormData),
      });

      setServiceDialogOpen(false);
      fetchData();
    } catch (error) {
      console.error('Error saving service:', error);
    }
  };

  const handleDeleteService = async (serviceId: string) => {
    if (!window.confirm('Are you sure you want to delete this service?')) return;

    try {
      await fetch(`/api/service-catalog/services/${serviceId}`, {
        method: 'DELETE',
      });
      fetchData();
    } catch (error) {
      console.error('Error deleting service:', error);
    }
  };

  const handleApprovalAction = async (action: 'approve' | 'reject') => {
    if (!selectedApproval) return;

    try {
      await fetch(`/api/service-catalog/approvals/${selectedApproval.id}/${action}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ comments: approvalComments }),
      });

      setApprovalDialogOpen(false);
      setApprovalComments('');
      fetchData();
    } catch (error) {
      console.error(`Error ${action}ing request:`, error);
    }
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'> = {
      low: 'info',
      medium: 'primary',
      high: 'warning',
      critical: 'error',
    };
    return colors[priority] || 'default';
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
          Service Catalog Administration
        </Typography>
        {activeTab === 0 && (
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleCreateService}
          >
            Create Service
          </Button>
        )}
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Services" />
          <Tab label={`Pending Approvals (${approvalRequests.length})`} />
        </Tabs>
      </Box>

      {/* Services Tab */}
      {activeTab === 0 && (
        <Card>
          <CardContent>
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Price</TableCell>
                    <TableCell>Delivery Time</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Requires Approval</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {services.map((service) => (
                    <TableRow key={service.id} hover>
                      <TableCell>{service.name}</TableCell>
                      <TableCell>
                        <Chip
                          label={service.category.toUpperCase()}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>${service.price.toFixed(2)}</TableCell>
                      <TableCell>{service.estimated_delivery_hours}h</TableCell>
                      <TableCell>
                        <Chip
                          label={service.is_active ? 'ACTIVE' : 'INACTIVE'}
                          color={service.is_active ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {service.requires_approval ? (
                          <CheckCircle color="primary" fontSize="small" />
                        ) : (
                          <Cancel color="disabled" fontSize="small" />
                        )}
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="Edit">
                          <IconButton
                            size="small"
                            onClick={() => handleEditService(service)}
                          >
                            <Edit />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDeleteService(service.id)}
                          >
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Approvals Tab */}
      {activeTab === 1 && (
        <Card>
          <CardContent>
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Request ID</TableCell>
                    <TableCell>Service</TableCell>
                    <TableCell>Requester</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {approvalRequests.length > 0 ? (
                    approvalRequests.map((approval) => (
                      <TableRow key={approval.id} hover>
                        <TableCell>
                          <Typography variant="body2" fontFamily="monospace">
                            {approval.request_id.substring(0, 8)}
                          </Typography>
                        </TableCell>
                        <TableCell>{approval.service_name}</TableCell>
                        <TableCell>{approval.requester_name}</TableCell>
                        <TableCell>
                          <Chip
                            label={approval.priority.toUpperCase()}
                            color={getPriorityColor(approval.priority)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          {new Date(approval.created_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="Review">
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedApproval(approval);
                                setApprovalDialogOpen(true);
                              }}
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
                          No pending approvals
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Service Dialog */}
      <Dialog
        open={serviceDialogOpen}
        onClose={() => setServiceDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedService ? 'Edit Service' : 'Create Service'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Service Name"
                  value={serviceFormData.name}
                  onChange={(e) =>
                    setServiceFormData({ ...serviceFormData, name: e.target.value })
                  }
                  required
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Description"
                  value={serviceFormData.description}
                  onChange={(e) =>
                    setServiceFormData({ ...serviceFormData, description: e.target.value })
                  }
                  required
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={serviceFormData.category}
                    label="Category"
                    onChange={(e) =>
                      setServiceFormData({ ...serviceFormData, category: e.target.value })
                    }
                  >
                    {categories.map((cat) => (
                      <MenuItem key={cat} value={cat}>
                        {cat.charAt(0).toUpperCase() + cat.slice(1)}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Price ($)"
                  value={serviceFormData.price}
                  onChange={(e) =>
                    setServiceFormData({ ...serviceFormData, price: parseFloat(e.target.value) })
                  }
                  required
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Estimated Delivery (hours)"
                  value={serviceFormData.estimated_delivery_hours}
                  onChange={(e) =>
                    setServiceFormData({
                      ...serviceFormData,
                      estimated_delivery_hours: parseInt(e.target.value),
                    })
                  }
                  required
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={serviceFormData.is_active}
                      onChange={(e) =>
                        setServiceFormData({ ...serviceFormData, is_active: e.target.checked })
                      }
                    />
                  }
                  label="Active"
                />
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={serviceFormData.requires_approval}
                      onChange={(e) =>
                        setServiceFormData({
                          ...serviceFormData,
                          requires_approval: e.target.checked,
                        })
                      }
                    />
                  }
                  label="Requires Approval"
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setServiceDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSaveService}
            disabled={!serviceFormData.name || !serviceFormData.description}
          >
            {selectedService ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Approval Dialog */}
      <Dialog
        open={approvalDialogOpen}
        onClose={() => setApprovalDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Review Request</DialogTitle>
        <DialogContent>
          {selectedApproval && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Service
                  </Typography>
                  <Typography variant="body1">{selectedApproval.service_name}</Typography>
                </Grid>

                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Requester
                  </Typography>
                  <Typography variant="body1">{selectedApproval.requester_name}</Typography>
                </Grid>

                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Business Justification
                  </Typography>
                  <Typography variant="body1">
                    {selectedApproval.business_justification}
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    label="Comments (Optional)"
                    value={approvalComments}
                    onChange={(e) => setApprovalComments(e.target.value)}
                  />
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApprovalDialogOpen(false)}>Cancel</Button>
          <Button
            color="error"
            startIcon={<Cancel />}
            onClick={() => handleApprovalAction('reject')}
          >
            Reject
          </Button>
          <Button
            variant="contained"
            color="success"
            startIcon={<CheckCircle />}
            onClick={() => handleApprovalAction('approve')}
          >
            Approve
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ServiceCatalogAdmin;