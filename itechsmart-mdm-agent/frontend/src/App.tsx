import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { theme } from './utils/theme';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import DeploymentManager from './components/DeploymentManager';
import ConfigurationBuilder from './components/ConfigurationBuilder';
import HealthMonitor from './components/HealthMonitor';
import AIOptimizer from './components/AIOptimizer';
import DeploymentHistory from './components/DeploymentHistory';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/deploy" element={<DeploymentManager />} />
            <Route path="/config" element={<ConfigurationBuilder />} />
            <Route path="/monitor" element={<HealthMonitor />} />
            <Route path="/ai" element={<AIOptimizer />} />
            <Route path="/history" element={<DeploymentHistory />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
