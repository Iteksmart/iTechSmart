/**
 * iTechSmart Citadel - Main Application Component
 * Sovereign Digital Infrastructure Platform
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Shield, AlertTriangle, FileCheck, Activity, Server } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Security from './pages/Security';
import Compliance from './pages/Compliance';
import Threats from './pages/Threats';
import Infrastructure from './pages/Infrastructure';

function Navigation() {
  const location = useLocation();
  
  const navItems = [
    { path: '/', icon: Activity, label: 'Dashboard' },
    { path: '/security', icon: Shield, label: 'Security' },
    { path: '/compliance', icon: FileCheck, label: 'Compliance' },
    { path: '/threats', icon: AlertTriangle, label: 'Threats' },
    { path: '/infrastructure', icon: Server, label: 'Infrastructure' },
  ];

  return (
    <nav className="bg-black border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="flex items-center space-x-2">
                <Shield className="w-8 h-8 text-blue-500" />
                <div>
                  <h1 className="text-xl font-bold text-white">iTechSmart Citadel</h1>
                  <p className="text-xs text-gray-400">Sovereign Infrastructure</p>
                </div>
              </div>
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
                      ? 'bg-gray-900 text-white'
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white'
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
      <div className="min-h-screen bg-black">
        <Navigation />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/security" element={<Security />} />
            <Route path="/compliance" element={<Compliance />} />
            <Route path="/threats" element={<Threats />} />
            <Route path="/infrastructure" element={<Infrastructure />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;