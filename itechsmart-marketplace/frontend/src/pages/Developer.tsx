import { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Eye, DollarSign, Download, Star, TrendingUp } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface App {
  id: number;
  name: string;
  status: string;
  version: string;
  total_downloads: number;
  total_revenue: number;
  average_rating: number;
  total_reviews: number;
}

interface DeveloperStats {
  total_apps: number;
  total_downloads: number;
  total_revenue: number;
  average_rating: number;
  total_reviews: number;
  active_users: number;
}

export default function Developer() {
  const [apps, setApps] = useState<App[]>([]);
  const [stats, setStats] = useState<DeveloperStats | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [activeTab, setActiveTab] = useState<'apps' | 'analytics' | 'profile'>('apps');

  useEffect(() => {
    loadApps();
    loadStats();
  }, []);

  const loadApps = () => {
    const mockApps: App[] = [
      {
        id: 1,
        name: 'DataFlow Pro',
        status: 'approved',
        version: '2.5.0',
        total_downloads: 15420,
        total_revenue: 154200,
        average_rating: 4.8,
        total_reviews: 342
      },
      {
        id: 2,
        name: 'Analytics Dashboard',
        status: 'approved',
        version: '1.8.2',
        total_downloads: 8920,
        total_revenue: 71360,
        average_rating: 4.6,
        total_reviews: 189
      },
      {
        id: 3,
        name: 'API Gateway',
        status: 'pending_review',
        version: '1.0.0',
        total_downloads: 0,
        total_revenue: 0,
        average_rating: 0,
        total_reviews: 0
      }
    ];
    setApps(mockApps);
  };

  const loadStats = () => {
    const mockStats: DeveloperStats = {
      total_apps: 3,
      total_downloads: 24340,
      total_revenue: 225560,
      average_rating: 4.7,
      total_reviews: 531,
      active_users: 18420
    };
    setStats(mockStats);
  };

  const revenueData = [
    { month: 'Jan', revenue: 18500 },
    { month: 'Feb', revenue: 22300 },
    { month: 'Mar', revenue: 28900 },
    { month: 'Apr', revenue: 31200 },
    { month: 'May', revenue: 35800 },
    { month: 'Jun', revenue: 42100 }
  ];

  const downloadsData = [
    { month: 'Jan', downloads: 2100 },
    { month: 'Feb', downloads: 2800 },
    { month: 'Mar', downloads: 3500 },
    { month: 'Apr', downloads: 4200 },
    { month: 'May', downloads: 5100 },
    { month: 'Jun', downloads: 6600 }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-700';
      case 'pending_review':
        return 'bg-yellow-100 text-yellow-700';
      case 'rejected':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Developer Dashboard</h1>
          <p className="text-gray-600">Manage your apps and track performance</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Create New App
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <span className="text-green-600 text-sm font-semibold">+12.5%</span>
            </div>
            <div className="text-2xl font-bold mb-1">{stats.total_apps}</div>
            <div className="text-gray-600 text-sm">Total Apps</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-green-100 rounded-lg">
                <Download className="w-6 h-6 text-green-600" />
              </div>
              <span className="text-green-600 text-sm font-semibold">+18.2%</span>
            </div>
            <div className="text-2xl font-bold mb-1">{stats.total_downloads.toLocaleString()}</div>
            <div className="text-gray-600 text-sm">Total Downloads</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-100 rounded-lg">
                <DollarSign className="w-6 h-6 text-purple-600" />
              </div>
              <span className="text-green-600 text-sm font-semibold">+24.8%</span>
            </div>
            <div className="text-2xl font-bold mb-1">${stats.total_revenue.toLocaleString()}</div>
            <div className="text-gray-600 text-sm">Total Revenue</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-yellow-100 rounded-lg">
                <Star className="w-6 h-6 text-yellow-600" />
              </div>
              <span className="text-green-600 text-sm font-semibold">+0.3</span>
            </div>
            <div className="text-2xl font-bold mb-1">{stats.average_rating}</div>
            <div className="text-gray-600 text-sm">Average Rating</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="border-b">
          <div className="flex">
            <button
              onClick={() => setActiveTab('apps')}
              className={`px-6 py-4 font-semibold transition ${
                activeTab === 'apps'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              My Apps
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`px-6 py-4 font-semibold transition ${
                activeTab === 'analytics'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              Analytics
            </button>
            <button
              onClick={() => setActiveTab('profile')}
              className={`px-6 py-4 font-semibold transition ${
                activeTab === 'profile'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              Developer Profile
            </button>
          </div>
        </div>

        <div className="p-6">
          {activeTab === 'apps' && (
            <div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4">App Name</th>
                      <th className="text-left py-3 px-4">Status</th>
                      <th className="text-left py-3 px-4">Version</th>
                      <th className="text-right py-3 px-4">Downloads</th>
                      <th className="text-right py-3 px-4">Revenue</th>
                      <th className="text-right py-3 px-4">Rating</th>
                      <th className="text-right py-3 px-4">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {apps.map(app => (
                      <tr key={app.id} className="border-b hover:bg-gray-50">
                        <td className="py-4 px-4 font-semibold">{app.name}</td>
                        <td className="py-4 px-4">
                          <span className={`px-3 py-1 rounded-full text-sm ${getStatusColor(app.status)}`}>
                            {app.status.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-gray-600">{app.version}</td>
                        <td className="py-4 px-4 text-right">{app.total_downloads.toLocaleString()}</td>
                        <td className="py-4 px-4 text-right font-semibold">${app.total_revenue.toLocaleString()}</td>
                        <td className="py-4 px-4 text-right">
                          <div className="flex items-center justify-end gap-1">
                            <Star className="w-4 h-4 text-yellow-500 fill-current" />
                            <span>{app.average_rating || 'N/A'}</span>
                          </div>
                        </td>
                        <td className="py-4 px-4">
                          <div className="flex items-center justify-end gap-2">
                            <button className="p-2 text-blue-600 hover:bg-blue-50 rounded">
                              <Eye className="w-4 h-4" />
                            </button>
                            <button className="p-2 text-gray-600 hover:bg-gray-100 rounded">
                              <Edit className="w-4 h-4" />
                            </button>
                            <button className="p-2 text-red-600 hover:bg-red-50 rounded">
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="space-y-8">
              <div>
                <h3 className="text-xl font-bold mb-4">Revenue Trend</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={revenueData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div>
                <h3 className="text-xl font-bold mb-4">Downloads Trend</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={downloadsData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="downloads" fill="#10b981" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {activeTab === 'profile' && (
            <div className="max-w-2xl">
              <h3 className="text-xl font-bold mb-6">Developer Profile</h3>
              <form className="space-y-6">
                <div>
                  <label className="block text-sm font-semibold mb-2">Company Name</label>
                  <input
                    type="text"
                    defaultValue="iTechSmart Inc."
                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2">Support Email</label>
                  <input
                    type="email"
                    defaultValue="support@itechsmart.com"
                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2">Support URL</label>
                  <input
                    type="url"
                    defaultValue="https://support.itechsmart.com"
                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2">Phone</label>
                  <input
                    type="tel"
                    defaultValue="+1 (555) 123-4567"
                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2">Address</label>
                  <textarea
                    rows={3}
                    defaultValue="123 Tech Street, San Francisco, CA 94105"
                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2">Tax ID</label>
                  <input
                    type="text"
                    defaultValue="12-3456789"
                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="flex gap-4">
                  <button
                    type="submit"
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
                  >
                    Save Changes
                  </button>
                  <button
                    type="button"
                    className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      </div>

      {/* Create App Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">Create New App</h2>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-semibold mb-2">App Name</label>
                <input
                  type="text"
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter app name"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Tagline</label>
                <input
                  type="text"
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Short description"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Description</label>
                <textarea
                  rows={4}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Detailed description"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Category</label>
                <select className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>Data Integration</option>
                  <option>Security</option>
                  <option>Analytics</option>
                  <option>API Management</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Price</label>
                <input
                  type="number"
                  step="0.01"
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                />
              </div>

              <div className="flex gap-4">
                <button
                  type="submit"
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
                >
                  Create App
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}