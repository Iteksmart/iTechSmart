import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Shield, Bell, Settings as SettingsIcon } from 'lucide-react';

// Pages
import Dashboard from './pages/Dashboard';
import Threats from './pages/Threats';
import Vulnerabilities from './pages/Vulnerabilities';
import Compliance from './pages/Compliance';
import Incidents from './pages/Incidents';
import Settings from './pages/Settings';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-gradient-to-r from-red-600 to-red-700 border-b border-red-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <Shield className="h-8 w-8 text-white" />
                <span className="ml-2 text-xl font-bold text-white">
                  iTechSmart Shield
                </span>
                <span className="ml-3 px-2 py-1 text-xs font-semibold text-red-100 bg-red-800 rounded">
                  SECURITY
                </span>
              </div>
              <nav className="flex space-x-8">
                <Link
                  to="/"
                  className="text-white hover:text-red-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Dashboard
                </Link>
                <Link
                  to="/threats"
                  className="text-white hover:text-red-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Threats
                </Link>
                <Link
                  to="/vulnerabilities"
                  className="text-white hover:text-red-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Vulnerabilities
                </Link>
                <Link
                  to="/compliance"
                  className="text-white hover:text-red-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Compliance
                </Link>
                <Link
                  to="/incidents"
                  className="text-white hover:text-red-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Incidents
                </Link>
                <Link
                  to="/settings"
                  className="text-white hover:text-red-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Settings
                </Link>
              </nav>
              <div className="flex items-center space-x-4">
                <button className="text-white hover:text-red-100">
                  <Bell className="h-5 w-5" />
                </button>
                <Link to="/settings" className="text-white hover:text-red-100">
                  <SettingsIcon className="h-5 w-5" />
                </Link>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/threats" element={<Threats />} />
            <Route path="/vulnerabilities" element={<Vulnerabilities />} />
            <Route path="/compliance" element={<Compliance />} />
            <Route path="/incidents" element={<Incidents />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;