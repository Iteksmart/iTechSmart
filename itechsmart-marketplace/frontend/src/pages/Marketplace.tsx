import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Star, Download, TrendingUp, Filter, Grid, List } from 'lucide-react';

interface App {
  id: number;
  name: string;
  slug: string;
  tagline: string;
  description: string;
  icon_url: string;
  price: number;
  is_free: boolean;
  average_rating: number;
  total_downloads: number;
  total_reviews: number;
  category_id: number;
  is_featured: boolean;
}

interface Category {
  id: number;
  name: string;
  slug: string;
  icon: string;
}

export default function Marketplace() {
  const [apps, setApps] = useState<App[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('popularity');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [priceFilter, setPriceFilter] = useState<'all' | 'free' | 'paid'>('all');

  useEffect(() => {
    loadApps();
    loadCategories();
  }, [selectedCategory, sortBy, priceFilter]);

  const loadApps = () => {
    // Simulated data
    const mockApps: App[] = [
      {
        id: 1,
        name: 'DataFlow Pro',
        slug: 'dataflow-pro',
        tagline: 'Enterprise Data Integration Platform',
        description: 'Connect, transform, and sync data across your entire organization',
        icon_url: '📊',
        price: 99.99,
        is_free: false,
        average_rating: 4.8,
        total_downloads: 15420,
        total_reviews: 342,
        category_id: 1,
        is_featured: true
      },
      {
        id: 2,
        name: 'Shield Security',
        slug: 'shield-security',
        tagline: 'Advanced Security & Compliance',
        description: 'Protect your infrastructure with real-time threat detection',
        icon_url: '🛡️',
        price: 149.99,
        is_free: false,
        average_rating: 4.9,
        total_downloads: 12850,
        total_reviews: 289,
        category_id: 2,
        is_featured: true
      },
      {
        id: 3,
        name: 'Pulse Analytics',
        slug: 'pulse-analytics',
        tagline: 'Business Intelligence & Analytics',
        description: 'Transform data into actionable insights with powerful visualizations',
        icon_url: '📈',
        price: 79.99,
        is_free: false,
        average_rating: 4.7,
        total_downloads: 18920,
        total_reviews: 456,
        category_id: 3,
        is_featured: true
      },
      {
        id: 4,
        name: 'Connect API Gateway',
        slug: 'connect-api',
        tagline: 'API Management Platform',
        description: 'Manage, secure, and scale your APIs with ease',
        icon_url: '🔌',
        price: 0,
        is_free: true,
        average_rating: 4.6,
        total_downloads: 25340,
        total_reviews: 567,
        category_id: 4,
        is_featured: false
      },
      {
        id: 5,
        name: 'Workflow Automation',
        slug: 'workflow-automation',
        tagline: 'Business Process Automation',
        description: 'Automate repetitive tasks and streamline your workflows',
        icon_url: '⚙️',
        price: 59.99,
        is_free: false,
        average_rating: 4.5,
        total_downloads: 14230,
        total_reviews: 298,
        category_id: 5,
        is_featured: false
      },
      {
        id: 6,
        name: 'Vault Secrets',
        slug: 'vault-secrets',
        tagline: 'Secrets Management',
        description: 'Securely store and manage sensitive credentials',
        icon_url: '🔐',
        price: 0,
        is_free: true,
        average_rating: 4.8,
        total_downloads: 19870,
        total_reviews: 412,
        category_id: 2,
        is_featured: false
      },
      {
        id: 7,
        name: 'Notify Hub',
        slug: 'notify-hub',
        tagline: 'Multi-Channel Notifications',
        description: 'Send notifications across email, SMS, push, and more',
        icon_url: '📢',
        price: 29.99,
        is_free: false,
        average_rating: 4.4,
        total_downloads: 22150,
        total_reviews: 534,
        category_id: 6,
        is_featured: false
      },
      {
        id: 8,
        name: 'Copilot AI',
        slug: 'copilot-ai',
        tagline: 'AI-Powered Assistant',
        description: 'Your intelligent coding companion with multi-model support',
        icon_url: '🤖',
        price: 199.99,
        is_free: false,
        average_rating: 4.9,
        total_downloads: 31240,
        total_reviews: 678,
        category_id: 7,
        is_featured: true
      }
    ];

    let filteredApps = mockApps;

    // Category filter
    if (selectedCategory) {
      filteredApps = filteredApps.filter(app => app.category_id === selectedCategory);
    }

    // Price filter
    if (priceFilter === 'free') {
      filteredApps = filteredApps.filter(app => app.is_free);
    } else if (priceFilter === 'paid') {
      filteredApps = filteredApps.filter(app => !app.is_free);
    }

    // Search filter
    if (searchQuery) {
      filteredApps = filteredApps.filter(app =>
        app.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        app.tagline.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Sort
    if (sortBy === 'popularity') {
      filteredApps.sort((a, b) => b.total_downloads - a.total_downloads);
    } else if (sortBy === 'rating') {
      filteredApps.sort((a, b) => b.average_rating - a.average_rating);
    } else if (sortBy === 'price_low') {
      filteredApps.sort((a, b) => a.price - b.price);
    } else if (sortBy === 'price_high') {
      filteredApps.sort((a, b) => b.price - a.price);
    }

    setApps(filteredApps);
  };

  const loadCategories = () => {
    const mockCategories: Category[] = [
      { id: 1, name: 'Data Integration', slug: 'data-integration', icon: '📊' },
      { id: 2, name: 'Security', slug: 'security', icon: '🛡️' },
      { id: 3, name: 'Analytics', slug: 'analytics', icon: '📈' },
      { id: 4, name: 'API Management', slug: 'api-management', icon: '🔌' },
      { id: 5, name: 'Automation', slug: 'automation', icon: '⚙️' },
      { id: 6, name: 'Communication', slug: 'communication', icon: '📢' },
      { id: 7, name: 'AI & ML', slug: 'ai-ml', icon: '🤖' }
    ];
    setCategories(mockCategories);
  };

  const featuredApps = apps.filter(app => app.is_featured);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 mb-8 text-white">
        <h1 className="text-4xl font-bold mb-4">Welcome to iTechSmart Marketplace</h1>
        <p className="text-xl mb-6">Discover powerful enterprise applications to transform your business</p>
        
        {/* Search Bar */}
        <div className="flex gap-4 max-w-3xl">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search apps..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button className="px-6 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-gray-100 transition">
            Search
          </button>
        </div>
      </div>

      {/* Featured Apps */}
      {featuredApps.length > 0 && !searchQuery && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-blue-600" />
              Featured Apps
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {featuredApps.slice(0, 3).map(app => (
              <Link
                key={app.id}
                to={`/app/${app.id}`}
                className="bg-white rounded-lg shadow-md hover:shadow-xl transition p-6"
              >
                <div className="flex items-start gap-4 mb-4">
                  <div className="text-5xl">{app.icon_url}</div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold mb-1">{app.name}</h3>
                    <p className="text-gray-600 text-sm">{app.tagline}</p>
                  </div>
                </div>
                <p className="text-gray-700 mb-4 line-clamp-2">{app.description}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 text-yellow-500 fill-current" />
                      <span className="font-semibold">{app.average_rating}</span>
                      <span className="text-gray-500 text-sm">({app.total_reviews})</span>
                    </div>
                    <div className="flex items-center gap-1 text-gray-600">
                      <Download className="w-4 h-4" />
                      <span className="text-sm">{(app.total_downloads / 1000).toFixed(1)}k</span>
                    </div>
                  </div>
                  <div className="text-xl font-bold text-blue-600">
                    {app.is_free ? 'Free' : `$${app.price}`}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Categories */}
      <div className="mb-6">
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-4 py-2 rounded-lg whitespace-nowrap transition ${
              selectedCategory === null
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            All Categories
          </button>
          {categories.map(category => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`px-4 py-2 rounded-lg whitespace-nowrap transition flex items-center gap-2 ${
                selectedCategory === category.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              <span>{category.icon}</span>
              <span>{category.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Filters and View Controls */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-600" />
            <select
              value={priceFilter}
              onChange={(e) => setPriceFilter(e.target.value as any)}
              className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Apps</option>
              <option value="free">Free Only</option>
              <option value="paid">Paid Only</option>
            </select>
          </div>
          
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="popularity">Most Popular</option>
            <option value="rating">Highest Rated</option>
            <option value="price_low">Price: Low to High</option>
            <option value="price_high">Price: High to Low</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600'}`}
          >
            <Grid className="w-5 h-5" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600'}`}
          >
            <List className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Apps Grid/List */}
      <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6' : 'space-y-4'}>
        {apps.map(app => (
          <Link
            key={app.id}
            to={`/app/${app.id}`}
            className={`bg-white rounded-lg shadow hover:shadow-lg transition ${
              viewMode === 'list' ? 'flex items-center gap-6 p-4' : 'p-4'
            }`}
          >
            <div className={`text-4xl ${viewMode === 'list' ? '' : 'mb-3'}`}>{app.icon_url}</div>
            <div className="flex-1">
              <h3 className="font-bold text-lg mb-1">{app.name}</h3>
              <p className="text-gray-600 text-sm mb-3 line-clamp-2">{app.tagline}</p>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 text-yellow-500 fill-current" />
                  <span className="text-sm font-semibold">{app.average_rating}</span>
                </div>
                <div className="font-bold text-blue-600">
                  {app.is_free ? 'Free' : `$${app.price}`}
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {apps.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No apps found matching your criteria</p>
        </div>
      )}
    </div>
  );
}