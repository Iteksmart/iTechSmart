import { useState, useEffect } from 'react';
import { 
  Workflow, 
  PlayCircle, 
  CheckCircle, 
  XCircle, 
  Clock,
  TrendingUp,
  Activity
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  BarChart,
  Bar,
  PieChart, 
  Pie, 
  Cell,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import axios from 'axios';

interface Analytics {
  total_workflows: number;
  active_workflows: number;
  draft_workflows: number;
  paused_workflows: number;
  archived_workflows: number;
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  avg_execution_time: number;
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
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-xl">Loading dashboard...</div>
      </div>
    );
  }

  const stats = [
    {
      label: 'Total Workflows',
      value: analytics?.total_workflows || 0,
      icon: Workflow,
      color: 'bg-blue-500',
      change: '+12%'
    },
    {
      label: 'Active Workflows',
      value: analytics?.active_workflows || 0,
      icon: Activity,
      color: 'bg-green-500',
      change: '+8%'
    },
    {
      label: 'Total Executions',
      value: analytics?.total_executions || 0,
      icon: PlayCircle,
      color: 'bg-purple-500',
      change: '+23%'
    },
    {
      label: 'Success Rate',
      value: analytics?.total_executions 
        ? `${Math.round((analytics.successful_executions / analytics.total_executions) * 100)}%`
        : '0%',
      icon: CheckCircle,
      color: 'bg-emerald-500',
      change: '+5%'
    }
  ];

  // Sample data for charts
  const executionTrendData = [
    { date: 'Mon', executions: 45, successful: 42, failed: 3 },
    { date: 'Tue', executions: 52, successful: 48, failed: 4 },
    { date: 'Wed', executions: 48, successful: 45, failed: 3 },
    { date: 'Thu', executions: 61, successful: 58, failed: 3 },
    { date: 'Fri', executions: 55, successful: 51, failed: 4 },
    { date: 'Sat', executions: 38, successful: 36, failed: 2 },
    { date: 'Sun', executions: 42, successful: 40, failed: 2 }
  ];

  const workflowStatusData = [
    { name: 'Active', value: analytics?.active_workflows || 0, color: '#10b981' },
    { name: 'Draft', value: analytics?.draft_workflows || 0, color: '#f59e0b' },
    { name: 'Paused', value: analytics?.paused_workflows || 0, color: '#6b7280' },
    { name: 'Archived', value: analytics?.archived_workflows || 0, color: '#ef4444' }
  ];

  const topWorkflows = [
    { name: 'Customer Onboarding', executions: 234, success_rate: 98 },
    { name: 'Invoice Processing', executions: 189, success_rate: 95 },
    { name: 'Data Sync', executions: 156, success_rate: 99 },
    { name: 'Email Campaign', executions: 142, success_rate: 97 },
    { name: 'Report Generation', executions: 128, success_rate: 94 }
  ];

  const recentActivity = [
    { workflow: 'Customer Onboarding', status: 'completed', time: '2 minutes ago' },
    { workflow: 'Invoice Processing', status: 'completed', time: '5 minutes ago' },
    { workflow: 'Data Sync', status: 'running', time: '8 minutes ago' },
    { workflow: 'Email Campaign', status: 'completed', time: '12 minutes ago' },
    { workflow: 'Report Generation', status: 'failed', time: '15 minutes ago' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>
        <p className="text-gray-600 mt-1">Overview of your workflow automation</p>
      </div>

      {/* Stats Grid */}
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

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Execution Trend */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Execution Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={executionTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="successful" 
                stroke="#10b981" 
                strokeWidth={2}
                name="Successful"
              />
              <Line 
                type="monotone" 
                dataKey="failed" 
                stroke="#ef4444" 
                strokeWidth={2}
                name="Failed"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Workflow Status Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Workflow Status</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={workflowStatusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {workflowStatusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Workflows */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Top Workflows</h3>
          <div className="space-y-4">
            {topWorkflows.map((workflow, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="font-medium text-gray-800">{workflow.name}</p>
                  <p className="text-sm text-gray-600">{workflow.executions} executions</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-green-600">{workflow.success_rate}%</p>
                  <p className="text-xs text-gray-500">success rate</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {recentActivity.map((activity, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  {activity.status === 'completed' && (
                    <CheckCircle size={20} className="text-green-500" />
                  )}
                  {activity.status === 'running' && (
                    <Clock size={20} className="text-blue-500" />
                  )}
                  {activity.status === 'failed' && (
                    <XCircle size={20} className="text-red-500" />
                  )}
                  <div>
                    <p className="font-medium text-gray-800">{activity.workflow}</p>
                    <p className="text-sm text-gray-600">{activity.time}</p>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  activity.status === 'completed' ? 'bg-green-100 text-green-800' :
                  activity.status === 'running' ? 'bg-blue-100 text-blue-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {activity.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;