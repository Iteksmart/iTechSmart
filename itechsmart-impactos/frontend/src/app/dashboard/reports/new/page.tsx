'use client';

import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, FileText, Sparkles } from 'lucide-react';

export default function NewReportPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    type: 'quarterly',
    organization_id: '',
    program_id: '',
    period_start: '',
    period_end: '',
    include_financials: true,
    include_metrics: true,
    include_stories: true
  });

  const { data: organizations } = useQuery({
    queryKey: ['organizations'],
    queryFn: async () => {
      return [
        { id: '1', name: 'Community Health Initiative' },
        { id: '2', name: 'Youth Education Foundation' }
      ];
    }
  });

  const { data: programs } = useQuery({
    queryKey: ['programs', formData.organization_id],
    queryFn: async () => {
      return [
        { id: '1', name: 'Youth Mentorship Program' },
        { id: '2', name: 'Community Health Screenings' }
      ];
    },
    enabled: !!formData.organization_id
  });

  const generateReport = useMutation({
    mutationFn: async (data: typeof formData) => {
      console.log('Generating report:', data);
      await new Promise(resolve => setTimeout(resolve, 2000));
      return { id: '123', ...data };
    },
    onSuccess: (data) => {
      router.push(`/dashboard/reports/${data.id}`);
    }
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    generateReport.mutate(formData);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard/reports" className="p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Generate Impact Report</h1>
            <p className="mt-1 text-sm text-gray-500">Create a comprehensive impact report with AI assistance</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 bg-blue-100 rounded-lg">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Report Configuration</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Report Type *</label>
              <select
                name="type"
                value={formData.type}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="quarterly">Quarterly Report</option>
                <option value="annual">Annual Report</option>
                <option value="donor">Donor Report</option>
                <option value="grant">Grant Report</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Organization *</label>
              <select
                name="organization_id"
                value={formData.organization_id}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Select organization</option>
                {organizations?.map((org) => (
                  <option key={org.id} value={org.id}>{org.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Program (Optional)</label>
              <select
                name="program_id"
                value={formData.program_id}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                disabled={!formData.organization_id}
              >
                <option value="">All programs</option>
                {programs?.map((program) => (
                  <option key={program.id} value={program.id}>{program.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Period Start *</label>
              <input
                type="date"
                name="period_start"
                value={formData.period_start}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Period End *</label>
              <input
                type="date"
                name="period_end"
                value={formData.period_end}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Report Sections</h2>
          <div className="space-y-4">
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                name="include_financials"
                checked={formData.include_financials}
                onChange={handleChange}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <div>
                <p className="text-sm font-medium text-gray-900">Financial Summary</p>
                <p className="text-xs text-gray-500">Include budget, expenses, and funding sources</p>
              </div>
            </label>

            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                name="include_metrics"
                checked={formData.include_metrics}
                onChange={handleChange}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <div>
                <p className="text-sm font-medium text-gray-900">Impact Metrics</p>
                <p className="text-xs text-gray-500">Include key performance indicators and outcomes</p>
              </div>
            </label>

            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                name="include_stories"
                checked={formData.include_stories}
                onChange={handleChange}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <div>
                <p className="text-sm font-medium text-gray-900">Success Stories</p>
                <p className="text-xs text-gray-500">Include participant testimonials and case studies</p>
              </div>
            </label>
          </div>
        </div>

        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-200">
          <div className="flex items-start space-x-3">
            <Sparkles className="w-6 h-6 text-blue-600 mt-1" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Report Generation</h3>
              <p className="text-sm text-gray-700 mb-4">
                Our AI will automatically analyze your data and generate a comprehensive impact report with:
              </p>
              <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
                <li>Executive summary with key highlights</li>
                <li>Data visualizations and charts</li>
                <li>Trend analysis and insights</li>
                <li>Recommendations for improvement</li>
                <li>Professional formatting and design</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end space-x-4">
          <Link
            href="/dashboard/reports"
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={generateReport.isPending}
            className="inline-flex items-center px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {generateReport.isPending ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Generating Report...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Report
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}