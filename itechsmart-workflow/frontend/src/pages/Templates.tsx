import { useState, useEffect } from 'react';
import { Search, Star, Download, Eye } from 'lucide-react';
import axios from 'axios';

interface Template {
  id: number;
  name: string;
  description: string;
  category: string;
  tags: string[];
  icon: string;
  is_featured: boolean;
  usage_count: number;
  rating: number;
}

const Templates = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');

  useEffect(() => {
    fetchTemplates();
  }, [categoryFilter]);

  const fetchTemplates = async () => {
    try {
      const token = localStorage.getItem('token');
      const params: any = {};
      if (categoryFilter !== 'all') {
        params.category = categoryFilter;
      }
      
      const response = await axios.get('/api/templates', {
        headers: { Authorization: `Bearer ${token}` },
        params
      });
      setTemplates(response.data);
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const categories = ['all', 'sales', 'marketing', 'hr', 'finance', 'operations', 'customer-service'];

  const filteredTemplates = templates.filter(template =>
    template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    template.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-xl">Loading templates...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Workflow Templates</h1>
        <p className="text-gray-600 mt-1">Start with pre-built workflow templates</p>
      </div>

      {/* Search and Filters */}
      <div className="card">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search templates..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-10"
              />
            </div>
          </div>
        </div>

        {/* Category Filters */}
        <div className="flex flex-wrap gap-2 mt-4">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setCategoryFilter(category)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                categoryFilter === category
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {category === 'all' ? 'All' : category.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Templates Grid */}
      {filteredTemplates.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-600 text-lg">No templates found</p>
          <p className="text-gray-500 mt-2">Try adjusting your search or filters</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTemplates.map((template) => (
            <div key={template.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <span className="text-2xl">{template.icon || '📋'}</span>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800">
                      {template.name}
                    </h3>
                    {template.is_featured && (
                      <span className="inline-flex items-center space-x-1 text-xs text-yellow-600">
                        <Star size={12} fill="currentColor" />
                        <span>Featured</span>
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                {template.description}
              </p>

              <div className="flex items-center space-x-2 mb-4">
                <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                  {template.category}
                </span>
              </div>

              {template.tags && template.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {template.tags.slice(0, 3).map((tag, index) => (
                    <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <span>{template.usage_count} uses</span>
                  <span className="flex items-center space-x-1">
                    <Star size={14} fill="currentColor" className="text-yellow-500" />
                    <span>{template.rating}/5</span>
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    className="p-2 hover:bg-blue-100 rounded-lg transition-colors"
                    title="Preview"
                  >
                    <Eye size={18} className="text-blue-600" />
                  </button>
                  <button
                    className="p-2 hover:bg-green-100 rounded-lg transition-colors"
                    title="Use Template"
                  >
                    <Download size={18} className="text-green-600" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Templates;