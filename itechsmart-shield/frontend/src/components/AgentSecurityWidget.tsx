/**
 * iTechSmart Shield - Agent Security Widget
 * Displays agent security monitoring with threat detection
 */

import React, { useState, useEffect } from 'react';

interface SecurityThreat {
  id: string;
  agent: string;
  agentId: string;
  type: string;
  severity: 'critical' | 'high' | 'warning' | 'low';
  title: string;
  description: string;
  recommendation: string;
  timestamp: string;
}

interface SecuritySummary {
  totalAgents: number;
  secureAgents: number;
  atRiskAgents: number;
  criticalAgents: number;
  averageSecurityScore: number;
  threats: SecurityThreat[];
  recommendations: string[];
}

const AgentSecurityWidget: React.FC = () => {
  const [summary, setSummary] = useState<SecuritySummary | null>(null);
  const [threats, setThreats] = useState<SecurityThreat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8017';

  const fetchData = async () => {
    try {
      setError(null);
      
      // Fetch security summary
      const summaryRes = await fetch(`${API_BASE}/api/v1/agents/security/summary`);
      if (!summaryRes.ok) throw new Error('Failed to fetch security summary');
      const summaryData = await summaryRes.json();
      setSummary(summaryData);

      // Fetch threats
      const threatsRes = await fetch(`${API_BASE}/api/v1/agents/security/threats`);
      if (!threatsRes.ok) throw new Error('Failed to fetch threats');
      const threatsData = await threatsRes.json();
      setThreats(threatsData.threats || []);

      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load security data');
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

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return { bg: 'bg-red-100', border: 'border-red-500', text: 'text-red-800', badge: 'bg-red-500' };
      case 'high': return { bg: 'bg-orange-100', border: 'border-orange-500', text: 'text-orange-800', badge: 'bg-orange-500' };
      case 'warning': return { bg: 'bg-yellow-100', border: 'border-yellow-500', text: 'text-yellow-800', badge: 'bg-yellow-500' };
      case 'low': return { bg: 'bg-blue-100', border: 'border-blue-500', text: 'text-blue-800', badge: 'bg-blue-500' };
      default: return { bg: 'bg-gray-100', border: 'border-gray-500', text: 'text-gray-800', badge: 'bg-gray-500' };
    }
  };

  const getSecurityScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const filteredThreats = selectedSeverity === 'all' 
    ? threats 
    : threats.filter(t => t.severity === selectedSeverity);

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-gray-900">🛡️ Security Monitoring</h3>
        </div>
        <div className="text-center py-12 text-gray-500">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500 mx-auto mb-4"></div>
          Loading security data...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-gray-900">🛡️ Security Monitoring</h3>
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
        <h3 className="text-xl font-semibold text-gray-900">🛡️ Security Monitoring</h3>
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

      {/* Security Score */}
      {summary && (
        <div className="mb-6">
          <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-600 mb-2">Average Security Score</div>
                <div className={`text-4xl font-bold ${getSecurityScoreColor(summary.averageSecurityScore)}`}>
                  {summary.averageSecurityScore}/100
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-600 mb-2">Status</div>
                <div className="text-lg font-semibold">
                  {summary.averageSecurityScore >= 90 ? '✅ Secure' :
                   summary.averageSecurityScore >= 70 ? '⚠️ At Risk' :
                   '🚨 Critical'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Summary Stats */}
      {summary && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="text-center p-4 bg-gray-50 rounded-lg border-2 border-gray-200">
            <div className="text-3xl font-bold text-gray-900">{summary.totalAgents}</div>
            <div className="text-xs text-gray-600 uppercase mt-1">Total</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg border-2 border-green-200">
            <div className="text-3xl font-bold text-green-600">{summary.secureAgents}</div>
            <div className="text-xs text-gray-600 uppercase mt-1">Secure</div>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded-lg border-2 border-yellow-200">
            <div className="text-3xl font-bold text-yellow-600">{summary.atRiskAgents}</div>
            <div className="text-xs text-gray-600 uppercase mt-1">At Risk</div>
          </div>
          <div className="text-center p-4 bg-red-50 rounded-lg border-2 border-red-200">
            <div className="text-3xl font-bold text-red-600">{summary.criticalAgents}</div>
            <div className="text-xs text-gray-600 uppercase mt-1">Critical</div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {summary && summary.recommendations.length > 0 && (
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
            <span>💡</span>
            <span>Security Recommendations</span>
          </div>
          <ul className="space-y-1 text-sm text-blue-800">
            {summary.recommendations.map((rec, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="mt-1">•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Threats Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-lg font-semibold text-gray-900">🚨 Active Threats</h4>
          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="warning">Warning</option>
            <option value="low">Low</option>
          </select>
        </div>

        <div className="space-y-3">
          {filteredThreats.length === 0 ? (
            <div className="text-center py-8 bg-green-50 rounded-lg border border-green-200">
              <div className="text-4xl mb-2">✅</div>
              <div className="text-green-800 font-medium">No Active Threats</div>
              <div className="text-sm text-green-600 mt-1">All systems are secure</div>
            </div>
          ) : (
            filteredThreats.map((threat) => {
              const colors = getSeverityColor(threat.severity);
              return (
                <div
                  key={threat.id}
                  className={`${colors.bg} border-l-4 ${colors.border} rounded-lg p-4`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`px-2 py-1 rounded text-xs font-bold text-white ${colors.badge}`}>
                          {threat.severity.toUpperCase()}
                        </span>
                        <span className={`font-semibold ${colors.text}`}>
                          {threat.title}
                        </span>
                      </div>
                      <div className={`text-sm ${colors.text} mb-2`}>
                        {threat.description}
                      </div>
                      <div className="text-xs text-gray-600 mb-2">
                        Agent: <span className="font-medium">{threat.agent}</span>
                      </div>
                      <div className="bg-white bg-opacity-50 rounded p-2 text-sm">
                        <div className="font-medium text-gray-700 mb-1">💡 Recommendation:</div>
                        <div className="text-gray-600">{threat.recommendation}</div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {filteredThreats.length > 0 && (
          <div className="mt-4 text-center text-sm text-gray-600">
            Showing {filteredThreats.length} of {threats.length} threat(s)
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentSecurityWidget;