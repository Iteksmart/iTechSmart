import React, { useState } from 'react';
import {
  Box,
  CssBaseline,
  ThemeProvider,
  createTheme,
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Container,
  Grid,
  Paper,
  Card,
  CardContent,
  Button,
  Chip,
  TextField,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Apps as AppsIcon,
  Build as BuildIcon,
  Code as CodeIcon,
  Storage as StorageIcon,
  PlayArrow as PlayIcon,
  CloudUpload as DeployIcon,
  Settings as SettingsIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';

const drawerWidth = 260;

// Create theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#9c27b0',
    },
    secondary: {
      main: '#00bcd4',
    },
    background: {
      default: '#0a0a0a',
      paper: '#1a1a1a',
    },
  },
});

// Mock data
const mockApps = [
  { id: 1, name: 'Customer Portal', type: 'Web App', status: 'Published', created: '2024-01-15' },
  { id: 2, name: 'Inventory Manager', type: 'Dashboard', status: 'Draft', created: '2024-01-20' },
  { id: 3, name: 'Sales Tracker', type: 'Mobile App', status: 'Published', created: '2024-01-25' },
  { id: 4, name: 'Employee Directory', type: 'Web App', status: 'Testing', created: '2024-02-01' },
];

const componentLibrary = [
  { id: 1, name: 'Button', category: 'Basic', icon: '🔘' },
  { id: 2, name: 'Text Input', category: 'Forms', icon: '📝' },
  { id: 3, name: 'Data Table', category: 'Data', icon: '📊' },
  { id: 4, name: 'Chart', category: 'Visualization', icon: '📈' },
  { id: 5, name: 'Card', category: 'Layout', icon: '🃏' },
  { id: 6, name: 'Navigation', category: 'Layout', icon: '🧭' },
];

function App() {
  const [selectedPage, setSelectedPage] = useState('dashboard');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newAppName, setNewAppName] = useState('');

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
    { id: 'apps', label: 'My Apps', icon: <AppsIcon /> },
    { id: 'builder', label: 'App Builder', icon: <BuildIcon /> },
    { id: 'components', label: 'Components', icon: <CodeIcon /> },
    { id: 'data', label: 'Data Sources', icon: <StorageIcon /> },
    { id: 'deploy', label: 'Deployment', icon: <DeployIcon /> },
    { id: 'settings', label: 'Settings', icon: <SettingsIcon /> },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Published':
        return 'success';
      case 'Testing':
        return 'warning';
      case 'Draft':
        return 'info';
      default:
        return 'default';
    }
  };

  const handleCreateApp = () => {
    console.log('Creating app:', newAppName);
    setCreateDialogOpen(false);
    setNewAppName('');
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex' }}>
        {/* App Bar */}
        <AppBar
          position="fixed"
          sx={{
            zIndex: (theme) => theme.zIndex.drawer + 1,
            background: 'linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%)',
          }}
        >
          <Toolbar>
            <BuildIcon sx={{ mr: 2, fontSize: 32 }} />
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
              iTechSmart Forge - Low-Code App Builder
            </Typography>
            <Chip label="iTechSmart Suite" color="secondary" size="small" />
          </Toolbar>
        </AppBar>

        {/* Sidebar */}
        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: drawerWidth,
              boxSizing: 'border-box',
              background: 'linear-gradient(180deg, #1a1a1a 0%, #0a0a0a 100%)',
              borderRight: '1px solid rgba(156, 39, 176, 0.2)',
            },
          }}
        >
          <Toolbar />
          <Box sx={{ overflow: 'auto', mt: 2 }}>
            <List>
              {menuItems.map((item) => (
                <ListItem key={item.id} disablePadding>
                  <ListItemButton
                    selected={selectedPage === item.id}
                    onClick={() => setSelectedPage(item.id)}
                    sx={{
                      mx: 1,
                      borderRadius: 1,
                      '&.Mui-selected': {
                        background: 'linear-gradient(135deg, rgba(156, 39, 176, 0.2) 0%, rgba(123, 31, 162, 0.2) 100%)',
                        borderLeft: '3px solid #9c27b0',
                      },
                    }}
                  >
                    <ListItemIcon sx={{ color: selectedPage === item.id ? '#9c27b0' : 'inherit' }}>
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText primary={item.label} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Box>
        </Drawer>

        {/* Main Content */}
        <Box component="main" sx={{ flexGrow: 1, p: 3, backgroundColor: '#0a0a0a', minHeight: '100vh' }}>
          <Toolbar />
          <Container maxWidth="xl">
            {selectedPage === 'dashboard' && (
              <>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Typography variant="h4" sx={{ fontWeight: 600 }}>
                    Dashboard
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => setCreateDialogOpen(true)}
                    sx={{ background: 'linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%)' }}
                  >
                    Create New App
                  </Button>
                </Box>

                {/* Stats Cards */}
                <Grid container spacing={3} sx={{ mb: 4 }}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%)' }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>Total Apps</Typography>
                        <Typography variant="h3" sx={{ fontWeight: 700 }}>24</Typography>
                        <Typography variant="body2" sx={{ mt: 1, opacity: 0.9 }}>
                          +3 this month
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #00bcd4 0%, #0097a7 100%)' }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>Published</Typography>
                        <Typography variant="h3" sx={{ fontWeight: 700 }}>18</Typography>
                        <Typography variant="body2" sx={{ mt: 1, opacity: 0.9 }}>
                          75% of total
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #4caf50 0%, #388e3c 100%)' }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>Active Users</Typography>
                        <Typography variant="h3" sx={{ fontWeight: 700 }}>1.2K</Typography>
                        <Typography variant="body2" sx={{ mt: 1, opacity: 0.9 }}>
                          +15% this week
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #ff9800 0%, #f57c00 100%)' }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>Components</Typography>
                        <Typography variant="h3" sx={{ fontWeight: 700 }}>156</Typography>
                        <Typography variant="body2" sx={{ mt: 1, opacity: 0.9 }}>
                          In library
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {/* Recent Apps */}
                <Paper sx={{ p: 3, background: '#1a1a1a' }}>
                  <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
                    Recent Applications
                  </Typography>
                  <Grid container spacing={2}>
                    {mockApps.map((app) => (
                      <Grid item xs={12} key={app.id}>
                        <Card sx={{ background: '#0a0a0a' }}>
                          <CardContent>
                            <Grid container alignItems="center" spacing={2}>
                              <Grid item xs={12} sm={3}>
                                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                                  {app.name}
                                </Typography>
                              </Grid>
                              <Grid item xs={12} sm={2}>
                                <Typography variant="body2" color="text.secondary">
                                  {app.type}
                                </Typography>
                              </Grid>
                              <Grid item xs={12} sm={2}>
                                <Chip
                                  label={app.status}
                                  color={getStatusColor(app.status) as any}
                                  size="small"
                                />
                              </Grid>
                              <Grid item xs={12} sm={2}>
                                <Typography variant="body2" color="text.secondary">
                                  {app.created}
                                </Typography>
                              </Grid>
                              <Grid item xs={12} sm={3}>
                                <Box sx={{ display: 'flex', gap: 1 }}>
                                  <IconButton size="small" color="primary">
                                    <ViewIcon />
                                  </IconButton>
                                  <IconButton size="small" color="primary">
                                    <EditIcon />
                                  </IconButton>
                                  <IconButton size="small" color="error">
                                    <DeleteIcon />
                                  </IconButton>
                                </Box>
                              </Grid>
                            </Grid>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Paper>
              </>
            )}

            {selectedPage === 'builder' && (
              <Paper sx={{ p: 4, background: '#1a1a1a' }}>
                <Typography variant="h5" gutterBottom>
                  Visual App Builder
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                  Drag and drop components to build your application
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} md={3}>
                    <Paper sx={{ p: 2, background: '#0a0a0a' }}>
                      <Typography variant="h6" gutterBottom>Component Library</Typography>
                      <List>
                        {componentLibrary.map((comp) => (
                          <ListItem key={comp.id} sx={{ py: 1 }}>
                            <ListItemText
                              primary={
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <span>{comp.icon}</span>
                                  <span>{comp.name}</span>
                                </Box>
                              }
                              secondary={comp.category}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, background: '#0a0a0a', minHeight: 500, border: '2px dashed #9c27b0' }}>
                      <Typography variant="h6" gutterBottom>Canvas</Typography>
                      <Box sx={{ textAlign: 'center', mt: 10 }}>
                        <BuildIcon sx={{ fontSize: 80, color: '#9c27b0', opacity: 0.3 }} />
                        <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
                          Drag components here to start building
                        </Typography>
                      </Box>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} md={3}>
                    <Paper sx={{ p: 2, background: '#0a0a0a' }}>
                      <Typography variant="h6" gutterBottom>Properties</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Select a component to edit its properties
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </Paper>
            )}

            {selectedPage !== 'dashboard' && selectedPage !== 'builder' && (
              <Paper sx={{ p: 4, textAlign: 'center', background: '#1a1a1a' }}>
                <Typography variant="h5" gutterBottom>
                  {menuItems.find(item => item.id === selectedPage)?.label}
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
                  This section is ready for implementation. The backend API is fully functional.
                </Typography>
                <Button variant="contained" sx={{ mt: 3 }}>
                  Get Started
                </Button>
              </Paper>
            )}
          </Container>
        </Box>
      </Box>

      {/* Create App Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Application</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Application Name"
            fullWidth
            variant="outlined"
            value={newAppName}
            onChange={(e) => setNewAppName(e.target.value)}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateApp} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </ThemeProvider>
  );
}

export default App;