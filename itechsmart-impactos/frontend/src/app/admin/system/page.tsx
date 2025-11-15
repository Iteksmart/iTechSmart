'use client';

import Link from 'next/link';
import { ArrowLeft, Save, Database, Server, Shield, Bell } from 'lucide-react';

export default function AdminSystemPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link href="/admin" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">System Settings</h1>
          <p className="mt-1 text-sm text-gray-500">Configure system-wide settings</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Database className="w-5 h-5 text-blue-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Database</h2>
          </div>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600 mb-2">Last Backup</p>
              <p className="text-sm font-medium text-gray-900">2 hours ago</p>
            </div>
            <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              Run Backup Now
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-green-100 rounded-lg">
              <Server className="w-5 h-5 text-green-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Server Status</h2>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">CPU Usage</span>
              <span className="text-sm font-medium text-gray-900">45%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Memory</span>
              <span className="text-sm font-medium text-gray-900">62%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Disk Space</span>
              <span className="text-sm font-medium text-gray-900">38%</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Shield className="w-5 h-5 text-purple-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Security</h2>
          </div>
          <div className="space-y-4">
            <label className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Two-Factor Authentication</span>
              <input type="checkbox" defaultChecked className="w-4 h-4 text-blue-600 rounded" />
            </label>
            <label className="flex items-center justify-between">
              <span className="text-sm text-gray-700">IP Whitelist</span>
              <input type="checkbox" className="w-4 h-4 text-blue-600 rounded" />
            </label>
            <label className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Session Timeout</span>
              <input type="checkbox" defaultChecked className="w-4 h-4 text-blue-600 rounded" />
            </label>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Bell className="w-5 h-5 text-orange-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Notifications</h2>
          </div>
          <div className="space-y-4">
            <label className="flex items-center justify-between">
              <span className="text-sm text-gray-700">System Alerts</span>
              <input type="checkbox" defaultChecked className="w-4 h-4 text-blue-600 rounded" />
            </label>
            <label className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Error Reports</span>
              <input type="checkbox" defaultChecked className="w-4 h-4 text-blue-600 rounded" />
            </label>
            <label className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Usage Reports</span>
              <input type="checkbox" className="w-4 h-4 text-blue-600 rounded" />
            </label>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-end">
        <button className="inline-flex items-center px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          <Save className="w-4 h-4 mr-2" />
          Save All Settings
        </button>
      </div>
    </div>
  );
}