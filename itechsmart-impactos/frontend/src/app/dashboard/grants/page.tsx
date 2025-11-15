'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { 
  FileText, 
  Plus, 
  Search, 
  Filter,
  DollarSign,
  Calendar,
  TrendingUp,
  ExternalLink,
  Bookmark,
  Clock
} from 'lucide-react';

interface Grant {
  id: string;
  title: string;
  funder: string;
  amount_min: number;
  amount_max: number;
  deadline: string;
  category: string;
  eligibility: string;
  status: 'open' | 'closing-soon' | 'closed';
  match_score: number;
  saved: boolean;
}

export default function GrantsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterStatus, setFilterStatus] = useState('open');
  const [showFilters, setShowFilters] = useState(false);

  const { data: grants, isLoading } = useQuery<Grant[]>({
    queryKey: ['grants', searchQuery, filterCategory, filterStatus],
    queryFn: async () => {
      return [
        {
          id: '1',
          title: 'Community Health Innovation Grant',
          funder: 'National Health Foundation',
          amount_min: 50000,
          amount_max: 250000,
          deadline: '2024-06-30',
          category: 'Healthcare',
          eligibility: '501(c)(3) organizations serving underserved communities',
          status: 'open',
          match_score: 92,
          saved: true
        },
        {
          id: '2',
          title: 'Youth Education Excellence Award',
          funder: 'Education First Foundation',
          amount_min: 25000,
          amount_max: 100000,
          deadline: '2024-05-15',
          category: 'Education',
          eligibility: 'Organizations focused on K-12 education',
          status: 'closing-soon',
          match_score: 88,
          saved: false
        },
        {
          id: '3',
          title: 'Environmental Sustainability Fund',
          funder: 'Green Earth Initiative',
          amount_min: 100000,
          amount_max: 500000,
          deadline: '2024-08-31',
          category: 'Environment',
          eligibility: 'Environmental nonprofits with 3+ years of operation',
          status: 'open',
          match_score: 85,
          saved: true
        },
        {
          id: '4',
          title: 'Social Services Innovation Grant',
          funder: 'Community Impact Fund',
          amount_min: 30000,
          amount_max: 150000,
          deadline: '2024-07-20',
          category: 'Social Services',
          eligibility: 'Nonprofits serving vulnerable populations',
          status: 'open',
          match_score: 78,
          saved: false
        },
        {
          id: '5',
          title: 'Arts & Culture Development Grant',
          funder: 'National Arts Council',
          amount_min: 15000,
          amount_max: 75000,
          deadline: '2024-04-30',
          category: 'Arts & Culture',
          eligibility: 'Arts organizations and cultural institutions',
          status: 'closing-soon',
          match_score: 72,
          saved: false
        }
      ];
    }
  });

  const filteredGrants = grants?.filter(grant => {
    const matchesSearch = grant.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         grant.funder.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = filterCategory === 'all' || grant.category === filterCategory;
    const matchesStatus = filterStatus === 'all' || grant.status === filterStatus;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const stats = {
    total: grants?.length || 0,
    open: grants?.filter(g => g.status === 'open').length || 0,
    saved: grants?.filter(g => g.saved).length || 0,
    closingSoon: grants?.filter(g => g.status === 'closing-soon').length || 0
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

  const getDaysUntilDeadline = (deadline: string) => {
    const days = Math.ceil((new Date(deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
    return days;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'bg-green-100 text-green-800';
      case 'closing-soon': return 'bg-yellow-100 text-yellow-800';
      case 'closed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Grant Opportunities</h1>
          <p className="mt-1 text-sm text-gray-500">
            Discover and apply for grants that match your organization
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            href="/dashboard/grants/search"
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Search className="w-4 h-4 mr-2" />
            Advanced Search
          </Link>
          <Link
            href="/dashboard/proposals"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <FileText className="w-4 h-4 mr-2" />
            My Proposals
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Available Grants</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Open Applications</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.open}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Saved Grants</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.saved}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <Bookmark className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Closing Soon</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.closingSoon}</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-lg">
              <Clock className="w-6 h-6 text-orange-600" />
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
              placeholder="Search grants by title or funder..."
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
                  Category
                </label>
                <select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">All Categories</option>
                  <option value="Healthcare">Healthcare</option>
                  <option value="Education">Education</option>
                  <option value="Environment">Environment</option>
                  <option value="Social Services">Social Services</option>
                  <option value="Arts & Culture">Arts & Culture</option>
                </select>
              </div>
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
                  <option value="open">Open</option>
                  <option value="closing-soon">Closing Soon</option>
                  <option value="closed">Closed</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Grants List */}
      {isLoading ? (
        <div className="p-12 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-500">Loading grants...</p>
        </div>
      ) : filteredGrants && filteredGrants.length > 0 ? (
        <div className="space-y-4">
          {filteredGrants.map((grant) => {
            const daysLeft = getDaysUntilDeadline(grant.deadline);
            return (
              <div key={grant.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <Link
                            href={`/dashboard/grants/${grant.id}`}
                            className="text-xl font-semibold text-gray-900 hover:text-blue-600"
                          >
                            {grant.title}
                          </Link>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(grant.status)}`}>
                            {grant.status === 'closing-soon' ? `${daysLeft} days left` : grant.status}
                          </span>
                          {grant.saved && (
                            <Bookmark className="w-5 h-5 text-yellow-500 fill-current" />
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{grant.funder}</p>
                      </div>
                      <div className="text-right ml-4">
                        <div className="flex items-center justify-end space-x-2 mb-1">
                          <div className="px-3 py-1 bg-blue-100 rounded-lg">
                            <p className="text-xs text-blue-600 font-medium">Match: {grant.match_score}%</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                      <div className="flex items-center space-x-2">
                        <DollarSign className="w-5 h-5 text-gray-400" />
                        <div>
                          <p className="text-xs text-gray-500">Award Range</p>
                          <p className="text-sm font-medium text-gray-900">
                            {formatCurrency(grant.amount_min)} - {formatCurrency(grant.amount_max)}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2">
                        <Calendar className="w-5 h-5 text-gray-400" />
                        <div>
                          <p className="text-xs text-gray-500">Deadline</p>
                          <p className="text-sm font-medium text-gray-900">{formatDate(grant.deadline)}</p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2">
                        <FileText className="w-5 h-5 text-gray-400" />
                        <div>
                          <p className="text-xs text-gray-500">Category</p>
                          <p className="text-sm font-medium text-gray-900">{grant.category}</p>
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                      <p className="text-xs text-gray-500 mb-1">Eligibility</p>
                      <p className="text-sm text-gray-700">{grant.eligibility}</p>
                    </div>

                    <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
                      <div className="flex items-center space-x-2">
                        {!grant.saved && (
                          <button className="inline-flex items-center px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                            <Bookmark className="w-4 h-4 mr-1" />
                            Save
                          </button>
                        )}
                        <Link
                          href={`/dashboard/grants/${grant.id}`}
                          className="inline-flex items-center px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          <ExternalLink className="w-4 h-4 mr-1" />
                          View Details
                        </Link>
                      </div>
                      <Link
                        href={`/dashboard/proposals/new?grant=${grant.id}`}
                        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Start Proposal
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No grants found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your search or filters to find more opportunities.
          </p>
        </div>
      )}
    </div>
  );
}