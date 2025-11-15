import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Box, Activity, Clock, Zap } from 'lucide-react';
import { sandboxApi } from '../services/api';
import type { Sandbox } from '../types';
import SandboxCard from '../components/SandboxCard';
import { parseErrorMessage } from '../utils/helpers';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [sandboxes, setSandboxes] = useState<Sandbox[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSandboxes();
  }, []);

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

  const stats = {
    total: sandboxes.length,
    running: sandboxes.filter((s) => s.status === 'running').length,
    stopped: sandboxes.filter((s) => s.status === 'stopped').length,
    creating: sandboxes.filter((s) => s.status === 'creating').length,
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
            Dashboard
          </h1>
          <p
            style={{
              margin: '8px 0 0 0',
              fontSize: '16px',
              color: 'var(--text-secondary)',
            }}
          >
            Manage your sandboxes and monitor activity
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

      {/* Stats */}
      <div className="grid grid-cols-4" style={{ marginBottom: 'var(--spacing-xl)' }}>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '48px',
                height: '48px',
                borderRadius: 'var(--border-radius)',
                background: 'rgba(37, 99, 235, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Box size={24} color="var(--primary)" />
            </div>
            <div>
              <p
                style={{
                  margin: 0,
                  fontSize: '14px',
                  color: 'var(--text-secondary)',
                }}
              >
                Total Sandboxes
              </p>
              <p style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>
                {stats.total}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '48px',
                height: '48px',
                borderRadius: 'var(--border-radius)',
                background: 'rgba(16, 185, 129, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Activity size={24} color="var(--success)" />
            </div>
            <div>
              <p
                style={{
                  margin: 0,
                  fontSize: '14px',
                  color: 'var(--text-secondary)',
                }}
              >
                Running
              </p>
              <p style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>
                {stats.running}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '48px',
                height: '48px',
                borderRadius: 'var(--border-radius)',
                background: 'rgba(245, 158, 11, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Clock size={24} color="var(--warning)" />
            </div>
            <div>
              <p
                style={{
                  margin: 0,
                  fontSize: '14px',
                  color: 'var(--text-secondary)',
                }}
              >
                Stopped
              </p>
              <p style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>
                {stats.stopped}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '48px',
                height: '48px',
                borderRadius: 'var(--border-radius)',
                background: 'rgba(6, 182, 212, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Zap size={24} color="var(--info)" />
            </div>
            <div>
              <p
                style={{
                  margin: 0,
                  fontSize: '14px',
                  color: 'var(--text-secondary)',
                }}
              >
                Creating
              </p>
              <p style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>
                {stats.creating}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Sandboxes List */}
      <div>
        <h2
          style={{
            margin: '0 0 var(--spacing-lg) 0',
            fontSize: '20px',
            fontWeight: 600,
          }}
        >
          Recent Sandboxes
        </h2>

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

        {!loading && !error && sandboxes.length === 0 && (
          <div className="card" style={{ textAlign: 'center', padding: 'var(--spacing-2xl)' }}>
            <Box size={48} color="var(--text-tertiary)" style={{ margin: '0 auto' }} />
            <h3 style={{ margin: 'var(--spacing-md) 0 var(--spacing-sm) 0' }}>
              No sandboxes yet
            </h3>
            <p style={{ margin: '0 0 var(--spacing-lg) 0', color: 'var(--text-secondary)' }}>
              Create your first sandbox to get started
            </p>
            <button
              className="btn btn-primary"
              onClick={() => navigate('/sandboxes/new')}
            >
              <Plus size={16} />
              Create Sandbox
            </button>
          </div>
        )}

        {!loading && !error && sandboxes.length > 0 && (
          <div className="grid grid-cols-3">
            {sandboxes.slice(0, 6).map((sandbox) => (
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

        {!loading && !error && sandboxes.length > 6 && (
          <div style={{ textAlign: 'center', marginTop: 'var(--spacing-lg)' }}>
            <button
              className="btn btn-secondary"
              onClick={() => navigate('/sandboxes')}
            >
              View All Sandboxes
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;