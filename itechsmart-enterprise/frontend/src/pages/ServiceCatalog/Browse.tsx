import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  TextField,
  InputAdornment,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  Search,
  ShoppingCart,
  Category,
  AttachMoney,
  Schedule,
  Info,
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
  form_schema: any;
}

interface RequestFormData {
  service_id: string;
  priority: string;
  business_justification: string;
  cost_center: string;
  form_data: Record<string, any>;
}

const ServiceCatalogBrowse: React.FC = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [filteredServices, setFilteredServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [requestDialogOpen, setRequestDialogOpen] = useState(false);
  const [requestFormData, setRequestFormData] = useState<RequestFormData>({
    service_id: '',
    priority: 'medium',
    business_justification: '',
    cost_center: '',
    form_data: {},
  });
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const categories = [
    'all',
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
    fetchServices();
  }, []);

  useEffect(() => {
    filterServices();
  }, [services, searchQuery, selectedCategory]);

  const fetchServices = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/service-catalog/services?is_active=true');
      const data = await response.json();
      setServices(data.services || []);
    } catch (error) {
      console.error('Error fetching services:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterServices = () => {
    let filtered = services;

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(s => s.category === selectedCategory);
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        s =>
          s.name.toLowerCase().includes(query) ||
          s.description.toLowerCase().includes(query)
      );
    }

    setFilteredServices(filtered);
  };

  const handleRequestService = (service: Service) => {
    setSelectedService(service);
    setRequestFormData({
      service_id: service.id,
      priority: 'medium',
      business_justification: '',
      cost_center: '',
      form_data: {},
    });
    setRequestDialogOpen(true);
  };

  const handleSubmitRequest = async () => {
    try {
      const response = await fetch('/api/service-catalog/requests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestFormData),
      });

      if (response.ok) {
        setSubmitSuccess(true);
        setTimeout(() => {
          setRequestDialogOpen(false);
          setSubmitSuccess(false);
          setSelectedService(null);
        }, 2000);
      }
    } catch (error) {
      console.error('Error submitting request:', error);
    }
  };

  const handleFormDataChange = (field: string, value: any) => {
    setRequestFormData(prev => ({
      ...prev,
      form_data: {
        ...prev.form_data,
        [field]: value,
      },
    }));
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
        Browse Service Catalog
      </Typography>

      {/* Search and Filter */}
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              placeholder="Search services..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={selectedCategory}
                label="Category"
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                {categories.map((cat) => (
                  <MenuItem key={cat} value={cat}>
                    {cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      {/* Category Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs
          value={selectedCategory}
          onChange={(e, newValue) => setSelectedCategory(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          {categories.map((cat) => (
            <Tab
              key={cat}
              label={cat.charAt(0).toUpperCase() + cat.slice(1)}
              value={cat}
            />
          ))}
        </Tabs>
      </Box>

      {/* Services Grid */}
      <Grid container spacing={3}>
        {filteredServices.length > 0 ? (
          filteredServices.map((service) => (
            <Grid item xs={12} sm={6} md={4} key={service.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Category color="primary" sx={{ mr: 1 }} />
                    <Chip
                      label={service.category.toUpperCase()}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </Box>
                  
                  <Typography variant="h6" gutterBottom>
                    {service.name}
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {service.description}
                  </Typography>

                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <AttachMoney fontSize="small" color="action" />
                    <Typography variant="body2" color="text.secondary">
                      ${service.price.toFixed(2)}
                    </Typography>
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Schedule fontSize="small" color="action" />
                    <Typography variant="body2" color="text.secondary" sx={{ ml: 0.5 }}>
                      Est. {service.estimated_delivery_hours} hours
                    </Typography>
                  </Box>

                  {service.requires_approval && (
                    <Chip
                      label="Requires Approval"
                      size="small"
                      color="warning"
                      variant="outlined"
                      sx={{ mt: 1 }}
                    />
                  )}
                </CardContent>

                <CardActions>
                  <Button
                    fullWidth
                    variant="contained"
                    startIcon={<ShoppingCart />}
                    onClick={() => handleRequestService(service)}
                  >
                    Request Service
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))
        ) : (
          <Grid item xs={12}>
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <Info sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                No services found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Try adjusting your search or filter criteria
              </Typography>
            </Box>
          </Grid>
        )}
      </Grid>

      {/* Request Dialog */}
      <Dialog
        open={requestDialogOpen}
        onClose={() => setRequestDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Request Service: {selectedService?.name}
        </DialogTitle>
        <DialogContent>
          {submitSuccess ? (
            <Alert severity="success" sx={{ mt: 2 }}>
              Request submitted successfully! Redirecting...
            </Alert>
          ) : (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Priority</InputLabel>
                    <Select
                      value={requestFormData.priority}
                      label="Priority"
                      onChange={(e) =>
                        setRequestFormData({ ...requestFormData, priority: e.target.value })
                      }
                    >
                      <MenuItem value="low">Low</MenuItem>
                      <MenuItem value="medium">Medium</MenuItem>
                      <MenuItem value="high">High</MenuItem>
                      <MenuItem value="critical">Critical</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Cost Center"
                    value={requestFormData.cost_center}
                    onChange={(e) =>
                      setRequestFormData({ ...requestFormData, cost_center: e.target.value })
                    }
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    label="Business Justification"
                    value={requestFormData.business_justification}
                    onChange={(e) =>
                      setRequestFormData({
                        ...requestFormData,
                        business_justification: e.target.value,
                      })
                    }
                    required
                  />
                </Grid>

                {/* Dynamic form fields based on service form_schema */}
                {selectedService?.form_schema?.fields?.map((field: any) => (
                  <Grid item xs={12} key={field.name}>
                    <TextField
                      fullWidth
                      label={field.label}
                      type={field.type}
                      required={field.required}
                      value={requestFormData.form_data[field.name] || ''}
                      onChange={(e) => handleFormDataChange(field.name, e.target.value)}
                      helperText={field.description}
                    />
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRequestDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSubmitRequest}
            disabled={!requestFormData.business_justification || submitSuccess}
          >
            Submit Request
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ServiceCatalogBrowse;