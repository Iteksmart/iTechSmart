import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import {
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Psychology as AIIcon,
  TrendingUp as PredictionsIcon,
  Lightbulb as InsightsIcon
} from '@mui/icons-material';

// Import AI pages
import AIDashboard from './pages/AIDashboard';
import ModelManagement from './pages/ModelManagement';
import PredictionsView from './pages/PredictionsView';
import InsightsExplorer from './pages/InsightsExplorer';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const drawerWidth = 240;

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex' }}>
          {/* App Bar */}
          <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
            <Toolbar>
              <AIIcon sx={{ mr: 2 }} />
              <Typography variant="h6" noWrap component="div">
                iTechSmart Analytics - AI Insights
              </Typography>
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
              },
            }}
          >
            <Toolbar />
            <Box sx={{ overflow: 'auto' }}>
              <List>
                <ListItem disablePadding>
                  <ListItemButton component={Link} to="/">
                    <ListItemIcon>
                      <DashboardIcon />
                    </ListItemIcon>
                    <ListItemText primary="AI Dashboard" />
                  </ListItemButton>
                </ListItem>
                <ListItem disablePadding>
                  <ListItemButton component={Link} to="/models">
                    <ListItemIcon>
                      <AIIcon />
                    </ListItemIcon>
                    <ListItemText primary="Model Management" />
                  </ListItemButton>
                </ListItem>
                <ListItem disablePadding>
                  <ListItemButton component={Link} to="/predictions">
                    <ListItemIcon>
                      <PredictionsIcon />
                    </ListItemIcon>
                    <ListItemText primary="Predictions" />
                  </ListItemButton>
                </ListItem>
                <ListItem disablePadding>
                  <ListItemButton component={Link} to="/insights">
                    <ListItemIcon>
                      <InsightsIcon />
                    </ListItemIcon>
                    <ListItemText primary="Insights Explorer" />
                  </ListItemButton>
                </ListItem>
              </List>
            </Box>
          </Drawer>

          {/* Main Content */}
          <Box component="main" sx={{ flexGrow: 1, bgcolor: 'background.default' }}>
            <Toolbar />
            <Routes>
              <Route path="/" element={<AIDashboard />} />
              <Route path="/models" element={<ModelManagement />} />
              <Route path="/predictions" element={<PredictionsView />} />
              <Route path="/insights" element={<InsightsExplorer />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;