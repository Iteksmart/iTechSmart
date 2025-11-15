import { BarChart3, TrendingUp, Users, Activity } from 'lucide-react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const mockData = [
  { name: 'Mon', messages: 120, patients: 45, connections: 5 },
  { name: 'Tue', messages: 150, patients: 52, connections: 5 },
  { name: 'Wed', messages: 180, patients: 61, connections: 6 },
  { name: 'Thu', messages: 140, patients: 48, connections: 6 },
  { name: 'Fri', messages: 200, patients: 70, connections: 6 },
  { name: 'Sat', messages: 90, patients: 30, connections: 5 },
  { name: 'Sun', messages: 80, patients: 25, connections: 5 },
]

export default function Analytics() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Analytics & Reporting
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          System performance and usage analytics
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {[
          {
            name: 'Total Messages',
            value: '12,345',
            change: '+12.5%',
            icon: Activity,
            color: 'text-primary-600',
          },
          {
            name: 'Active Patients',
            value: '1,234',
            change: '+8.2%',
            icon: Users,
            color: 'text-success-600',
          },
          {
            name: 'Avg Response Time',
            value: '45ms',
            change: '-5.1%',
            icon: TrendingUp,
            color: 'text-warning-600',
          },
          {
            name: 'Success Rate',
            value: '99.8%',
            change: '+0.3%',
            icon: BarChart3,
            color: 'text-danger-600',
          },
        ].map((metric) => (
          <div key={metric.name} className="card p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {metric.name}
                </p>
                <p className="mt-1 text-2xl font-semibold text-gray-900 dark:text-gray-100">
                  {metric.value}
                </p>
                <p className="mt-1 text-sm text-success-600">{metric.change}</p>
              </div>
              <metric.icon className={`h-8 w-8 ${metric.color}`} />
            </div>
          </div>
        ))}
      </div>

      {/* Message Volume Chart */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          Message Volume (Last 7 Days)
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={mockData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="messages"
              stroke="#3b82f6"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Activity Chart */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          System Activity
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={mockData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="patients" fill="#22c55e" />
            <Bar dataKey="connections" fill="#f59e0b" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Top Connections */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          Top Connections by Usage
        </h3>
        <div className="space-y-4">
          {[
            { name: 'Epic Main', messages: 5234, percentage: 42 },
            { name: 'Cerner Main', messages: 3456, percentage: 28 },
            { name: 'Meditech Main', messages: 2345, percentage: 19 },
            { name: 'Allscripts Main', messages: 1310, percentage: 11 },
          ].map((connection) => (
            <div key={connection.name}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {connection.name}
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {connection.messages} messages
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full"
                  style={{ width: `${connection.percentage}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}