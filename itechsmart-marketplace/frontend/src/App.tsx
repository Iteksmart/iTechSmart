import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Store, User, ShoppingCart, Settings, BarChart3, Code } from 'lucide-react';
import Marketplace from './pages/Marketplace';
import AppDetail from './pages/AppDetail';
import Developer from './pages/Developer';
import MyApps from './pages/MyApps';
import SettingsPage from './pages/Settings';

function Navigation() {
  const location = useLocation();
  
  const isActive = (path: string) => {
    return location.pathname === path ? 'bg-blue-700' : '';
  };

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center space-x-2">
              <Store className="w-8 h-8" />
              <span className="text-xl font-bold">iTechSmart Marketplace</span>
            </Link>
            
            <div className="flex space-x-4">
              <Link
                to="/"
                className={`flex items-center space-x-2 px-3 py-2 rounded-md hover:bg-blue-700 transition ${isActive('/')}`}
              >
                <Store className="w-4 h-4" />
                <span>Marketplace</span>
              </Link>
              
              <Link
                to="/my-apps"
                className={`flex items-center space-x-2 px-3 py-2 rounded-md hover:bg-blue-700 transition ${isActive('/my-apps')}`}
              >
                <ShoppingCart className="w-4 h-4" />
                <span>My Apps</span>
              </Link>
              
              <Link
                to="/developer"
                className={`flex items-center space-x-2 px-3 py-2 rounded-md hover:bg-blue-700 transition ${isActive('/developer')}`}
              >
                <Code className="w-4 h-4" />
                <span>Developer</span>
              </Link>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <Link
              to="/settings"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md hover:bg-blue-700 transition ${isActive('/settings')}`}
            >
              <Settings className="w-4 h-4" />
              <span>Settings</span>
            </Link>
            
            <div className="flex items-center space-x-2 px-3 py-2 bg-blue-700 rounded-md">
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
          <Route path="/" element={<Marketplace />} />
          <Route path="/app/:id" element={<AppDetail />} />
          <Route path="/developer" element={<Developer />} />
          <Route path="/my-apps" element={<MyApps />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;