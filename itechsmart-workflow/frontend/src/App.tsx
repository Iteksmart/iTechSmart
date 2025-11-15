import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Dashboard from './pages/Dashboard';
import Workflows from './pages/Workflows';
import Executions from './pages/Executions';
import Templates from './pages/Templates';
import Integrations from './pages/Integrations';
import Settings from './pages/Settings';
import Login from './pages/Login';
import Sidebar from './components/Sidebar';
import Header from './components/Header';

// Automation Orchestrator Pages
import AutomationOrchestratorDashboard from './pages/AutomationOrchestrator/Dashboard';
import AutomationOrchestratorWorkflows from './pages/AutomationOrchestrator/Workflows';
import AutomationOrchestratorBuilder from './pages/AutomationOrchestrator/Builder';
import AutomationOrchestratorExecutions from './pages/AutomationOrchestrator/Executions';
import AutomationOrchestratorTemplates from './pages/AutomationOrchestrator/Templates';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
    setIsLoading(false);
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <Router>
        <Routes>
          <Route path="/login" element={<Login onLogin={() => setIsAuthenticated(true)} />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    );
  }

  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header onLogout={() => setIsAuthenticated(false)} />
          <main className="flex-1 overflow-y-auto p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/workflows" element={<Workflows />} />
              <Route path="/executions" element={<Executions />} />
              <Route path="/templates" element={<Templates />} />
              <Route path="/integrations" element={<Integrations />} />
              <Route path="/settings" element={<Settings />} />
              
              {/* Automation Orchestrator Routes */}
              <Route path="/automation-orchestrator" element={<AutomationOrchestratorDashboard />} />
              <Route path="/automation-orchestrator/workflows" element={<AutomationOrchestratorWorkflows />} />
              <Route path="/automation-orchestrator/builder" element={<AutomationOrchestratorBuilder />} />
              <Route path="/automation-orchestrator/executions" element={<AutomationOrchestratorExecutions />} />
              <Route path="/automation-orchestrator/templates" element={<AutomationOrchestratorTemplates />} />
              
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;