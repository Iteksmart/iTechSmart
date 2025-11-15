import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Download, Star, Calendar, RefreshCw, Trash2, ExternalLink } from 'lucide-react';

interface Purchase {
  id: number;
  app: {
    id: number;
    name: string;
    icon_url: string;
    version: string;
    developer: string;
  };
  purchase_date: string;
  amount: number;
  status: string;
}

export default function MyApps() {
  const [purchases, setPurchases] = useState<Purchase[]>([]);
  const [activeTab, setActiveTab] = useState<'purchased' | 'wishlist'>('purchased');

  useEffect(() => {
    loadPurchases();
  }, []);

  const loadPurchases = () => {
    const mockPurchases: Purchase[] = [
      {
        id: 1,
        app: {
          id: 1,
          name: 'DataFlow Pro',
          icon_url: '📊',
          version: '2.5.0',
          developer: 'iTechSmart Inc.'
        },
        purchase_date: '2024-01-15',
        amount: 99.99,
        status: 'completed'
      },
      {
        id: 2,
        app: {
          id: 2,
          name: 'Shield Security',
          icon_url: '🛡️',
          version: '3.2.1',
          developer: 'iTechSmart Inc.'
        },
        purchase_date: '2024-01-10',
        amount: 149.99,
        status: 'completed'
      },
      {
        id: 3,
        app: {
          id: 3,
          name: 'Pulse Analytics',
          icon_url: '📈',
          version: '1.8.0',
          developer: 'iTechSmart Inc.'
        },
        purchase_date: '2024-01-05',
        amount: 79.99,
        status: 'completed'
      },
      {
        id: 4,
        app: {
          id: 4,
          name: 'Connect API Gateway',
          icon_url: '🔌',
          version: '2.0.0',
          developer: 'iTechSmart Inc.'
        },
        purchase_date: '2023-12-20',
        amount: 0,
        status: 'completed'
      }
    ];
    setPurchases(mockPurchases);
  };

  const wishlistApps = [
    {
      id: 5,
      name: 'Workflow Automation',
      icon_url: '⚙️',
      tagline: 'Business Process Automation',
      price: 59.99,
      rating: 4.5,
      reviews: 298
    },
    {
      id: 6,
      name: 'Vault Secrets',
      icon_url: '🔐',
      tagline: 'Secrets Management',
      price: 0,
      rating: 4.8,
      reviews: 412
    },
    {
      id: 7,
      name: 'Copilot AI',
      icon_url: '🤖',
      tagline: 'AI-Powered Assistant',
      price: 199.99,
      rating: 4.9,
      reviews: 678
    }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">My Apps</h1>
        <p className="text-gray-600">Manage your purchased apps and wishlist</p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="border-b">
          <div className="flex">
            <button
              onClick={() => setActiveTab('purchased')}
              className={`px-6 py-4 font-semibold transition ${
                activeTab === 'purchased'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              Purchased Apps ({purchases.length})
            </button>
            <button
              onClick={() => setActiveTab('wishlist')}
              className={`px-6 py-4 font-semibold transition ${
                activeTab === 'wishlist'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              Wishlist ({wishlistApps.length})
            </button>
          </div>
        </div>

        <div className="p-6">
          {activeTab === 'purchased' && (
            <div>
              {purchases.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📦</div>
                  <h3 className="text-xl font-semibold mb-2">No purchased apps yet</h3>
                  <p className="text-gray-600 mb-6">Browse the marketplace to find apps for your needs</p>
                  <Link
                    to="/"
                    className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
                  >
                    Browse Marketplace
                  </Link>
                </div>
              ) : (
                <div className="space-y-4">
                  {purchases.map(purchase => (
                    <div key={purchase.id} className="border rounded-lg p-6 hover:shadow-md transition">
                      <div className="flex items-start gap-6">
                        <div className="text-6xl">{purchase.app.icon_url}</div>
                        
                        <div className="flex-1">
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <h3 className="text-xl font-bold mb-1">{purchase.app.name}</h3>
                              <p className="text-gray-600 text-sm">by {purchase.app.developer}</p>
                            </div>
                            <div className="text-right">
                              <div className="text-sm text-gray-600 mb-1">Version {purchase.app.version}</div>
                              <div className="text-sm text-gray-600">
                                Purchased {new Date(purchase.purchase_date).toLocaleDateString()}
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center gap-4 mb-4">
                            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-semibold">
                              Active
                            </span>
                            {purchase.amount > 0 && (
                              <span className="text-gray-600 text-sm">
                                Paid ${purchase.amount}
                              </span>
                            )}
                            {purchase.amount === 0 && (
                              <span className="text-gray-600 text-sm">Free</span>
                            )}
                          </div>

                          <div className="flex items-center gap-3">
                            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition flex items-center gap-2">
                              <Download className="w-4 h-4" />
                              Download
                            </button>
                            
                            <Link
                              to={`/app/${purchase.app.id}`}
                              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition flex items-center gap-2"
                            >
                              <ExternalLink className="w-4 h-4" />
                              View Details
                            </Link>
                            
                            <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition flex items-center gap-2">
                              <RefreshCw className="w-4 h-4" />
                              Check Updates
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'wishlist' && (
            <div>
              {wishlistApps.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">❤️</div>
                  <h3 className="text-xl font-semibold mb-2">Your wishlist is empty</h3>
                  <p className="text-gray-600 mb-6">Add apps to your wishlist to keep track of them</p>
                  <Link
                    to="/"
                    className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
                  >
                    Browse Marketplace
                  </Link>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {wishlistApps.map(app => (
                    <div key={app.id} className="bg-white border rounded-lg p-6 hover:shadow-md transition">
                      <div className="flex items-start justify-between mb-4">
                        <div className="text-5xl">{app.icon_url}</div>
                        <button className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition">
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                      
                      <h3 className="text-lg font-bold mb-1">{app.name}</h3>
                      <p className="text-gray-600 text-sm mb-4">{app.tagline}</p>
                      
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-1">
                          <Star className="w-4 h-4 text-yellow-500 fill-current" />
                          <span className="text-sm font-semibold">{app.rating}</span>
                          <span className="text-gray-500 text-sm">({app.reviews})</span>
                        </div>
                        <div className="text-lg font-bold text-blue-600">
                          {app.price === 0 ? 'Free' : `$${app.price}`}
                        </div>
                      </div>
                      
                      <div className="flex gap-2">
                        <Link
                          to={`/app/${app.id}`}
                          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition text-center"
                        >
                          View App
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Purchase History Summary */}
      {activeTab === 'purchased' && purchases.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Purchase Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="text-3xl font-bold text-blue-600 mb-1">{purchases.length}</div>
              <div className="text-gray-600">Total Apps</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-green-600 mb-1">
                ${purchases.reduce((sum, p) => sum + p.amount, 0).toFixed(2)}
              </div>
              <div className="text-gray-600">Total Spent</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-purple-600 mb-1">
                {purchases.filter(p => p.amount === 0).length}
              </div>
              <div className="text-gray-600">Free Apps</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}