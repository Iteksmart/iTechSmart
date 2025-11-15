import { useState } from 'react';
import { Book, Code, FileText, Search, ExternalLink } from 'lucide-react';

const Documentation = () => {
  const [selectedAPI, setSelectedAPI] = useState('user-auth');
  const [searchTerm, setSearchTerm] = useState('');

  const apis = [
    { id: 'user-auth', name: 'User Authentication API', version: 'v2' },
    { id: 'payment', name: 'Payment Processing API', version: 'v1' },
    { id: 'analytics', name: 'Data Analytics API', version: 'v3' },
    { id: 'notifications', name: 'Notification Service API', version: 'v1' },
  ];

  const endpoints = [
    {
      method: 'POST',
      path: '/auth/login',
      description: 'Authenticate user and return access token',
      parameters: [
        { name: 'email', type: 'string', required: true, description: 'User email address' },
        { name: 'password', type: 'string', required: true, description: 'User password' },
      ],
      response: {
        success: {
          access_token: 'string',
          token_type: 'string',
          expires_in: 'number',
        },
      },
    },
    {
      method: 'POST',
      path: '/auth/register',
      description: 'Register a new user account',
      parameters: [
        { name: 'email', type: 'string', required: true, description: 'User email address' },
        { name: 'password', type: 'string', required: true, description: 'User password (min 8 characters)' },
        { name: 'name', type: 'string', required: true, description: 'User full name' },
      ],
      response: {
        success: {
          user_id: 'string',
          email: 'string',
          created_at: 'string',
        },
      },
    },
    {
      method: 'GET',
      path: '/auth/profile',
      description: 'Get current user profile',
      parameters: [],
      response: {
        success: {
          user_id: 'string',
          email: 'string',
          name: 'string',
          created_at: 'string',
        },
      },
    },
    {
      method: 'PUT',
      path: '/auth/profile',
      description: 'Update user profile',
      parameters: [
        { name: 'name', type: 'string', required: false, description: 'User full name' },
        { name: 'avatar', type: 'string', required: false, description: 'Avatar URL' },
      ],
      response: {
        success: {
          message: 'string',
          user: 'object',
        },
      },
    },
  ];

  const getMethodColor = (method: string) => {
    switch (method) {
      case 'GET':
        return 'bg-green-100 text-green-800';
      case 'POST':
        return 'bg-blue-100 text-blue-800';
      case 'PUT':
        return 'bg-yellow-100 text-yellow-800';
      case 'DELETE':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">API Documentation</h1>
        <p className="mt-2 text-sm text-gray-600">
          Complete reference for all API endpoints and integration guides
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow rounded-lg p-4 sticky top-4">
            <div className="mb-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9 w-full text-sm rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
            </div>

            <nav className="space-y-1">
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                APIs
              </div>
              {apis.map((api) => (
                <button
                  key={api.id}
                  onClick={() => setSelectedAPI(api.id)}
                  className={`w-full text-left px-3 py-2 text-sm rounded-md ${
                    selectedAPI === api.id
                      ? 'bg-blue-50 text-blue-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span>{api.name}</span>
                    <span className="text-xs text-gray-500">{api.version}</span>
                  </div>
                </button>
              ))}

              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider mt-4">
                Resources
              </div>
              <a href="#" className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md">
                <Book className="w-4 h-4 mr-2" />
                Getting Started
              </a>
              <a href="#" className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md">
                <Code className="w-4 h-4 mr-2" />
                Code Examples
              </a>
              <a href="#" className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md">
                <FileText className="w-4 h-4 mr-2" />
                Changelog
              </a>
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          {/* API Overview */}
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">User Authentication API</h2>
            <p className="text-gray-600 mb-4">
              The User Authentication API provides secure authentication and user management capabilities.
              Use this API to implement login, registration, and profile management in your applications.
            </p>
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center">
                <span className="text-gray-500">Base URL:</span>
                <code className="ml-2 px-2 py-1 bg-gray-100 rounded text-blue-600">
                  https://api.example.com/auth
                </code>
              </div>
              <div className="flex items-center">
                <span className="text-gray-500">Version:</span>
                <span className="ml-2 font-medium">v2</span>
              </div>
            </div>
          </div>

          {/* Authentication */}
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Authentication</h3>
            <p className="text-gray-600 mb-4">
              All API requests require authentication using an API key. Include your API key in the request header:
            </p>
            <div className="bg-gray-900 rounded-lg p-4 mb-4">
              <code className="text-green-400 text-sm">
                Authorization: Bearer YOUR_API_KEY
              </code>
            </div>
            <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
              <p className="text-sm text-blue-700">
                <strong>Note:</strong> Keep your API keys secure and never expose them in client-side code.
              </p>
            </div>
          </div>

          {/* Endpoints */}
          <div className="space-y-6">
            {endpoints.map((endpoint, index) => (
              <div key={index} className="bg-white shadow rounded-lg overflow-hidden">
                <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className={`px-3 py-1 rounded-md text-xs font-semibold ${getMethodColor(endpoint.method)}`}>
                        {endpoint.method}
                      </span>
                      <code className="text-sm font-mono text-gray-900">{endpoint.path}</code>
                    </div>
                    <button className="text-gray-400 hover:text-gray-600">
                      <ExternalLink className="w-4 h-4" />
                    </button>
                  </div>
                  <p className="mt-2 text-sm text-gray-600">{endpoint.description}</p>
                </div>

                <div className="p-6">
                  {/* Parameters */}
                  {endpoint.parameters.length > 0 && (
                    <div className="mb-6">
                      <h4 className="text-sm font-semibold text-gray-900 mb-3">Parameters</h4>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead>
                            <tr>
                              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                Name
                              </th>
                              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                Type
                              </th>
                              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                Required
                              </th>
                              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                Description
                              </th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-200">
                            {endpoint.parameters.map((param, idx) => (
                              <tr key={idx}>
                                <td className="px-3 py-2 text-sm font-mono text-gray-900">{param.name}</td>
                                <td className="px-3 py-2 text-sm text-gray-500">{param.type}</td>
                                <td className="px-3 py-2 text-sm">
                                  {param.required ? (
                                    <span className="text-red-600 font-medium">Yes</span>
                                  ) : (
                                    <span className="text-gray-500">No</span>
                                  )}
                                </td>
                                <td className="px-3 py-2 text-sm text-gray-600">{param.description}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* Request Example */}
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-gray-900 mb-3">Request Example</h4>
                    <div className="bg-gray-900 rounded-lg p-4">
                      <pre className="text-green-400 text-sm overflow-x-auto">
{`curl -X ${endpoint.method} \\
  https://api.example.com${endpoint.path} \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    ${endpoint.parameters.map(p => `"${p.name}": "value"`).join(',\n    ')}
  }'`}
                      </pre>
                    </div>
                  </div>

                  {/* Response Example */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 mb-3">Response Example</h4>
                    <div className="bg-gray-900 rounded-lg p-4">
                      <pre className="text-green-400 text-sm overflow-x-auto">
                        {JSON.stringify(endpoint.response.success, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Rate Limiting */}
          <div className="bg-white shadow rounded-lg p-6 mt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Rate Limiting</h3>
            <p className="text-gray-600 mb-4">
              API requests are rate limited to ensure fair usage and system stability.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="text-2xl font-bold text-blue-600">1,000</div>
                <div className="text-sm text-gray-600">Requests per hour</div>
              </div>
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="text-2xl font-bold text-blue-600">10,000</div>
                <div className="text-sm text-gray-600">Requests per day</div>
              </div>
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="text-2xl font-bold text-blue-600">100,000</div>
                <div className="text-sm text-gray-600">Requests per month</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Documentation;