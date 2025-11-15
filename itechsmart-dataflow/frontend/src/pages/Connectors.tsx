import React from 'react';
import { Database, Cloud, ShoppingCart, Activity } from 'lucide-react';

const Connectors: React.FC = () => {
  const connectors = [
    {
      id: 'postgresql',
      name: 'PostgreSQL',
      type: 'Database',
      category: 'source',
      icon: Database,
      color: 'blue',
      supported: true
    },
    {
      id: 'mysql',
      name: 'MySQL',
      type: 'Database',
      category: 'source',
      icon: Database,
      color: 'orange',
      supported: true
    },
    {
      id: 'mongodb',
      name: 'MongoDB',
      type: 'Database',
      category: 'source',
      icon: Database,
      color: 'green',
      supported: true
    },
    {
      id: 'salesforce',
      name: 'Salesforce',
      type: 'SaaS',
      category: 'source',
      icon: Cloud,
      color: 'blue',
      supported: true
    },
    {
      id: 'stripe',
      name: 'Stripe',
      type: 'SaaS',
      category: 'source',
      icon: ShoppingCart,
      color: 'purple',
      supported: true
    },
    {
      id: 's3',
      name: 'Amazon S3',
      type: 'Storage',
      category: 'destination',
      icon: Cloud,
      color: 'orange',
      supported: true
    },
    {
      id: 'snowflake',
      name: 'Snowflake',
      type: 'Warehouse',
      category: 'destination',
      icon: Database,
      color: 'blue',
      supported: true
    },
    {
      id: 'hl7',
      name: 'HL7 FHIR',
      type: 'Healthcare',
      category: 'source',
      icon: Activity,
      color: 'red',
      supported: true
    }
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Connectors</h1>
        <p className="mt-2 text-sm text-gray-600">
          Browse and configure 100+ data connectors
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="text-sm font-medium text-gray-500">Total Connectors</div>
            <div className="mt-1 text-3xl font-semibold text-gray-900">100+</div>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="text-sm font-medium text-gray-500">Databases</div>
            <div className="mt-1 text-3xl font-semibold text-gray-900">25</div>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="text-sm font-medium text-gray-500">SaaS Apps</div>
            <div className="mt-1 text-3xl font-semibold text-gray-900">50</div>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="text-sm font-medium text-gray-500">Cloud Storage</div>
            <div className="mt-1 text-3xl font-semibold text-gray-900">15</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="flex space-x-4">
          <select className="block w-48 pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md">
            <option>All Categories</option>
            <option>Databases</option>
            <option>SaaS</option>
            <option>Storage</option>
            <option>Warehouse</option>
          </select>
          <select className="block w-48 pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md">
            <option>All Types</option>
            <option>Source</option>
            <option>Destination</option>
            <option>Both</option>
          </select>
          <input
            type="text"
            placeholder="Search connectors..."
            className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
          />
        </div>
      </div>

      {/* Connectors Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {connectors.map((connector) => {
          const Icon = connector.icon;
          return (
            <div
              key={connector.id}
              className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow cursor-pointer"
            >
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div className={`flex-shrink-0 bg-${connector.color}-100 rounded-md p-3`}>
                    <Icon className={`h-6 w-6 text-${connector.color}-600`} />
                  </div>
                  {connector.supported && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Supported
                    </span>
                  )}
                </div>
                <div className="mt-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    {connector.name}
                  </h3>
                  <p className="mt-1 text-sm text-gray-500">{connector.type}</p>
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      {connector.category}
                    </span>
                  </div>
                </div>
                <div className="mt-4">
                  <button className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200">
                    Configure
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* More Connectors */}
      <div className="bg-white shadow rounded-lg p-6 text-center">
        <h3 className="text-lg font-medium text-gray-900">
          Need a specific connector?
        </h3>
        <p className="mt-2 text-sm text-gray-500">
          We support 100+ connectors. Contact us to request a new connector.
        </p>
        <button className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
          Request Connector
        </button>
      </div>
    </div>
  );
};

export default Connectors;