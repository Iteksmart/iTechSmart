'use client';

import Link from 'next/link';
import { ArrowLeft, DollarSign, TrendingUp, PieChart } from 'lucide-react';

export default function FinancialAnalyticsPage() {
  const financial = {
    total_revenue: 2850000,
    total_expenses: 2450000,
    net_income: 400000,
    budget_utilization: 86
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link href="/dashboard/analytics" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Financial Analytics</h1>
          <p className="mt-1 text-sm text-gray-500">Monitor your financial health and performance</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="p-3 bg-green-100 rounded-lg w-fit mb-4">
            <DollarSign className="w-6 h-6 text-green-600" />
          </div>
          <p className="text-sm text-gray-500">Total Revenue</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            ${(financial.total_revenue / 1000000).toFixed(2)}M
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="p-3 bg-red-100 rounded-lg w-fit mb-4">
            <DollarSign className="w-6 h-6 text-red-600" />
          </div>
          <p className="text-sm text-gray-500">Total Expenses</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            ${(financial.total_expenses / 1000000).toFixed(2)}M
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="p-3 bg-blue-100 rounded-lg w-fit mb-4">
            <TrendingUp className="w-6 h-6 text-blue-600" />
          </div>
          <p className="text-sm text-gray-500">Net Income</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            ${(financial.net_income / 1000).toFixed(0)}K
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="p-3 bg-purple-100 rounded-lg w-fit mb-4">
            <PieChart className="w-6 h-6 text-purple-600" />
          </div>
          <p className="text-sm text-gray-500">Budget Utilization</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{financial.budget_utilization}%</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Expense Breakdown</h2>
        <div className="space-y-4">
          {[
            { category: 'Personnel', amount: 1200000, percentage: 49 },
            { category: 'Programs', amount: 800000, percentage: 33 },
            { category: 'Operations', amount: 350000, percentage: 14 },
            { category: 'Other', amount: 100000, percentage: 4 }
          ].map((item) => (
            <div key={item.category}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">{item.category}</span>
                <span className="text-sm font-bold text-gray-900">
                  ${(item.amount / 1000).toFixed(0)}K ({item.percentage}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-purple-600 h-2 rounded-full" style={{ width: `${item.percentage}%` }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}