import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Button,
  CssBaseline,
  ThemeProvider,
  createTheme,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
} from '@mui/material';
import {
  Dashboard,
  Assessment,
  Security,
  TrendingDown,
  Description,
  Policy,
} from '@mui/icons-material';

// Import pages
import ComplianceDashboard from './pages/ComplianceDashboard';
import ControlsManagement from './pages/ControlsManagement';
import AssessmentsPage from './pages/AssessmentsPage';
import GapAnalysis from './pages/GapAnalysis';
import ReportsPage from './pages/ReportsPage';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const drawerWidth = 240;

function Home() {
  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        Welcome to iTechSmart Compliance Center
      </Typography>
      <Typography variant="h6" color="text.secondary" paragraph>
        Multi-Framework Compliance Tracking and Management Platform
      </Typography>
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          Compliance Center Features
        </Typography>
        <Typography variant="body1" paragraph>
          Comprehensive compliance management across multiple frameworks:
        </Typography>
        <ul>
          <li><strong>SOC 2 Type II</strong> - Service Organization Control with 64+ control points</li>
          <li><strong>ISO 27001</strong> - Information Security Management with 114 controls</li>
          <li><strong>HIPAA</strong> - Healthcare data protection with administrative, physical, and technical safeguards</li>
          <li><strong>GDPR</strong> - General Data Protection Regulation</li>
          <li><strong>PCI-DSS</strong> - Payment Card Industry Data Security Standard</li>
        </ul>
        
        <Typography variant="h6" sx={{ mt: 3 }} gutterBottom>
          Key Capabilities
        </Typography>
        <ul>
          <li>Multi-framework compliance tracking and policy alignment</li>
          <li>Evidence management and verification</li>
          <li>Assessment and audit workflows</li>
          <li>Gap analysis and remediation tracking</li>
          <li>Automated compliance reporting</li>
          <li>Policy document management</li>
          <li>Complete audit trail</li>
        </ul>
      </Box>
    </Container>
  );
}

function App() {
  const menuItems = [
    { text: 'Dashboard', icon: <Dashboard />, path: '/dashboard' },
    { text: 'Controls', icon: <Security />, path: '/controls' },
    { text: 'Assessments', icon: <Assessment />, path: '/assessments' },
    { text: 'Gap Analysis', icon: <TrendingDown />, path: '/gap-analysis' },
    { text: 'Reports', icon: <Description />, path: '/reports' },
  ];

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex' }}>
          <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
            <Toolbar>
              <Policy sx={{ mr: 2 }} />
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                iTechSmart Compliance Center
              </Typography>
              <Typography variant="body2" sx={{ mr: 2 }}>
                v1.1.0
              </Typography>
            </Toolbar>
          </AppBar>
          
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
                      <Dashboard />
                    </ListItemIcon>
                    <ListItemText primary="Home" />
                  </ListItemButton>
                </ListItem>
                {menuItems.map((item) => (
                  <ListItem key={item.text} disablePadding>
                    <ListItemButton component={Link} to={item.path}>
                      <ListItemIcon>{item.icon}</ListItemIcon>
                      <ListItemText primary={item.text} />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            </Box>
          </Drawer>
          
          <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
            <Toolbar />
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/dashboard" element={<ComplianceDashboard />} />
              <Route path="/controls" element={<ControlsManagement />} />
              <Route path="/assessments" element={<AssessmentsPage />} />
              <Route path="/gap-analysis" element={<GapAnalysis />} />
              <Route path="/reports" element={<ReportsPage />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;