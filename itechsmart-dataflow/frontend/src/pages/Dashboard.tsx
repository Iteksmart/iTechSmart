import React from 'react';
import { Activity, Database, CheckCircle, XCircle, Clock, TrendingUp } from 'lucide-react';

const Dashboard: React.FC = () => {
  const stats = [
    {
      name: 'Total Pipelines',
      value: '50',
      change: '+12%',
      icon: Database,
      color: 'blue'
    },
    {
      name: 'Active Pipelines',
      value: '45',
      change: '+8%',
      icon: Activity,
      color: 'green'
    },
    {
      name: 'Success Rate',
      value: '99.2%',
      change: '+2.1%',
      icon: CheckCircle,
      color: 'emerald'
    },
    {
      name: 'Records Processed',
      value: '10M',
      change: '+25%',
      icon: TrendingUp,
      color: 'purple'
    }
  ];

  const recentPipelines = [
    {
      id: 'pipeline-001',
      name: 'Customer Data Sync',
      status: 'running',
      lastRun: '2 minutes ago',
      records: '125,000'
    },
    {
      id: 'pipeline-002',
      name: 'HL7 Healthcare Data',
      status: 'completed',
      lastRun: '15 minutes ago',
      records: '50,000'
    },
    {
      id: 'pipeline-003',
      name: 'Sales Analytics',
      status: 'running',
      lastRun: '5 minutes ago',
      records: '75,000'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-sm text-gray-600">
          Overview of your data pipelines and ETL operations
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.name}
              className="bg-white overflow-hidden shadow rounded-lg"
            >
              <div className="p-5">
                <div className="flex items-center">
                  <div className={`flex-shrink-0 bg-${stat.color}-100 rounded-md p-3`}>
                    <Icon className={`h-6 w-6 text-${stat.color}-600`} />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        {stat.name}
                      </dt>
                      <dd className="flex items-baseline">
                        <div className="text-2xl font-semibold text-gray-900">
                          {stat.value}
                        </div>
                        <div className="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                          {stat.change}
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Pipelines */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Recent Pipeline Runs</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {recentPipelines.map((pipeline) => (
            <div key={pipeline.id} className="px-6 py-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="text-sm font-medium text-gray-900">
                    {pipeline.name}
                  </h3>
                  <p className="text-sm text-gray-500">
                    Last run: {pipeline.lastRun} • {pipeline.records} records
                  </p>
                </div>
                <div className="ml-4">
                  {pipeline.status === 'running' ? (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      <Clock className="h-3 w-3 mr-1" />
                      Running
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Completed
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Integration Status */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">
            iTechSmart Platform Integrations
          </h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { name: 'ImpactOS', status: 'connected' },
              { name: 'HL7', status: 'connected' },
              { name: 'Passport', status: 'connected' },
              { name: 'Enterprise Hub', status: 'connected' },
              { name: 'Ninja', status: 'connected' },
              { name: 'Pulse', status: 'pending' }
            ].map((integration) => (
              <div
                key={integration.name}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
              >
                <span className="text-sm font-medium text-gray-900">
                  {integration.name}
                </span>
                {integration.status === 'connected' ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : (
                  <Clock className="h-5 w-5 text-yellow-500" />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;