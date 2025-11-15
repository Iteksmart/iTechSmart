import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';

// Import components
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Tickets from './pages/Tickets';
import Integrations from './pages/Integrations';
import Settings from './pages/Settings';

// Service Catalog Pages - Legacy
import ServiceCatalogDashboard from './pages/ServiceCatalog/Dashboard';
import ServiceCatalogBrowse from './pages/ServiceCatalog/Browse';
import ServiceCatalogRequests from './pages/ServiceCatalog/Requests';
import ServiceCatalogAdmin from './pages/ServiceCatalog/Admin';
import ServiceCatalogAnalytics from './pages/ServiceCatalog/Analytics';

// Service Catalog Pages - Enhanced (New)
import CatalogHome from './pages/ServiceCatalog/CatalogHome';
import RequestForm from './pages/ServiceCatalog/RequestForm';
import MyRequests from './pages/ServiceCatalog/MyRequests';
import Approvals from './pages/ServiceCatalog/Approvals';
import AdminConfig from './pages/ServiceCatalog/AdminConfig';

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

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Header />
          <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/tickets" element={<Tickets />} />
              <Route path="/integrations" element={<Integrations />} />
              <Route path="/settings" element={<Settings />} />
              
              {/* Service Catalog Routes - Enhanced Self-Service Portal */}
              <Route path="/service-catalog" element={<CatalogHome />} />
              <Route path="/service-catalog/request/:serviceId" element={<RequestForm />} />
              <Route path="/service-catalog/my-requests" element={<MyRequests />} />
              <Route path="/service-catalog/approvals" element={<Approvals />} />
              <Route path="/service-catalog/config" element={<AdminConfig />} />
              
              {/* Legacy Service Catalog Routes */}
              <Route path="/service-catalog/dashboard" element={<ServiceCatalogDashboard />} />
              <Route path="/service-catalog/browse" element={<ServiceCatalogBrowse />} />
              <Route path="/service-catalog/requests-old" element={<ServiceCatalogRequests />} />
              <Route path="/service-catalog/admin" element={<ServiceCatalogAdmin />} />
              <Route path="/service-catalog/analytics" element={<ServiceCatalogAnalytics />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
