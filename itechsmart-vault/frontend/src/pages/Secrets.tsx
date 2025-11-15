import { useState, useEffect } from 'react';
import { Plus, Search, Eye, EyeOff, Copy, Edit, Trash2, RefreshCw } from 'lucide-react';
import axios from 'axios';

interface Secret {
  id: number;
  name: string;
  description: string;
  secret_type: string;
  status: string;
  vault_id: number;
  access_count: number;
  created_at: string;
}

const Secrets = () => {
  const [secrets, setSecrets] = useState<Secret[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchSecrets();
  }, []);

  const fetchSecrets = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/secrets', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSecrets(response.data);
    } catch (error) {
      console.error('Failed to fetch secrets:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this secret?')) return;
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`/api/secrets/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchSecrets();
    } catch (error) {
      console.error('Failed to delete secret:', error);
    }
  };

  const filteredSecrets = secrets.filter(s =>
    s.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (isLoading) return <div className="flex items-center justify-center h-full"><div className="text-xl">Loading...</div></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Secrets</h1>
          <p className="text-gray-600 mt-1">Manage your encrypted secrets</p>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="btn-primary flex items-center space-x-2">
          <Plus size={20} />
          <span>Create Secret</span>
        </button>
      </div>

      <div className="card">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input type="text" placeholder="Search secrets..." value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)} className="input pl-10" />
        </div>
      </div>

      {filteredSecrets.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-600 text-lg">No secrets found</p>
          <button onClick={() => setShowCreateModal(true)} className="btn-primary mt-4">Create Secret</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredSecrets.map((secret) => (
            <div key={secret.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-800">{secret.name}</h3>
                  <p className="text-sm text-gray-600">{secret.description || 'No description'}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2 mb-4">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  secret.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {secret.status}
                </span>
                <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {secret.secret_type.replace('_', ' ')}
                </span>
              </div>
              <div className="flex items-center justify-between pt-4 border-t">
                <span className="text-sm text-gray-600">{secret.access_count} accesses</span>
                <div className="flex items-center space-x-2">
                  <button className="p-2 hover:bg-blue-100 rounded-lg" title="View">
                    <Eye size={18} className="text-blue-600" />
                  </button>
                  <button className="p-2 hover:bg-green-100 rounded-lg" title="Copy">
                    <Copy size={18} className="text-green-600" />
                  </button>
                  <button onClick={() => handleDelete(secret.id)} className="p-2 hover:bg-red-100 rounded-lg" title="Delete">
                    <Trash2 size={18} className="text-red-600" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Secrets;
