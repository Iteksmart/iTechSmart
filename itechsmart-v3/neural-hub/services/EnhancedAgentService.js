const axios = require('axios');
const EventEmitter = require('events');
const os = require('os');
const fs = require('fs').promises;
const path = require('path');

class EnhancedAgentService extends EventEmitter {
    constructor(neuralHubUrl) {
        super();
        this.neuralHubUrl = neuralHubUrl;
        this.agentId = this.generateAgentId();
        this.isRunning = false;
        this.metrics = {
            system: {},
            security: {},
            applications: {},
            network: {},
            performance: {}
        };
        this.alerts = [];
        this.workflows = new Map();
        this.connections = new Map();
        
        this.initializeAgent();
    }

    generateAgentId() {
        return `agent-${os.hostname()}-${Date.now()}`;
    }

    async initializeAgent() {
        console.log('🤖 Initializing iTechSmart Enhanced Agent...');
        
        try {
            // Register with Neural Hub
            await this.registerWithNeuralHub();
            
            // Start monitoring
            this.startSystemMonitoring();
            this.startSecurityMonitoring();
            this.startApplicationMonitoring();
            this.startNetworkMonitoring();
            
            // Listen for commands from Neural Hub
            this.setupCommandListener();
            
            this.isRunning = true;
            console.log('✅ iTechSmart Enhanced Agent initialized successfully');
            
            this.emit('agent-initialized', {
                agentId: this.agentId,
                hostname: os.hostname(),
                platform: os.platform(),
                arch: os.arch()
            });
            
        } catch (error) {
            console.error('❌ Failed to initialize agent:', error);
            this.emit('agent-error', error);
        }
    }

    async registerWithNeuralHub() {
        try {
            const systemInfo = await this.getSystemInfo();
            
            const response = await axios.post(`${this.neuralHubUrl}/api/products/register`, {
                productId: this.agentId,
                name: `iTechSmart Agent - ${os.hostname()}`,
                category: 'monitoring',
                endpoint: `http://${os.hostname()}:3001`,
                capabilities: [
                    'system-monitoring',
                    'security-scanning',
                    'application-monitoring',
                    'network-analysis',
                    'automated-remediation',
                    'workflow-execution',
                    'log-aggregation',
                    'performance-analysis'
                ],
                systemInfo
            });

            console.log('✅ Registered with Neural Hub:', response.data.productId);
            
        } catch (error) {
            console.error('❌ Failed to register with Neural Hub:', error.message);
            throw error;
        }
    }

    async getSystemInfo() {
        const cpus = os.cpus();
        const totalMemory = os.totalmem();
        const freeMemory = os.freemem();
        const usedMemory = totalMemory - freeMemory;
        
        return {
            hostname: os.hostname(),
            platform: os.platform(),
            arch: os.arch(),
            uptime: os.uptime(),
            loadAverage: os.loadavg(),
            cpuCount: cpus.length,
            cpuModel: cpus[0]?.model,
            cpuSpeed: cpus[0]?.speed,
            totalMemory: totalMemory,
            freeMemory: freeMemory,
            usedMemory: usedMemory,
            memoryUsagePercent: (usedMemory / totalMemory) * 100,
            networkInterfaces: os.networkInterfaces(),
            homedir: os.homedir(),
            tmpdir: os.tmpdir()
        };
    }

    startSystemMonitoring() {
        console.log('📊 Starting system monitoring...');
        
        setInterval(async () => {
            try {
                const systemMetrics = await this.collectSystemMetrics();
                this.metrics.system = systemMetrics;
                
                // Check for threshold violations
                this.checkSystemThresholds(systemMetrics);
                
                // Send to Neural Hub
                await this.sendMetricsToHub('system', systemMetrics);
                
            } catch (error) {
                console.error('❌ System monitoring error:', error);
            }
        }, 30000); // Every 30 seconds
    }

    async collectSystemMetrics() {
        const cpus = os.cpus();
        const loadAvg = os.loadavg();
        const totalMem = os.totalmem();
        const freeMem = os.freemem();
        const usedMem = totalMem - freeMem;
        
        // Calculate CPU usage
        let totalIdle = 0;
        let totalTick = 0;
        cpus.forEach(cpu => {
            for (let type in cpu.times) {
                totalTick += cpu.times[type];
            }
            totalIdle += cpu.times.idle;
        });
        
        const cpuUsage = 100 - (totalIdle / totalTick * 100);
        
        return {
            timestamp: new Date().toISOString(),
            cpu: {
                usage: cpuUsage.toFixed(2),
                loadAverage: loadAvg,
                coreCount: cpus.length,
                speed: cpus[0]?.speed
            },
            memory: {
                total: totalMem,
                used: usedMem,
                free: freeMem,
                usagePercent: ((usedMem / totalMem) * 100).toFixed(2)
            },
            uptime: os.uptime(),
            processes: await this.getProcessCount()
        };
    }

    startSecurityMonitoring() {
        console.log('🛡️ Starting security monitoring...');
        
        setInterval(async () => {
            try {
                const securityMetrics = await this.collectSecurityMetrics();
                this.metrics.security = securityMetrics;
                
                // Analyze for security threats
                await this.analyzeSecurityThreats(securityMetrics);
                
                // Send to Neural Hub
                await this.sendMetricsToHub('security', securityMetrics);
                
            } catch (error) {
                console.error('❌ Security monitoring error:', error);
            }
        }, 60000); // Every minute
    }

    async collectSecurityMetrics() {
        try {
            // Check firewall status (Linux)
            let firewallStatus = 'unknown';
            if (os.platform() === 'linux') {
                try {
                    const { execSync } = require('child_process');
                    const ufwStatus = execSync('sudo ufw status', { encoding: 'utf8' });
                    firewallStatus = ufwStatus.includes('active') ? 'active' : 'inactive';
                } catch (error) {
                    firewallStatus = 'error';
                }
            }
            
            // Check open ports
            const openPorts = await this.scanOpenPorts();
            
            // Check failed login attempts
            const failedLogins = await this.checkFailedLogins();
            
            // Check system updates
            const systemUpdates = await this.checkSystemUpdates();
            
            return {
                timestamp: new Date().toISOString(),
                firewall: {
                    status: firewallStatus
                },
                network: {
                    openPorts: openPorts
                },
                authentication: {
                    failedLogins: failedLogins
                },
                system: {
                    pendingUpdates: systemUpdates
                },
                lastSecurityScan: new Date().toISOString()
            };
        } catch (error) {
            return {
                timestamp: new Date().toISOString(),
                error: error.message
            };
        }
    }

    async scanOpenPorts() {
        // Simplified port scanning - in production, use proper network scanning tools
        const commonPorts = [22, 80, 443, 3306, 5432, 6379, 27017];
        const openPorts = [];
        
        for (const port of commonPorts) {
            try {
                const net = require('net');
                const socket = new net.Socket();
                
                socket.setTimeout(1000);
                
                await new Promise((resolve, reject) => {
                    socket.connect(port, '127.0.0.1', () => {
                        openPorts.push(port);
                        socket.destroy();
                        resolve();
                    });
                    
                    socket.on('error', () => {
                        socket.destroy();
                        resolve();
                    });
                    
                    socket.on('timeout', () => {
                        socket.destroy();
                        resolve();
                    });
                });
            } catch (error) {
                // Port is closed
            }
        }
        
        return openPorts;
    }

    async checkFailedLogins() {
        try {
            const { execSync } = require('child_process');
            if (os.platform() === 'linux') {
                const authLog = execSync('sudo grep "Failed password" /var/log/auth.log | wc -l', { encoding: 'utf8' });
                return parseInt(authLog.trim());
            }
            return 0;
        } catch (error) {
            return 0;
        }
    }

    async checkSystemUpdates() {
        try {
            const { execSync } = require('child_process');
            if (os.platform() === 'linux') {
                const updates = execSync('apt list --upgradable 2>/dev/null | grep -v "WARNING" | wc -l', { encoding: 'utf8' });
                return parseInt(updates.trim());
            }
            return 0;
        } catch (error) {
            return 0;
        }
    }

    async analyzeSecurityThreats(securityMetrics) {
        const threats = [];
        
        // Check firewall status
        if (securityMetrics.firewall?.status === 'inactive') {
            threats.push({
                type: 'FIREWALL_DISABLED',
                severity: 'high',
                description: 'Firewall is disabled',
                recommendation: 'Enable firewall immediately',
                timestamp: new Date().toISOString()
            });
        }
        
        // Check for unusual open ports
        if (securityMetrics.network?.openPorts?.length > 5) {
            threats.push({
                type: 'UNUSUAL_OPEN_PORTS',
                severity: 'medium',
                description: `Unusual number of open ports: ${securityMetrics.network.openPorts.length}`,
                recommendation: 'Review open ports and close unnecessary ones',
                details: securityMetrics.network.openPorts,
                timestamp: new Date().toISOString()
            });
        }
        
        // Check for failed login attempts
        if (securityMetrics.authentication?.failedLogins > 10) {
            threats.push({
                type: 'BRUTE_FORCE_ATTACK',
                severity: 'high',
                description: `High number of failed login attempts: ${securityMetrics.authentication.failedLogins}`,
                recommendation: 'Investigate source IPs and consider blocking',
                timestamp: new Date().toISOString()
            });
        }
        
        // Send threats to Neural Hub
        for (const threat of threats) {
            await this.sendSecurityAlert(threat);
        }
    }

    startApplicationMonitoring() {
        console.log('🚀 Starting application monitoring...');
        
        setInterval(async () => {
            try {
                const appMetrics = await this.collectApplicationMetrics();
                this.metrics.applications = appMetrics;
                
                await this.sendMetricsToHub('applications', appMetrics);
                
            } catch (error) {
                console.error('❌ Application monitoring error:', error);
            }
        }, 45000); // Every 45 seconds
    }

    async collectApplicationMetrics() {
        try {
            const processes = await this.getRunningProcesses();
            const services = await this.getSystemServices();
            
            return {
                timestamp: new Date().toISOString(),
                processes: {
                    total: processes.length,
                    running: processes.filter(p => p.state === 'running').length,
                    sleeping: processes.filter(p => p.state === 'sleeping').length,
                    topCpuConsumers: processes.sort((a, b) => b.cpu - a.cpu).slice(0, 5),
                    topMemoryConsumers: processes.sort((a, b) => b.memory - a.memory).slice(0, 5)
                },
                services: {
                    total: services.length,
                    active: services.filter(s => s.active).length,
                    inactive: services.filter(s => !s.active).length,
                    critical: services.filter(s => s.critical && !s.active)
                }
            };
        } catch (error) {
            return {
                timestamp: new Date().toISOString(),
                error: error.message
            };
        }
    }

    startNetworkMonitoring() {
        console.log('🌐 Starting network monitoring...');
        
        setInterval(async () => {
            try {
                const networkMetrics = await this.collectNetworkMetrics();
                this.metrics.network = networkMetrics;
                
                await this.sendMetricsToHub('network', networkMetrics);
                
            } catch (error) {
                console.error('❌ Network monitoring error:', error);
            }
        }, 60000); // Every minute
    }

    async collectNetworkMetrics() {
        try {
            const networkInterfaces = os.networkInterfaces();
            const activeInterfaces = [];
            
            for (const [name, interfaces] of Object.entries(networkInterfaces)) {
                for (const iface of interfaces) {
                    if (!iface.internal && iface.family === 'IPv4') {
                        activeInterfaces.push({
                            name: name,
                            address: iface.address,
                            netmask: iface.netmask,
                            mac: iface.mac
                        });
                    }
                }
            }
            
            return {
                timestamp: new Date().toISOString(),
                interfaces: activeInterfaces,
                connectionCount: await this.getConnectionCount(),
                bandwidthUsage: await this.getBandwidthUsage()
            };
        } catch (error) {
            return {
                timestamp: new Date().toISOString(),
                error: error.message
            };
        }
    }

    async getProcessCount() {
        try {
            const { execSync } = require('child_process');
            if (os.platform() === 'linux') {
                const count = execSync('ps aux | wc -l', { encoding: 'utf8' });
                return parseInt(count.trim()) - 1; // Subtract header line
            }
            return 0;
        } catch (error) {
            return 0;
        }
    }

    async getRunningProcesses() {
        // Simplified process monitoring
        try {
            const { execSync } = require('child_process');
            if (os.platform() === 'linux') {
                const psOutput = execSync('ps aux --no-headers', { encoding: 'utf8' });
                const lines = psOutput.trim().split('\n');
                
                return lines.slice(0, 20).map(line => {
                    const parts = line.trim().split(/\s+/);
                    return {
                        pid: parts[1],
                        user: parts[0],
                        cpu: parseFloat(parts[2]),
                        memory: parseFloat(parts[3]),
                        command: parts.slice(10).join(' ').substring(0, 50),
                        state: 'running' // Simplified
                    };
                });
            }
            return [];
        } catch (error) {
            return [];
        }
    }

    async getSystemServices() {
        // Simplified service monitoring
        try {
            const { execSync } = require('child_process');
            if (os.platform() === 'linux') {
                const services = ['nginx', 'apache2', 'mysql', 'postgresql', 'redis', 'docker'];
                const serviceStatus = [];
                
                for (const service of services) {
                    try {
                        const status = execSync(`systemctl is-active ${service} 2>/dev/null`, { encoding: 'utf8' });
                        serviceStatus.push({
                            name: service,
                            active: status.trim() === 'active',
                            critical: ['nginx', 'apache2', 'docker'].includes(service)
                        });
                    } catch (error) {
                        serviceStatus.push({
                            name: service,
                            active: false,
                            critical: ['nginx', 'apache2', 'docker'].includes(service)
                        });
                    }
                }
                
                return serviceStatus;
            }
            return [];
        } catch (error) {
            return [];
        }
    }

    async getConnectionCount() {
        try {
            const { execSync } = require('child_process');
            if (os.platform() === 'linux') {
                const connections = execSync('netstat -an | grep ESTABLISHED | wc -l', { encoding: 'utf8' });
                return parseInt(connections.trim());
            }
            return 0;
        } catch (error) {
            return 0;
        }
    }

    async getBandwidthUsage() {
        // Simplified bandwidth monitoring
        try {
            const { execSync } = require('child_process');
            if (os.platform() === 'linux') {
                const stats = execSync('cat /proc/net/dev | grep -E "(eth|ens|wlp)" | head -1', { encoding: 'utf8' });
                const parts = stats.trim().split(/\s+/);
                return {
                    rxBytes: parseInt(parts[1]),
                    txBytes: parseInt(parts[9]),
                    timestamp: new Date().toISOString()
                };
            }
            return null;
        } catch (error) {
            return null;
        }
    }

    checkSystemThresholds(metrics) {
        const alerts = [];
        
        // CPU threshold check
        if (parseFloat(metrics.cpu.usage) > 90) {
            alerts.push({
                type: 'CPU_HIGH',
                severity: 'critical',
                metric: 'cpu',
                value: metrics.cpu.usage,
                threshold: 90,
                description: `CPU usage is critically high: ${metrics.cpu.usage}%`
            });
        } else if (parseFloat(metrics.cpu.usage) > 80) {
            alerts.push({
                type: 'CPU_WARNING',
                severity: 'warning',
                metric: 'cpu',
                value: metrics.cpu.usage,
                threshold: 80,
                description: `CPU usage is high: ${metrics.cpu.usage}%`
            });
        }
        
        // Memory threshold check
        if (parseFloat(metrics.memory.usagePercent) > 90) {
            alerts.push({
                type: 'MEMORY_HIGH',
                severity: 'critical',
                metric: 'memory',
                value: metrics.memory.usagePercent,
                threshold: 90,
                description: `Memory usage is critically high: ${metrics.memory.usagePercent}%`
            });
        } else if (parseFloat(metrics.memory.usagePercent) > 80) {
            alerts.push({
                type: 'MEMORY_WARNING',
                severity: 'warning',
                metric: 'memory',
                value: metrics.memory.usagePercent,
                threshold: 80,
                description: `Memory usage is high: ${metrics.memory.usagePercent}%`
            });
        }
        
        // Send alerts to Neural Hub
        for (const alert of alerts) {
            await this.sendAlert(alert);
        }
    }

    async sendMetricsToHub(category, metrics) {
        try {
            await axios.post(`${this.neuralHubUrl}/api/events/publish`, {
                type: 'METRICS_UPDATE',
                category: category,
                source: this.agentId,
                data: metrics,
                timestamp: new Date().toISOString()
            });
        } catch (error) {
            console.error('❌ Failed to send metrics to Neural Hub:', error.message);
        }
    }

    async sendAlert(alert) {
        try {
            await axios.post(`${this.neuralHubUrl}/api/events/publish`, {
                type: 'SYSTEM_ALERT',
                source: this.agentId,
                ...alert,
                timestamp: new Date().toISOString()
            });
            
            this.emit('alert', alert);
            console.log(`🚨 Alert: ${alert.description}`);
            
        } catch (error) {
            console.error('❌ Failed to send alert to Neural Hub:', error.message);
        }
    }

    async sendSecurityAlert(threat) {
        try {
            await axios.post(`${this.neuralHubUrl}/api/events/publish`, {
                type: 'SECURITY_THREAT',
                source: this.agentId,
                ...threat,
                timestamp: new Date().toISOString()
            });
            
            this.emit('security-threat', threat);
            console.log(`🛡️ Security Threat: ${threat.description}`);
            
        } catch (error) {
            console.error('❌ Failed to send security threat to Neural Hub:', error.message);
        }
    }

    setupCommandListener() {
        console.log('👂 Setting up command listener...');
        
        // In a real implementation, this would connect to Neural Hub via WebSocket
        // For now, we'll simulate command reception
        
        this.on('execute-command', async (command) => {
            await this.executeCommand(command);
        });
    }

    async executeCommand(command) {
        console.log(`⚡ Executing command: ${command.action}`);
        
        try {
            let result;
            
            switch (command.action) {
                case 'restart-service':
                    result = await this.restartService(command.parameters.service);
                    break;
                case 'update-system':
                    result = await this.updateSystem();
                    break;
                case 'cleanup-disk':
                    result = await this.cleanupDisk();
                    break;
                case 'scan-security':
                    result = await this.performSecurityScan();
                    break;
                case 'get-logs':
                    result = await this.getSystemLogs(command.parameters);
                    break;
                default:
                    result = { error: `Unknown command: ${command.action}` };
            }
            
            // Send result back to Neural Hub
            await this.sendCommandResult(command, result);
            
        } catch (error) {
            await this.sendCommandResult(command, { error: error.message });
        }
    }

    async restartService(serviceName) {
        try {
            const { execSync } = require('child_process');
            execSync(`sudo systemctl restart ${serviceName}`, { encoding: 'utf8' });
            return { success: true, message: `Service ${serviceName} restarted successfully` };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async updateSystem() {
        try {
            const { execSync } = require('child_process');
            execSync('sudo apt update && sudo apt upgrade -y', { encoding: 'utf8' });
            return { success: true, message: 'System updated successfully' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async cleanupDisk() {
        try {
            const { execSync } = require('child_process');
            execSync('sudo apt autoremove -y && sudo apt autoclean', { encoding: 'utf8' });
            return { success: true, message: 'Disk cleanup completed' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async performSecurityScan() {
        try {
            const securityMetrics = await this.collectSecurityMetrics();
            const threats = [];
            
            // Analyze current security state
            await this.analyzeSecurityThreats(securityMetrics);
            
            return {
                success: true,
                message: 'Security scan completed',
                metrics: securityMetrics
            };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async getSystemLogs(parameters) {
        try {
            const { execSync } = require('child_process');
            const lines = parameters.lines || 50;
            const service = parameters.service || '';
            
            let command = `sudo journalctl -n ${lines}`;
            if (service) {
                command += ` -u ${service}`;
            }
            
            const logs = execSync(command, { encoding: 'utf8' });
            
            return {
                success: true,
                logs: logs,
                lines: lines,
                service: service
            };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async sendCommandResult(command, result) {
        try {
            await axios.post(`${this.neuralHubUrl}/api/events/publish`, {
                type: 'COMMAND_RESULT',
                source: this.agentId,
                commandId: command.id,
                action: command.action,
                result: result,
                timestamp: new Date().toISOString()
            });
        } catch (error) {
            console.error('❌ Failed to send command result to Neural Hub:', error.message);
        }
    }

    getMetrics() {
        return this.metrics;
    }

    getAlerts() {
        return this.alerts;
    }

    async shutdown() {
        console.log('🛑 Shutting down iTechSmart Enhanced Agent...');
        this.isRunning = false;
        
        // Send final status to Neural Hub
        try {
            await axios.post(`${this.neuralHubUrl}/api/events/publish`, {
                type: 'AGENT_SHUTDOWN',
                source: this.agentId,
                timestamp: new Date().toISOString()
            });
        } catch (error) {
            console.error('❌ Failed to send shutdown notification:', error.message);
        }
        
        console.log('✅ iTechSmart Enhanced Agent shutdown complete');
    }
}

module.exports = EnhancedAgentService;