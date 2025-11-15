import React, { useState, useEffect } from 'react';
import { Shield, AlertTriangle, Activity, TrendingUp, Filter, Download, RefreshCw } from 'lucide-react';

interface Threat {
  id: string;
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  source: string;
  target: string;
  description: string;
  status: 'active' | 'mitigated' | 'investigating';
  detected_at: string;
  indicators: string[];
}

const Threats: React.FC = () => {
  const [threats, setThreats] = useState<Threat[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [severityFilter, setSeverityFilter] = useState<string>('all');

  useEffect(() => {
    fetchThreats();
  }, []);

  const fetchThreats = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/threats');
      const data = await response.json();
      setThreats(data.threats || []);
    } catch (error) {
      console.error('Error fetching threats:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-red-100 text-red-800';
      case 'investigating': return 'bg-yellow-100 text-yellow-800';
      case 'mitigated': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredThreats = threats.filter(threat => {
    const matchesStatus = filter === 'all' || threat.status === filter;
    const matchesSeverity = severityFilter === 'all' || threat.severity === severityFilter;
    return matchesStatus && matchesSeverity;
  });

  const threatStats = {
    total: threats.length,
    critical: threats.filter(t => t.severity === 'critical').length,
    active: threats.filter(t => t.status === 'active').length,
    mitigated: threats.filter(t => t.status === 'mitigated').length,
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Shield className="w-8 h-8 text-red-600" />
              Threat Detection
            </h1>
            <p className="text-gray-600 mt-2">Real-time security threat monitoring and analysis</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={fetchThreats}
              className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            <button className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2">
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Threats</p>
                <p className="text-3xl font-bold text-gray-900">{threatStats.total}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Critical</p>
                <p className="text-3xl font-bold text-red-600">{threatStats.critical}</p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <Shield className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Active</p>
                <p className="text-3xl font-bold text-orange-600">{threatStats.active}</p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Mitigated</p>
                <p className="text-3xl font-bold text-green-600">{threatStats.mitigated}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 flex items-center gap-4">
          <Filter className="w-5 h-5 text-gray-400" />
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg ${filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
            >
              All
            </button>
            <button
              onClick={() => setFilter('active')}
              className={`px-4 py-2 rounded-lg ${filter === 'active' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
            >
              Active
            </button>
            <button
              onClick={() => setFilter('investigating')}
              className={`px-4 py-2 rounded-lg ${filter === 'investigating' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
            >
              Investigating
            </button>
            <button
              onClick={() => setFilter('mitigated')}
              className={`px-4 py-2 rounded-lg ${filter === 'mitigated' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
            >
              Mitigated
            </button>
          </div>
          <div className="ml-auto flex gap-2">
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Threats List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        {loading ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading threats...</p>
          </div>
        ) : filteredThreats.length === 0 ? (
          <div className="p-12 text-center">
            <Shield className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600">No threats found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredThreats.map((threat) => (
              <div key={threat.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getSeverityColor(threat.severity)}`}>
                        {threat.severity.toUpperCase()}
                      </span>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(threat.status)}`}>
                        {threat.status.toUpperCase()}
                      </span>
                      <span className="text-sm text-gray-500">{threat.type}</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{threat.description}</h3>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span>Source: <span className="font-mono text-gray-900">{threat.source}</span></span>
                      <span>→</span>
                      <span>Target: <span className="font-mono text-gray-900">{threat.target}</span></span>
                      <span className="ml-auto">Detected: {new Date(threat.detected_at).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
                {threat.indicators && threat.indicators.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-700 mb-2">Indicators of Compromise:</p>
                    <div className="flex flex-wrap gap-2">
                      {threat.indicators.map((indicator, idx) => (
                        <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-mono">
                          {indicator}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Threats;