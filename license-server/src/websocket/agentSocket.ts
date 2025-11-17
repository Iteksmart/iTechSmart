import { Server as SocketIOServer } from 'socket.io';
import { Server as HTTPServer } from 'http';
import { PrismaClient, AgentStatus, CommandStatus } from '@prisma/client';
import jwt from 'jsonwebtoken';

const prisma = new PrismaClient();

export function setupAgentWebSocket(httpServer: HTTPServer) {
  const io = new SocketIOServer(httpServer, {
    path: '/ws/agents',
    cors: {
      origin: process.env.CORS_ORIGIN || '*',
      methods: ['GET', 'POST'],
    },
  });

  // Authentication middleware
  io.use(async (socket, next) => {
    try {
      const token = socket.handshake.auth.token || socket.handshake.headers.authorization?.replace('Bearer ', '');
      
      if (!token) {
        return next(new Error('Authentication token required'));
      }

      // Check if it's an agent API key
      if (token.startsWith('agent_')) {
        const agent = await prisma.agent.findUnique({
          where: { apiKey: token },
          include: { organization: true },
        });

        if (!agent) {
          return next(new Error('Invalid agent API key'));
        }

        (socket as any).agent = agent;
        (socket as any).agentId = agent.id;
        (socket as any).organizationId = agent.organizationId;
        (socket as any).type = 'agent';
        
        return next();
      }

      // Otherwise, verify JWT token (for dashboard connections)
      const decoded = jwt.verify(token, process.env.JWT_SECRET || 'secret') as any;
      (socket as any).userId = decoded.userId;
      (socket as any).organizationId = decoded.organizationId;
      (socket as any).type = 'dashboard';
      
      next();
    } catch (error) {
      console.error('WebSocket authentication error:', error);
      next(new Error('Authentication failed'));
    }
  });

  io.on('connection', async (socket) => {
    const socketData = socket as any;
    console.log(`WebSocket connected: ${socketData.type} - ${socketData.agentId || socketData.userId}`);

    if (socketData.type === 'agent') {
      // Agent connected
      await handleAgentConnection(socket, socketData.agentId);
    } else {
      // Dashboard connected
      await handleDashboardConnection(socket, socketData.organizationId);
    }

    // Handle disconnection
    socket.on('disconnect', async () => {
      console.log(`WebSocket disconnected: ${socketData.type} - ${socketData.agentId || socketData.userId}`);
      
      if (socketData.type === 'agent') {
        await handleAgentDisconnection(socketData.agentId);
      }
    });

    // Handle agent messages
    if (socketData.type === 'agent') {
      socket.on('metrics', async (data) => {
        await handleAgentMetrics(socketData.agentId, data);
        // Broadcast to dashboards
        io.to(`org:${socketData.organizationId}`).emit('agent:metrics', {
          agentId: socketData.agentId,
          ...data,
        });
      });

      socket.on('alert', async (data) => {
        await handleAgentAlert(socketData.agentId, data);
        // Broadcast to dashboards
        io.to(`org:${socketData.organizationId}`).emit('agent:alert', {
          agentId: socketData.agentId,
          ...data,
        });
      });

      socket.on('command:result', async (data) => {
        await handleCommandResult(data.commandId, data.result, data.error);
        // Broadcast to dashboards
        io.to(`org:${socketData.organizationId}`).emit('agent:command:result', {
          agentId: socketData.agentId,
          ...data,
        });
      });

      socket.on('heartbeat', async () => {
        await prisma.agent.update({
          where: { id: socketData.agentId },
          data: { 
            lastSeen: new Date(),
            status: AgentStatus.ACTIVE,
          },
        });
      });
    }

    // Handle dashboard messages
    if (socketData.type === 'dashboard') {
      socket.on('command:send', async (data) => {
        const { agentId, commandType, commandData } = data;
        
        // Verify agent belongs to organization
        const agent = await prisma.agent.findFirst({
          where: { 
            id: agentId,
            organizationId: socketData.organizationId,
          },
        });

        if (!agent) {
          socket.emit('error', { message: 'Agent not found' });
          return;
        }

        // Create command
        const command = await prisma.agentCommand.create({
          data: {
            agentId,
            commandType,
            commandData,
            createdBy: socketData.userId,
            status: CommandStatus.SENT,
            sentAt: new Date(),
          },
        });

        // Send command to agent
        io.to(`agent:${agentId}`).emit('command', {
          commandId: command.id,
          commandType,
          commandData,
        });

        socket.emit('command:sent', { commandId: command.id });
      });
    }
  });

  return io;
}

async function handleAgentConnection(socket: any, agentId: string) {
  // Join agent room
  socket.join(`agent:${agentId}`);
  
  // Update agent status
  await prisma.agent.update({
    where: { id: agentId },
    data: { 
      status: AgentStatus.ACTIVE,
      lastSeen: new Date(),
    },
  });

  // Get agent organization
  const agent = await prisma.agent.findUnique({
    where: { id: agentId },
    select: { organizationId: true },
  });

  if (agent) {
    // Join organization room
    socket.join(`org:${agent.organizationId}`);
    
    // Notify dashboards
    socket.to(`org:${agent.organizationId}`).emit('agent:connected', { agentId });
  }

  // Send pending commands
  const pendingCommands = await prisma.agentCommand.findMany({
    where: {
      agentId,
      status: CommandStatus.PENDING,
    },
    orderBy: { createdAt: 'asc' },
  });

  for (const command of pendingCommands) {
    socket.emit('command', {
      commandId: command.id,
      commandType: command.commandType,
      commandData: command.commandData,
    });

    await prisma.agentCommand.update({
      where: { id: command.id },
      data: {
        status: CommandStatus.SENT,
        sentAt: new Date(),
      },
    });
  }
}

async function handleAgentDisconnection(agentId: string) {
  // Update agent status
  await prisma.agent.update({
    where: { id: agentId },
    data: { 
      status: AgentStatus.OFFLINE,
      lastSeen: new Date(),
    },
  });

  // Get agent organization
  const agent = await prisma.agent.findUnique({
    where: { id: agentId },
    select: { organizationId: true },
  });

  if (agent) {
    // Notify dashboards
    const io = (global as any).io;
    if (io) {
      io.to(`org:${agent.organizationId}`).emit('agent:disconnected', { agentId });
    }
  }
}

async function handleDashboardConnection(socket: any, organizationId: string) {
  // Join organization room
  socket.join(`org:${organizationId}`);

  // Send current agent status
  const agents = await prisma.agent.findMany({
    where: { organizationId },
    select: {
      id: true,
      hostname: true,
      status: true,
      lastSeen: true,
    },
  });

  socket.emit('agents:status', { agents });
}

async function handleAgentMetrics(agentId: string, data: any) {
  try {
    // Create metric record
    await prisma.agentMetric.create({
      data: {
        agentId,
        metricType: data.metricType || 'system',
        metricData: data.metricData || data,
        timestamp: data.timestamp ? new Date(data.timestamp) : new Date(),
      },
    });

    // Update agent last seen
    await prisma.agent.update({
      where: { id: agentId },
      data: { 
        lastSeen: new Date(),
        status: AgentStatus.ACTIVE,
      },
    });
  } catch (error) {
    console.error('Error handling agent metrics:', error);
  }
}

async function handleAgentAlert(agentId: string, data: any) {
  try {
    // Create alert
    await prisma.agentAlert.create({
      data: {
        agentId,
        alertType: data.alertType,
        severity: data.severity,
        message: data.message,
        details: data.details || {},
      },
    });
  } catch (error) {
    console.error('Error handling agent alert:', error);
  }
}

async function handleCommandResult(commandId: string, result: any, error: string | null) {
  try {
    await prisma.agentCommand.update({
      where: { id: commandId },
      data: {
        status: error ? CommandStatus.FAILED : CommandStatus.COMPLETED,
        result: result || null,
        error: error || null,
        completedAt: new Date(),
      },
    });
  } catch (err) {
    console.error('Error handling command result:', err);
  }
}