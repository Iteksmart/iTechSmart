import { useState, useEffect } from 'react';
import { Plus, FolderLock } from 'lucide-react';
import axios from 'axios';

interface Vault {
  id: number;
  name: string;
  description: string;
  is_default: boolean;
  secret_count: number;
  created_at: string;
}

const Vaults = () => {
  const [vaults, setVaults] = useState<Vault[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchVaults();
  }, []);

  const fetchVaults = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/vaults', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setVaults(response.data);
    } catch (error) {
      console.error('Failed to fetch vaults:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) return <div className="flex items-center justify-center h-full"><div className="text-xl">Loading...</div></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Vaults</h1>
          <p className="text-gray-600 mt-1">Organize secrets into vaults</p>
        </div>
        <button className="btn-primary flex items-center space-x-2">
          <Plus size={20} />
          <span>Create Vault</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {vaults.map((vault) => (
          <div key={vault.id} className="card hover:shadow-lg transition-shadow">
            <div className="flex items-center space-x-4 mb-4">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                <FolderLock size={24} className="text-primary-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-800">{vault.name}</h3>
                {vault.is_default && <span className="text-xs text-blue-600">Default</span>}
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-4">{vault.description || 'No description'}</p>
            <div className="pt-4 border-t">
              <p className="text-2xl font-bold text-gray-800">{vault.secret_count}</p>
              <p className="text-sm text-gray-600">Secrets</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Vaults;
