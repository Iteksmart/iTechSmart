'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { ArrowLeft, FileText, Download, Share2, Edit, TrendingUp, Users, DollarSign } from 'lucide-react';

interface ReportDetailsProps {
  params: { id: string };
}

export default function ReportDetailsPage({ params }: ReportDetailsProps) {
  const { data: report, isLoading } = useQuery({
    queryKey: ['report', params.id],
    queryFn: async () => {
      return {
        id: params.id,
        title: 'Q1 2024 Impact Report',
        type: 'quarterly',
        organization: 'Community Health Initiative',
        period: 'Q1 2024',
        created_date: '2024-04-01',
        status: 'published',
        summary: 'This quarter demonstrated significant growth across all key metrics...',
        metrics: {
          participants_served: 1250,
          programs_active: 8,
          budget_utilized: 87500,
          impact_score: 92
        }
      };
    }
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!report) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard/reports" className="p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{report.title}</h1>
            <p className="mt-1 text-sm text-gray-500">{report.organization} • {report.period}</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            href={`/dashboard/reports/${params.id}/edit`}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <Edit className="w-4 h-4 mr-2" />
            Edit
          </Link>
          <Link
            href={`/dashboard/reports/${params.id}/export`}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </Link>
          <button className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            <Share2 className="w-4 h-4 mr-2" />
            Share
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <Users className="w-8 h-8 text-blue-600" />
          </div>
          <p className="text-sm text-gray-500">Participants Served</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {report.metrics.participants_served.toLocaleString()}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <FileText className="w-8 h-8 text-green-600" />
          </div>
          <p className="text-sm text-gray-500">Active Programs</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{report.metrics.programs_active}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="w-8 h-8 text-purple-600" />
          </div>
          <p className="text-sm text-gray-500">Budget Utilized</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            ${(report.metrics.budget_utilized / 1000).toFixed(0)}K
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-8 h-8 text-orange-600" />
          </div>
          <p className="text-sm text-gray-500">Impact Score</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{report.metrics.impact_score}/100</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Executive Summary</h2>
        <p className="text-gray-700 leading-relaxed">{report.summary}</p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Key Highlights</h2>
        <ul className="space-y-3">
          <li className="flex items-start space-x-3">
            <div className="p-1 bg-green-100 rounded">
              <TrendingUp className="w-4 h-4 text-green-600" />
            </div>
            <span className="text-gray-700">25% increase in participant engagement</span>
          </li>
          <li className="flex items-start space-x-3">
            <div className="p-1 bg-blue-100 rounded">
              <Users className="w-4 h-4 text-blue-600" />
            </div>
            <span className="text-gray-700">Launched 2 new community programs</span>
          </li>
          <li className="flex items-start space-x-3">
            <div className="p-1 bg-purple-100 rounded">
              <DollarSign className="w-4 h-4 text-purple-600" />
            </div>
            <span className="text-gray-700">Secured $150K in additional funding</span>
          </li>
        </ul>
      </div>
    </div>
  );
}