import { useState, useEffect } from 'react';
import { Wallet, ArrowLeftRight, FileCode, TrendingUp, Activity, DollarSign } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface DashboardStats {
  total_wallets: number;
  total_transactions: number;
  total_smart_contracts: number;
  total_volume: number;
  network_stats: NetworkStat[];
}

interface NetworkStat {
  network: string;
  total_transactions: number;
  total_wallets: number;
  total_volume: number;
  avg_transaction_fee: number;
}

interface Transaction {
  id: number;
  from_address: string;
  to_address: string;
  amount: number;
  network: string;
  status: string;
  created_at: string;
  transaction_hash: string;
}

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    total_wallets: 12,
    total_transactions: 156,
    total_smart_contracts: 8,
    total_volume: 45678.90,
    network_stats: [
      { network: 'ethereum', total_transactions: 89, total_wallets: 5, total_volume: 25000, avg_transaction_fee: 15.5 },
      { network: 'polygon', total_transactions: 45, total_wallets: 4, total_volume: 12000, avg_transaction_fee: 0.5 },
      { network: 'bitcoin', total_transactions: 22, total_wallets: 3, total_volume: 8678.90, avg_transaction_fee: 2.3 },
    ]
  });

  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([
    {
      id: 1,
      from_address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
      to_address: '0x8ba1f109551bD432803012645Ac136ddd64DBA72',
      amount: 1.5,
      network: 'ethereum',
      status: 'confirmed',
      created_at: '2024-01-15T10:30:00Z',
      transaction_hash: '0x1234...5678'
    },
    {
      id: 2,
      from_address: '0x9ba1f109551bD432803012645Ac136ddd64DBA73',
      to_address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
      amount: 0.8,
      network: 'polygon',
      status: 'confirmed',
      created_at: '2024-01-15T09:15:00Z',
      transaction_hash: '0xabcd...efgh'
    },
    {
      id: 3,
      from_address: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
      to_address: '3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy',
      amount: 0.05,
      network: 'bitcoin',
      status: 'pending',
      created_at: '2024-01-15T08:45:00Z',
      transaction_hash: 'bc1q...xyz'
    }
  ]);

  // Transaction volume over time (last 7 days)
  const volumeData = [
    { date: 'Jan 9', volume: 4200 },
    { date: 'Jan 10', volume: 5800 },
    { date: 'Jan 11', volume: 6500 },
    { date: 'Jan 12', volume: 5200 },
    { date: 'Jan 13', volume: 7100 },
    { date: 'Jan 14', volume: 6800 },
    { date: 'Jan 15', volume: 8900 },
  ];

  // Network distribution
  const networkDistribution = stats.network_stats.map(stat => ({
    name: stat.network.charAt(0).toUpperCase() + stat.network.slice(1),
    value: stat.total_transactions
  }));

  const formatAddress = (address: string) => {
    if (address.length > 20) {
      return `${address.slice(0, 10)}...${address.slice(-8)}`;
    }
    return address;
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

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-sm text-gray-700">
            Overview of your blockchain activities and portfolio
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Wallet className="h-6 w-6 text-indigo-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Wallets</dt>
                  <dd className="text-2xl font-semibold text-gray-900">{stats.total_wallets}</dd>
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
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Transactions</dt>
                  <dd className="text-2xl font-semibold text-gray-900">{stats.total_transactions}</dd>
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
                  <dt className="text-sm font-medium text-gray-500 truncate">Smart Contracts</dt>
                  <dd className="text-2xl font-semibold text-gray-900">{stats.total_smart_contracts}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DollarSign className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Volume</dt>
                  <dd className="text-2xl font-semibold text-gray-900">${stats.total_volume.toLocaleString()}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="mt-8 grid grid-cols-1 gap-5 lg:grid-cols-2">
        {/* Transaction Volume Chart */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Transaction Volume (Last 7 Days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={volumeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="volume" stroke="#6366f1" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Network Distribution Chart */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Network Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={networkDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {networkDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Network Stats Table */}
      <div className="mt-8 bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Network Statistics</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Network
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Transactions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Wallets
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Volume
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Fee
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {stats.network_stats.map((stat) => (
                <tr key={stat.network}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getNetworkColor(stat.network)}`}>
                      {stat.network.charAt(0).toUpperCase() + stat.network.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {stat.total_transactions}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {stat.total_wallets}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${stat.total_volume.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${stat.avg_transaction_fee.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="mt-8 bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Transactions</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
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
                  Network
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentTransactions.map((tx) => (
                <tr key={tx.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-indigo-600">
                    {tx.transaction_hash}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatAddress(tx.from_address)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatAddress(tx.to_address)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {tx.amount} {tx.network === 'bitcoin' ? 'BTC' : 'ETH'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getNetworkColor(tx.network)}`}>
                      {tx.network.charAt(0).toUpperCase() + tx.network.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(tx.status)}`}>
                      {tx.status.charAt(0).toUpperCase() + tx.status.slice(1)}
                    </span>
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