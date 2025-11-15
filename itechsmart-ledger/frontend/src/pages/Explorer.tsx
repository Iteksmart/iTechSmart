import { useState } from 'react';
import { Search, Cube, ArrowLeftRight, FileCode } from 'lucide-react';

interface Block {
  id: number;
  network: string;
  block_number: number;
  block_hash: string;
  timestamp: string;
  miner: string;
  transaction_count: number;
  gas_used: number;
  gas_limit: number;
}

export default function Explorer() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState<'block' | 'transaction' | 'address'>('block');
  const [selectedNetwork, setSelectedNetwork] = useState('ethereum');

  const [recentBlocks] = useState<Block[]>([
    {
      id: 1,
      network: 'ethereum',
      block_number: 18500000,
      block_hash: '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
      timestamp: '2024-01-15T10:30:00Z',
      miner: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
      transaction_count: 156,
      gas_used: 12500000,
      gas_limit: 30000000
    },
    {
      id: 2,
      network: 'ethereum',
      block_number: 18499999,
      block_hash: '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
      timestamp: '2024-01-15T10:28:00Z',
      miner: '0x8ba1f109551bD432803012645Ac136ddd64DBA72',
      transaction_count: 142,
      gas_used: 11800000,
      gas_limit: 30000000
    },
    {
      id: 3,
      network: 'ethereum',
      block_number: 18499998,
      block_hash: '0x567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234',
      timestamp: '2024-01-15T10:26:00Z',
      miner: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
      transaction_count: 168,
      gas_used: 13200000,
      gas_limit: 30000000
    }
  ]);

  const networks = [
    { value: 'ethereum', label: 'Ethereum' },
    { value: 'polygon', label: 'Polygon' },
    { value: 'bitcoin', label: 'Bitcoin' },
    { value: 'binance', label: 'Binance Smart Chain' }
  ];

  const searchTypes = [
    { value: 'block', label: 'Block Number' },
    { value: 'transaction', label: 'Transaction Hash' },
    { value: 'address', label: 'Address' }
  ];

  const handleSearch = () => {
    if (!searchQuery) return;
    alert(`Searching for ${searchType}: ${searchQuery} on ${selectedNetwork}`);
  };

  const formatAddress = (address: string) => {
    if (address.length > 20) {
      return `${address.slice(0, 10)}...${address.slice(-8)}`;
    }
    return address;
  };

  const formatHash = (hash: string) => {
    if (hash.length > 20) {
      return `${hash.slice(0, 16)}...${hash.slice(-8)}`;
    }
    return hash;
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

  const calculateGasUsedPercentage = (gasUsed: number, gasLimit: number) => {
    return ((gasUsed / gasLimit) * 100).toFixed(2);
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-3xl font-bold text-gray-900">Blockchain Explorer</h1>
          <p className="mt-2 text-sm text-gray-700">
            Search and explore blockchain data across multiple networks
          </p>
        </div>
      </div>

      {/* Search Section */}
      <div className="mt-8 bg-white shadow rounded-lg p-6">
        <div className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Network
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

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Type
              </label>
              <select
                value={searchType}
                onChange={(e) => setSearchType(e.target.value as any)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                {searchTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Query
              </label>
              <div className="flex">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={`Enter ${searchType}...`}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
                <button
                  onClick={handleSearch}
                  className="px-4 py-2 border border-transparent rounded-r-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  <Search className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
            <p className="text-sm text-blue-800">
              <strong>Tip:</strong> You can search by block number, transaction hash, or wallet address
            </p>
          </div>
        </div>
      </div>

      {/* Network Stats */}
      <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Cube className="h-6 w-6 text-indigo-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Latest Block</dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {recentBlocks[0]?.block_number.toLocaleString()}
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
                <ArrowLeftRight className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Avg Transactions</dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {Math.round(recentBlocks.reduce((sum, b) => sum + b.transaction_count, 0) / recentBlocks.length)}
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
                <Cube className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Avg Gas Used</dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {((recentBlocks.reduce((sum, b) => sum + b.gas_used, 0) / recentBlocks.length) / 1000000).toFixed(1)}M
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
                <FileCode className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Network</dt>
                  <dd className="text-lg font-semibold text-gray-900">
                    {selectedNetwork.charAt(0).toUpperCase() + selectedNetwork.slice(1)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Blocks */}
      <div className="mt-8 bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Blocks</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Block
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Hash
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Miner
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Transactions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Gas Used
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentBlocks.map((block) => (
                <tr key={block.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <Cube className="w-5 h-5 text-indigo-600 mr-2" />
                      <span className="text-sm font-medium text-indigo-600">
                        #{block.block_number.toLocaleString()}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm font-mono text-gray-500">
                      {formatHash(block.block_hash)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm font-mono text-gray-500">
                      {formatAddress(block.miner)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <ArrowLeftRight className="w-4 h-4 text-gray-400 mr-2" />
                      <span className="text-sm text-gray-900">{block.transaction_count}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex flex-col">
                      <span className="text-sm text-gray-900">
                        {(block.gas_used / 1000000).toFixed(2)}M
                      </span>
                      <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                        <div
                          className="bg-indigo-600 h-1.5 rounded-full"
                          style={{ width: `${calculateGasUsedPercentage(block.gas_used, block.gas_limit)}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500 mt-1">
                        {calculateGasUsedPercentage(block.gas_used, block.gas_limit)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(block.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Info Section */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-2">About Blockchain Explorer</h3>
        <p className="text-sm text-blue-800">
          The blockchain explorer allows you to search and view detailed information about blocks, transactions, 
          and addresses across multiple blockchain networks. Use the search bar above to find specific data, 
          or browse recent blocks to see the latest network activity.
        </p>
      </div>
    </div>
  );
}