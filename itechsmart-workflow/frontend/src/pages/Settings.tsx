import { useState } from 'react';
import { User, Bell, Shield, Database, Zap, Globe } from 'lucide-react';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('profile');

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'database', label: 'Database', icon: Database },
    { id: 'performance', label: 'Performance', icon: Zap },
    { id: 'general', label: 'General', icon: Globe },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Settings</h1>
        <p className="text-gray-600 mt-1">Manage your account and application settings</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="card">
            <nav className="space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                      activeTab === tab.id
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <Icon size={20} />
                    <span className="font-medium">{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          <div className="card">
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-800">Profile Settings</h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Full Name
                    </label>
                    <input
                      type="text"
                      className="input"
                      placeholder="John Doe"
                      defaultValue="Admin User"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      className="input"
                      placeholder="admin@example.com"
                      defaultValue="admin@itechsmart.com"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Username
                    </label>
                    <input
                      type="text"
                      className="input"
                      placeholder="admin"
                      defaultValue="admin"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Bio
                    </label>
                    <textarea
                      className="input"
                      rows={4}
                      placeholder="Tell us about yourself..."
                    />
                  </div>

                  <button className="btn-primary">
                    Save Changes
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-800">Notification Settings</h2>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-800">Workflow Execution</p>
                      <p className="text-sm text-gray-600">Get notified when workflows complete</p>
                    </div>
                    <input type="checkbox" className="w-5 h-5" defaultChecked />
                  </div>

                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-800">Execution Failures</p>
                      <p className="text-sm text-gray-600">Get notified when workflows fail</p>
                    </div>
                    <input type="checkbox" className="w-5 h-5" defaultChecked />
                  </div>

                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-800">Weekly Summary</p>
                      <p className="text-sm text-gray-600">Receive weekly execution summary</p>
                    </div>
                    <input type="checkbox" className="w-5 h-5" />
                  </div>

                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-800">System Updates</p>
                      <p className="text-sm text-gray-600">Get notified about system updates</p>
                    </div>
                    <input type="checkbox" className="w-5 h-5" defaultChecked />
                  </div>

                  <button className="btn-primary">
                    Save Preferences
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-800">Security Settings</h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Current Password
                    </label>
                    <input
                      type="password"
                      className="input"
                      placeholder="Enter current password"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      New Password
                    </label>
                    <input
                      type="password"
                      className="input"
                      placeholder="Enter new password"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Confirm New Password
                    </label>
                    <input
                      type="password"
                      className="input"
                      placeholder="Confirm new password"
                    />
                  </div>

                  <button className="btn-primary">
                    Update Password
                  </button>

                  <div className="border-t pt-6 mt-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Two-Factor Authentication</h3>
                    <p className="text-gray-600 mb-4">
                      Add an extra layer of security to your account
                    </p>
                    <button className="btn-secondary">
                      Enable 2FA
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'database' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-800">Database Settings</h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Database Host
                    </label>
                    <input
                      type="text"
                      className="input"
                      placeholder="localhost"
                      defaultValue="localhost"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Database Port
                    </label>
                    <input
                      type="text"
                      className="input"
                      placeholder="5432"
                      defaultValue="5432"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Database Name
                    </label>
                    <input
                      type="text"
                      className="input"
                      placeholder="itechsmart_workflow"
                      defaultValue="itechsmart_workflow"
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <div>
                      <p className="font-medium text-yellow-800">Backup Database</p>
                      <p className="text-sm text-yellow-700">Create a backup of your database</p>
                    </div>
                    <button className="btn-secondary">
                      Backup Now
                    </button>
                  </div>

                  <button className="btn-primary">
                    Save Configuration
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'performance' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-800">Performance Settings</h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Max Concurrent Executions
                    </label>
                    <input
                      type="number"
                      className="input"
                      placeholder="10"
                      defaultValue="10"
                    />
                    <p className="text-sm text-gray-600 mt-1">
                      Maximum number of workflows that can run simultaneously
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Execution Timeout (seconds)
                    </label>
                    <input
                      type="number"
                      className="input"
                      placeholder="300"
                      defaultValue="300"
                    />
                    <p className="text-sm text-gray-600 mt-1">
                      Maximum time a workflow can run before timing out
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Retry Attempts
                    </label>
                    <input
                      type="number"
                      className="input"
                      placeholder="3"
                      defaultValue="3"
                    />
                    <p className="text-sm text-gray-600 mt-1">
                      Number of times to retry failed tasks
                    </p>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-800">Enable Caching</p>
                      <p className="text-sm text-gray-600">Cache workflow results for faster execution</p>
                    </div>
                    <input type="checkbox" className="w-5 h-5" defaultChecked />
                  </div>

                  <button className="btn-primary">
                    Save Settings
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'general' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-800">General Settings</h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Application Name
                    </label>
                    <input
                      type="text"
                      className="input"
                      placeholder="iTechSmart Workflow"
                      defaultValue="iTechSmart Workflow"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Timezone
                    </label>
                    <select className="input">
                      <option>UTC</option>
                      <option>America/New_York</option>
                      <option>America/Los_Angeles</option>
                      <option>Europe/London</option>
                      <option>Asia/Tokyo</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date Format
                    </label>
                    <select className="input">
                      <option>MM/DD/YYYY</option>
                      <option>DD/MM/YYYY</option>
                      <option>YYYY-MM-DD</option>
                    </select>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-800">Dark Mode</p>
                      <p className="text-sm text-gray-600">Enable dark mode interface</p>
                    </div>
                    <input type="checkbox" className="w-5 h-5" />
                  </div>

                  <button className="btn-primary">
                    Save Settings
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;