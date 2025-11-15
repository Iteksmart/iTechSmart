'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import {
  Upload,
  FileText,
  CheckCircle,
  XCircle,
  Loader2,
  Download,
  Trash2,
  Copy,
  AlertCircle,
} from 'lucide-react';

interface FileWithStatus {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  proofLink?: string;
  error?: string;
}

export default function BatchProofsPage() {
  const [files, setFiles] = useState<FileWithStatus[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map((file) => ({
      file,
      status: 'pending' as const,
      progress: 0,
    }));
    setFiles((prev) => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: true,
  });

  const createBatchProofs = useMutation({
    mutationFn: async (filesToUpload: FileWithStatus[]) => {
      setIsProcessing(true);
      const results = [];

      for (let i = 0; i < filesToUpload.length; i++) {
        const fileWithStatus = filesToUpload[i];
        
        // Update status to uploading
        setFiles((prev) =>
          prev.map((f) =>
            f.file === fileWithStatus.file
              ? { ...f, status: 'uploading' as const, progress: 0 }
              : f
          )
        );

        try {
          const formData = new FormData();
          formData.append('file', fileWithStatus.file);

          // Simulate progress
          const progressInterval = setInterval(() => {
            setFiles((prev) =>
              prev.map((f) =>
                f.file === fileWithStatus.file && f.progress < 90
                  ? { ...f, progress: f.progress + 10 }
                  : f
              )
            );
          }, 200);

          const response = await api.post('/proofs', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });

          clearInterval(progressInterval);

          // Update to success
          setFiles((prev) =>
            prev.map((f) =>
              f.file === fileWithStatus.file
                ? {
                    ...f,
                    status: 'success' as const,
                    progress: 100,
                    proofLink: response.data.proof_link,
                  }
                : f
            )
          );

          results.push({ success: true, data: response.data });
        } catch (error: any) {
          // Update to error
          setFiles((prev) =>
            prev.map((f) =>
              f.file === fileWithStatus.file
                ? {
                    ...f,
                    status: 'error' as const,
                    progress: 0,
                    error: error.message || 'Upload failed',
                  }
                : f
            )
          );

          results.push({ success: false, error: error.message });
        }
      }

      setIsProcessing(false);
      return results;
    },
  });

  const handleUploadAll = () => {
    const pendingFiles = files.filter((f) => f.status === 'pending');
    if (pendingFiles.length > 0) {
      createBatchProofs.mutate(pendingFiles);
    }
  };

  const handleRemoveFile = (file: File) => {
    setFiles((prev) => prev.filter((f) => f.file !== file));
  };

  const handleClearAll = () => {
    setFiles([]);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const exportResults = () => {
    const successfulProofs = files.filter((f) => f.status === 'success');
    const csv = [
      'Filename,Proof Link,Status',
      ...successfulProofs.map(
        (f) => `"${f.file.name}","${f.proofLink}","Success"`
      ),
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `prooflink-batch-${Date.now()}.csv`;
    a.click();
  };

  const stats = {
    total: files.length,
    pending: files.filter((f) => f.status === 'pending').length,
    uploading: files.filter((f) => f.status === 'uploading').length,
    success: files.filter((f) => f.status === 'success').length,
    error: files.filter((f) => f.status === 'error').length,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Batch Upload</h1>
          <p className="text-gray-600">Upload multiple files at once to create proofs</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
            <p className="text-sm text-gray-600 mb-1">Total</p>
            <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
            <p className="text-sm text-gray-600 mb-1">Pending</p>
            <p className="text-2xl font-bold text-orange-600">{stats.pending}</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
            <p className="text-sm text-gray-600 mb-1">Uploading</p>
            <p className="text-2xl font-bold text-blue-600">{stats.uploading}</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
            <p className="text-sm text-gray-600 mb-1">Success</p>
            <p className="text-2xl font-bold text-green-600">{stats.success}</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
            <p className="text-sm text-gray-600 mb-1">Failed</p>
            <p className="text-2xl font-bold text-red-600">{stats.error}</p>
          </div>
        </div>

        {/* Upload Area */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 mb-6">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            {isDragActive ? (
              <p className="text-lg font-medium text-blue-600">Drop files here...</p>
            ) : (
              <>
                <p className="text-lg font-medium text-gray-900 mb-2">
                  Drag & drop files here, or click to select
                </p>
                <p className="text-sm text-gray-600">
                  Upload multiple files at once (up to 100 files)
                </p>
              </>
            )}
          </div>
        </div>

        {/* Actions */}
        {files.length > 0 && (
          <div className="flex gap-3 mb-6">
            <button
              onClick={handleUploadAll}
              disabled={isProcessing || stats.pending === 0}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5" />
                  Upload All ({stats.pending})
                </>
              )}
            </button>
            {stats.success > 0 && (
              <button
                onClick={exportResults}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
              >
                <Download className="w-5 h-5" />
                Export Results
              </button>
            )}
            <button
              onClick={handleClearAll}
              disabled={isProcessing}
              className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 flex items-center gap-2"
            >
              <Trash2 className="w-5 h-5" />
              Clear All
            </button>
          </div>
        )}

        {/* Files List */}
        {files.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="divide-y divide-gray-200">
              {files.map((fileWithStatus, index) => (
                <div key={index} className="p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3 flex-1">
                      <FileText className="w-5 h-5 text-gray-400" />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">
                          {fileWithStatus.file.name}
                        </p>
                        <p className="text-sm text-gray-600">
                          {(fileWithStatus.file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>

                    {/* Status Icon */}
                    <div className="flex items-center gap-3">
                      {fileWithStatus.status === 'pending' && (
                        <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-medium">
                          Pending
                        </span>
                      )}
                      {fileWithStatus.status === 'uploading' && (
                        <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                      )}
                      {fileWithStatus.status === 'success' && (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      )}
                      {fileWithStatus.status === 'error' && (
                        <XCircle className="w-5 h-5 text-red-600" />
                      )}
                      <button
                        onClick={() => handleRemoveFile(fileWithStatus.file)}
                        disabled={fileWithStatus.status === 'uploading'}
                        className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  {fileWithStatus.status === 'uploading' && (
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${fileWithStatus.progress}%` }}
                      />
                    </div>
                  )}

                  {/* Proof Link */}
                  {fileWithStatus.status === 'success' && fileWithStatus.proofLink && (
                    <div className="flex items-center gap-2 mt-2">
                      <input
                        type="text"
                        value={fileWithStatus.proofLink}
                        readOnly
                        className="flex-1 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm font-mono"
                      />
                      <button
                        onClick={() => copyToClipboard(fileWithStatus.proofLink!)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                  )}

                  {/* Error Message */}
                  {fileWithStatus.status === 'error' && fileWithStatus.error && (
                    <div className="flex items-center gap-2 mt-2 text-red-600 text-sm">
                      <AlertCircle className="w-4 h-4" />
                      {fileWithStatus.error}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {files.length === 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No files uploaded yet</h3>
            <p className="text-gray-600">
              Drag and drop files above or click to select files to get started
            </p>
          </div>
        )}
      </div>
    </div>
  );
}