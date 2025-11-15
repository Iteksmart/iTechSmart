/**
 * iTechSmart Supreme Plus - Remediations Page
 * Remediation execution and monitoring
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

import { useEffect, useState } from 'react';
import { Activity, CheckCircle, XCircle, Clock, Play } from 'lucide-react';
import axios from 'axios';
import RemediationLog from '../components/RemediationLog';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8034';

interface Remediation {
  id: number;
  incident_id: number;
  action_type: string;
  target_node_id: number;
  status: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  result?: any;
}

export default function Remediations() {
  const [remediations, setRemediations] = useState<Remediation[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    fetchRemediations();
    const interval = setInterval(fetchRemediations, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, [filter]);

  const fetchRemediations = async () => {
    try {
      const params: any = {};
      if (filter !== 'all') {
        params.status = filter;
      }
      const response = await axios.get(`${API_URL}/api/remediations`, { params });
      setRemediations(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching remediations:', error);
      setLoading(false);
    }
  };

  const executeRemediation = async (remediationId: number) => {
    try {
      await axios.post(`${API_URL}/api/remediations/${remediationId}/execute`);
      alert('Remediation execution started');
      fetchRemediations();
    } catch (error) {
      console.error('Error executing remediation:', error);
      alert('Failed to execute remediation');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-500 bg-green-900/20';
      case 'failed': return 'text-red-500 bg-red-900/20';
      case 'in_progress': return 'text-blue-500 bg-blue-900/20';
      case 'pending': return 'text-yellow-500 bg-yellow-900/20';
      default: return 'text-gray-500 bg-gray-900/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed': return <XCircle className="w-5 h-5 text-red-500" />;
      case 'in_progress': return <Activity className="w-5 h-5 text-blue-500 animate-pulse" />;
      case 'pending': return <Clock className="w-5 h-5 text-yellow-500" />;
      default: return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Remediations</h1>
        <p className="text-slate-400 mt-1">Auto-remediation execution and monitoring</p>
      </div>

      {/* Filters */}
      <div className="flex space-x-2">
        {['all', 'pending', 'in_progress', 'success', 'failed'].map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === status
                ? 'bg-blue-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Remediations List */}
      <div className="space-y-4">
        {remediations.length === 0 ? (
          <div className="bg-slate-800 rounded-lg p-12 text-center border border-slate-700">
            <Activity className="w-12 h-12 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">No remediations found</p>
          </div>
        ) : (
          remediations.map((remediation) => (
            <div
              key={remediation.id}
              className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-slate-600 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    {getStatusIcon(remediation.status)}
                    <h3 className="text-lg font-semibold text-white">
                      {remediation.action_type.replace(/_/g, ' ').toUpperCase()}
                    </h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(remediation.status)}`}>
                      {remediation.status}
                    </span>
                  </div>
                  <div className="space-y-1 text-sm text-slate-400">
                    <p>Incident ID: #{remediation.incident_id}</p>
                    <p>Target Node: #{remediation.target_node_id}</p>
                    <p>Created: {new Date(remediation.created_at).toLocaleString()}</p>
                    {remediation.completed_at && (
                      <p>Completed: {new Date(remediation.completed_at).toLocaleString()}</p>
                    )}
                  </div>
                  {remediation.result && (
                    <div className="mt-4">
                      <RemediationLog result={remediation.result} />
                    </div>
                  )}
                </div>
                {remediation.status === 'pending' && (
                  <button
                    onClick={() => executeRemediation(remediation.id)}
                    className="ml-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Execute
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}