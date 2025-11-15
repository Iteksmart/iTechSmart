import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { BarChart3, FileText, Database, Search, Settings, LayoutDashboard } from 'lucide-react';

// Pages
import Dashboard from './pages/Dashboard';
import Reports from './pages/Reports';
import DataSources from './pages/DataSources';
import QueryBuilder from './pages/QueryBuilder';
import Visualizations from './pages/Visualizations';
import SettingsPage from './pages/Settings';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-gradient-to-r from-blue-600 to-blue-700 border-b border-blue-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <BarChart3 className="h-8 w-8 text-white" />
                <span className="ml-2 text-xl font-bold text-white">
                  iTechSmart Pulse
                </span>
                <span className="ml-3 px-2 py-1 text-xs font-semibold text-blue-100 bg-blue-800 rounded">
                  ANALYTICS
                </span>
              </div>
              <nav className="flex space-x-8">
                <Link
                  to="/"
                  className="text-white hover:text-blue-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Dashboard
                </Link>
                <Link
                  to="/reports"
                  className="text-white hover:text-blue-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Reports
                </Link>
                <Link
                  to="/datasources"
                  className="text-white hover:text-blue-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Data Sources
                </Link>
                <Link
                  to="/query-builder"
                  className="text-white hover:text-blue-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Query Builder
                </Link>
                <Link
                  to="/visualizations"
                  className="text-white hover:text-blue-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Visualizations
                </Link>
                <Link
                  to="/settings"
                  className="text-white hover:text-blue-100 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Settings
                </Link>
              </nav>
              <div className="flex items-center space-x-4">
                <button className="text-white hover:text-blue-100">
                  <Search className="h-5 w-5" />
                </button>
                <Link to="/settings" className="text-white hover:text-blue-100">
                  <Settings className="h-5 w-5" />
                </Link>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/datasources" element={<DataSources />} />
            <Route path="/query-builder" element={<QueryBuilder />} />
            <Route path="/visualizations" element={<Visualizations />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;