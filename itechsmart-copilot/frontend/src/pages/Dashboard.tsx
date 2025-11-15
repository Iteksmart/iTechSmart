import { useState, useEffect } from 'react';
import { MessageSquare, FileText, DollarSign, TrendingUp, Lightbulb, BookOpen, Code, Star } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface DashboardStats {
  total_conversations: number;
  total_messages: number;
  total_tokens: number;
  total_cost: number;
  active_conversations: number;
  favorite_snippets: number;
  documents_count: number;
  prompts_count: number;
}

interface Conversation {
  id: number;
  title: string;
  updated_at: string;
  total_tokens: number;
  total_cost: number;
}

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    total_conversations: 24,
    total_messages: 156,
    total_tokens: 45678,
    total_cost: 2.34,
    active_conversations: 8,
    favorite_snippets: 12,
    documents_count: 15,
    prompts_count: 18
  });

  const [recentConversations, setRecentConversations] = useState<Conversation[]>([
    {
      id: 1,
      title: 'Help with React components',
      updated_at: '2024-01-15T10:30:00Z',
      total_tokens: 2500,
      total_cost: 0.15
    },
    {
      id: 2,
      title: 'Python data analysis script',
      updated_at: '2024-01-15T09:15:00Z',
      total_tokens: 3200,
      total_cost: 0.22
    },
    {
      id: 3,
      title: 'API documentation review',
      updated_at: '2024-01-14T16:45:00Z',
      total_tokens: 1800,
      total_cost: 0.12
    }
  ]);

  // Token usage over time (last 7 days)
  const tokenUsageData = [
    { date: 'Jan 9', tokens: 4200 },
    { date: 'Jan 10', tokens: 5800 },
    { date: 'Jan 11', tokens: 6500 },
    { date: 'Jan 12', tokens: 5200 },
    { date: 'Jan 13', tokens: 7100 },
    { date: 'Jan 14', tokens: 6800 },
    { date: 'Jan 15', tokens: 8900 },
  ];

  // Model usage distribution
  const modelUsageData = [
    { name: 'GPT-4', value: 45 },
    { name: 'GPT-3.5', value: 30 },
    { name: 'Claude', value: 15 },
    { name: 'Gemini', value: 10 },
  ];

  // Cost breakdown by category
  const costData = [
    { category: 'Chat', cost: 1.2 },
    { category: 'Code Gen', cost: 0.8 },
    { category: 'Analysis', cost: 0.34 },
  ];

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-sm text-gray-700">
            Overview of your AI assistant usage and activities
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <MessageSquare className="h-6 w-6 text-indigo-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Conversations</dt>
                  <dd className="text-2xl font-semibold text-gray-900">{stats.total_conversations}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FileText className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Messages</dt>
                  <dd className="text-2xl font-semibold text-gray-900">{stats.total_messages}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Tokens</dt>
                  <dd className="text-2xl font-semibold text-gray-900">{stats.total_tokens.toLocaleString()}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DollarSign className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Cost</dt>
                  <dd className="text-2xl font-semibold text-gray-900">${stats.total_cost.toFixed(2)}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Secondary Stats */}
      <div className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <MessageSquare className="h-5 w-5 text-blue-600" />
              </div>
              <div className="ml-3 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Active Chats</dt>
                  <dd className="text-lg font-semibold text-gray-900">{stats.active_conversations}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Code className="h-5 w-5 text-green-600" />
              </div>
              <div className="ml-3 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Code Snippets</dt>
                  <dd className="text-lg font-semibold text-gray-900">{stats.favorite_snippets}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BookOpen className="h-5 w-5 text-purple-600" />
              </div>
              <div className="ml-3 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Documents</dt>
                  <dd className="text-lg font-semibold text-gray-900">{stats.documents_count}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Lightbulb className="h-5 w-5 text-yellow-600" />
              </div>
              <div className="ml-3 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Prompts</dt>
                  <dd className="text-lg font-semibold text-gray-900">{stats.prompts_count}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="mt-8 grid grid-cols-1 gap-5 lg:grid-cols-2">
        {/* Token Usage Chart */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Token Usage (Last 7 Days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={tokenUsageData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="tokens" stroke="#6366f1" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Model Usage Distribution */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Model Usage Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={modelUsageData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {modelUsageData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Cost Breakdown */}
      <div className="mt-8 bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Cost Breakdown by Category</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={costData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="cost" fill="#6366f1" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Conversations */}
      <div className="mt-8 bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Conversations</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Updated
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tokens
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cost
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentConversations.map((conv) => (
                <tr key={conv.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <MessageSquare className="w-5 h-5 text-indigo-600 mr-2" />
                      <span className="text-sm font-medium text-gray-900">{conv.title}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(conv.updated_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {conv.total_tokens.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${conv.total_cost.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <button className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow">
          <MessageSquare className="h-8 w-8 text-indigo-600 mb-3" />
          <h3 className="text-lg font-medium text-gray-900">New Chat</h3>
          <p className="mt-1 text-sm text-gray-500">Start a new conversation</p>
        </button>

        <button className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow">
          <Lightbulb className="h-8 w-8 text-yellow-600 mb-3" />
          <h3 className="text-lg font-medium text-gray-900">Browse Prompts</h3>
          <p className="mt-1 text-sm text-gray-500">Explore prompt templates</p>
        </button>

        <button className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow">
          <BookOpen className="h-8 w-8 text-purple-600 mb-3" />
          <h3 className="text-lg font-medium text-gray-900">Knowledge Base</h3>
          <p className="mt-1 text-sm text-gray-500">Manage your documents</p>
        </button>

        <button className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow">
          <Code className="h-8 w-8 text-green-600 mb-3" />
          <h3 className="text-lg font-medium text-gray-900">Code Snippets</h3>
          <p className="mt-1 text-sm text-gray-500">View saved code</p>
        </button>
      </div>
    </div>
  );
}