/**
 * iTechSmart Supreme Plus - Incidents Page
 * Incident management and AI analysis
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

import { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, Clock, Brain, Play } from 'lucide-react';
import axios from 'axios';
import IncidentCard from '../components/IncidentCard';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8034';

interface Incident {
  id: number;
  title: string;
  description: string;
  severity: string;
  status: string;
  source: string;
  created_at: string;
  resolved_at?: string;
}

export default function Incidents() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchIncidents();
  }, [filter]);

  const fetchIncidents = async () => {
    try {
      const params: any = {};
      if (filter !== 'all') {
        params.status = filter;
      }
      const response = await axios.get(`${API_URL}/api/incidents`, { params });
      setIncidents(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching incidents:', error);
      setLoading(false);
    }
  };

  const analyzeIncident = async (incidentId: number) => {
    try {
      await axios.post(`${API_URL}/api/incidents/${incidentId}/analyze`);
      alert('AI analysis completed successfully');
      fetchIncidents();
    } catch (error) {
      console.error('Error analyzing incident:', error);
      alert('Failed to analyze incident');
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-500 bg-red-900/20';
      case 'high': return 'text-orange-500 bg-orange-900/20';
      case 'medium': return 'text-yellow-500 bg-yellow-900/20';
      case 'low': return 'text-blue-500 bg-blue-900/20';
      default: return 'text-gray-500 bg-gray-900/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open': return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'resolved': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'in_progress': return <Clock className="w-5 h-5 text-blue-500" />;
      default: return <AlertTriangle className="w-5 h-5 text-gray-500" />;
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Incidents</h1>
          <p className="text-slate-400 mt-1">Manage and analyze infrastructure incidents</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          Create Incident
        </button>
      </div>

      {/* Filters */}
      <div className="flex space-x-2">
        {['all', 'open', 'in_progress', 'resolved'].map((status) => (
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

      {/* Incidents List */}
      <div className="space-y-4">
        {incidents.length === 0 ? (
          <div className="bg-slate-800 rounded-lg p-12 text-center border border-slate-700">
            <AlertTriangle className="w-12 h-12 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">No incidents found</p>
          </div>
        ) : (
          incidents.map((incident) => (
            <IncidentCard
              key={incident.id}
              incident={incident}
              onAnalyze={analyzeIncident}
              getSeverityColor={getSeverityColor}
              getStatusIcon={getStatusIcon}
            />
          ))
        )}
      </div>
    </div>
  );
}