import React, { useState, useEffect } from 'react';
import { useQuantum } from '../contexts/QuantumContext';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: string;
  color: string;
  trend?: number;
}

function MetricCard({ title, value, icon, color, trend }: MetricCardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {trend !== undefined && (
            <p className={`text-sm mt-1 ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
            </p>
          )}
        </div>
        <div className={`text-3xl ${color}`}>{icon}</div>
      </div>
    </div>
  );
}

interface AlgorithmPerformanceProps {
  algorithm: string;
  performance: number;
  jobs: number;
  success_rate: number;
}

function AlgorithmPerformance({ algorithm, performance, jobs, success_rate }: AlgorithmPerformanceProps) {
  const getStatusColor = (rate: number) => {
    if (rate >= 0.9) return 'bg-green-500';
    if (rate >= 0.7) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-medium text-gray-900">{algorithm}</h4>
        <div className={`w-3 h-3 rounded-full ${getStatusColor(success_rate)}`}></div>
      </div>
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Performance</span>
          <span className="font-medium">{performance.toFixed(1)}ms</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Jobs</span>
          <span className="font-medium">{jobs}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Success Rate</span>
          <span className="font-medium">{(success_rate * 100).toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className={`${getStatusColor(success_rate)} h-2 rounded-full`}
            style={{ width: `${success_rate * 100}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}

export function Dashboard() {
  const { state, fetchStatus, runDemo } = useQuantum();
  const [isRunningDemo, setIsRunningDemo] = useState(false);

  useEffect(() => {
    const interval = setInterval(fetchStatus, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, [fetchStatus]);

  const handleRunDemo = async (type: 'grover' | 'optimization') => {
    try {
      setIsRunningDemo(true);
      await runDemo(type);
    } catch (error) {
      console.error('Demo failed:', error);
    } finally {
      setIsRunningDemo(false);
    }
  };

  const algorithmPerformance = [
    { algorithm: 'Grover Search', performance: 45.2, jobs: 23, success_rate: 0.95 },
    { algorithm: 'QAOA Optimization', performance: 125.8, jobs: 15, success_rate: 0.88 },
    { algorithm: 'VQE Eigenvalue', performance: 98.4, jobs: 8, success_rate: 0.92 },
    { algorithm: 'Quantum ML', performance: 234.1, jobs: 12, success_rate: 0.78 },
  ];

  const recentJobs = state.jobs.slice(0, 5);

  return (
    <div className="space-y-6">
      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="flex flex-wrap gap-4">
          <button
            onClick={() => handleRunDemo('grover')}
            disabled={isRunningDemo}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isRunningDemo ? 'Running...' : 'Run Grover Demo'}
          </button>
          <button
            onClick={() => handleRunDemo('optimization')}
            disabled={isRunningDemo}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isRunningDemo ? 'Running...' : 'Run Optimization Demo'}
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Active Jobs"
          value={state.status?.active_jobs || 0}
          icon="⚡"
          color="text-blue-600"
          trend={12}
        />
        <MetricCard
          title="Total Jobs"
          value={state.status?.total_jobs || 0}
          icon="📊"
          color="text-green-600"
          trend={8}
        />
        <MetricCard
          title="Available Backends"
          value={state.status?.available_backends || 0}
          icon="💎"
          color="text-purple-600"
          trend={0}
        />
        <MetricCard
          title="Service Status"
          value={state.status?.service_status || 'Unknown'}
          icon="🟢"
          color="text-green-600"
        />
      </div>

      {/* Algorithm Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="lg:col-span-2">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Algorithm Performance</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {algorithmPerformance.map((algo, index) => (
              <AlgorithmPerformance key={index} {...algo} />
            ))}
          </div>
        </div>
      </div>

      {/* Recent Jobs */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Recent Jobs</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Job ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Algorithm
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Backend
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Execution Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentJobs.map((job) => (
                <tr key={job.job_id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {job.job_id.substring(0, 12)}...
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {job.algorithm}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {job.backend}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      job.status === 'completed' ? 'bg-green-100 text-green-800' :
                      job.status === 'failed' ? 'bg-red-100 text-red-800' :
                      job.status === 'running' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {job.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {job.execution_time ? `${job.execution_time.toFixed(2)}s` : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(job.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {recentJobs.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No jobs found. Run a demo to get started!
            </div>
          )}
        </div>
      </div>

      {/* Quantum Capabilities Info */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quantum Computing Capabilities</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">🔍 Search Algorithms</h4>
            <p className="text-sm text-gray-600">Quadratic speedup for unstructured search problems using Grover's algorithm.</p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">🎯 Optimization</h4>
            <p className="text-sm text-gray-600">Advanced optimization using QAOA and quantum annealing techniques.</p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">🧮 Machine Learning</h4>
            <p className="text-sm text-gray-600">Quantum-enhanced machine learning algorithms for pattern recognition.</p>
          </div>
        </div>
      </div>
    </div>
  );
}