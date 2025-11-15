'use client';

import { useState } from 'react';
import {
  Shield,
  Plus,
  Search,
  Key,
  CreditCard,
  FileText,
  Globe,
  Lock,
  Eye,
  Star,
  AlertTriangle,
  TrendingUp,
  CheckCircle,
  Zap,
} from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const [searchQuery, setSearchQuery] = useState('');

  const stats = [
    { label: 'Total Items', value: '47', icon: Key, color: 'blue' },
    { label: 'Weak Passwords', value: '3', icon: AlertTriangle, color: 'red' },
    { label: 'Security Score', value: '92%', icon: Shield, color: 'green' },
    { label: 'Last Breach Check', value: '2h ago', icon: Eye, color: 'purple' },
  ];

  const recentItems = [
    {
      id: 1,
      title: 'Netflix',
      username: 'john@example.com',
      category: 'Entertainment',
      icon: '🎬',
      lastUsed: '2 hours ago',
      favorite: true,
    },
    {
      id: 2,
      title: 'Gmail',
      username: 'john.doe@gmail.com',
      category: 'Email',
      icon: '📧',
      lastUsed: '5 hours ago',
      favorite: true,
    },
    {
      id: 3,
      title: 'Bank of America',
      username: 'johndoe',
      category: 'Banking',
      icon: '🏦',
      lastUsed: '1 day ago',
      favorite: false,
    },
    {
      id: 4,
      title: 'Amazon',
      username: 'john@example.com',
      category: 'Shopping',
      icon: '🛒',
      lastUsed: '2 days ago',
      favorite: false,
    },
  ];

  const quickActions = [
    { label: 'Add Password', icon: Plus, href: '/dashboard/vault/add', color: 'blue' },
    { label: 'Generate Password', icon: Zap, href: '/dashboard/generator', color: 'purple' },
    { label: 'Security Check', icon: Shield, href: '/dashboard/security', color: 'green' },
    { label: 'Import Data', icon: FileText, href: '/dashboard/import', color: 'orange' },
  ];

  const securityAlerts = [
    {
      type: 'warning',
      message: '3 weak passwords detected',
      action: 'Fix Now',
      href: '/dashboard/security',
    },
    {
      type: 'info',
      message: 'Enable 2FA for better security',
      action: 'Enable',
      href: '/dashboard/settings',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black bg-opacity-30 backdrop-blur-lg border-b border-white border-opacity-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">PassPort</h1>
                <p className="text-xs text-blue-300">Your Digital Vault</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button className="p-2 text-white hover:bg-white hover:bg-opacity-10 rounded-lg transition-colors">
                <Search className="w-5 h-5" />
              </button>
              <Link
                href="/dashboard/settings"
                className="px-4 py-2 bg-white bg-opacity-10 text-white rounded-lg hover:bg-opacity-20 transition-colors"
              >
                Settings
              </Link>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">Welcome back, John! 👋</h2>
          <p className="text-blue-200">Your vault is secure and ready to use.</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            const colorClasses = {
              blue: 'from-blue-500 to-blue-600',
              red: 'from-red-500 to-red-600',
              green: 'from-green-500 to-green-600',
              purple: 'from-purple-500 to-purple-600',
            };

            return (
              <div
                key={index}
                className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-white border-opacity-10"
              >
                <div className="flex items-center justify-between mb-4">
                  <span className="text-gray-400 text-sm">{stat.label}</span>
                  <div
                    className={`w-10 h-10 bg-gradient-to-br ${
                      colorClasses[stat.color as keyof typeof colorClasses]
                    } rounded-lg flex items-center justify-center`}
                  >
                    <Icon className="w-5 h-5 text-white" />
                  </div>
                </div>
                <p className="text-3xl font-bold text-white">{stat.value}</p>
              </div>
            );
          })}
        </div>

        {/* Security Alerts */}
        {securityAlerts.length > 0 && (
          <div className="mb-8 space-y-4">
            {securityAlerts.map((alert, index) => (
              <div
                key={index}
                className={`bg-gradient-to-br ${
                  alert.type === 'warning'
                    ? 'from-orange-900 to-red-900'
                    : 'from-blue-900 to-indigo-900'
                } bg-opacity-30 rounded-xl p-4 border ${
                  alert.type === 'warning' ? 'border-orange-500' : 'border-blue-500'
                } border-opacity-30 flex items-center justify-between`}
              >
                <div className="flex items-center gap-3">
                  {alert.type === 'warning' ? (
                    <AlertTriangle className="w-5 h-5 text-orange-400" />
                  ) : (
                    <CheckCircle className="w-5 h-5 text-blue-400" />
                  )}
                  <span className="text-white">{alert.message}</span>
                </div>
                <Link
                  href={alert.href}
                  className="px-4 py-2 bg-white bg-opacity-10 text-white rounded-lg hover:bg-opacity-20 transition-colors text-sm font-medium"
                >
                  {alert.action}
                </Link>
              </div>
            ))}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Quick Actions */}
            <div>
              <h3 className="text-xl font-bold text-white mb-4">Quick Actions</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {quickActions.map((action, index) => {
                  const Icon = action.icon;
                  const colorClasses = {
                    blue: 'from-blue-500 to-blue-600',
                    purple: 'from-purple-500 to-purple-600',
                    green: 'from-green-500 to-green-600',
                    orange: 'from-orange-500 to-red-600',
                  };

                  return (
                    <Link
                      key={index}
                      href={action.href}
                      className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-white border-opacity-10 hover:border-opacity-30 transition-all text-center group"
                    >
                      <div
                        className={`w-12 h-12 bg-gradient-to-br ${
                          colorClasses[action.color as keyof typeof colorClasses]
                        } rounded-lg flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform`}
                      >
                        <Icon className="w-6 h-6 text-white" />
                      </div>
                      <p className="text-white font-medium text-sm">{action.label}</p>
                    </Link>
                  );
                })}
              </div>
            </div>

            {/* Recent Items */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white">Recent Items</h3>
                <Link
                  href="/dashboard/vault"
                  className="text-blue-400 hover:text-blue-300 text-sm font-medium"
                >
                  View All →
                </Link>
              </div>
              <div className="space-y-3">
                {recentItems.map((item) => (
                  <div
                    key={item.id}
                    className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-4 border border-white border-opacity-10 hover:border-opacity-30 transition-all cursor-pointer group"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="text-3xl">{item.icon}</div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="text-white font-semibold">{item.title}</h4>
                            {item.favorite && <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />}
                          </div>
                          <p className="text-gray-400 text-sm">{item.username}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-xs text-gray-400 block mb-1">{item.category}</span>
                        <span className="text-xs text-blue-400">{item.lastUsed}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Security Score */}
            <div className="bg-gradient-to-br from-green-900 to-emerald-900 bg-opacity-30 rounded-xl p-6 border border-green-500 border-opacity-30">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white font-bold">Security Score</h3>
                <Shield className="w-6 h-6 text-green-400" />
              </div>
              <div className="relative w-32 h-32 mx-auto mb-4">
                <svg className="transform -rotate-90 w-32 h-32">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="transparent"
                    className="text-green-900"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="transparent"
                    strokeDasharray={`${2 * Math.PI * 56}`}
                    strokeDashoffset={`${2 * Math.PI * 56 * (1 - 0.92)}`}
                    className="text-green-400"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-3xl font-bold text-white">92%</span>
                </div>
              </div>
              <p className="text-green-200 text-center text-sm">Excellent security posture</p>
              <Link
                href="/dashboard/security"
                className="mt-4 block w-full py-2 bg-green-500 bg-opacity-20 text-green-300 rounded-lg hover:bg-opacity-30 transition-colors text-center text-sm font-medium"
              >
                View Details
              </Link>
            </div>

            {/* Categories */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-white border-opacity-10">
              <h3 className="text-white font-bold mb-4">Categories</h3>
              <div className="space-y-3">
                {[
                  { name: 'Logins', count: 32, icon: Key },
                  { name: 'Credit Cards', count: 5, icon: CreditCard },
                  { name: 'Secure Notes', count: 8, icon: FileText },
                  { name: 'Identities', count: 2, icon: Globe },
                ].map((category, index) => {
                  const Icon = category.icon;
                  return (
                    <Link
                      key={index}
                      href={`/dashboard/vault?category=${category.name.toLowerCase()}`}
                      className="flex items-center justify-between p-3 bg-slate-700 bg-opacity-30 rounded-lg hover:bg-opacity-50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <Icon className="w-5 h-5 text-blue-400" />
                        <span className="text-white">{category.name}</span>
                      </div>
                      <span className="text-gray-400 text-sm">{category.count}</span>
                    </Link>
                  );
                })}
              </div>
            </div>

            {/* Upgrade CTA */}
            <div className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl p-6">
              <h3 className="text-white font-bold mb-2">Upgrade to Pro</h3>
              <p className="text-blue-100 text-sm mb-4">
                Get advanced features like team sharing and priority support for just $3/month.
              </p>
              <Link
                href="/pricing"
                className="block w-full py-2 bg-white text-purple-600 rounded-lg hover:bg-blue-50 transition-colors text-center font-semibold"
              >
                Upgrade Now
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}