'use client';

import { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Save } from 'lucide-react';

interface ProposalEditProps {
  params: { id: string };
}

export default function EditProposalPage({ params }: ProposalEditProps) {
  const router = useRouter();

  const { data: proposal, isLoading } = useQuery({
    queryKey: ['proposal', params.id],
    queryFn: async () => {
      return {
        id: params.id,
        title: 'Community Health Mobile Clinic Initiative',
        grant_id: '1',
        organization_id: '1',
        amount_requested: 150000,
        executive_summary: 'This proposal outlines a comprehensive mobile health clinic initiative...',
        project_description: 'Our mobile clinic will provide essential healthcare services...',
        goals_objectives: '1. Serve 5,000 patients in the first year\n2. Reduce emergency room visits by 30%',
        methodology: 'We will deploy two fully-equipped mobile clinics...',
        budget_narrative: 'Personnel: $80,000\nEquipment: $40,000\nOperations: $30,000',
        evaluation_plan: 'We will track patient outcomes, satisfaction scores, and cost savings...'
      };
    }
  });

  const [formData, setFormData] = useState({
    title: '',
    grant_id: '',
    organization_id: '',
    amount_requested: 0,
    executive_summary: '',
    project_description: '',
    goals_objectives: '',
    methodology: '',
    budget_narrative: '',
    evaluation_plan: ''
  });

  useEffect(() => {
    if (proposal) {
      setFormData({
        title: proposal.title,
        grant_id: proposal.grant_id,
        organization_id: proposal.organization_id,
        amount_requested: proposal.amount_requested,
        executive_summary: proposal.executive_summary,
        project_description: proposal.project_description,
        goals_objectives: proposal.goals_objectives,
        methodology: proposal.methodology,
        budget_narrative: proposal.budget_narrative,
        evaluation_plan: proposal.evaluation_plan
      });
    }
  }, [proposal]);

  const updateProposal = useMutation({
    mutationFn: async (data: typeof formData) => {
      console.log('Updating proposal:', data);
      return { id: params.id, ...data };
    },
    onSuccess: () => {
      router.push(`/dashboard/proposals/${params.id}`);
    }
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'amount_requested' ? parseFloat(value) || 0 : value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateProposal.mutate(formData);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href={`/dashboard/proposals/${params.id}`} className="p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Edit Proposal</h1>
            <p className="mt-1 text-sm text-gray-500">Update your proposal content</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Basic Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Proposal Title</label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Amount Requested</label>
              <input
                type="number"
                name="amount_requested"
                value={formData.amount_requested || ''}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Proposal Content</h2>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Executive Summary</label>
              <textarea
                name="executive_summary"
                value={formData.executive_summary}
                onChange={handleChange}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Project Description</label>
              <textarea
                name="project_description"
                value={formData.project_description}
                onChange={handleChange}
                rows={6}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Goals & Objectives</label>
              <textarea
                name="goals_objectives"
                value={formData.goals_objectives}
                onChange={handleChange}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Methodology</label>
              <textarea
                name="methodology"
                value={formData.methodology}
                onChange={handleChange}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Budget Narrative</label>
              <textarea
                name="budget_narrative"
                value={formData.budget_narrative}
                onChange={handleChange}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Evaluation Plan</label>
              <textarea
                name="evaluation_plan"
                value={formData.evaluation_plan}
                onChange={handleChange}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end space-x-4">
          <Link
            href={`/dashboard/proposals/${params.id}`}
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={updateProposal.isPending}
            className="inline-flex items-center px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {updateProposal.isPending ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}