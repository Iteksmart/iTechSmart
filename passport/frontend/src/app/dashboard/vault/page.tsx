'use client';

import { useState } from 'react';
import {
  Search,
  Plus,
  Key,
  CreditCard,
  FileText,
  Globe,
  Star,
  Eye,
  Copy,
  Edit,
  Trash2,
  Filter,
  SortAsc,
  Lock,
  CheckCircle,
} from 'lucide-react';
import Link from 'next/link';

interface VaultItem {
  id: string;
  type: 'login' | 'card' | 'note' | 'identity';
  title: string;
  username?: string;
  email?: string;
  website?: string;
  category: string;
  favorite: boolean;
  lastUsed: string;
  strength?: 'weak' | 'fair' | 'good' | 'strong';
  icon: string;
}

export default function VaultPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'usage'>('name');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const vaultItems: VaultItem[] = [
    {
      id: '1',
      type: 'login',
      title: 'Netflix',
      username: 'john@example.com',
      website: 'netflix.com',
      category: 'Entertainment',
      favorite: true,
      lastUsed: '2 hours ago',
      strength: 'strong',
      icon: '🎬',
    },
    {
      id: '2',
      type: 'login',
      title: 'Gmail',
      email: 'john.doe@gmail.com',
      website: 'gmail.com',
      category: 'Email',
      favorite: true,
      lastUsed: '5 hours ago',
      strength: 'strong',
      icon: '📧',
    },
    {
      id: '3',
      type: 'login',
      title: 'Bank of America',
      username: 'johndoe',
      website: 'bankofamerica.com',
      category: 'Banking',
      favorite: false,
      lastUsed: '1 day ago',
      strength: 'good',
      icon: '🏦',
    },
    {
      id: '4',
      type: 'card',
      title: 'Visa **** 4242',
      category: 'Payment',
      favorite: false,
      lastUsed: '3 days ago',
      icon: '💳',
    },
    {
      id: '5',
      type: 'login',
      title: 'Amazon',
      email: 'john@example.com',
      website: 'amazon.com',
      category: 'Shopping',
      favorite: false,
      lastUsed: '2 days ago',
      strength: 'weak',
      icon: '🛒',
    },
    {
      id: '6',
      type: 'note',
      title: 'WiFi Password',
      category: 'Personal',
      favorite: true,
      lastUsed: '1 week ago',
      icon: '📝',
    },
  ];

  const filteredItems = vaultItems.filter((item) => {
    const matchesSearch =
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.username?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.email?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterType === 'all' || item.type === filterType;
    return matchesSearch && matchesFilter;
  });

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getStrengthColor = (strength?: string) => {
    switch (strength) {
      case 'weak':
        return 'text-red-400';
      case 'fair':
        return 'text-orange-400';
      case 'good':
        return 'text-yellow-400';
      case 'strong':
        return 'text-green-400';
      default:
        return 'text-gray-400';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'login':
        return Key;
      case 'card':
        return CreditCard;
      case 'note':
        return FileText;
      case 'identity':
        return Globe;
      default:
        return Key;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black bg-opacity-30 backdrop-blur-lg border-b border-white border-opacity-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/dashboard" className="text-blue-400 hover:text-blue-300">
                ← Back
              </Link>
              <h1 className="text-2xl font-bold text-white">My Vault</h1>
            </div>
            <Link
              href="/dashboard/vault/add"
              className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Add Item
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Search and Filters */}
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-white border-opacity-10 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search vault..."
                className="w-full pl-10 pr-4 py-3 bg-slate-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Filter */}
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-3 bg-slate-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Items</option>
              <option value="login">Logins</option>
              <option value="card">Cards</option>
              <option value="note">Notes</option>
              <option value="identity">Identities</option>
            </select>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-4 py-3 bg-slate-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="name">Sort by Name</option>
              <option value="date">Sort by Date</option>
              <option value="usage">Sort by Usage</option>
            </select>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Total Items', value: vaultItems.length, color: 'blue' },
            { label: 'Favorites', value: vaultItems.filter((i) => i.favorite).length, color: 'yellow' },
            { label: 'Weak Passwords', value: vaultItems.filter((i) => i.strength === 'weak').length, color: 'red' },
            { label: 'Strong Passwords', value: vaultItems.filter((i) => i.strength === 'strong').length, color: 'green' },
          ].map((stat, index) => (
            <div
              key={index}
              className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-4 border border-white border-opacity-10"
            >
              <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
              <p className="text-2xl font-bold text-white">{stat.value}</p>
            </div>
          ))}
        </div>

        {/* Vault Items */}
        {filteredItems.length > 0 ? (
          <div className="grid grid-cols-1 gap-4">
            {filteredItems.map((item) => {
              const TypeIcon = getTypeIcon(item.type);
              return (
                <div
                  key={item.id}
                  className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-white border-opacity-10 hover:border-opacity-30 transition-all group"
                >
                  <div className="flex items-center justify-between">
                    {/* Left Side */}
                    <div className="flex items-center gap-4 flex-1">
                      <div className="text-4xl">{item.icon}</div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-white font-semibold text-lg">{item.title}</h3>
                          {item.favorite && (
                            <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                          )}
                          {item.strength && (
                            <span className={`text-xs ${getStrengthColor(item.strength)}`}>
                              {item.strength}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-400">
                          {item.username && <span>👤 {item.username}</span>}
                          {item.email && <span>📧 {item.email}</span>}
                          {item.website && <span>🌐 {item.website}</span>}
                        </div>
                        <div className="flex items-center gap-4 text-xs text-gray-500 mt-1">
                          <span>{item.category}</span>
                          <span>•</span>
                          <span>Last used {item.lastUsed}</span>
                        </div>
                      </div>
                    </div>

                    {/* Right Side - Actions */}
                    <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => copyToClipboard('password', item.id)}
                        className="p-2 bg-blue-500 bg-opacity-20 text-blue-400 rounded-lg hover:bg-opacity-30 transition-colors"
                        title="Copy Password"
                      >
                        {copiedId === item.id ? (
                          <CheckCircle className="w-5 h-5" />
                        ) : (
                          <Copy className="w-5 h-5" />
                        )}
                      </button>
                      <button
                        className="p-2 bg-green-500 bg-opacity-20 text-green-400 rounded-lg hover:bg-opacity-30 transition-colors"
                        title="View"
                      >
                        <Eye className="w-5 h-5" />
                      </button>
                      <Link
                        href={`/dashboard/vault/edit/${item.id}`}
                        className="p-2 bg-purple-500 bg-opacity-20 text-purple-400 rounded-lg hover:bg-opacity-30 transition-colors"
                        title="Edit"
                      >
                        <Edit className="w-5 h-5" />
                      </Link>
                      <button
                        className="p-2 bg-red-500 bg-opacity-20 text-red-400 rounded-lg hover:bg-opacity-30 transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-12 border border-white border-opacity-10 text-center">
            <Lock className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">No items found</h3>
            <p className="text-gray-400 mb-6">
              {searchQuery ? 'Try adjusting your search' : 'Start by adding your first item'}
            </p>
            <Link
              href="/dashboard/vault/add"
              className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all gap-2"
            >
              <Plus className="w-5 h-5" />
              Add First Item
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}