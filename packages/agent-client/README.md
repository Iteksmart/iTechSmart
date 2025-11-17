# @itechsmart/agent-client

Shared client library for iTechSmart Agent integration across all iTechSmart products.

## Installation

```bash
npm install @itechsmart/agent-client
```

## Usage

### Basic Setup

```typescript
import { AgentClient } from '@itechsmart/agent-client';

const client = new AgentClient({
  serverUrl: 'https://license-server.itechsmart.dev',
  token: 'your-jwt-token', // or apiKey: 'your-api-key'
  autoConnect: true, // Auto-connect WebSocket (default: true)
});

// Listen for connection
client.on('connected', () => {
  console.log('Connected to agent server');
});

// Listen for agent events
client.on('agent:metrics', (data) => {
  console.log('New metrics:', data);
});

client.on('agent:alert', (data) => {
  console.log('New alert:', data);
});
```

### Get All Agents

```typescript
const { agents, total } = await client.getAgents({
  status: 'ACTIVE',
  limit: 100,
  offset: 0,
});

console.log(`Found ${total} agents`);
agents.forEach(agent => {
  console.log(`${agent.hostname} - ${agent.status}`);
});
```

### Get Agent Details

```typescript
const agent = await client.getAgent('agent-id');
console.log(agent);
```

### Get System Metrics

```typescript
const metrics = await client.getSystemMetrics('agent-id');
if (metrics) {
  console.log(`CPU: ${metrics.cpu}%`);
  console.log(`Memory: ${metrics.memory}%`);
  console.log(`Disk: ${metrics.disk}%`);
}
```

### Get Security Status

```typescript
const security = await client.getSecurityStatus('agent-id');
if (security) {
  console.log(`Firewall: ${security.firewallEnabled ? 'Enabled' : 'Disabled'}`);
  console.log(`Antivirus: ${security.antivirusEnabled ? 'Enabled' : 'Disabled'}`);
  console.log(`Updates Available: ${security.updatesAvailable}`);
}
```

### Get Alerts

```typescript
const { alerts } = await client.getAlerts('agent-id', {
  resolved: false,
  severity: 'CRITICAL',
  limit: 10,
});

alerts.forEach(alert => {
  console.log(`[${alert.severity}] ${alert.message}`);
});
```

### Resolve Alert

```typescript
await client.resolveAlert('agent-id', 'alert-id');
```

### Execute Command

```typescript
// Execute shell command
const command = await client.executeCommand('agent-id', 'systemctl restart nginx');
console.log(`Command status: ${command.status}`);

// Or use sendCommand for custom commands
const result = await client.sendCommand('agent-id', {
  commandType: 'execute',
  commandData: {
    command: 'df -h',
  },
});
```

### Restart Agent

```typescript
await client.restartAgent('agent-id');
```

### Update Agent Configuration

```typescript
await client.updateAgentConfig('agent-id', {
  collection_interval: 30,
  metrics_enabled: true,
  security_checks_enabled: true,
});
```

### Real-Time Events

```typescript
// Agent connected
client.on('agent:connected', (data) => {
  console.log(`Agent ${data.agentId} connected`);
});

// Agent disconnected
client.on('agent:disconnected', (data) => {
  console.log(`Agent ${data.agentId} disconnected`);
});

// New metrics
client.on('agent:metrics', (data) => {
  console.log(`Metrics from ${data.agentId}:`, data.metricData);
});

// New alert
client.on('agent:alert', (data) => {
  console.log(`Alert from ${data.agentId}: ${data.message}`);
});

// Command result
client.on('agent:command:result', (data) => {
  console.log(`Command ${data.commandId} result:`, data.result);
});

// Agent status update
client.on('agents:status', (data) => {
  console.log('Agent status update:', data.agents);
});
```

### Disconnect

```typescript
client.disconnect();
```

## API Reference

### Constructor

```typescript
new AgentClient(config: AgentClientConfig)
```

**Config Options:**
- `serverUrl` (string, required): License Server URL
- `token` (string, optional): JWT token for authentication
- `apiKey` (string, optional): API key for authentication
- `autoConnect` (boolean, optional): Auto-connect WebSocket (default: true)

### Methods

#### Agent Management
- `getAgents(params?)`: Get all agents
- `getAgent(agentId)`: Get agent by ID
- `updateAgent(agentId, data)`: Update agent configuration
- `deleteAgent(agentId)`: Delete agent

#### Metrics
- `getMetrics(agentId, params?)`: Get agent metrics
- `submitMetrics(agentId, data)`: Submit metrics (for agent use)
- `getSystemMetrics(agentId)`: Get latest system metrics
- `getSecurityStatus(agentId)`: Get latest security status

#### Alerts
- `getAlerts(agentId, params?)`: Get agent alerts
- `resolveAlert(agentId, alertId)`: Resolve alert
- `getUnresolvedAlertsCount(agentId)`: Get unresolved alerts count

#### Commands
- `sendCommand(agentId, command)`: Send command to agent
- `getCommands(agentId, params?)`: Get agent commands
- `executeCommand(agentId, command)`: Execute shell command
- `restartAgent(agentId)`: Restart agent
- `updateAgentConfig(agentId, config)`: Update agent configuration

#### Connection
- `connect()`: Connect to WebSocket
- `disconnect()`: Disconnect from WebSocket
- `isConnected()`: Check connection status

### Events

- `connected`: WebSocket connected
- `disconnected`: WebSocket disconnected
- `error`: Error occurred
- `agent:connected`: Agent connected
- `agent:disconnected`: Agent disconnected
- `agent:metrics`: New metrics received
- `agent:alert`: New alert received
- `agent:command:result`: Command result received
- `agents:status`: Agent status update

## TypeScript Support

Full TypeScript support with type definitions included.

```typescript
import { 
  AgentClient, 
  Agent, 
  AgentMetric, 
  AgentAlert, 
  AgentCommand,
  AgentStatus,
  AlertSeverity,
  CommandStatus 
} from '@itechsmart/agent-client';
```

## Examples

### React Component

```typescript
import React, { useEffect, useState } from 'react';
import { AgentClient, Agent } from '@itechsmart/agent-client';

const AgentDashboard: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [client] = useState(() => new AgentClient({
    serverUrl: process.env.REACT_APP_LICENSE_SERVER_URL!,
    token: localStorage.getItem('token')!,
  }));

  useEffect(() => {
    // Load agents
    client.getAgents().then(({ agents }) => {
      setAgents(agents);
    });

    // Listen for updates
    client.on('agent:connected', () => {
      client.getAgents().then(({ agents }) => setAgents(agents));
    });

    client.on('agent:disconnected', () => {
      client.getAgents().then(({ agents }) => setAgents(agents));
    });

    return () => {
      client.disconnect();
    };
  }, [client]);

  return (
    <div>
      <h1>Agents ({agents.length})</h1>
      {agents.map(agent => (
        <div key={agent.id}>
          {agent.hostname} - {agent.status}
        </div>
      ))}
    </div>
  );
};
```

### Node.js Backend

```typescript
import { AgentClient } from '@itechsmart/agent-client';

const client = new AgentClient({
  serverUrl: process.env.LICENSE_SERVER_URL!,
  apiKey: process.env.LICENSE_SERVER_API_KEY!,
});

// Monitor all agents
client.on('agent:alert', async (data) => {
  if (data.severity === 'CRITICAL') {
    // Send notification
    await sendNotification({
      title: 'Critical Alert',
      message: data.message,
      agentId: data.agentId,
    });
  }
});

// Auto-remediation
client.on('agent:metrics', async (data) => {
  if (data.metricData.disk_percent > 90) {
    // Clean up disk space
    await client.executeCommand(data.agentId, 'docker system prune -af');
  }
});
```

## License

Proprietary - © 2025 iTechSmart Inc. All rights reserved.