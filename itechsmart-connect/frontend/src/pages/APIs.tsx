import { useState } from 'react';
import { Plus, Search, MoreVertical, Edit, Trash2, Eye, Power, Globe } from 'lucide-react';

const APIs = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  // Mock data
  const apis = [
    {
      id: '1',
      name: 'User Authentication API',
      slug: 'user-auth',
      version: 'v2',
      baseUrl: 'https://api.example.com/auth',
      status: 'active',
      requests: 12500,
      uptime: 99.9,
      lastUpdated: '2024-01-15',
    },
    {
      id: '2',
      name: 'Payment Processing API',
      slug: 'payment',
      version: 'v1',
      baseUrl: 'https://api.example.com/payment',
      status: 'active',
      requests: 8200,
      uptime: 99.8,
      lastUpdated: '2024-01-14',
    },
    {
      id: '3',
      name: 'Data Analytics API',
      slug: 'analytics',
      version: 'v3',
      baseUrl: 'https://api.example.com/analytics',
      status: 'maintenance',
      requests: 6800,
      uptime: 98.5,
      lastUpdated: '2024-01-13',
    },
    {
      id: '4',
      name: 'Notification Service API',
      slug: 'notifications',
      version: 'v1',
      baseUrl: 'https://api.example.com/notify',
      status: 'active',
      requests: 5400,
      uptime: 99.7,
      lastUpdated: '2024-01-12',
    },
    {
      id: '5',
      name: 'File Storage API',
      slug: 'storage',
      version: 'v2',
      baseUrl: 'https://api.example.com/storage',
      status: 'active',
      requests: 4200,
      uptime: 99.9,
      lastUpdated: '2024-01-11',
    },
    {
      id: '6',
      name: 'Search API',
      slug: 'search',
      version: 'v1',
      baseUrl: 'https://api.example.com/search',
      status: 'deprecated',
      requests: 1200,
      uptime: 95.0,
      lastUpdated: '2023-12-20',
    },
  ];

  const filteredAPIs = apis.filter((api) => {
    const matchesSearch =
      api.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      api.slug.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || api.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-800';
      case 'deprecated':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">APIs</h1>
            <p className="mt-2 text-sm text-gray-600">
              Manage and monitor your API endpoints
            </p>
          </div>
          <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
            <Plus className="w-5 h-5 mr-2" />
            Create API
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search APIs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <div>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="maintenance">Maintenance</option>
              <option value="deprecated">Deprecated</option>
            </select>
          </div>
        </div>
      </div>

      {/* APIs Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {filteredAPIs.map((api) => (
          <div key={api.id} className="bg-white shadow rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
            <div className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center">
                    <h3 className="text-lg font-semibold text-gray-900">{api.name}</h3>
                    <span className={`ml-3 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(api.status)}`}>
                      {api.status}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-gray-500">/{api.slug}</p>
                  <div className="mt-2 flex items-center text-sm text-gray-500">
                    <Globe className="w-4 h-4 mr-1" />
                    {api.baseUrl}
                  </div>
                </div>
                <div className="ml-4">
                  <button className="text-gray-400 hover:text-gray-600">
                    <MoreVertical className="w-5 h-5" />
                  </button>
                </div>
              </div>

              <div className="mt-6 grid grid-cols-3 gap-4">
                <div>
                  <p className="text-xs text-gray-500">Version</p>
                  <p className="mt-1 text-sm font-semibold text-gray-900">{api.version}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Requests</p>
                  <p className="mt-1 text-sm font-semibold text-gray-900">{api.requests.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Uptime</p>
                  <p className="mt-1 text-sm font-semibold text-gray-900">{api.uptime}%</p>
                </div>
              </div>

              <div className="mt-6 flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  Updated {api.lastUpdated}
                </span>
                <div className="flex space-x-2">
                  <button className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded">
                    <Eye className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded">
                    <Edit className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded">
                    <Power className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredAPIs.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No APIs found matching your criteria.</p>
        </div>
      )}
    </div>
  );
};

export default APIs;