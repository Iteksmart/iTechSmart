'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { ArrowLeft, FileText, Edit, Download, Send, DollarSign, Calendar, Building2 } from 'lucide-react';

interface ProposalDetailsProps {
  params: { id: string };
}

export default function ProposalDetailsPage({ params }: ProposalDetailsProps) {
  const { data: proposal, isLoading } = useQuery({
    queryKey: ['proposal', params.id],
    queryFn: async () => {
      return {
        id: params.id,
        title: 'Community Health Mobile Clinic Initiative',
        grant_title: 'Community Health Innovation Grant',
        organization: 'Community Health Initiative',
        amount_requested: 150000,
        status: 'submitted',
        deadline: '2024-06-30',
        submitted_date: '2024-04-15',
        executive_summary: 'This proposal outlines a comprehensive mobile health clinic initiative...',
        project_description: 'Our mobile clinic will provide essential healthcare services...',
        goals_objectives: '1. Serve 5,000 patients in the first year\n2. Reduce emergency room visits by 30%',
        methodology: 'We will deploy two fully-equipped mobile clinics...',
        budget_narrative: 'Personnel: $80,000\nEquipment: $40,000\nOperations: $30,000',
        evaluation_plan: 'We will track patient outcomes, satisfaction scores, and cost savings...'
      };
    }
  });

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'submitted': return 'bg-blue-100 text-blue-800';
      case 'under-review': return 'bg-yellow-100 text-yellow-800';
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!proposal) {
    return (
      <div className="text-center py-12">
        <FileText className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Proposal not found</h3>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard/proposals" className="p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-3xl font-bold text-gray-900">{proposal.title}</h1>
              <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(proposal.status)}`}>
                {proposal.status}
              </span>
            </div>
            <p className="mt-1 text-sm text-gray-500">{proposal.grant_title}</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          {proposal.status === 'draft' && (
            <Link
              href={`/dashboard/proposals/${params.id}/edit`}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </Link>
          )}
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            <Download className="w-4 h-4 mr-2" />
            Export PDF
          </button>
          {proposal.status === 'draft' && (
            <button className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              <Send className="w-4 h-4 mr-2" />
              Submit
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="w-8 h-8 text-green-600" />
          </div>
          <p className="text-sm text-gray-500">Amount Requested</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {formatCurrency(proposal.amount_requested)}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <Calendar className="w-8 h-8 text-blue-600" />
          </div>
          <p className="text-sm text-gray-500">Deadline</p>
          <p className="text-lg font-bold text-gray-900 mt-1">
            {formatDate(proposal.deadline)}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <Building2 className="w-8 h-8 text-purple-600" />
          </div>
          <p className="text-sm text-gray-500">Organization</p>
          <p className="text-lg font-bold text-gray-900 mt-1">{proposal.organization}</p>
        </div>
      </div>

      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Executive Summary</h2>
          <p className="text-gray-700 whitespace-pre-wrap">{proposal.executive_summary}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Project Description</h2>
          <p className="text-gray-700 whitespace-pre-wrap">{proposal.project_description}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Goals & Objectives</h2>
          <p className="text-gray-700 whitespace-pre-wrap">{proposal.goals_objectives}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Methodology</h2>
          <p className="text-gray-700 whitespace-pre-wrap">{proposal.methodology}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Budget Narrative</h2>
          <p className="text-gray-700 whitespace-pre-wrap">{proposal.budget_narrative}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Evaluation Plan</h2>
          <p className="text-gray-700 whitespace-pre-wrap">{proposal.evaluation_plan}</p>
        </div>
      </div>
    </div>
  );
}