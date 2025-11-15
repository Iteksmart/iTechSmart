'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Download, FileText, Image, File } from 'lucide-react';

interface ReportExportProps {
  params: { id: string };
}

export default function ReportExportPage({ params }: ReportExportProps) {
  const [format, setFormat] = useState('pdf');
  const [includeCharts, setIncludeCharts] = useState(true);
  const [includeData, setIncludeData] = useState(true);

  const handleExport = () => {
    console.log('Exporting report:', { format, includeCharts, includeData });
    alert(`Exporting report as ${format.toUpperCase()}...`);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href={`/dashboard/reports/${params.id}`} className="p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Export Report</h1>
            <p className="mt-1 text-sm text-gray-500">Choose your export format and options</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Export Format</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => setFormat('pdf')}
            className={`p-6 border-2 rounded-lg transition-all ${
              format === 'pdf'
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <FileText className={`w-8 h-8 mx-auto mb-3 ${format === 'pdf' ? 'text-blue-600' : 'text-gray-400'}`} />
            <p className="font-medium text-gray-900">PDF Document</p>
            <p className="text-xs text-gray-500 mt-1">Professional formatted report</p>
          </button>

          <button
            onClick={() => setFormat('docx')}
            className={`p-6 border-2 rounded-lg transition-all ${
              format === 'docx'
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <File className={`w-8 h-8 mx-auto mb-3 ${format === 'docx' ? 'text-blue-600' : 'text-gray-400'}`} />
            <p className="font-medium text-gray-900">Word Document</p>
            <p className="text-xs text-gray-500 mt-1">Editable DOCX format</p>
          </button>

          <button
            onClick={() => setFormat('html')}
            className={`p-6 border-2 rounded-lg transition-all ${
              format === 'html'
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <Image className={`w-8 h-8 mx-auto mb-3 ${format === 'html' ? 'text-blue-600' : 'text-gray-400'}`} />
            <p className="font-medium text-gray-900">Web Page</p>
            <p className="text-xs text-gray-500 mt-1">Interactive HTML format</p>
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Export Options</h2>
        <div className="space-y-4">
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={includeCharts}
              onChange={(e) => setIncludeCharts(e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <div>
              <p className="text-sm font-medium text-gray-900">Include Charts & Visualizations</p>
              <p className="text-xs text-gray-500">Add data visualizations and graphs</p>
            </div>
          </label>

          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={includeData}
              onChange={(e) => setIncludeData(e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <div>
              <p className="text-sm font-medium text-gray-900">Include Raw Data Tables</p>
              <p className="text-xs text-gray-500">Add detailed data tables and metrics</p>
            </div>
          </label>
        </div>
      </div>

      <div className="flex items-center justify-end space-x-4">
        <Link
          href={`/dashboard/reports/${params.id}`}
          className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Cancel
        </Link>
        <button
          onClick={handleExport}
          className="inline-flex items-center px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Download className="w-4 h-4 mr-2" />
          Export Report
        </button>
      </div>
    </div>
  );
}