import { useState } from 'react';
import { Wallet, Plus, Trash2, Eye, EyeOff, Copy, ExternalLink } from 'lucide-react';

interface WalletData {
  id: number;
  name: string;
  address: string;
  network: string;
  wallet_type: string;
  balance: number;
  is_active: boolean;
  created_at: string;
}

export default function Wallets() {
  const [wallets, setWallets] = useState<WalletData[]>([
    {
      id: 1,
      name: 'Main Ethereum Wallet',
      address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
      network: 'ethereum',
      wallet_type: 'hot',
      balance: 12.5,
      is_active: true,
      created_at: '2024-01-10T10:00:00Z'
    },
    {
      id: 2,
      name: 'Polygon Trading',
      address: '0x8ba1f109551bD432803012645Ac136ddd64DBA72',
      network: 'polygon',
      wallet_type: 'hot',
      balance: 450.8,
      is_active: true,
      created_at: '2024-01-12T14:30:00Z'
    },
    {
      id: 3,
      name: 'Bitcoin Cold Storage',
      address: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
      network: 'bitcoin',
      wallet_type: 'cold',
      balance: 0.5,
      is_active: true,
      created_at: '2024-01-08T09:15:00Z'
    }
  ]);

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newWallet, setNewWallet] = useState({
    name: '',
    network: 'ethereum',
    wallet_type: 'hot'
  });

  const [selectedNetwork, setSelectedNetwork] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const networks = [
    { value: 'all', label: 'All Networks' },
    { value: 'ethereum', label: 'Ethereum' },
    { value: 'polygon', label: 'Polygon' },
    { value: 'bitcoin', label: 'Bitcoin' },
    { value: 'binance', label: 'Binance Smart Chain' },
    { value: 'solana', label: 'Solana' }
  ];

  const walletTypes = [
    { value: 'hot', label: 'Hot Wallet' },
    { value: 'cold', label: 'Cold Wallet' },
    { value: 'multisig', label: 'Multi-Signature' }
  ];

  const handleCreateWallet = () => {
    const wallet: WalletData = {
      id: wallets.length + 1,
      name: newWallet.name,
      address: `0x${Math.random().toString(16).substr(2, 40)}`,
      network: newWallet.network,
      wallet_type: newWallet.wallet_type,
      balance: 0,
      is_active: true,
      created_at: new Date().toISOString()
    };
    setWallets([...wallets, wallet]);
    setShowCreateModal(false);
    setNewWallet({ name: '', network: 'ethereum', wallet_type: 'hot' });
  };

  const handleDeleteWallet = (id: number) => {
    if (confirm('Are you sure you want to delete this wallet?')) {
      setWallets(wallets.filter(w => w.id !== id));
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('Address copied to clipboard!');
  };

  const formatAddress = (address: string) => {
    if (address.length > 20) {
      return `${address.slice(0, 10)}...${address.slice(-8)}`;
    }
    return address;
  };

  const getNetworkColor = (network: string) => {
    switch (network.toLowerCase()) {
      case 'ethereum': return 'bg-indigo-100 text-indigo-800';
      case 'polygon': return 'bg-purple-100 text-purple-800';
      case 'bitcoin': return 'bg-orange-100 text-orange-800';
      case 'binance': return 'bg-yellow-100 text-yellow-800';
      case 'solana': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getWalletTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'hot': return 'bg-red-100 text-red-800';
      case 'cold': return 'bg-blue-100 text-blue-800';
      case 'multisig': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredWallets = wallets.filter(wallet => {
    const matchesNetwork = selectedNetwork === 'all' || wallet.network === selectedNetwork;
    const matchesSearch = wallet.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         wallet.address.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesNetwork && matchesSearch;
  });

  const totalBalance = filteredWallets.reduce((sum, wallet) => sum + wallet.balance, 0);

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Wallets</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage your blockchain wallets across multiple networks
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Wallet
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Wallet className="h-6 w-6 text-indigo-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Wallets</dt>
                  <dd className="text-2xl font-semibold text-gray-900">{filteredWallets.length}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Wallet className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Active Wallets</dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {filteredWallets.filter(w => w.is_active).length}
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
                <Wallet className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Balance</dt>
                  <dd className="text-2xl font-semibold text-gray-900">${totalBalance.toFixed(2)}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mt-8 bg-white shadow rounded-lg p-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Wallets
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

      {/* Wallets Grid */}
      <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {filteredWallets.map((wallet) => (
          <div key={wallet.id} className="bg-white shadow rounded-lg overflow-hidden">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">{wallet.name}</h3>
                <div className="flex space-x-2">
                  <button
                    onClick={() => copyToClipboard(wallet.address)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteWallet(wallet.id)}
                    className="text-red-400 hover:text-red-600"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                <div>
                  <p className="text-xs text-gray-500 mb-1">Address</p>
                  <p className="text-sm font-mono text-gray-900">{formatAddress(wallet.address)}</p>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Network</p>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getNetworkColor(wallet.network)}`}>
                      {wallet.network.charAt(0).toUpperCase() + wallet.network.slice(1)}
                    </span>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Type</p>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getWalletTypeColor(wallet.wallet_type)}`}>
                      {wallet.wallet_type.charAt(0).toUpperCase() + wallet.wallet_type.slice(1)}
                    </span>
                  </div>
                </div>

                <div>
                  <p className="text-xs text-gray-500 mb-1">Balance</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {wallet.balance} {wallet.network === 'bitcoin' ? 'BTC' : 'ETH'}
                  </p>
                </div>

                <div className="pt-3 border-t border-gray-200">
                  <p className="text-xs text-gray-500">
                    Created: {new Date(wallet.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredWallets.length === 0 && (
        <div className="mt-8 text-center py-12 bg-white shadow rounded-lg">
          <Wallet className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No wallets found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchQuery || selectedNetwork !== 'all' 
              ? 'Try adjusting your filters'
              : 'Get started by creating a new wallet'}
          </p>
        </div>
      )}

      {/* Create Wallet Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Wallet</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Wallet Name
                </label>
                <input
                  type="text"
                  value={newWallet.name}
                  onChange={(e) => setNewWallet({ ...newWallet, name: e.target.value })}
                  placeholder="My Ethereum Wallet"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Network
                </label>
                <select
                  value={newWallet.network}
                  onChange={(e) => setNewWallet({ ...newWallet, network: e.target.value })}
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
                  Wallet Type
                </label>
                <select
                  value={newWallet.wallet_type}
                  onChange={(e) => setNewWallet({ ...newWallet, wallet_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  {walletTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
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
                onClick={handleCreateWallet}
                disabled={!newWallet.name}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Create Wallet
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}