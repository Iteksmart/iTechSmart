'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { 
  Target, 
  Plus, 
  Search, 
  Filter,
  Users,
  TrendingUp,
  Calendar,
  DollarSign,
  Edit,
  Trash2,
  BarChart3
} from 'lucide-react';

interface Program {
  id: string;
  name: string;
  organization_id: string;
  organization_name: string;
  description: string;
  category: string;
  status: 'active' | 'planned' | 'completed' | 'on-hold';
  start_date: string;
  end_date: string | null;
  budget: number;
  participants_target: number;
  participants_current: number;
  impact_score: number;
  created_at: string;
}

export default function ProgramsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterCategory, setFilterCategory] = useState('all');
  const [showFilters, setShowFilters] = useState(false);

  const { data: programs, isLoading } = useQuery<Program[]>({
    queryKey: ['programs', searchQuery, filterStatus, filterCategory],
    queryFn: async () => {
      // TODO: Replace with actual API call
      return [
        {
          id: '1',
          name: 'Youth Mentorship Program',
          organization_id: '1',
          organization_name: 'Community Health Initiative',
          description: 'Connecting at-risk youth with professional mentors for career guidance and personal development',
          category: 'Education',
          status: 'active',
          start_date: '2024-01-01',
          end_date: null,
          budget: 150000,
          participants_target: 100,
          participants_current: 78,
          impact_score: 85,
          created_at: '2024-01-01T10:00:00Z'
        },
        {
          id: '2',
          name: 'Community Health Screenings',
          organization_id: '1',
          organization_name: 'Community Health Initiative',
          description: 'Free health screenings and preventive care for underserved communities',
          category: 'Healthcare',
          status: 'active',
          start_date: '2024-02-15',
          end_date: '2024-12-31',
          budget: 250000,
          participants_target: 500,
          participants_current: 342,
          impact_score: 92,
          created_at: '2024-02-01T09:00:00Z'
        },
        {
          id: '3',
          name: 'After-School Tutoring',
          organization_id: '2',
          organization_name: 'Youth Education Foundation',
          description: 'Academic support and homework help for elementary school students',
          category: 'Education',
          status: 'active',
          start_date: '2023-09-01',
          end_date: '2024-06-30',
          budget: 80000,
          participants_target: 150,
          participants_current: 145,
          impact_score: 88,
          created_at: '2023-08-15T08:00:00Z'
        },
        {
          id: '4',
          name: 'Urban Garden Initiative',
          organization_id: '3',
          organization_name: 'Environmental Action Network',
          description: 'Creating community gardens in urban areas to promote sustainability',
          category: 'Environment',
          status: 'planned',
          start_date: '2024-04-01',
          end_date: '2024-10-31',
          budget: 120000,
          participants_target: 200,
          participants_current: 0,
          impact_score: 0,
          created_at: '2024-01-20T11:00:00Z'
        }
      ];
    }
  });

  const filteredPrograms = programs?.filter(program => {
    const matchesSearch = program.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         program.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === 'all' || program.status === filterStatus;
    const matchesCategory = filterCategory === 'all' || program.category === filterCategory;
    return matchesSearch && matchesStatus && matchesCategory;
  });

  const stats = {
    total: programs?.length || 0,
    active: programs?.filter(p => p.status === 'active').length || 0,
    totalBudget: programs?.reduce((sum, p) => sum + p.budget, 0) || 0,
    totalParticipants: programs?.reduce((sum, p) => sum + p.participants_current, 0) || 0
  };

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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'planned': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      case 'on-hold': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Programs</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage and track your organization's programs
          </p>
        </div>
        <Link
          href="/dashboard/programs/new"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5 mr-2" />
          Add Program
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Programs</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Target className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Active Programs</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.active}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Budget</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {formatCurrency(stats.totalBudget)}
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <DollarSign className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Participants</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {stats.totalParticipants.toLocaleString()}
              </p>
            </div>
            <div className="p-3 bg-orange-100 rounded-lg">
              <Users className="w-6 h-6 text-orange-600" />
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
              placeholder="Search programs..."
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
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Status
                </label>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">All Statuses</option>
                  <option value="active">Active</option>
                  <option value="planned">Planned</option>
                  <option value="completed">Completed</option>
                  <option value="on-hold">On Hold</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category
                </label>
                <select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">All Categories</option>
                  <option value="Education">Education</option>
                  <option value="Healthcare">Healthcare</option>
                  <option value="Environment">Environment</option>
                  <option value="Social Services">Social Services</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Programs Grid */}
      {isLoading ? (
        <div className="p-12 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-500">Loading programs...</p>
        </div>
      ) : filteredPrograms && filteredPrograms.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPrograms.map((program) => (
            <div key={program.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <Link
                      href={`/dashboard/programs/${program.id}`}
                      className="text-lg font-semibold text-gray-900 hover:text-blue-600"
                    >
                      {program.name}
                    </Link>
                    <p className="text-sm text-gray-500 mt-1">{program.organization_name}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(program.status)}`}>
                    {program.status}
                  </span>
                </div>

                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                  {program.description}
                </p>

                <div className="space-y-3 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Budget</span>
                    <span className="font-medium text-gray-900">{formatCurrency(program.budget)}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Participants</span>
                    <span className="font-medium text-gray-900">
                      {program.participants_current} / {program.participants_target}
                    </span>
                  </div>
                  <div>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-500">Progress</span>
                      <span className="font-medium text-gray-900">
                        {Math.round((program.participants_current / program.participants_target) * 100)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${Math.min((program.participants_current / program.participants_target) * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <div className="flex items-center space-x-2">
                    <Link
                      href={`/dashboard/programs/${program.id}/edit`}
                      className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    >
                      <Edit className="w-4 h-4" />
                    </Link>
                    <Link
                      href={`/dashboard/programs/${program.id}/metrics`}
                      className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    >
                      <BarChart3 className="w-4 h-4" />
                    </Link>
                  </div>
                  <Link
                    href={`/dashboard/programs/${program.id}`}
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    View Details →
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Target className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No programs found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating a new program.
          </p>
          <div className="mt-6">
            <Link
              href="/dashboard/programs/new"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-5 h-5 mr-2" />
              Add Program
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}