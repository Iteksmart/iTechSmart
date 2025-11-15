import { useState } from 'react';
import { ArrowLeftRight, Plus, Search, Filter, ExternalLink, Clock, CheckCircle, XCircle } from 'lucide-react';

interface Transaction {
  id: number;
  from_address: string;
  to_address: string;
  amount: number;
  fee: number;
  network: string;
  status: string;
  transaction_hash: string;
  block_number: number | null;
  confirmations: number;
  created_at: string;
  confirmed_at: string | null;
}

export default function Transactions() {
  const [transactions, setTransactions] = useState<Transaction[]>([
    {
      id: 1,
      from_address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
      to_address: '0x8ba1f109551bD432803012645Ac136ddd64DBA72',
      amount: 1.5,
      fee: 0.002,
      network: 'ethereum',
      status: 'confirmed',
      transaction_hash: '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
      block_number: 18500000,
      confirmations: 12,
      created_at: '2024-01-15T10:30:00Z',
      confirmed_at: '2024-01-15T10:35:00Z'
    },
    {
      id: 2,
      from_address: '0x9ba1f109551bD432803012645Ac136ddd64DBA73',
      to_address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
      amount: 0.8,
      fee: 0.0005,
      network: 'polygon',
      status: 'confirmed',
      transaction_hash: '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
      block_number: 50123456,
      confirmations: 25,
      created_at: '2024-01-15T09:15:00Z',
      confirmed_at: '2024-01-15T09:18:00Z'
    },
    {
      id: 3,
      from_address: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
      to_address: '3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy',
      amount: 0.05,
      fee: 0.0001,
      network: 'bitcoin',
      status: 'pending',
      transaction_hash: 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
      block_number: null,
      confirmations: 0,
      created_at: '2024-01-15T08:45:00Z',
      confirmed_at: null
    },
    {
      id: 4,
      from_address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
      to_address: '0x5555567890abcdef1234567890abcdef12345678',
      amount: 2.3,
      fee: 0.003,
      network: 'ethereum',
      status: 'failed',
      transaction_hash: '0xfailed567890abcdef1234567890abcdef1234567890abcdef1234567890abcd',
      block_number: 18499999,
      confirmations: 0,
      created_at: '2024-01-14T16:20:00Z',
      confirmed_at: null
    }
  ]);

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTransaction, setNewTransaction] = useState({
    from_wallet_id: '',
    to_address: '',
    amount: '',
    network: 'ethereum'
  });

  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedNetwork, setSelectedNetwork] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const networks = [
    { value: 'all', label: 'All Networks' },
    { value: 'ethereum', label: 'Ethereum' },
    { value: 'polygon', label: 'Polygon' },
    { value: 'bitcoin', label: 'Bitcoin' },
    { value: 'binance', label: 'Binance Smart Chain' }
  ];

  const statuses = [
    { value: 'all', label: 'All Statuses' },
    { value: 'pending', label: 'Pending' },
    { value: 'confirmed', label: 'Confirmed' },
    { value: 'failed', label: 'Failed' }
  ];

  const handleCreateTransaction = () => {
    const transaction: Transaction = {
      id: transactions.length + 1,
      from_address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
      to_address: newTransaction.to_address,
      amount: parseFloat(newTransaction.amount),
      fee: 0.002,
      network: newTransaction.network,
      status: 'pending',
      transaction_hash: `0x${Math.random().toString(16).substr(2, 64)}`,
      block_number: null,
      confirmations: 0,
      created_at: new Date().toISOString(),
      confirmed_at: null
    };
    setTransactions([transaction, ...transactions]);
    setShowCreateModal(false);
    setNewTransaction({ from_wallet_id: '', to_address: '', amount: '', network: 'ethereum' });
  };

  const formatAddress = (address: string) => {
    if (address.length > 20) {
      return `${address.slice(0, 10)}...${address.slice(-8)}`;
    }
    return address;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'confirmed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getNetworkColor = (network: string) => {
    switch (network.toLowerCase()) {
      case 'ethereum': return 'bg-indigo-100 text-indigo-800';
      case 'polygon': return 'bg-purple-100 text-purple-800';
      case 'bitcoin': return 'bg-orange-100 text-orange-800';
      case 'binance': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredTransactions = transactions.filter(tx => {
    const matchesStatus = selectedStatus === 'all' || tx.status === selectedStatus;
    const matchesNetwork = selectedNetwork === 'all' || tx.network === selectedNetwork;
    const matchesSearch = tx.transaction_hash.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         tx.from_address.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         tx.to_address.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesNetwork && matchesSearch;
  });

  const totalVolume = filteredTransactions
    .filter(tx => tx.status === 'confirmed')
    .reduce((sum, tx) => sum + tx.amount, 0);

  const totalFees = filteredTransactions
    .filter(tx => tx.status === 'confirmed')
    .reduce((sum, tx) => sum + tx.fee, 0);

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Transactions</h1>
          <p className="mt-2 text-sm text-gray-700">
            View and manage your blockchain transactions
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Transaction
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ArrowLeftRight className="h-6 w-6 text-indigo-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Transactions</dt>
                  <dd className="text-2xl font-semibold text-gray-900">{filteredTransactions.length}</dd>
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
                  <dt className="text-sm font-medium text-gray-500 truncate">Confirmed</dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {filteredTransactions.filter(tx => tx.status === 'confirmed').length}
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
                <ArrowLeftRight className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Volume</dt>
                  <dd className="text-2xl font-semibold text-gray-900">{totalVolume.toFixed(4)}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ArrowLeftRight className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Fees</dt>
                  <dd className="text-2xl font-semibold text-gray-900">{totalFees.toFixed(6)}</dd>
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
              Search Transactions
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by hash or address..."
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

      {/* Transactions Table */}
      <div className="mt-8 bg-white shadow rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Hash
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  From
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  To
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fee
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Network
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Block
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredTransactions.map((tx) => (
                <tr key={tx.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getStatusIcon(tx.status)}
                      <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(tx.status)}`}>
                        {tx.status.charAt(0).toUpperCase() + tx.status.slice(1)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-sm font-medium text-indigo-600 font-mono">
                        {formatAddress(tx.transaction_hash)}
                      </span>
                      <ExternalLink className="ml-2 w-4 h-4 text-gray-400 cursor-pointer hover:text-gray-600" />
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                    {formatAddress(tx.from_address)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                    {formatAddress(tx.to_address)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {tx.amount} {tx.network === 'bitcoin' ? 'BTC' : 'ETH'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {tx.fee.toFixed(6)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getNetworkColor(tx.network)}`}>
                      {tx.network.charAt(0).toUpperCase() + tx.network.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {tx.block_number ? (
                      <span>#{tx.block_number.toLocaleString()}</span>
                    ) : (
                      <span className="text-gray-400">Pending</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(tx.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {filteredTransactions.length === 0 && (
        <div className="mt-8 text-center py-12 bg-white shadow rounded-lg">
          <ArrowLeftRight className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No transactions found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchQuery || selectedStatus !== 'all' || selectedNetwork !== 'all'
              ? 'Try adjusting your filters'
              : 'Get started by creating a new transaction'}
          </p>
        </div>
      )}

      {/* Create Transaction Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Transaction</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  To Address
                </label>
                <input
                  type="text"
                  value={newTransaction.to_address}
                  onChange={(e) => setNewTransaction({ ...newTransaction, to_address: e.target.value })}
                  placeholder="0x..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Amount
                </label>
                <input
                  type="number"
                  step="0.000001"
                  value={newTransaction.amount}
                  onChange={(e) => setNewTransaction({ ...newTransaction, amount: e.target.value })}
                  placeholder="0.0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Network
                </label>
                <select
                  value={newTransaction.network}
                  onChange={(e) => setNewTransaction({ ...newTransaction, network: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  {networks.filter(n => n.value !== 'all').map(network => (
                    <option key={network.value} value={network.value}>
                      {network.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                <p className="text-sm text-yellow-800">
                  <strong>Note:</strong> Estimated fee: 0.002 {newTransaction.network === 'bitcoin' ? 'BTC' : 'ETH'}
                </p>
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
                onClick={handleCreateTransaction}
                disabled={!newTransaction.to_address || !newTransaction.amount}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Send Transaction
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}