import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import SandboxList from './pages/SandboxList';
import CreateSandbox from './pages/CreateSandbox';
import SandboxDetail from './pages/SandboxDetail';
import CodeEditor from './pages/CodeEditor';
import './styles/globals.css';

const App: React.FC = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/sandboxes" element={<SandboxList />} />
          <Route path="/sandboxes/new" element={<CreateSandbox />} />
          <Route path="/sandboxes/:id" element={<SandboxDetail />} />
          <Route path="/editor" element={<CodeEditor />} />
          <Route path="/monitoring" element={<div className="card"><h2>Monitoring - Coming Soon</h2></div>} />
          <Route path="/files" element={<div className="card"><h2>File Management - Coming Soon</h2></div>} />
          <Route path="/tests" element={<div className="card"><h2>Tests - Coming Soon</h2></div>} />
          <Route path="/settings" element={<div className="card"><h2>Settings - Coming Soon</h2></div>} />
        </Routes>
      </Layout>
    </Router>
  );
};

export default App;