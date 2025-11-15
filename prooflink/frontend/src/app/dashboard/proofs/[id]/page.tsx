'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  ArrowLeft,
  FileText,
  Hash,
  Calendar,
  Eye,
  Download,
  Share2,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  ExternalLink,
  Copy,
  Shield,
  Activity,
} from 'lucide-react';
import { useState } from 'react';

interface ProofDetails {
  id: string;
  filename: string;
  file_hash: string;
  proof_link: string;
  verification_count: number;
  created_at: string;
  expires_at: string | null;
  is_active: boolean;
  file_size: number;
  mime_type: string;
  metadata: any;
  verifications: Array<{
    id: string;
    verified_at: string;
    ip_address: string;
    user_agent: string;
    is_valid: boolean;
  }>;
}

export default function ProofDetailsPage() {
  const params = useParams();
  const proofId = params.id as string;
  const [copied, setCopied] = useState(false);

  const { data: proof, isLoading } = useQuery({
    queryKey: ['proof', proofId],
    queryFn: async () => {
      const response = await api.get(`/proofs/${proofId}`);
      return response.data as ProofDetails;
    },
  });

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading proof details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!proof) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Proof Not Found</h2>
            <p className="text-gray-600 mb-6">The proof you're looking for doesn't exist.</p>
            <Link
              href="/dashboard/proofs"
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Proofs
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Link
            href="/dashboard/proofs"
            className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Proofs
          </Link>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">{proof.filename}</h1>
              <div className="flex items-center gap-4">
                {proof.is_active ? (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                    <CheckCircle className="w-4 h-4 mr-1" />
                    Active
                  </span>
                ) : (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
                    <XCircle className="w-4 h-4 mr-1" />
                    Expired
                  </span>
                )}
                <span className="text-gray-600">
                  {formatFileSize(proof.file_size)} • {proof.mime_type}
                </span>
              </div>
            </div>
            <div className="flex gap-3">
              <button className="px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 flex items-center gap-2">
                <Download className="w-4 h-4" />
                Download
              </button>
              <button className="px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 flex items-center gap-2">
                <Share2 className="w-4 h-4" />
                Share
              </button>
              <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2">
                <Trash2 className="w-4 h-4" />
                Delete
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Proof Link */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <ExternalLink className="w-5 h-5 mr-2 text-blue-600" />
                Proof Link
              </h2>
              <div className="flex items-center gap-3">
                <input
                  type="text"
                  value={proof.proof_link}
                  readOnly
                  className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg font-mono text-sm"
                />
                <button
                  onClick={() => copyToClipboard(proof.proof_link)}
                  className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  {copied ? (
                    <>
                      <CheckCircle className="w-4 h-4" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      Copy
                    </>
                  )}
                </button>
              </div>
              <p className="mt-3 text-sm text-gray-600">
                Share this link to allow anyone to verify the authenticity of your file.
              </p>
            </div>

            {/* File Hash */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Hash className="w-5 h-5 mr-2 text-purple-600" />
                Cryptographic Hash (SHA-256)
              </h2>
              <div className="flex items-center gap-3">
                <code className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg font-mono text-sm break-all">
                  {proof.file_hash}
                </code>
                <button
                  onClick={() => copyToClipboard(proof.file_hash)}
                  className="px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  <Copy className="w-4 h-4" />
                </button>
              </div>
              <p className="mt-3 text-sm text-gray-600">
                This unique hash serves as the digital fingerprint of your file.
              </p>
            </div>

            {/* Verification History */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Activity className="w-5 h-5 mr-2 text-green-600" />
                Verification History
              </h2>
              {proof.verifications && proof.verifications.length > 0 ? (
                <div className="space-y-3">
                  {proof.verifications.slice(0, 10).map((verification) => (
                    <div
                      key={verification.id}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        {verification.is_valid ? (
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        ) : (
                          <XCircle className="w-5 h-5 text-red-600" />
                        )}
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {verification.is_valid ? 'Valid Verification' : 'Invalid Verification'}
                          </p>
                          <p className="text-xs text-gray-600">
                            {formatDate(verification.verified_at)}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-gray-600">{verification.ip_address}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Eye className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-600">No verifications yet</p>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Stats */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Statistics</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 flex items-center">
                    <Eye className="w-4 h-4 mr-2" />
                    Verifications
                  </span>
                  <span className="font-semibold text-gray-900">{proof.verification_count}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 flex items-center">
                    <Calendar className="w-4 h-4 mr-2" />
                    Created
                  </span>
                  <span className="text-sm text-gray-900">
                    {new Date(proof.created_at).toLocaleDateString()}
                  </span>
                </div>
                {proof.expires_at && (
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 flex items-center">
                      <Clock className="w-4 h-4 mr-2" />
                      Expires
                    </span>
                    <span className="text-sm text-gray-900">
                      {new Date(proof.expires_at).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Security Info */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-blue-600 rounded-lg">
                  <Shield className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900">Cryptographically Secured</h3>
              </div>
              <p className="text-sm text-gray-700 leading-relaxed">
                This proof is secured using SHA-256 cryptographic hashing, making it mathematically
                impossible to forge or tamper with the original file.
              </p>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
              <div className="space-y-2">
                <a
                  href={proof.proof_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
                >
                  <ExternalLink className="w-4 h-4" />
                  Open Proof Link
                </a>
                <button className="w-full px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 flex items-center justify-center gap-2">
                  <Download className="w-4 h-4" />
                  Download File
                </button>
                <button className="w-full px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 flex items-center justify-center gap-2">
                  <Share2 className="w-4 h-4" />
                  Share Proof
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}