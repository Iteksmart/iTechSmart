'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { Users, Plus, Search, Filter, Calendar, CheckCircle, Clock } from 'lucide-react';

interface Partnership {
  id: string;
  partner_name: string;
  type: string;
  status: 'active' | 'pending' | 'completed';
  start_date: string;
  end_date: string | null;
  description: string;
}

export default function PartnershipsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  const { data: partnerships, isLoading } = useQuery<Partnership[]>({
    queryKey: ['partnerships', searchQuery, filterStatus],
    queryFn: async () => {
      return [
        {
          id: '1',
          partner_name: 'Tech for Good Foundation',
          type: 'Technology Partnership',
          status: 'active',
          start_date: '2024-01-15',
          end_date: null,
          description: 'Providing IT infrastructure and support'
        },
        {
          id: '2',
          partner_name: 'Community Wellness Center',
          type: 'Service Partnership',
          status: 'active',
          start_date: '2024-02-01',
          end_date: '2024-12-31',
          description: 'Healthcare services collaboration'
        },
        {
          id: '3',
          partner_name: 'Education First Alliance',
          type: 'Program Partnership',
          status: 'pending',
          start_date: '2024-05-01',
          end_date: null,
          description: 'Joint educational program development'
        }
      ];
    }
  });

  const filteredPartnerships = partnerships?.filter(partnership => {
    const matchesSearch = partnership.partner_name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === 'all' || partnership.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const stats = {
    total: partnerships?.length || 0,
    active: partnerships?.filter(p => p.status === 'active').length || 0,
    pending: partnerships?.filter(p => p.status === 'pending').length || 0
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
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Partnerships</h1>
          <p className="mt-1 text-sm text-gray-500">Manage your active partnerships</p>
        </div>
        <Link
          href="/dashboard/partnerships/new"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-5 h-5 mr-2" />
          New Partnership
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Partnerships</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Active</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.active}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Pending</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.pending}</p>
            </div>
            <div className="p-3 bg-yellow-100 rounded-lg">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search partnerships..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>

      <div className="space-y-4">
        {isLoading ? (
          <div className="p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : filteredPartnerships && filteredPartnerships.length > 0 ? (
          filteredPartnerships.map((partnership) => (
            <div key={partnership.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <Link
                      href={`/dashboard/partnerships/${partnership.id}`}
                      className="text-lg font-semibold text-gray-900 hover:text-blue-600"
                    >
                      {partnership.partner_name}
                    </Link>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(partnership.status)}`}>
                      {partnership.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-4">{partnership.description}</p>
                  <div className="flex items-center space-x-6 text-sm text-gray-500">
                    <div className="flex items-center">
                      <Calendar className="w-4 h-4 mr-2" />
                      Started: {formatDate(partnership.start_date)}
                    </div>
                    {partnership.end_date && (
                      <div className="flex items-center">
                        <Calendar className="w-4 h-4 mr-2" />
                        Ends: {formatDate(partnership.end_date)}
                      </div>
                    )}
                  </div>
                </div>
                <Link
                  href={`/dashboard/partnerships/${partnership.id}`}
                  className="ml-4 px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  View Details
                </Link>
              </div>
            </div>
          ))
        ) : (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <Users className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No partnerships found</h3>
            <p className="mt-1 text-sm text-gray-500">Get started by creating a new partnership.</p>
            <div className="mt-6">
              <Link
                href="/dashboard/partnerships/new"
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Plus className="w-5 h-5 mr-2" />
                New Partnership
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}