# Agent Client Library Integration Guide

**Version**: 1.0.0  
**Date**: November 17, 2025  
**Status**: Ready for Integration

---

## Overview

This guide provides step-by-step instructions for integrating the `@itechsmart/agent-client` library into iTechSmart products. The library provides a unified interface for accessing agent data and functionality through the License Server.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Basic Setup](#basic-setup)
4. [Integration Levels](#integration-levels)
5. [Product-Specific Integration](#product-specific-integration)
6. [API Reference](#api-reference)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- Node.js 18+ or compatible runtime
- Access to License Server
- Valid authentication token
- Network connectivity to License Server

### Optional
- TypeScript 5.0+ (for type support)
- React 18+ (for UI components)
- Vue 3+ or Angular 15+ (alternative frameworks)

---

## Installation

### Option 1: Local Package (Development)

```bash
# From your product directory
npm install ../../packages/agent-client
```

### Option 2: npm Registry (Production - Coming Soon)

```bash
npm install @itechsmart/agent-client
```

### Option 3: Direct File Link

```json
{
  "dependencies": {
    "@itechsmart/agent-client": "file:../../packages/agent-client"
  }
}
```

---

## Basic Setup

### 1. Environment Configuration

Add to your `.env` file:

```bash
LICENSE_SERVER_URL=https://license-server.itechsmart.dev
# or for local development
LICENSE_SERVER_URL=http://localhost:3000
```

### 2. Initialize Client

```typescript
import { AgentClient } from '@itechsmart/agent-client';

const client = new AgentClient({
  serverUrl: process.env.LICENSE_SERVER_URL || 'http://localhost:3000',
  token: userAuthToken, // From your authentication system
});
```

### 3. Basic Usage

```typescript
// Get all agents
const { agents, total } = await client.getAgents();

// Get specific agent
const agent = await client.getAgent('agent-id');

// Get system metrics
const metrics = await client.getSystemMetrics('agent-id');

// Get security status
const security = await client.getSecurityStatus('agent-id');
```

---

## Integration Levels

### Level 1: Basic Awareness (5 minutes)
**What**: Configuration only, no UI changes  
**Who**: All Tier 3 products (27 products)  
**Effort**: 5 minutes per product

**Steps**:
1. Add environment variable
2. Install client library
3. Initialize client in config
4. Done!

**Example**:
```typescript
// config/agent.ts
import { AgentClient } from '@itechsmart/agent-client';

export const agentClient = new AgentClient({
  serverUrl: process.env.LICENSE_SERVER_URL,
  token: process.env.AUTH_TOKEN,
});
```

---

### Level 2: Display Integration (1-2 hours)
**What**: Status widgets and basic displays  
**Who**: Tier 2 products (5 products)  
**Effort**: 1-2 hours per product

**Components to Add**:
- Agent status badge
- System health indicator
- Alert counter
- Quick stats widget

**Example Component**:
```typescript
// components/AgentStatusWidget.tsx
import { useEffect, useState } from 'react';
import { agentClient } from '../config/agent';

export function AgentStatusWidget() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const loadStats = async () => {
      const { agents } = await agentClient.getAgents();
      const activeCount = agents.filter(a => a.status === 'ACTIVE').length;
      setStats({ total: agents.length, active: activeCount });
    };
    loadStats();
  }, []);

  if (!stats) return <div>Loading...</div>;

  return (
    <div className="agent-status-widget">
      <h3>Agent Status</h3>
      <p>{stats.active} / {stats.total} Active</p>
    </div>
  );
}
```

---

### Level 3: Full Integration (1-2 days)
**What**: Complete agent management UI  
**Who**: Tier 1 products (5 products)  
**Effort**: 1-2 days per product

**Features to Implement**:
- Agent list/grid view
- Agent detail pages
- Real-time metrics dashboard
- Alert management
- Command execution
- Historical data charts

**Pages to Create**:
1. `/agents` - Agent list
2. `/agents/:id` - Agent details
3. `/agents/:id/metrics` - Metrics dashboard
4. `/agents/:id/alerts` - Alert management
5. `/agents/:id/commands` - Command center

---

## Product-Specific Integration

### iTechSmart Ninja (RMM Platform)

**Priority**: HIGH (Tier 1 - Full Integration)  
**Timeline**: 1-2 days  
**Complexity**: Medium

**Integration Points**:
1. Dashboard - Add agent overview widget
2. Devices Page - Show agent status per device
3. Monitoring - Display real-time metrics
4. Alerts - Integrate agent alerts
5. Remote Control - Use agent commands

**New Routes**:
```typescript
// src/routes/agents.ts
import { Router } from 'express';
import { agentClient } from '../config/agent';

const router = Router();

router.get('/agents', async (req, res) => {
  const { agents, total } = await agentClient.getAgents();
  res.json({ agents, total });
});

router.get('/agents/:id', async (req, res) => {
  const agent = await agentClient.getAgent(req.params.id);
  res.json(agent);
});

export default router;
```

**UI Components**:
```typescript
// src/components/AgentDashboard.tsx
import { AgentList } from './AgentList';
import { AgentMetrics } from './AgentMetrics';
import { AgentAlerts } from './AgentAlerts';

export function AgentDashboard() {
  return (
    <div className="agent-dashboard">
      <h1>Agent Management</h1>
      <AgentList />
      <AgentMetrics />
      <AgentAlerts />
    </div>
  );
}
```

---

### iTechSmart Enterprise (Business Suite)

**Priority**: HIGH (Tier 1 - Full Integration)  
**Timeline**: 1-2 days  
**Complexity**: Medium

**Integration Points**:
1. Admin Dashboard - Agent overview
2. System Health - Real-time monitoring
3. Reports - Agent data analytics
4. Settings - Agent configuration

**Features**:
- Executive dashboard with agent KPIs
- System health monitoring
- Compliance reporting
- Resource utilization tracking

---

### iTechSmart Supreme (Advanced Analytics)

**Priority**: HIGH (Tier 1 - Full Integration)  
**Timeline**: 1-2 days  
**Complexity**: High

**Integration Points**:
1. Analytics Dashboard - Agent metrics
2. Predictive Analysis - Agent data trends
3. Reports - Custom agent reports
4. Visualizations - Agent data charts

**Features**:
- Advanced analytics on agent data
- Predictive maintenance insights
- Custom reporting
- Data visualization

---

### iTechSmart Citadel (Security Platform)

**Priority**: HIGH (Tier 1 - Full Integration)  
**Timeline**: 1-2 days  
**Complexity**: High

**Integration Points**:
1. Security Dashboard - Agent security status
2. Threat Detection - Agent alerts
3. Compliance - Agent compliance checks
4. Incident Response - Agent commands

**Features**:
- Security posture monitoring
- Threat detection and response
- Compliance tracking
- Incident management

---

### Desktop Launcher

**Priority**: HIGH (Tier 1 - Full Integration)  
**Timeline**: 1-2 days  
**Complexity**: Medium

**Integration Points**:
1. System Tray - Agent status indicator
2. Quick Actions - Agent commands
3. Notifications - Agent alerts
4. Settings - Agent configuration

**Features**:
- System tray integration
- Quick access to agent features
- Real-time notifications
- Agent management

---

## API Reference

### AgentClient Class

#### Constructor
```typescript
new AgentClient(config: AgentClientConfig)
```

**Parameters**:
- `serverUrl`: License Server URL
- `token`: Authentication token
- `timeout?`: Request timeout (default: 30000ms)

#### Methods

##### getAgents()
```typescript
getAgents(params?: {
  page?: number;
  limit?: number;
  status?: AgentStatus;
  search?: string;
}): Promise<{ agents: Agent[]; total: number; }>
```

##### getAgent()
```typescript
getAgent(agentId: string): Promise<Agent>
```

##### updateAgent()
```typescript
updateAgent(agentId: string, data: Partial<Agent>): Promise<Agent>
```

##### deleteAgent()
```typescript
deleteAgent(agentId: string): Promise<void>
```

##### submitMetrics()
```typescript
submitMetrics(agentId: string, metrics: SystemMetrics): Promise<void>
```

##### getMetrics()
```typescript
getMetrics(agentId: string, params?: {
  startDate?: Date;
  endDate?: Date;
  limit?: number;
}): Promise<AgentMetric[]>
```

##### getLatestMetrics()
```typescript
getLatestMetrics(agentId: string): Promise<AgentMetric>
```

##### getSystemMetrics()
```typescript
getSystemMetrics(agentId: string): Promise<SystemMetrics>
```

##### getSecurityStatus()
```typescript
getSecurityStatus(agentId: string): Promise<SecurityStatus>
```

##### getAlerts()
```typescript
getAlerts(agentId: string, params?: {
  severity?: AlertSeverity;
  resolved?: boolean;
}): Promise<AgentAlert[]>
```

##### resolveAlert()
```typescript
resolveAlert(agentId: string, alertId: string): Promise<void>
```

##### getUnresolvedAlertCount()
```typescript
getUnresolvedAlertCount(agentId: string): Promise<number>
```

##### sendCommand()
```typescript
sendCommand(agentId: string, command: string, params?: any): Promise<AgentCommand>
```

##### executeCommand()
```typescript
executeCommand(agentId: string, command: string, params?: any): Promise<any>
```

##### getCommands()
```typescript
getCommands(agentId: string): Promise<AgentCommand[]>
```

##### getCommandStatus()
```typescript
getCommandStatus(agentId: string, commandId: string): Promise<AgentCommand>
```

##### connect()
```typescript
connect(): void
```

##### disconnect()
```typescript
disconnect(): void
```

##### on()
```typescript
on(event: string, handler: Function): void
```

---

## Examples

### Example 1: Simple Agent List

```typescript
import { AgentClient } from '@itechsmart/agent-client';

const client = new AgentClient({
  serverUrl: process.env.LICENSE_SERVER_URL,
  token: userToken,
});

async function listAgents() {
  const { agents, total } = await client.getAgents();
  
  console.log(`Total agents: ${total}`);
  agents.forEach(agent => {
    console.log(`- ${agent.hostname} (${agent.status})`);
  });
}
```

### Example 2: Real-time Metrics

```typescript
import { AgentClient } from '@itechsmart/agent-client';

const client = new AgentClient({
  serverUrl: process.env.LICENSE_SERVER_URL,
  token: userToken,
});

// Connect to WebSocket
client.connect();

// Listen for metrics
client.on('agent:metrics', (data) => {
  console.log('New metrics:', data);
  updateDashboard(data);
});

// Listen for alerts
client.on('agent:alert', (alert) => {
  console.log('New alert:', alert);
  showNotification(alert);
});
```

### Example 3: Execute Command

```typescript
import { AgentClient } from '@itechsmart/agent-client';

const client = new AgentClient({
  serverUrl: process.env.LICENSE_SERVER_URL,
  token: userToken,
});

async function restartService(agentId: string) {
  try {
    const result = await client.executeCommand(
      agentId,
      'restart_service',
      { serviceName: 'nginx' }
    );
    
    console.log('Service restarted:', result);
  } catch (error) {
    console.error('Failed to restart service:', error);
  }
}
```

### Example 4: React Component

```typescript
import { useEffect, useState } from 'react';
import { AgentClient } from '@itechsmart/agent-client';

const client = new AgentClient({
  serverUrl: process.env.REACT_APP_LICENSE_SERVER_URL,
  token: localStorage.getItem('authToken'),
});

export function AgentList() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAgents();
  }, []);

  async function loadAgents() {
    try {
      const { agents } = await client.getAgents();
      setAgents(agents);
    } catch (error) {
      console.error('Failed to load agents:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div>Loading...</div>;

  return (
    <div className="agent-list">
      <h2>Agents ({agents.length})</h2>
      <ul>
        {agents.map(agent => (
          <li key={agent.id}>
            <strong>{agent.hostname}</strong>
            <span className={`status ${agent.status.toLowerCase()}`}>
              {agent.status}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## Troubleshooting

### Common Issues

#### 1. Connection Refused
**Problem**: Cannot connect to License Server  
**Solution**: 
- Check LICENSE_SERVER_URL is correct
- Verify License Server is running
- Check network connectivity
- Verify firewall rules

#### 2. Authentication Failed
**Problem**: 401 Unauthorized error  
**Solution**:
- Verify token is valid
- Check token expiration
- Ensure token has correct permissions
- Re-authenticate if needed

#### 3. WebSocket Connection Failed
**Problem**: Real-time updates not working  
**Solution**:
- Check WebSocket URL (ws:// or wss://)
- Verify WebSocket port is open
- Check proxy/firewall settings
- Try reconnecting

#### 4. TypeScript Errors
**Problem**: Type errors when using library  
**Solution**:
- Ensure TypeScript 5.0+ is installed
- Check tsconfig.json includes node_modules
- Import types explicitly if needed
- Update @types/node if needed

---

## Best Practices

### 1. Error Handling
Always wrap API calls in try-catch blocks:

```typescript
try {
  const agents = await client.getAgents();
  // Handle success
} catch (error) {
  console.error('Failed to load agents:', error);
  // Handle error
}
```

### 2. Loading States
Show loading indicators during API calls:

```typescript
const [loading, setLoading] = useState(true);

useEffect(() => {
  loadData().finally(() => setLoading(false));
}, []);
```

### 3. Caching
Cache agent data to reduce API calls:

```typescript
const cache = new Map();

async function getAgent(id: string) {
  if (cache.has(id)) {
    return cache.get(id);
  }
  
  const agent = await client.getAgent(id);
  cache.set(id, agent);
  return agent;
}
```

### 4. Real-time Updates
Use WebSocket for real-time data:

```typescript
client.connect();

client.on('agent:metrics', (data) => {
  updateUI(data);
});

// Clean up on unmount
return () => client.disconnect();
```

---

## Support

### Documentation
- Main README: `/packages/agent-client/README.md`
- API Docs: `/docs/api/agent-client.md`
- Examples: `/examples/agent-client/`

### Contact
- Email: support@itechsmart.dev
- GitHub: https://github.com/Iteksmart/iTechSmart
- Website: https://itechsmart.dev

---

**© 2025 iTechSmart Inc. All rights reserved.**