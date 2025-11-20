import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const iTechSmartGenerativeWorkflow = () => {
  const [workflowText, setWorkflowText] = useState('');
  const [generatedWorkflow, setGeneratedWorkflow] = useState(null);
  const [executionStatus, setExecutionStatus] = useState('idle');
  const [executionLogs, setExecutionLogs] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [workflowComplexity, setWorkflowComplexity] = useState('medium');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  
  const canvasRef = useRef(null);

  // Workflow templates
  const templates = [
    {
      id: 'deployment',
      title: 'CI/CD Pipeline',
      description: 'Automated deployment workflow',
      text: 'Create a CI/CD pipeline that runs tests, builds Docker images, and deploys to production with rollback capabilities'
    },
    {
      id: 'monitoring',
      title: 'System Monitoring',
      description: 'Alert and monitoring workflow',
      text: 'Set up monitoring that checks system health, sends alerts on failures, and creates incident tickets automatically'
    },
    {
      id: 'backup',
      title: 'Backup Strategy',
      description: 'Automated backup and recovery',
      text: 'Implement automated daily backups with verification, cleanup of old backups, and disaster recovery testing'
    },
    {
      id: 'security',
      title: 'Security Scan',
      description: 'Security vulnerability scanning',
      text: 'Run daily security scans, check for vulnerabilities, generate reports, and notify security team of findings'
    },
    {
      id: 'data-sync',
      title: 'Data Synchronization',
      description: 'Multi-database sync workflow',
      text: 'Synchronize data between production and backup databases, validate integrity, and handle conflicts'
    }
  ];

  useEffect(() => {
    if (generatedWorkflow && canvasRef.current) {
      drawWorkflowVisualization();
    }
  }, [generatedWorkflow]);

  const drawWorkflowVisualization = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Sample workflow nodes
    const nodes = [
      { id: 'start', type: 'start', x: 100, y: 200, label: 'Start' },
      { id: 'validate', type: 'process', x: 250, y: 200, label: 'Validate Input' },
      { id: 'decision', type: 'decision', x: 400, y: 200, label: 'Conditions?' },
      { id: 'process1', type: 'process', x: 550, y: 100, label: 'Process A' },
      { id: 'process2', type: 'process', x: 550, y: 300, label: 'Process B' },
      { id: 'notify', type: 'process', x: 700, y: 200, label: 'Notify' },
      { id: 'end', type: 'end', x: 850, y: 200, label: 'Complete' }
    ];

    // Draw connections
    ctx.strokeStyle = 'rgba(102, 126, 234, 0.6)';
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);

    const connections = [
      ['start', 'validate'],
      ['validate', 'decision'],
      ['decision', 'process1'],
      ['decision', 'process2'],
      ['process1', 'notify'],
      ['process2', 'notify'],
      ['notify', 'end']
    ];

    connections.forEach(([from, to]) => {
      const fromNode = nodes.find(n => n.id === from);
      const toNode = nodes.find(n => n.id === to);
      
      ctx.beginPath();
      ctx.moveTo(fromNode.x, fromNode.y);
      
      if (from === 'decision') {
        // Draw curved lines from decision
        const midY = (fromNode.y + toNode.y) / 2;
        ctx.quadraticCurveTo(fromNode.x + 50, midY, toNode.x, toNode.y);
      } else {
        ctx.lineTo(toNode.x, toNode.y);
      }
      
      ctx.stroke();
      
      // Draw arrow
      const angle = Math.atan2(toNode.y - fromNode.y, toNode.x - fromNode.x);
      ctx.save();
      ctx.translate(toNode.x, toNode.y);
      ctx.rotate(angle);
      ctx.beginPath();
      ctx.moveTo(-15, -5);
      ctx.lineTo(0, 0);
      ctx.lineTo(-15, 5);
      ctx.stroke();
      ctx.restore();
    });

    ctx.setLineDash([]);

    // Draw nodes
    nodes.forEach(node => {
      ctx.save();
      
      if (node.type === 'decision') {
        // Diamond shape for decision nodes
        ctx.translate(node.x, node.y);
        ctx.beginPath();
        ctx.moveTo(0, -30);
        ctx.lineTo(30, 0);
        ctx.lineTo(0, 30);
        ctx.lineTo(-30, 0);
        ctx.closePath();
      } else {
        // Rounded rectangle for other nodes
        ctx.translate(node.x, node.y);
        const width = 100;
        const height = 40;
        const radius = 8;
        
        ctx.beginPath();
        ctx.moveTo(-width/2 + radius, -height/2);
        ctx.lineTo(width/2 - radius, -height/2);
        ctx.quadraticCurveTo(width/2, -height/2, width/2, -height/2 + radius);
        ctx.lineTo(width/2, height/2 - radius);
        ctx.quadraticCurveTo(width/2, height/2, width/2 - radius, height/2);
        ctx.lineTo(-width/2 + radius, height/2);
        ctx.quadraticCurveTo(-width/2, height/2, -width/2, height/2 - radius);
        ctx.lineTo(-width/2, -height/2 + radius);
        ctx.quadraticCurveTo(-width/2, -height/2, -width/2 + radius, -height/2);
        ctx.closePath();
      }

      // Apply gradient based on node type
      let gradient;
      switch (node.type) {
        case 'start':
          gradient = ctx.createLinearGradient(-50, -20, 50, 20);
          gradient.addColorStop(0, '#4facfe');
          gradient.addColorStop(1, '#00f2fe');
          break;
        case 'end':
          gradient = ctx.createLinearGradient(-50, -20, 50, 20);
          gradient.addColorStop(0, '#f093fb');
          gradient.addColorStop(1, '#f5576c');
          break;
        case 'decision':
          gradient = ctx.createLinearGradient(-30, -30, 30, 30);
          gradient.addColorStop(0, '#fa709a');
          gradient.addColorStop(1, '#fee140');
          break;
        default:
          gradient = ctx.createLinearGradient(-50, -20, 50, 20);
          gradient.addColorStop(0, '#667eea');
          gradient.addColorStop(1, '#764ba2');
      }
      
      ctx.fillStyle = gradient;
      ctx.fill();
      
      // Draw border
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
      ctx.lineWidth = 2;
      ctx.stroke();
      
      // Draw label
      ctx.fillStyle = 'white';
      ctx.font = '12px Inter';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(node.label, 0, 0);
      
      ctx.restore();
    });
  };

  const handleGenerateWorkflow = () => {
    if (!workflowText.trim()) {
      alert('Please enter a workflow description');
      return;
    }

    setIsGenerating(true);
    addExecutionLog('info', 'Starting workflow generation...');

    // Simulate AI workflow generation
    setTimeout(() => {
      const workflow = {
        id: Date.now(),
        name: 'Generated Workflow',
        description: workflowText,
        complexity: workflowComplexity,
        steps: [
          { id: 1, name: 'Parse Input', type: 'process', duration: '2s' },
          { id: 2, name: 'Validate Requirements', type: 'decision', duration: '3s' },
          { id: 3, name: 'Execute Main Process', type: 'process', duration: '10s' },
          { id: 4, name: 'Handle Results', type: 'process', duration: '5s' },
          { id: 5, name: 'Notify Stakeholders', type: 'process', duration: '3s' }
        ],
        estimatedTime: '23s',
        confidence: 0.92
      };

      setGeneratedWorkflow(workflow);
      setIsGenerating(false);
      addExecutionLog('success', `Workflow generated successfully with ${workflow.steps.length} steps`);
    }, 2000);
  };

  const handleExecuteWorkflow = () => {
    if (!generatedWorkflow) {
      alert('Please generate a workflow first');
      return;
    }

    setIsExecuting(true);
    setExecutionStatus('running');
    addExecutionLog('info', 'Starting workflow execution...');

    // Simulate workflow execution
    generatedWorkflow.steps.forEach((step, index) => {
      setTimeout(() => {
        addExecutionLog('info', `Executing step ${index + 1}: ${step.name}`);
        
        if (step.type === 'decision') {
          setTimeout(() => {
            addExecutionLog('success', `Decision point: ${step.name} - Condition met`);
          }, 1000);
        }
        
        if (index === generatedWorkflow.steps.length - 1) {
          setTimeout(() => {
            setIsExecuting(false);
            setExecutionStatus('success');
            addExecutionLog('success', 'Workflow completed successfully!');
          }, 2000);
        }
      }, index * 4000);
    });
  };

  const addExecutionLog = (level, message) => {
    const timestamp = new Date().toLocaleTimeString();
    setExecutionLogs(prev => [
      { timestamp, level, message },
      ...prev
    ].slice(0, 50)); // Keep only last 50 logs
  };

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template.id);
    setWorkflowText(template.text);
  };

  const clearLogs = () => {
    setExecutionLogs([]);
  };

  const resetWorkflow = () => {
    setGeneratedWorkflow(null);
    setExecutionStatus('idle');
    setExecutionLogs([]);
    setWorkflowText('');
    setSelectedTemplate('');
  };

  return (
    <div className="workflow-app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo-section">
            <div className="logo-icon">🤖</div>
            <div className="logo-text">iTechSmart Generative Workflow</div>
          </div>
          <div className="header-stats">
            <div className="stat-item">
              <div className="stat-value">{generatedWorkflow ? generatedWorkflow.steps.length : 0}</div>
              <div className="stat-label">Steps</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{generatedWorkflow ? generatedWorkflow.confidence * 100 : 0}%</div>
              <div className="stat-label">Confidence</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{executionLogs.length}</div>
              <div className="stat-label">Logs</div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Input Section */}
        <div className="input-section">
          {/* Text Input Card */}
          <div className="input-card fade-in">
            <div className="card-title">
              <div className="card-icon">✍️</div>
              Describe Your Workflow
            </div>
            <textarea
              className="workflow-input"
              placeholder="Describe the workflow you want to generate in natural language. For example: 'Create a workflow that backs up the database every night, validates the backup, and sends a notification if it fails.'"
              value={workflowText}
              onChange={(e) => setWorkflowText(e.target.value)}
            />
          </div>

          {/* Generation Controls */}
          <div className="input-card fade-in">
            <div className="card-title">
              <div className="card-icon">⚙️</div>
              Generation Settings
            </div>
            
            <div className="generation-controls">
              <div className="control-group">
                <label className="control-label">Complexity</label>
                <select
                  className="control-select"
                  value={workflowComplexity}
                  onChange={(e) => setWorkflowComplexity(e.target.value)}
                >
                  <option value="simple">Simple</option>
                  <option value="medium">Medium</option>
                  <option value="complex">Complex</option>
                </select>
              </div>
              
              <div className="control-group">
                <label className="control-label">Integration Target</label>
                <select className="control-select">
                  <option>All Products</option>
                  <option>Arbiter</option>
                  <option>Digital Twin</option>
                  <option>Business Value</option>
                  <option>Knowledge Graph</option>
                </select>
              </div>
            </div>

            <div className="action-buttons">
              <button
                className="btn btn-primary"
                onClick={handleGenerateWorkflow}
                disabled={isGenerating || !workflowText.trim()}
              >
                {isGenerating ? (
                  <>
                    <span className="loading-spinner"></span>
                    Generating...
                  </>
                ) : (
                  <>
                    ⚡ Generate Workflow
                  </>
                )}
              </button>
              
              <button
                className="btn btn-secondary"
                onClick={resetWorkflow}
              >
                🔄 Reset
              </button>
            </div>
          </div>

          {/* Templates Section */}
          <div className="input-card fade-in">
            <div className="card-title">
              <div className="card-icon">📋</div>
              Quick Templates
            </div>
            
            <div className="templates-section">
              <div className="template-grid">
                {templates.map(template => (
                  <div
                    key={template.id}
                    className={`template-card ${selectedTemplate === template.id ? 'selected' : ''}`}
                    onClick={() => handleTemplateSelect(template)}
                  >
                    <div className="template-title">{template.title}</div>
                    <div className="template-description">{template.description}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Output Section */}
        <div className="output-section">
          {/* Workflow Visualization */}
          <div className="workflow-visualization fade-in">
            <div className="card-title">
              <div className="card-icon">🎯</div>
              Workflow Visualization
            </div>
            
            <div className="workflow-canvas">
              {generatedWorkflow ? (
                <canvas
                  ref={canvasRef}
                  width={1000}
                  height={400}
                  style={{ width: '100%', height: '100%' }}
                />
              ) : (
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  height: '100%',
                  color: 'var(--text-muted)'
                }}>
                  Generate a workflow to see the visualization
                </div>
              )}
            </div>
            
            {generatedWorkflow && (
              <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem' }}>
                <div style={{ fontSize: '0.875rem' }}>
                  <strong>Estimated Time:</strong> {generatedWorkflow.estimatedTime}
                </div>
                <div style={{ fontSize: '0.875rem' }}>
                  <strong>Confidence:</strong> {(generatedWorkflow.confidence * 100).toFixed(0)}%
                </div>
              </div>
            )}
          </div>

          {/* Execution Results */}
          <div className="execution-results fade-in">
            <div className="card-title">
              <div className="card-icon">🚀</div>
              Execution Status
            </div>
            
            <div className="execution-status">
              <div className={`status-indicator ${executionStatus}`} />
              <span>
                {executionStatus === 'idle' && 'Ready to execute'}
                {executionStatus === 'running' && 'Workflow running...'}
                {executionStatus === 'success' && 'Workflow completed'}
                {executionStatus === 'error' && 'Execution failed'}
              </span>
            </div>

            <div className="action-buttons">
              <button
                className="btn btn-primary"
                onClick={handleExecuteWorkflow}
                disabled={!generatedWorkflow || isExecuting}
              >
                {isExecuting ? (
                  <>
                    <span className="loading-spinner"></span>
                    Executing...
                  </>
                ) : (
                  <>
                    ▶️ Execute Workflow
                  </>
                )}
              </button>
              
              <button
                className="btn btn-secondary"
                onClick={clearLogs}
              >
                🧹 Clear Logs
              </button>
            </div>

            <div className="execution-log">
              {executionLogs.length === 0 ? (
                <div style={{ color: 'var(--text-muted)', textAlign: 'center' }}>
                  No execution logs yet. Generate and execute a workflow to see logs.
                </div>
              ) : (
                executionLogs.map((log, index) => (
                  <div key={index} className="log-entry">
                    <span className="log-timestamp">{log.timestamp}</span>
                    <span className={`log-level ${log.level}`}>{log.level}</span>
                    <span className="log-message">{log.message}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default iTechSmartGenerativeWorkflow;