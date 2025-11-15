import { useQuery } from '@tanstack/react-query'
import {
  Activity,
  Database,
  Users,
  FileText,
  CheckCircle,
  Clock,
} from 'lucide-react'
import { connectionsAPI, healthAPI } from '../lib/api'
import { useWebSocket } from '../lib/websocket'

export default function Dashboard() {
  const { data: connectionStats } = useQuery({
    queryKey: ['connection-stats'],
    queryFn: () => connectionsAPI.stats(),
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  const { data: healthData } = useQuery({
    queryKey: ['health'],
    queryFn: () => healthAPI.detailed(),
    refetchInterval: 10000, // Refetch every 10 seconds
  })

  const { isConnected, lastMessage } = useWebSocket('default')

  const stats = connectionStats?.data || {}

  const statCards = [
    {
      name: 'Active Connections',
      value: stats.active_connections || 0,
      icon: Database,
      color: 'text-primary-600',
      bgColor: 'bg-primary-50 dark:bg-primary-900',
    },
    {
      name: 'Total Connections',
      value: stats.total_connections || 0,
      icon: Activity,
      color: 'text-success-600',
      bgColor: 'bg-success-50 dark:bg-success-900',
    },
    {
      name: 'Patients',
      value: '1,234', // This would come from API
      icon: Users,
      color: 'text-warning-600',
      bgColor: 'bg-warning-50 dark:bg-warning-900',
    },
    {
      name: 'HL7 Messages',
      value: '5,678', // This would come from API
      icon: FileText,
      color: 'text-danger-600',
      bgColor: 'bg-danger-50 dark:bg-danger-900',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Dashboard
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Real-time overview of your healthcare integration platform
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <div key={stat.name} className="card p-5">
            <div className="flex items-center">
              <div className={`flex-shrink-0 rounded-md p-3 ${stat.bgColor}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    {stat.name}
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
                    {stat.value}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* System Health */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {/* Connection Status */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
            Connection Status
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-success-500 mr-2" />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  WebSocket
                </span>
              </div>
              <span className={`badge ${isConnected ? 'badge-success' : 'badge-danger'}`}>
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-success-500 mr-2" />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  API Server
                </span>
              </div>
              <span className="badge badge-success">Healthy</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-success-500 mr-2" />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Database
                </span>
              </div>
              <span className="badge badge-success">Connected</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-success-500 mr-2" />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Redis Cache
                </span>
              </div>
              <span className="badge badge-success">Active</span>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
            Recent Activity
          </h3>
          <div className="space-y-4">
            {lastMessage ? (
              <div className="flex items-start">
                <Clock className="h-5 w-5 text-gray-400 mr-2 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    {lastMessage.type}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {new Date(lastMessage.timestamp || '').toLocaleString()}
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                No recent activity
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Connection Types */}
      {stats.connections_by_type && (
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
            Connections by Type
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(stats.connections_by_type).map(([type, count]) => (
              <div key={type} className="text-center">
                <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {count as number}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400 capitalize">
                  {type}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="btn btn-primary">
            <Database className="h-5 w-5 mr-2" />
            Add Connection
          </button>
          <button className="btn btn-secondary">
            <Users className="h-5 w-5 mr-2" />
            Search Patients
          </button>
          <button className="btn btn-secondary">
            <FileText className="h-5 w-5 mr-2" />
            View Messages
          </button>
        </div>
      </div>
    </div>
  )
}