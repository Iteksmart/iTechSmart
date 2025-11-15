import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, Square, Trash2, Clock, Cpu } from 'lucide-react';
import type { Sandbox } from '../types';
import {
  getStatusColor,
  formatRelativeTime,
  formatDuration,
  calculateTimeRemaining,
} from '../utils/helpers';

interface SandboxCardProps {
  sandbox: Sandbox;
  onStart?: (id: string) => void;
  onStop?: (id: string) => void;
  onTerminate?: (id: string) => void;
}

const SandboxCard: React.FC<SandboxCardProps> = ({
  sandbox,
  onStart,
  onStop,
  onTerminate,
}) => {
  const navigate = useNavigate();
  const timeRemaining = calculateTimeRemaining(
    sandbox.created_at,
    sandbox.ttl_seconds
  );

  return (
    <div
      className="card"
      style={{
        cursor: 'pointer',
        transition: 'transform 0.2s, box-shadow 0.2s',
      }}
      onClick={() => navigate(`/sandboxes/${sandbox.id}`)}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = 'var(--shadow-md)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: 'var(--spacing-md)',
        }}
      >
        <div>
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>
            {sandbox.name}
          </h3>
          <p
            style={{
              margin: '4px 0 0 0',
              fontSize: '14px',
              color: 'var(--text-secondary)',
            }}
          >
            {sandbox.image}
          </p>
        </div>
        <span className={`badge ${getStatusColor(sandbox.status)}`}>
          {sandbox.status}
        </span>
      </div>

      {/* Info */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--spacing-sm)',
          marginBottom: 'var(--spacing-md)',
        }}
      >
        {sandbox.gpu_type && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Cpu size={16} color="var(--text-secondary)" />
            <span style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
              GPU: {sandbox.gpu_type}
            </span>
          </div>
        )}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Clock size={16} color="var(--text-secondary)" />
          <span style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
            Created {formatRelativeTime(sandbox.created_at)}
          </span>
        </div>
        {sandbox.status === 'running' && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Clock size={16} color="var(--text-secondary)" />
            <span style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
              Time remaining: {formatDuration(Math.floor(timeRemaining))}
            </span>
          </div>
        )}
      </div>

      {/* Actions */}
      <div
        style={{
          display: 'flex',
          gap: 'var(--spacing-sm)',
          paddingTop: 'var(--spacing-md)',
          borderTop: '1px solid var(--border-color)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {sandbox.status === 'stopped' && onStart && (
          <button
            className="btn btn-success btn-sm"
            onClick={() => onStart(sandbox.id)}
          >
            <Play size={14} />
            Start
          </button>
        )}
        {sandbox.status === 'running' && onStop && (
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => onStop(sandbox.id)}
          >
            <Square size={14} />
            Stop
          </button>
        )}
        {onTerminate && (
          <button
            className="btn btn-danger btn-sm"
            onClick={() => {
              if (
                window.confirm(
                  `Are you sure you want to terminate "${sandbox.name}"?`
                )
              ) {
                onTerminate(sandbox.id);
              }
            }}
          >
            <Trash2 size={14} />
            Terminate
          </button>
        )}
      </div>
    </div>
  );
};

export default SandboxCard;