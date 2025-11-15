'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import {
  TrendingUp,
  Eye,
  FileText,
  Users,
  Calendar,
  Activity,
  BarChart3,
  PieChart,
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart as RechartsPie,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface AnalyticsData {
  total_proofs: number;
  total_verifications: number;
  active_proofs: number;
  verification_trend: Array<{ date: string; count: number }>;
  proof_types: Array<{ type: string; count: number }>;
  top_proofs: Array<{ filename: string; verifications: number }>;
}

const COLORS = ['#3B82F6', '#8B5CF6', '#EC4899', '#F59E0B', '#10B981', '#6366F1'];

export default function AnalyticsPage() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: async () => {
      const response = await api.get('/analytics/overview');
      return response.data as AnalyticsData;
    },
  });

  // Mock data for demonstration
  const verificationTrend = [
    { date: 'Jan', count: 45 },
    { date: 'Feb', count: 52 },
    { date: 'Mar', count: 61 },
    { date: 'Apr', count: 58 },
    { date: 'May', count: 70 },
    { date: 'Jun', count: 85 },
    { date: 'Jul', count: 92 },
  ];

  const proofTypes = [
    { type: 'Documents', count: 145 },
    { type: 'Images', count: 89 },
    { type: 'Videos', count: 34 },
    { type: 'Audio', count: 23 },
    { type: 'Other', count: 12 },
  ];

  const topProofs = [
    { filename: 'contract_2024.pdf', verifications: 234 },
    { filename: 'certificate.png', verifications: 189 },
    { filename: 'report_final.docx', verifications: 156 },
    { filename: 'presentation.pptx', verifications: 142 },
    { filename: 'invoice_001.pdf', verifications: 128 },
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading analytics...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
          <p className="text-gray-600">Track your proof performance and verification trends</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm font-medium">Total Proofs</span>
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">303</p>
            <p className="text-sm text-green-600 mt-2">+12% from last month</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm font-medium">Total Verifications</span>
              <Eye className="w-5 h-5 text-purple-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">1,234</p>
            <p className="text-sm text-green-600 mt-2">+18% from last month</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm font-medium">Active Proofs</span>
              <Activity className="w-5 h-5 text-green-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">287</p>
            <p className="text-sm text-gray-600 mt-2">94.7% active rate</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm font-medium">Avg. Verifications</span>
              <TrendingUp className="w-5 h-5 text-orange-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">4.1</p>
            <p className="text-sm text-green-600 mt-2">+0.3 from last month</p>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Verification Trend */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Verification Trend</h2>
              <BarChart3 className="w-5 h-5 text-blue-600" />
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={verificationTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="date" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #E5E7EB',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#3B82F6"
                  strokeWidth={3}
                  dot={{ fill: '#3B82F6', r: 5 }}
                  name="Verifications"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Proof Types Distribution */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Proof Types</h2>
              <PieChart className="w-5 h-5 text-purple-600" />
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <RechartsPie>
                <Pie
                  data={proofTypes}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ type, percent }) => `${type} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {proofTypes.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </RechartsPie>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Proofs */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Top Verified Proofs</h2>
          <div className="space-y-4">
            {topProofs.map((proof, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-4">
                  <div className="flex items-center justify-center w-10 h-10 bg-blue-100 text-blue-600 rounded-lg font-bold">
                    #{index + 1}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{proof.filename}</p>
                    <p className="text-sm text-gray-600">{proof.verifications} verifications</p>
                  </div>
                </div>
                <div className="w-48">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${(proof.verifications / topProofs[0].verifications) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Monthly Activity */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Monthly Activity</h2>
            <Calendar className="w-5 h-5 text-green-600" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={verificationTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="date" stroke="#6B7280" />
              <YAxis stroke="#6B7280" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <Bar dataKey="count" fill="#10B981" name="Verifications" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Insights */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900">Growth Insight</h3>
            </div>
            <p className="text-gray-700">
              Your verification rate has increased by 18% this month. Keep up the great work!
            </p>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-100">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-purple-600 rounded-lg">
                <FileText className="w-5 h-5 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900">Most Popular</h3>
            </div>
            <p className="text-gray-700">
              Documents are your most verified proof type, accounting for 48% of all verifications.
            </p>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-100">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-green-600 rounded-lg">
                <Users className="w-5 h-5 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900">Engagement</h3>
            </div>
            <p className="text-gray-700">
              Your proofs are being verified by an average of 4.1 unique users each.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}