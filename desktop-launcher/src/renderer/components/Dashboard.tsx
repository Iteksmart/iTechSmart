import React, { useState, useEffect } from 'react';
import ProductCard from './ProductCard';
import { Search, Filter } from 'lucide-react';

interface DashboardProps {
  license: any;
}

function Dashboard({ license }: DashboardProps) {
  const [products, setProducts] = useState<any[]>([]);
  const [statuses, setStatuses] = useState<Record<string, string>>({});
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProducts();
    loadStatuses();

    // Refresh statuses every 5 seconds
    const interval = setInterval(loadStatuses, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadProducts = async () => {
    try {
      const productsList = await window.electron.getProducts();
      setProducts(productsList);
    } catch (error) {
      console.error('Failed to load products:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStatuses = async () => {
    try {
      const allStatuses = await window.electron.getAllProductStatuses();
      setStatuses(allStatuses);
    } catch (error) {
      console.error('Failed to load statuses:', error);
    }
  };

  const categories = ['all', ...new Set(products.map(p => p.category))];

  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         product.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const runningCount = Object.values(statuses).filter(s => s === 'running').length;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading products...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">Dashboard</h1>
          <p className="text-slate-400 mt-1">
            {runningCount} of {products.length} products running
          </p>
        </div>
        
        {license && (
          <div className="bg-slate-800 px-6 py-3 rounded-lg border border-slate-700">
            <div className="text-sm text-slate-400">License Tier</div>
            <div className="text-xl font-bold text-blue-400">
              {license.tier.toUpperCase()}
            </div>
          </div>
        )}
      </div>

      {/* Search and Filter */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
          <input
            type="text"
            placeholder="Search products..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-400 focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>

        <div className="relative">
          <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="pl-10 pr-8 py-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-blue-500 transition-colors appearance-none cursor-pointer"
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category === 'all' ? 'All Categories' : category}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Products Grid */}
      {filteredProducts.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-slate-400 text-lg">No products found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredProducts.map(product => (
            <ProductCard
              key={product.id}
              product={product}
              status={statuses[product.id] || 'stopped'}
              license={license}
              onStatusChange={loadStatuses}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default Dashboard;