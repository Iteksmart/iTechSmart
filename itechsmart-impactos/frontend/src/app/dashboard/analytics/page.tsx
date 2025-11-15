'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { TrendingUp, Users, DollarSign, Target, ArrowUp, ArrowDown, BarChart3 } from 'lucide-react';

export default function AnalyticsPage() {
  const { data: analytics } = useQuery({
    queryKey: ['analytics'],
    queryFn: async () => {
      return {
        overview: {
          total_participants: 3250,
          participants_change: 12.5,
          active_programs: 24,
          programs_change: 8.3,
          total_budget: 2850000,
          budget_change: -5.2,
          impact_score: 88,
          impact_change: 3.7
        },
        monthly_trends: [
          { month: 'Jan', participants: 2800, budget: 240000 },
          { month: 'Feb', participants: 2950, budget: 255000 },
          { month: 'Mar', participants: 3100, budget: 268000 },
          { month: 'Apr', participants: 3250, budget: 282000 }
        ]
      };
    }
  });

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatChange = (change: number) => {
    const isPositive = change >= 0;
    return (
      <div className={`flex items-center text-sm ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
        {isPositive ? <ArrowUp className="w-4 h-4 mr-1" /> : <ArrowDown className="w-4 h-4 mr-1" />}
        {Math.abs(change)}%
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Overview</h1>
          <p className="mt-1 text-sm text-gray-500">Track your organization's performance and impact</p>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            href="/dashboard/analytics/impact"
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Impact Analytics
          </Link>
          <Link
            href="/dashboard/analytics/programs"
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Program Analytics
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
            {formatChange(analytics?.overview.participants_change || 0)}
          </div>
          <p className="text-sm text-gray-500">Total Participants</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {analytics?.overview.total_participants.toLocaleString()}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <Target className="w-6 h-6 text-green-600" />
            </div>
            {formatChange(analytics?.overview.programs_change || 0)}
          </div>
          <p className="text-sm text-gray-500">Active Programs</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{analytics?.overview.active_programs}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <DollarSign className="w-6 h-6 text-purple-600" />
            </div>
            {formatChange(analytics?.overview.budget_change || 0)}
          </div>
          <p className="text-sm text-gray-500">Total Budget</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {formatCurrency(analytics?.overview.total_budget || 0)}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-orange-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
            {formatChange(analytics?.overview.impact_change || 0)}
          </div>
          <p className="text-sm text-gray-500">Impact Score</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{analytics?.overview.impact_score}/100</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Participant Growth</h2>
          <div className="space-y-4">
            {analytics?.monthly_trends.map((trend, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">{trend.month}</span>
                <div className="flex-1 mx-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${(trend.participants / 3500) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <span className="text-sm font-bold text-gray-900">{trend.participants.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Budget Utilization</h2>
          <div className="space-y-4">
            {analytics?.monthly_trends.map((trend, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">{trend.month}</span>
                <div className="flex-1 mx-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${(trend.budget / 300000) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <span className="text-sm font-bold text-gray-900">{formatCurrency(trend.budget)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Link
          href="/dashboard/analytics/impact"
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <TrendingUp className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Impact Analytics</h3>
              <p className="text-sm text-gray-500">Measure your social impact</p>
            </div>
          </div>
        </Link>

        <Link
          href="/dashboard/analytics/programs"
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <Target className="w-8 h-8 text-green-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Program Analytics</h3>
              <p className="text-sm text-gray-500">Track program performance</p>
            </div>
          </div>
        </Link>

        <Link
          href="/dashboard/analytics/financial"
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <DollarSign className="w-8 h-8 text-purple-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Financial Analytics</h3>
              <p className="text-sm text-gray-500">Monitor financial health</p>
            </div>
          </div>
        </Link>
      </div>
    </div>
  );
}