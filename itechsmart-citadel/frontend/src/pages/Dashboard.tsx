/**
 * iTechSmart Citadel - Dashboard Page
 * Overview of security posture and system health
 * 
 * Copyright (c) 2025 iTechSmart Suite
 * Launch Date: August 8, 2025
 */

import { useEffect, useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, Activity, Lock, Database } from 'lucide-react';
import axios from 'axios';
import SecurityStatus from '../components/SecurityStatus';
import ThreatMap from '../components/ThreatMap';
import ComplianceScore from '../components/ComplianceScore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8035';

interface Stats {
  security_events: {
    total: number;
    open: number;
    resolved: number;
  };
  threat_intelligence: {
    active_indicators: number;
  };
  compliance: {
    active_policies: number;
  };
  vulnerabilities: {
    open: number;
  };
}

function StatCard({ title, value, subtitle, icon: Icon, color }: any) {
  return (
    <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium">{title}</p>
          <p className={`text-3xl font-bold mt-2 ${color}`}>{value}</p>
          {subtitle && <p className="text-gray-500 text-sm mt-1">{subtitle}</p>}
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
    const interval = setInterval(fetchStats, 30000);
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
        <h1 className="text-3xl font-bold text-white">Security Dashboard</h1>
        <p className="text-gray-400 mt-1">Sovereign Digital Infrastructure Overview</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Open Security Events"
          value={stats?.security_events.open || 0}
          subtitle={`${stats?.security_events.total || 0} total`}
          icon={AlertTriangle}
          color="text-red-500"
        />
        <StatCard
          title="Threat Indicators"
          value={stats?.threat_intelligence.active_indicators || 0}
          subtitle="Active threats"
          icon={Shield}
          color="text-orange-500"
        />
        <StatCard
          title="Compliance Policies"
          value={stats?.compliance.active_policies || 0}
          subtitle="Active frameworks"
          icon={CheckCircle}
          color="text-green-500"
        />
        <StatCard
          title="Open Vulnerabilities"
          value={stats?.vulnerabilities.open || 0}
          subtitle="Requiring attention"
          icon={Activity}
          color="text-yellow-500"
        />
      </div>

      {/* Security Features */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
          <div className="flex items-center space-x-3 mb-4">
            <Lock className="w-6 h-6 text-blue-500" />
            <h2 className="text-xl font-semibold text-white">Post-Quantum Crypto</h2>
          </div>
          <p className="text-gray-400 mb-4">CRYSTALS-Kyber encryption active</p>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">Algorithm</span>
              <span className="text-green-500 font-semibold">Active</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">Key Rotation</span>
              <span className="text-green-500 font-semibold">Enabled</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
          <div className="flex items-center space-x-3 mb-4">
            <Shield className="w-6 h-6 text-purple-500" />
            <h2 className="text-xl font-semibold text-white">Zero Trust</h2>
          </div>
          <p className="text-gray-400 mb-4">All access verified and encrypted</p>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">MFA Required</span>
              <span className="text-green-500 font-semibold">Yes</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">Session Timeout</span>
              <span className="text-green-500 font-semibold">15 min</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
          <div className="flex items-center space-x-3 mb-4">
            <Database className="w-6 h-6 text-cyan-500" />
            <h2 className="text-xl font-semibold text-white">Immutable Backup</h2>
          </div>
          <p className="text-gray-400 mb-4">Ransomware-proof data protection</p>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">Encryption</span>
              <span className="text-green-500 font-semibold">AES-256</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">Retention</span>
              <span className="text-green-500 font-semibold">90 days</span>
            </div>
          </div>
        </div>
      </div>

      {/* Security Status & Threat Map */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
          <h2 className="text-xl font-semibold text-white mb-4">Security Status</h2>
          <SecurityStatus />
        </div>

        <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
          <h2 className="text-xl font-semibold text-white mb-4">Threat Activity</h2>
          <ThreatMap />
        </div>
      </div>

      {/* Compliance Score */}
      <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
        <h2 className="text-xl font-semibold text-white mb-4">Compliance Overview</h2>
        <ComplianceScore />
      </div>
    </div>
  );
}