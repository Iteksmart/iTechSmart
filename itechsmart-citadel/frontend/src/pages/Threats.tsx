/**
 * iTechSmart Citadel - Threats Page
 * Threat intelligence and vulnerability management
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

import { useEffect, useState } from 'react';
import { AlertTriangle, Shield, Bug } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8035';

interface ThreatIndicator {
  id: number;
  threat_type: string;
  indicator: string;
  indicator_type: string;
  confidence: number;
  severity: string;
  last_seen: string;
}

interface Vulnerability {
  id: number;
  title: string;
  severity: string;
  cve_id: string;
  cvss_score: number;
  status: string;
  discovered_at: string;
}

export default function Threats() {
  const [indicators, setIndicators] = useState<ThreatIndicator[]>([]);
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('indicators');

  useEffect(() => {
    fetchIndicators();
    fetchVulnerabilities();
  }, []);

  const fetchIndicators = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/threats/indicators`);
      setIndicators(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching indicators:', error);
      setLoading(false);
    }
  };

  const fetchVulnerabilities = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/threats/vulnerabilities`);
      setVulnerabilities(response.data);
    } catch (error) {
      console.error('Error fetching vulnerabilities:', error);
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

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Threat Intelligence</h1>
        <p className="text-gray-400 mt-1">Monitor threats and vulnerabilities</p>
      </div>

      <div className="flex space-x-2">
        <button
          onClick={() => setActiveTab('indicators')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'indicators' ? 'bg-blue-600 text-white' : 'bg-gray-900 text-gray-300 hover:bg-gray-800'
          }`}
        >
          Threat Indicators
        </button>
        <button
          onClick={() => setActiveTab('vulnerabilities')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'vulnerabilities' ? 'bg-blue-600 text-white' : 'bg-gray-900 text-gray-300 hover:bg-gray-800'
          }`}
        >
          Vulnerabilities
        </button>
      </div>

      {activeTab === 'indicators' && (
        <div className="space-y-4">
          {indicators.length === 0 ? (
            <div className="bg-gray-900 rounded-lg p-12 text-center border border-gray-800">
              <Shield className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">No threat indicators found</p>
            </div>
          ) : (
            indicators.map((indicator) => (
              <div key={indicator.id} className="bg-gray-900 rounded-lg p-6 border border-gray-800">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <AlertTriangle className="w-5 h-5 text-red-500" />
                      <h3 className="text-lg font-semibold text-white">{indicator.threat_type.toUpperCase()}</h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getSeverityColor(indicator.severity)}`}>
                        {indicator.severity}
                      </span>
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-gray-800 text-gray-300">
                        Confidence: {(indicator.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-gray-400 mb-2 font-mono">{indicator.indicator}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>Type: {indicator.indicator_type}</span>
                      <span>•</span>
                      <span>Last Seen: {new Date(indicator.last_seen).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === 'vulnerabilities' && (
        <div className="space-y-4">
          {vulnerabilities.length === 0 ? (
            <div className="bg-gray-900 rounded-lg p-12 text-center border border-gray-800">
              <Bug className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">No vulnerabilities found</p>
            </div>
          ) : (
            vulnerabilities.map((vuln) => (
              <div key={vuln.id} className="bg-gray-900 rounded-lg p-6 border border-gray-800">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <Bug className="w-5 h-5 text-orange-500" />
                      <h3 className="text-lg font-semibold text-white">{vuln.title}</h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getSeverityColor(vuln.severity)}`}>
                        {vuln.severity}
                      </span>
                      {vuln.cve_id && (
                        <span className="px-3 py-1 rounded-full text-xs font-medium bg-gray-800 text-gray-300">
                          {vuln.cve_id}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>CVSS: {vuln.cvss_score}</span>
                      <span>•</span>
                      <span>Status: {vuln.status}</span>
                      <span>•</span>
                      <span>Discovered: {new Date(vuln.discovered_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}