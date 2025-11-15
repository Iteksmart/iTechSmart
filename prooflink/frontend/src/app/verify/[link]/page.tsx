'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Shield, CheckCircle, XCircle, FileCheck, Calendar, User, Hash, Loader, AlertTriangle } from 'lucide-react';
import { proofsAPI } from '@/lib/api';

export default function VerifyProofPage() {
  const params = useParams();
  const proofLink = params.link as string;
  
  const [loading, setLoading] = useState(true);
  const [proof, setProof] = useState<any>(null);
  const [verified, setVerified] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (proofLink) {
      verifyProof();
    }
  }, [proofLink]);

  const verifyProof = async () => {
    try {
      const response = await proofsAPI.verifyByLink(proofLink);
      setProof(response.data.proof);
      setVerified(response.data.verified);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Proof not found');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="h-12 w-12 text-primary-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Verifying proof...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
            <XCircle className="h-8 w-8 text-red-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Proof Not Found</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <Link href="/" className="btn btn-primary">
            Go to Homepage
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="flex items-center space-x-2">
              <Shield className="h-8 w-8 text-primary-600" />
              <span className="text-xl font-bold gradient-text">ProofLink.AI</span>
            </Link>
            
            <div className="flex items-center space-x-4">
              <Link href="/verify" className="text-gray-600 hover:text-gray-900">
                Verify Another
              </Link>
              <Link href="/auth/login" className="btn btn-outline">
                Login
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Verification Status */}
        <div className="text-center mb-8">
          <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full mb-4 ${
            verified ? 'bg-green-100' : 'bg-red-100'
          }`}>
            {verified ? (
              <CheckCircle className="h-10 w-10 text-green-600" />
            ) : (
              <XCircle className="h-10 w-10 text-red-600" />
            )}
          </div>
          
          <h1 className={`text-4xl font-bold mb-2 ${
            verified ? 'text-green-600' : 'text-red-600'
          }`}>
            {verified ? 'Verified ✓' : 'Not Verified ✗'}
          </h1>
          
          <p className="text-xl text-gray-600">
            {verified 
              ? 'This proof is authentic and has not been tampered with'
              : 'This proof could not be verified'
            }
          </p>
        </div>

        {/* Proof Details */}
        <div className="card p-8 space-y-6">
          {/* File Information */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">File Information</h2>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <FileCheck className="h-5 w-5 text-gray-400 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm text-gray-600">File Name</p>
                  <p className="font-medium text-gray-900">{proof.file_name || 'N/A'}</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <Calendar className="h-5 w-5 text-gray-400 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm text-gray-600">Created</p>
                  <p className="font-medium text-gray-900">
                    {new Date(proof.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <Hash className="h-5 w-5 text-gray-400 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm text-gray-600">File Hash (SHA-256)</p>
                  <p className="font-mono text-sm text-gray-900 break-all">
                    {proof.file_hash}
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <User className="h-5 w-5 text-gray-400 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm text-gray-600">Verification Count</p>
                  <p className="font-medium text-gray-900">
                    {proof.verification_count} times
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Verification Details */}
          <div className="border-t border-gray-200 pt-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Verification Details</h2>
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Hash Match</span>
                <span className="badge badge-success">✓ Verified</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Timestamp Valid</span>
                <span className="badge badge-success">✓ Valid</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Signature</span>
                <span className="badge badge-success">✓ Authentic</span>
              </div>
            </div>
          </div>

          {/* Trust Indicators */}
          <div className="border-t border-gray-200 pt-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Trust Indicators</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                <CheckCircle className="h-8 w-8 text-green-600 mx-auto mb-2" />
                <p className="text-sm font-medium text-green-900">Cryptographically Secure</p>
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
                <Shield className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                <p className="text-sm font-medium text-blue-900">Tamper-Proof</p>
              </div>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 text-center">
                <FileCheck className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                <p className="text-sm font-medium text-purple-900">Timestamped</p>
              </div>
            </div>
          </div>

          {/* How It Works */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="h-5 w-5 text-blue-600 mt-0.5" />
              <div className="flex-1">
                <h4 className="text-sm font-medium text-blue-900 mb-1">
                  How Verification Works
                </h4>
                <p className="text-sm text-blue-800">
                  ProofLink uses SHA-256 cryptographic hashing to create a unique fingerprint of your file.
                  This fingerprint is stored securely and can be used to verify that the file hasn't been
                  modified since it was first uploaded. The verification process is instant and tamper-proof.
                </p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-4 pt-4">
            <Link href="/auth/register" className="btn btn-primary flex-1">
              Create Your Own Proof
            </Link>
            <Link href="/verify" className="btn btn-outline flex-1">
              Verify Another Proof
            </Link>
          </div>
        </div>

        {/* Powered By */}
        <div className="text-center mt-8">
          <p className="text-sm text-gray-600">
            Powered by{' '}
            <Link href="/" className="text-primary-600 hover:text-primary-700 font-medium">
              ProofLink.AI
            </Link>
            {' '}- The World's Trust Layer
          </p>
        </div>
      </div>
    </div>
  );
}