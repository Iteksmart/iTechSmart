'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Shield, Upload, FileCheck, X, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { proofsAPI } from '@/lib/api';
import toast from 'react-hot-toast';

export default function CreateProofPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [proofLink, setProofLink] = useState('');
  const [isPublic, setIsPublic] = useState(true);
  const [isDownloadable, setIsDownloadable] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxFiles: 1,
    maxSize: 100 * 1024 * 1024, // 100MB
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      toast.error('Please select a file');
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('proof_type', 'file');
      formData.append('is_public', String(isPublic));
      formData.append('is_downloadable', String(isDownloadable));

      const response = await proofsAPI.create(formData);
      const proof = response.data;

      setProofLink(proof.verification_url);
      toast.success('Proof created successfully!');
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to create proof';
      toast.error(message);
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setProofLink('');
    setIsPublic(true);
    setIsDownloadable(false);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/dashboard" className="flex items-center space-x-2">
              <Shield className="h-8 w-8 text-primary-600" />
              <span className="text-xl font-bold gradient-text">ProofLink.AI</span>
            </Link>
            
            <div className="flex items-center space-x-6">
              <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
                Dashboard
              </Link>
              <Link href="/dashboard/proofs" className="text-gray-600 hover:text-gray-900">
                My Proofs
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {!proofLink ? (
          <>
            {/* Header */}
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Proof</h1>
              <p className="text-gray-600">
                Upload a file to create a cryptographic proof of its authenticity
              </p>
            </div>

            {/* Upload Form */}
            <div className="card p-8">
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* File Upload */}
                <div>
                  <label className="label block mb-2">Upload File</label>
                  
                  {!file ? (
                    <div
                      {...getRootProps()}
                      className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition ${
                        isDragActive
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-300 hover:border-primary-400'
                      }`}
                    >
                      <input {...getInputProps()} />
                      <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-lg font-medium text-gray-900 mb-2">
                        {isDragActive ? 'Drop file here' : 'Drag & drop file here'}
                      </p>
                      <p className="text-sm text-gray-600 mb-4">or click to browse</p>
                      <p className="text-xs text-gray-500">
                        Maximum file size: 100MB
                      </p>
                    </div>
                  ) : (
                    <div className="border-2 border-primary-200 bg-primary-50 rounded-lg p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="bg-primary-100 p-3 rounded-lg">
                            <FileCheck className="h-6 w-6 text-primary-600" />
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">{file.name}</p>
                            <p className="text-sm text-gray-600">
                              {(file.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => setFile(null)}
                          className="text-gray-400 hover:text-gray-600"
                        >
                          <X className="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Options */}
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      id="isPublic"
                      checked={isPublic}
                      onChange={(e) => setIsPublic(e.target.checked)}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <label htmlFor="isPublic" className="text-sm text-gray-700">
                      Make proof publicly verifiable (anyone can verify with the link)
                    </label>
                  </div>

                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      id="isDownloadable"
                      checked={isDownloadable}
                      onChange={(e) => setIsDownloadable(e.target.checked)}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <label htmlFor="isDownloadable" className="text-sm text-gray-700">
                      Allow file download from verification page
                    </label>
                  </div>
                </div>

                {/* Info Box */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-blue-900 mb-1">
                        How it works
                      </h4>
                      <p className="text-sm text-blue-800">
                        We create a cryptographic hash (SHA-256) of your file and store it securely.
                        The original file is encrypted and can only be accessed by you.
                        Anyone with the proof link can verify the file's authenticity.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={!file || uploading}
                  className="btn btn-primary w-full"
                >
                  {uploading ? (
                    <span className="flex items-center justify-center">
                      <Loader className="animate-spin -ml-1 mr-3 h-5 w-5" />
                      Creating proof...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center">
                      <FileCheck className="mr-2 h-5 w-5" />
                      Create Proof
                    </span>
                  )}
                </button>
              </form>
            </div>
          </>
        ) : (
          <>
            {/* Success State */}
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Proof Created!</h1>
              <p className="text-gray-600">
                Your file has been verified and a proof has been generated
              </p>
            </div>

            {/* Proof Details */}
            <div className="card p-8 space-y-6">
              {/* File Info */}
              <div>
                <label className="label block mb-2">File</label>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="font-medium text-gray-900">{file?.name}</p>
                  <p className="text-sm text-gray-600">
                    {file && (file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>

              {/* Verification Link */}
              <div>
                <label className="label block mb-2">Verification Link</label>
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={proofLink}
                    readOnly
                    className="input flex-1"
                  />
                  <button
                    onClick={() => copyToClipboard(proofLink)}
                    className="btn btn-outline"
                  >
                    Copy
                  </button>
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Share this link with anyone to verify your file's authenticity
                </p>
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-4">
                <Link href={proofLink} target="_blank" className="btn btn-primary flex-1">
                  View Proof
                </Link>
                <button onClick={handleReset} className="btn btn-outline flex-1">
                  Create Another
                </button>
              </div>

              {/* Next Steps */}
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-purple-900 mb-2">Next Steps</h4>
                <ul className="text-sm text-purple-800 space-y-1">
                  <li>• Share the verification link with others</li>
                  <li>• Download the QR code for easy sharing</li>
                  <li>• View all your proofs in the dashboard</li>
                  <li>• Set up API access for automated verification</li>
                </ul>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}