/**
 * iTechSmart Supreme Plus - Monitoring Page
 * Infrastructure monitoring and metrics
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

import { useEffect, useState } from 'react';
import { Server, Activity, HardDrive, Cpu, Network } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8034';

interface Node {
  id: number;
  hostname: string;
  ip_address: string;
  node_type: string;
  os_type: string;
  status: string;
  last_seen?: string;
}

interface Metric {
  id: number;
  node_id: number;
  metric_name: string;
  value: number;
  unit: string;
  timestamp: string;
}

export default function Monitoring() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [metrics, setMetrics] = useState<{ [key: number]: Metric[] }>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNodes();
    const interval = setInterval(fetchNodes, 15000); // Refresh every 15 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchNodes = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/monitoring/nodes`);
      setNodes(response.data);
      
      // Fetch latest metrics for each node
      for (const node of response.data) {
        fetchNodeMetrics(node.id);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching nodes:', error);
      setLoading(false);
    }
  };

  const fetchNodeMetrics = async (nodeId: number) => {
    try {
      const response = await axios.get(`${API_URL}/api/monitoring/nodes/${nodeId}/metrics`, {
        params: { hours: 1 }
      });
      setMetrics(prev => ({ ...prev, [nodeId]: response.data }));
    } catch (error) {
      console.error(`Error fetching metrics for node ${nodeId}:`, error);
    }
  };

  const collectMetrics = async (nodeId: number) => {
    try {
      await axios.post(`${API_URL}/api/monitoring/nodes/${nodeId}/metrics/collect`);
      alert('Metrics collection started');
      fetchNodeMetrics(nodeId);
    } catch (error) {
      console.error('Error collecting metrics:', error);
      alert('Failed to collect metrics');
    }
  };

  const getMetricIcon = (metricName: string) => {
    switch (metricName) {
      case 'cpu_usage': return <Cpu className="w-4 h-4" />;
      case 'memory_usage': return <Activity className="w-4 h-4" />;
      case 'disk_usage': return <HardDrive className="w-4 h-4" />;
      case 'network_in':
      case 'network_out': return <Network className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const getMetricColor = (metricName: string, value: number) => {
    if (metricName.includes('usage')) {
      if (value >= 90) return 'text-red-500';
      if (value >= 75) return 'text-yellow-500';
      return 'text-green-500';
    }
    return 'text-blue-500';
  };

  const getLatestMetric = (nodeId: number, metricName: string): Metric | undefined => {
    const nodeMetrics = metrics[nodeId] || [];
    return nodeMetrics.find(m => m.metric_name === metricName);
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
          <h1 className="text-3xl font-bold text-white">Infrastructure Monitoring</h1>
          <p className="text-slate-400 mt-1">Real-time infrastructure health and metrics</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
          Add Node
        </button>
      </div>

      {/* Nodes Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {nodes.length === 0 ? (
          <div className="col-span-2 bg-slate-800 rounded-lg p-12 text-center border border-slate-700">
            <Server className="w-12 h-12 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">No nodes configured</p>
            <button className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
              Add Your First Node
            </button>
          </div>
        ) : (
          nodes.map((node) => {
            const cpuMetric = getLatestMetric(node.id, 'cpu_usage');
            const memoryMetric = getLatestMetric(node.id, 'memory_usage');
            const diskMetric = getLatestMetric(node.id, 'disk_usage');

            return (
              <div
                key={node.id}
                className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-slate-600 transition-colors"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-slate-700 rounded-lg">
                      <Server className="w-6 h-6 text-blue-500" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white">{node.hostname}</h3>
                      <p className="text-sm text-slate-400">{node.ip_address}</p>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    node.status === 'active' 
                      ? 'bg-green-900/20 text-green-500' 
                      : 'bg-red-900/20 text-red-500'
                  }`}>
                    {node.status}
                  </span>
                </div>

                <div className="space-y-2 text-sm text-slate-400 mb-4">
                  <p>Type: {node.node_type}</p>
                  <p>OS: {node.os_type}</p>
                  {node.last_seen && (
                    <p>Last Seen: {new Date(node.last_seen).toLocaleString()}</p>
                  )}
                </div>

                {/* Metrics */}
                <div className="space-y-3 mb-4">
                  {cpuMetric && (
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center space-x-2">
                          {getMetricIcon('cpu_usage')}
                          <span className="text-sm text-slate-300">CPU Usage</span>
                        </div>
                        <span className={`text-sm font-semibold ${getMetricColor('cpu_usage', cpuMetric.value)}`}>
                          {cpuMetric.value.toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-700 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            cpuMetric.value >= 90 ? 'bg-red-500' :
                            cpuMetric.value >= 75 ? 'bg-yellow-500' : 'bg-green-500'
                          }`}
                          style={{ width: `${cpuMetric.value}%` }}
                        ></div>
                      </div>
                    </div>
                  )}

                  {memoryMetric && (
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center space-x-2">
                          {getMetricIcon('memory_usage')}
                          <span className="text-sm text-slate-300">Memory Usage</span>
                        </div>
                        <span className={`text-sm font-semibold ${getMetricColor('memory_usage', memoryMetric.value)}`}>
                          {memoryMetric.value.toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-700 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            memoryMetric.value >= 90 ? 'bg-red-500' :
                            memoryMetric.value >= 75 ? 'bg-yellow-500' : 'bg-green-500'
                          }`}
                          style={{ width: `${memoryMetric.value}%` }}
                        ></div>
                      </div>
                    </div>
                  )}

                  {diskMetric && (
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center space-x-2">
                          {getMetricIcon('disk_usage')}
                          <span className="text-sm text-slate-300">Disk Usage</span>
                        </div>
                        <span className={`text-sm font-semibold ${getMetricColor('disk_usage', diskMetric.value)}`}>
                          {diskMetric.value.toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-700 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            diskMetric.value >= 90 ? 'bg-red-500' :
                            diskMetric.value >= 75 ? 'bg-yellow-500' : 'bg-green-500'
                          }`}
                          style={{ width: `${diskMetric.value}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>

                <button
                  onClick={() => collectMetrics(node.id)}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Collect Metrics
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}