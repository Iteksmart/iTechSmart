import React from 'react';
import { Activity, AlertCircle, CheckCircle, Clock, TrendingUp, TrendingDown } from 'lucide-react';

const Monitoring: React.FC = () => {
  const metrics = [
    {
      name: 'Active Pipelines',
      value: '45',
      change: '+8%',
      trend: 'up',
      icon: Activity
    },
    {
      name: 'Success Rate',
      value: '99.2%',
      change: '+2.1%',
      trend: 'up',
      icon: CheckCircle
    },
    {
      name: 'Avg Latency',
      value: '150ms',
      change: '-12%',
      trend: 'down',
      icon: Clock
    },
    {
      name: 'Error Rate',
      value: '0.8%',
      change: '-0.3%',
      trend: 'down',
      icon: AlertCircle
    }
  ];

  const recentAlerts = [
    {
      id: 1,
      type: 'warning',
      message: 'Pipeline "Sales Analytics" running slower than usual',
      time: '5 minutes ago'
    },
    {
      id: 2,
      type: 'info',
      message: 'New connector "Shopify" successfully configured',
      time: '15 minutes ago'
    },
    {
      id: 3,
      type: 'success',
      message: 'Pipeline "Customer Data Sync" completed successfully',
      time: '30 minutes ago'
    }
  ];

  const systemHealth = [
    { name: 'API Server', status: 'healthy', uptime: '99.9%' },
    { name: 'Database', status: 'healthy', uptime: '99.8%' },
    { name: 'Redis Cache', status: 'healthy', uptime: '99.9%' },
    { name: 'Kafka', status: 'healthy', uptime: '99.7%' },
    { name: 'MinIO Storage', status: 'healthy', uptime: '99.9%' }
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Monitoring</h1>
        <p className="mt-2 text-sm text-gray-600">
          Real-time monitoring and system health
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          const TrendIcon = metric.trend === 'up' ? TrendingUp : TrendingDown;
          const trendColor = metric.trend === 'up' ? 'text-green-600' : 'text-red-600';
          
          return (
            <div
              key={metric.name}
              className="bg-white overflow-hidden shadow rounded-lg"
            >
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Icon className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        {metric.name}
                      </dt>
                      <dd className="flex items-baseline">
                        <div className="text-2xl font-semibold text-gray-900">
                          {metric.value}
                        </div>
                        <div className={`ml-2 flex items-baseline text-sm font-semibold ${trendColor}`}>
                          <TrendIcon className="h-4 w-4 mr-1" />
                          {metric.change}
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

      {/* System Health */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">System Health</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {systemHealth.map((system) => (
            <div key={system.name} className="px-6 py-4 flex items-center justify-between">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                <div>
                  <h3 className="text-sm font-medium text-gray-900">{system.name}</h3>
                  <p className="text-sm text-gray-500">Uptime: {system.uptime}</p>
                </div>
              </div>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                {system.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Recent Alerts</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {recentAlerts.map((alert) => {
            const alertColors = {
              warning: 'bg-yellow-100 text-yellow-800',
              info: 'bg-blue-100 text-blue-800',
              success: 'bg-green-100 text-green-800'
            };
            
            return (
              <div key={alert.id} className="px-6 py-4">
                <div className="flex items-start">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${alertColors[alert.type as keyof typeof alertColors]}`}>
                    {alert.type}
                  </span>
                  <div className="ml-3 flex-1">
                    <p className="text-sm text-gray-900">{alert.message}</p>
                    <p className="mt-1 text-xs text-gray-500">{alert.time}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Performance Chart Placeholder */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">
          Performance Over Time
        </h2>
        <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
          <p className="text-gray-500">Chart visualization would go here</p>
        </div>
      </div>
    </div>
  );
};

export default Monitoring;