import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, TestTube, CheckCircle, XCircle } from 'lucide-react'
import { connectionsAPI } from '../lib/api'

export default function Connections() {
  const [showAddModal, setShowAddModal] = useState(false)
  const queryClient = useQueryClient()

  const { data: connections, isLoading } = useQuery({
    queryKey: ['connections'],
    queryFn: () => connectionsAPI.list(),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => connectionsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connections'] })
    },
  })

  const testMutation = useMutation({
    mutationFn: (id: string) => connectionsAPI.test(id),
  })

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this connection?')) {
      await deleteMutation.mutateAsync(id)
    }
  }

  const handleTest = async (id: string) => {
    await testMutation.mutateAsync(id)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500 dark:text-gray-400">Loading connections...</div>
      </div>
    )
  }

  const connectionsList = connections?.data || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            EMR Connections
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Manage connections to Electronic Medical Record systems
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn btn-primary"
        >
          <Plus className="h-5 w-5 mr-2" />
          Add Connection
        </button>
      </div>

      {/* Connections Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {connectionsList.map((connection: any) => (
          <div key={connection.id} className="card p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    {connection.id}
                  </h3>
                  <span
                    className={`ml-3 badge ${
                      connection.active ? 'badge-success' : 'badge-danger'
                    }`}
                  >
                    {connection.active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400 capitalize">
                  {connection.emr_type}
                </p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleTest(connection.id)}
                  className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
                  title="Test Connection"
                >
                  <TestTube className="h-5 w-5" />
                </button>
                <button
                  onClick={() => handleDelete(connection.id)}
                  className="text-danger-600 hover:text-danger-700 dark:text-danger-400 dark:hover:text-danger-300"
                  title="Delete Connection"
                >
                  <Trash2 className="h-5 w-5" />
                </button>
              </div>
            </div>

            <div className="mt-4 space-y-2">
              <div className="flex items-center text-sm">
                {connection.active ? (
                  <CheckCircle className="h-4 w-4 text-success-500 mr-2" />
                ) : (
                  <XCircle className="h-4 w-4 text-danger-500 mr-2" />
                )}
                <span className="text-gray-700 dark:text-gray-300">
                  Status: {connection.active ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>
        ))}

        {connectionsList.length === 0 && (
          <div className="col-span-2 text-center py-12">
            <p className="text-gray-500 dark:text-gray-400">
              No connections configured. Add your first connection to get started.
            </p>
          </div>
        )}
      </div>

      {/* Add Connection Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4">
            <div
              className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
              onClick={() => setShowAddModal(false)}
            />
            <div className="relative bg-white dark:bg-gray-800 rounded-lg max-w-lg w-full p-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                Add EMR Connection
              </h3>
              <form className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Connection ID
                  </label>
                  <input type="text" className="input" placeholder="epic_main" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    EMR Type
                  </label>
                  <select className="input">
                    <option value="epic">Epic</option>
                    <option value="cerner">Cerner</option>
                    <option value="meditech">Meditech</option>
                    <option value="allscripts">Allscripts</option>
                    <option value="generic_hl7">Generic HL7</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Base URL
                  </label>
                  <input
                    type="text"
                    className="input"
                    placeholder="https://fhir.epic.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Client ID
                  </label>
                  <input type="text" className="input" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Client Secret
                  </label>
                  <input type="password" className="input" />
                </div>
                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary">
                    Add Connection
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}