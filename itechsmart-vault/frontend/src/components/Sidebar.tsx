import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Key, FolderLock, Shield, FileText, Settings } from 'lucide-react';

const Sidebar = () => {
  const location = useLocation();
  const menuItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/secrets', icon: Key, label: 'Secrets' },
    { path: '/vaults', icon: FolderLock, label: 'Vaults' },
    { path: '/policies', icon: Shield, label: 'Policies' },
    { path: '/audit', icon: FileText, label: 'Audit Logs' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col">
      <div className="p-6">
        <h1 className="text-2xl font-bold">iTechSmart</h1>
        <p className="text-sm text-gray-400">Vault</p>
      </div>
      <nav className="flex-1 px-4">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link key={item.path} to={item.path}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg mb-2 transition-colors ${
                isActive ? 'bg-primary-600 text-white' : 'text-gray-300 hover:bg-gray-800'
              }`}>
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-gray-800">
        <div className="text-xs text-gray-400">Version 1.0.0</div>
      </div>
    </div>
  );
};

export default Sidebar;
