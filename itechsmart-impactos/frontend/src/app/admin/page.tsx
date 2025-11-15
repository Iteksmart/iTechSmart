'use client';

import Link from 'next/link';
import { Users, Building2, Settings, Activity, TrendingUp, AlertCircle } from 'lucide-react';

export default function AdminDashboardPage() {
  const stats = {
    total_users: 156,
    total_organizations: 12,
    active_sessions: 45,
    system_health: 98
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">System overview and management</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <p className="text-sm text-gray-500">Total Users</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total_users}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <Building2 className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <p className="text-sm text-gray-500">Organizations</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total_organizations}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Activity className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <p className="text-sm text-gray-500">Active Sessions</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{stats.active_sessions}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-orange-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
          </div>
          <p className="text-sm text-gray-500">System Health</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{stats.system_health}%</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          href="/admin/users"
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">User Management</h3>
              <p className="text-sm text-gray-500">Manage user accounts</p>
            </div>
          </div>
        </Link>

        <Link
          href="/admin/organizations"
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <Building2 className="w-8 h-8 text-green-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Organizations</h3>
              <p className="text-sm text-gray-500">Manage organizations</p>
            </div>
          </div>
        </Link>

        <Link
          href="/admin/system"
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Settings className="w-8 h-8 text-purple-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">System Settings</h3>
              <p className="text-sm text-gray-500">Configure system</p>
            </div>
          </div>
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <div className="space-y-3">
          {[
            { action: 'New user registered', time: '5 minutes ago', type: 'info' },
            { action: 'Organization created', time: '1 hour ago', type: 'success' },
            { action: 'System backup completed', time: '2 hours ago', type: 'success' }
          ].map((activity, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <AlertCircle className={`w-5 h-5 ${
                  activity.type === 'success' ? 'text-green-600' : 'text-blue-600'
                }`} />
                <span className="text-sm text-gray-900">{activity.action}</span>
              </div>
              <span className="text-xs text-gray-500">{activity.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}