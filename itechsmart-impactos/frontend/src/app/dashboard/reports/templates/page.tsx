'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, FileText, Download, Eye } from 'lucide-react';

export default function ReportTemplatesPage() {
  const templates = [
    {
      id: '1',
      name: 'Quarterly Impact Report',
      description: 'Comprehensive quarterly report with metrics, financials, and highlights',
      category: 'quarterly',
      sections: 8
    },
    {
      id: '2',
      name: 'Annual Report',
      description: 'Year-end summary with full financial statements and program outcomes',
      category: 'annual',
      sections: 12
    },
    {
      id: '3',
      name: 'Donor Impact Report',
      description: 'Donor-focused report highlighting contributions and impact',
      category: 'donor',
      sections: 6
    },
    {
      id: '4',
      name: 'Grant Report',
      description: 'Grant-specific report with deliverables and outcomes',
      category: 'grant',
      sections: 10
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard/reports" className="p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Report Templates</h1>
            <p className="mt-1 text-sm text-gray-500">Choose a template to get started</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {templates.map((template) => (
          <div key={template.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <FileText className="w-6 h-6 text-blue-600" />
              </div>
              <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                {template.sections} sections
              </span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{template.name}</h3>
            <p className="text-sm text-gray-600 mb-4">{template.description}</p>
            <div className="flex items-center space-x-2">
              <button className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                <Eye className="w-4 h-4 mr-2" />
                Preview
              </button>
              <Link
                href={`/dashboard/reports/new?template=${template.id}`}
                className="flex-1 inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Use Template
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}