import { useState } from 'react'
import { Search, User } from 'lucide-react'

export default function Patients() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedConnection, setSelectedConnection] = useState('')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Patient Search
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Search for patients across connected EMR systems
        </p>
      </div>

      {/* Search Form */}
      <div className="card p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              EMR Connection
            </label>
            <select
              className="input"
              value={selectedConnection}
              onChange={(e) => setSelectedConnection(e.target.value)}
            >
              <option value="">Select connection...</option>
              <option value="epic_main">Epic Main</option>
              <option value="cerner_main">Cerner Main</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Search
            </label>
            <div className="relative">
              <input
                type="text"
                className="input pl-10"
                placeholder="Patient name, MRN, or DOB..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
            </div>
          </div>
        </div>
        <div className="mt-4">
          <button className="btn btn-primary">
            <Search className="h-5 w-5 mr-2" />
            Search Patients
          </button>
        </div>
      </div>

      {/* Results */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          Search Results
        </h3>
        <div className="text-center py-12">
          <User className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            No patients found. Try searching with different criteria.
          </p>
        </div>
      </div>
    </div>
  )
}