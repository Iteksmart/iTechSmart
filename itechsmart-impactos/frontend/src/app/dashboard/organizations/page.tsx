'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { 
  Building2, 
  Plus, 
  Search, 
  Filter,
  Users,
  TrendingUp,
  Calendar,
  MoreVertical,
  Edit,
  Trash2,
  Settings
} from 'lucide-react';

interface Organization {
  id: string;
  name: string;
  type: string;
  mission: string;
  website: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  ein: string;
  founded_date: string;
  annual_budget: number;
  staff_count: number;
  volunteer_count: number;
  programs_count: number;
  impact_score: number;
  created_at: string;
}

export default function OrganizationsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [showFilters, setShowFilters] = useState(false);

  // Fetch organizations
  const { data: organizations, isLoading } = useQuery<Organization[]>({
    queryKey: ['organizations', searchQuery, filterType],
    queryFn: async () => {
      // TODO: Replace with actual API call
      return [
        {
          id: '1',
          name: 'Community Health Initiative',
          type: 'Healthcare',
          mission: 'Providing accessible healthcare to underserved communities',
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
          impact_score: 87,
          created_at: '2024-01-15T10:00:00Z'
        },
        {
          id: '2',
          name: 'Youth Education Foundation',
          type: 'Education',
          mission: 'Empowering youth through quality education and mentorship',
          website: 'https://yef.org',
          email: 'contact@yef.org',
          phone: '(555) 234-5678',
          address: '456 Oak Ave',
          city: 'Oakland',
          state: 'CA',
          zip_code: '94601',
          ein: '23-4567890',
          founded_date: '2012-09-20',
          annual_budget: 1800000,
          staff_count: 32,
          volunteer_count: 85,
          programs_count: 12,
          impact_score: 92,
          created_at: '2024-01-10T09:00:00Z'
        },
        {
          id: '3',
          name: 'Environmental Action Network',
          type: 'Environment',
          mission: 'Protecting and restoring natural ecosystems',
          website: 'https://ean.org',
          email: 'hello@ean.org',
          phone: '(555) 345-6789',
          address: '789 Green Blvd',
          city: 'Berkeley',
          state: 'CA',
          zip_code: '94704',
          ein: '34-5678901',
          founded_date: '2018-06-10',
          annual_budget: 3200000,
          staff_count: 58,
          volunteer_count: 200,
          programs_count: 15,
          impact_score: 95,
          created_at: '2024-01-05T08:00:00Z'
        }
      ];
    }
  });

  const filteredOrganizations = organizations?.filter(org => {
    const matchesSearch = org.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         org.mission.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'all' || org.type === filterType;
    return matchesSearch && matchesType;
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
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Organizations</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your nonprofit organizations and their programs
          </p>
        </div>
        <Link
          href="/dashboard/organizations/new"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5 mr-2" />
          Add Organization
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Organizations</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {organizations?.length || 0}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Building2 className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Programs</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {organizations?.reduce((sum, org) => sum + org.programs_count, 0) || 0}
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Staff</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {organizations?.reduce((sum, org) => sum + org.staff_count, 0) || 0}
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
              <p className="text-sm text-gray-500">Avg Impact Score</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {organizations?.length 
                  ? Math.round(organizations.reduce((sum, org) => sum + org.impact_score, 0) / organizations.length)
                  : 0}
              </p>
            </div>
            <div className="p-3 bg-orange-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search organizations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Filter className="w-5 h-5 mr-2" />
            Filters
          </button>
        </div>

        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Organization Type
                </label>
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">All Types</option>
                  <option value="Healthcare">Healthcare</option>
                  <option value="Education">Education</option>
                  <option value="Environment">Environment</option>
                  <option value="Social Services">Social Services</option>
                  <option value="Arts & Culture">Arts & Culture</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Organizations List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-500">Loading organizations...</p>
          </div>
        ) : filteredOrganizations && filteredOrganizations.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Organization
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Budget
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Programs
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Impact Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Founded
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredOrganizations.map((org) => (
                  <tr key={org.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          <Building2 className="w-6 h-6 text-blue-600" />
                        </div>
                        <div className="ml-4">
                          <Link
                            href={`/dashboard/organizations/${org.id}`}
                            className="text-sm font-medium text-gray-900 hover:text-blue-600"
                          >
                            {org.name}
                          </Link>
                          <p className="text-sm text-gray-500">{org.city}, {org.state}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                        {org.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(org.annual_budget)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {org.programs_count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                          <div
                            className="bg-green-600 h-2 rounded-full"
                            style={{ width: `${org.impact_score}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900">
                          {org.impact_score}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(org.founded_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        <Link
                          href={`/dashboard/organizations/${org.id}/edit`}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          <Edit className="w-4 h-4" />
                        </Link>
                        <Link
                          href={`/dashboard/organizations/${org.id}/settings`}
                          className="text-gray-600 hover:text-gray-900"
                        >
                          <Settings className="w-4 h-4" />
                        </Link>
                        <button className="text-red-600 hover:text-red-900">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-12 text-center">
            <Building2 className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No organizations found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating a new organization.
            </p>
            <div className="mt-6">
              <Link
                href="/dashboard/organizations/new"
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-5 h-5 mr-2" />
                Add Organization
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}