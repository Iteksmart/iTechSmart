import React, { useState, useEffect } from 'react';
import { FileCheck, CheckCircle, XCircle, AlertTriangle, Download, RefreshCw, TrendingUp } from 'lucide-react';

interface ComplianceFramework {
  id: string;
  name: string;
  description: string;
  total_controls: number;
  passed_controls: number;
  failed_controls: number;
  compliance_score: number;
  last_assessed: string;
  status: 'compliant' | 'non_compliant' | 'partial';
}

interface ComplianceControl {
  id: string;
  framework: string;
  control_id: string;
  title: string;
  description: string;
  status: 'passed' | 'failed' | 'not_tested';
  evidence: string[];
  last_tested: string;
}

const Compliance: React.FC = () => {
  const [frameworks, setFrameworks] = useState<ComplianceFramework[]>([]);
  const [controls, setControls] = useState<ComplianceControl[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFramework, setSelectedFramework] = useState<string>('all');

  useEffect(() => {
    fetchCompliance();
  }, []);

  const fetchCompliance = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/compliance');
      const data = await response.json();
      setFrameworks(data.frameworks || []);
      setControls(data.controls || []);
    } catch (error) {
      console.error('Error fetching compliance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant':
      case 'passed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'non_compliant':
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'partial':
      case 'not_tested':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'compliant':
      case 'passed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'non_compliant':
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'partial':
      case 'not_tested':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-gray-600" />;
    }
  };

  const filteredControls = selectedFramework === 'all' 
    ? controls 
    : controls.filter(c => c.framework === selectedFramework);

  const overallStats = {
    totalFrameworks: frameworks.length,
    compliantFrameworks: frameworks.filter(f => f.status === 'compliant').length,
    averageScore: frameworks.length > 0 
      ? frameworks.reduce((sum, f) => sum + f.compliance_score, 0) / frameworks.length 
      : 0,
    totalControls: controls.length,
    passedControls: controls.filter(c => c.status === 'passed').length,
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <FileCheck className="w-8 h-8 text-green-600" />
              Compliance Management
            </h1>
            <p className="text-gray-600 mt-2">Monitor compliance across security frameworks and standards</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={fetchCompliance}
              className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            <button className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2">
              <Download className="w-4 h-4" />
              Export Report
            </button>
          </div>
        </div>

        {/* Overall Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Frameworks</p>
                <p className="text-3xl font-bold text-gray-900">{overallStats.totalFrameworks}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <FileCheck className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Compliant</p>
                <p className="text-3xl font-bold text-green-600">{overallStats.compliantFrameworks}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Average Score</p>
                <p className="text-3xl font-bold text-blue-600">{overallStats.averageScore.toFixed(1)}%</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Controls Passed</p>
                <p className="text-3xl font-bold text-green-600">
                  {overallStats.passedControls}/{overallStats.totalControls}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Frameworks Overview */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Compliance Frameworks</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
            <div className="col-span-full p-12 text-center bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-600 mt-4">Loading compliance data...</p>
            </div>
          ) : frameworks.length === 0 ? (
            <div className="col-span-full p-12 text-center bg-white rounded-xl shadow-sm border border-gray-200">
              <FileCheck className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600">No compliance frameworks configured</p>
            </div>
          ) : (
            frameworks.map((framework) => (
              <div
                key={framework.id}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => setSelectedFramework(framework.name)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-900 mb-1">{framework.name}</h3>
                    <p className="text-sm text-gray-600">{framework.description}</p>
                  </div>
                  {getStatusIcon(framework.status)}
                </div>

                <div className="mb-4">
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-gray-600">Compliance Score</span>
                    <span className="font-bold text-gray-900">{framework.compliance_score.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        framework.compliance_score >= 90 ? 'bg-green-600' :
                        framework.compliance_score >= 70 ? 'bg-yellow-600' :
                        'bg-red-600'
                      }`}
                      style={{ width: `${framework.compliance_score}%` }}
                    ></div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">{framework.total_controls}</p>
                    <p className="text-xs text-gray-600">Total</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">{framework.passed_controls}</p>
                    <p className="text-xs text-gray-600">Passed</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-red-600">{framework.failed_controls}</p>
                    <p className="text-xs text-gray-600">Failed</p>
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(framework.status)}`}>
                      {framework.status.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-500">
                      Last assessed: {new Date(framework.last_assessed).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Controls Details */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Compliance Controls</h2>
          <select
            value={selectedFramework}
            onChange={(e) => setSelectedFramework(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Frameworks</option>
            {frameworks.map((framework) => (
              <option key={framework.id} value={framework.name}>
                {framework.name}
              </option>
            ))}
          </select>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          {filteredControls.length === 0 ? (
            <div className="p-12 text-center">
              <FileCheck className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600">No controls found</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredControls.map((control) => (
                <div key={control.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="font-mono text-sm font-semibold text-blue-600">{control.control_id}</span>
                        <span className="text-sm text-gray-600">{control.framework}</span>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(control.status)}`}>
                          {control.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">{control.title}</h3>
                      <p className="text-sm text-gray-600 mb-3">{control.description}</p>
                      <div className="text-sm text-gray-500">
                        Last tested: {new Date(control.last_tested).toLocaleString()}
                      </div>
                    </div>
                    {getStatusIcon(control.status)}
                  </div>
                  {control.evidence && control.evidence.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-sm font-medium text-gray-700 mb-2">Evidence:</p>
                      <div className="space-y-1">
                        {control.evidence.map((evidence, idx) => (
                          <p key={idx} className="text-sm text-gray-600 pl-4 border-l-2 border-gray-300">
                            {evidence}
                          </p>
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
    </div>
  );
};

export default Compliance;