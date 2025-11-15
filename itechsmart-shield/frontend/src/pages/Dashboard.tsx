import React from 'react';
import { Shield, AlertTriangle, CheckCircle, Activity, TrendingUp, TrendingDown, Eye, Lock } from 'lucide-react';

const Dashboard: React.FC = () => {
  const securityScore = 92;
  
  const stats = [
    {
      name: 'Security Score',
      value: `${securityScore}%`,
      change: '+5%',
      trend: 'up',
      icon: Shield,
      color: 'green'
    },
    {
      name: 'Active Threats',
      value: '3',
      change: '-2',
      trend: 'down',
      icon: AlertTriangle,
      color: 'red'
    },
    {
      name: 'Blocked Attacks',
      value: '1,247',
      change: '+156',
      trend: 'up',
      icon: CheckCircle,
      color: 'blue'
    },
    {
      name: 'Vulnerabilities',
      value: '25',
      change: '-8',
      trend: 'down',
      icon: Eye,
      color: 'yellow'
    }
  ];

  const recentThreats = [
    {
      id: 1,
      type: 'Malware',
      severity: 'high',
      status: 'blocked',
      target: 'web-server-01',
      time: '5 minutes ago'
    },
    {
      id: 2,
      type: 'Brute Force',
      severity: 'medium',
      status: 'monitoring',
      target: 'ssh-server',
      time: '15 minutes ago'
    },
    {
      id: 3,
      type: 'DDoS Attack',
      severity: 'critical',
      status: 'mitigated',
      target: 'api-gateway',
      time: '1 hour ago'
    }
  ];

  const compliance = [
    { name: 'SOC 2', score: 98, status: 'compliant' },
    { name: 'ISO 27001', score: 95, status: 'compliant' },
    { name: 'GDPR', score: 97, status: 'compliant' }
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Security Dashboard</h1>
          <p className="mt-2 text-sm text-gray-600">
            Real-time security monitoring and threat detection
          </p>
        </div>
        <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700">
          <Activity className="h-4 w-4 mr-2" />
          Run Security Scan
        </button>
      </div>

      {/* Security Score Card */}
      <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-medium">Overall Security Score</h2>
            <p className="text-4xl font-bold mt-2">{securityScore}%</p>
            <p className="text-sm mt-2 text-green-100">
              Excellent - Your systems are well protected
            </p>
          </div>
          <div className="bg-white bg-opacity-20 rounded-full p-4">
            <Shield className="h-16 w-16" />
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          const TrendIcon = stat.trend === 'up' ? TrendingUp : TrendingDown;
          const trendColor = stat.trend === 'up' ? 'text-green-600' : 'text-red-600';
          
          return (
            <div
              key={stat.name}
              className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow"
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
                        <div className={`ml-2 flex items-baseline text-sm font-semibold ${trendColor}`}>
                          <TrendIcon className="h-4 w-4 mr-1" />
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

      {/* Recent Threats */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Recent Threats</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {recentThreats.map((threat) => {
            const severityColors = {
              critical: 'bg-red-100 text-red-800',
              high: 'bg-orange-100 text-orange-800',
              medium: 'bg-yellow-100 text-yellow-800',
              low: 'bg-blue-100 text-blue-800'
            };
            
            const statusColors = {
              blocked: 'bg-green-100 text-green-800',
              monitoring: 'bg-yellow-100 text-yellow-800',
              mitigated: 'bg-blue-100 text-blue-800'
            };
            
            return (
              <div key={threat.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${severityColors[threat.severity as keyof typeof severityColors]}`}>
                        {threat.severity}
                      </span>
                      <h3 className="text-sm font-medium text-gray-900">
                        {threat.type}
                      </h3>
                    </div>
                    <p className="mt-1 text-sm text-gray-500">
                      Target: {threat.target} • {threat.time}
                    </p>
                  </div>
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${statusColors[threat.status as keyof typeof statusColors]}`}>
                    {threat.status}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Compliance Status */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Compliance Status</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
            {compliance.map((framework) => (
              <div key={framework.name} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-gray-900">{framework.name}</h3>
                  <CheckCircle className="h-5 w-5 text-green-500" />
                </div>
                <div className="mt-2">
                  <div className="flex items-baseline">
                    <span className="text-2xl font-semibold text-gray-900">{framework.score}%</span>
                    <span className="ml-2 text-sm text-gray-500">compliant</span>
                  </div>
                  <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${framework.score}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
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
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { name: 'Passport', status: 'connected' },
              { name: 'Enterprise Hub', status: 'connected' },
              { name: 'Ninja', status: 'connected' },
              { name: 'Supreme', status: 'connected' }
            ].map((integration) => (
              <div
                key={integration.name}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
              >
                <span className="text-sm font-medium text-gray-900">
                  {integration.name}
                </span>
                <CheckCircle className="h-5 w-5 text-green-500" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;