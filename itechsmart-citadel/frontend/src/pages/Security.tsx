/**
 * iTechSmart Citadel - Security Page
 * Security event management and incident response
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

import { useEffect, useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8035';

interface SecurityEvent {
  id: number;
  event_type: string;
  severity: string;
  source: string;
  description: string;
  status: string;
  threat_level: number;
  detected_at: string;
}

export default function Security() {
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchEvents();
  }, [filter]);

  const fetchEvents = async () => {
    try {
      const params: any = {};
      if (filter !== 'all') params.status = filter;
      const response = await axios.get(`${API_URL}/api/security/events`, { params });
      setEvents(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching events:', error);
      setLoading(false);
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
      case 'open': return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'investigating': return <Shield className="w-5 h-5 text-yellow-500" />;
      case 'resolved': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'false_positive': return <XCircle className="w-5 h-5 text-gray-500" />;
      default: return <AlertTriangle className="w-5 h-5 text-gray-500" />;
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Security Events</h1>
          <p className="text-gray-400 mt-1">Monitor and respond to security incidents</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
          Create Event
        </button>
      </div>

      <div className="flex space-x-2">
        {['all', 'open', 'investigating', 'resolved'].map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === status ? 'bg-blue-600 text-white' : 'bg-gray-900 text-gray-300 hover:bg-gray-800'
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </button>
        ))}
      </div>

      <div className="space-y-4">
        {events.length === 0 ? (
          <div className="bg-gray-900 rounded-lg p-12 text-center border border-gray-800">
            <Shield className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">No security events found</p>
          </div>
        ) : (
          events.map((event) => (
            <div key={event.id} className="bg-gray-900 rounded-lg p-6 border border-gray-800 hover:border-gray-700 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    {getStatusIcon(event.status)}
                    <h3 className="text-lg font-semibold text-white">{event.event_type.replace(/_/g, ' ').toUpperCase()}</h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getSeverityColor(event.severity)}`}>
                      {event.severity}
                    </span>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-gray-800 text-gray-300">
                      Threat Level: {event.threat_level}
                    </span>
                  </div>
                  <p className="text-gray-400 mb-4">{event.description}</p>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>Source: {event.source}</span>
                    <span>•</span>
                    <span>Detected: {new Date(event.detected_at).toLocaleString()}</span>
                  </div>
                </div>
                <button className="ml-4 bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
                  Respond
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}