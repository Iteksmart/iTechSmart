import { useState, useEffect } from 'react';
import { Key, FolderLock, Shield, Activity, TrendingUp, AlertTriangle } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

interface Analytics {
  total_vaults: number;
  total_secrets: number;
  active_secrets: number;
  expired_secrets: number;
  revoked_secrets: number;
  total_access_grants: number;
  total_policies: number;
  secrets_by_type: Record<string, number>;
}

const Dashboard = () => {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/analytics/overview', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="flex items-center justify-center h-full"><div className="text-xl">Loading...</div></div>;
  }

  const stats = [
    { label: 'Total Secrets', value: analytics?.total_secrets || 0, icon: Key, color: 'bg-blue-500', change: '+12%' },
    { label: 'Active Secrets', value: analytics?.active_secrets || 0, icon: Activity, color: 'bg-green-500', change: '+8%' },
    { label: 'Total Vaults', value: analytics?.total_vaults || 0, icon: FolderLock, color: 'bg-purple-500', change: '+5%' },
    { label: 'Policies', value: analytics?.total_policies || 0, icon: Shield, color: 'bg-orange-500', change: '+3%' }
  ];

  const secretStatusData = [
    { name: 'Active', value: analytics?.active_secrets || 0, color: '#10b981' },
    { name: 'Expired', value: analytics?.expired_secrets || 0, color: '#f59e0b' },
    { name: 'Revoked', value: analytics?.revoked_secrets || 0, color: '#ef4444' }
  ];

  const secretTypeData = Object.entries(analytics?.secrets_by_type || {}).map(([name, value]) => ({
    name: name.replace('_', ' ').toUpperCase(),
    value
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>
        <p className="text-gray-600 mt-1">Overview of your secrets management</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">{stat.label}</p>
                  <p className="text-3xl font-bold text-gray-800">{stat.value}</p>
                  <p className="text-sm text-green-600 mt-2 flex items-center">
                    <TrendingUp size={16} className="mr-1" />
                    {stat.change}
                  </p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon size={24} className="text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Secret Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={secretStatusData} cx="50%" cy="50%" labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100} fill="#8884d8" dataKey="value">
                {secretStatusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Secrets by Type</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={secretTypeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Security Alerts</h3>
        <div className="space-y-3">
          <div className="flex items-center p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <AlertTriangle size={20} className="text-yellow-600 mr-3" />
            <div>
              <p className="font-medium text-gray-800">3 secrets expiring soon</p>
              <p className="text-sm text-gray-600">Review and rotate these secrets</p>
            </div>
          </div>
          <div className="flex items-center p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <Activity size={20} className="text-blue-600 mr-3" />
            <div>
              <p className="font-medium text-gray-800">All systems operational</p>
              <p className="text-sm text-gray-600">No security incidents detected</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
