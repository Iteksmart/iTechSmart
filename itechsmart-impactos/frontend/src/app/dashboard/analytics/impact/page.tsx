'use client';

import Link from 'next/link';
import { ArrowLeft, TrendingUp, Users, Award, Target } from 'lucide-react';

export default function ImpactAnalyticsPage() {
  const impactMetrics = {
    overall_score: 88,
    lives_impacted: 15000,
    satisfaction_rate: 92,
    goal_achievement: 85
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link href="/dashboard/analytics" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Impact Analytics</h1>
          <p className="mt-1 text-sm text-gray-500">Measure your social impact and outcomes</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="p-3 bg-orange-100 rounded-lg w-fit mb-4">
            <TrendingUp className="w-6 h-6 text-orange-600" />
          </div>
          <p className="text-sm text-gray-500">Overall Impact Score</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{impactMetrics.overall_score}/100</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="p-3 bg-blue-100 rounded-lg w-fit mb-4">
            <Users className="w-6 h-6 text-blue-600" />
          </div>
          <p className="text-sm text-gray-500">Lives Impacted</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{impactMetrics.lives_impacted.toLocaleString()}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="p-3 bg-green-100 rounded-lg w-fit mb-4">
            <Award className="w-6 h-6 text-green-600" />
          </div>
          <p className="text-sm text-gray-500">Satisfaction Rate</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{impactMetrics.satisfaction_rate}%</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="p-3 bg-purple-100 rounded-lg w-fit mb-4">
            <Target className="w-6 h-6 text-purple-600" />
          </div>
          <p className="text-sm text-gray-500">Goal Achievement</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{impactMetrics.goal_achievement}%</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Impact by Category</h2>
        <div className="space-y-4">
          {['Education', 'Healthcare', 'Environment', 'Social Services'].map((category, index) => {
            const score = [92, 88, 85, 90][index];
            return (
              <div key={category}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">{category}</span>
                  <span className="text-sm font-bold text-gray-900">{score}/100</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${score}%` }}></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}