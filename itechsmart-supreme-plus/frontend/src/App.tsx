/**
 * iTechSmart Supreme Plus - Main Application Component
 * AI-Powered Infrastructure Auto-Remediation Platform
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Activity, AlertTriangle, Settings, Server, BarChart3 } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Incidents from './pages/Incidents';
import Remediations from './pages/Remediations';
import Integrations from './pages/Integrations';
import Monitoring from './pages/Monitoring';

function Navigation() {
  const location = useLocation();
  
  const navItems = [
    { path: '/', icon: BarChart3, label: 'Dashboard' },
    { path: '/incidents', icon: AlertTriangle, label: 'Incidents' },
    { path: '/remediations', icon: Activity, label: 'Remediations' },
    { path: '/monitoring', icon: Server, label: 'Monitoring' },
    { path: '/integrations', icon: Settings, label: 'Integrations' },
  ];

  return (
    <nav className="bg-slate-800 border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold text-white">iTechSmart Supreme Plus</h1>
              <p className="text-xs text-slate-400">AI-Powered Auto-Remediation</p>
            </div>
          </div>
          <div className="flex space-x-4">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-slate-900 text-white'
                      : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {item.label}
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-900">
        <Navigation />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/incidents" element={<Incidents />} />
            <Route path="/remediations" element={<Remediations />} />
            <Route path="/monitoring" element={<Monitoring />} />
            <Route path="/integrations" element={<Integrations />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;