import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';

// Import components
import Header from './components/Header';

// Observatory Pages
import ObservatoryDashboard from './pages/Observatory/Dashboard';
import ObservatoryMetrics from './pages/Observatory/Metrics';
import ObservatoryTraces from './pages/Observatory/Traces';
import ObservatoryLogs from './pages/Observatory/Logs';
import ObservatoryAlerts from './pages/Observatory/Alerts';

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
          <Box component="main" sx={{ flexGrow: 1 }}>
            <Routes>
              <Route path="/" element={<Navigate to="/observatory/dashboard" replace />} />
              <Route path="/observatory/dashboard" element={<ObservatoryDashboard />} />
              <Route path="/observatory/metrics" element={<ObservatoryMetrics />} />
              <Route path="/observatory/traces" element={<ObservatoryTraces />} />
              <Route path="/observatory/logs" element={<ObservatoryLogs />} />
              <Route path="/observatory/alerts" element={<ObservatoryAlerts />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;