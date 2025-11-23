const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const kafka = require('kafka-node');
const redis = require('redis');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
require('dotenv').config();

// iTechSmart Neural Hub - Central Orchestration System
class NeuralHub {
    constructor() {
        this.app = express();
        this.server = http.createServer(this.app);
        this.io = socketIo(this.server, {
            cors: {
                origin: "*",
                methods: ["GET", "POST"]
            }
        });
        
        this.port = process.env.PORT || 8080;
        this.products = new Map();
        this.eventHandlers = new Map();
        this.workflows = new Map();
        
        this.setupMiddleware();
        this.setupKafka();
        this.setupRedis();
        this.setupMongoDB();
        this.setupRoutes();
        this.setupSocketHandlers();
    }

    setupMiddleware() {
        this.app.use(helmet());
        this.app.use(cors());
        this.app.use(morgan('combined'));
        this.app.use(express.json({ limit: '50mb' }));
        this.app.use(express.urlencoded({ extended: true }));
    }

    setupKafka() {
        const kafkaClient = new kafka.KafkaClient({
            kafkaHost: process.env.KAFKA_HOST || 'localhost:9092'
        });
        
        this.producer = new kafka.Producer(kafkaClient);
        this.consumer = new kafka.Consumer(
            kafkaClient,
            [{ topic: 'itechsmart-events', partition: 0 }],
            { autoCommit: true }
        );

        this.producer.on('ready', () => {
            console.log('🚀 Kafka Producer ready - iTechSmart Neural Hub connected');
        });

        this.consumer.on('message', (message) => {
            this.handleEvent(JSON.parse(message.value));
        });

        this.consumer.on('error', (err) => {
            console.error('❌ Kafka Consumer error:', err);
        });
    }

    setupRedis() {
        this.redisClient = redis.createClient({
            host: process.env.REDIS_HOST || 'localhost',
            port: process.env.REDIS_PORT || 6379
        });

        this.redisClient.on('connect', () => {
            console.log('🔴 Redis connected - iTechSmart Neural Hub cache ready');
        });
    }

    setupMongoDB() {
        mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/itechsmart-neural', {
            useNewUrlParser: true,
            useUnifiedTopology: true
        });

        mongoose.connection.on('connected', () => {
            console.log('🗄️ MongoDB connected - iTechSmart Neural Hub database ready');
        });
    }

    setupRoutes() {
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'healthy',
                timestamp: new Date().toISOString(),
                products: this.products.size,
                workflows: this.workflows.size,
                uptime: process.uptime()
            });
        });

        // Product registration
        this.app.post('/api/products/register', async (req, res) => {
            try {
                const { productId, name, category, endpoint, capabilities } = req.body;
                
                this.products.set(productId, {
                    id: productId,
                    name,
                    category,
                    endpoint,
                    capabilities,
                    status: 'active',
                    lastSeen: new Date()
                });

                // Broadcast product registration
                this.broadcastEvent({
                    type: 'PRODUCT_REGISTERED',
                    productId,
                    name,
                    category,
                    timestamp: new Date().toISOString()
                });

                res.json({ success: true, productId });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // Event publishing
        this.app.post('/api/events/publish', async (req, res) => {
            try {
                const event = req.body;
                await this.publishEvent(event);
                res.json({ success: true, eventId: event.id });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // Workflow execution
        this.app.post('/api/workflows/execute', async (req, res) => {
            try {
                const { workflowId, trigger, context } = req.body;
                const result = await this.executeWorkflow(workflowId, trigger, context);
                res.json(result);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // AI command processing
        this.app.post('/api/ai/command', async (req, res) => {
            try {
                const { command, context } = req.body;
                const result = await this.processAICommand(command, context);
                res.json(result);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // Get all active products
        this.app.get('/api/products', (req, res) => {
            const products = Array.from(this.products.values());
            res.json(products);
        });
    }

    setupSocketHandlers() {
        this.io.on('connection', (socket) => {
            console.log('🔌 Client connected to iTechSmart Neural Hub');

            socket.on('register-product', (data) => {
                this.products.set(data.productId, {
                    ...data,
                    socketId: socket.id,
                    lastSeen: new Date()
                });
                socket.join(`product-${data.productId}`);
            });

            socket.on('product-event', async (event) => {
                await this.handleEvent(event);
            });

            socket.on('disconnect', () => {
                console.log('🔌 Client disconnected from iTechSmart Neural Hub');
            });
        });
    }

    async publishEvent(event) {
        const enrichedEvent = {
            ...event,
            id: event.id || this.generateEventId(),
            timestamp: event.timestamp || new Date().toISOString(),
            source: 'neural-hub'
        };

        // Send to Kafka
        const payload = [{
            topic: 'itechsmart-events',
            messages: JSON.stringify(enrichedEvent)
        }];

        this.producer.send(payload, (err, data) => {
            if (err) {
                console.error('❌ Failed to publish event:', err);
            } else {
                console.log('📤 Event published:', enrichedEvent.type);
            }
        });

        // Cache in Redis
        await this.redisClient.setex(
            `event:${enrichedEvent.id}`,
            3600,
            JSON.stringify(enrichedEvent)
        );

        // Broadcast via WebSocket
        this.broadcastEvent(enrichedEvent);
    }

    async handleEvent(event) {
        console.log('📥 Event received:', event.type);

        // Cache event
        await this.redisClient.setex(
            `event:${event.id}`,
            3600,
            JSON.stringify(event)
        );

        // Process event handlers
        const handlers = this.eventHandlers.get(event.type) || [];
        for (const handler of handlers) {
            try {
                await handler(event);
            } catch (error) {
                console.error('❌ Event handler error:', error);
            }
        }

        // Trigger automated workflows
        await this.triggerWorkflows(event);

        // Broadcast to connected clients
        this.broadcastEvent(event);
    }

    broadcastEvent(event) {
        this.io.emit('neural-event', event);
        
        // Send to specific product rooms
        if (event.targetProducts) {
            event.targetProducts.forEach(productId => {
                this.io.to(`product-${productId}`).emit('product-event', event);
            });
        }
    }

    async executeWorkflow(workflowId, trigger, context) {
        const workflow = this.workflows.get(workflowId);
        if (!workflow) {
            throw new Error(`Workflow ${workflowId} not found`);
        }

        console.log('🔄 Executing workflow:', workflowId);

        // Execute workflow steps
        const results = [];
        for (const step of workflow.steps) {
            try {
                const stepResult = await this.executeWorkflowStep(step, context);
                results.push(stepResult);
            } catch (error) {
                console.error('❌ Workflow step failed:', error);
                results.push({ error: error.message });
            }
        }

        return {
            workflowId,
            trigger,
            results,
            completedAt: new Date().toISOString()
        };
    }

    async executeWorkflowStep(step, context) {
        switch (step.type) {
            case 'product-action':
                return await this.executeProductAction(step, context);
            case 'ai-process':
                return await this.executeAIProcess(step, context);
            case 'wait':
                await new Promise(resolve => setTimeout(resolve, step.duration));
                return { status: 'waited', duration: step.duration };
            default:
                throw new Error(`Unknown step type: ${step.type}`);
        }
    }

    async executeProductAction(step, context) {
        const product = this.products.get(step.productId);
        if (!product) {
            throw new Error(`Product ${step.productId} not found`);
        }

        // Send action to product via WebSocket
        this.io.to(`product-${step.productId}`).emit('execute-action', {
            action: step.action,
            parameters: step.parameters,
            context
        });

        return {
            product: step.productId,
            action: step.action,
            status: 'executed'
        };
    }

    async executeAIProcess(step, context) {
        // Enhanced AI processing for cross-product orchestration
        const aiResponse = await this.processAICommand(step.command, context);
        return aiResponse;
    }

    async processAICommand(command, context) {
        console.log('🤖 Processing AI command:', command);

        // Parse command and determine required actions
        const parsedCommand = this.parseNaturalLanguageCommand(command);
        
        // Execute cross-product orchestration
        const actions = [];
        
        if (parsedCommand.scaleRequest) {
            // Handle scaling requests via iTechSmart Supreme
            actions.push(await this.executeProductAction({
                productId: 'itechsmart-supreme',
                action: 'scale-resources',
                parameters: parsedCommand.scaleRequest
            }, context));
        }

        if (parsedCommand.securityRequest) {
            // Handle security requests via iTechSmart Citadel
            actions.push(await this.executeProductAction({
                productId: 'itechsmart-citadel',
                action: 'update-security',
                parameters: parsedCommand.securityRequest
            }, context));
        }

        if (parsedCommand.costRequest) {
            // Handle FinOps requests via Business Value Dashboard
            actions.push(await this.executeProductAction({
                productId: 'itechsmart-business-value',
                action: 'analyze-costs',
                parameters: parsedCommand.costRequest
            }, context));
        }

        return {
            command,
            parsedIntent: parsedCommand,
            actionsExecuted: actions,
            completedAt: new Date().toISOString()
        };
    }

    parseNaturalLanguageCommand(command) {
        // Natural language processing for iTechSmart commands
        const lowerCommand = command.toLowerCase();
        
        const result = {
            scaleRequest: null,
            securityRequest: null,
            costRequest: null,
            regions: [],
            services: []
        };

        // Parse scaling requests
        if (lowerCommand.includes('scale up') || lowerCommand.includes('scale down')) {
            const scaleMatch = command.match(/scale (up|down) the (\w+) in (\w+)/i);
            if (scaleMatch) {
                result.scaleRequest = {
                    direction: scaleMatch[1],
                    service: scaleMatch[2],
                    region: scaleMatch[3]
                };
            }
        }

        // Parse security requests
        if (lowerCommand.includes('firewall') || lowerCommand.includes('security')) {
            result.securityRequest = {
                action: 'update-firewall',
                source: command
            };
        }

        // Parse cost analysis requests
        if (lowerCommand.includes('cost') || lowerCommand.includes('spending')) {
            result.costRequest = {
                action: 'analyze-costs',
                timeframe: 'current-month',
                source: command
            };
        }

        return result;
    }

    generateEventId() {
        return `event-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    async triggerWorkflows(event) {
        // Find workflows triggered by this event type
        for (const [workflowId, workflow] of this.workflows) {
            if (workflow.triggers.includes(event.type)) {
                await this.executeWorkflow(workflowId, event, { event });
            }
        }
    }

    start() {
        this.server.listen(this.port, () => {
            console.log('🚀 iTechSmart Neural Hub started on port', this.port);
            console.log('🧠 Central Orchestration System Active');
            console.log('📡 Neural Data Plane Connected');
            console.log('🤖 AI-First Interface Ready');
        });
    }
}

// Initialize and start the Neural Hub
const neuralHub = new NeuralHub();
neuralHub.start();

module.exports = NeuralHub;