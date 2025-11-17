import { Router, Request, Response } from 'express';
import { PrismaClient, AgentStatus, AlertSeverity, CommandStatus } from '@prisma/client';
import { authenticateApiKey, authenticateJWT } from '../middleware/auth';
import { generateApiKey } from '../utils/crypto';
import { z } from 'zod';

const router = Router();
const prisma = new PrismaClient();

// Validation schemas
const registerAgentSchema = z.object({
  hostname: z.string().min(1).max(255),
  ipAddress: z.string().ip().optional(),
  osType: z.enum(['linux', 'windows', 'darwin']),
  osVersion: z.string().optional(),
  agentVersion: z.string(),
  config: z.record(z.any()).optional(),
});

const submitMetricsSchema = z.object({
  timestamp: z.string().datetime().optional(),
  metricType: z.string(),
  metricData: z.record(z.any()),
});

const createCommandSchema = z.object({
  commandType: z.string(),
  commandData: z.record(z.any()),
});

// Register new agent
router.post('/register', authenticateApiKey, async (req: Request, res: Response) => {
  try {
    const data = registerAgentSchema.parse(req.body);
    const organizationId = (req as any).organization.id;

    // Check if agent already exists
    const existingAgent = await prisma.agent.findUnique({
      where: {
        organizationId_hostname: {
          organizationId,
          hostname: data.hostname,
        },
      },
    });

    if (existingAgent) {
      // Update existing agent
      const agent = await prisma.agent.update({
        where: { id: existingAgent.id },
        data: {
          ipAddress: data.ipAddress,
          osType: data.osType,
          osVersion: data.osVersion,
          agentVersion: data.agentVersion,
          config: data.config || {},
          status: AgentStatus.ACTIVE,
          lastSeen: new Date(),
        },
      });

      return res.json({
        id: agent.id,
        apiKey: agent.apiKey,
        websocketUrl: `${process.env.WEBSOCKET_URL || 'wss://localhost:3000'}/ws/agents`,
        status: 'updated',
      });
    }

    // Create new agent
    const apiKey = `agent_${generateApiKey()}`;
    
    const agent = await prisma.agent.create({
      data: {
        organizationId,
        hostname: data.hostname,
        ipAddress: data.ipAddress,
        osType: data.osType,
        osVersion: data.osVersion,
        agentVersion: data.agentVersion,
        config: data.config || {},
        apiKey,
        status: AgentStatus.ACTIVE,
        lastSeen: new Date(),
      },
    });

    res.status(201).json({
      id: agent.id,
      apiKey: agent.apiKey,
      websocketUrl: `${process.env.WEBSOCKET_URL || 'wss://localhost:3000'}/ws/agents`,
      status: 'created',
    });
  } catch (error) {
    console.error('Agent registration error:', error);
    if (error instanceof z.ZodError) {
      return res.status(400).json({ error: 'Invalid request data', details: error.errors });
    }
    res.status(500).json({ error: 'Failed to register agent' });
  }
});

// List all agents for organization
router.get('/', authenticateJWT, async (req: Request, res: Response) => {
  try {
    const organizationId = (req as any).user.organizationId;
    const { status, limit = 100, offset = 0 } = req.query;

    const where: any = { organizationId };
    if (status) {
      where.status = status;
    }

    const [agents, total] = await Promise.all([
      prisma.agent.findMany({
        where,
        include: {
          license: {
            select: {
              licenseKey: true,
              tier: true,
              status: true,
            },
          },
          _count: {
            select: {
              metrics: true,
              alerts: { where: { resolved: false } },
              commands: { where: { status: CommandStatus.PENDING } },
            },
          },
        },
        orderBy: { lastSeen: 'desc' },
        take: Number(limit),
        skip: Number(offset),
      }),
      prisma.agent.count({ where }),
    ]);

    res.json({
      agents,
      total,
      limit: Number(limit),
      offset: Number(offset),
    });
  } catch (error) {
    console.error('List agents error:', error);
    res.status(500).json({ error: 'Failed to list agents' });
  }
});

// Get agent details
router.get('/:id', authenticateJWT, async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const organizationId = (req as any).user.organizationId;

    const agent = await prisma.agent.findFirst({
      where: { id, organizationId },
      include: {
        license: true,
        _count: {
          select: {
            metrics: true,
            alerts: { where: { resolved: false } },
            commands: { where: { status: CommandStatus.PENDING } },
          },
        },
      },
    });

    if (!agent) {
      return res.status(404).json({ error: 'Agent not found' });
    }

    res.json(agent);
  } catch (error) {
    console.error('Get agent error:', error);
    res.status(500).json({ error: 'Failed to get agent' });
  }
});

// Update agent configuration
router.put('/:id', authenticateJWT, async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const organizationId = (req as any).user.organizationId;
    const { config, status } = req.body;

    const agent = await prisma.agent.findFirst({
      where: { id, organizationId },
    });

    if (!agent) {
      return res.status(404).json({ error: 'Agent not found' });
    }

    const updatedAgent = await prisma.agent.update({
      where: { id },
      data: {
        config: config || agent.config,
        status: status || agent.status,
      },
    });

    res.json(updatedAgent);
  } catch (error) {
    console.error('Update agent error:', error);
    res.status(500).json({ error: 'Failed to update agent' });
  }
});

// Delete agent
router.delete('/:id', authenticateJWT, async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const organizationId = (req as any).user.organizationId;

    const agent = await prisma.agent.findFirst({
      where: { id, organizationId },
    });

    if (!agent) {
      return res.status(404).json({ error: 'Agent not found' });
    }

    await prisma.agent.delete({ where: { id } });

    res.json({ message: 'Agent deleted successfully' });
  } catch (error) {
    console.error('Delete agent error:', error);
    res.status(500).json({ error: 'Failed to delete agent' });
  }
});

// Submit metrics (called by agent)
router.post('/:id/metrics', authenticateApiKey, async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const data = submitMetricsSchema.parse(req.body);

    // Verify agent exists and belongs to organization
    const agent = await prisma.agent.findFirst({
      where: { 
        id,
        organizationId: (req as any).organization.id,
      },
    });

    if (!agent) {
      return res.status(404).json({ error: 'Agent not found' });
    }

    // Create metric record
    await prisma.agentMetric.create({
      data: {
        agentId: id,
        metricType: data.metricType,
        metricData: data.metricData,
        timestamp: data.timestamp ? new Date(data.timestamp) : new Date(),
      },
    });

    // Update agent last seen
    await prisma.agent.update({
      where: { id },
      data: { 
        lastSeen: new Date(),
        status: AgentStatus.ACTIVE,
      },
    });

    // Check for alerts based on metrics
    const alerts = await checkMetricsForAlerts(id, data.metricType, data.metricData);

    res.json({
      status: 'received',
      alerts: alerts.map(a => ({
        type: a.alertType,
        severity: a.severity,
        message: a.message,
      })),
    });
  } catch (error) {
    console.error('Submit metrics error:', error);
    if (error instanceof z.ZodError) {
      return res.status(400).json({ error: 'Invalid request data', details: error.errors });
    }
    res.status(500).json({ error: 'Failed to submit metrics' });
  }
});

// Get agent metrics
router.get('/:id/metrics', authenticateJWT, async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const organizationId = (req as any).user.organizationId;
    const { metricType, from, to, limit = 100 } = req.query;

    // Verify agent belongs to organization
    const agent = await prisma.agent.findFirst({
      where: { id, organizationId },
    });

    if (!agent) {
      return res.status(404).json({ error: 'Agent not found' });
    }

    const where: any = { agentId: id };
    if (metricType) {
      where.metricType = metricType;
    }
    if (from || to) {
      where.timestamp = {};
      if (from) where.timestamp.gte = new Date(from as string);
      if (to) where.timestamp.lte = new Date(to as string);
    }

    const metrics = await prisma.agentMetric.findMany({
      where,
      orderBy: { timestamp: 'desc' },
      take: Number(limit),
    });

    res.json({ metrics });
  } catch (error) {
    console.error('Get metrics error:', error);
    res.status(500).json({ error: 'Failed to get metrics' });
  }
});

// Get agent alerts
router.get('/:id/alerts', authenticateJWT, async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const organizationId = (req as any).user.organizationId;
    const { resolved, severity, limit = 100 } = req.query;

    // Verify agent belongs to organization
    const agent = await prisma.agent.findFirst({
      where: { id, organizationId },
    });

    if (!agent) {
      return res.status(404).json({ error: 'Agent not found' });
    }

    const where: any = { agentId: id };
    if (resolved !== undefined) {
      where.resolved = resolved === 'true';
    }
    if (severity) {
      where.severity = severity;
    }

    const alerts = await prisma.agentAlert.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      take: Number(limit),
    });

    res.json({ alerts });
  } catch (error) {
    console.error('Get alerts error:', error);
    res.status(500).json({ error: 'Failed to get alerts' });
  }
});

// Resolve alert
router.put('/:id/alerts/:alertId/resolve', authenticateJWT, async (req: Request, res: Response) => {
  try {
    const { id, alertId } = req.params;
    const organizationId = (req as any).user.organizationId;
    const userId = (req as any).user.id;

    // Verify agent belongs to organization
    const agent = await prisma.agent.findFirst({
      where: { id, organizationId },
    });

    if (!agent) {
      return res.status(404).json({ error: 'Agent not found' });
    }

    const alert = await prisma.agentAlert.update({
      where: { id: alertId },
      data: {
        resolved: true,
        resolvedAt: new Date(),
        resolvedBy: userId,
      },
    });

    res.json(alert);
  } catch (error) {
    console.error('Resolve alert error:', error);
    res.status(500).json({ error: 'Failed to resolve alert' });
  }
});

// Create command for agent
router.post('/:id/commands', authenticateJWT, async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const organizationId = (req as any).user.organizationId;
    const userId = (req as any).user.id;
    const data = createCommandSchema.parse(req.body);

    // Verify agent belongs to organization
    const agent = await prisma.agent.findFirst({
      where: { id, organizationId },
    });

    if (!agent) {
      return res.status(404).json({ error: 'Agent not found' });
    }

    const command = await prisma.agentCommand.create({
      data: {
        agentId: id,
        commandType: data.commandType,
        commandData: data.commandData,
        createdBy: userId,
      },
    });

    res.status(201).json(command);
  } catch (error) {
    console.error('Create command error:', error);
    if (error instanceof z.ZodError) {
      return res.status(400).json({ error: 'Invalid request data', details: error.errors });
    }
    res.status(500).json({ error: 'Failed to create command' });
  }
});

// Get agent commands
router.get('/:id/commands', authenticateJWT, async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const organizationId = (req as any).user.organizationId;
    const { status, limit = 100 } = req.query;

    // Verify agent belongs to organization
    const agent = await prisma.agent.findFirst({
      where: { id, organizationId },
    });

    if (!agent) {
      return res.status(404).json({ error: 'Agent not found' });
    }

    const where: any = { agentId: id };
    if (status) {
      where.status = status;
    }

    const commands = await prisma.agentCommand.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      take: Number(limit),
    });

    res.json({ commands });
  } catch (error) {
    console.error('Get commands error:', error);
    res.status(500).json({ error: 'Failed to get commands' });
  }
});

// Helper function to check metrics for alerts
async function checkMetricsForAlerts(
  agentId: string,
  metricType: string,
  metricData: any
): Promise<any[]> {
  const alerts: any[] = [];

  if (metricType === 'system') {
    // CPU alert
    if (metricData.cpu_percent > 90) {
      const alert = await prisma.agentAlert.create({
        data: {
          agentId,
          alertType: 'cpu',
          severity: AlertSeverity.CRITICAL,
          message: `CPU usage critical: ${metricData.cpu_percent}%`,
          details: { cpu_percent: metricData.cpu_percent },
        },
      });
      alerts.push(alert);
    } else if (metricData.cpu_percent > 80) {
      const alert = await prisma.agentAlert.create({
        data: {
          agentId,
          alertType: 'cpu',
          severity: AlertSeverity.WARNING,
          message: `CPU usage high: ${metricData.cpu_percent}%`,
          details: { cpu_percent: metricData.cpu_percent },
        },
      });
      alerts.push(alert);
    }

    // Memory alert
    if (metricData.memory_percent > 90) {
      const alert = await prisma.agentAlert.create({
        data: {
          agentId,
          alertType: 'memory',
          severity: AlertSeverity.CRITICAL,
          message: `Memory usage critical: ${metricData.memory_percent}%`,
          details: { memory_percent: metricData.memory_percent },
        },
      });
      alerts.push(alert);
    } else if (metricData.memory_percent > 80) {
      const alert = await prisma.agentAlert.create({
        data: {
          agentId,
          alertType: 'memory',
          severity: AlertSeverity.WARNING,
          message: `Memory usage high: ${metricData.memory_percent}%`,
          details: { memory_percent: metricData.memory_percent },
        },
      });
      alerts.push(alert);
    }

    // Disk alert
    if (metricData.disk_percent > 90) {
      const alert = await prisma.agentAlert.create({
        data: {
          agentId,
          alertType: 'disk',
          severity: AlertSeverity.CRITICAL,
          message: `Disk usage critical: ${metricData.disk_percent}%`,
          details: { disk_percent: metricData.disk_percent },
        },
      });
      alerts.push(alert);
    } else if (metricData.disk_percent > 75) {
      const alert = await prisma.agentAlert.create({
        data: {
          agentId,
          alertType: 'disk',
          severity: AlertSeverity.WARNING,
          message: `Disk usage high: ${metricData.disk_percent}%`,
          details: { disk_percent: metricData.disk_percent },
        },
      });
      alerts.push(alert);
    }
  }

  if (metricType === 'security') {
    // Firewall alert
    if (!metricData.firewall_enabled) {
      const alert = await prisma.agentAlert.create({
        data: {
          agentId,
          alertType: 'security',
          severity: AlertSeverity.ERROR,
          message: 'Firewall is disabled',
          details: { firewall_enabled: false },
        },
      });
      alerts.push(alert);
    }

    // Antivirus alert
    if (!metricData.antivirus_enabled) {
      const alert = await prisma.agentAlert.create({
        data: {
          agentId,
          alertType: 'security',
          severity: AlertSeverity.ERROR,
          message: 'Antivirus is disabled',
          details: { antivirus_enabled: false },
        },
      });
      alerts.push(alert);
    }

    // Updates alert
    if (metricData.updates_available > 10) {
      const alert = await prisma.agentAlert.create({
        data: {
          agentId,
          alertType: 'updates',
          severity: AlertSeverity.WARNING,
          message: `${metricData.updates_available} updates available`,
          details: { updates_available: metricData.updates_available },
        },
      });
      alerts.push(alert);
    }
  }

  return alerts;
}

export default router;