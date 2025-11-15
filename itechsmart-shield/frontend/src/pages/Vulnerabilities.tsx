import React, { useState, useEffect } from 'react';
import { Bug, AlertCircle, CheckCircle, Clock, Filter, Download, RefreshCw, Search } from 'lucide-react';

interface Vulnerability {
  id: string;
  cve_id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  cvss_score: number;
  affected_systems: string[];
  status: 'open' | 'in_progress' | 'resolved';
  discovered_at: string;
  patch_available: boolean;
  remediation: string;
}

const Vulnerabilities: React.FC = () => {
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [severityFilter, setSeverityFilter] = useState<string>('all');

  useEffect(() => {
    fetchVulnerabilities();
  }, []);

  const fetchVulnerabilities = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/vulnerabilities');
      const data = await response.json();
      setVulnerabilities(data.vulnerabilities || []);
    } catch (error) {
      console.error('Error fetching vulnerabilities:', error);
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

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open': return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'in_progress': return <Clock className="w-5 h-5 text-yellow-600" />;
      case 'resolved': return <CheckCircle className="w-5 h-5 text-green-600" />;
      default: return <AlertCircle className="w-5 h-5 text-gray-600" />;
    }
  };

  const getCVSSColor = (score: number) => {
    if (score >= 9.0) return 'text-red-600';
    if (score >= 7.0) return 'text-orange-600';
    if (score >= 4.0) return 'text-yellow-600';
    return 'text-blue-600';
  };

  const filteredVulnerabilities = vulnerabilities.filter(vuln => {
    const matchesSearch = vuln.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         vuln.cve_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         vuln.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || vuln.status === statusFilter;
    const matchesSeverity = severityFilter === 'all' || vuln.severity === severityFilter;
    return matchesSearch && matchesStatus && matchesSeverity;
  });

  const vulnStats = {
    total: vulnerabilities.length,
    critical: vulnerabilities.filter(v => v.severity === 'critical').length,
    open: vulnerabilities.filter(v => v.status === 'open').length,
    resolved: vulnerabilities.filter(v => v.status === 'resolved').length,
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Bug className="w-8 h-8 text-orange-600" />
              Vulnerability Management
            </h1>
            <p className="text-gray-600 mt-2">Track and remediate security vulnerabilities</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={fetchVulnerabilities}
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
                <p className="text-sm text-gray-600 mb-1">Total Vulnerabilities</p>
                <p className="text-3xl font-bold text-gray-900">{vulnStats.total}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Bug className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Critical</p>
                <p className="text-3xl font-bold text-red-600">{vulnStats.critical}</p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Open</p>
                <p className="text-3xl font-bold text-orange-600">{vulnStats.open}</p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Resolved</p>
                <p className="text-3xl font-bold text-green-600">{vulnStats.resolved}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by CVE ID, title, or description..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div className="flex items-center gap-4">
            <Filter className="w-5 h-5 text-gray-400" />
            <div className="flex gap-2">
              <button
                onClick={() => setStatusFilter('all')}
                className={`px-4 py-2 rounded-lg ${statusFilter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
              >
                All
              </button>
              <button
                onClick={() => setStatusFilter('open')}
                className={`px-4 py-2 rounded-lg ${statusFilter === 'open' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
              >
                Open
              </button>
              <button
                onClick={() => setStatusFilter('in_progress')}
                className={`px-4 py-2 rounded-lg ${statusFilter === 'in_progress' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
              >
                In Progress
              </button>
              <button
                onClick={() => setStatusFilter('resolved')}
                className={`px-4 py-2 rounded-lg ${statusFilter === 'resolved' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
              >
                Resolved
              </button>
            </div>
            <div className="ml-auto">
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
      </div>

      {/* Vulnerabilities List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        {loading ? (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading vulnerabilities...</p>
          </div>
        ) : filteredVulnerabilities.length === 0 ? (
          <div className="p-12 text-center">
            <Bug className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600">No vulnerabilities found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredVulnerabilities.map((vuln) => (
              <div key={vuln.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="font-mono text-sm font-semibold text-blue-600">{vuln.cve_id}</span>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getSeverityColor(vuln.severity)}`}>
                        {vuln.severity.toUpperCase()}
                      </span>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(vuln.status)}
                        <span className="text-sm text-gray-600">{vuln.status.replace('_', ' ').toUpperCase()}</span>
                      </div>
                      {vuln.patch_available && (
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-semibold">
                          Patch Available
                        </span>
                      )}
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{vuln.title}</h3>
                    <p className="text-sm text-gray-600 mb-3">{vuln.description}</p>
                    <div className="flex items-center gap-6 text-sm">
                      <div>
                        <span className="text-gray-600">CVSS Score: </span>
                        <span className={`font-bold text-lg ${getCVSSColor(vuln.cvss_score)}`}>
                          {vuln.cvss_score.toFixed(1)}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Discovered: </span>
                        <span className="text-gray-900">{new Date(vuln.discovered_at).toLocaleDateString()}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Affected Systems: </span>
                        <span className="text-gray-900 font-semibold">{vuln.affected_systems.length}</span>
                      </div>
                    </div>
                  </div>
                </div>
                {vuln.affected_systems && vuln.affected_systems.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-700 mb-2">Affected Systems:</p>
                    <div className="flex flex-wrap gap-2">
                      {vuln.affected_systems.map((system, idx) => (
                        <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-mono">
                          {system}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {vuln.remediation && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-700 mb-1">Remediation:</p>
                    <p className="text-sm text-gray-600">{vuln.remediation}</p>
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

export default Vulnerabilities;