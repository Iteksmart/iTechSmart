import React, { useState } from 'react';
import { BarChart3, PieChart, LineChart, TrendingUp, Activity, Grid, Plus } from 'lucide-react';
import { BarChart, Bar, LineChart as RechartsLine, Line, PieChart as RechartsPie, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';

const Visualizations: React.FC = () => {
  const [selectedType, setSelectedType] = useState('all');

  // Sample data
  const barData = [
    { name: 'Jan', sales: 4000, target: 3500 },
    { name: 'Feb', sales: 3000, target: 3200 },
    { name: 'Mar', sales: 5000, target: 4500 },
    { name: 'Apr', sales: 4500, target: 4000 },
    { name: 'May', sales: 6000, target: 5500 },
    { name: 'Jun', sales: 5500, target: 5000 },
  ];

  const pieData = [
    { name: 'Product A', value: 400, color: '#3b82f6' },
    { name: 'Product B', value: 300, color: '#10b981' },
    { name: 'Product C', value: 200, color: '#f59e0b' },
    { name: 'Product D', value: 100, color: '#ef4444' },
  ];

  const lineData = [
    { month: 'Jan', revenue: 45000, expenses: 32000 },
    { month: 'Feb', revenue: 52000, expenses: 35000 },
    { month: 'Mar', revenue: 48000, expenses: 33000 },
    { month: 'Apr', revenue: 61000, expenses: 38000 },
    { month: 'May', revenue: 55000, expenses: 36000 },
    { month: 'Jun', revenue: 67000, expenses: 40000 },
  ];

  const areaData = [
    { date: 'Mon', users: 120 },
    { date: 'Tue', users: 150 },
    { date: 'Wed', users: 180 },
    { date: 'Thu', users: 160 },
    { date: 'Fri', users: 200 },
    { date: 'Sat', users: 140 },
    { date: 'Sun', users: 110 },
  ];

  const visualizationTypes = [
    { id: 'all', name: 'All Types', icon: Grid, count: 20 },
    { id: 'bar', name: 'Bar Charts', icon: BarChart3, count: 5 },
    { id: 'line', name: 'Line Charts', icon: LineChart, count: 4 },
    { id: 'pie', name: 'Pie Charts', icon: PieChart, count: 3 },
    { id: 'area', name: 'Area Charts', icon: Activity, count: 4 },
    { id: 'metric', name: 'Metrics', icon: TrendingUp, count: 4 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-blue-600" />
            Visualizations
          </h1>
          <p className="text-gray-600 mt-2">Explore and create data visualizations</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Create Visualization
        </button>
      </div>

      {/* Visualization Type Filter */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
          {visualizationTypes.map((type) => {
            const Icon = type.icon;
            return (
              <button
                key={type.id}
                onClick={() => setSelectedType(type.id)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  selectedType === type.id
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Icon className={`w-6 h-6 mx-auto mb-2 ${selectedType === type.id ? 'text-blue-600' : 'text-gray-600'}`} />
                <p className={`text-sm font-medium ${selectedType === type.id ? 'text-blue-900' : 'text-gray-900'}`}>
                  {type.name}
                </p>
                <p className="text-xs text-gray-500 mt-1">{type.count} charts</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Sample Visualizations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Monthly Sales Performance</h3>
            <BarChart3 className="w-5 h-5 text-blue-600" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="sales" fill="#3b82f6" name="Actual Sales" />
              <Bar dataKey="target" fill="#10b981" name="Target" />
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-4 flex items-center justify-between text-sm">
            <span className="text-gray-600">Last updated: 2 hours ago</span>
            <button className="text-blue-600 hover:text-blue-700 font-medium">View Details →</button>
          </div>
        </div>

        {/* Pie Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Product Distribution</h3>
            <PieChart className="w-5 h-5 text-green-600" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <RechartsPie>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </RechartsPie>
          </ResponsiveContainer>
          <div className="mt-4 flex items-center justify-between text-sm">
            <span className="text-gray-600">Last updated: 1 hour ago</span>
            <button className="text-blue-600 hover:text-blue-700 font-medium">View Details →</button>
          </div>
        </div>

        {/* Line Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Revenue vs Expenses</h3>
            <LineChart className="w-5 h-5 text-purple-600" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <RechartsLine data={lineData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} name="Revenue" />
              <Line type="monotone" dataKey="expenses" stroke="#ef4444" strokeWidth={2} name="Expenses" />
            </RechartsLine>
          </ResponsiveContainer>
          <div className="mt-4 flex items-center justify-between text-sm">
            <span className="text-gray-600">Last updated: 30 minutes ago</span>
            <button className="text-blue-600 hover:text-blue-700 font-medium">View Details →</button>
          </div>
        </div>

        {/* Area Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Daily Active Users</h3>
            <Activity className="w-5 h-5 text-orange-600" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={areaData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="users" stroke="#f59e0b" fill="#fef3c7" name="Active Users" />
            </AreaChart>
          </ResponsiveContainer>
          <div className="mt-4 flex items-center justify-between text-sm">
            <span className="text-gray-600">Last updated: 5 minutes ago</span>
            <button className="text-blue-600 hover:text-blue-700 font-medium">View Details →</button>
          </div>
        </div>

        {/* Metric Cards */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Key Metrics</h3>
            <TrendingUp className="w-5 h-5 text-blue-600" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-600 mb-1">Total Revenue</p>
              <p className="text-3xl font-bold text-blue-900">$328K</p>
              <p className="text-sm text-blue-600 mt-2">↑ 12.5%</p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-green-600 mb-1">New Customers</p>
              <p className="text-3xl font-bold text-green-900">1,250</p>
              <p className="text-sm text-green-600 mt-2">↑ 8.3%</p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-purple-600 mb-1">Conversion Rate</p>
              <p className="text-3xl font-bold text-purple-900">3.2%</p>
              <p className="text-sm text-purple-600 mt-2">↑ 5.7%</p>
            </div>
            <div className="p-4 bg-orange-50 rounded-lg">
              <p className="text-sm text-orange-600 mb-1">Avg Order Value</p>
              <p className="text-3xl font-bold text-orange-900">$262</p>
              <p className="text-sm text-orange-600 mt-2">↓ 2.1%</p>
            </div>
          </div>
          <div className="mt-4 flex items-center justify-between text-sm">
            <span className="text-gray-600">Real-time data</span>
            <button className="text-blue-600 hover:text-blue-700 font-medium">View All Metrics →</button>
          </div>
        </div>

        {/* Chart Templates */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Chart Templates</h3>
            <Grid className="w-5 h-5 text-gray-600" />
          </div>
          <div className="space-y-3">
            <button className="w-full p-4 bg-gray-50 hover:bg-gray-100 rounded-lg text-left transition-colors">
              <div className="flex items-center gap-3">
                <BarChart3 className="w-5 h-5 text-blue-600" />
                <div>
                  <p className="font-medium text-gray-900">Sales Dashboard</p>
                  <p className="text-sm text-gray-600">Revenue, orders, and customer metrics</p>
                </div>
              </div>
            </button>
            <button className="w-full p-4 bg-gray-50 hover:bg-gray-100 rounded-lg text-left transition-colors">
              <div className="flex items-center gap-3">
                <LineChart className="w-5 h-5 text-green-600" />
                <div>
                  <p className="font-medium text-gray-900">Trend Analysis</p>
                  <p className="text-sm text-gray-600">Time-series data visualization</p>
                </div>
              </div>
            </button>
            <button className="w-full p-4 bg-gray-50 hover:bg-gray-100 rounded-lg text-left transition-colors">
              <div className="flex items-center gap-3">
                <PieChart className="w-5 h-5 text-purple-600" />
                <div>
                  <p className="font-medium text-gray-900">Distribution Chart</p>
                  <p className="text-sm text-gray-600">Category breakdown and proportions</p>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Visualizations;