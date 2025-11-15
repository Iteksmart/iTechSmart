'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { 
  ArrowLeft, 
  Building2, 
  Mail, 
  Phone, 
  Globe, 
  MapPin,
  Calendar,
  Users,
  DollarSign,
  TrendingUp,
  Edit,
  Settings,
  FileText,
  Award,
  Target
} from 'lucide-react';

interface OrganizationDetailsProps {
  params: {
    id: string;
  };
}

export default function OrganizationDetailsPage({ params }: OrganizationDetailsProps) {
  const { data: organization, isLoading } = useQuery({
    queryKey: ['organization', params.id],
    queryFn: async () => {
      // TODO: Replace with actual API call
      return {
        id: params.id,
        name: 'Community Health Initiative',
        type: 'Healthcare',
        mission: 'Providing accessible healthcare to underserved communities through innovative programs and partnerships.',
        website: 'https://chi.org',
        email: 'info@chi.org',
        phone: '(555) 123-4567',
        address: '123 Main St',
        city: 'San Francisco',
        state: 'CA',
        zip_code: '94102',
        ein: '12-3456789',
        founded_date: '2015-03-15',
        annual_budget: 2500000,
        staff_count: 45,
        volunteer_count: 120,
        programs_count: 8,
        active_grants: 5,
        total_funding: 3200000,
        impact_score: 87,
        beneficiaries_served: 15000,
        created_at: '2024-01-15T10:00:00Z',
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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-500">Loading organization...</p>
        </div>
      </div>
    );
  }

  if (!organization) {
    return (
      <div className="text-center py-12">
        <Building2 className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Organization not found</h3>
        <p className="mt-1 text-sm text-gray-500">
          The organization you're looking for doesn't exist.
        </p>
        <div className="mt-6">
          <Link
            href="/dashboard/organizations"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Organizations
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            href="/dashboard/organizations"
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{organization.name}</h1>
            <p className="mt-1 text-sm text-gray-500">
              {organization.type} • Founded {formatDate(organization.founded_date)}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            href={`/dashboard/organizations/${params.id}/edit`}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Edit className="w-4 h-4 mr-2" />
            Edit
          </Link>
          <Link
            href={`/dashboard/organizations/${params.id}/settings`}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </Link>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Annual Budget</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {formatCurrency(organization.annual_budget)}
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <DollarSign className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Active Programs</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {organization.programs_count}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Target className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">People Served</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {organization.beneficiaries_served.toLocaleString()}
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <Users className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Impact Score</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {organization.impact_score}/100
              </p>
            </div>
            <div className="p-3 bg-orange-100 rounded-lg">
              <Award className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Mission Statement */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Mission Statement</h2>
            <p className="text-gray-700 leading-relaxed">{organization.mission}</p>
          </div>

          {/* Team Overview */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Team Overview</h2>
            <div className="grid grid-cols-2 gap-6">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Users className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Staff Members</p>
                    <p className="text-2xl font-bold text-gray-900">{organization.staff_count}</p>
                  </div>
                </div>
              </div>
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Users className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Volunteers</p>
                    <p className="text-2xl font-bold text-gray-900">{organization.volunteer_count}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Funding Overview */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Funding Overview</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm text-gray-500">Total Funding Received</p>
                  <p className="text-xl font-bold text-gray-900">{formatCurrency(organization.total_funding)}</p>
                </div>
                <TrendingUp className="w-8 h-8 text-green-600" />
              </div>
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm text-gray-500">Active Grants</p>
                  <p className="text-xl font-bold text-gray-900">{organization.active_grants}</p>
                </div>
                <FileText className="w-8 h-8 text-blue-600" />
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
            <div className="space-y-4">
              <div className="flex items-start space-x-3 pb-4 border-b border-gray-200">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <FileText className="w-4 h-4 text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">New grant proposal submitted</p>
                  <p className="text-xs text-gray-500 mt-1">2 days ago</p>
                </div>
              </div>
              <div className="flex items-start space-x-3 pb-4 border-b border-gray-200">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Award className="w-4 h-4 text-green-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Impact report generated</p>
                  <p className="text-xs text-gray-500 mt-1">5 days ago</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Users className="w-4 h-4 text-purple-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">New program launched</p>
                  <p className="text-xs text-gray-500 mt-1">1 week ago</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Contact Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h2>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <Mail className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Email</p>
                  <a href={`mailto:${organization.email}`} className="text-sm text-blue-600 hover:underline">
                    {organization.email}
                  </a>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <Phone className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Phone</p>
                  <a href={`tel:${organization.phone}`} className="text-sm text-blue-600 hover:underline">
                    {organization.phone}
                  </a>
                </div>
              </div>
              {organization.website && (
                <div className="flex items-start space-x-3">
                  <Globe className="w-5 h-5 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500">Website</p>
                    <a 
                      href={organization.website} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline"
                    >
                      {organization.website}
                    </a>
                  </div>
                </div>
              )}
              <div className="flex items-start space-x-3">
                <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Address</p>
                  <p className="text-sm text-gray-900">
                    {organization.address}<br />
                    {organization.city}, {organization.state} {organization.zip_code}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Organization Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Organization Details</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">EIN (Tax ID)</p>
                <p className="text-sm font-medium text-gray-900">{organization.ein}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Organization Type</p>
                <span className="inline-block px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                  {organization.type}
                </span>
              </div>
              <div>
                <p className="text-sm text-gray-500">Founded</p>
                <p className="text-sm font-medium text-gray-900">{formatDate(organization.founded_date)}</p>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-2">
              <Link
                href={`/dashboard/programs?org=${params.id}`}
                className="block w-full px-4 py-2 text-sm text-center border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                View Programs
              </Link>
              <Link
                href={`/dashboard/reports?org=${params.id}`}
                className="block w-full px-4 py-2 text-sm text-center border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Generate Report
              </Link>
              <Link
                href={`/dashboard/grants?org=${params.id}`}
                className="block w-full px-4 py-2 text-sm text-center border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                View Grants
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}