'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Shield, Plus, FileCheck, TrendingUp, Users, Clock, ArrowRight } from 'lucide-react';
import { usersAPI, proofsAPI } from '@/lib/api';
import toast from 'react-hot-toast';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [recentProofs, setRecentProofs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/auth/login');
      return;
    }

    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [profileRes, statsRes, proofsRes] = await Promise.all([
        usersAPI.getProfile(),
        usersAPI.getStats(),
        proofsAPI.getMyProofs(1, 5),
      ]);

      setUser(profileRes.data);
      setStats(statsRes.data);
      setRecentProofs(proofsRes.data.proofs);
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    router.push('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <Link href="/dashboard" className="flex items-center space-x-2">
                <Shield className="h-8 w-8 text-primary-600" />
                <span className="text-xl font-bold gradient-text">ProofLink.AI</span>
              </Link>
              
              <div className="hidden md:flex items-center space-x-6">
                <Link href="/dashboard" className="text-gray-900 font-medium">
                  Dashboard
                </Link>
                <Link href="/dashboard/proofs" className="text-gray-600 hover:text-gray-900">
                  My Proofs
                </Link>
                <Link href="/dashboard/create" className="text-gray-600 hover:text-gray-900">
                  Create Proof
                </Link>
                <Link href="/verify" className="text-gray-600 hover:text-gray-900">
                  Verify
                </Link>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Link href="/dashboard/settings" className="text-gray-600 hover:text-gray-900">
                Settings
              </Link>
              <button onClick={handleLogout} className="btn btn-outline">
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.full_name || user?.email}!
          </h1>
          <p className="text-gray-600">
            Here's what's happening with your proofs today.
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-primary-100 p-3 rounded-lg">
                <FileCheck className="h-6 w-6 text-primary-600" />
              </div>
              <span className="text-sm text-gray-500">Total</span>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">
              {stats?.total_proofs || 0}
            </div>
            <p className="text-sm text-gray-600">Proofs Created</p>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-green-100 p-3 rounded-lg">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <span className="text-sm text-gray-500">This Month</span>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">
              {stats?.proofs_this_month || 0}
            </div>
            <p className="text-sm text-gray-600">New Proofs</p>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-blue-100 p-3 rounded-lg">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
              <span className="text-sm text-gray-500">Total</span>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">
              {stats?.total_verifications || 0}
            </div>
            <p className="text-sm text-gray-600">Verifications</p>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-purple-100 p-3 rounded-lg">
                <Clock className="h-6 w-6 text-purple-600" />
              </div>
              <span className="text-sm text-gray-500">Storage</span>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">
              {stats?.storage_used_mb || 0}
            </div>
            <p className="text-sm text-gray-600">MB Used</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Link href="/dashboard/create" className="card p-6 hover:shadow-lg transition group">
            <div className="flex items-center space-x-4">
              <div className="bg-primary-100 p-4 rounded-lg group-hover:bg-primary-200 transition">
                <Plus className="h-8 w-8 text-primary-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-1">Create Proof</h3>
                <p className="text-sm text-gray-600">Upload and verify a new file</p>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-primary-600 transition" />
            </div>
          </Link>

          <Link href="/verify" className="card p-6 hover:shadow-lg transition group">
            <div className="flex items-center space-x-4">
              <div className="bg-green-100 p-4 rounded-lg group-hover:bg-green-200 transition">
                <FileCheck className="h-8 w-8 text-green-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-1">Verify Proof</h3>
                <p className="text-sm text-gray-600">Check a proof's authenticity</p>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-green-600 transition" />
            </div>
          </Link>

          <Link href="/dashboard/api-keys" className="card p-6 hover:shadow-lg transition group">
            <div className="flex items-center space-x-4">
              <div className="bg-blue-100 p-4 rounded-lg group-hover:bg-blue-200 transition">
                <Shield className="h-8 w-8 text-blue-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-1">API Keys</h3>
                <p className="text-sm text-gray-600">Manage your API access</p>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-blue-600 transition" />
            </div>
          </Link>
        </div>

        {/* Recent Proofs */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Recent Proofs</h2>
            <Link href="/dashboard/proofs" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View all
            </Link>
          </div>

          {recentProofs.length === 0 ? (
            <div className="text-center py-12">
              <FileCheck className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No proofs yet</h3>
              <p className="text-gray-600 mb-4">Create your first proof to get started</p>
              <Link href="/dashboard/create" className="btn btn-primary">
                Create Proof
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {recentProofs.map((proof) => (
                <div key={proof.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
                  <div className="flex items-center space-x-4">
                    <div className="bg-primary-100 p-3 rounded-lg">
                      <FileCheck className="h-6 w-6 text-primary-600" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{proof.file_name || 'Untitled'}</h4>
                      <p className="text-sm text-gray-600">
                        Created {new Date(proof.timestamp).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="badge badge-success">Verified</span>
                    <Link href={`/dashboard/proofs/${proof.id}`} className="text-primary-600 hover:text-primary-700">
                      View
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Subscription Status */}
        {stats?.role === 'free' && (
          <div className="mt-8 card p-6 bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-primary-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">Upgrade to Premium</h3>
                <p className="text-gray-600 mb-4">
                  Get unlimited proofs, AI verification, and more for just $1/month
                </p>
                <Link href="/dashboard/billing" className="btn btn-primary">
                  Upgrade Now
                </Link>
              </div>
              <div className="hidden md:block">
                <Shield className="h-24 w-24 text-primary-300" />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}