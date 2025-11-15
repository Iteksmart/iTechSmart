import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  AppBar,
  Toolbar,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Chip,
  Avatar,
  IconButton,
  Badge,
  Divider,
  Container
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Security as SecurityIcon,
  Cloud as CloudIcon,
  Storage as StorageIcon,
  Analytics as AnalyticsIcon,
  Api as ApiIcon,
  Lock as LockIcon,
  Notifications as NotificationsIcon,
  AccountTree as AccountTreeIcon,
  SmartToy as SmartToyIcon,
  Store as StoreIcon,
  PhoneAndroid as PhoneAndroidIcon,
  Code as CodeIcon,
  Assessment as AssessmentIcon,
  People as PeopleIcon,
  LocalHospital as LocalHospitalIcon,
  FitnessCenter as FitnessCenterIcon,
  VerifiedUser as VerifiedUserIcon,
  TrendingUp as TrendingUpIcon,
  Menu as MenuIcon,
  Settings as SettingsIcon,
  ExitToApp as ExitToAppIcon
} from '@mui/icons-material';

interface Product {
  id: string;
  name: string;
  description: string;
  icon: React.ReactElement;
  status: 'active' | 'inactive';
  url: string;
  category: string;
}

const UnifiedDashboard: React.FC = () => {
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [products, setProducts] = useState<Product[]>([
    // Foundation Products
    { id: 'enterprise', name: 'Enterprise Hub', description: 'Central integration platform', icon: <DashboardIcon />, status: 'active', url: '/enterprise', category: 'foundation' },
    { id: 'ninja', name: 'Ninja', description: 'Self-healing AI agent', icon: <SmartToyIcon />, status: 'active', url: '/ninja', category: 'foundation' },
    { id: 'analytics', name: 'Analytics', description: 'ML-powered analytics', icon: <AnalyticsIcon />, status: 'active', url: '/analytics', category: 'foundation' },
    { id: 'supreme', name: 'Supreme', description: 'Healthcare management', icon: <LocalHospitalIcon />, status: 'active', url: '/supreme', category: 'foundation' },
    { id: 'hl7', name: 'HL7', description: 'Medical data integration', icon: <LocalHospitalIcon />, status: 'active', url: '/hl7', category: 'foundation' },
    { id: 'prooflink', name: 'ProofLink.AI', description: 'Document verification', icon: <VerifiedUserIcon />, status: 'active', url: '/prooflink', category: 'foundation' },
    { id: 'passport', name: 'PassPort', description: 'Identity management', icon: <LockIcon />, status: 'active', url: '/passport', category: 'foundation' },
    { id: 'impactos', name: 'ImpactOS', description: 'Impact measurement', icon: <TrendingUpIcon />, status: 'active', url: '/impactos', category: 'foundation' },
    { id: 'fitsnap', name: 'FitSnap.AI', description: 'Fitness tracking', icon: <FitnessCenterIcon />, status: 'active', url: '/fitsnap', category: 'foundation' },
    
    // Strategic Products
    { id: 'dataflow', name: 'DataFlow', description: 'Data pipeline & ETL', icon: <StorageIcon />, status: 'active', url: '/dataflow', category: 'strategic' },
    { id: 'shield', name: 'Shield', description: 'Cybersecurity platform', icon: <SecurityIcon />, status: 'active', url: '/shield', category: 'strategic' },
    { id: 'pulse', name: 'Pulse', description: 'Real-time analytics', icon: <AssessmentIcon />, status: 'active', url: '/pulse', category: 'strategic' },
    { id: 'connect', name: 'Connect', description: 'API management', icon: <ApiIcon />, status: 'active', url: '/connect', category: 'strategic' },
    { id: 'workflow', name: 'Workflow', description: 'Business automation', icon: <AccountTreeIcon />, status: 'active', url: '/workflow', category: 'strategic' },
    { id: 'vault', name: 'Vault', description: 'Secrets management', icon: <LockIcon />, status: 'active', url: '/vault', category: 'strategic' },
    { id: 'notify', name: 'Notify', description: 'Omnichannel notifications', icon: <NotificationsIcon />, status: 'active', url: '/notify', category: 'strategic' },
    { id: 'ledger', name: 'Ledger', description: 'Blockchain & audit', icon: <VerifiedUserIcon />, status: 'active', url: '/ledger', category: 'strategic' },
    { id: 'copilot', name: 'Copilot', description: 'AI assistant', icon: <SmartToyIcon />, status: 'active', url: '/copilot', category: 'strategic' },
    { id: 'marketplace', name: 'Marketplace', description: 'App store', icon: <StoreIcon />, status: 'active', url: '/marketplace', category: 'strategic' },
    
    // Business Products
    { id: 'mobile', name: 'Mobile', description: 'Mobile platform', icon: <PhoneAndroidIcon />, status: 'active', url: '/mobile', category: 'business' },
    { id: 'cloud', name: 'Cloud', description: 'Multi-cloud management', icon: <CloudIcon />, status: 'active', url: '/cloud', category: 'business' },
    { id: 'ai', name: 'AI Platform', description: 'AI/ML platform', icon: <SmartToyIcon />, status: 'active', url: '/ai', category: 'business' },
    { id: 'compliance', name: 'Compliance', description: 'Regulatory compliance', icon: <VerifiedUserIcon />, status: 'active', url: '/compliance', category: 'business' },
    { id: 'devops', name: 'DevOps', description: 'CI/CD automation', icon: <CodeIcon />, status: 'active', url: '/devops', category: 'business' },
    { id: 'customer-success', name: 'Customer Success', description: 'Customer platform', icon: <PeopleIcon />, status: 'active', url: '/customer-success', category: 'business' },
    { id: 'data-platform', name: 'Data Platform', description: 'Data governance', icon: <StorageIcon />, status: 'active', url: '/data-platform', category: 'business' }
  ]);

  const categories = [
    { id: 'all', name: 'All Products', count: products.length },
    { id: 'foundation', name: 'Foundation', count: products.filter(p => p.category === 'foundation').length },
    { id: 'strategic', name: 'Strategic', count: products.filter(p => p.category === 'strategic').length },
    { id: 'business', name: 'Business', count: products.filter(p => p.category === 'business').length }
  ];

  const filteredProducts = selectedCategory === 'all' 
    ? products 
    : products.filter(p => p.category === selectedCategory);

  const handleProductClick = (product: Product) => {
    window.location.href = product.url;
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      {/* App Bar */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setDrawerOpen(!drawerOpen)}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            iTechSmart Enterprise Suite
          </Typography>
          <IconButton color="inherit">
            <Badge badgeContent={4} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>
          <IconButton color="inherit">
            <SettingsIcon />
          </IconButton>
          <IconButton color="inherit">
            <ExitToAppIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Drawer
        variant="persistent"
        open={drawerOpen}
        sx={{
          width: 280,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: 280,
            boxSizing: 'border-box',
            mt: 8
          }
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Categories
          </Typography>
          <List>
            {categories.map((category) => (
              <ListItemButton
                key={category.id}
                selected={selectedCategory === category.id}
                onClick={() => setSelectedCategory(category.id)}
                sx={{ borderRadius: 1, mb: 1 }}
              >
                <ListItemText 
                  primary={category.name}
                  secondary={`${category.count} products`}
                />
              </ListItemButton>
            ))}
          </List>
          
          <Divider sx={{ my: 2 }} />
          
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            System Status
          </Typography>
          <Box sx={{ mt: 1 }}>
            <Chip label="All Systems Operational" color="success" size="small" sx={{ mb: 1 }} />
            <Typography variant="caption" display="block" color="text.secondary">
              26/26 Products Active
            </Typography>
          </Box>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          ml: drawerOpen ? 0 : -35
        }}
      >
        <Container maxWidth="xl">
          {/* Header */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h4" gutterBottom>
              Welcome to iTechSmart Suite
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Access all 26 integrated products from one unified dashboard
            </Typography>
          </Box>

          {/* Stats Cards */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Products
                  </Typography>
                  <Typography variant="h3">26</Typography>
                  <Chip label="100% Active" color="success" size="small" sx={{ mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Active Users
                  </Typography>
                  <Typography variant="h3">1.2K</Typography>
                  <Typography variant="body2" color="success.main">
                    +12% this week
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    API Calls Today
                  </Typography>
                  <Typography variant="h3">45K</Typography>
                  <Typography variant="body2" color="info.main">
                    Avg: 1.8K/hour
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    System Health
                  </Typography>
                  <Typography variant="h3">99.9%</Typography>
                  <Typography variant="body2" color="success.main">
                    All systems operational
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Products Grid */}
          <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
            {selectedCategory === 'all' ? 'All Products' : categories.find(c => c.id === selectedCategory)?.name}
          </Typography>
          
          <Grid container spacing={3}>
            {filteredProducts.map((product) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
                <Card 
                  sx={{ 
                    height: '100%',
                    cursor: 'pointer',
                    transition: 'all 0.3s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 4
                    }
                  }}
                  onClick={() => handleProductClick(product)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                        {product.icon}
                      </Avatar>
                      <Box>
                        <Typography variant="h6" component="div">
                          {product.name}
                        </Typography>
                        <Chip 
                          label={product.status} 
                          color={product.status === 'active' ? 'success' : 'default'}
                          size="small"
                        />
                      </Box>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {product.description}
                    </Typography>
                    <Button 
                      variant="outlined" 
                      fullWidth 
                      sx={{ mt: 2 }}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleProductClick(product);
                      }}
                    >
                      Open Dashboard
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>
    </Box>
  );
};

export default UnifiedDashboard;