'use client';

import { useState } from 'react';
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  TrendingUp,
  Lock,
  Eye,
  RefreshCw,
  Zap,
  Key,
} from 'lucide-react';
import Link from 'next/link';

export default function SecurityPage() {
  const [isScanning, setIsScanning] = useState(false);

  const securityScore = 92;

  const issues = [
    {
      severity: 'high',
      title: 'Weak Password Detected',
      description: 'Amazon account has a weak password',
      action: 'Update Password',
      count: 1,
    },
    {
      severity: 'medium',
      title: 'Reused Passwords',
      description: '2 accounts share the same password',
      action: 'Generate Unique',
      count: 2,
    },
    {
      severity: 'low',
      title: 'Old Passwords',
      description: '5 passwords haven\'t been changed in 6+ months',
      action: 'Review',
      count: 5,
    },
  ];

  const breachCheck = {
    lastCheck: '2 hours ago',
    breachesFound: 0,
    accountsChecked: 47,
  };

  const passwordHealth = [
    { label: 'Strong', count: 32, percentage: 68, color: 'green' },
    { label: 'Good', count: 10, percentage: 21, color: 'yellow' },
    { label: 'Fair', count: 3, percentage: 6, color: 'orange' },
    { label: 'Weak', count: 2, percentage: 4, color: 'red' },
  ];

  const recommendations = [
    {
      icon: RefreshCw,
      title: 'Enable Auto-Rotation',
      description: 'Let AI automatically update weak passwords',
      action: 'Enable',
    },
    {
      icon: Shield,
      title: 'Add 2FA to Critical Accounts',
      description: 'Secure your banking and email with two-factor authentication',
      action: 'Setup',
    },
    {
      icon: Eye,
      title: 'Review Shared Passwords',
      description: 'Check which passwords are shared with family members',
      action: 'Review',
    },
  ];

  const handleScan = async () => {
    setIsScanning(true);
    await new Promise((resolve) => setTimeout(resolve, 3000));
    setIsScanning(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black bg-opacity-30 backdrop-blur-lg border-b border-white border-opacity-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/dashboard" className="text-blue-400 hover:text-blue-300">
                ← Back
              </Link>
              <h1 className="text-2xl font-bold text-white">Security Center</h1>
            </div>
            <button
              onClick={handleScan}
              disabled={isScanning}
              className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all flex items-center gap-2 disabled:opacity-50"
            >
              <RefreshCw className={`w-5 h-5 ${isScanning ? 'animate-spin' : ''}`} />
              {isScanning ? 'Scanning...' : 'Run Security Scan'}
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Security Score */}
        <div className="bg-gradient-to-br from-green-900 to-emerald-900 bg-opacity-30 rounded-2xl p-8 border border-green-500 border-opacity-30 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Security Score</h2>
              <p className="text-green-200">Your vault security is excellent</p>
            </div>
            <Shield className="w-12 h-12 text-green-400" />
          </div>

          <div className="flex items-center gap-8">
            <div className="relative w-40 h-40">
              <svg className="transform -rotate-90 w-40 h-40">
                <circle
                  cx="80"
                  cy="80"
                  r="70"
                  stroke="currentColor"
                  strokeWidth="12"
                  fill="transparent"
                  className="text-green-900"
                />
                <circle
                  cx="80"
                  cy="80"
                  r="70"
                  stroke="currentColor"
                  strokeWidth="12"
                  fill="transparent"
                  strokeDasharray={`${2 * Math.PI * 70}`}
                  strokeDashoffset={`${2 * Math.PI * 70 * (1 - securityScore / 100)}`}
                  className="text-green-400"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center flex-col">
                <span className="text-4xl font-bold text-white">{securityScore}</span>
                <span className="text-green-300 text-sm">/ 100</span>
              </div>
            </div>

            <div className="flex-1 grid grid-cols-3 gap-4">
              {[
                { label: 'Strong Passwords', value: '32/47', icon: CheckCircle, color: 'green' },
                { label: 'Weak Passwords', value: '2', icon: AlertTriangle, color: 'red' },
                { label: 'Reused Passwords', value: '2', icon: XCircle, color: 'orange' },
              ].map((stat, index) => {
                const Icon = stat.icon;
                return (
                  <div key={index} className="bg-black bg-opacity-30 rounded-lg p-4">
                    <Icon className={`w-6 h-6 text-${stat.color}-400 mb-2`} />
                    <p className="text-2xl font-bold text-white mb-1">{stat.value}</p>
                    <p className="text-sm text-gray-300">{stat.label}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Security Issues */}
            <div>
              <h3 className="text-xl font-bold text-white mb-4">Security Issues</h3>
              <div className="space-y-4">
                {issues.map((issue, index) => {
                  const severityColors = {
                    high: 'from-red-900 to-orange-900 border-red-500',
                    medium: 'from-orange-900 to-yellow-900 border-orange-500',
                    low: 'from-yellow-900 to-amber-900 border-yellow-500',
                  };

                  return (
                    <div
                      key={index}
                      className={`bg-gradient-to-br ${
                        severityColors[issue.severity as keyof typeof severityColors]
                      } bg-opacity-30 rounded-xl p-6 border border-opacity-30`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <AlertTriangle className="w-5 h-5 text-orange-400" />
                            <h4 className="text-white font-semibold">{issue.title}</h4>
                            <span className="px-2 py-1 bg-black bg-opacity-30 rounded-full text-xs text-white">
                              {issue.count} {issue.count === 1 ? 'item' : 'items'}
                            </span>
                          </div>
                          <p className="text-gray-300 text-sm">{issue.description}</p>
                        </div>
                        <button className="px-4 py-2 bg-white bg-opacity-10 text-white rounded-lg hover:bg-opacity-20 transition-colors text-sm font-medium">
                          {issue.action}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Password Health */}
            <div>
              <h3 className="text-xl font-bold text-white mb-4">Password Health</h3>
              <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-white border-opacity-10">
                <div className="space-y-4">
                  {passwordHealth.map((item, index) => {
                    const colorClasses = {
                      green: 'bg-green-500',
                      yellow: 'bg-yellow-500',
                      orange: 'bg-orange-500',
                      red: 'bg-red-500',
                    };

                    return (
                      <div key={index}>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-white font-medium">{item.label}</span>
                          <span className="text-gray-400 text-sm">
                            {item.count} ({item.percentage}%)
                          </span>
                        </div>
                        <div className="w-full h-3 bg-gray-700 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${
                              colorClasses[item.color as keyof typeof colorClasses]
                            } transition-all`}
                            style={{ width: `${item.percentage}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Breach Check */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-white border-opacity-10">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white font-bold">Breach Monitoring</h3>
                <Eye className="w-6 h-6 text-blue-400" />
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-sm">Last Check</span>
                  <span className="text-white text-sm">{breachCheck.lastCheck}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-sm">Breaches Found</span>
                  <span className="text-green-400 text-sm font-bold">
                    {breachCheck.breachesFound}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-sm">Accounts Checked</span>
                  <span className="text-white text-sm">{breachCheck.accountsChecked}</span>
                </div>
              </div>
              <button className="mt-4 w-full py-2 bg-blue-500 bg-opacity-20 text-blue-300 rounded-lg hover:bg-opacity-30 transition-colors text-sm font-medium">
                Check Now
              </button>
            </div>

            {/* Recommendations */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-white border-opacity-10">
              <h3 className="text-white font-bold mb-4">Recommendations</h3>
              <div className="space-y-4">
                {recommendations.map((rec, index) => {
                  const Icon = rec.icon;
                  return (
                    <div key={index} className="pb-4 border-b border-gray-700 last:border-0 last:pb-0">
                      <div className="flex items-start gap-3 mb-2">
                        <Icon className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <h4 className="text-white font-medium text-sm mb-1">{rec.title}</h4>
                          <p className="text-gray-400 text-xs mb-2">{rec.description}</p>
                          <button className="text-blue-400 hover:text-blue-300 text-xs font-medium">
                            {rec.action} →
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-gradient-to-br from-blue-900 to-indigo-900 bg-opacity-30 rounded-xl p-6 border border-blue-500 border-opacity-30">
              <h3 className="text-white font-bold mb-4">Quick Stats</h3>
              <div className="space-y-3">
                {[
                  { label: 'Total Passwords', value: '47' },
                  { label: 'Avg. Password Age', value: '4.2 months' },
                  { label: 'Last Password Update', value: '2 days ago' },
                  { label: '2FA Enabled', value: '12/47' },
                ].map((stat, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-blue-200 text-sm">{stat.label}</span>
                    <span className="text-white font-semibold text-sm">{stat.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}