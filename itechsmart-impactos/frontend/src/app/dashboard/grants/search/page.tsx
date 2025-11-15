'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { ArrowLeft, Search, Filter, Sliders } from 'lucide-react';

export default function GrantSearchPage() {
  const [filters, setFilters] = useState({
    keywords: '',
    category: 'all',
    minAmount: '',
    maxAmount: '',
    deadline: 'all',
    location: 'all',
    eligibility: 'all'
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard/grants" className="p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Advanced Grant Search</h1>
            <p className="mt-1 text-sm text-gray-500">Find grants that match your specific criteria</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">Keywords</label>
            <input
              type="text"
              value={filters.keywords}
              onChange={(e) => setFilters({...filters, keywords: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Search by keywords..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              value={filters.category}
              onChange={(e) => setFilters({...filters, category: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Categories</option>
              <option value="Healthcare">Healthcare</option>
              <option value="Education">Education</option>
              <option value="Environment">Environment</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Deadline</label>
            <select
              value={filters.deadline}
              onChange={(e) => setFilters({...filters, deadline: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">Any Time</option>
              <option value="30">Next 30 Days</option>
              <option value="60">Next 60 Days</option>
              <option value="90">Next 90 Days</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Min Amount</label>
            <input
              type="number"
              value={filters.minAmount}
              onChange={(e) => setFilters({...filters, minAmount: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="$0"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Max Amount</label>
            <input
              type="number"
              value={filters.maxAmount}
              onChange={(e) => setFilters({...filters, maxAmount: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="$1,000,000"
            />
          </div>
        </div>

        <div className="mt-6 flex items-center justify-end space-x-4">
          <button className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            Reset
          </button>
          <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Search Grants
          </button>
        </div>
      </div>
    </div>
  );
}