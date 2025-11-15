import { useState } from 'react';
import { User, Shield, Key } from 'lucide-react';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'api-keys', label: 'API Keys', icon: Key },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Settings</h1>
        <p className="text-gray-600 mt-1">Manage your account settings</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <div className="card">
            <nav className="space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                      activeTab === tab.id ? 'bg-primary-50 text-primary-700' : 'text-gray-700 hover:bg-gray-50'
                    }`}>
                    <Icon size={20} />
                    <span className="font-medium">{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        <div className="lg:col-span-3">
          <div className="card">
            {activeTab === 'profile' && (
              <div className="space-y-4">
                <h2 className="text-2xl font-bold text-gray-800">Profile Settings</h2>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                  <input type="text" className="input" defaultValue="Admin User" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  <input type="email" className="input" defaultValue="admin@itechsmart.com" />
                </div>
                <button className="btn-primary">Save Changes</button>
              </div>
            )}
            {activeTab === 'security' && (
              <div className="space-y-4">
                <h2 className="text-2xl font-bold text-gray-800">Security Settings</h2>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
                  <input type="password" className="input" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">New Password</label>
                  <input type="password" className="input" />
                </div>
                <button className="btn-primary">Update Password</button>
              </div>
            )}
            {activeTab === 'api-keys' && (
              <div className="space-y-4">
                <h2 className="text-2xl font-bold text-gray-800">API Keys</h2>
                <p className="text-gray-600">Manage API keys for programmatic access</p>
                <button className="btn-primary">Generate API Key</button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
