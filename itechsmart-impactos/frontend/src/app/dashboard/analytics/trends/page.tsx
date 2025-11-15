'use client';

import Link from 'next/link';
import { ArrowLeft, TrendingUp, Calendar } from 'lucide-react';

export default function TrendsAnalysisPage() {
  const trends = [
    { month: 'Jan', participants: 2800, programs: 20, budget: 240000 },
    { month: 'Feb', participants: 2950, programs: 22, budget: 255000 },
    { month: 'Mar', participants: 3100, programs: 23, budget: 268000 },
    { month: 'Apr', participants: 3250, programs: 24, budget: 282000 },
    { month: 'May', participants: 3400, programs: 25, budget: 295000 },
    { month: 'Jun', participants: 3550, programs: 26, budget: 310000 }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link href="/dashboard/analytics" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Trends Analysis</h1>
          <p className="mt-1 text-sm text-gray-500">Analyze trends and patterns over time</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">6-Month Trends</h2>
        <div className="space-y-6">
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-4">Participant Growth</h3>
            <div className="space-y-3">
              {trends.map((trend, index) => (
                <div key={index} className="flex items-center">
                  <div className="w-16 text-sm text-gray-600">{trend.month}</div>
                  <div className="flex-1 mx-4">
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-blue-600 h-3 rounded-full transition-all"
                        style={{ width: `${(trend.participants / 4000) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="w-24 text-sm font-medium text-gray-900 text-right">
                    {trend.participants.toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-6 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-700 mb-4">Program Expansion</h3>
            <div className="space-y-3">
              {trends.map((trend, index) => (
                <div key={index} className="flex items-center">
                  <div className="w-16 text-sm text-gray-600">{trend.month}</div>
                  <div className="flex-1 mx-4">
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-green-600 h-3 rounded-full transition-all"
                        style={{ width: `${(trend.programs / 30) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="w-24 text-sm font-medium text-gray-900 text-right">
                    {trend.programs} programs
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-6 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-700 mb-4">Budget Utilization</h3>
            <div className="space-y-3">
              {trends.map((trend, index) => (
                <div key={index} className="flex items-center">
                  <div className="w-16 text-sm text-gray-600">{trend.month}</div>
                  <div className="flex-1 mx-4">
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-purple-600 h-3 rounded-full transition-all"
                        style={{ width: `${(trend.budget / 350000) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="w-24 text-sm font-medium text-gray-900 text-right">
                    ${(trend.budget / 1000).toFixed(0)}K
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <TrendingUp className="w-6 h-6 text-blue-600 mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Key Insights</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>• Participant growth averaging 5.3% month-over-month</li>
              <li>• Program expansion steady at 1-2 new programs per month</li>
              <li>• Budget utilization increasing proportionally with growth</li>
              <li>• Overall trajectory indicates sustainable scaling</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}