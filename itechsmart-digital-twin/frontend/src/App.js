import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const iTechSmartDigitalTwin = () => {
  const [simulationStatus, setSimulationStatus] = useState('idle');
  const [timeAcceleration, setTimeAcceleration] = useState(1000);
  const [simulationTime, setSimulationTime] = useState(0);
  const [selectedScenario, setSelectedScenario] = useState('normal-operation');
  const [impactPrediction, setImpactPrediction] = useState({});
  const [simulationHistory, setSimulationHistory] = useState([]);
  const [metrics, setMetrics] = useState({
    cpuUtilization: 45,
    memoryUsage: 62,
    networkLatency: 25,
    errorRate: 0.8,
    throughput: 850
  });
  
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const simulationIntervalRef = useRef(null);

  // Simulation scenarios
  const scenarios = [
    { id: 'normal-operation', name: 'Normal Operation', description: 'Standard operating conditions' },
    { id: 'traffic-spike', name: 'Traffic Spike', description: 'Sudden increase in user traffic' },
    { id: 'server-failure', name: 'Server Failure', description: 'Single server failure scenario' },
    { id: 'network-outage', name: 'Network Outage', description: 'Partial network connectivity loss' },
    { id: 'ddos-attack', name: 'DDoS Attack', description: 'Distributed denial of service attack' },
    { id: 'database-overload', name: 'Database Overload', description: 'Database performance degradation' }
  ];

  useEffect(() => {
    // Initialize canvas for visualization
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      drawNetworkVisualization(ctx);
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      if (simulationIntervalRef.current) {
        clearInterval(simulationIntervalRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (simulationStatus === 'running') {
      simulationIntervalRef.current = setInterval(() => {
        setSimulationTime(prev => prev + timeAcceleration / 1000);
        updateMetrics();
      }, 100);
    } else {
      if (simulationIntervalRef.current) {
        clearInterval(simulationIntervalRef.current);
      }
    }
  }, [simulationStatus, timeAcceleration]);

  const drawNetworkVisualization = (ctx) => {
    const canvas = ctx.canvas;
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw network nodes
    const nodes = [
      { x: width * 0.2, y: height * 0.3, label: 'Gateway', color: '#6366f1' },
      { x: width * 0.5, y: height * 0.2, label: 'Load Balancer', color: '#8b5cf6' },
      { x: width * 0.8, y: height * 0.3, label: 'Arbiter', color: '#22d3ee' },
      { x: width * 0.3, y: height * 0.6, label: 'Analytics', color: '#10b981' },
      { x: width * 0.5, y: height * 0.7, label: 'Database', color: '#f59e0b' },
      { x: width * 0.7, y: height * 0.6, label: 'Cache', color: '#ef4444' }
    ];

    // Draw connections
    ctx.strokeStyle = 'rgba(99, 102, 241, 0.3)';
    ctx.lineWidth = 2;
    
    const connections = [
      [0, 1], [1, 2], [1, 3], [1, 4], [1, 5], [3, 4], [4, 5]
    ];

    connections.forEach(([from, to]) => {
      ctx.beginPath();
      ctx.moveTo(nodes[from].x, nodes[from].y);
      ctx.lineTo(nodes[to].x, nodes[to].y);
      ctx.stroke();
    });

    // Draw nodes
    nodes.forEach(node => {
      // Node circle
      ctx.beginPath();
      ctx.arc(node.x, node.y, 20, 0, Math.PI * 2);
      ctx.fillStyle = node.color;
      ctx.fill();
      
      // Node label
      ctx.fillStyle = '#f1f5f9';
      ctx.font = '12px Inter';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(node.label, node.x, node.y);
    });
  };

  const updateMetrics = () => {
    setMetrics(prev => {
      const variation = (Math.random() - 0.5) * 10;
      return {
        cpuUtilization: Math.max(0, Math.min(100, prev.cpuUtilization + variation)),
        memoryUsage: Math.max(0, Math.min(100, prev.memoryUsage + variation * 0.8)),
        networkLatency: Math.max(0, prev.networkLatency + variation * 0.5),
        errorRate: Math.max(0, prev.errorRate + variation * 0.1),
        throughput: Math.max(0, prev.throughput + variation * 10)
      };
    });
  };

  const handleStartSimulation = () => {
    setSimulationStatus('running');
    
    // Add to history
    const historyEntry = {
      id: Date.now(),
      action: 'Simulation Started',
      scenario: scenarios.find(s => s.id === selectedScenario)?.name,
      timestamp: new Date(),
      impact: 'medium',
      description: `Started ${selectedScenario} simulation at ${timeAcceleration}x speed`
    };
    setSimulationHistory([historyEntry, ...simulationHistory]);

    // Calculate impact prediction
    predictImpact();
  };

  const handleStopSimulation = () => {
    setSimulationStatus('stopped');
    
    const historyEntry = {
      id: Date.now(),
      action: 'Simulation Stopped',
      timestamp: new Date(),
      impact: 'low',
      description: `Simulation stopped after ${simulationTime.toFixed(1)} seconds`
    };
    setSimulationHistory([historyEntry, ...simulationHistory]);
  };

  const handleResetSimulation = () => {
    setSimulationStatus('idle');
    setSimulationTime(0);
    setMetrics({
      cpuUtilization: 45,
      memoryUsage: 62,
      networkLatency: 25,
      errorRate: 0.8,
      throughput: 850
    });
    
    const historyEntry = {
      id: Date.now(),
      action: 'Simulation Reset',
      timestamp: new Date(),
      impact: 'low',
      description: 'Simulation reset to initial state'
    };
    setSimulationHistory([historyEntry, ...simulationHistory]);
  };

  const predictImpact = () => {
    const scenarioImpacts = {
      'normal-operation': { cpu: '+5%', memory: '+3%', latency: '+2%', errors: '0%' },
      'traffic-spike': { cpu: '+45%', memory: '+30%', latency: '+80%', errors: '+15%' },
      'server-failure': { cpu: '+20%', memory: '+15%', latency: '+120%', errors: '+25%' },
      'network-outage': { cpu: '-10%', memory: '-5%', latency: '+500%', errors: '+40%' },
      'ddos-attack': { cpu: '+85%', memory: '+60%', latency: '+300%', errors: '+60%' },
      'database-overload': { cpu: '+35%', memory: '+50%', latency: '+200%', errors: '+35%' }
    };

    setImpactPrediction(scenarioImpacts[selectedScenario] || {});
  };

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const getMetricChangeColor = (metric) => {
    const threshold = {
      cpuUtilization: 70,
      memoryUsage: 80,
      networkLatency: 50,
      errorRate: 2,
      throughput: 500
    };
    
    if (metric > threshold[metric]) {
      return 'negative';
    } else if (metric < threshold[metric] * 0.7) {
      return 'positive';
    }
    return '';
  };

  return (
    <div className="digital-twin-app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo-section">
            <div className="logo-icon">🎮</div>
            <div className="logo-text">iTechSmart Digital Twin</div>
          </div>
          <div className="header-status">
            <div className="status-item">
              <span className="status-label">Status</span>
              <span className="status-value">{simulationStatus.toUpperCase()}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Speed</span>
              <span className="status-value">{timeAcceleration}x</span>
            </div>
            <div className="status-item">
              <span className="status-label">Time</span>
              <span className="status-value">{formatTime(simulationTime)}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Simulation Controls */}
        <div className="simulation-controls fade-in-up">
          <div className="controls-header">
            <div className="controls-title">
              🎛️ Simulation Controls
            </div>
            <div className="card-badge simulating">
              {simulationStatus === 'running' ? 'SIMULATING' : 'READY'}
            </div>
          </div>
          
          <div className="controls-grid">
            <div className="control-group">
              <label className="control-label">Scenario</label>
              <select 
                className="control-select"
                value={selectedScenario}
                onChange={(e) => setSelectedScenario(e.target.value)}
                disabled={simulationStatus === 'running'}
              >
                {scenarios.map(scenario => (
                  <option key={scenario.id} value={scenario.id}>
                    {scenario.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="control-group">
              <label className="control-label">Time Acceleration</label>
              <select 
                className="control-select"
                value={timeAcceleration}
                onChange={(e) => setTimeAcceleration(Number(e.target.value))}
              >
                <option value="100">1x</option>
                <option value="500">5x</option>
                <option value="1000">10x</option>
                <option value="5000">50x</option>
                <option value="10000">100x</option>
              </select>
            </div>
            
            <div className="control-group">
              <label className="control-label">Duration (minutes)</label>
              <input 
                type="number"
                className="control-input"
                placeholder="60"
                defaultValue="60"
                disabled={simulationStatus === 'running'}
              />
            </div>
          </div>
          
          <div className="control-buttons">
            <button
              className="control-button primary"
              onClick={handleStartSimulation}
              disabled={simulationStatus === 'running'}
            >
              ▶️ Start Simulation
            </button>
            
            <button
              className="control-button secondary"
              onClick={handleStopSimulation}
              disabled={simulationStatus !== 'running'}
            >
              ⏸️ Stop Simulation
            </button>
            
            <button
              className="control-button danger"
              onClick={handleResetSimulation}
            >
              🔄 Reset
            </button>
          </div>
        </div>

        {/* Dashboard Grid */}
        <div className="dashboard-grid">
          {/* System Visualization */}
          <div className="card fade-in-up">
            <div className="card-header">
              <div className="card-title">
                <div className="card-icon">🌐</div>
                System Visualization
              </div>
              <div className="card-badge active">LIVE</div>
            </div>
            
            <div className="visualization-area">
              <canvas
                ref={canvasRef}
                width={400}
                height={300}
                className="visualization-canvas"
              />
              
              {simulationStatus === 'running' && (
                <div className="simulation-overlay active">
                  <div className="simulation-message">
                    <div className="simulation-spinner"></div>
                    <div>Simulating {scenarios.find(s => s.id === selectedScenario)?.name}</div>
                    <div style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
                      Speed: {timeAcceleration}x
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Impact Prediction */}
          <div className="card fade-in-up">
            <div className="card-header">
              <div className="card-title">
                <div className="card-icon">📊</div>
                Impact Prediction
              </div>
              <div className="card-badge warning">PREDICTIVE</div>
            </div>
            
            <div className="metrics-grid">
              <div className="metric-item">
                <div className="metric-label">CPU Utilization</div>
                <div className="metric-value">{impactPrediction.cpu || '+5%'}</div>
              </div>
              <div className="metric-item">
                <div className="metric-label">Memory Usage</div>
                <div className="metric-value">{impactPrediction.memory || '+3%'}</div>
              </div>
              <div className="metric-item">
                <div className="metric-label">Network Latency</div>
                <div className="metric-value">{impactPrediction.latency || '+2%'}</div>
              </div>
              <div className="metric-item">
                <div className="metric-label">Error Rate</div>
                <div className="metric-value">{impactPrediction.errors || '0%'}</div>
              </div>
            </div>
            
            <div style={{ marginTop: '1rem', padding: '1rem', background: 'var(--background-color)', borderRadius: '8px' }}>
              <strong>Scenario:</strong> {scenarios.find(s => s.id === selectedScenario)?.description}
            </div>
          </div>

          {/* Real-time Metrics */}
          <div className="card fade-in-up">
            <div className="card-header">
              <div className="card-title">
                <div className="card-icon">📈</div>
                Real-time Metrics
              </div>
              <div className={`card-badge ${simulationStatus === 'running' ? 'simulating' : 'active'}`}>
                {simulationStatus === 'running' ? 'LIVE' : 'IDLE'}
              </div>
            </div>
            
            <div className="metrics-grid">
              <div className="metric-item">
                <div className="metric-label">CPU Utilization</div>
                <div className="metric-value">{metrics.cpuUtilization.toFixed(1)}%</div>
                <div className={`metric-change ${getMetricChangeColor('cpuUtilization')}`}>
                  {metrics.cpuUtilization > 70 ? '⚠️ High' : '✅ Normal'}
                </div>
              </div>
              <div className="metric-item">
                <div className="metric-label">Memory Usage</div>
                <div className="metric-value">{metrics.memoryUsage.toFixed(1)}%</div>
                <div className={`metric-change ${getMetricChangeColor('memoryUsage')}`}>
                  {metrics.memoryUsage > 80 ? '⚠️ High' : '✅ Normal'}
                </div>
              </div>
              <div className="metric-item">
                <div className="metric-label">Network Latency</div>
                <div className="metric-value">{metrics.networkLatency.toFixed(1)}ms</div>
                <div className={`metric-change ${getMetricChangeColor('networkLatency')}`}>
                  {metrics.networkLatency > 50 ? '⚠️ High' : '✅ Normal'}
                </div>
              </div>
              <div className="metric-item">
                <div className="metric-label">Error Rate</div>
                <div className="metric-value">{metrics.errorRate.toFixed(2)}%</div>
                <div className={`metric-change ${getMetricChangeColor('errorRate')}`}>
                  {metrics.errorRate > 2 ? '⚠️ High' : '✅ Normal'}
                </div>
              </div>
              <div className="metric-item">
                <div className="metric-label">Throughput</div>
                <div className="metric-value">{metrics.throughput.toFixed(0)} req/s</div>
                <div className={`metric-change ${getMetricChangeColor('throughput')}`}>
                  {metrics.throughput < 500 ? '⚠️ Low' : '✅ Normal'}
                </div>
              </div>
            </div>
          </div>

          {/* Simulation History */}
          <div className="card fade-in-up">
            <div className="card-header">
              <div className="card-title">
                <div className="card-icon">📜</div>
                Simulation History
              </div>
            </div>
            
            <div className="timeline-container">
              {simulationHistory.length === 0 ? (
                <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '2rem' }}>
                  No simulation history available. Start a simulation to see the timeline.
                </div>
              ) : (
                simulationHistory.map((entry, index) => (
                  <div key={entry.id} className="timeline-item">
                    <div className="timeline-marker" />
                    <div className="timeline-content">
                      <div className="timeline-title">{entry.action}</div>
                      <div className="timeline-description">{entry.description}</div>
                      <div className="timeline-meta">
                        <span>{entry.timestamp.toLocaleTimeString()}</span>
                        <span className={`timeline-impact ${entry.impact}`}>
                          {entry.impact.toUpperCase()} IMPACT
                        </span>
                      </div>
                    </div>
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

export default iTechSmartDigitalTwin;