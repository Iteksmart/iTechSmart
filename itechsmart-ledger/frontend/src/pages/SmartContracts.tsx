import { useState } from 'react';
import { FileCode, Plus, Play, Eye, Trash2, CheckCircle, Clock, AlertCircle } from 'lucide-react';

interface SmartContract {
  id: number;
  name: string;
  description: string;
  network: string;
  contract_address: string | null;
  status: string;
  is_verified: boolean;
  created_at: string;
  deployed_at: string | null;
  source_code: string;
}

export default function SmartContracts() {
  const [contracts, setContracts] = useState<SmartContract[]>([
    {
      id: 1,
      name: 'ERC20 Token Contract',
      description: 'Standard ERC20 token implementation',
      network: 'ethereum',
      contract_address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
      status: 'deployed',
      is_verified: true,
      created_at: '2024-01-10T10:00:00Z',
      deployed_at: '2024-01-10T11:30:00Z',
      source_code: 'pragma solidity ^0.8.0;\n\ncontract Token { ... }'
    },
    {
      id: 2,
      name: 'NFT Marketplace',
      description: 'Decentralized NFT marketplace contract',
      network: 'polygon',
      contract_address: '0x8ba1f109551bD432803012645Ac136ddd64DBA72',
      status: 'deployed',
      is_verified: false,
      created_at: '2024-01-12T14:00:00Z',
      deployed_at: '2024-01-12T15:45:00Z',
      source_code: 'pragma solidity ^0.8.0;\n\ncontract NFTMarketplace { ... }'
    },
    {
      id: 3,
      name: 'Staking Contract',
      description: 'Token staking and rewards distribution',
      network: 'ethereum',
      contract_address: null,
      status: 'draft',
      is_verified: false,
      created_at: '2024-01-14T09:00:00Z',
      deployed_at: null,
      source_code: 'pragma solidity ^0.8.0;\n\ncontract Staking { ... }'
    }
  ]);

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedContract, setSelectedContract] = useState<SmartContract | null>(null);
  const [newContract, setNewContract] = useState({
    name: '',
    description: '',
    network: 'ethereum',
    source_code: ''
  });

  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedNetwork, setSelectedNetwork] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const networks = [
    { value: 'all', label: 'All Networks' },
    { value: 'ethereum', label: 'Ethereum' },
    { value: 'polygon', label: 'Polygon' },
    { value: 'binance', label: 'Binance Smart Chain' }
  ];

  const statuses = [
    { value: 'all', label: 'All Statuses' },
    { value: 'draft', label: 'Draft' },
    { value: 'deployed', label: 'Deployed' },
    { value: 'verified', label: 'Verified' }
  ];

  const handleCreateContract = () => {
    const contract: SmartContract = {
      id: contracts.length + 1,
      name: newContract.name,
      description: newContract.description,
      network: newContract.network,
      contract_address: null,
      status: 'draft',
      is_verified: false,
      created_at: new Date().toISOString(),
      deployed_at: null,
      source_code: newContract.source_code
    };
    setContracts([...contracts, contract]);
    setShowCreateModal(false);
    setNewContract({ name: '', description: '', network: 'ethereum', source_code: '' });
  };

  const handleDeployContract = (id: number) => {
    setContracts(contracts.map(contract => {
      if (contract.id === id) {
        return {
          ...contract,
          status: 'deployed',
          contract_address: `0x${Math.random().toString(16).substr(2, 40)}`,
          deployed_at: new Date().toISOString()
        };
      }
      return contract;
    }));
  };

  const handleDeleteContract = (id: number) => {
    if (confirm('Are you sure you want to delete this contract?')) {
      setContracts(contracts.filter(c => c.id !== id));
    }
  };

  const handleViewContract = (contract: SmartContract) => {
    setSelectedContract(contract);
    setShowViewModal(true);
  };

  const formatAddress = (address: string | null) => {
    if (!address) return 'Not deployed';
    if (address.length > 20) {
      return `${address.slice(0, 10)}...${address.slice(-8)}`;
    }
    return address;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'deployed':
      case 'verified':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'draft':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'deployed': return 'bg-green-100 text-green-800';
      case 'verified': return 'bg-blue-100 text-blue-800';
      case 'draft': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getNetworkColor = (network: string) => {
    switch (network.toLowerCase()) {
      case 'ethereum': return 'bg-indigo-100 text-indigo-800';
      case 'polygon': return 'bg-purple-100 text-purple-800';
      case 'binance': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredContracts = contracts.filter(contract => {
    const matchesStatus = selectedStatus === 'all' || contract.status === selectedStatus;
    const matchesNetwork = selectedNetwork === 'all' || contract.network === selectedNetwork;
    const matchesSearch = contract.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         contract.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (contract.contract_address && contract.contract_address.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesStatus && matchesNetwork && matchesSearch;
  });

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Smart Contracts</h1>
          <p className="mt-2 text-sm text-gray-700">
            Deploy and manage smart contracts across blockchain networks
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Contract
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FileCode className="h-6 w-6 text-indigo-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Contracts</dt>
                  <dd className="text-2xl font-semibold text-gray-900">{filteredContracts.length}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Deployed</dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {filteredContracts.filter(c => c.status === 'deployed' || c.status === 'verified').length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircle className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Verified</dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {filteredContracts.filter(c => c.is_verified).length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Clock className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Drafts</dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {filteredContracts.filter(c => c.status === 'draft').length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mt-8 bg-white shadow rounded-lg p-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Contracts
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by name or address..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Status
            </label>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              {statuses.map(status => (
                <option key={status.value} value={status.value}>
                  {status.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Network
            </label>
            <select
              value={selectedNetwork}
              onChange={(e) => setSelectedNetwork(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              {networks.map(network => (
                <option key={network.value} value={network.value}>
                  {network.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Contracts Grid */}
      <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {filteredContracts.map((contract) => (
          <div key={contract.id} className="bg-white shadow rounded-lg overflow-hidden">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  {getStatusIcon(contract.status)}
                  <h3 className="ml-2 text-lg font-medium text-gray-900">{contract.name}</h3>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleViewContract(contract)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteContract(contract.id)}
                    className="text-red-400 hover:text-red-600"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-4">{contract.description}</p>

              <div className="space-y-3">
                <div>
                  <p className="text-xs text-gray-500 mb-1">Contract Address</p>
                  <p className="text-sm font-mono text-gray-900">{formatAddress(contract.contract_address)}</p>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Network</p>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getNetworkColor(contract.network)}`}>
                      {contract.network.charAt(0).toUpperCase() + contract.network.slice(1)}
                    </span>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Status</p>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(contract.status)}`}>
                      {contract.status.charAt(0).toUpperCase() + contract.status.slice(1)}
                    </span>
                  </div>
                </div>

                {contract.is_verified && (
                  <div className="flex items-center text-sm text-blue-600">
                    <CheckCircle className="w-4 h-4 mr-1" />
                    Verified Contract
                  </div>
                )}

                <div className="pt-3 border-t border-gray-200">
                  <p className="text-xs text-gray-500">
                    Created: {new Date(contract.created_at).toLocaleDateString()}
                  </p>
                  {contract.deployed_at && (
                    <p className="text-xs text-gray-500">
                      Deployed: {new Date(contract.deployed_at).toLocaleDateString()}
                    </p>
                  )}
                </div>

                {contract.status === 'draft' && (
                  <button
                    onClick={() => handleDeployContract(contract.id)}
                    className="w-full mt-3 inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Deploy Contract
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredContracts.length === 0 && (
        <div className="mt-8 text-center py-12 bg-white shadow rounded-lg">
          <FileCode className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No contracts found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchQuery || selectedStatus !== 'all' || selectedNetwork !== 'all'
              ? 'Try adjusting your filters'
              : 'Get started by creating a new smart contract'}
          </p>
        </div>
      )}

      {/* Create Contract Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Smart Contract</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contract Name
                </label>
                <input
                  type="text"
                  value={newContract.name}
                  onChange={(e) => setNewContract({ ...newContract, name: e.target.value })}
                  placeholder="My Token Contract"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={newContract.description}
                  onChange={(e) => setNewContract({ ...newContract, description: e.target.value })}
                  placeholder="Describe your smart contract..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Network
                </label>
                <select
                  value={newContract.network}
                  onChange={(e) => setNewContract({ ...newContract, network: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  {networks.filter(n => n.value !== 'all').map(network => (
                    <option key={network.value} value={network.value}>
                      {network.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Source Code
                </label>
                <textarea
                  value={newContract.source_code}
                  onChange={(e) => setNewContract({ ...newContract, source_code: e.target.value })}
                  placeholder="pragma solidity ^0.8.0;&#10;&#10;contract MyContract {&#10;    // Your code here&#10;}"
                  rows={10}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm"
                />
              </div>
            </div>

            <div className="mt-6 flex justify-end space-x-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateContract}
                disabled={!newContract.name || !newContract.source_code}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Create Contract
              </button>
            </div>
          </div>
        </div>
      )}

      {/* View Contract Modal */}
      {showViewModal && selectedContract && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">{selectedContract.name}</h3>
              <button
                onClick={() => setShowViewModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">Description</p>
                <p className="text-sm text-gray-600">{selectedContract.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Network</p>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getNetworkColor(selectedContract.network)}`}>
                    {selectedContract.network.charAt(0).toUpperCase() + selectedContract.network.slice(1)}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Status</p>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(selectedContract.status)}`}>
                    {selectedContract.status.charAt(0).toUpperCase() + selectedContract.status.slice(1)}
                  </span>
                </div>
              </div>

              {selectedContract.contract_address && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Contract Address</p>
                  <p className="text-sm font-mono text-gray-900 bg-gray-50 p-2 rounded">
                    {selectedContract.contract_address}
                  </p>
                </div>
              )}

              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Source Code</p>
                <pre className="text-sm font-mono text-gray-900 bg-gray-50 p-4 rounded overflow-x-auto">
                  {selectedContract.source_code}
                </pre>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setShowViewModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}