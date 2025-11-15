/**
 * iTechSmart Supreme Plus - Integrations Page
 * Integration management for monitoring systems
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

import { useEffect, useState } from 'react';
import { Settings, CheckCircle, XCircle, Plus, TestTube } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8034';

interface Integration {
  id: number;
  name: string;
  integration_type: string;
  enabled: boolean;
  last_sync?: string;
  created_at: string;
}

export default function Integrations() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchIntegrations();
  }, []);

  const fetchIntegrations = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/integrations`);
      setIntegrations(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching integrations:', error);
      setLoading(false);
    }
  };

  const testIntegration = async (integrationId: number) => {
    try {
      const response = await axios.post(`${API_URL}/api/integrations/${integrationId}/test`);
      if (response.data.success) {
        alert('Integration test successful!');
      } else {
        alert(`Integration test failed: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Error testing integration:', error);
      alert('Failed to test integration');
    }
  };

  const toggleIntegration = async (integrationId: number, enabled: boolean) => {
    try {
      await axios.put(`${API_URL}/api/integrations/${integrationId}`, { enabled: !enabled });
      fetchIntegrations();
    } catch (error) {
      console.error('Error toggling integration:', error);
      alert('Failed to toggle integration');
    }
  };

  const getIntegrationIcon = (type: string) => {
    // Return appropriate icon based on integration type
    return <Settings className="w-6 h-6" />;
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
          <h1 className="text-3xl font-bold text-white">Integrations</h1>
          <p className="text-slate-400 mt-1">Connect with monitoring and alerting systems</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          Add Integration
        </button>
      </div>

      {/* Integration Types Info */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-lg font-semibold text-white mb-4">Supported Integrations</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {['Prometheus', 'Wazuh', 'Grafana', 'Elasticsearch', 'Splunk', 'Datadog', 'New Relic', 'PagerDuty', 'Slack', 'Webhook'].map((type) => (
            <div key={type} className="bg-slate-700 rounded-lg p-3 text-center">
              <p className="text-slate-300 text-sm font-medium">{type}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Integrations List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {integrations.length === 0 ? (
          <div className="col-span-2 bg-slate-800 rounded-lg p-12 text-center border border-slate-700">
            <Settings className="w-12 h-12 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">No integrations configured</p>
            <button className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
              Add Your First Integration
            </button>
          </div>
        ) : (
          integrations.map((integration) => (
            <div
              key={integration.id}
              className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-slate-600 transition-colors"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-slate-700 rounded-lg">
                    {getIntegrationIcon(integration.integration_type)}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">{integration.name}</h3>
                    <p className="text-sm text-slate-400">{integration.integration_type}</p>
                  </div>
                </div>
                {integration.enabled ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-500" />
                )}
              </div>

              <div className="space-y-2 text-sm text-slate-400 mb-4">
                <p>Status: {integration.enabled ? 'Enabled' : 'Disabled'}</p>
                <p>Created: {new Date(integration.created_at).toLocaleDateString()}</p>
                {integration.last_sync && (
                  <p>Last Sync: {new Date(integration.last_sync).toLocaleString()}</p>
                )}
              </div>

              <div className="flex space-x-2">
                <button
                  onClick={() => testIntegration(integration.id)}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center"
                >
                  <TestTube className="w-4 h-4 mr-2" />
                  Test
                </button>
                <button
                  onClick={() => toggleIntegration(integration.id, integration.enabled)}
                  className={`flex-1 font-medium py-2 px-4 rounded-lg transition-colors ${
                    integration.enabled
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-green-600 hover:bg-green-700 text-white'
                  }`}
                >
                  {integration.enabled ? 'Disable' : 'Enable'}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}