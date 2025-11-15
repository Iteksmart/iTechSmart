import { useState } from 'react';
import { BookOpen, Plus, Trash2, Upload, FileText, Search } from 'lucide-react';

interface Document {
  id: number;
  title: string;
  document_type: string;
  file_size: number;
  created_at: string;
}

interface KnowledgeBase {
  id: number;
  name: string;
  description: string;
  document_count: number;
  is_active: boolean;
}

export default function Knowledge() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([
    {
      id: 1,
      name: 'Technical Documentation',
      description: 'API docs, technical specifications, and guides',
      document_count: 24,
      is_active: true
    },
    {
      id: 2,
      name: 'Company Policies',
      description: 'HR policies, procedures, and guidelines',
      document_count: 15,
      is_active: true
    }
  ]);

  const [documents, setDocuments] = useState<Document[]>([
    {
      id: 1,
      title: 'API Documentation v2.0',
      document_type: 'pdf',
      file_size: 2048000,
      created_at: '2024-01-15T10:30:00Z'
    },
    {
      id: 2,
      title: 'User Guide',
      document_type: 'docx',
      file_size: 1024000,
      created_at: '2024-01-14T14:20:00Z'
    }
  ]);

  const [selectedKB, setSelectedKB] = useState<number>(1);
  const [searchQuery, setSearchQuery] = useState('');

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Knowledge Base</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage documents and knowledge bases for AI context
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex space-x-3">
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
            <Plus className="w-4 h-4 mr-2" />
            New Knowledge Base
          </button>
          <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700">
            <Upload className="w-4 h-4 mr-2" />
            Upload Document
          </button>
        </div>
      </div>

      {/* Knowledge Bases */}
      <div className="mt-8">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Knowledge Bases</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {knowledgeBases.map((kb) => (
            <div
              key={kb.id}
              onClick={() => setSelectedKB(kb.id)}
              className={`bg-white shadow rounded-lg p-6 cursor-pointer hover:shadow-lg transition-shadow ${
                selectedKB === kb.id ? 'ring-2 ring-indigo-500' : ''
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <BookOpen className="w-8 h-8 text-indigo-600" />
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  kb.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {kb.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">{kb.name}</h3>
              <p className="text-sm text-gray-600 mb-3">{kb.description}</p>
              <div className="flex items-center text-sm text-gray-500">
                <FileText className="w-4 h-4 mr-1" />
                {kb.document_count} documents
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Search */}
      <div className="mt-8">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search documents..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
          <button className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700">
            Search
          </button>
        </div>
      </div>

      {/* Documents */}
      <div className="mt-8 bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Documents</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <FileText className="w-5 h-5 text-gray-400 mr-2" />
                      <span className="text-sm font-medium text-gray-900">{doc.title}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                      {doc.document_type.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatFileSize(doc.file_size)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <button className="text-red-600 hover:text-red-800">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}