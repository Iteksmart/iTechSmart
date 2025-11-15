import { BarChart, Bar, LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, Activity, Clock, AlertCircle } from 'lucide-react';

const Analytics = () => {
  // Mock data
  const requestTrend = [
    { date: '2024-01-08', requests: 38000, errors: 120 },
    { date: '2024-01-09', requests: 42000, errors: 95 },
    { date: '2024-01-10', requests: 45000, errors: 110 },
    { date: '2024-01-11', requests: 41000, errors: 88 },
    { date: '2024-01-12', requests: 48000, errors: 102 },
    { date: '2024-01-13', requests: 52000, errors: 78 },
    { date: '2024-01-14', requests: 49000, errors: 92 },
  ];

  const responseTimeData = [
    { time: '00:00', p50: 45, p95: 120, p99: 250 },
    { time: '04:00', p50: 38, p95: 95, p99: 180 },
    { time: '08:00', p50: 52, p95: 145, p99: 320 },
    { time: '12:00', p50: 68, p95: 180, p99: 420 },
    { time: '16:00', p50: 55, p95: 150, p99: 350 },
    { time: '20:00', p50: 42, p95: 110, p99: 240 },
  ];

  const endpointPerformance = [
    { endpoint: '/api/auth/login', requests: 15200, avgTime: 45, errors: 12 },
    { endpoint: '/api/users/profile', requests: 12800, avgTime: 38, errors: 8 },
    { endpoint: '/api/payment/process', requests: 8500, avgTime: 125, errors: 45 },
    { endpoint: '/api/data/query', requests: 6200, avgTime: 220, errors: 18 },
    { endpoint: '/api/files/upload', requests: 4800, avgTime: 380, errors: 32 },
  ];

  const statusDistribution = [
    { name: '2xx Success', value: 45000, color: '#10b981' },
    { name: '3xx Redirect', value: 2500, color: '#3b82f6' },
    { name: '4xx Client Error', value: 180, color: '#f59e0b' },
    { name: '5xx Server Error', value: 45, color: '#ef4444' },
  ];

  const geographicData = [
    { region: 'North America', requests: 18500, percentage: 38.8 },
    { region: 'Europe', requests: 14200, percentage: 29.8 },
    { region: 'Asia Pacific', requests: 10800, percentage: 22.6 },
    { region: 'South America', requests: 2800, percentage: 5.9 },
    { region: 'Africa', requests: 1400, percentage: 2.9 },
  ];

  const metrics = [
    {
      label: 'Total Requests',
      value: '47.7K',
      change: '+12.5%',
      trend: 'up',
      icon: Activity,
    },
    {
      label: 'Avg Response Time',
      value: '52ms',
      change: '-8.2%',
      trend: 'down',
      icon: Clock,
    },
    {
      label: 'Error Rate',
      value: '0.19%',
      change: '-0.05%',
      trend: 'down',
      icon: AlertCircle,
    },
    {
      label: 'Success Rate',
      value: '99.81%',
      change: '+0.05%',
      trend: 'up',
      icon: TrendingUp,
    },
  ];

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <p className="mt-2 text-sm text-gray-600">
          Detailed insights into your API performance and usage
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <div key={metric.label} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Icon className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">{metric.label}</dt>
                      <dd className="flex items-baseline">
                        <div className="text-2xl font-semibold text-gray-900">{metric.value}</div>
                        <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                          metric.trend === 'up' ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {metric.trend === 'up' ? (
                            <TrendingUp className="w-4 h-4 mr-1" />
                          ) : (
                            <TrendingDown className="w-4 h-4 mr-1" />
                          )}
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

      {/* Request Trend */}
      <div className="bg-white shadow rounded-lg p-6 mb-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Request Trend (7 Days)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={requestTrend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Area type="monotone" dataKey="requests" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
            <Area type="monotone" dataKey="errors" stackId="2" stroke="#ef4444" fill="#ef4444" fillOpacity={0.6} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Response Time and Status Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Response Time */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Response Time Percentiles</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={responseTimeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="p50" stroke="#10b981" strokeWidth={2} name="P50 (Median)" />
              <Line type="monotone" dataKey="p95" stroke="#f59e0b" strokeWidth={2} name="P95" />
              <Line type="monotone" dataKey="p99" stroke="#ef4444" strokeWidth={2} name="P99" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Status Distribution */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Status Code Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {statusDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Endpoint Performance */}
      <div className="bg-white shadow rounded-lg mb-8">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Top Endpoints by Traffic</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Endpoint
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Requests
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Time (ms)
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Errors
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Error Rate
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {endpointPerformance.map((endpoint, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {endpoint.endpoint}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {endpoint.requests.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {endpoint.avgTime}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {endpoint.errors}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      (endpoint.errors / endpoint.requests) * 100 < 0.5
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {((endpoint.errors / endpoint.requests) * 100).toFixed(2)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Geographic Distribution */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Geographic Distribution</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {geographicData.map((region, index) => (
              <div key={index}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-900">{region.region}</span>
                  <span className="text-sm text-gray-500">
                    {region.requests.toLocaleString()} ({region.percentage}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${region.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;