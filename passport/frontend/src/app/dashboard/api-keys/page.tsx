"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Key,
  Plus,
  Copy,
  Eye,
  EyeOff,
  Trash2,
  Calendar,
  Activity,
  AlertCircle,
  Check,
} from "lucide-react";

interface APIKey {
  id: number;
  name: string;
  key_prefix: string;
  scopes: string[];
  is_active: boolean;
  expires_at?: string;
  last_used_at?: string;
  usage_count: number;
  created_at: string;
}

export default function APIKeysPage() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showKey, setShowKey] = useState<number | null>(null);
  const [copiedKey, setCopiedKey] = useState<number | null>(null);

  // Mock data
  const apiKeys: APIKey[] = [
    {
      id: 1,
      name: "Production API",
      key_prefix: "psp_abc123",
      scopes: ["read:passwords", "write:passwords"],
      is_active: true,
      expires_at: "2024-12-31T23:59:59Z",
      last_used_at: "2024-01-15T10:30:00Z",
      usage_count: 1234,
      created_at: "2024-01-01T00:00:00Z",
    },
    {
      id: 2,
      name: "Development API",
      key_prefix: "psp_def456",
      scopes: ["read:passwords"],
      is_active: true,
      last_used_at: "2024-01-14T15:20:00Z",
      usage_count: 567,
      created_at: "2024-01-05T00:00:00Z",
    },
    {
      id: 3,
      name: "Testing API",
      key_prefix: "psp_ghi789",
      scopes: ["read:passwords", "write:passwords", "delete:passwords"],
      is_active: false,
      expires_at: "2024-01-10T23:59:59Z",
      last_used_at: "2024-01-10T12:00:00Z",
      usage_count: 89,
      created_at: "2023-12-01T00:00:00Z",
    },
  ];

  const copyToClipboard = (keyId: number, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(keyId);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const isExpired = (expiresAt?: string) => {
    if (!expiresAt) return false;
    return new Date(expiresAt) < new Date();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">API Keys</h1>
          <p className="text-gray-400">
            Manage your API keys for programmatic access
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Keys</p>
                <p className="text-2xl font-bold text-white">{apiKeys.length}</p>
              </div>
              <Key className="w-8 h-8 text-blue-400" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Active Keys</p>
                <p className="text-2xl font-bold text-white">
                  {apiKeys.filter((k) => k.is_active).length}
                </p>
              </div>
              <Activity className="w-8 h-8 text-green-400" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Requests</p>
                <p className="text-2xl font-bold text-white">
                  {apiKeys.reduce((sum, k) => sum + k.usage_count, 0).toLocaleString()}
                </p>
              </div>
              <Activity className="w-8 h-8 text-purple-400" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Expired Keys</p>
                <p className="text-2xl font-bold text-orange-400">
                  {apiKeys.filter((k) => isExpired(k.expires_at)).length}
                </p>
              </div>
              <AlertCircle className="w-8 h-8 text-orange-400" />
            </div>
          </motion.div>
        </div>

        {/* Create Button */}
        <div className="mb-6">
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Create New API Key
          </button>
        </div>

        {/* API Keys List */}
        <div className="space-y-4">
          {apiKeys.map((apiKey, index) => (
            <motion.div
              key={apiKey.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                    <Key className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-1">
                      {apiKey.name}
                    </h3>
                    <div className="flex items-center gap-2">
                      <code className="px-2 py-1 bg-white/5 rounded text-sm text-gray-400 font-mono">
                        {apiKey.key_prefix}...
                      </code>
                      {apiKey.is_active ? (
                        <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs font-semibold">
                          Active
                        </span>
                      ) : (
                        <span className="px-2 py-1 bg-gray-500/20 text-gray-400 rounded text-xs font-semibold">
                          Inactive
                        </span>
                      )}
                      {isExpired(apiKey.expires_at) && (
                        <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-xs font-semibold">
                          Expired
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => copyToClipboard(apiKey.id, apiKey.key_prefix)}
                    className="p-2 bg-white/5 text-gray-400 rounded-lg hover:bg-white/10 hover:text-white transition-colors"
                    title="Copy API Key"
                  >
                    {copiedKey === apiKey.id ? (
                      <Check className="w-5 h-5 text-green-400" />
                    ) : (
                      <Copy className="w-5 h-5" />
                    )}
                  </button>
                  <button className="p-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors">
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Scopes */}
              <div className="mb-4">
                <p className="text-gray-400 text-sm mb-2">Scopes:</p>
                <div className="flex flex-wrap gap-2">
                  {apiKey.scopes.map((scope, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs font-medium"
                    >
                      {scope}
                    </span>
                  ))}
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-white/5 rounded-lg">
                <div>
                  <p className="text-gray-400 text-sm mb-1">Created</p>
                  <p className="text-white font-medium">
                    {new Date(apiKey.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm mb-1">Last Used</p>
                  <p className="text-white font-medium">
                    {apiKey.last_used_at
                      ? new Date(apiKey.last_used_at).toLocaleDateString()
                      : "Never"}
                  </p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm mb-1">Total Requests</p>
                  <p className="text-white font-medium">
                    {apiKey.usage_count.toLocaleString()}
                  </p>
                </div>
              </div>

              {/* Expiration */}
              {apiKey.expires_at && (
                <div className="mt-4 p-3 bg-orange-500/10 border border-orange-500/20 rounded-lg">
                  <div className="flex items-center gap-2 text-orange-400">
                    <Calendar className="w-4 h-4" />
                    <span className="text-sm">
                      {isExpired(apiKey.expires_at)
                        ? `Expired on ${new Date(apiKey.expires_at).toLocaleDateString()}`
                        : `Expires on ${new Date(apiKey.expires_at).toLocaleDateString()}`}
                    </span>
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </div>

        {/* Empty State */}
        {apiKeys.length === 0 && (
          <div className="text-center py-12">
            <Key className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">
              No API Keys Yet
            </h3>
            <p className="text-gray-400 mb-6">
              Create your first API key to start using the PassPort API
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all inline-flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Create Your First API Key
            </button>
          </div>
        )}

        {/* Create Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-slate-900 rounded-xl p-6 max-w-md w-full border border-white/20"
            >
              <h2 className="text-2xl font-bold text-white mb-4">
                Create New API Key
              </h2>

              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-gray-400 mb-2">Key Name</label>
                  <input
                    type="text"
                    placeholder="Production API"
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">Scopes</label>
                  <div className="space-y-2">
                    {[
                      "read:passwords",
                      "write:passwords",
                      "delete:passwords",
                      "read:profile",
                      "write:profile",
                    ].map((scope) => (
                      <label
                        key={scope}
                        className="flex items-center gap-2 text-white"
                      >
                        <input
                          type="checkbox"
                          className="w-4 h-4 rounded border-white/20 bg-white/5"
                        />
                        <span className="text-sm">{scope}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">
                    Expiration (Optional)
                  </label>
                  <select className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-blue-500">
                    <option value="">Never</option>
                    <option value="30">30 days</option>
                    <option value="90">90 days</option>
                    <option value="180">180 days</option>
                    <option value="365">1 year</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-3 bg-white/5 text-white rounded-lg hover:bg-white/10 transition-colors"
                >
                  Cancel
                </button>
                <button className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all">
                  Create Key
                </button>
              </div>
            </motion.div>
          </div>
        )}

        {/* Documentation */}
        <div className="mt-8 p-6 bg-blue-500/10 border border-blue-500/20 rounded-xl">
          <h3 className="text-lg font-semibold text-white mb-2">
            API Documentation
          </h3>
          <p className="text-gray-300 mb-4">
            Learn how to use the PassPort API to integrate password management
            into your applications.
          </p>
          <a
            href="/docs/api"
            className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors"
          >
            View API Documentation →
          </a>
        </div>
      </div>
    </div>
  );
}