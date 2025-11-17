import { useState, useEffect } from 'react';
import { 
  ComputerDesktopIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ChartBarIcon,
  CommandLineIcon,
  BellIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

interface Agent {
  id: string;
  hostname: string;
  ip_address: string;
  platform: string;
  status: 'ACTIVE' | 'OFFLINE' | 'ERROR' | 'MAINTENANCE';
  last_seen: string;
  version: string;
  organization_id?: string;
}

interface AgentStats {
  total_agents: number;
  active_agents: number;
  offline_agents: number;
  error_agents: number;
  total_unresolved_alerts: number;
}

interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_rx: number;
  network_tx: number;
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [stats, setStats] = useState<AgentStats | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    loadAgents();
    loadStats();
    
    // Refresh every 30 seconds
    const interval = setInterval(() => {
      loadAgents();
      loadStats();
      if (selectedAgent) {
        loadAgentMetrics(selectedAgent.id);
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [filter]);

  const loadAgents = async () => {
    try {
      const params = new URLSearchParams();
      if (filter !== 'all') {
        params.append('status', filter.toUpperCase());
      }
      
      const response = await fetch(`/api/v1/system-agents/?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to load agents');
      
      const data = await response.json();
      setAgents(data.agents || []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load agents');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/v1/system-agents/stats/overview', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to load stats');
      
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const loadAgentMetrics = async (agentId: string) => {
    try {
      const response = await fetch(`/api/v1/system-agents/${agentId}/metrics/system`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to load metrics');
      
      const data = await response.json();
      setMetrics(data);
    } catch (err) {
      console.error('Failed to load metrics:', err);
    }
  };

  const handleAgentClick = (agent: Agent) => {
    setSelectedAgent(agent);
    loadAgentMetrics(agent.id);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'text-green-600 bg-green-100';
      case 'OFFLINE': return 'text-gray-600 bg-gray-100';
      case 'ERROR': return 'text-red-600 bg-red-100';
      case 'MAINTENANCE': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ACTIVE': return <CheckCircleIcon className="w-5 h-5" />;
      case 'OFFLINE': return <XCircleIcon className="w-5 h-5" />;
      case 'ERROR': return <ExclamationTriangleIcon className="w-5 h-5" />;
      case 'MAINTENANCE': return <ClockIcon className="w-5 h-5" />;
      default: return <ComputerDesktopIcon className="w-5 h-5" />;
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getMetricColor = (value: number) => {
    if (value >= 90) return 'text-red-600';
    if (value >= 80) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getHealthScore = () => {
    if (!stats) return 0;
    const total = stats.total_agents;
    if (total === 0) return 100;
    return Math.round((stats.active_agents / total) * 100);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading agents...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <ExclamationTriangleIcon className="w-12 h-12 text-red-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Agents</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadAgents}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">System Agents</h1>
              <p className="text-gray-600">Enterprise-wide system monitoring and management</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-gray-600">System Health</p>
                <p className={`text-2xl font-bold ${getHealthScore() >= 90 ? 'text-green-600' : getHealthScore() >= 70 ? 'text-yellow-600' : 'text-red-600'}`}>
                  {getHealthScore()}%
                </p>
              </div>
              <ShieldCheckIcon className={`w-12 h-12 ${getHealthScore() >= 90 ? 'text-green-600' : getHealthScore() >= 70 ? 'text-yellow-600' : 'text-red-600'}`} />
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Agents</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.total_agents}</p>
                </div>
                <ComputerDesktopIcon className="w-10 h-10 text-blue-600" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Active</p>
                  <p className="text-3xl font-bold text-green-600">{stats.active_agents}</p>
                </div>
                <CheckCircleIcon className="w-10 h-10 text-green-600" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Offline</p>
                  <p className="text-3xl font-bold text-gray-600">{stats.offline_agents}</p>
                </div>
                <XCircleIcon className="w-10 h-10 text-gray-600" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Errors</p>
                  <p className="text-3xl font-bold text-red-600">{stats.error_agents}</p>
                </div>
                <ExclamationTriangleIcon className="w-10 h-10 text-red-600" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Alerts</p>
                  <p className="text-3xl font-bold text-yellow-600">{stats.total_unresolved_alerts}</p>
                </div>
                <BellIcon className="w-10 h-10 text-yellow-600" />
              </div>
            </div>
          </div>
        )}

        {/* Filter Tabs */}
        <div className="mb-6">
          <div className="flex space-x-2 border-b border-gray-200">
            {['all', 'active', 'offline', 'error'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-4 py-2 font-medium capitalize transition-colors ${
                  filter === f
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Agent List */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">Agents ({agents.length})</h2>
              </div>
              <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
                {agents.length === 0 ? (
                  <div className="p-6 text-center text-gray-500">
                    <ComputerDesktopIcon className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                    <p>No agents found. Deploy agents to start monitoring.</p>
                  </div>
                ) : (
                  agents.map((agent) => (
                    <div
                      key={agent.id}
                      onClick={() => handleAgentClick(agent)}
                      className={`p-6 cursor-pointer hover:bg-gray-50 transition-colors ${
                        selectedAgent?.id === agent.id ? 'bg-blue-50 border-l-4 border-blue-600' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className={`p-3 rounded-lg ${getStatusColor(agent.status)}`}>
                            {getStatusIcon(agent.status)}
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900">{agent.hostname}</h3>
                            <p className="text-sm text-gray-600">{agent.ip_address}</p>
                            <p className="text-xs text-gray-500 mt-1">
                              Last seen: {new Date(agent.last_seen).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(agent.status)}`}>
                            {agent.status}
                          </span>
                          <p className="text-xs text-gray-500 mt-2">
                            {agent.platform} • v{agent.version}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Agent Details */}
          <div className="lg:col-span-1">
            {selectedAgent ? (
              <div className="bg-white rounded-lg shadow-md sticky top-6">
                <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-blue-700">
                  <h2 className="text-xl font-semibold text-white">Agent Details</h2>
                </div>
                <div className="p-6 space-y-6">
                  {/* Basic Info */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-3">Information</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between py-2 border-b border-gray-100">
                        <span className="text-sm text-gray-600">Hostname:</span>
                        <span className="text-sm font-medium text-gray-900">{selectedAgent.hostname}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b border-gray-100">
                        <span className="text-sm text-gray-600">IP Address:</span>
                        <span className="text-sm font-medium text-gray-900">{selectedAgent.ip_address}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b border-gray-100">
                        <span className="text-sm text-gray-600">Platform:</span>
                        <span className="text-sm font-medium text-gray-900">{selectedAgent.platform}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b border-gray-100">
                        <span className="text-sm text-gray-600">Version:</span>
                        <span className="text-sm font-medium text-gray-900">{selectedAgent.version}</span>
                      </div>
                      <div className="flex justify-between py-2">
                        <span className="text-sm text-gray-600">Last Seen:</span>
                        <span className="text-sm font-medium text-gray-900">
                          {new Date(selectedAgent.last_seen).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* System Metrics */}
                  {metrics && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 mb-3">System Metrics</h3>
                      <div className="space-y-4">
                        <div>
                          <div className="flex justify-between mb-2">
                            <span className="text-sm text-gray-600">CPU Usage</span>
                            <span className={`text-sm font-medium ${getMetricColor(metrics.cpu_usage)}`}>
                              {metrics.cpu_usage.toFixed(1)}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2.5">
                            <div
                              className={`h-2.5 rounded-full transition-all ${
                                metrics.cpu_usage >= 90 ? 'bg-red-600' :
                                metrics.cpu_usage >= 80 ? 'bg-yellow-600' : 'bg-green-600'
                              }`}
                              style={{ width: `${metrics.cpu_usage}%` }}
                            ></div>
                          </div>
                        </div>

                        <div>
                          <div className="flex justify-between mb-2">
                            <span className="text-sm text-gray-600">Memory Usage</span>
                            <span className={`text-sm font-medium ${getMetricColor(metrics.memory_usage)}`}>
                              {metrics.memory_usage.toFixed(1)}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2.5">
                            <div
                              className={`h-2.5 rounded-full transition-all ${
                                metrics.memory_usage >= 90 ? 'bg-red-600' :
                                metrics.memory_usage >= 80 ? 'bg-yellow-600' : 'bg-green-600'
                              }`}
                              style={{ width: `${metrics.memory_usage}%` }}
                            ></div>
                          </div>
                        </div>

                        <div>
                          <div className="flex justify-between mb-2">
                            <span className="text-sm text-gray-600">Disk Usage</span>
                            <span className={`text-sm font-medium ${getMetricColor(metrics.disk_usage)}`}>
                              {metrics.disk_usage.toFixed(1)}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2.5">
                            <div
                              className={`h-2.5 rounded-full transition-all ${
                                metrics.disk_usage >= 90 ? 'bg-red-600' :
                                metrics.disk_usage >= 75 ? 'bg-yellow-600' : 'bg-green-600'
                              }`}
                              style={{ width: `${metrics.disk_usage}%` }}
                            ></div>
                          </div>
                        </div>

                        <div className="pt-3 border-t border-gray-200">
                          <div className="flex justify-between py-2">
                            <span className="text-sm text-gray-600">Network RX:</span>
                            <span className="text-sm font-medium text-gray-900">
                              {formatBytes(metrics.network_rx)}/s
                            </span>
                          </div>
                          <div className="flex justify-between py-2">
                            <span className="text-sm text-gray-600">Network TX:</span>
                            <span className="text-sm font-medium text-gray-900">
                              {formatBytes(metrics.network_tx)}/s
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="pt-4 border-t border-gray-200 space-y-2">
                    <button className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2 font-medium">
                      <ChartBarIcon className="w-5 h-5" />
                      <span>View Detailed Metrics</span>
                    </button>
                    <button className="w-full px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center space-x-2 font-medium">
                      <CommandLineIcon className="w-5 h-5" />
                      <span>Execute Command</span>
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-md p-8 text-center">
                <ComputerDesktopIcon className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600 font-medium">Select an agent to view details</p>
                <p className="text-sm text-gray-500 mt-2">Click on any agent from the list to see its metrics and information</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}