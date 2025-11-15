import { useState } from 'react';
import { Plus, Copy, Eye, EyeOff, Trash2, Calendar, Shield } from 'lucide-react';

const APIKeys = () => {
  const [showKey, setShowKey] = useState<string | null>(null);

  // Mock data
  const apiKeys = [
    {
      id: '1',
      name: 'Production Mobile App',
      key: 'sk_live_4eC39HqLyjWDarjtT1zdp7dc',
      scopes: ['read', 'write'],
      created: '2024-01-10',
      lastUsed: '2 hours ago',
      expires: '2024-12-31',
      status: 'active',
      requests: 45200,
    },
    {
      id: '2',
      name: 'Development Environment',
      key: 'sk_test_51HqLyjWDarjtT1zdp7dcXYZ',
      scopes: ['read'],
      created: '2024-01-05',
      lastUsed: '5 minutes ago',
      expires: '2024-06-30',
      status: 'active',
      requests: 12800,
    },
    {
      id: '3',
      name: 'Partner Integration',
      key: 'sk_live_9fB28GpMklNEbrstU2aep8ef',
      scopes: ['read', 'write', 'admin'],
      created: '2023-12-15',
      lastUsed: '1 day ago',
      expires: '2025-12-31',
      status: 'active',
      requests: 89500,
    },
    {
      id: '4',
      name: 'Legacy System',
      key: 'sk_live_7dA19FoJhiMCdqsuV3bfq9gh',
      scopes: ['read'],
      created: '2023-06-20',
      lastUsed: '30 days ago',
      expires: '2024-03-31',
      status: 'expiring',
      requests: 5200,
    },
    {
      id: '5',
      name: 'Testing Key',
      key: 'sk_test_3cZ08EqKghLBcpqrS1ydo6cd',
      scopes: ['read', 'write'],
      created: '2023-11-01',
      lastUsed: 'Never',
      expires: '2024-02-28',
      status: 'revoked',
      requests: 0,
    },
  ];

  const maskKey = (key: string) => {
    return `${key.substring(0, 12)}${'*'.repeat(20)}${key.substring(key.length - 4)}`;
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // You could add a toast notification here
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'expiring':
        return 'bg-yellow-100 text-yellow-800';
      case 'revoked':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getScopeColor = (scope: string) => {
    switch (scope) {
      case 'admin':
        return 'bg-purple-100 text-purple-800';
      case 'write':
        return 'bg-blue-100 text-blue-800';
      case 'read':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">API Keys</h1>
            <p className="mt-2 text-sm text-gray-600">
              Manage API keys for authentication and access control
            </p>
          </div>
          <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
            <Plus className="w-5 h-5 mr-2" />
            Generate New Key
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3 mb-8">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-500 rounded-md p-3">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Active Keys</dt>
                  <dd className="text-2xl font-semibold text-gray-900">3</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-yellow-500 rounded-md p-3">
                <Calendar className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Expiring Soon</dt>
                  <dd className="text-2xl font-semibold text-gray-900">1</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-purple-500 rounded-md p-3">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Requests</dt>
                  <dd className="text-2xl font-semibold text-gray-900">152.7K</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* API Keys List */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Your API Keys</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {apiKeys.map((apiKey) => (
            <div key={apiKey.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center">
                    <h4 className="text-lg font-medium text-gray-900">{apiKey.name}</h4>
                    <span className={`ml-3 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(apiKey.status)}`}>
                      {apiKey.status}
                    </span>
                  </div>
                  
                  <div className="mt-3 flex items-center space-x-2">
                    <code className="px-3 py-2 bg-gray-100 rounded text-sm font-mono text-gray-800">
                      {showKey === apiKey.id ? apiKey.key : maskKey(apiKey.key)}
                    </code>
                    <button
                      onClick={() => setShowKey(showKey === apiKey.id ? null : apiKey.id)}
                      className="p-2 text-gray-400 hover:text-gray-600 rounded hover:bg-gray-100"
                    >
                      {showKey === apiKey.id ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                    <button
                      onClick={() => copyToClipboard(apiKey.key)}
                      className="p-2 text-gray-400 hover:text-gray-600 rounded hover:bg-gray-100"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="mt-4 flex flex-wrap gap-2">
                    {apiKey.scopes.map((scope) => (
                      <span
                        key={scope}
                        className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${getScopeColor(scope)}`}
                      >
                        {scope}
                      </span>
                    ))}
                  </div>

                  <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Created</p>
                      <p className="mt-1 font-medium text-gray-900">{apiKey.created}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Last Used</p>
                      <p className="mt-1 font-medium text-gray-900">{apiKey.lastUsed}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Expires</p>
                      <p className="mt-1 font-medium text-gray-900">{apiKey.expires}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Requests</p>
                      <p className="mt-1 font-medium text-gray-900">{apiKey.requests.toLocaleString()}</p>
                    </div>
                  </div>
                </div>

                <div className="ml-4">
                  <button className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded">
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Security Notice */}
      <div className="mt-6 bg-yellow-50 border-l-4 border-yellow-400 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <Shield className="h-5 w-5 text-yellow-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">Security Best Practices</h3>
            <div className="mt-2 text-sm text-yellow-700">
              <ul className="list-disc list-inside space-y-1">
                <li>Never share your API keys publicly or commit them to version control</li>
                <li>Rotate keys regularly and revoke unused keys</li>
                <li>Use different keys for different environments (development, staging, production)</li>
                <li>Monitor key usage and set up alerts for suspicious activity</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default APIKeys;