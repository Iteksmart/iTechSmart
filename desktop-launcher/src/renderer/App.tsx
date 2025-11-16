import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import LicenseActivation from './components/LicenseActivation';
import Settings from './components/Settings';
import { Menu, Settings as SettingsIcon, Key, X } from 'lucide-react';

function App() {
  const [currentView, setCurrentView] = useState<'dashboard' | 'settings' | 'license'>('dashboard');
  const [license, setLicense] = useState<any>(null);
  const [dockerInstalled, setDockerInstalled] = useState<boolean>(true);
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);

  useEffect(() => {
    // Check Docker installation
    window.electron.checkDockerInstalled().then(setDockerInstalled);
    
    // Load license
    window.electron.getLicense().then(setLicense);

    // Listen for events
    window.electron.on('docker-not-installed', () => {
      setDockerInstalled(false);
    });

    window.electron.on('license-invalid', () => {
      setCurrentView('license');
    });
  }, []);

  const handleLicenseActivated = (newLicense: any) => {
    setLicense(newLicense);
    setCurrentView('dashboard');
  };

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-slate-800 border-r border-slate-700 transition-all duration-300 flex flex-col`}>
        {/* Header */}
        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
          {sidebarOpen && (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg"></div>
              <span className="font-bold text-lg">iTechSmart</span>
            </div>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <Menu size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          <button
            onClick={() => setCurrentView('dashboard')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
              currentView === 'dashboard'
                ? 'bg-blue-600 text-white'
                : 'hover:bg-slate-700 text-slate-300'
            }`}
          >
            <Menu size={20} />
            {sidebarOpen && <span>Dashboard</span>}
          </button>

          <button
            onClick={() => setCurrentView('license')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
              currentView === 'license'
                ? 'bg-blue-600 text-white'
                : 'hover:bg-slate-700 text-slate-300'
            }`}
          >
            <Key size={20} />
            {sidebarOpen && <span>License</span>}
          </button>

          <button
            onClick={() => setCurrentView('settings')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
              currentView === 'settings'
                ? 'bg-blue-600 text-white'
                : 'hover:bg-slate-700 text-slate-300'
            }`}
          >
            <SettingsIcon size={20} />
            {sidebarOpen && <span>Settings</span>}
          </button>
        </nav>

        {/* License Info */}
        {sidebarOpen && license && (
          <div className="p-4 border-t border-slate-700">
            <div className="text-xs text-slate-400 mb-1">License</div>
            <div className="text-sm font-medium text-slate-200">
              {license.tier.toUpperCase()}
            </div>
            {license.isTrial && (
              <div className="text-xs text-yellow-400 mt-1">
                Trial: {getDaysRemaining(license.trialEndsAt)} days left
              </div>
            )}
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Docker Warning */}
        {!dockerInstalled && (
          <div className="bg-yellow-600 text-white px-6 py-3 flex items-center justify-between">
            <div>
              <strong>Docker not installed.</strong> Please install Docker Desktop to use iTechSmart Suite.
            </div>
            <button
              onClick={() => window.electron.installDocker()}
              className="px-4 py-2 bg-white text-yellow-600 rounded-lg hover:bg-yellow-50 transition-colors font-medium"
            >
              Install Docker
            </button>
          </div>
        )}

        {/* Content Area */}
        <div className="flex-1 overflow-auto">
          {currentView === 'dashboard' && <Dashboard license={license} />}
          {currentView === 'license' && (
            <LicenseActivation
              currentLicense={license}
              onLicenseActivated={handleLicenseActivated}
            />
          )}
          {currentView === 'settings' && <Settings />}
        </div>
      </div>
    </div>
  );
}

function getDaysRemaining(expiresAt: string): number {
  const now = new Date();
  const expires = new Date(expiresAt);
  const diff = expires.getTime() - now.getTime();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

export default App;