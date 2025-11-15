import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus } from 'lucide-react';
import { sandboxApi, templateApi } from '../services/api';
import type { Template } from '../types';
import { parseErrorMessage } from '../utils/helpers';

const CreateSandbox: React.FC = () => {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    image: 'python:3.11',
    gpu_type: '',
    ttl_seconds: 3600,
    template_id: '',
  });

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const data = await templateApi.list();
      setTemplates(data);
    } catch (err) {
      console.error('Failed to load templates:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      const sandbox = await sandboxApi.create({
        name: formData.name,
        image: formData.image,
        gpu_type: formData.gpu_type || undefined,
        ttl_seconds: formData.ttl_seconds,
        template_id: formData.template_id || undefined,
      });
      navigate(`/sandboxes/${sandbox.id}`);
    } catch (err) {
      alert(parseErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleTemplateSelect = (template: Template) => {
    setFormData({
      ...formData,
      image: template.image,
      gpu_type: template.gpu_type || '',
      ttl_seconds: template.default_ttl_seconds,
      template_id: template.id,
    });
  };

  const commonImages = [
    { value: 'python:3.11', label: 'Python 3.11' },
    { value: 'python:3.10', label: 'Python 3.10' },
    { value: 'node:20', label: 'Node.js 20' },
    { value: 'node:18', label: 'Node.js 18' },
    { value: 'ubuntu:22.04', label: 'Ubuntu 22.04' },
    { value: 'ubuntu:20.04', label: 'Ubuntu 20.04' },
  ];

  const gpuTypes = [
    { value: '', label: 'No GPU' },
    { value: 'T4', label: 'NVIDIA T4' },
    { value: 'A10G', label: 'NVIDIA A10G' },
    { value: 'V100', label: 'NVIDIA V100' },
    { value: 'A100', label: 'NVIDIA A100' },
  ];

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
        <h1 style={{ margin: 0, fontSize: '32px', fontWeight: 'bold' }}>
          Create New Sandbox
        </h1>
        <p
          style={{
            margin: '8px 0 0 0',
            fontSize: '16px',
            color: 'var(--text-secondary)',
          }}
        >
          Set up a new isolated environment for code execution
        </p>
      </div>

      <div className="grid grid-cols-3" style={{ gap: 'var(--spacing-xl)' }}>
        {/* Form */}
        <div style={{ gridColumn: 'span 2' }}>
          <form onSubmit={handleSubmit} className="card">
            <h2
              style={{
                margin: '0 0 var(--spacing-lg) 0',
                fontSize: '20px',
                fontWeight: 600,
              }}
            >
              Sandbox Configuration
            </h2>

            {/* Name */}
            <div className="form-group">
              <label className="form-label">Sandbox Name *</label>
              <input
                type="text"
                className="form-input"
                placeholder="my-sandbox"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                required
              />
            </div>

            {/* Image */}
            <div className="form-group">
              <label className="form-label">Base Image *</label>
              <select
                className="form-select"
                value={formData.image}
                onChange={(e) =>
                  setFormData({ ...formData, image: e.target.value })
                }
                required
              >
                {commonImages.map((img) => (
                  <option key={img.value} value={img.value}>
                    {img.label}
                  </option>
                ))}
              </select>
              <p
                style={{
                  margin: '4px 0 0 0',
                  fontSize: '12px',
                  color: 'var(--text-secondary)',
                }}
              >
                Or enter a custom Docker image name
              </p>
            </div>

            {/* GPU Type */}
            <div className="form-group">
              <label className="form-label">GPU Type (Optional)</label>
              <select
                className="form-select"
                value={formData.gpu_type}
                onChange={(e) =>
                  setFormData({ ...formData, gpu_type: e.target.value })
                }
              >
                {gpuTypes.map((gpu) => (
                  <option key={gpu.value} value={gpu.value}>
                    {gpu.label}
                  </option>
                ))}
              </select>
            </div>

            {/* TTL */}
            <div className="form-group">
              <label className="form-label">Time to Live (seconds) *</label>
              <input
                type="number"
                className="form-input"
                placeholder="3600"
                value={formData.ttl_seconds}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    ttl_seconds: parseInt(e.target.value),
                  })
                }
                min="60"
                required
              />
              <p
                style={{
                  margin: '4px 0 0 0',
                  fontSize: '12px',
                  color: 'var(--text-secondary)',
                }}
              >
                Sandbox will auto-terminate after this duration (minimum 60 seconds)
              </p>
            </div>

            {/* Submit */}
            <div
              style={{
                display: 'flex',
                gap: 'var(--spacing-md)',
                paddingTop: 'var(--spacing-md)',
                borderTop: '1px solid var(--border-color)',
              }}
            >
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <div className="spinner" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus size={16} />
                    Create Sandbox
                  </>
                )}
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => navigate('/sandboxes')}
                disabled={loading}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>

        {/* Templates Sidebar */}
        <div>
          <div className="card">
            <h3
              style={{
                margin: '0 0 var(--spacing-md) 0',
                fontSize: '16px',
                fontWeight: 600,
              }}
            >
              Quick Start Templates
            </h3>
            {templates.length === 0 ? (
              <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '14px' }}>
                No templates available
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {templates.map((template) => (
                  <button
                    key={template.id}
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => handleTemplateSelect(template)}
                    style={{ justifyContent: 'flex-start', textAlign: 'left' }}
                  >
                    <div>
                      <div style={{ fontWeight: 600 }}>{template.name}</div>
                      {template.description && (
                        <div
                          style={{
                            fontSize: '12px',
                            color: 'var(--text-secondary)',
                            marginTop: '2px',
                          }}
                        >
                          {template.description}
                        </div>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateSandbox;