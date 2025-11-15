import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Bell, FileText, Radio, History, BarChart3, Settings, User } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Templates from './pages/Templates';
import Channels from './pages/Channels';
import NotificationHistory from './pages/History';
import Analytics from './pages/Analytics';
import SettingsPage from './pages/Settings';

function Navigation() {
  const location = useLocation();
  
  const isActive = (path: string) => {
    return location.pathname === path ? 'bg-purple-700' : '';
  };

  return (
    <nav className="bg-purple-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center space-x-2">
              <Bell className="w-8 h-8" />
              <span className="text-xl font-bold">iTechSmart Notify</span>
            </Link>
            
            <div className="flex space-x-4">
              <Link
                to="/"
                className={`flex items-center space-x-2 px-3 py-2 rounded-md hover:bg-purple-700 transition ${isActive('/')}`}
              >
                <BarChart3 className="w-4 h-4" />
                <span>Dashboard</span>
              </Link>
              
              <Link
                to="/templates"
                className={`flex items-center space-x-2 px-3 py-2 rounded-md hover:bg-purple-700 transition ${isActive('/templates')}`}
              >
                <FileText className="w-4 h-4" />
                <span>Templates</span>
              </Link>
              
              <Link
                to="/channels"
                className={`flex items-center space-x-2 px-3 py-2 rounded-md hover:bg-purple-700 transition ${isActive('/channels')}`}
              >
                <Radio className="w-4 h-4" />
                <span>Channels</span>
              </Link>
              
              <Link
                to="/history"
                className={`flex items-center space-x-2 px-3 py-2 rounded-md hover:bg-purple-700 transition ${isActive('/history')}`}
              >
                <History className="w-4 h-4" />
                <span>History</span>
              </Link>
              
              <Link
                to="/analytics"
                className={`flex items-center space-x-2 px-3 py-2 rounded-md hover:bg-purple-700 transition ${isActive('/analytics')}`}
              >
                <BarChart3 className="w-4 h-4" />
                <span>Analytics</span>
              </Link>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <Link
              to="/settings"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md hover:bg-purple-700 transition ${isActive('/settings')}`}
            >
              <Settings className="w-4 h-4" />
              <span>Settings</span>
            </Link>
            
            <div className="flex items-center space-x-2 px-3 py-2 bg-purple-700 rounded-md">
              <User className="w-4 h-4" />
              <span>Admin User</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/templates" element={<Templates />} />
          <Route path="/channels" element={<Channels />} />
          <Route path="/history" element={<NotificationHistory />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;