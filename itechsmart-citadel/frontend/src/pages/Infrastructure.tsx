/**
 * iTechSmart Citadel - Infrastructure Page
 * Infrastructure asset monitoring and management
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

import { useEffect, useState } from 'react';
import { Server, HardDrive, Lock } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8035';

interface Asset {
  id: number;
  asset_type: string;
  name: string;
  hostname: string;
  ip_address: string;
  environment: string;
  criticality: string;
  status: string;
}

export default function Infrastructure() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/monitoring/assets`);
      setAssets(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching assets:', error);
      setLoading(false);
    }
  };

  const getCriticalityColor = (criticality: string) => {
    switch (criticality) {
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Infrastructure Assets</h1>
          <p className="text-gray-400 mt-1">Monitor and manage infrastructure</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
          Add Asset
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {assets.length === 0 ? (
          <div className="col-span-2 bg-gray-900 rounded-lg p-12 text-center border border-gray-800">
            <Server className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">No infrastructure assets configured</p>
          </div>
        ) : (
          assets.map((asset) => (
            <div key={asset.id} className="bg-gray-900 rounded-lg p-6 border border-gray-800 hover:border-gray-700 transition-colors">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-gray-800 rounded-lg">
                    <Server className="w-6 h-6 text-blue-500" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">{asset.name}</h3>
                    <p className="text-sm text-gray-400">{asset.hostname}</p>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  asset.status === 'active' ? 'bg-green-900/20 text-green-500' : 'bg-red-900/20 text-red-500'
                }`}>
                  {asset.status}
                </span>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Type</span>
                  <span className="text-white">{asset.asset_type}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">IP Address</span>
                  <span className="text-white font-mono">{asset.ip_address}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Environment</span>
                  <span className="text-white">{asset.environment}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Criticality</span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getCriticalityColor(asset.criticality)}`}>
                    {asset.criticality}
                  </span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-800 flex space-x-2">
                <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-3 rounded transition-colors">
                  Scan
                </button>
                <button className="flex-1 bg-gray-800 hover:bg-gray-700 text-white text-sm font-medium py-2 px-3 rounded transition-colors">
                  Details
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}