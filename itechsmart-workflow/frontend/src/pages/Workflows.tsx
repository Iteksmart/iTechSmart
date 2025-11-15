import { useState, useEffect } from 'react';
import { 
  Plus, 
  Search, 
  Filter, 
  Play, 
  Edit, 
  Trash2, 
  Copy,
  MoreVertical,
  CheckCircle,
  XCircle,
  Clock,
  Pause
} from 'lucide-react';
import axios from 'axios';

interface Workflow {
  id: number;
  name: string;
  description: string;
  status: string;
  category: string;
  tags: string[];
  execution_count: number;
  success_count: number;
  failure_count: number;
  created_at: string;
  updated_at: string;
}

const Workflows = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchWorkflows();
  }, [statusFilter]);

  const fetchWorkflows = async () => {
    try {
      const token = localStorage.getItem('token');
      const params: any = {};
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      
      const response = await axios.get('/api/workflows', {
        headers: { Authorization: `Bearer ${token}` },
        params
      });
      setWorkflows(response.data);
    } catch (error) {
      console.error('Failed to fetch workflows:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExecuteWorkflow = async (workflowId: number) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post('/api/executions', 
        { workflow_id: workflowId, trigger_type: 'manual' },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Workflow execution started!');
      fetchWorkflows();
    } catch (error) {
      console.error('Failed to execute workflow:', error);
      alert('Failed to execute workflow');
    }
  };

  const handleDeleteWorkflow = async (workflowId: number) => {
    if (!confirm('Are you sure you want to delete this workflow?')) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`/api/workflows/${workflowId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchWorkflows();
    } catch (error) {
      console.error('Failed to delete workflow:', error);
      alert('Failed to delete workflow');
    }
  };

  const filteredWorkflows = workflows.filter(workflow =>
    workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    workflow.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'draft': return 'bg-yellow-100 text-yellow-800';
      case 'paused': return 'bg-gray-100 text-gray-800';
      case 'archived': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle size={16} />;
      case 'draft': return <Edit size={16} />;
      case 'paused': return <Pause size={16} />;
      case 'archived': return <XCircle size={16} />;
      default: return <Clock size={16} />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-xl">Loading workflows...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Workflows</h1>
          <p className="text-gray-600 mt-1">Manage your automation workflows</p>
        </div>
        <button 
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus size={20} />
          <span>Create Workflow</span>
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search workflows..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-10"
              />
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter size={20} className="text-gray-600" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="input"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="draft">Draft</option>
                <option value="paused">Paused</option>
                <option value="archived">Archived</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Workflows Grid */}
      {filteredWorkflows.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-600 text-lg">No workflows found</p>
          <p className="text-gray-500 mt-2">Create your first workflow to get started</p>
          <button 
            onClick={() => setShowCreateModal(true)}
            className="btn-primary mt-4"
          >
            Create Workflow
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredWorkflows.map((workflow) => (
            <div key={workflow.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-800 mb-1">
                    {workflow.name}
                  </h3>
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {workflow.description || 'No description'}
                  </p>
                </div>
                <button className="p-2 hover:bg-gray-100 rounded-lg">
                  <MoreVertical size={20} className="text-gray-600" />
                </button>
              </div>

              <div className="flex items-center space-x-2 mb-4">
                <span className={`px-3 py-1 rounded-full text-xs font-medium flex items-center space-x-1 ${getStatusColor(workflow.status)}`}>
                  {getStatusIcon(workflow.status)}
                  <span className="capitalize">{workflow.status}</span>
                </span>
                {workflow.category && (
                  <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {workflow.category}
                  </span>
                )}
              </div>

              {workflow.tags && workflow.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {workflow.tags.slice(0, 3).map((tag, index) => (
                    <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                      {tag}
                    </span>
                  ))}
                  {workflow.tags.length > 3 && (
                    <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                      +{workflow.tags.length - 3}
                    </span>
                  )}
                </div>
              )}

              <div className="grid grid-cols-3 gap-4 mb-4 py-4 border-t border-b border-gray-200">
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-800">{workflow.execution_count}</p>
                  <p className="text-xs text-gray-600">Executions</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">{workflow.success_count}</p>
                  <p className="text-xs text-gray-600">Success</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-600">{workflow.failure_count}</p>
                  <p className="text-xs text-gray-600">Failed</p>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleExecuteWorkflow(workflow.id)}
                    className="p-2 hover:bg-green-100 rounded-lg transition-colors"
                    title="Execute"
                    disabled={workflow.status !== 'active'}
                  >
                    <Play size={18} className={workflow.status === 'active' ? 'text-green-600' : 'text-gray-400'} />
                  </button>
                  <button
                    className="p-2 hover:bg-blue-100 rounded-lg transition-colors"
                    title="Edit"
                  >
                    <Edit size={18} className="text-blue-600" />
                  </button>
                  <button
                    className="p-2 hover:bg-purple-100 rounded-lg transition-colors"
                    title="Duplicate"
                  >
                    <Copy size={18} className="text-purple-600" />
                  </button>
                </div>
                <button
                  onClick={() => handleDeleteWorkflow(workflow.id)}
                  className="p-2 hover:bg-red-100 rounded-lg transition-colors"
                  title="Delete"
                >
                  <Trash2 size={18} className="text-red-600" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal (placeholder) */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Create New Workflow</h2>
            <p className="text-gray-600 mb-6">
              Workflow builder interface would go here. This is a placeholder for the full workflow creation UI.
            </p>
            <div className="flex justify-end space-x-4">
              <button
                onClick={() => setShowCreateModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button className="btn-primary">
                Create Workflow
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Workflows;