'use client';

import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, FileText, Save } from 'lucide-react';

export default function NewProposalPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const grantId = searchParams.get('grant');

  const [formData, setFormData] = useState({
    title: '',
    grant_id: grantId || '',
    organization_id: '',
    amount_requested: 0,
    executive_summary: '',
    project_description: '',
    goals_objectives: '',
    methodology: '',
    budget_narrative: '',
    evaluation_plan: ''
  });

  const { data: grants } = useQuery({
    queryKey: ['grants'],
    queryFn: async () => {
      return [
        { id: '1', title: 'Community Health Innovation Grant' },
        { id: '2', title: 'Youth Education Excellence Award' }
      ];
    }
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

  const createProposal = useMutation({
    mutationFn: async (data: typeof formData) => {
      console.log('Creating proposal:', data);
      return { id: '123', ...data };
    },
    onSuccess: (data) => {
      router.push(`/dashboard/proposals/${data.id}`);
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
    createProposal.mutate(formData);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard/proposals" className="p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create New Proposal</h1>
            <p className="mt-1 text-sm text-gray-500">Draft your grant proposal</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Basic Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Proposal Title *</label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Grant *</label>
              <select
                name="grant_id"
                value={formData.grant_id}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Select grant</option>
                {grants?.map((grant) => (
                  <option key={grant.id} value={grant.id}>{grant.title}</option>
                ))}
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
              <label className="block text-sm font-medium text-gray-700 mb-2">Amount Requested *</label>
              <input
                type="number"
                name="amount_requested"
                value={formData.amount_requested || ''}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
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
            href="/dashboard/proposals"
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={createProposal.isPending}
            className="inline-flex items-center px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {createProposal.isPending ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Creating...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Create Proposal
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}