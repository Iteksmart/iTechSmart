/**
 * iTechSmart Citadel - Compliance Page
 * Compliance management and policy enforcement
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

import { useEffect, useState } from 'react';
import { FileCheck, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8035';

interface CompliancePolicy {
  id: number;
  name: string;
  framework: string;
  description: string;
  enabled: boolean;
  created_at: string;
}

const frameworks = ['HIPAA', 'PCI-DSS', 'SOC2', 'ISO27001', 'NIST', 'GDPR'];

export default function Compliance() {
  const [policies, setPolicies] = useState<CompliancePolicy[]>([]);
  const [scores, setScores] = useState<{[key: string]: number}>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPolicies();
    fetchScores();
  }, []);

  const fetchPolicies = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/compliance/policies`);
      setPolicies(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching policies:', error);
      setLoading(false);
    }
  };

  const fetchScores = async () => {
    const newScores: {[key: string]: number} = {};
    for (const framework of frameworks) {
      try {
        const response = await axios.get(`${API_URL}/api/compliance/frameworks/${framework}/score`);
        newScores[framework] = response.data.score;
      } catch (error) {
        newScores[framework] = 0;
      }
    }
    setScores(newScores);
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-500';
    if (score >= 75) return 'text-yellow-500';
    return 'text-red-500';
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
          <h1 className="text-3xl font-bold text-white">Compliance Management</h1>
          <p className="text-gray-400 mt-1">Monitor compliance across frameworks</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
          Add Policy
        </button>
      </div>

      {/* Framework Scores */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {frameworks.map((framework) => (
          <div key={framework} className="bg-gray-900 rounded-lg p-4 border border-gray-800 text-center">
            <p className="text-gray-400 text-sm mb-2">{framework}</p>
            <p className={`text-2xl font-bold ${getScoreColor(scores[framework] || 0)}`}>
              {(scores[framework] || 0).toFixed(1)}%
            </p>
          </div>
        ))}
      </div>

      {/* Policies List */}
      <div className="space-y-4">
        {policies.length === 0 ? (
          <div className="bg-gray-900 rounded-lg p-12 text-center border border-gray-800">
            <FileCheck className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">No compliance policies configured</p>
          </div>
        ) : (
          policies.map((policy) => (
            <div key={policy.id} className="bg-gray-900 rounded-lg p-6 border border-gray-800 hover:border-gray-700 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <FileCheck className="w-5 h-5 text-blue-500" />
                    <h3 className="text-lg font-semibold text-white">{policy.name}</h3>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-900/20 text-purple-500">
                      {policy.framework}
                    </span>
                    {policy.enabled ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-500" />
                    )}
                  </div>
                  <p className="text-gray-400 mb-2">{policy.description}</p>
                  <p className="text-sm text-gray-500">Created: {new Date(policy.created_at).toLocaleDateString()}</p>
                </div>
                <button className="ml-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
                  Run Check
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}