import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  TextField,
  InputAdornment,
  Tab,
  Tabs,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Search as SearchIcon,
  Lock as LockIcon,
  Computer as ComputerIcon,
  Storage as StorageIcon,
  Build as BuildIcon,
  Settings as SettingsIcon,
  Inventory as InventoryIcon,
  Receipt as ReceiptIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface ServiceItem {
  id: number;
  name: string;
  description: string;
  category: string;
  icon: string;
  sla_hours: number;
  requires_approval: boolean;
  automation_enabled: boolean;
  ai_assisted: boolean;
}

const categoryIcons: { [key: string]: React.ReactNode } = {
  access_management: <LockIcon />,
  it_support: <ComputerIcon />,
  systems_servers: <StorageIcon />,
  devops_automation: <BuildIcon />,
  network_requests: <SettingsIcon />,
  software_deployment: <InventoryIcon />,
  hardware_requests: <ReceiptIcon />,
  hr_onboarding: <PersonIcon />
};

const categoryColors: { [key: string]: string } = {
  access_management: '#1976d2',
  it_support: '#2e7d32',
  systems_servers: '#ed6c02',
  devops_automation: '#9c27b0',
  network_requests: '#d32f2f',
  software_deployment: '#0288d1',
  hardware_requests: '#f57c00',
  hr_onboarding: '#7b1fa2'
};

const CatalogHome: React.FC = () => {
  const navigate = useNavigate();
  const [categories, setCategories] = useState<any[]>([]);
  const [serviceItems, setServiceItems] = useState<ServiceItem[]>([]);
  const [filteredItems, setFilteredItems] = useState<ServiceItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    filterItems();
  }, [selectedCategory, searchQuery, serviceItems]);

  const loadData = async () => {
    try {
      // Load categories
      const categoriesRes = await fetch('/api/service-catalog/categories');
      const categoriesData = await categoriesRes.json();
      setCategories(categoriesData.categories);

      // Load service items
      const itemsRes = await fetch('/api/service-catalog/items');
      const itemsData = await itemsRes.json();
      setServiceItems(itemsData);
      setFilteredItems(itemsData);
      
      setLoading(false);
    } catch (error) {
      console.error('Error loading data:', error);
      setLoading(false);
    }
  };

  const filterItems = () => {
    let filtered = serviceItems;

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(item => item.category === selectedCategory);
    }

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(item =>
        item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setFilteredItems(filtered);
  };

  const handleRequestService = (serviceId: number) => {
    navigate(`/service-catalog/request/${serviceId}`);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h3" gutterBottom fontWeight="bold" color="primary">
          🛍️ Service Catalog
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Self-Service Portal - Request IT services with automated fulfillment
        </Typography>
        
        <Alert severity="info" sx={{ mt: 2 }}>
          <strong>AI-Powered Automation:</strong> Most requests are fulfilled automatically with AI assistance. 
          Average fulfillment time: <strong>15 minutes</strong>
        </Alert>
      </Box>

      {/* Search Bar */}
      <Box mb={4}>
        <TextField
          fullWidth
          placeholder="Search services..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              backgroundColor: 'white',
              borderRadius: 2
            }
          }}
        />
      </Box>

      {/* Category Tabs */}
      <Box mb={4}>
        <Tabs
          value={selectedCategory}
          onChange={(e, newValue) => setSelectedCategory(newValue)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            backgroundColor: 'white',
            borderRadius: 2,
            '& .MuiTab-root': {
              minHeight: 64,
              fontSize: '1rem'
            }
          }}
        >
          <Tab label="All Services" value="all" />
          {categories.map((category) => (
            <Tab
              key={category.id}
              label={category.name}
              value={category.id}
            />
          ))}
        </Tabs>
      </Box>

      {/* Service Cards */}
      <Grid container spacing={3}>
        {filteredItems.map((item) => (
          <Grid item xs={12} sm={6} md={4} key={item.id}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: 6
                },
                borderTop: `4px solid ${categoryColors[item.category] || '#1976d2'}`
              }}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                {/* Icon and Title */}
                <Box display="flex" alignItems="center" mb={2}>
                  <Box
                    sx={{
                      width: 56,
                      height: 56,
                      borderRadius: 2,
                      backgroundColor: `${categoryColors[item.category]}20`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '2rem',
                      mr: 2
                    }}
                  >
                    {item.icon}
                  </Box>
                  <Typography variant="h6" fontWeight="bold">
                    {item.name}
                  </Typography>
                </Box>

                {/* Description */}
                <Typography variant="body2" color="text.secondary" mb={2}>
                  {item.description}
                </Typography>

                {/* Tags */}
                <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
                  {item.automation_enabled && (
                    <Chip
                      label="⚡ Auto-Fulfill"
                      size="small"
                      color="success"
                      variant="outlined"
                    />
                  )}
                  {item.ai_assisted && (
                    <Chip
                      label="🤖 AI-Assisted"
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  )}
                  {item.requires_approval && (
                    <Chip
                      label="✓ Approval Required"
                      size="small"
                      color="warning"
                      variant="outlined"
                    />
                  )}
                </Box>

                {/* SLA */}
                <Typography variant="caption" color="text.secondary">
                  ⏱️ SLA: {item.sla_hours} hours
                </Typography>
              </CardContent>

              <CardActions sx={{ p: 2, pt: 0 }}>
                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  onClick={() => handleRequestService(item.id)}
                  sx={{
                    backgroundColor: categoryColors[item.category] || '#1976d2',
                    '&:hover': {
                      backgroundColor: categoryColors[item.category] || '#1565c0'
                    }
                  }}
                >
                  Request Service →
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* No Results */}
      {filteredItems.length === 0 && (
        <Box textAlign="center" py={8}>
          <Typography variant="h6" color="text.secondary">
            No services found matching your criteria
          </Typography>
          <Button
            variant="outlined"
            onClick={() => {
              setSearchQuery('');
              setSelectedCategory('all');
            }}
            sx={{ mt: 2 }}
          >
            Clear Filters
          </Button>
        </Box>
      )}

      {/* Quick Stats */}
      <Box mt={6} p={3} sx={{ backgroundColor: 'white', borderRadius: 2 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="primary" fontWeight="bold">
                {serviceItems.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Available Services
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="success.main" fontWeight="bold">
                {serviceItems.filter(i => i.automation_enabled).length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Auto-Fulfilled
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="info.main" fontWeight="bold">
                {serviceItems.filter(i => i.ai_assisted).length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                AI-Assisted
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="warning.main" fontWeight="bold">
                15 min
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Avg. Fulfillment Time
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default CatalogHome;