import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Star, Download, Heart, Share2, ShoppingCart, Check, AlertCircle } from 'lucide-react';

interface App {
  id: number;
  name: string;
  tagline: string;
  description: string;
  long_description: string;
  icon_url: string;
  banner_url: string;
  screenshots: string[];
  price: number;
  is_free: boolean;
  average_rating: number;
  total_downloads: number;
  total_reviews: number;
  version: string;
  size_mb: number;
  features: string[];
  developer: {
    company_name: string;
    support_email: string;
  };
}

interface Review {
  id: number;
  user: {
    username: string;
    avatar_url: string;
  };
  rating: number;
  title: string;
  comment: string;
  created_at: string;
  is_verified_purchase: boolean;
}

export default function AppDetail() {
  const { id } = useParams();
  const [app, setApp] = useState<App | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [isPurchased, setIsPurchased] = useState(false);
  const [isInWishlist, setIsInWishlist] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'reviews' | 'details'>('overview');

  useEffect(() => {
    loadApp();
    loadReviews();
  }, [id]);

  const loadApp = () => {
    // Simulated data
    const mockApp: App = {
      id: parseInt(id || '1'),
      name: 'DataFlow Pro',
      tagline: 'Enterprise Data Integration Platform',
      description: 'Connect, transform, and sync data across your entire organization with powerful ETL capabilities.',
      long_description: `DataFlow Pro is a comprehensive data integration platform designed for enterprise needs. 
      
      With support for 100+ data sources including databases, cloud services, APIs, and file systems, DataFlow Pro makes it easy to connect all your data sources in one place.
      
      Key capabilities include:
      - Real-time data synchronization
      - Advanced data transformation and cleansing
      - Scheduled and event-driven pipelines
      - Data quality validation
      - Comprehensive monitoring and alerting
      
      Built on modern architecture with high availability and scalability in mind, DataFlow Pro can handle data volumes from gigabytes to petabytes.`,
      icon_url: '📊',
      banner_url: '🎨',
      screenshots: ['📸', '📸', '📸', '📸'],
      price: 99.99,
      is_free: false,
      average_rating: 4.8,
      total_downloads: 15420,
      total_reviews: 342,
      version: '2.5.0',
      size_mb: 125.5,
      features: [
        '100+ data source connectors',
        'Real-time data streaming',
        'Advanced ETL transformations',
        'Data quality validation',
        'Scheduled pipelines',
        'Monitoring dashboard',
        'API access',
        'Team collaboration'
      ],
      developer: {
        company_name: 'iTechSmart Inc.',
        support_email: 'support@itechsmart.com'
      }
    };
    setApp(mockApp);
  };

  const loadReviews = () => {
    const mockReviews: Review[] = [
      {
        id: 1,
        user: { username: 'john_doe', avatar_url: '👤' },
        rating: 5,
        title: 'Excellent data integration tool!',
        comment: 'This has transformed how we handle data across our organization. The connectors are robust and the UI is intuitive.',
        created_at: '2024-01-15',
        is_verified_purchase: true
      },
      {
        id: 2,
        user: { username: 'sarah_smith', avatar_url: '👤' },
        rating: 4,
        title: 'Great features, minor learning curve',
        comment: 'Very powerful platform with lots of features. Took a bit to learn but worth it. Support team is responsive.',
        created_at: '2024-01-10',
        is_verified_purchase: true
      },
      {
        id: 3,
        user: { username: 'mike_johnson', avatar_url: '👤' },
        rating: 5,
        title: 'Best investment for our data team',
        comment: 'We evaluated several solutions and DataFlow Pro came out on top. The real-time streaming is a game changer.',
        created_at: '2024-01-05',
        is_verified_purchase: true
      }
    ];
    setReviews(mockReviews);
  };

  const handlePurchase = () => {
    alert('Purchase functionality would be implemented here with Stripe integration');
    setIsPurchased(true);
  };

  const handleWishlist = () => {
    setIsInWishlist(!isInWishlist);
  };

  if (!app) {
    return <div className="max-w-7xl mx-auto px-4 py-8">Loading...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
        <div className="flex items-start gap-6">
          <div className="text-8xl">{app.icon_url}</div>
          <div className="flex-1">
            <h1 className="text-4xl font-bold mb-2">{app.name}</h1>
            <p className="text-xl text-gray-600 mb-4">{app.tagline}</p>
            
            <div className="flex items-center gap-6 mb-4">
              <div className="flex items-center gap-2">
                <div className="flex">
                  {[1, 2, 3, 4, 5].map(star => (
                    <Star
                      key={star}
                      className={`w-5 h-5 ${
                        star <= Math.round(app.average_rating)
                          ? 'text-yellow-500 fill-current'
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <span className="font-semibold">{app.average_rating}</span>
                <span className="text-gray-500">({app.total_reviews} reviews)</span>
              </div>
              
              <div className="flex items-center gap-2 text-gray-600">
                <Download className="w-5 h-5" />
                <span>{app.total_downloads.toLocaleString()} downloads</span>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-3xl font-bold text-blue-600">
                {app.is_free ? 'Free' : `$${app.price}`}
              </div>
              
              {isPurchased ? (
                <button className="px-6 py-3 bg-green-600 text-white rounded-lg font-semibold flex items-center gap-2">
                  <Check className="w-5 h-5" />
                  Purchased
                </button>
              ) : (
                <button
                  onClick={handlePurchase}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition flex items-center gap-2"
                >
                  <ShoppingCart className="w-5 h-5" />
                  {app.is_free ? 'Get App' : 'Purchase'}
                </button>
              )}
              
              <button
                onClick={handleWishlist}
                className={`p-3 rounded-lg border-2 transition ${
                  isInWishlist
                    ? 'border-red-500 text-red-500 bg-red-50'
                    : 'border-gray-300 text-gray-600 hover:border-red-500 hover:text-red-500'
                }`}
              >
                <Heart className={`w-5 h-5 ${isInWishlist ? 'fill-current' : ''}`} />
              </button>
              
              <button className="p-3 rounded-lg border-2 border-gray-300 text-gray-600 hover:border-blue-500 hover:text-blue-500 transition">
                <Share2 className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-lg mb-6">
        <div className="border-b">
          <div className="flex">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-6 py-4 font-semibold transition ${
                activeTab === 'overview'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('reviews')}
              className={`px-6 py-4 font-semibold transition ${
                activeTab === 'reviews'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              Reviews ({app.total_reviews})
            </button>
            <button
              onClick={() => setActiveTab('details')}
              className={`px-6 py-4 font-semibold transition ${
                activeTab === 'details'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              Details
            </button>
          </div>
        </div>

        <div className="p-8">
          {activeTab === 'overview' && (
            <div>
              <div className="mb-8">
                <h2 className="text-2xl font-bold mb-4">About this app</h2>
                <div className="prose max-w-none text-gray-700 whitespace-pre-line">
                  {app.long_description}
                </div>
              </div>

              <div className="mb-8">
                <h2 className="text-2xl font-bold mb-4">Screenshots</h2>
                <div className="grid grid-cols-4 gap-4">
                  {app.screenshots.map((screenshot, index) => (
                    <div key={index} className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center text-6xl">
                      {screenshot}
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h2 className="text-2xl font-bold mb-4">Key Features</h2>
                <div className="grid grid-cols-2 gap-4">
                  {app.features.map((feature, index) => (
                    <div key={index} className="flex items-start gap-3">
                      <Check className="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'reviews' && (
            <div>
              <div className="mb-6">
                <h2 className="text-2xl font-bold mb-4">Customer Reviews</h2>
                <div className="flex items-center gap-8 mb-6">
                  <div className="text-center">
                    <div className="text-5xl font-bold text-blue-600 mb-2">{app.average_rating}</div>
                    <div className="flex justify-center mb-2">
                      {[1, 2, 3, 4, 5].map(star => (
                        <Star
                          key={star}
                          className={`w-5 h-5 ${
                            star <= Math.round(app.average_rating)
                              ? 'text-yellow-500 fill-current'
                              : 'text-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                    <div className="text-gray-600">{app.total_reviews} reviews</div>
                  </div>
                  
                  <div className="flex-1">
                    {[5, 4, 3, 2, 1].map(rating => (
                      <div key={rating} className="flex items-center gap-3 mb-2">
                        <span className="w-12 text-sm text-gray-600">{rating} star</span>
                        <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-yellow-500"
                            style={{ width: `${rating === 5 ? 70 : rating === 4 ? 20 : 10}%` }}
                          />
                        </div>
                        <span className="w-12 text-sm text-gray-600 text-right">
                          {rating === 5 ? 70 : rating === 4 ? 20 : 10}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                {reviews.map(review => (
                  <div key={review.id} className="border-b pb-6">
                    <div className="flex items-start gap-4">
                      <div className="text-4xl">{review.user.avatar_url}</div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="font-semibold">{review.user.username}</span>
                          {review.is_verified_purchase && (
                            <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full flex items-center gap-1">
                              <Check className="w-3 h-3" />
                              Verified Purchase
                            </span>
                          )}
                          <span className="text-gray-500 text-sm">{review.created_at}</span>
                        </div>
                        <div className="flex mb-2">
                          {[1, 2, 3, 4, 5].map(star => (
                            <Star
                              key={star}
                              className={`w-4 h-4 ${
                                star <= review.rating
                                  ? 'text-yellow-500 fill-current'
                                  : 'text-gray-300'
                              }`}
                            />
                          ))}
                        </div>
                        <h4 className="font-semibold mb-2">{review.title}</h4>
                        <p className="text-gray-700">{review.comment}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'details' && (
            <div className="grid grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-bold mb-4">App Information</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Version</span>
                    <span className="font-semibold">{app.version}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Size</span>
                    <span className="font-semibold">{app.size_mb} MB</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Downloads</span>
                    <span className="font-semibold">{app.total_downloads.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Rating</span>
                    <span className="font-semibold">{app.average_rating} / 5.0</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-bold mb-4">Developer Information</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Company</span>
                    <span className="font-semibold">{app.developer.company_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Support</span>
                    <a href={`mailto:${app.developer.support_email}`} className="text-blue-600 hover:underline">
                      {app.developer.support_email}
                    </a>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}