import React, { useState } from 'react';
import { Plus, Play, Pause, Trash2, Edit, CheckCircle, XCircle, Clock } from 'lucide-react';

const Pipelines: React.FC = () => {
  const [pipelines] = useState([
    {
      id: 'pipeline-001',
      name: 'Customer Data Sync',
      source: 'PostgreSQL',
      destination: 'Data Lake',
      status: 'running',
      lastRun: '2024-11-12T10:00:00Z',
      successRate: 99.5,
      recordsProcessed: 1000000
    },
    {
      id: 'pipeline-002',
      name: 'HL7 Healthcare Data',
      source: 'HL7 FHIR',
      destination: 'Analytics DB',
      status: 'completed',
      lastRun: '2024-11-12T10:30:00Z',
      successRate: 98.8,
      recordsProcessed: 500000
    },
    {
      id: 'pipeline-003',
      name: 'Sales Analytics',
      source: 'Salesforce',
      destination: 'Snowflake',
      status: 'paused',
      lastRun: '2024-11-12T09:00:00Z',
      successRate: 97.2,
      recordsProcessed: 750000
    },
    {
      id: 'pipeline-004',
      name: 'Financial Reports',
      source: 'MySQL',
      destination: 'S3',
      status: 'failed',
      lastRun: '2024-11-12T08:00:00Z',
      successRate: 95.5,
      recordsProcessed: 250000
    }
  ]);

  const getStatusBadge = (status: string) => {
    const badges = {
      running: {
        icon: Clock,
        className: 'bg-blue-100 text-blue-800',
        label: 'Running'
      },
      completed: {
        icon: CheckCircle,
        className: 'bg-green-100 text-green-800',
        label: 'Completed'
      },
      paused: {
        icon: Pause,
        className: 'bg-yellow-100 text-yellow-800',
        label: 'Paused'
      },
      failed: {
        icon: XCircle,
        className: 'bg-red-100 text-red-800',
        label: 'Failed'
      }
    };

    const badge = badges[status as keyof typeof badges];
    const Icon = badge.icon;

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${badge.className}`}>
        <Icon className="h-3 w-3 mr-1" />
        {badge.label}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Pipelines</h1>
          <p className="mt-2 text-sm text-gray-600">
            Manage your data pipelines and ETL workflows
          </p>
        </div>
        <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
          <Plus className="h-4 w-4 mr-2" />
          Create Pipeline
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="flex space-x-4">
          <select className="block w-48 pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md">
            <option>All Status</option>
            <option>Running</option>
            <option>Completed</option>
            <option>Paused</option>
            <option>Failed</option>
          </select>
          <select className="block w-48 pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md">
            <option>All Sources</option>
            <option>PostgreSQL</option>
            <option>MySQL</option>
            <option>MongoDB</option>
            <option>Salesforce</option>
          </select>
          <input
            type="text"
            placeholder="Search pipelines..."
            className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
          />
        </div>
      </div>

      {/* Pipelines Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Pipeline
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Source → Destination
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Success Rate
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Records
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {pipelines.map((pipeline) => (
              <tr key={pipeline.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {pipeline.name}
                  </div>
                  <div className="text-sm text-gray-500">{pipeline.id}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {pipeline.source} → {pipeline.destination}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(pipeline.status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="text-sm text-gray-900">
                      {pipeline.successRate}%
                    </div>
                    <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full"
                        style={{ width: `${pipeline.successRate}%` }}
                      />
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {(pipeline.recordsProcessed / 1000000).toFixed(1)}M
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex space-x-2">
                    <button className="text-blue-600 hover:text-blue-900">
                      <Play className="h-4 w-4" />
                    </button>
                    <button className="text-gray-600 hover:text-gray-900">
                      <Edit className="h-4 w-4" />
                    </button>
                    <button className="text-red-600 hover:text-red-900">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Pipelines;