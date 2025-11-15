'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { 
  ArrowLeft, 
  Target, 
  Edit,
  BarChart3,
  Users,
  Calendar,
  DollarSign,
  TrendingUp,
  Award,
  FileText
} from 'lucide-react';

interface ProgramDetailsProps {
  params: {
    id: string;
  };
}

export default function ProgramDetailsPage({ params }: ProgramDetailsProps) {
  const { data: program, isLoading } = useQuery({
    queryKey: ['program', params.id],
    queryFn: async () => {
      return {
        id: params.id,
        name: 'Youth Mentorship Program',
        organization_id: '1',
        organization_name: 'Community Health Initiative',
        description: 'Connecting at-risk youth with professional mentors for career guidance and personal development. This comprehensive program provides one-on-one mentoring, group workshops, and career exploration opportunities.',
        category: 'Education',
        status: 'active',
        start_date: '2024-01-01',
        end_date: null,
        budget: 150000,
        spent: 87500,
        participants_target: 100,
        participants_current: 78,
        participants_completed: 45,
        impact_score: 85,
        goals: 'Improve academic performance, increase college enrollment rates, develop professional skills',
        success_metrics: 'GPA improvement, college applications, mentor satisfaction scores',
        created_at: '2024-01-01T10:00:00Z',
        updated_at: '2024-01-20T14:30:00Z'
      };
    }
  });

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
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
      case 'active': return 'bg-green-100 text-green-800';
      case 'planned': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      case 'on-hold': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-500">Loading program...</p>
        </div>
      </div>
    );
  }

  if (!program) {
    return (
      <div className="text-center py-12">
        <Target className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Program not found</h3>
        <p className="mt-1 text-sm text-gray-500">
          The program you're looking for doesn't exist.
        </p>
        <div className="mt-6">
          <Link
            href="/dashboard/programs"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Programs
          </Link>
        </div>
      </div>
    );
  }

  const budgetUsed = (program.spent / program.budget) * 100;
  const participantProgress = (program.participants_current / program.participants_target) * 100;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            href="/dashboard/programs"
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-3xl font-bold text-gray-900">{program.name}</h1>
              <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(program.status)}`}>
                {program.status}
              </span>
            </div>
            <p className="mt-1 text-sm text-gray-500">
              {program.organization_name} • {program.category}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            href={`/dashboard/programs/${params.id}/edit`}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Edit className="w-4 h-4 mr-2" />
            Edit
          </Link>
          <Link
            href={`/dashboard/programs/${params.id}/metrics`}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            View Metrics
          </Link>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Budget</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {formatCurrency(program.budget)}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {formatCurrency(program.spent)} spent
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <DollarSign className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full"
                style={{ width: `${budgetUsed}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-1">{Math.round(budgetUsed)}% used</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Participants</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {program.participants_current}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                of {program.participants_target} target
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${participantProgress}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-1">{Math.round(participantProgress)}% of target</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Completed</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {program.participants_completed}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                participants
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <Award className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Impact Score</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {program.impact_score}/100
              </p>
            </div>
            <div className="p-3 bg-orange-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
          </div>
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-orange-600 h-2 rounded-full"
                style={{ width: `${program.impact_score}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Program Description</h2>
            <p className="text-gray-700 leading-relaxed">{program.description}</p>
          </div>

          {/* Goals */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Program Goals</h2>
            <p className="text-gray-700 leading-relaxed">{program.goals}</p>
          </div>

          {/* Success Metrics */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Success Metrics</h2>
            <p className="text-gray-700 leading-relaxed">{program.success_metrics}</p>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
            <div className="space-y-4">
              <div className="flex items-start space-x-3 pb-4 border-b border-gray-200">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Users className="w-4 h-4 text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">5 new participants enrolled</p>
                  <p className="text-xs text-gray-500 mt-1">2 days ago</p>
                </div>
              </div>
              <div className="flex items-start space-x-3 pb-4 border-b border-gray-200">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Award className="w-4 h-4 text-green-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">3 participants completed program</p>
                  <p className="text-xs text-gray-500 mt-1">5 days ago</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <FileText className="w-4 h-4 text-purple-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Monthly report generated</p>
                  <p className="text-xs text-gray-500 mt-1">1 week ago</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Program Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Program Details</h2>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Start Date</p>
                  <p className="text-sm font-medium text-gray-900">{formatDate(program.start_date)}</p>
                </div>
              </div>
              {program.end_date && (
                <div className="flex items-start space-x-3">
                  <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500">End Date</p>
                    <p className="text-sm font-medium text-gray-900">{formatDate(program.end_date)}</p>
                  </div>
                </div>
              )}
              <div className="flex items-start space-x-3">
                <Target className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Category</p>
                  <span className="inline-block px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                    {program.category}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Organization */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Organization</h2>
            <Link
              href={`/dashboard/organizations/${program.organization_id}`}
              className="flex items-center space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors"
            >
              <div className="p-2 bg-blue-100 rounded-lg">
                <Target className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">{program.organization_name}</p>
                <p className="text-xs text-gray-500">View organization →</p>
              </div>
            </Link>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-2">
              <Link
                href={`/dashboard/programs/${params.id}/participants`}
                className="block w-full px-4 py-2 text-sm text-center border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Manage Participants
              </Link>
              <Link
                href={`/dashboard/programs/${params.id}/metrics`}
                className="block w-full px-4 py-2 text-sm text-center border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                View Metrics
              </Link>
              <Link
                href={`/dashboard/reports/new?program=${params.id}`}
                className="block w-full px-4 py-2 text-sm text-center border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Generate Report
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}