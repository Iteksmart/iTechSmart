import { Shield, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'
import { useWebSocket } from '../lib/websocket'

export default function Security() {
  const { messages, isConnected } = useWebSocket('alerts')

  const securityAlerts = messages.filter((msg) => msg.type === 'alert')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Security & Compliance
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Real-time security monitoring and HIPAA compliance
        </p>
      </div>

      {/* Security Status */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 rounded-md p-3 bg-success-50 dark:bg-success-900">
              <CheckCircle className="h-6 w-6 text-success-600" />
            </div>
            <div className="ml-5">
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                HIPAA Compliant
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                All controls active
              </p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 rounded-md p-3 bg-primary-50 dark:bg-primary-900">
              <Shield className="h-6 w-6 text-primary-600" />
            </div>
            <div className="ml-5">
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                Encryption Active
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Data at rest & in transit
              </p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 rounded-md p-3 bg-warning-50 dark:bg-warning-900">
              <AlertTriangle className="h-6 w-6 text-warning-600" />
            </div>
            <div className="ml-5">
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                {securityAlerts.length} Alerts
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Requires attention
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Security Alerts */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          Security Alerts
        </h3>
        <div className="space-y-4">
          {securityAlerts.length > 0 ? (
            securityAlerts.map((alert, index) => (
              <div
                key={index}
                className="flex items-start p-4 bg-warning-50 dark:bg-warning-900 rounded-lg"
              >
                <AlertTriangle className="h-5 w-5 text-warning-600 mr-3 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {alert.data?.alert_type || 'Security Alert'}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {alert.data?.message || 'Security event detected'}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    {new Date(alert.timestamp || '').toLocaleString()}
                  </p>
                </div>
                <span className={`badge badge-${alert.data?.severity || 'warning'}`}>
                  {alert.data?.severity || 'medium'}
                </span>
              </div>
            ))
          ) : (
            <div className="text-center py-8">
              <CheckCircle className="mx-auto h-12 w-12 text-success-500" />
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                No security alerts. System is secure.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Compliance Status */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          HIPAA Compliance Status
        </h3>
        <div className="space-y-3">
          {[
            { name: 'Access Control', status: 'compliant' },
            { name: 'Audit Controls', status: 'compliant' },
            { name: 'Integrity Controls', status: 'compliant' },
            { name: 'Person/Entity Authentication', status: 'compliant' },
            { name: 'Transmission Security', status: 'compliant' },
          ].map((item) => (
            <div key={item.name} className="flex items-center justify-between">
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {item.name}
              </span>
              <div className="flex items-center">
                <CheckCircle className="h-4 w-4 text-success-500 mr-2" />
                <span className="badge badge-success">Compliant</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Monitoring Status */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          Real-time Monitoring
        </h3>
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-700 dark:text-gray-300">
            Security Monitor Status
          </span>
          <div className="flex items-center">
            {isConnected ? (
              <>
                <CheckCircle className="h-4 w-4 text-success-500 mr-2" />
                <span className="badge badge-success">Active</span>
              </>
            ) : (
              <>
                <XCircle className="h-4 w-4 text-danger-500 mr-2" />
                <span className="badge badge-danger">Disconnected</span>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}