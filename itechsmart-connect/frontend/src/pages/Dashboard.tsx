import { Activity, Key, Zap, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  // Mock data
  const stats = [
    { label: 'Total APIs', value: '24', change: '+12%', icon: Activity, color: 'blue' },
    { label: 'API Keys', value: '156', change: '+8%', icon: Key, color: 'green' },
    { label: 'Requests Today', value: '45.2K', change: '+23%', icon: Zap, color: 'purple' },
    { label: 'Success Rate', value: '99.8%', change: '+0.2%', icon: TrendingUp, color: 'emerald' },
  ];

  const requestData = [
    { time: '00:00', requests: 1200 },
    { time: '04:00', requests: 800 },
    { time: '08:00', requests: 2400 },
    { time: '12:00', requests: 3200 },
    { time: '16:00', requests: 2800 },
    { time: '20:00', requests: 1600 },
  ];

  const statusData = [
    { name: '2xx Success', value: 45000, color: '#10b981' },
    { name: '4xx Client Error', value: 80, color: '#f59e0b' },
    { name: '5xx Server Error', value: 20, color: '#ef4444' },
  ];

  const topAPIs = [
    { name: 'User Authentication API', requests: 12500, status: 'healthy' },
    { name: 'Payment Processing API', requests: 8200, status: 'healthy' },
    { name: 'Data Analytics API', requests: 6800, status: 'warning' },
    { name: 'Notification Service API', requests: 5400, status: 'healthy' },
    { name: 'File Storage API', requests: 4200, status: 'healthy' },
  ];

  const recentActivity = [
    { action: 'New API created', api: 'Inventory Management API', time: '5 minutes ago', type: 'success' },
    { action: 'API key generated', api: 'Mobile App v2', time: '12 minutes ago', type: 'info' },
    { action: 'Rate limit exceeded', api: 'Search API', time: '25 minutes ago', type: 'warning' },
    { action: 'API updated', api: 'User Authentication API', time: '1 hour ago', type: 'success' },
    { action: 'Webhook configured', api: 'Payment Processing API', time: '2 hours ago', type: 'info' },
  ];

  const getStatColor = (color: string) => {
    const colors: Record<string, string> = {
      blue: 'bg-blue-500',
      green: 'bg-green-500',
      purple: 'bg-purple-500',
      emerald: 'bg-emerald-500',
    };
    return colors[color] || 'bg-gray-500';
  };

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-sm text-gray-600">
          Monitor your API performance and usage in real-time
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className={`flex-shrink-0 ${getStatColor(stat.color)} rounded-md p-3`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">{stat.label}</dt>
                      <dd className="flex items-baseline">
                        <div className="text-2xl font-semibold text-gray-900">{stat.value}</div>
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

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Request Timeline */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Request Timeline (24h)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={requestData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="requests" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Status Distribution */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Response Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top APIs and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top APIs */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Top APIs by Requests</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {topAPIs.map((api, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <span className="text-sm font-medium text-gray-900">{api.name}</span>
                      {api.status === 'healthy' ? (
                        <CheckCircle className="ml-2 w-4 h-4 text-green-500" />
                      ) : (
                        <AlertCircle className="ml-2 w-4 h-4 text-yellow-500" />
                      )}
                    </div>
                    <div className="mt-1 flex items-center">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${(api.requests / 12500) * 100}%` }}
                        />
                      </div>
                      <span className="ml-3 text-sm text-gray-500">{api.requests.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
          </div>
          <div className="p-6">
            <div className="flow-root">
              <ul className="-mb-8">
                {recentActivity.map((activity, index) => (
                  <li key={index}>
                    <div className="relative pb-8">
                      {index !== recentActivity.length - 1 && (
                        <span
                          className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                          aria-hidden="true"
                        />
                      )}
                      <div className="relative flex space-x-3">
                        <div>
                          <span
                            className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${
                              activity.type === 'success'
                                ? 'bg-green-500'
                                : activity.type === 'warning'
                                ? 'bg-yellow-500'
                                : 'bg-blue-500'
                            }`}
                          >
                            <Activity className="h-4 w-4 text-white" />
                          </span>
                        </div>
                        <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                          <div>
                            <p className="text-sm text-gray-900">{activity.action}</p>
                            <p className="text-sm text-gray-500">{activity.api}</p>
                          </div>
                          <div className="whitespace-nowrap text-right text-sm text-gray-500">
                            {activity.time}
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;