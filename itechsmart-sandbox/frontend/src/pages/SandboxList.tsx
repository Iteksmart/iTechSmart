import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, Filter } from 'lucide-react';
import { sandboxApi } from '../services/api';
import type { Sandbox } from '../types';
import SandboxCard from '../components/SandboxCard';
import { parseErrorMessage } from '../utils/helpers';

const SandboxList: React.FC = () => {
  const navigate = useNavigate();
  const [sandboxes, setSandboxes] = useState<Sandbox[]>([]);
  const [filteredSandboxes, setFilteredSandboxes] = useState<Sandbox[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  useEffect(() => {
    loadSandboxes();
  }, []);

  useEffect(() => {
    filterSandboxes();
  }, [sandboxes, searchQuery, statusFilter]);

  const loadSandboxes = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await sandboxApi.list();
      setSandboxes(data);
    } catch (err) {
      setError(parseErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const filterSandboxes = () => {
    let filtered = [...sandboxes];

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(
        (s) =>
          s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          s.image.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter((s) => s.status === statusFilter);
    }

    setFilteredSandboxes(filtered);
  };

  const handleStart = async (id: string) => {
    try {
      await sandboxApi.start(id);
      await loadSandboxes();
    } catch (err) {
      alert(parseErrorMessage(err));
    }
  };

  const handleStop = async (id: string) => {
    try {
      await sandboxApi.stop(id);
      await loadSandboxes();
    } catch (err) {
      alert(parseErrorMessage(err));
    }
  };

  const handleTerminate = async (id: string) => {
    try {
      await sandboxApi.terminate(id);
      await loadSandboxes();
    } catch (err) {
      alert(parseErrorMessage(err));
    }
  };

  return (
    <div>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 'var(--spacing-xl)',
        }}
      >
        <div>
          <h1 style={{ margin: 0, fontSize: '32px', fontWeight: 'bold' }}>
            Sandboxes
          </h1>
          <p
            style={{
              margin: '8px 0 0 0',
              fontSize: '16px',
              color: 'var(--text-secondary)',
            }}
          >
            Manage all your sandbox environments
          </p>
        </div>
        <button
          className="btn btn-primary btn-lg"
          onClick={() => navigate('/sandboxes/new')}
        >
          <Plus size={20} />
          Create Sandbox
        </button>
      </div>

      {/* Filters */}
      <div
        className="card"
        style={{
          marginBottom: 'var(--spacing-lg)',
          display: 'flex',
          gap: 'var(--spacing-md)',
          alignItems: 'center',
        }}
      >
        {/* Search */}
        <div style={{ flex: 1, position: 'relative' }}>
          <Search
            size={20}
            style={{
              position: 'absolute',
              left: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--text-tertiary)',
            }}
          />
          <input
            type="text"
            className="form-input"
            placeholder="Search sandboxes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ paddingLeft: '40px' }}
          />
        </div>

        {/* Status Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Filter size={20} color="var(--text-secondary)" />
          <select
            className="form-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ minWidth: '150px' }}
          >
            <option value="all">All Status</option>
            <option value="running">Running</option>
            <option value="stopped">Stopped</option>
            <option value="creating">Creating</option>
            <option value="terminated">Terminated</option>
            <option value="error">Error</option>
          </select>
        </div>
      </div>

      {/* Results Count */}
      <div style={{ marginBottom: 'var(--spacing-md)' }}>
        <p style={{ margin: 0, color: 'var(--text-secondary)' }}>
          Showing {filteredSandboxes.length} of {sandboxes.length} sandboxes
        </p>
      </div>

      {/* Sandboxes Grid */}
      {loading && (
        <div style={{ textAlign: 'center', padding: 'var(--spacing-2xl)' }}>
          <div className="spinner" style={{ width: '40px', height: '40px' }} />
          <p style={{ marginTop: 'var(--spacing-md)', color: 'var(--text-secondary)' }}>
            Loading sandboxes...
          </p>
        </div>
      )}

      {error && (
        <div
          className="card"
          style={{
            background: '#fee2e2',
            border: '1px solid #fecaca',
            color: '#991b1b',
          }}
        >
          <p style={{ margin: 0 }}>Error: {error}</p>
        </div>
      )}

      {!loading && !error && filteredSandboxes.length === 0 && (
        <div className="card" style={{ textAlign: 'center', padding: 'var(--spacing-2xl)' }}>
          <h3 style={{ margin: '0 0 var(--spacing-sm) 0' }}>No sandboxes found</h3>
          <p style={{ margin: 0, color: 'var(--text-secondary)' }}>
            {searchQuery || statusFilter !== 'all'
              ? 'Try adjusting your filters'
              : 'Create your first sandbox to get started'}
          </p>
        </div>
      )}

      {!loading && !error && filteredSandboxes.length > 0 && (
        <div className="grid grid-cols-3">
          {filteredSandboxes.map((sandbox) => (
            <SandboxCard
              key={sandbox.id}
              sandbox={sandbox}
              onStart={handleStart}
              onStop={handleStop}
              onTerminate={handleTerminate}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default SandboxList;