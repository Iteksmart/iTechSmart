import React, { useState, useEffect } from 'react';
import { Database, Plus, CheckCircle, XCircle, Clock, RefreshCw, Settings, Trash2 } from 'lucide-react';

interface DataSource {
  id: string;
  name: string;
  type: string;
  host: string;
  database: string;
  status: string;
  last_sync: string;
  tables_count?: number;
  endpoints_count?: number;
  sheets_count?: number;
}

const DataSources: React.FC = () => {
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    fetchDataSources();
  }, []);

  const fetchDataSources = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/datasources');
      const data = await response.json();
      setDataSources(data.datasources || []);
    } catch (error) {
      console.error('Error fetching data sources:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'bg-green-100 text-green-800';
      case 'error': return 'bg-red-100 text-red-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type: string) => {
    const icons: { [key: string]: string } = {
      postgresql: '🐘',
      mysql: '🐬',
      mongodb: '🍃',
      api: '🔌',
      google_sheets: '📊',
      excel: '📈',
      csv: '📄',
    };
    return icons[type] || '💾';
  };

  const connectedCount = dataSources.filter(ds => ds.status === 'connected').length;
  const errorCount = dataSources.filter(ds => ds.status === 'error').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Database className="w-8 h-8 text-blue-600" />
            Data Sources
          </h1>
          <p className="text-gray-600 mt-2">Connect and manage your data sources</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Data Source
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Sources</p>
              <p className="text-3xl font-bold text-gray-900">{dataSources.length}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Database className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Connected</p>
              <p className="text-3xl font-bold text-green-600">{connectedCount}</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Errors</p>
              <p className="text-3xl font-bold text-red-600">{errorCount}</p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <XCircle className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Sync Rate</p>
              <p className="text-3xl font-bold text-blue-600">98%</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <RefreshCw className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Data Sources Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading data sources...</p>
          </div>
        ) : dataSources.length === 0 ? (
          <div className="col-span-full p-12 text-center">
            <Database className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600 mb-4">No data sources configured</p>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Add Your First Data Source
            </button>
          </div>
        ) : (
          dataSources.map((source) => (
            <div
              key={source.id}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="text-3xl">{getTypeIcon(source.type)}</div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{source.name}</h3>
                    <p className="text-sm text-gray-600 capitalize">{source.type.replace('_', ' ')}</p>
                  </div>
                </div>
                {getStatusIcon(source.status)}
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Host:</span>
                  <span className="text-gray-900 font-mono text-xs">{source.host}</span>
                </div>
                {source.database && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Database:</span>
                    <span className="text-gray-900 font-mono text-xs">{source.database}</span>
                  </div>
                )}
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Last Sync:</span>
                  <span className="text-gray-900 text-xs">{source.last_sync}</span>
                </div>
                {source.tables_count !== undefined && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Tables:</span>
                    <span className="text-gray-900 font-semibold">{source.tables_count}</span>
                  </div>
                )}
                {source.endpoints_count !== undefined && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Endpoints:</span>
                    <span className="text-gray-900 font-semibold">{source.endpoints_count}</span>
                  </div>
                )}
                {source.sheets_count !== undefined && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Sheets:</span>
                    <span className="text-gray-900 font-semibold">{source.sheets_count}</span>
                  </div>
                )}
              </div>

              <div className="pt-4 border-t border-gray-200">
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(source.status)}`}>
                  {source.status.toUpperCase()}
                </span>
              </div>

              <div className="flex gap-2 mt-4">
                <button className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2 text-sm">
                  <RefreshCw className="w-4 h-4" />
                  Sync
                </button>
                <button className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
                  <Settings className="w-4 h-4" />
                </button>
                <button className="px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Add Data Source Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Add Data Source</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
              {['PostgreSQL', 'MySQL', 'MongoDB', 'REST API', 'Google Sheets', 'Excel'].map((type) => (
                <button
                  key={type}
                  className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-600 hover:bg-blue-50 transition-colors"
                >
                  <div className="text-3xl mb-2">{getTypeIcon(type.toLowerCase().replace(' ', '_'))}</div>
                  <p className="text-sm font-medium text-gray-900">{type}</p>
                </button>
              ))}
            </div>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataSources;