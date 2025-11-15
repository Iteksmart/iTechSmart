'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import {
  Cloud,
  CheckCircle,
  XCircle,
  Settings,
  Link as LinkIcon,
  Trash2,
  Plus,
  Mail,
  MessageSquare,
  Database,
} from 'lucide-react';

interface Integration {
  id: string;
  name: string;
  type: 'google_drive' | 'dropbox' | 'slack' | 'gmail';
  is_connected: boolean;
  connected_at: string | null;
  last_sync: string | null;
}

export default function IntegrationsPage() {
  const [showConnectModal, setShowConnectModal] = useState(false);
  const [selectedIntegration, setSelectedIntegration] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: integrations, isLoading } = useQuery({
    queryKey: ['integrations'],
    queryFn: async () => {
      const response = await api.get('/integrations');
      return response.data as Integration[];
    },
  });

  const connectIntegration = useMutation({
    mutationFn: async (type: string) => {
      const response = await api.post('/integrations/connect', { type });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      setShowConnectModal(false);
    },
  });

  const disconnectIntegration = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/integrations/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
    },
  });

  const availableIntegrations = [
    {
      type: 'google_drive',
      name: 'Google Drive',
      icon: Cloud,
      color: 'blue',
      description: 'Automatically create proofs for files in Google Drive',
      features: ['Auto-sync files', 'Folder monitoring', 'Real-time updates'],
    },
    {
      type: 'dropbox',
      name: 'Dropbox',
      icon: Database,
      color: 'indigo',
      description: 'Sync and verify files from your Dropbox account',
      features: ['Two-way sync', 'Selective folders', 'Version tracking'],
    },
    {
      type: 'slack',
      name: 'Slack',
      icon: MessageSquare,
      color: 'purple',
      description: 'Get notifications and share proofs in Slack',
      features: ['Verification alerts', 'Share proofs', 'Team collaboration'],
    },
    {
      type: 'gmail',
      name: 'Gmail',
      icon: Mail,
      color: 'red',
      description: 'Create proofs from email attachments automatically',
      features: ['Auto-proof attachments', 'Email notifications', 'Smart filters'],
    },
  ];

  const getIntegrationStatus = (type: string) => {
    return integrations?.find((i) => i.type === type);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Integrations</h1>
          <p className="text-gray-600">Connect ProofLink with your favorite tools</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm font-medium">Connected</span>
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {integrations?.filter((i) => i.is_connected).length || 0}
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm font-medium">Available</span>
              <Cloud className="w-5 h-5 text-blue-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{availableIntegrations.length}</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm font-medium">Last Sync</span>
              <LinkIcon className="w-5 h-5 text-purple-600" />
            </div>
            <p className="text-sm font-medium text-gray-900">2 hours ago</p>
          </div>
        </div>

        {/* Integrations Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {availableIntegrations.map((integration) => {
            const Icon = integration.icon;
            const status = getIntegrationStatus(integration.type);
            const isConnected = status?.is_connected;

            const colorClasses = {
              blue: 'from-blue-50 to-indigo-50 border-blue-100',
              indigo: 'from-indigo-50 to-purple-50 border-indigo-100',
              purple: 'from-purple-50 to-pink-50 border-purple-100',
              red: 'from-red-50 to-orange-50 border-red-100',
            };

            const iconColors = {
              blue: 'bg-blue-600',
              indigo: 'bg-indigo-600',
              purple: 'bg-purple-600',
              red: 'bg-red-600',
            };

            return (
              <div
                key={integration.type}
                className={`bg-gradient-to-br ${
                  colorClasses[integration.color as keyof typeof colorClasses]
                } rounded-xl p-6 border`}
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div
                      className={`p-3 ${
                        iconColors[integration.color as keyof typeof iconColors]
                      } rounded-lg`}
                    >
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">{integration.name}</h3>
                      {isConnected ? (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 mt-1">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Connected
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 mt-1">
                          <XCircle className="w-3 h-3 mr-1" />
                          Not Connected
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Description */}
                <p className="text-gray-700 mb-4">{integration.description}</p>

                {/* Features */}
                <ul className="space-y-2 mb-6">
                  {integration.features.map((feature, i) => (
                    <li key={i} className="flex items-center text-sm text-gray-700">
                      <CheckCircle className="w-4 h-4 text-green-600 mr-2 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>

                {/* Actions */}
                <div className="flex gap-3">
                  {isConnected ? (
                    <>
                      <button className="flex-1 px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 flex items-center justify-center gap-2">
                        <Settings className="w-4 h-4" />
                        Configure
                      </button>
                      <button
                        onClick={() => status && disconnectIntegration.mutate(status.id)}
                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
                      >
                        <Trash2 className="w-4 h-4" />
                        Disconnect
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => connectIntegration.mutate(integration.type)}
                      className="w-full px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 flex items-center justify-center gap-2 font-medium"
                    >
                      <Plus className="w-4 h-4" />
                      Connect {integration.name}
                    </button>
                  )}
                </div>

                {/* Last Sync */}
                {isConnected && status?.last_sync && (
                  <p className="mt-3 text-xs text-gray-600">
                    Last synced: {new Date(status.last_sync).toLocaleString()}
                  </p>
                )}
              </div>
            );
          })}
        </div>

        {/* Coming Soon */}
        <div className="mt-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-8 text-white text-center">
          <h2 className="text-2xl font-bold mb-2">More Integrations Coming Soon</h2>
          <p className="text-blue-100 mb-6">
            We're working on integrations with OneDrive, Box, Notion, and more!
          </p>
          <button className="px-6 py-3 bg-white text-blue-600 rounded-lg hover:bg-blue-50 font-semibold">
            Request an Integration
          </button>
        </div>
      </div>
    </div>
  );
}