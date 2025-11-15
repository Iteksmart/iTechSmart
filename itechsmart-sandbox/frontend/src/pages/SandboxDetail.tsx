import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Play,
  Square,
  Trash2,
  RefreshCw,
  Terminal,
  Activity,
} from 'lucide-react';
import { sandboxApi } from '../services/api';
import type { Sandbox, ResourceMetric } from '../types';
import MetricsChart from '../components/MetricsChart';
import {
  getStatusColor,
  formatDate,
  formatDuration,
  calculateTimeRemaining,
  parseErrorMessage,
} from '../utils/helpers';

const SandboxDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [sandbox, setSandbox] = useState<Sandbox | null>(null);
  const [metrics, setMetrics] = useState<ResourceMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadSandbox();
      loadMetrics();
      
      // Refresh every 5 seconds
      const interval = setInterval(() => {
        loadSandbox();
        loadMetrics();
      }, 5000);

      return () => clearInterval(interval);
    }
  }, [id]);

  const loadSandbox = async () => {
    if (!id) return;
    
    try {
      setError(null);
      const data = await sandboxApi.get(id);
      setSandbox(data);
    } catch (err) {
      setError(parseErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const loadMetrics = async () => {
    if (!id) return;
    
    try {
      const data = await sandboxApi.getMetrics(id, 50);
      setMetrics(data);
    } catch (err) {
      console.error('Failed to load metrics:', err);
    }
  };

  const handleStart = async () => {
    if (!id) return;
    try {
      await sandboxApi.start(id);
      await loadSandbox();
    } catch (err) {
      alert(parseErrorMessage(err));
    }
  };

  const handleStop = async () => {
    if (!id) return;
    try {
      await sandboxApi.stop(id);
      await loadSandbox();
    } catch (err) {
      alert(parseErrorMessage(err));
    }
  };

  const handleTerminate = async () => {
    if (!id) return;
    if (window.confirm(`Are you sure you want to terminate "${sandbox?.name}"?`)) {
      try {
        await sandboxApi.terminate(id);
        navigate('/sandboxes');
      } catch (err) {
        alert(parseErrorMessage(err));
      }
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 'var(--spacing-2xl)' }}>
        <div className="spinner" style={{ width: '40px', height: '40px' }} />
        <p style={{ marginTop: 'var(--spacing-md)', color: 'var(--text-secondary)' }}>
          Loading sandbox...
        </p>
      </div>
    );
  }

  if (error || !sandbox) {
    return (
      <div>
        <button
          className="btn btn-secondary"
          onClick={() => navigate('/sandboxes')}
          style={{ marginBottom: 'var(--spacing-md)' }}
        >
          <ArrowLeft size={16} />
          Back to Sandboxes
        </button>
        <div
          className="card"
          style={{
            background: '#fee2e2',
            border: '1px solid #fecaca',
            color: '#991b1b',
          }}
        >
          <p style={{ margin: 0 }}>Error: {error || 'Sandbox not found'}</p>
        </div>
      </div>
    );
  }

  const timeRemaining = calculateTimeRemaining(
    sandbox.created_at,
    sandbox.ttl_seconds
  );

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 'var(--spacing-xl)' }}>
        <button
          className="btn btn-secondary"
          onClick={() => navigate('/sandboxes')}
          style={{ marginBottom: 'var(--spacing-md)' }}
        >
          <ArrowLeft size={16} />
          Back to Sandboxes
        </button>
        
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <h1 style={{ margin: 0, fontSize: '32px', fontWeight: 'bold' }}>
                {sandbox.name}
              </h1>
              <span className={`badge ${getStatusColor(sandbox.status)}`}>
                {sandbox.status}
              </span>
            </div>
            <p
              style={{
                margin: '8px 0 0 0',
                fontSize: '16px',
                color: 'var(--text-secondary)',
              }}
            >
              {sandbox.image}
            </p>
          </div>

          <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
            <button
              className="btn btn-secondary"
              onClick={loadSandbox}
              title="Refresh"
            >
              <RefreshCw size={16} />
            </button>
            {sandbox.status === 'stopped' && (
              <button className="btn btn-success" onClick={handleStart}>
                <Play size={16} />
                Start
              </button>
            )}
            {sandbox.status === 'running' && (
              <button className="btn btn-secondary" onClick={handleStop}>
                <Square size={16} />
                Stop
              </button>
            )}
            <button className="btn btn-danger" onClick={handleTerminate}>
              <Trash2 size={16} />
              Terminate
            </button>
          </div>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-4" style={{ marginBottom: 'var(--spacing-xl)' }}>
        <div className="card">
          <p
            style={{
              margin: '0 0 4px 0',
              fontSize: '14px',
              color: 'var(--text-secondary)',
            }}
          >
            Created
          </p>
          <p style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>
            {formatDate(sandbox.created_at)}
          </p>
        </div>

        <div className="card">
          <p
            style={{
              margin: '0 0 4px 0',
              fontSize: '14px',
              color: 'var(--text-secondary)',
            }}
          >
            Time Remaining
          </p>
          <p style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>
            {formatDuration(Math.floor(timeRemaining))}
          </p>
        </div>

        <div className="card">
          <p
            style={{
              margin: '0 0 4px 0',
              fontSize: '14px',
              color: 'var(--text-secondary)',
            }}
          >
            GPU Type
          </p>
          <p style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>
            {sandbox.gpu_type || 'None'}
          </p>
        </div>

        <div className="card">
          <p
            style={{
              margin: '0 0 4px 0',
              fontSize: '14px',
              color: 'var(--text-secondary)',
            }}
          >
            Sandbox ID
          </p>
          <p
            style={{
              margin: 0,
              fontSize: '14px',
              fontWeight: 600,
              fontFamily: 'var(--font-mono)',
            }}
          >
            {sandbox.id.substring(0, 8)}...
          </p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-3" style={{ marginBottom: 'var(--spacing-xl)' }}>
        <button
          className="btn btn-secondary"
          onClick={() => navigate(`/editor?sandbox=${sandbox.id}`)}
          style={{ justifyContent: 'flex-start', padding: 'var(--spacing-lg)' }}
        >
          <Terminal size={20} />
          <div style={{ textAlign: 'left' }}>
            <div style={{ fontWeight: 600 }}>Open Code Editor</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              Write and execute code
            </div>
          </div>
        </button>

        <button
          className="btn btn-secondary"
          onClick={() => navigate(`/monitoring?sandbox=${sandbox.id}`)}
          style={{ justifyContent: 'flex-start', padding: 'var(--spacing-lg)' }}
        >
          <Activity size={20} />
          <div style={{ textAlign: 'left' }}>
            <div style={{ fontWeight: 600 }}>View Monitoring</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              Real-time resource metrics
            </div>
          </div>
        </button>

        <button
          className="btn btn-secondary"
          onClick={() => navigate(`/files?sandbox=${sandbox.id}`)}
          style={{ justifyContent: 'flex-start', padding: 'var(--spacing-lg)' }}
        >
          <Terminal size={20} />
          <div style={{ textAlign: 'left' }}>
            <div style={{ fontWeight: 600 }}>Manage Files</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              Upload and download files
            </div>
          </div>
        </button>
      </div>

      {/* Metrics */}
      {metrics.length > 0 && (
        <div>
          <h2
            style={{
              margin: '0 0 var(--spacing-lg) 0',
              fontSize: '20px',
              fontWeight: 600,
            }}
          >
            Resource Metrics
          </h2>
          <div className="grid grid-cols-2">
            <MetricsChart
              metrics={metrics}
              dataKey="cpu_percent"
              title="CPU Usage"
              color="#2563eb"
              unit="%"
            />
            <MetricsChart
              metrics={metrics}
              dataKey="memory_percent"
              title="Memory Usage"
              color="#10b981"
              unit="%"
            />
            <MetricsChart
              metrics={metrics}
              dataKey="disk_read_mb"
              title="Disk Read"
              color="#f59e0b"
              unit=" MB"
            />
            <MetricsChart
              metrics={metrics}
              dataKey="network_rx_mb"
              title="Network Received"
              color="#06b6d4"
              unit=" MB"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default SandboxDetail;