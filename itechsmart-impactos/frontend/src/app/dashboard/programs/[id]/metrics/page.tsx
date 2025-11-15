'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { ArrowLeft, TrendingUp, Users, DollarSign, Award, Calendar } from 'lucide-react';

interface ProgramMetricsProps {
  params: {
    id: string;
  };
}

export default function ProgramMetricsPage({ params }: ProgramMetricsProps) {
  const { data: program } = useQuery({
    queryKey: ['program', params.id],
    queryFn: async () => {
      return {
        id: params.id,
        name: 'Youth Mentorship Program',
        metrics: {
          participants: {
            total: 78,
            target: 100,
            new_this_month: 12,
            completed: 45,
            active: 33,
            dropout_rate: 5.2
          },
          budget: {
            total: 150000,
            spent: 87500,
            remaining: 62500,
            monthly_burn: 12500
          },
          impact: {
            score: 85,
            satisfaction_rate: 92,
            goal_achievement: 78,
            retention_rate: 94.8
          },
          timeline: [
            { month: 'Jan', participants: 45, budget_spent: 25000 },
            { month: 'Feb', participants: 58, budget_spent: 37500 },
            { month: 'Mar', participants: 67, budget_spent: 62500 },
            { month: 'Apr', participants: 78, budget_spent: 87500 }
          ]
        }
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

  if (!program) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-500">Loading metrics...</p>
        </div>
      </div>
    );
  }

  const { metrics } = program;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            href={`/dashboard/programs/${params.id}`}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Program Metrics</h1>
            <p className="mt-1 text-sm text-gray-500">{program.name}</p>
          </div>
        </div>
      </div>

      {/* Key Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
            <span className="text-sm font-medium text-green-600">+{metrics.participants.new_this_month} this month</span>
          </div>
          <p className="text-sm text-gray-500">Total Participants</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">
            {metrics.participants.total}
          </p>
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${(metrics.participants.total / metrics.participants.target) * 100}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {Math.round((metrics.participants.total / metrics.participants.target) * 100)}% of target
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <DollarSign className="w-6 h-6 text-green-600" />
            </div>
            <span className="text-sm font-medium text-gray-600">{formatCurrency(metrics.budget.monthly_burn)}/mo</span>
          </div>
          <p className="text-sm text-gray-500">Budget Spent</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">
            {formatCurrency(metrics.budget.spent)}
          </p>
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full"
                style={{ width: `${(metrics.budget.spent / metrics.budget.total) * 100}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {formatCurrency(metrics.budget.remaining)} remaining
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Award className="w-6 h-6 text-purple-600" />
            </div>
            <span className="text-sm font-medium text-purple-600">{metrics.participants.completed} total</span>
          </div>
          <p className="text-sm text-gray-500">Completion Rate</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">
            {Math.round((metrics.participants.completed / metrics.participants.total) * 100)}%
          </p>
          <p className="text-xs text-gray-500 mt-4">
            {metrics.participants.active} currently active
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-orange-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
            <span className="text-sm font-medium text-orange-600">Excellent</span>
          </div>
          <p className="text-sm text-gray-500">Impact Score</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">
            {metrics.impact.score}/100
          </p>
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-orange-600 h-2 rounded-full"
                style={{ width: `${metrics.impact.score}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Participant Metrics */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Participant Metrics</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm text-gray-500">Total Enrolled</p>
                <p className="text-2xl font-bold text-gray-900">{metrics.participants.total}</p>
              </div>
              <Users className="w-8 h-8 text-blue-600" />
            </div>
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm text-gray-500">Currently Active</p>
                <p className="text-2xl font-bold text-gray-900">{metrics.participants.active}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm text-gray-500">Completed Program</p>
                <p className="text-2xl font-bold text-gray-900">{metrics.participants.completed}</p>
              </div>
              <Award className="w-8 h-8 text-purple-600" />
            </div>
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm text-gray-500">Dropout Rate</p>
                <p className="text-2xl font-bold text-gray-900">{metrics.participants.dropout_rate}%</p>
              </div>
              <div className="text-sm text-gray-500">Low is better</div>
            </div>
          </div>
        </div>

        {/* Impact Metrics */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Impact Metrics</h2>
          <div className="space-y-6">
            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium text-gray-700">Overall Impact Score</p>
                <p className="text-sm font-bold text-gray-900">{metrics.impact.score}/100</p>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-orange-600 h-3 rounded-full"
                  style={{ width: `${metrics.impact.score}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium text-gray-700">Satisfaction Rate</p>
                <p className="text-sm font-bold text-gray-900">{metrics.impact.satisfaction_rate}%</p>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-green-600 h-3 rounded-full"
                  style={{ width: `${metrics.impact.satisfaction_rate}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium text-gray-700">Goal Achievement</p>
                <p className="text-sm font-bold text-gray-900">{metrics.impact.goal_achievement}%</p>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-blue-600 h-3 rounded-full"
                  style={{ width: `${metrics.impact.goal_achievement}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium text-gray-700">Retention Rate</p>
                <p className="text-sm font-bold text-gray-900">{metrics.impact.retention_rate}%</p>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-purple-600 h-3 rounded-full"
                  style={{ width: `${metrics.impact.retention_rate}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Timeline Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Growth Timeline</h2>
        <div className="space-y-4">
          {metrics.timeline.map((month, index) => (
            <div key={index} className="border-b border-gray-200 pb-4 last:border-0">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <Calendar className="w-5 h-5 text-gray-400" />
                  <span className="font-medium text-gray-900">{month.month}</span>
                </div>
                <div className="flex items-center space-x-6">
                  <div className="text-right">
                    <p className="text-xs text-gray-500">Participants</p>
                    <p className="text-sm font-bold text-gray-900">{month.participants}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">Budget Spent</p>
                    <p className="text-sm font-bold text-gray-900">{formatCurrency(month.budget_spent)}</p>
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${(month.participants / metrics.participants.target) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${(month.budget_spent / metrics.budget.total) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Export Options */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Export Metrics</h2>
        <div className="flex items-center space-x-4">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Export as PDF
          </button>
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            Export as CSV
          </button>
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            Share Report
          </button>
        </div>
      </div>
    </div>
  );
}