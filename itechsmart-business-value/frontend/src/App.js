import React, { useState, useEffect } from 'react';
import './App.css';

const iTechSmartBusinessValue = () => {
  const [timeRange, setTimeRange] = useState('30d');
  const [kpis, setKpis] = useState({
    totalROI: 287.5,
    costSavings: 1240000,
    revenueGenerated: 2150000,
    automationValue: 890000,
    efficiencyGain: 67.3,
    riskReduction: 82.1
  });
  
  const [roiInputs, setRoiInputs] = useState({
    initialInvestment: 250000,
    annualSavings: 450000,
    revenueIncrease: 320000,
    timeHorizon: 3
  });
  
  const [calculatedROI, setCalculatedROI] = useState(null);

  useEffect(() => {
    // Simulate real-time data updates
    const interval = setInterval(() => {
      setKpis(prev => ({
        ...prev,
        totalROI: prev.totalROI + (Math.random() - 0.5) * 2,
        efficiencyGain: Math.max(0, Math.min(100, prev.efficiencyGain + (Math.random() - 0.5) * 1)),
        riskReduction: Math.max(0, Math.min(100, prev.riskReduction + (Math.random() - 0.5) * 0.5))
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const calculateROI = () => {
    const { initialInvestment, annualSavings, revenueIncrease, timeHorizon } = roiInputs;
    
    const totalBenefits = (annualSavings + revenueIncrease) * timeHorizon;
    const netBenefit = totalBenefits - initialInvestment;
    const roi = (netBenefit / initialInvestment) * 100;
    const paybackPeriod = initialInvestment / (annualSavings + revenueIncrease);
    
    setCalculatedROI({
      roi: roi.toFixed(1),
      paybackPeriod: paybackPeriod.toFixed(1),
      totalBenefits: totalBenefits,
      netBenefit: netBenefit
    });
  };

  const valueDrivers = [
    {
      name: 'Automated Incident Resolution',
      value: '$425,000',
      description: 'Reduced MTTR by 85% through AI-powered incident analysis and automated resolution workflows',
      impact: 'High Impact',
      change: '+15%'
    },
    {
      name: 'Infrastructure Optimization',
      value: '$320,000',
      description: '30% reduction in cloud costs through predictive scaling and resource optimization',
      impact: 'Medium Impact',
      change: '+8%'
    },
    {
      name: 'Operational Efficiency',
      value: '$285,000',
      description: '2000+ hours saved monthly through automation of routine IT operations',
      impact: 'High Impact',
      change: '+22%'
    },
    {
      name: 'Compliance Automation',
      value: '$180,000',
      description: 'Automated SOC2, HIPAA, and GDPR compliance monitoring and reporting',
      impact: 'Medium Impact',
      change: '+12%'
    },
    {
      name: 'Predictive Maintenance',
      value: '$150,000',
      description: 'Prevented 95% of system failures through predictive analytics',
      impact: 'High Impact',
      change: '+18%'
    }
  ];

  const costBreakdown = [
    { category: 'Licensing & Subscriptions', amount: 45000, percentage: 18 },
    { category: 'Infrastructure & Cloud', amount: 75000, percentage: 30 },
    { category: 'Implementation & Setup', amount: 62500, percentage: 25 },
    { category: 'Training & Support', amount: 37500, percentage: 15 },
    { category: 'Maintenance & Updates', amount: 30000, percentage: 12 }
  ];

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  const getTrendClass = (value) => {
    if (value > 0) return 'up';
    if (value < 0) return 'down';
    return 'neutral';
  };

  const getTrendIcon = (value) => {
    if (value > 0) return '↑';
    if (value < 0) return '↓';
    return '→';
  };

  return (
    <div className="business-value-app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo-section">
            <div className="logo-icon">💰</div>
            <div className="logo-text">iTechSmart Business Value Dashboard</div>
          </div>
          <div className="header-controls">
            <select 
              className="time-range-selector"
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
              <option value="1y">Last Year</option>
            </select>
            <button className="refresh-button">
              🔄 Refresh
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* KPI Cards */}
        <div className="kpi-grid">
          <div className="kpi-card fade-in">
            <div className="kpi-header">
              <div className="kpi-title">Total ROI</div>
              <div className="kpi-icon">📈</div>
            </div>
            <div className="kpi-value">{kpis.totalROI.toFixed(1)}%</div>
            <div className="kpi-change positive">
              <span className="trend-indicator up">
                {getTrendIcon(12.3)} 12.3%
              </span>
              vs last period
            </div>
            <div className="kpi-sparkline">
              <div className="chart-placeholder">
                <div className="chart-icon">📊</div>
              </div>
            </div>
          </div>

          <div className="kpi-card fade-in">
            <div className="kpi-header">
              <div className="kpi-title">Cost Savings</div>
              <div className="kpi-icon">💵</div>
            </div>
            <div className="kpi-value">{formatCurrency(kpis.costSavings)}</div>
            <div className="kpi-change positive">
              <span className="trend-indicator up">
                {getTrendIcon(8.7)} 8.7%
              </span>
              vs last period
            </div>
            <div className="kpi-sparkline">
              <div className="chart-placeholder">
                <div className="chart-icon">📉</div>
              </div>
            </div>
          </div>

          <div className="kpi-card fade-in">
            <div className="kpi-header">
              <div className="kpi-title">Revenue Generated</div>
              <div className="kpi-icon">💎</div>
            </div>
            <div className="kpi-value">{formatCurrency(kpis.revenueGenerated)}</div>
            <div className="kpi-change positive">
              <span className="trend-indicator up">
                {getTrendIcon(15.2)} 15.2%
              </span>
              vs last period
            </div>
            <div className="kpi-sparkline">
              <div className="chart-placeholder">
                <div className="chart-icon">📈</div>
              </div>
            </div>
          </div>

          <div className="kpi-card fade-in">
            <div className="kpi-header">
              <div className="kpi-title">Automation Value</div>
              <div className="kpi-icon">🤖</div>
            </div>
            <div className="kpi-value">{formatCurrency(kpis.automationValue)}</div>
            <div className="kpi-change positive">
              <span className="trend-indicator up">
                {getTrendIcon(22.1)} 22.1%
              </span>
              vs last period
            </div>
            <div className="kpi-sparkline">
              <div className="chart-placeholder">
                <div className="chart-icon">⚙️</div>
              </div>
            </div>
          </div>

          <div className="kpi-card fade-in">
            <div className="kpi-header">
              <div className="kpi-title">Efficiency Gain</div>
              <div className="kpi-icon">⚡</div>
            </div>
            <div className="kpi-value">{kpis.efficiencyGain.toFixed(1)}%</div>
            <div className="kpi-change positive">
              <span className="trend-indicator up">
                {getTrendIcon(5.4)} 5.4%
              </span>
              improvement
            </div>
            <div className="kpi-sparkline">
              <div className="chart-placeholder">
                <div className="chart-icon">📊</div>
              </div>
            </div>
          </div>

          <div className="kpi-card fade-in">
            <div className="kpi-header">
              <div className="kpi-title">Risk Reduction</div>
              <div className="kpi-icon">🛡️</div>
            </div>
            <div className="kpi-value">{kpis.riskReduction.toFixed(1)}%</div>
            <div className="kpi-change positive">
              <span className="trend-indicator up">
                {getTrendIcon(3.2)} 3.2%
              </span>
              reduction
            </div>
            <div className="kpi-sparkline">
              <div className="chart-placeholder">
                <div className="chart-icon">🔽</div>
              </div>
            </div>
          </div>
        </div>

        {/* Dashboard Grid */}
        <div className="dashboard-grid">
          {/* Value Drivers */}
          <div className="card fade-in">
            <div className="card-header">
              <div className="card-title">
                <div className="card-icon">🎯</div>
                Value Drivers
              </div>
              <div className="card-actions">
                <button className="action-button">Export</button>
                <button className="action-button">Details</button>
              </div>
            </div>
            
            <div className="value-drivers">
              {valueDrivers.map((driver, index) => (
                <div key={index} className="driver-item">
                  <div className="driver-header">
                    <div className="driver-name">{driver.name}</div>
                    <div className="driver-value">{driver.value}</div>
                  </div>
                  <div className="driver-description">{driver.description}</div>
                  <div className="driver-impact">
                    <span className="trend-indicator up">
                      {getTrendIcon(parseFloat(driver.change))} {driver.change}
                    </span>
                    <span>{driver.impact}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* ROI Calculator */}
          <div className="card fade-in">
            <div className="card-header">
              <div className="card-title">
                <div className="card-icon">🧮</div>
                ROI Calculator
              </div>
              <div className="card-actions">
                <button className="action-button">Reset</button>
              </div>
            </div>
            
            <div className="roi-calculator">
              <div className="input-group">
                <label className="input-label">Initial Investment</label>
                <input
                  type="number"
                  className="input-field"
                  value={roiInputs.initialInvestment}
                  onChange={(e) => setRoiInputs({...roiInputs, initialInvestment: Number(e.target.value)})}
                />
              </div>
              
              <div className="input-group">
                <label className="input-label">Annual Savings</label>
                <input
                  type="number"
                  className="input-field"
                  value={roiInputs.annualSavings}
                  onChange={(e) => setRoiInputs({...roiInputs, annualSavings: Number(e.target.value)})}
                />
              </div>
              
              <div className="input-group">
                <label className="input-label">Revenue Increase</label>
                <input
                  type="number"
                  className="input-field"
                  value={roiInputs.revenueIncrease}
                  onChange={(e) => setRoiInputs({...roiInputs, revenueIncrease: Number(e.target.value)})}
                />
              </div>
              
              <div className="input-group">
                <label className="input-label">Time Horizon (years)</label>
                <input
                  type="number"
                  className="input-field"
                  value={roiInputs.timeHorizon}
                  onChange={(e) => setRoiInputs({...roiInputs, timeHorizon: Number(e.target.value)})}
                />
              </div>
            </div>
            
            <button className="calculate-button" onClick={calculateROI}>
              Calculate ROI
            </button>
            
            {calculatedROI && (
              <div className="roi-result">
                <div className="roi-value">{calculatedROI.roi}%</div>
                <div className="roi-description">
                  ROI over {roiInputs.timeHorizon} years with {calculatedROI.paybackPeriod} year payback period
                </div>
                <div style={{ marginTop: '1rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                  <div>Total Benefits: {formatCurrency(calculatedROI.totalBenefits)}</div>
                  <div>Net Benefit: {formatCurrency(calculatedROI.netBenefit)}</div>
                </div>
              </div>
            )}
          </div>

          {/* Cost Breakdown */}
          <div className="card fade-in">
            <div className="card-header">
              <div className="card-title">
                <div className="card-icon">💳</div>
                Cost Breakdown
              </div>
              <div className="card-actions">
                <button className="action-button">Details</button>
              </div>
            </div>
            
            <div className="cost-breakdown">
              {costBreakdown.map((item, index) => (
                <div key={index} className="cost-item">
                  <div>
                    <div className="cost-category">{item.category}</div>
                    <div className="cost-percentage">{item.percentage}% of total</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div className="cost-amount">{formatCurrency(item.amount)}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Performance Trends */}
          <div className="card fade-in">
            <div className="card-header">
              <div className="card-title">
                <div className="card-icon">📈</div>
                Performance Trends
              </div>
              <div className="card-actions">
                <button className="action-button">Full Report</button>
              </div>
            </div>
            
            <div className="chart-container">
              <div className="chart-placeholder">
                <div className="chart-icon">📊</div>
                <div>Performance trends chart</div>
                <div style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
                  Showing ROI trends over selected time period
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default iTechSmartBusinessValue;