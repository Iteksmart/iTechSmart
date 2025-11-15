import React, { useState, useEffect } from 'react';
import { Plus, Mail, MessageSquare, Smartphone, Bell, Settings, CheckCircle, XCircle, Edit2, Trash2 } from 'lucide-react';

interface Channel {
  id: string;
  name: string;
  type: string;
  enabled: boolean;
  config: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

const Channels: React.FC = () => {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingChannel, setEditingChannel] = useState<Channel | null>(null);

  const [formData, setFormData] = useState({
    name: '',
    type: 'email',
    enabled: true,
    config: {} as Record<string, any>
  });

  useEffect(() => {
    fetchChannels();
  }, []);

  const fetchChannels = async () => {
    try {
      const response = await fetch('/api/channels');
      const data = await response.json();
      setChannels(data.data || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching channels:', error);
      setLoading(false);
    }
  };

  const handleCreateChannel = async () => {
    try {
      const response = await fetch('/api/channels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        await fetchChannels();
        setShowModal(false);
        resetForm();
      }
    } catch (error) {
      console.error('Error creating channel:', error);
    }
  };

  const handleUpdateChannel = async () => {
    if (!editingChannel) return;

    try {
      const response = await fetch(`/api/channels/${editingChannel.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        await fetchChannels();
        setShowModal(false);
        setEditingChannel(null);
        resetForm();
      }
    } catch (error) {
      console.error('Error updating channel:', error);
    }
  };

  const handleDeleteChannel = async (id: string) => {
    if (!confirm('Are you sure you want to delete this channel?')) return;

    try {
      const response = await fetch(`/api/channels/${id}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        await fetchChannels();
      }
    } catch (error) {
      console.error('Error deleting channel:', error);
    }
  };

  const handleToggleChannel = async (channel: Channel) => {
    try {
      const response = await fetch(`/api/channels/${channel.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...channel, enabled: !channel.enabled })
      });

      if (response.ok) {
        await fetchChannels();
      }
    } catch (error) {
      console.error('Error toggling channel:', error);
    }
  };

  const openEditModal = (channel: Channel) => {
    setEditingChannel(channel);
    setFormData({
      name: channel.name,
      type: channel.type,
      enabled: channel.enabled,
      config: channel.config
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      type: 'email',
      enabled: true,
      config: {}
    });
    setEditingChannel(null);
  };

  const getChannelIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'email':
        return <Mail className="w-8 h-8 text-blue-600" />;
      case 'sms':
        return <MessageSquare className="w-8 h-8 text-green-600" />;
      case 'push':
        return <Smartphone className="w-8 h-8 text-purple-600" />;
      default:
        return <Bell className="w-8 h-8 text-orange-600" />;
    }
  };

  const getChannelColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'email':
        return 'bg-blue-100 border-blue-200';
      case 'sms':
        return 'bg-green-100 border-green-200';
      case 'push':
        return 'bg-purple-100 border-purple-200';
      default:
        return 'bg-orange-100 border-orange-200';
    }
  };

  const renderConfigFields = () => {
    switch (formData.type) {
      case 'email':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                SMTP Host
              </label>
              <input
                type="text"
                value={formData.config.host || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  config: { ...formData.config, host: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="smtp.example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                SMTP Port
              </label>
              <input
                type="number"
                value={formData.config.port || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  config: { ...formData.config, port: parseInt(e.target.value) }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="587"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <input
                type="text"
                value={formData.config.username || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  config: { ...formData.config, username: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="user@example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                type="password"
                value={formData.config.password || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  config: { ...formData.config, password: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="••••••••"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                From Address
              </label>
              <input
                type="email"
                value={formData.config.from || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  config: { ...formData.config, from: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="noreply@example.com"
              />
            </div>
          </>
        );
      case 'sms':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Provider
              </label>
              <select
                value={formData.config.provider || 'twilio'}
                onChange={(e) => setFormData({
                  ...formData,
                  config: { ...formData.config, provider: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="twilio">Twilio</option>
                <option value="nexmo">Nexmo</option>
                <option value="aws-sns">AWS SNS</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Account SID / API Key
              </label>
              <input
                type="text"
                value={formData.config.accountSid || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  config: { ...formData.config, accountSid: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Account SID or API Key"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Auth Token / API Secret
              </label>
              <input
                type="password"
                value={formData.config.authToken || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  config: { ...formData.config, authToken: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="••••••••"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                From Number
              </label>
              <input
                type="tel"
                value={formData.config.fromNumber || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  config: { ...formData.config, fromNumber: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="+1234567890"
              />
            </div>
          </>
        );
      case 'push':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Provider
              </label>
              <select
                value={formData.config.provider || 'fcm'}
                onChange={(e) => setFormData({
                  ...formData,
                  config: { ...formData.config, provider: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="fcm">Firebase Cloud Messaging</option>
                <option value="apns">Apple Push Notification Service</option>
                <option value="onesignal">OneSignal</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Server Key / API Key
              </label>
              <input
                type="password"
                value={formData.config.serverKey || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  config: { ...formData.config, serverKey: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="••••••••"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sender ID (Optional)
              </label>
              <input
                type="text"
                value={formData.config.senderId || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  config: { ...formData.config, senderId: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Sender ID"
              />
            </div>
          </>
        );
      case 'webhook':
        return (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Webhook URL
              </label>
              <input
                type="url"
                value={formData.config.url || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  config: { ...formData.config, url: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="https://api.example.com/webhook"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                HTTP Method
              </label>
              <select
                value={formData.config.method || 'POST'}
                onChange={(e) => setFormData({
                  ...formData,
                  config: { ...formData.config, method: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="POST">POST</option>
                <option value="PUT">PUT</option>
                <option value="PATCH">PATCH</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Authentication Header (Optional)
              </label>
              <input
                type="text"
                value={formData.config.authHeader || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  config: { ...formData.config, authHeader: e.target.value }
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Bearer token123..."
              />
            </div>
          </>
        );
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Channels</h1>
          <p className="mt-2 text-gray-600">Configure notification delivery channels</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>Add Channel</span>
        </button>
      </div>

      {/* Channels Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {channels.length === 0 ? (
          <div className="col-span-full text-center py-12 bg-white rounded-lg shadow">
            <Settings className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No channels configured</p>
            <button
              onClick={() => setShowModal(true)}
              className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
            >
              Add your first channel
            </button>
          </div>
        ) : (
          channels.map((channel) => (
            <div
              key={channel.id}
              className={`bg-white rounded-lg shadow hover:shadow-lg transition-shadow border-2 ${getChannelColor(channel.type)}`}
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    {getChannelIcon(channel.type)}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{channel.name}</h3>
                      <p className="text-sm text-gray-500 capitalize">{channel.type}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleToggleChannel(channel)}
                    className={`p-2 rounded-lg transition-colors ${
                      channel.enabled
                        ? 'text-green-600 bg-green-100 hover:bg-green-200'
                        : 'text-gray-400 bg-gray-100 hover:bg-gray-200'
                    }`}
                  >
                    {channel.enabled ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <XCircle className="w-5 h-5" />
                    )}
                  </button>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Status</span>
                    <span className={`font-medium ${channel.enabled ? 'text-green-600' : 'text-gray-400'}`}>
                      {channel.enabled ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Created</span>
                    <span className="text-gray-900">
                      {new Date(channel.createdAt).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-end space-x-2 pt-4 border-t border-gray-200">
                  <button
                    onClick={() => openEditModal(channel)}
                    className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Edit"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteChannel(channel.id)}
                    className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">
                {editingChannel ? 'Edit Channel' : 'Add Channel'}
              </h2>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Channel Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Production Email"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Channel Type
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value, config: {} })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={!!editingChannel}
                >
                  <option value="email">Email</option>
                  <option value="sms">SMS</option>
                  <option value="push">Push Notification</option>
                  <option value="webhook">Webhook</option>
                </select>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="enabled"
                  checked={formData.enabled}
                  onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="enabled" className="text-sm font-medium text-gray-700">
                  Enable this channel
                </label>
              </div>

              <div className="border-t border-gray-200 pt-4">
                <h3 className="text-sm font-medium text-gray-900 mb-4">Channel Configuration</h3>
                <div className="space-y-4">
                  {renderConfigFields()}
                </div>
              </div>
            </div>

            <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowModal(false);
                  setEditingChannel(null);
                  resetForm();
                }}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={editingChannel ? handleUpdateChannel : handleCreateChannel}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                {editingChannel ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Channels;