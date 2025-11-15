'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { Users, Plus, Search, Filter, Star, MapPin, Briefcase, ExternalLink } from 'lucide-react';

interface Partner {
  id: string;
  name: string;
  type: string;
  category: string;
  location: string;
  description: string;
  rating: number;
  partnerships_count: number;
  verified: boolean;
}

export default function PartnersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [showFilters, setShowFilters] = useState(false);

  const { data: partners, isLoading } = useQuery<Partner[]>({
    queryKey: ['partners', searchQuery, filterCategory],
    queryFn: async () => {
      return [
        {
          id: '1',
          name: 'Tech for Good Foundation',
          type: 'Technology Partner',
          category: 'Technology',
          location: 'San Francisco, CA',
          description: 'Providing technology solutions for nonprofits',
          rating: 4.8,
          partnerships_count: 45,
          verified: true
        },
        {
          id: '2',
          name: 'Community Wellness Center',
          type: 'Service Provider',
          category: 'Healthcare',
          location: 'Oakland, CA',
          description: 'Healthcare services and wellness programs',
          rating: 4.6,
          partnerships_count: 32,
          verified: true
        },
        {
          id: '3',
          name: 'Education First Alliance',
          type: 'Educational Partner',
          category: 'Education',
          location: 'Berkeley, CA',
          description: 'Supporting educational initiatives and programs',
          rating: 4.9,
          partnerships_count: 58,
          verified: true
        }
      ];
    }
  });

  const filteredPartners = partners?.filter(partner => {
    const matchesSearch = partner.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = filterCategory === 'all' || partner.category === filterCategory;
    return matchesSearch && matchesCategory;
  });

  const stats = {
    total: partners?.length || 0,
    verified: partners?.filter(p => p.verified).length || 0,
    active: partners?.reduce((sum, p) => sum + p.partnerships_count, 0) || 0
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Partners Marketplace</h1>
          <p className="mt-1 text-sm text-gray-500">Discover and connect with potential partners</p>
        </div>
        <Link
          href="/dashboard/partnerships"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Users className="w-5 h-5 mr-2" />
          My Partnerships
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Available Partners</p>
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
              <p className="text-sm text-gray-500">Verified Partners</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.verified}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <Star className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Active Partnerships</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.active}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <Briefcase className="w-6 h-6 text-purple-600" />
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
              placeholder="Search partners..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <Filter className="w-5 h-5 mr-2" />
            Filters
          </button>
        </div>

        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Categories</option>
                  <option value="Technology">Technology</option>
                  <option value="Healthcare">Healthcare</option>
                  <option value="Education">Education</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          <div className="col-span-3 p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : filteredPartners && filteredPartners.length > 0 ? (
          filteredPartners.map((partner) => (
            <div key={partner.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{partner.name}</h3>
                    {partner.verified && (
                      <Star className="w-5 h-5 text-yellow-500 fill-current" />
                    )}
                  </div>
                  <p className="text-sm text-blue-600">{partner.type}</p>
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-4 line-clamp-2">{partner.description}</p>

              <div className="space-y-2 mb-4">
                <div className="flex items-center text-sm text-gray-500">
                  <MapPin className="w-4 h-4 mr-2" />
                  {partner.location}
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <Briefcase className="w-4 h-4 mr-2" />
                  {partner.partnerships_count} partnerships
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <Star className="w-4 h-4 mr-2 text-yellow-500" />
                  {partner.rating} rating
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <Link
                  href={`/dashboard/partners/${partner.id}`}
                  className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  <ExternalLink className="w-4 h-4 mr-2" />
                  View Profile
                </Link>
                <button className="flex-1 inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  Connect
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-3 p-12 text-center">
            <Users className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No partners found</h3>
          </div>
        )}
      </div>
    </div>
  );
}