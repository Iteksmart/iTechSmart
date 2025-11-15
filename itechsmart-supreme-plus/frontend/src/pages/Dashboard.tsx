/**
 * iTechSmart Supreme Plus - Dashboard Page
 * Overview of incidents, remediations, and system health
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

import { useEffect, useState } from 'react';
import { AlertTriangle, Activity, CheckCircle, XCircle, TrendingUp, Server } from 'lucide-react';
import axios from 'axios';
import MetricsChart from '../components/MetricsChart';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8034';

interface Stats {
  incidents: {
    total: number;
    active: number;
    resolved: number;
  };
  remediations: {
    total: number;
    successful: number;
    failed: number;
    success_rate: number;
  };
  integrations: {
    active: number;
  };
}

function StatCard({ title, value, subtitle, icon: Icon, color }: any) {
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-slate-400 text-sm font-medium">{title}</p>
          <p className={`text-3xl font-bold mt-2 ${color}`}>{value}</p>
          {subtitle && <p className="text-slate-500 text-sm mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-lg ${color.replace('text-', 'bg-').replace('500', '900')}`}>
          <Icon className={`w-6 h-6 ${color}`} />
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/stats`);
      setStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching stats:', error);
      setLoading(false);
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
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-slate-400 mt-1">AI-Powered Infrastructure Auto-Remediation Overview</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Active Incidents"
          value={stats?.incidents.active || 0}
          subtitle={`${stats?.incidents.total || 0} total`}
          icon={AlertTriangle}
          color="text-yellow-500"
        />
        <StatCard
          title="Resolved Incidents"
          value={stats?.incidents.resolved || 0}
          subtitle="All time"
          icon={CheckCircle}
          color="text-green-500"
        />
        <StatCard
          title="Success Rate"
          value={`${stats?.remediations.success_rate || 0}%`}
          subtitle={`${stats?.remediations.successful || 0} successful`}
          icon={TrendingUp}
          color="text-blue-500"
        />
        <StatCard
          title="Active Integrations"
          value={stats?.integrations.active || 0}
          subtitle="Connected systems"
          icon={Server}
          color="text-purple-500"
        />
      </div>

      {/* Remediation Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-xl font-semibold text-white mb-4">Remediation Overview</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                <span className="text-slate-300">Successful</span>
              </div>
              <span className="text-white font-semibold">{stats?.remediations.successful || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <XCircle className="w-5 h-5 text-red-500 mr-2" />
                <span className="text-slate-300">Failed</span>
              </div>
              <span className="text-white font-semibold">{stats?.remediations.failed || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Activity className="w-5 h-5 text-blue-500 mr-2" />
                <span className="text-slate-300">Total</span>
              </div>
              <span className="text-white font-semibold">{stats?.remediations.total || 0}</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-xl font-semibold text-white mb-4">System Health</h2>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-300">Auto-Remediation</span>
                <span className="text-green-500 font-semibold">Active</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '100%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-300">AI Analysis</span>
                <span className="text-green-500 font-semibold">Operational</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '100%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-300">Monitoring</span>
                <span className="text-green-500 font-semibold">Active</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '100%' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Chart */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-xl font-semibold text-white mb-4">Incident Trends (Last 7 Days)</h2>
        <MetricsChart />
      </div>

      {/* Quick Actions */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors">
            Create Incident
          </button>
          <button className="bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-4 rounded-lg transition-colors">
            Run Diagnostics
          </button>
          <button className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 px-4 rounded-lg transition-colors">
            Add Integration
          </button>
        </div>
      </div>
    </div>
  );
}