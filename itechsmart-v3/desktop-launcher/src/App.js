import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Avatar,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Badge,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  TextField,
  InputAdornment,
  Alert,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Settings,
  Notifications,
  Search,
  Dashboard,
  Security,
  AttachMoney,
  Code,
  People,
  School,
  Cloud,
  SmartToy,
  Menu as MenuIcon,
  Launch,
  Update,
  Speed,
  Assessment,
  Build,
  Lock,
  Timeline,
  TrendingUp,
  Refresh,
  PowerSettingsNew,
  Info,
  CheckCircle,
  Warning,
  Error,
} from '@mui/icons-material';
import { io } from 'socket.io-client';

const iTechSmartDesktopLauncher = () => {
  const [products, setProducts] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [notifications, setNotifications] = useState([]);
  const [systemStatus, setSystemStatus] = useState({});
  const [neuralHubConnected, setNeuralHubConnected] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [socket, setSocket] = useState(null);

  // iTechSmart Suite Products - All 45+ Products
  const allProducts = [
    // AI & Automation
    { id: 'ninja', name: 'iTechSmart Ninja', category: 'ai-automation', icon: <SmartToy />, status: 'running', port: 3002, description: 'AI-powered personal assistant' },
    { id: 'supreme', name: 'iTechSmart Supreme', category: 'ai-automation', icon: <TrendingUp />, status: 'running', port: 3003, description: 'Autonomous infrastructure management' },
    { id: 'arbiter', name: 'iTechSmart Arbiter', category: 'ai-automation', icon: <Lock />, status: 'running', port: 3004, description: 'AI governance and safety' },
    { id: 'digital-twin', name: 'iTechSmart Digital Twin', category: 'ai-automation', icon: <Cloud />, status: 'running', port: 3005, description: 'Predictive simulation engine' },
    { id: 'generative-workflow', name: 'iTechSmart Generative Workflow', category: 'ai-automation', icon: <Timeline />, status: 'running', port: 3006, description: 'Text-to-workflow automation' },
    
    // Enhanced Products v2.0
    { id: 'customer-data-platform', name: 'Customer Data Platform v2.0', category: 'ai-automation', icon: <People />, status: 'running', port: 3010, description: 'Real-time CDP with AI orchestration' },
    { id: 'iot-fleet-management', name: 'IoT Fleet Management v2.0', category: 'ai-automation', icon: <Cloud />, status: 'running', port: 3011, description: 'Geospatial fleet management' },
    { id: 'portal-builder', name: 'Portal Builder v2.0', category: 'ai-automation', icon: <Dashboard />, status: 'running', port: 3012, description: 'No-code portal development' },

    // Security & Compliance
    { id: 'citadel', name: 'iTechSmart Citadel', category: 'security', icon: <Security />, status: 'running', port: 3020, description: 'Enterprise security platform' },
    { id: 'shield', name: 'iTechSmart Shield', category: 'security', icon: <Lock />, status: 'running', port: 3021, description: 'Threat detection & response' },
    { id: 'sentinel', name: 'iTechSmart Sentinel', category: 'security', icon: <Assessment />, status: 'running', port: 3022, description: 'Security monitoring' },
    { id: 'vault', name: 'iTechSmart Vault', category: 'security', icon: <Security />, status: 'running', port: 3023, description: 'Secrets management' },
    { id: 'compliance', name: 'iTechSmart Compliance', category: 'security', icon: <CheckCircle />, status: 'running', port: 3024, description: 'Compliance automation' },

    // Monitoring & Analytics
    { id: 'analytics', name: 'iTechSmart Analytics', category: 'monitoring', icon: <Assessment />, status: 'running', port: 3030, description: 'Business intelligence platform' },
    { id: 'observatory', name: 'iTechSmart Observatory', category: 'monitoring', icon: <Dashboard />, status: 'running', port: 3031, description: 'Infrastructure monitoring' },
    { id: 'pulse', name: 'iTechSmart Pulse', category: 'monitoring', icon: <Speed />, status: 'running', port: 3032, description: 'Real-time system health' },
    { id: 'business-value', name: 'Business Value Dashboard', category: 'monitoring', icon: <AttachMoney />, status: 'running', port: 3033, description: 'FinOps analytics platform' },
    { id: 'knowledge-graph', name: 'iTechSmart Knowledge Graph', category: 'monitoring', icon: <Timeline />, status: 'running', port: 3034, description: 'Semantic relationship mapping' },

    // Enterprise Management
    { id: 'enterprise', name: 'iTechSmart Enterprise', category: 'enterprise', icon: <Dashboard />, status: 'running', port: 3040, description: 'Enterprise management platform' },
    { id: 'supreme-plus', name: 'iTechSmart Supreme Plus', category: 'enterprise', icon: <TrendingUp />, status: 'running', port: 3041, description: 'Premium enterprise features' },
    { id: 'connect', name: 'iTechSmart Connect', category: 'enterprise', icon: <Cloud />, status: 'running', port: 3042, description: 'Integration platform' },
    { id: 'workflow', name: 'iTechSmart Workflow', category: 'enterprise', icon: <Timeline />, status: 'running', port: 3043, description: 'Visual workflow designer' },
    { id: 'devops', name: 'iTechSmart DevOps', category: 'enterprise', icon: <Code />, status: 'running', port: 3044, description: 'DevOps automation' },
    { id: 'uaio-certification', name: 'UAIO Architect Certification', category: 'enterprise', icon: <School />, status: 'running', port: 3045, description: 'Professional certification program' },

    // Development & Integration
    { id: 'gateway', name: 'iTechSmart Gateway', category: 'development', icon: <Cloud />, status: 'running', port: 3050, description: 'Unified API gateway' },
    { id: 'cloud', name: 'iTechSmart Cloud', category: 'development', icon: <Cloud />, status: 'running', port: 3051, description: 'Cloud management platform' },
    { id: 'dataflow', name: 'iTechSmart Dataflow', category: 'development', icon: <Timeline />, status: 'running', port: 3052, description: 'Data pipeline management' },
    { id: 'forge', name: 'iTechSmart Forge', category: 'development', icon: <Build />, status: 'running', port: 3053, description: 'Development platform' },

    // Infrastructure
    { id: 'sandbox', name: 'iTechSmart Sandbox', category: 'infrastructure', icon: <Cloud />, status: 'running', port: 3060, description: 'Development environment' },
    { id: 'edge-computing', name: 'iTechSmart Edge Computing', category: 'infrastructure', icon: <Cloud />, status: 'running', port: 3061, description: 'Global edge infrastructure' },
    { id: 'ai-infrastructure', name: 'iTechSmart AI Infrastructure', category: 'infrastructure', icon: <SmartToy />, status: 'running', port: 3062, description: 'AI-native infrastructure' },
    { id: 'ai-governance', name: 'iTechSmart AI Governance', category: 'infrastructure', icon: <Lock />, status: 'running', port: 3063, description: 'Enterprise AI governance' },

    // New v3.0 Products
    { id: 'neural-hub', name: 'iTechSmart Neural Hub', category: 'infrastructure', icon: <Dashboard />, status: 'running', port: 8080, description: 'Central orchestration system' },
    { id: 'unified-dashboard', name: 'Unified Dashboard', category: 'infrastructure', icon: <Dashboard />, status: 'running', port: 3000, description: 'Single pane of glass' },
    { id: 'community', name: 'Community Portal', category: 'enterprise', icon: <People />, status: 'running', port: 3001, description: 'UAIO certification platform' },
  ];

  const categoryColors = {
    'ai-automation': '#667eea',
    'security': '#dc3545',
    'monitoring': '#28a745',
    'enterprise': '#ffc107',
    'development': '#17a2b8',
    'infrastructure': '#764ba2',
  };

  useEffect(() => {
    initializeLauncher();
    connectToNeuralHub();
    
    // Simulate periodic status updates
    const statusInterval = setInterval(() => {
      updateProductStatuses();
    }, 30000);

    return () => {
      clearInterval(statusInterval);
      if (socket) {
        socket.disconnect();
      }
    };
  }, []);

  const initializeLauncher = () => {
    setProducts(allProducts);
    setSystemStatus({
      cpu: Math.floor(Math.random() * 30 + 20),
      memory: Math.floor(Math.random() * 40 + 30),
      disk: Math.floor(Math.random() * 20 + 40),
      network: Math.floor(Math.random() * 25 + 15),
    });
  };

  const connectToNeuralHub = () => {
    try {
      const newSocket = io('http://localhost:8080');
      
      newSocket.on('connect', () => {
        setNeuralHubConnected(true);
        setConnectionStatus('connected');
        addNotification({
          type: 'success',
          title: 'Connected to Neural Hub',
          message: 'Real-time orchestration enabled',
          timestamp: new Date(),
        });
      });

      newSocket.on('disconnect', () => {
        setNeuralHubConnected(false);
        setConnectionStatus('disconnected');
        addNotification({
          type: 'warning',
          title: 'Disconnected from Neural Hub',
          message: 'Real-time features unavailable',
          timestamp: new Date(),
        });
      });

      newSocket.on('neural-event', (event) => {
        handleNeuralEvent(event);
      });

      newSocket.on('product-status-update', (data) => {
        updateProductStatus(data.productId, data.status);
      });

      setSocket(newSocket);
    } catch (error) {
      setConnectionStatus('error');
      console.error('Failed to connect to Neural Hub:', error);
    }
  };

  const handleNeuralEvent = (event) => {
    addNotification({
      type: event.type === 'SECURITY_THREAT' ? 'error' : 'info',
      title: event.type,
      message: event.description,
      timestamp: new Date(),
      actions: event.actions || []
    });
  };

  const updateProductStatuses = () => {
    // Simulate random status changes
    setProducts(prev => prev.map(product => {
      const rand = Math.random();
      let status = product.status;
      
      if (rand < 0.05) status = 'starting';
      else if (rand < 0.1) status = 'stopping';
      else if (rand < 0.15) status = 'error';
      else status = 'running';
      
      return { ...product, status };
    }));
  };

  const updateProductStatus = (productId, status) => {
    setProducts(prev => prev.map(product => 
      product.id === productId ? { ...product, status } : product
    ));
  };

  const addNotification = (notification) => {
    setNotifications(prev => [notification, ...prev].slice(0, 50));
  };

  const launchProduct = (product) => {
    setSelectedProduct(product);
    
    // Launch in browser
    const url = `http://localhost:${product.port}`;
    window.open(url, '_blank');
    
    addNotification({
      type: 'info',
      title: 'Product Launched',
      message: `${product.name} opened in browser`,
      timestamp: new Date(),
    });

    // Update status
    updateProductStatus(product.id, 'running');
  };

  const startProduct = async (product) => {
    updateProductStatus(product.id, 'starting');
    
    // Simulate product startup
    setTimeout(() => {
      updateProductStatus(product.id, 'running');
      launchProduct(product);
    }, 2000);
  };

  const stopProduct = (product) => {
    updateProductStatus(product.id, 'stopping');
    
    setTimeout(() => {
      updateProductStatus(product.id, 'stopped');
      addNotification({
        type: 'info',
        title: 'Product Stopped',
        message: `${product.name} has been stopped`,
        timestamp: new Date(),
      });
    }, 1500);
  };

  const restartProduct = (product) => {
    stopProduct(product);
    setTimeout(() => startProduct(product), 2000);
  };

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    product.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'success';
      case 'starting': return 'warning';
      case 'stopping': return 'warning';
      case 'error': return 'error';
      case 'stopped': return 'default';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running': return <CheckCircle />;
      case 'starting': return <Refresh />;
      case 'stopping': return <Refresh />;
      case 'error': return <Error />;
      case 'stopped': return <PowerSettingsNew />;
      default: return <Info />;
    }
  };

  const ProductCard = ({ product }) => (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flex: 1 }}>
        <Box display="flex" alignItems="center" mb={2}>
          <Avatar sx={{ bgcolor: categoryColors[product.category], mr: 2 }}>
            {product.icon}
          </Avatar>
          <Box flex={1}>
            <Typography variant="h6" noWrap>
              {product.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {product.category.replace('-', ' ')}
            </Typography>
          </Box>
          <Chip
            icon={getStatusIcon(product.status)}
            label={product.status}
            color={getStatusColor(product.status)}
            size="small"
          />
        </Box>
        
        <Typography variant="body2" color="text.secondary" mb={2}>
          {product.description}
        </Typography>
        
        <Box display="flex" alignItems="center" mb={2}>
          <Typography variant="caption" color="text.secondary">
            Port: {product.port}
          </Typography>
        </Box>
      </CardContent>
      
      <CardActions>
        <Button
          size="small"
          variant="contained"
          startIcon={<Launch />}
          onClick={() => launchProduct(product)}
          disabled={product.status !== 'running'}
        >
          Launch
        </Button>
        {product.status === 'running' ? (
          <Button size="small" onClick={() => stopProduct(product)}>
            Stop
          </Button>
        ) : (
          <Button size="small" onClick={() => startProduct(product)}>
            Start
          </Button>
        )}
        <IconButton size="small" onClick={() => restartProduct(product)}>
          <Refresh />
        </IconButton>
      </CardActions>
    </Card>
  );

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* AppBar */}
      <AppBar position="static" sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => setDrawerOpen(true)}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            🚀 iTechSmart Suite v3.0
          </Typography>
          
          <Box display="flex" alignItems="center" gap={1}>
            {/* Connection Status */}
            <Chip
              icon={neuralHubConnected ? <CheckCircle /> : <Error />}
              label={connectionStatus}
              color={neuralHubConnected ? 'success' : 'error'}
              size="small"
            />
            
            {/* Update Indicator */}
            {updateAvailable && (
              <IconButton color="inherit">
                <Badge badgeContent={1} color="error">
                  <Update />
                </Badge>
              </IconButton>
            )}
            
            {/* Notifications */}
            <IconButton color="inherit" onClick={(e) => setMenuAnchor(e.currentTarget)}>
              <Badge badgeContent={notifications.length} color="error">
                <Notifications />
              </Badge>
            </IconButton>
            
            {/* Settings */}
            <IconButton color="inherit">
              <Settings />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      {/* System Status Bar */}
      <Box sx={{ background: '#f5f5f5', p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Grid container spacing={2}>
          <Grid item xs={3}>
            <Box display="flex" alignItems="center">
              <Speed sx={{ mr: 1, color: '#667eea' }} />
              <Box flex={1}>
                <Typography variant="caption" color="text.secondary">CPU</Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={systemStatus.cpu} 
                  sx={{ height: 4, borderRadius: 2 }}
                />
                <Typography variant="caption">{systemStatus.cpu}%</Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box display="flex" alignItems="center">
              <Assessment sx={{ mr: 1, color: '#28a745' }} />
              <Box flex={1}>
                <Typography variant="caption" color="text.secondary">Memory</Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={systemStatus.memory} 
                  sx={{ height: 4, borderRadius: 2 }}
                />
                <Typography variant="caption">{systemStatus.memory}%</Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box display="flex" alignItems="center">
              <Cloud sx={{ mr: 1, color: '#ffc107' }} />
              <Box flex={1}>
                <Typography variant="caption" color="text.secondary">Disk</Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={systemStatus.disk} 
                  sx={{ height: 4, borderRadius: 2 }}
                />
                <Typography variant="caption">{systemStatus.disk}%</Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box display="flex" alignItems="center">
              <Timeline sx={{ mr: 1, color: '#764ba2' }} />
              <Box flex={1}>
                <Typography variant="caption" color="text.secondary">Network</Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={systemStatus.network} 
                  sx={{ height: 4, borderRadius: 2 }}
                />
                <Typography variant="caption">{systemStatus.network}%</Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Box>

      {/* Main Content */}
      <Box sx={{ flex: 1, p: 3, overflow: 'auto' }}>
        {/* Search Bar */}
        <TextField
          fullWidth
          placeholder="Search iTechSmart products..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
          sx={{ mb: 3 }}
        />

        {/* Products Grid */}
        <Grid container spacing={3}>
          {filteredProducts.map((product) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
              <ProductCard product={product} />
            </Grid>
          ))}
        </Grid>

        {/* Neural Hub Status */}
        {!neuralHubConnected && (
          <Alert severity="warning" sx={{ mt: 3 }}>
            <Typography variant="h6">Neural Hub Disconnected</Typography>
            <Typography variant="body2">
              Real-time orchestration and cross-product communication are unavailable. 
              Please check if the Neural Hub service is running.
            </Typography>
            <Button variant="outlined" sx={{ mt: 1 }} onClick={connectToNeuralHub}>
              Reconnect
            </Button>
          </Alert>
        )}
      </Box>

      {/* Navigation Drawer */}
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Box sx={{ width: 300, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            iTechSmart Suite
          </Typography>
          <Divider sx={{ mb: 2 }} />
          
          <List>
            <ListItem button onClick={() => window.open('http://localhost:3000', '_blank')}>
              <ListItemIcon><Dashboard /></ListItemIcon>
              <ListItemText primary="Unified Dashboard" />
            </ListItem>
            <ListItem button onClick={() => window.open('http://localhost:3001', '_blank')}>
              <ListItemIcon><People /></ListItemIcon>
              <ListItemText primary="Community Portal" />
            </ListItem>
            <ListItem button onClick={() => window.open('http://localhost:8080/health', '_blank')}>
              <ListItemIcon><Settings /></ListItemIcon>
              <ListItemText primary="Neural Hub Status" />
            </ListItem>
            <ListItem button onClick={() => window.open('http://localhost:3100', '_blank')}>
              <ListItemIcon><Assessment /></ListItemIcon>
              <ListItemText primary="Grafana Metrics" />
            </ListItem>
            <ListItem button onClick={() => window.open('http://localhost:5601', '_blank')}>
              <ListItemIcon><Timeline /></ListItemIcon>
              <ListItemText primary="Kibana Logs" />
            </ListItem>
          </List>
        </Box>
      </Drawer>

      {/* Notifications Menu */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={() => setMenuAnchor(null)}
        PaperProps={{ sx: { maxHeight: 400, width: 350 } }}
      >
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6">Notifications</Typography>
        </Box>
        {notifications.length === 0 ? (
          <MenuItem disabled>No notifications</MenuItem>
        ) : (
          notifications.slice(0, 10).map((notification, index) => (
            <MenuItem key={index} onClick={() => setMenuAnchor(null)}>
              <Box>
                <Typography variant="body2" fontWeight="medium">
                  {notification.title}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {notification.message}
                </Typography>
              </Box>
            </MenuItem>
          ))
        )}
      </Menu>

      {/* Product Details Dialog */}
      <Dialog open={Boolean(selectedProduct)} onClose={() => setSelectedProduct(null)}>
        <DialogTitle>
          {selectedProduct?.name}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" gutterBottom>
            {selectedProduct?.description}
          </Typography>
          <Box mt={2}>
            <Typography variant="subtitle2">Details:</Typography>
            <Typography variant="body2">
              Category: {selectedProduct?.category}<br/>
              Port: {selectedProduct?.port}<br/>
              Status: {selectedProduct?.status}<br/>
              URL: http://localhost:{selectedProduct?.port}
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedProduct(null)}>Close</Button>
          <Button 
            variant="contained" 
            onClick={() => {
              if (selectedProduct) launchProduct(selectedProduct);
              setSelectedProduct(null);
            }}
          >
            Launch
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default iTechSmartDesktopLauncher;