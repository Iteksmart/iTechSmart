import React, { useState, useEffect } from 'react';
import { Bell, Send, CheckCircle, XCircle, Clock, TrendingUp, Users, Mail, MessageSquare, Smartphone } from 'lucide-react';

interface NotificationStats {
  total: number;
  sent: number;
  delivered: number;
  failed: number;
  pending: number;
}

interface ChannelStats {
  email: number;
  sms: number;
  push: number;
  webhook: number;
}

interface RecentNotification {
  id: string;
  title: string;
  channel: string;
  status: string;
  timestamp: string;
  recipient: string;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<NotificationStats>({
    total: 0,
    sent: 0,
    delivered: 0,
    failed: 0,
    pending: 0
  });

  const [channelStats, setChannelStats] = useState<ChannelStats>({
    email: 0,
    sms: 0,
    push: 0,
    webhook: 0
  });

  const [recentNotifications, setRecentNotifications] = useState<RecentNotification[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch stats
      const statsResponse = await fetch('/api/notifications/stats');
      const statsData = await statsResponse.json();
      setStats(statsData);

      // Fetch channel stats
      const channelResponse = await fetch('/api/notifications/stats/channels');
      const channelData = await channelResponse.json();
      setChannelStats(channelData);

      // Fetch recent notifications
      const recentResponse = await fetch('/api/notifications?limit=10&sort=createdAt:desc');
      const recentData = await recentResponse.json();
      setRecentNotifications(recentData.data || []);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'delivered':
        return 'text-green-600 bg-green-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100';
      case 'sent':
        return 'text-blue-600 bg-blue-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getChannelIcon = (channel: string) => {
    switch (channel.toLowerCase()) {
      case 'email':
        return <Mail className="w-4 h-4" />;
      case 'sms':
        return <MessageSquare className="w-4 h-4" />;
      case 'push':
        return <Smartphone className="w-4 h-4" />;
      default:
        return <Bell className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const deliveryRate = stats.total > 0 ? ((stats.delivered / stats.total) * 100).toFixed(1) : '0';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Overview of your notification system</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Notifications</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total.toLocaleString()}</p>
            </div>
            <div className="bg-blue-100 rounded-full p-3">
              <Bell className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Sent</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{stats.sent.toLocaleString()}</p>
            </div>
            <div className="bg-indigo-100 rounded-full p-3">
              <Send className="w-6 h-6 text-indigo-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Delivered</p>
              <p className="text-3xl font-bold text-green-600 mt-2">{stats.delivered.toLocaleString()}</p>
            </div>
            <div className="bg-green-100 rounded-full p-3">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Failed</p>
              <p className="text-3xl font-bold text-red-600 mt-2">{stats.failed.toLocaleString()}</p>
            </div>
            <div className="bg-red-100 rounded-full p-3">
              <XCircle className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending</p>
              <p className="text-3xl font-bold text-yellow-600 mt-2">{stats.pending.toLocaleString()}</p>
            </div>
            <div className="bg-yellow-100 rounded-full p-3">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Delivery Rate & Channel Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Delivery Rate */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Delivery Rate</h2>
            <TrendingUp className="w-5 h-5 text-green-600" />
          </div>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <p className="text-5xl font-bold text-green-600">{deliveryRate}%</p>
              <p className="text-sm text-gray-600 mt-2">Overall delivery success rate</p>
            </div>
          </div>
        </div>

        {/* Channel Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Channel Distribution</h2>
            <Users className="w-5 h-5 text-blue-600" />
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Mail className="w-5 h-5 text-blue-600" />
                <span className="text-sm font-medium text-gray-700">Email</span>
              </div>
              <span className="text-sm font-bold text-gray-900">{channelStats.email.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <MessageSquare className="w-5 h-5 text-green-600" />
                <span className="text-sm font-medium text-gray-700">SMS</span>
              </div>
              <span className="text-sm font-bold text-gray-900">{channelStats.sms.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Smartphone className="w-5 h-5 text-purple-600" />
                <span className="text-sm font-medium text-gray-700">Push</span>
              </div>
              <span className="text-sm font-bold text-gray-900">{channelStats.push.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Bell className="w-5 h-5 text-orange-600" />
                <span className="text-sm font-medium text-gray-700">Webhook</span>
              </div>
              <span className="text-sm font-bold text-gray-900">{channelStats.webhook.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Notifications */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Notifications</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Notification
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Channel
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Recipient
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentNotifications.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                    No notifications yet
                  </td>
                </tr>
              ) : (
                recentNotifications.map((notification) => (
                  <tr key={notification.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{notification.title}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        {getChannelIcon(notification.channel)}
                        <span className="text-sm text-gray-700 capitalize">{notification.channel}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-700">{notification.recipient}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(notification.status)}`}>
                        {notification.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(notification.timestamp).toLocaleString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;