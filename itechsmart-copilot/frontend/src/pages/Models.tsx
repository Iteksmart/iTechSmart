import { useState } from 'react';
import { Cpu, Plus, Edit, Trash2, CheckCircle, XCircle } from 'lucide-react';

interface AIModel {
  id: number;
  name: string;
  provider: string;
  model_id: string;
  description: string;
  max_tokens: number;
  temperature: number;
  cost_per_1k_tokens: number;
  is_active: boolean;
  is_default: boolean;
}

export default function Models() {
  const [models, setModels] = useState<AIModel[]>([
    {
      id: 1,
      name: 'GPT-4',
      provider: 'openai',
      model_id: 'gpt-4',
      description: 'Most capable model, best for complex tasks',
      max_tokens: 8192,
      temperature: 0.7,
      cost_per_1k_tokens: 0.03,
      is_active: true,
      is_default: true
    },
    {
      id: 2,
      name: 'GPT-3.5 Turbo',
      provider: 'openai',
      model_id: 'gpt-3.5-turbo',
      description: 'Fast and efficient for most tasks',
      max_tokens: 4096,
      temperature: 0.7,
      cost_per_1k_tokens: 0.002,
      is_active: true,
      is_default: false
    },
    {
      id: 3,
      name: 'Claude 2',
      provider: 'anthropic',
      model_id: 'claude-2',
      description: 'Excellent for long-form content and analysis',
      max_tokens: 100000,
      temperature: 0.7,
      cost_per_1k_tokens: 0.008,
      is_active: true,
      is_default: false
    },
    {
      id: 4,
      name: 'Gemini Pro',
      provider: 'google',
      model_id: 'gemini-pro',
      description: 'Google\'s advanced AI model',
      max_tokens: 32768,
      temperature: 0.7,
      cost_per_1k_tokens: 0.00025,
      is_active: false,
      is_default: false
    }
  ]);

  const [selectedProvider, setSelectedProvider] = useState<string>('all');

  const providers = ['all', 'openai', 'anthropic', 'google', 'cohere'];

  const filteredModels = selectedProvider === 'all' 
    ? models 
    : models.filter(m => m.provider === selectedProvider);

  const getProviderColor = (provider: string) => {
    switch (provider.toLowerCase()) {
      case 'openai': return 'bg-green-100 text-green-800';
      case 'anthropic': return 'bg-purple-100 text-purple-800';
      case 'google': return 'bg-blue-100 text-blue-800';
      case 'cohere': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI Models</h1>
          <p className="mt-2 text-sm text-gray-700">
            Configure and manage AI model settings
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700">
            <Plus className="w-4 h-4 mr-2" />
            Add Model
          </button>
        </div>
      </div>

      {/* Provider Filter */}
      <div className="mt-8 flex space-x-2 overflow-x-auto">
        {providers.map((provider) => (
          <button
            key={provider}
            onClick={() => setSelectedProvider(provider)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap ${
              selectedProvider === provider
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
            }`}
          >
            {provider.charAt(0).toUpperCase() + provider.slice(1)}
          </button>
        ))}
      </div>

      {/* Models Grid */}
      <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {filteredModels.map((model) => (
          <div key={model.id} className="bg-white shadow rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <Cpu className="w-6 h-6 text-indigo-600 mr-2" />
                  <h3 className="text-lg font-medium text-gray-900">{model.name}</h3>
                </div>
                <div className="flex space-x-2">
                  {model.is_active ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : (
                    <XCircle className="w-5 h-5 text-gray-400" />
                  )}
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-4">{model.description}</p>

              <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Provider:</span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getProviderColor(model.provider)}`}>
                    {model.provider.charAt(0).toUpperCase() + model.provider.slice(1)}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Max Tokens:</span>
                  <span className="font-medium text-gray-900">{model.max_tokens.toLocaleString()}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Temperature:</span>
                  <span className="font-medium text-gray-900">{model.temperature}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Cost per 1K:</span>
                  <span className="font-medium text-gray-900">${model.cost_per_1k_tokens.toFixed(4)}</span>
                </div>
              </div>

              {model.is_default && (
                <div className="mb-4 px-3 py-2 bg-indigo-50 border border-indigo-200 rounded text-sm text-indigo-800">
                  ⭐ Default Model
                </div>
              )}

              <div className="flex space-x-2">
                <button className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
                  <Edit className="w-4 h-4 inline mr-1" />
                  Edit
                </button>
                <button className="px-3 py-2 border border-red-300 rounded-md text-sm font-medium text-red-700 hover:bg-red-50">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Model Comparison */}
      <div className="mt-8 bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Model Comparison</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Model</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Max Tokens</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost/1K</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {models.map((model) => (
                <tr key={model.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {model.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getProviderColor(model.provider)}`}>
                      {model.provider}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {model.max_tokens.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${model.cost_per_1k_tokens.toFixed(4)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {model.is_active ? (
                      <span className="px-2 py-1 text-xs font-medium rounded bg-green-100 text-green-800">
                        Active
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-800">
                        Inactive
                      </span>
                    )}
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