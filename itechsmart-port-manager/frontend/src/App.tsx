import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  CssBaseline,
  ThemeProvider,
  createTheme,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Badge,
  Chip,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Settings as SettingsIcon,
  Storage as StorageIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Refresh as RefreshIcon,
  Backup as BackupIcon,
  RestartAlt as RestartAltIcon
} from '@mui/icons-material';

import Dashboard from './components/Dashboard';
import PortManagement from './components/PortManagement';
import ServiceStatus from './components/ServiceStatus';
import ConflictResolution from './components/ConflictResolution';
import Configuration from './components/Configuration';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#667eea',
    },
    secondary: {
      main: '#764ba2',
    },
    success: {
      main: '#38ef7d',
    },
    error: {
      main: '#fa709a',
    },
  },
});

function App() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard');
  const [conflicts, setConflicts] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' as 'success' | 'error' | 'info' | 'warning' });
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    // Connect to WebSocket for real-time updates
    const ws = new WebSocket('ws://localhost:8100/ws/updates');
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setWsConnected(true);
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'port_change') {
        setSnackbar({
          open: true,
          message: `Port changed for ${data.service_id}: ${data.old_port} → ${data.new_port}`,
          severity: 'info'
        });
      } else if (data.type === 'conflicts_detected') {
        setConflicts(data.count);
        if (data.count > 0) {
          setSnackbar({
            open: true,
            message: `${data.count} port conflict(s) detected!`,
            severity: 'warning'
          });
        }
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);
    };
    
    return () => {
      ws.close();
    };
  }, []);

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
    { id: 'ports', label: 'Port Management', icon: <StorageIcon /> },
    { id: 'services', label: 'Service Status', icon: <CheckCircleIcon /> },
    { id: 'conflicts', label: 'Conflict Resolution', icon: <WarningIcon />, badge: conflicts },
    { id: 'config', label: 'Configuration', icon: <SettingsIcon /> },
  ];

  const handleViewChange = (viewId: string) => {
    setCurrentView(viewId);
    setDrawerOpen(false);
  };

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'ports':
        return <PortManagement />;
      case 'services':
        return <ServiceStatus />;
      case 'conflicts':
        return <ConflictResolution />;
      case 'config':
        return <Configuration />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex' }}>
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
              iTechSmart Port Manager
            </Typography>
            <Chip
              icon={wsConnected ? <CheckCircleIcon /> : <WarningIcon />}
              label={wsConnected ? 'Connected' : 'Disconnected'}
              color={wsConnected ? 'success' : 'error'}
              size="small"
              sx={{ mr: 2 }}
            />
            <Typography variant="body2" sx={{ mr: 2 }}>
              iTechSmart Suite
            </Typography>
          </Toolbar>
        </AppBar>

        {/* Drawer */}
        <Drawer
          variant="temporary"
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          sx={{
            width: 240,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: 240,
              boxSizing: 'border-box',
            },
          }}
        >
          <Toolbar />
          <Box sx={{ overflow: 'auto' }}>
            <List>
              {menuItems.map((item) => (
                <ListItem key={item.id} disablePadding>
                  <ListItemButton
                    selected={currentView === item.id}
                    onClick={() => handleViewChange(item.id)}
                  >
                    <ListItemIcon>
                      {item.badge ? (
                        <Badge badgeContent={item.badge} color="error">
                          {item.icon}
                        </Badge>
                      ) : (
                        item.icon
                      )}
                    </ListItemIcon>
                    <ListItemText primary={item.label} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
            <Divider />
            <List>
              <ListItem disablePadding>
                <ListItemButton>
                  <ListItemIcon>
                    <BackupIcon />
                  </ListItemIcon>
                  <ListItemText primary="Backup" />
                </ListItemButton>
              </ListItem>
              <ListItem disablePadding>
                <ListItemButton>
                  <ListItemIcon>
                    <RestartAltIcon />
                  </ListItemIcon>
                  <ListItemText primary="Reset" />
                </ListItemButton>
              </ListItem>
            </List>
          </Box>
        </Drawer>

        {/* Main Content */}
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Toolbar />
          <Container maxWidth="xl">
            {renderView()}
          </Container>
        </Box>

        {/* Snackbar for notifications */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert
            onClose={() => setSnackbar({ ...snackbar, open: false })}
            severity={snackbar.severity}
            sx={{ width: '100%' }}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
}

export default App;