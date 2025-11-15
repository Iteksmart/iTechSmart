import { useState } from 'react';
import { Lightbulb, Plus, Trash2, Edit, Copy, Star } from 'lucide-react';

interface Prompt {
  id: number;
  name: string;
  description: string;
  template: string;
  category: string;
  usage_count: number;
  is_public: boolean;
}

export default function Prompts() {
  const [prompts, setPrompts] = useState<Prompt[]>([
    {
      id: 1,
      name: 'Code Review',
      description: 'Review code for best practices and improvements',
      template: 'Please review the following code and provide suggestions for improvements:\n\n{code}',
      category: 'Development',
      usage_count: 45,
      is_public: true
    },
    {
      id: 2,
      name: 'Bug Fix Assistant',
      description: 'Help identify and fix bugs in code',
      template: 'I have a bug in my code. Here\'s the error: {error}\n\nCode:\n{code}\n\nPlease help me fix it.',
      category: 'Development',
      usage_count: 32,
      is_public: true
    },
    {
      id: 3,
      name: 'Documentation Writer',
      description: 'Generate documentation for code',
      template: 'Generate comprehensive documentation for the following code:\n\n{code}',
      category: 'Documentation',
      usage_count: 28,
      is_public: false
    }
  ]);

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const categories = ['all', 'Development', 'Documentation', 'Writing', 'Analysis', 'Other'];

  const filteredPrompts = selectedCategory === 'all' 
    ? prompts 
    : prompts.filter(p => p.category === selectedCategory);

  const copyPrompt = (template: string) => {
    navigator.clipboard.writeText(template);
    alert('Prompt copied to clipboard!');
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Prompt Templates</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage and use pre-built prompt templates
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Prompt
          </button>
        </div>
      </div>

      {/* Category Filter */}
      <div className="mt-8 flex space-x-2 overflow-x-auto">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap ${
              selectedCategory === category
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
            }`}
          >
            {category.charAt(0).toUpperCase() + category.slice(1)}
          </button>
        ))}
      </div>

      {/* Prompts Grid */}
      <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {filteredPrompts.map((prompt) => (
          <div key={prompt.id} className="bg-white shadow rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <Lightbulb className="w-5 h-5 text-yellow-500 mr-2" />
                  <h3 className="text-lg font-medium text-gray-900">{prompt.name}</h3>
                </div>
                <div className="flex space-x-2">
                  <button className="text-gray-400 hover:text-gray-600">
                    <Edit className="w-4 h-4" />
                  </button>
                  <button className="text-gray-400 hover:text-red-600">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-4">{prompt.description}</p>

              <div className="bg-gray-50 rounded p-3 mb-4">
                <p className="text-xs font-mono text-gray-700 line-clamp-3">
                  {prompt.template}
                </p>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded text-xs font-medium">
                    {prompt.category}
                  </span>
                  <span>{prompt.usage_count} uses</span>
                </div>
                <button
                  onClick={() => copyPrompt(prompt.template)}
                  className="text-indigo-600 hover:text-indigo-800 flex items-center text-sm font-medium"
                >
                  <Copy className="w-4 h-4 mr-1" />
                  Copy
                </button>
              </div>

              {prompt.is_public && (
                <div className="mt-3 flex items-center text-xs text-gray-500">
                  <Star className="w-3 h-3 mr-1 text-yellow-500" />
                  Public Template
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredPrompts.length === 0 && (
        <div className="mt-8 text-center py-12 bg-white shadow rounded-lg">
          <Lightbulb className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No prompts found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating a new prompt template
          </p>
        </div>
      )}
    </div>
  );
}