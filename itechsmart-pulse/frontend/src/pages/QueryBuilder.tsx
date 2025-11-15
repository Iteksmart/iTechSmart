import React, { useState } from 'react';
import { Search, Play, Save, Download, Code, Table, Database, CheckCircle, XCircle } from 'lucide-react';

const QueryBuilder: React.FC = () => {
  const [query, setQuery] = useState('SELECT * FROM customers LIMIT 10;');
  const [results, setResults] = useState<any[]>([]);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionTime, setExecutionTime] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const sampleResults = [
    { id: 1, name: 'John Doe', email: 'john@example.com', country: 'USA', revenue: 5000 },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', country: 'UK', revenue: 7500 },
    { id: 3, name: 'Bob Johnson', email: 'bob@example.com', country: 'Canada', revenue: 3200 },
    { id: 4, name: 'Alice Brown', email: 'alice@example.com', country: 'Australia', revenue: 9100 },
    { id: 5, name: 'Charlie Wilson', email: 'charlie@example.com', country: 'USA', revenue: 6400 },
  ];

  const executeQuery = async () => {
    setIsExecuting(true);
    setError(null);
    
    // Simulate query execution
    setTimeout(() => {
      setResults(sampleResults);
      setExecutionTime(125);
      setIsExecuting(false);
    }, 1000);
  };

  const savedQueries = [
    { name: 'Top Customers', query: 'SELECT * FROM customers ORDER BY revenue DESC LIMIT 10' },
    { name: 'Monthly Revenue', query: 'SELECT DATE_TRUNC(\'month\', date) as month, SUM(amount) FROM orders GROUP BY month' },
    { name: 'Product Sales', query: 'SELECT product_name, COUNT(*) as sales FROM orders GROUP BY product_name' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Search className="w-8 h-8 text-blue-600" />
            Query Builder
          </h1>
          <p className="text-gray-600 mt-2">Write and execute SQL queries against your data sources</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-4">
          {/* Data Source Selector */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Database className="w-4 h-4" />
              Data Source
            </h3>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option>Sales Database</option>
              <option>CRM API</option>
              <option>Marketing Data</option>
            </select>
          </div>

          {/* Saved Queries */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Saved Queries</h3>
            <div className="space-y-2">
              {savedQueries.map((sq, index) => (
                <button
                  key={index}
                  onClick={() => setQuery(sq.query)}
                  className="w-full text-left px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg text-sm transition-colors"
                >
                  {sq.name}
                </button>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full px-3 py-2 bg-blue-50 text-blue-700 rounded-lg text-sm hover:bg-blue-100">
                New Query
              </button>
              <button className="w-full px-3 py-2 bg-gray-50 text-gray-700 rounded-lg text-sm hover:bg-gray-100">
                Query History
              </button>
              <button className="w-full px-3 py-2 bg-gray-50 text-gray-700 rounded-lg text-sm hover:bg-gray-100">
                Templates
              </button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3 space-y-4">
          {/* Query Editor */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <div className="flex items-center gap-2">
                <Code className="w-5 h-5 text-gray-600" />
                <h3 className="text-sm font-semibold text-gray-900">SQL Editor</h3>
              </div>
              <div className="flex gap-2">
                <button className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm flex items-center gap-2">
                  <Save className="w-4 h-4" />
                  Save
                </button>
                <button
                  onClick={executeQuery}
                  disabled={isExecuting}
                  className="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm flex items-center gap-2 disabled:opacity-50"
                >
                  <Play className="w-4 h-4" />
                  {isExecuting ? 'Executing...' : 'Run Query'}
                </button>
              </div>
            </div>
            <div className="p-4">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full h-48 p-4 font-mono text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50"
                placeholder="Enter your SQL query here..."
              />
            </div>
          </div>

          {/* Execution Info */}
          {(executionTime !== null || error) && (
            <div className={`rounded-xl shadow-sm border p-4 ${error ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
              <div className="flex items-center gap-2">
                {error ? (
                  <>
                    <XCircle className="w-5 h-5 text-red-600" />
                    <span className="text-sm font-medium text-red-900">Query Failed</span>
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="text-sm font-medium text-green-900">
                      Query executed successfully in {executionTime}ms
                    </span>
                    <span className="text-sm text-green-700 ml-auto">
                      {results.length} rows returned
                    </span>
                  </>
                )}
              </div>
              {error && <p className="text-sm text-red-700 mt-2">{error}</p>}
            </div>
          )}

          {/* Results */}
          {results.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center justify-between p-4 border-b border-gray-200">
                <div className="flex items-center gap-2">
                  <Table className="w-5 h-5 text-gray-600" />
                  <h3 className="text-sm font-semibold text-gray-900">Query Results</h3>
                  <span className="text-sm text-gray-600">({results.length} rows)</span>
                </div>
                <button className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm flex items-center gap-2">
                  <Download className="w-4 h-4" />
                  Export CSV
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      {Object.keys(results[0]).map((key) => (
                        <th key={key} className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {results.map((row, rowIndex) => (
                      <tr key={rowIndex} className="hover:bg-gray-50">
                        {Object.values(row).map((value: any, colIndex) => (
                          <td key={colIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {typeof value === 'number' ? value.toLocaleString() : value}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Empty State */}
          {results.length === 0 && !isExecuting && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
              <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">No results yet</p>
              <p className="text-sm text-gray-500">Write a query and click "Run Query" to see results</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QueryBuilder;