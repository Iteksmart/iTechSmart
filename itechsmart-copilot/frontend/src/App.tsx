import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { MessageSquare, FileText, Lightbulb, BookOpen, Cpu, Settings, LayoutDashboard } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Prompts from './pages/Prompts';
import Knowledge from './pages/Knowledge';
import Models from './pages/Models';
import SettingsPage from './pages/Settings';

function Navigation() {
  const location = useLocation();
  
  const navItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/chat', icon: MessageSquare, label: 'Chat' },
    { path: '/prompts', icon: Lightbulb, label: 'Prompts' },
    { path: '/knowledge', icon: BookOpen, label: 'Knowledge' },
    { path: '/models', icon: Cpu, label: 'Models' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <h1 className="text-2xl font-bold text-indigo-600">iTechSmart Copilot</h1>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                      isActive
                        ? 'border-indigo-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
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
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/prompts" element={<Prompts />} />
            <Route path="/knowledge" element={<Knowledge />} />
            <Route path="/models" element={<Models />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;