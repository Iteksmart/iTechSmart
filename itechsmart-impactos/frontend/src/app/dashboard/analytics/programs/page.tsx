'use client';

import Link from 'next/link';
import { ArrowLeft, Target, Users, TrendingUp, DollarSign } from 'lucide-react';

export default function ProgramAnalyticsPage() {
  const programs = [
    { name: 'Youth Mentorship', participants: 78, budget: 150000, impact: 85, status: 'On Track' },
    { name: 'Health Screenings', participants: 342, budget: 250000, impact: 92, status: 'Exceeding' },
    { name: 'After-School Tutoring', participants: 145, budget: 80000, impact: 88, status: 'On Track' }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link href="/dashboard/analytics" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Program Analytics</h1>
          <p className="mt-1 text-sm text-gray-500">Track performance across all programs</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Program</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Participants</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Budget</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Impact</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {programs.map((program, index) => (
              <tr key={index}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <Target className="w-5 h-5 text-blue-600 mr-3" />
                    <span className="text-sm font-medium text-gray-900">{program.name}</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{program.participants}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${(program.budget / 1000).toFixed(0)}K
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div className="bg-green-600 h-2 rounded-full" style={{ width: `${program.impact}%` }}></div>
                    </div>
                    <span className="text-sm text-gray-900">{program.impact}%</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    program.status === 'Exceeding' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                  }`}>
                    {program.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}