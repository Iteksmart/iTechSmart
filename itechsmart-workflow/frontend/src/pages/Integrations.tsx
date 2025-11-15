import { useState, useEffect } from 'react';
import { Plus, Search, Plug, CheckCircle, XCircle, Edit, Trash2 } from 'lucide-react';
import axios from 'axios';

interface Integration {
  id: number;
  name: string;
  type: string;
  description: string;
  is_active: boolean;
  last_used_at: string | null;
  usage_count: number;
  created_at: string;
}

const Integrations = () => {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchIntegrations();
  }, []);

  const fetchIntegrations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/integrations', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setIntegrations(response.data);
    } catch (error) {
      console.error('Failed to fetch integrations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteIntegration = async (integrationId: number) => {
    if (!confirm('Are you sure you want to delete this integration?')) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`/api/integrations/${integrationId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchIntegrations();
    } catch (error) {
      console.error('Failed to delete integration:', error);
      alert('Failed to delete integration');
    }
  };

  const filteredIntegrations = integrations.filter(integration =>
    integration.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    integration.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const integrationTypes = [
    { type: 'slack', name: 'Slack', icon: '💬', color: 'bg-purple-100 text-purple-800' },
    { type: 'email', name: 'Email', icon: '📧', color: 'bg-blue-100 text-blue-800' },
    { type: 'http', name: 'HTTP/REST', icon: '🌐', color: 'bg-green-100 text-green-800' },
    { type: 'database', name: 'Database', icon: '🗄️', color: 'bg-yellow-100 text-yellow-800' },
    { type: 'aws', name: 'AWS', icon: '☁️', color: 'bg-orange-100 text-orange-800' },
    { type: 'github', name: 'GitHub', icon: '🐙', color: 'bg-gray-100 text-gray-800' },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-xl">Loading integrations...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Integrations</h1>
          <p className="text-gray-600 mt-1">Connect external services to your workflows</p>
        </div>
        <button 
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus size={20} />
          <span>Add Integration</span>
        </button>
      </div>

      {/* Search */}
      <div className="card">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search integrations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input pl-10"
          />
        </div>
      </div>

      {/* Available Integration Types */}
      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Available Integrations</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {integrationTypes.map((type) => (
            <div key={type.type} className="card hover:shadow-lg transition-shadow cursor-pointer">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center text-2xl">
                  {type.icon}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-800">{type.name}</h3>
                  <p className="text-sm text-gray-600">Connect to {type.name}</p>
                </div>
                <button className="btn-primary text-sm">
                  Connect
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Connected Integrations */}
      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Connected Integrations</h2>
        {filteredIntegrations.length === 0 ? (
          <div className="card text-center py-12">
            <Plug size={48} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600 text-lg">No integrations connected</p>
            <p className="text-gray-500 mt-2">Add your first integration to get started</p>
            <button 
              onClick={() => setShowCreateModal(true)}
              className="btn-primary mt-4"
            >
              Add Integration
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredIntegrations.map((integration) => (
              <div key={integration.id} className="card hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                      <Plug size={24} className="text-primary-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800">
                        {integration.name}
                      </h3>
                      <p className="text-sm text-gray-600 capitalize">{integration.type}</p>
                    </div>
                  </div>
                  {integration.is_active ? (
                    <CheckCircle size={20} className="text-green-500" />
                  ) : (
                    <XCircle size={20} className="text-red-500" />
                  )}
                </div>

                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                  {integration.description || 'No description'}
                </p>

                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <div className="text-sm text-gray-600">
                    <p>{integration.usage_count} uses</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      className="p-2 hover:bg-blue-100 rounded-lg transition-colors"
                      title="Edit"
                    >
                      <Edit size={18} className="text-blue-600" />
                    </button>
                    <button
                      onClick={() => handleDeleteIntegration(integration.id)}
                      className="p-2 hover:bg-red-100 rounded-lg transition-colors"
                      title="Delete"
                    >
                      <Trash2 size={18} className="text-red-600" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Modal (placeholder) */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Add New Integration</h2>
            <p className="text-gray-600 mb-6">
              Integration configuration form would go here.
            </p>
            <div className="flex justify-end space-x-4">
              <button
                onClick={() => setShowCreateModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button className="btn-primary">
                Add Integration
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Integrations;