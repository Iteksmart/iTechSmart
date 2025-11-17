/**
 * iTechSmart Copilot - Agent Status Widget with AI Insights
 * Displays agent monitoring with AI-powered analysis
 */

import React, { useState, useEffect } from 'react';

interface Agent {
  id: string;
  hostname: string;
  status: 'ACTIVE' | 'OFFLINE' | 'ERROR' | 'MAINTENANCE';
  lastSeen: string;
  lastMetrics?: {
    cpuUsage: number;
    memoryUsage: number;
    diskUsage: number;
  };
  alertCount?: number;
}

interface AgentSummary {
  total: number;
  active: number;
  offline: number;
  error: number;
  averageMetrics: {
    cpu: number;
    memory: number;
    disk: number;
  };
}

interface AIInsight {
  type: 'success' | 'info' | 'warning' | 'error';
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  agents?: string[];
}

interface AIInsights {
  insights: AIInsight[];
  recommendations: string[];
  summary: string;
  healthPercentage: number;
}

const AgentStatusWidget: React.FC = () => {
  const [summary, setSummary] = useState<AgentSummary | null>(null);
  const [aiInsights, setAiInsights] = useState<AIInsights | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [showInsights, setShowInsights] = useState(true);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8004';

  const fetchData = async () => {
    try {
      setError(null);
      
      // Fetch summary
      const summaryRes = await fetch(`${API_BASE}/api/v1/agents/stats/summary`);
      if (!summaryRes.ok) throw new Error('Failed to fetch summary');
      const summaryData = await summaryRes.json();
      setSummary(summaryData);

      // Fetch AI insights
      const insightsRes = await fetch(`${API_BASE}/api/v1/agents/ai/insights`);
      if (!insightsRes.ok) throw new Error('Failed to fetch AI insights');
      const insightsData = await insightsRes.json();
      setAiInsights(insightsData);

      // Fetch agents list
      const agentsRes = await fetch(`${API_BASE}/api/v1/agents?limit=10`);
      if (!agentsRes.ok) throw new Error('Failed to fetch agents');
      const agentsData = await agentsRes.json();
      setAgents(agentsData.agents || []);

      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load agent data');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    if (autoRefresh) {
      const interval = setInterval(fetchData, 30000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'bg-green-500';
      case 'OFFLINE': return 'bg-gray-500';
      case 'ERROR': return 'bg-red-500';
      case 'MAINTENANCE': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getInsightColor = (type: string) => {
    switch (type) {
      case 'success': return 'bg-green-50 border-green-200 text-green-800';
      case 'info': return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'warning': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'error': return 'bg-red-50 border-red-200 text-red-800';
      default: return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'success': return '✓';
      case 'info': return 'ℹ';
      case 'warning': return '⚠';
      case 'error': return '✕';
      default: return '•';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-gray-900">🤖 AI Agent Monitoring</h3>
        </div>
        <div className="text-center py-12 text-gray-500">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          Loading agent data...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-gray-900">🤖 AI Agent Monitoring</h3>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">⚠️</span>
            <span className="text-red-800">{error}</span>
          </div>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-900">🤖 AI Agent Monitoring</h3>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
            Auto-refresh
          </label>
          <button
            onClick={fetchData}
            className="text-xl hover:rotate-180 transition-transform duration-500"
          >
            🔄
          </button>
        </div>
      </div>

      {/* AI Insights Section */}
      {aiInsights && showInsights && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <span>🧠</span>
              AI Insights
            </h4>
            <button
              onClick={() => setShowInsights(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          {/* Health Summary */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-600 mb-1">System Health</div>
                <div className="text-2xl font-bold text-gray-900">
                  {aiInsights.healthPercentage}%
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-600">{aiInsights.summary}</div>
              </div>
            </div>
          </div>

          {/* Insights */}
          <div className="space-y-3 mb-4">
            {aiInsights.insights.map((insight, index) => (
              <div
                key={index}
                className={`border rounded-lg p-4 ${getInsightColor(insight.type)}`}
              >
                <div className="flex items-start gap-3">
                  <span className="text-xl">{getInsightIcon(insight.type)}</span>
                  <div className="flex-1">
                    <div className="font-semibold mb-1">{insight.title}</div>
                    <div className="text-sm mb-2">{insight.description}</div>
                    {insight.agents && insight.agents.length > 0 && (
                      <div className="text-xs opacity-75">
                        Affected: {insight.agents.join(', ')}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Recommendations */}
          {aiInsights.recommendations.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="font-semibold text-blue-900 mb-2">💡 Recommendations</div>
              <ul className="space-y-1 text-sm text-blue-800">
                {aiInsights.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span>•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {!showInsights && (
        <button
          onClick={() => setShowInsights(true)}
          className="mb-6 text-blue-600 hover:text-blue-700 text-sm font-medium"
        >
          Show AI Insights
        </button>
      )}

      {/* Summary Stats */}
      {summary && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl font-bold text-gray-900">{summary.total}</div>
            <div className="text-xs text-gray-600 uppercase mt-1">Total</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-3xl font-bold text-green-600">{summary.active}</div>
            <div className="text-xs text-gray-600 uppercase mt-1">Active</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl font-bold text-gray-600">{summary.offline}</div>
            <div className="text-xs text-gray-600 uppercase mt-1">Offline</div>
          </div>
          <div className="text-center p-4 bg-red-50 rounded-lg">
            <div className="text-3xl font-bold text-red-600">{summary.error}</div>
            <div className="text-xs text-gray-600 uppercase mt-1">Error</div>
          </div>
        </div>
      )}

      {/* Average Metrics */}
      {summary && (
        <div className="mb-6">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Average Metrics</h4>
          <div className="space-y-3">
            {[
              { label: 'CPU', value: summary.averageMetrics.cpu, color: 'blue' },
              { label: 'Memory', value: summary.averageMetrics.memory, color: 'purple' },
              { label: 'Disk', value: summary.averageMetrics.disk, color: 'indigo' }
            ].map((metric) => (
              <div key={metric.label}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">{metric.label}</span>
                  <span className={`font-semibold text-${metric.color}-600`}>
                    {metric.value.toFixed(1)}%
                  </span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full bg-${metric.color}-500 transition-all duration-300`}
                    style={{ width: `${metric.value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Agents */}
      <div>
        <h4 className="text-sm font-semibold text-gray-700 mb-3">Recent Agents</h4>
        <div className="space-y-2">
          {agents.length === 0 ? (
            <div className="text-center py-8 text-gray-500 text-sm">
              No agents registered
            </div>
          ) : (
            agents.map((agent) => (
              <div
                key={agent.id}
                className="bg-gray-50 rounded-lg p-3 border border-gray-200 hover:border-blue-300 transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="font-medium text-gray-900">{agent.hostname}</div>
                  <span
                    className={`px-2 py-1 rounded text-xs font-semibold text-white ${getStatusColor(agent.status)}`}
                  >
                    {agent.status}
                  </span>
                </div>
                {agent.lastMetrics && (
                  <div className="flex gap-4 text-xs text-gray-600">
                    <span>CPU: {agent.lastMetrics.cpuUsage.toFixed(1)}%</span>
                    <span>MEM: {agent.lastMetrics.memoryUsage.toFixed(1)}%</span>
                    <span>DISK: {agent.lastMetrics.diskUsage.toFixed(1)}%</span>
                  </div>
                )}
                {agent.alertCount !== undefined && agent.alertCount > 0 && (
                  <div className="mt-2 text-xs text-red-600 bg-red-50 rounded px-2 py-1 inline-block">
                    ⚠️ {agent.alertCount} alert{agent.alertCount !== 1 ? 's' : ''}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default AgentStatusWidget;