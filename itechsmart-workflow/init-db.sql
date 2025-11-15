-- iTechSmart Workflow - Database Initialization Script
-- PostgreSQL Database Schema with Sample Data

-- Drop existing tables if they exist
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS schedules CASCADE;
DROP TABLE IF EXISTS execution_logs CASCADE;
DROP TABLE IF EXISTS templates CASCADE;
DROP TABLE IF EXISTS integrations CASCADE;
DROP TABLE IF EXISTS workflow_variables CASCADE;
DROP TABLE IF EXISTS triggers CASCADE;
DROP TABLE IF EXISTS task_executions CASCADE;
DROP TABLE IF EXISTS executions CASCADE;
DROP TABLE IF EXISTS workflows CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create ENUM types
CREATE TYPE workflow_status AS ENUM ('draft', 'active', 'paused', 'archived');
CREATE TYPE execution_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');
CREATE TYPE task_status AS ENUM ('pending', 'running', 'completed', 'failed', 'skipped');
CREATE TYPE trigger_type AS ENUM ('manual', 'scheduled', 'webhook', 'event', 'api');

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workflows table
CREATE TABLE workflows (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status workflow_status DEFAULT 'draft',
    definition JSONB NOT NULL,
    version INTEGER DEFAULT 1,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(100),
    tags JSONB,
    is_template BOOLEAN DEFAULT FALSE,
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_duration_seconds INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Executions table
CREATE TABLE executions (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    status execution_status DEFAULT 'pending',
    trigger_type trigger_type NOT NULL,
    triggered_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    input_data JSONB,
    output_data JSONB,
    context JSONB,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Task executions table
CREATE TABLE task_executions (
    id SERIAL PRIMARY KEY,
    execution_id INTEGER NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    task_id VARCHAR(100) NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    status task_status DEFAULT 'pending',
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Triggers table
CREATE TABLE triggers (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    trigger_type trigger_type NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    configuration JSONB NOT NULL,
    last_triggered_at TIMESTAMP,
    trigger_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workflow variables table
CREATE TABLE workflow_variables (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    key VARCHAR(255) NOT NULL,
    value TEXT,
    is_secret BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workflow_id, key)
);

-- Integrations table
CREATE TABLE integrations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    description TEXT,
    configuration JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    last_used_at TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Templates table
CREATE TABLE templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    tags JSONB,
    definition JSONB NOT NULL,
    icon VARCHAR(255),
    is_featured BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    rating INTEGER DEFAULT 0,
    created_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Execution logs table
CREATE TABLE execution_logs (
    id SERIAL PRIMARY KEY,
    execution_id INTEGER NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    task_id VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schedules table
CREATE TABLE schedules (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    cron_expression VARCHAR(100) NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT TRUE,
    next_run_at TIMESTAMP,
    last_run_at TIMESTAMP,
    run_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id INTEGER,
    changes JSONB,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_workflows_owner ON workflows(owner_id);
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_category ON workflows(category);
CREATE INDEX idx_executions_workflow ON executions(workflow_id);
CREATE INDEX idx_executions_status ON executions(status);
CREATE INDEX idx_executions_created ON executions(created_at DESC);
CREATE INDEX idx_task_executions_execution ON task_executions(execution_id);
CREATE INDEX idx_task_executions_status ON task_executions(status);
CREATE INDEX idx_triggers_workflow ON triggers(workflow_id);
CREATE INDEX idx_triggers_type ON triggers(trigger_type);
CREATE INDEX idx_workflow_variables_workflow ON workflow_variables(workflow_id);
CREATE INDEX idx_integrations_owner ON integrations(owner_id);
CREATE INDEX idx_integrations_type ON integrations(type);
CREATE INDEX idx_templates_category ON templates(category);
CREATE INDEX idx_templates_featured ON templates(is_featured);
CREATE INDEX idx_execution_logs_execution ON execution_logs(execution_id);
CREATE INDEX idx_execution_logs_created ON execution_logs(created_at);
CREATE INDEX idx_schedules_workflow ON schedules(workflow_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);

-- Insert sample data

-- Sample users (password is 'password' hashed with bcrypt)
INSERT INTO users (email, username, hashed_password, full_name, is_admin) VALUES
('admin@itechsmart.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQqK', 'Admin User', TRUE),
('john@itechsmart.com', 'john', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQqK', 'John Doe', FALSE),
('jane@itechsmart.com', 'jane', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQqK', 'Jane Smith', FALSE);

-- Sample workflows
INSERT INTO workflows (name, description, status, definition, owner_id, category, tags, execution_count, success_count, failure_count) VALUES
('Customer Onboarding', 'Automated customer onboarding workflow', 'active', '{"nodes": [{"id": "1", "type": "start"}, {"id": "2", "type": "email"}], "edges": [{"source": "1", "target": "2"}]}', 1, 'sales', '["onboarding", "customer", "automation"]', 234, 229, 5),
('Invoice Processing', 'Process and validate invoices automatically', 'active', '{"nodes": [{"id": "1", "type": "start"}, {"id": "2", "type": "validate"}], "edges": [{"source": "1", "target": "2"}]}', 1, 'finance', '["invoice", "finance", "automation"]', 189, 180, 9),
('Data Sync', 'Sync data between systems', 'active', '{"nodes": [{"id": "1", "type": "start"}, {"id": "2", "type": "sync"}], "edges": [{"source": "1", "target": "2"}]}', 1, 'operations', '["sync", "data", "integration"]', 156, 154, 2),
('Email Campaign', 'Send automated email campaigns', 'active', '{"nodes": [{"id": "1", "type": "start"}, {"id": "2", "type": "email"}], "edges": [{"source": "1", "target": "2"}]}', 2, 'marketing', '["email", "campaign", "marketing"]', 142, 138, 4),
('Report Generation', 'Generate weekly reports', 'paused', '{"nodes": [{"id": "1", "type": "start"}, {"id": "2", "type": "report"}], "edges": [{"source": "1", "target": "2"}]}', 2, 'operations', '["report", "analytics"]', 128, 120, 8),
('Lead Qualification', 'Qualify and score leads', 'draft', '{"nodes": [{"id": "1", "type": "start"}], "edges": []}', 3, 'sales', '["lead", "sales"]', 0, 0, 0);

-- Sample executions
INSERT INTO executions (workflow_id, status, trigger_type, triggered_by_user_id, started_at, completed_at, duration_seconds, created_at) VALUES
(1, 'completed', 'manual', 1, NOW() - INTERVAL '2 minutes', NOW() - INTERVAL '1 minute', 45, NOW() - INTERVAL '2 minutes'),
(2, 'completed', 'scheduled', 1, NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '4 minutes', 38, NOW() - INTERVAL '5 minutes'),
(3, 'running', 'webhook', 1, NOW() - INTERVAL '8 minutes', NULL, NULL, NOW() - INTERVAL '8 minutes'),
(4, 'completed', 'manual', 2, NOW() - INTERVAL '12 minutes', NOW() - INTERVAL '10 minutes', 52, NOW() - INTERVAL '12 minutes'),
(5, 'failed', 'scheduled', 2, NOW() - INTERVAL '15 minutes', NOW() - INTERVAL '14 minutes', 28, NOW() - INTERVAL '15 minutes'),
(1, 'completed', 'api', 1, NOW() - INTERVAL '1 hour', NOW() - INTERVAL '59 minutes', 42, NOW() - INTERVAL '1 hour'),
(2, 'completed', 'manual', 1, NOW() - INTERVAL '2 hours', NOW() - INTERVAL '119 minutes', 35, NOW() - INTERVAL '2 hours');

-- Sample task executions
INSERT INTO task_executions (execution_id, task_id, task_name, task_type, status, started_at, completed_at, duration_seconds) VALUES
(1, 'task_1', 'Send Welcome Email', 'email', 'completed', NOW() - INTERVAL '2 minutes', NOW() - INTERVAL '1 minute', 45),
(2, 'task_1', 'Validate Invoice', 'validation', 'completed', NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '4 minutes', 38),
(3, 'task_1', 'Sync Data', 'sync', 'running', NOW() - INTERVAL '8 minutes', NULL, NULL),
(4, 'task_1', 'Send Campaign Email', 'email', 'completed', NOW() - INTERVAL '12 minutes', NOW() - INTERVAL '10 minutes', 52),
(5, 'task_1', 'Generate Report', 'report', 'failed', NOW() - INTERVAL '15 minutes', NOW() - INTERVAL '14 minutes', 28);

-- Sample triggers
INSERT INTO triggers (workflow_id, name, trigger_type, configuration, is_active) VALUES
(1, 'Daily at 9 AM', 'scheduled', '{"cron": "0 9 * * *", "timezone": "UTC"}', TRUE),
(2, 'Every Hour', 'scheduled', '{"cron": "0 * * * *", "timezone": "UTC"}', TRUE),
(3, 'Webhook Trigger', 'webhook', '{"url": "/webhook/data-sync", "method": "POST"}', TRUE),
(4, 'Manual Trigger', 'manual', '{}', TRUE);

-- Sample workflow variables
INSERT INTO workflow_variables (workflow_id, key, value, is_secret, description) VALUES
(1, 'welcome_email_template', 'template_001', FALSE, 'Welcome email template ID'),
(1, 'api_key', 'sk_test_xxxxx', TRUE, 'API key for external service'),
(2, 'invoice_threshold', '1000', FALSE, 'Invoice amount threshold'),
(3, 'sync_interval', '3600', FALSE, 'Sync interval in seconds');

-- Sample integrations
INSERT INTO integrations (name, type, description, configuration, owner_id, usage_count) VALUES
('Slack Notifications', 'slack', 'Send notifications to Slack', '{"webhook_url": "https://hooks.slack.com/services/xxx", "channel": "#notifications"}', 1, 45),
('SendGrid Email', 'email', 'Send emails via SendGrid', '{"api_key": "SG.xxxxx", "from_email": "noreply@itechsmart.com"}', 1, 234),
('AWS S3 Storage', 'aws', 'Store files in AWS S3', '{"bucket": "itechsmart-files", "region": "us-east-1"}', 1, 89),
('PostgreSQL Database', 'database', 'Connect to PostgreSQL', '{"host": "localhost", "port": 5432, "database": "production"}', 2, 156);

-- Sample templates
INSERT INTO templates (name, description, category, tags, definition, icon, is_featured, usage_count, rating) VALUES
('Customer Onboarding', 'Complete customer onboarding workflow', 'sales', '["onboarding", "customer"]', '{"nodes": [{"id": "1", "type": "start"}], "edges": []}', '👤', TRUE, 45, 5),
('Invoice Processing', 'Automated invoice processing', 'finance', '["invoice", "finance"]', '{"nodes": [{"id": "1", "type": "start"}], "edges": []}', '💰', TRUE, 38, 5),
('Email Campaign', 'Marketing email campaign', 'marketing', '["email", "marketing"]', '{"nodes": [{"id": "1", "type": "start"}], "edges": []}', '📧', TRUE, 52, 4),
('Data Backup', 'Automated data backup', 'operations', '["backup", "data"]', '{"nodes": [{"id": "1", "type": "start"}], "edges": []}', '💾', FALSE, 28, 4),
('Lead Scoring', 'Automated lead scoring', 'sales', '["lead", "scoring"]', '{"nodes": [{"id": "1", "type": "start"}], "edges": []}', '⭐', FALSE, 19, 4),
('Report Generation', 'Automated report generation', 'operations', '["report", "analytics"]', '{"nodes": [{"id": "1", "type": "start"}], "edges": []}', '📊', FALSE, 34, 5);

-- Sample execution logs
INSERT INTO execution_logs (execution_id, level, message, task_id) VALUES
(1, 'INFO', 'Workflow execution started', NULL),
(1, 'INFO', 'Task "Send Welcome Email" started', 'task_1'),
(1, 'INFO', 'Email sent successfully', 'task_1'),
(1, 'INFO', 'Workflow execution completed', NULL),
(2, 'INFO', 'Workflow execution started', NULL),
(2, 'INFO', 'Invoice validation started', 'task_1'),
(2, 'INFO', 'Invoice validated successfully', 'task_1'),
(2, 'INFO', 'Workflow execution completed', NULL),
(5, 'INFO', 'Workflow execution started', NULL),
(5, 'ERROR', 'Report generation failed: Database connection timeout', 'task_1'),
(5, 'ERROR', 'Workflow execution failed', NULL);

-- Sample schedules
INSERT INTO schedules (workflow_id, name, cron_expression, timezone, is_active, next_run_at, run_count) VALUES
(1, 'Daily Morning Run', '0 9 * * *', 'UTC', TRUE, NOW() + INTERVAL '1 day', 45),
(2, 'Hourly Sync', '0 * * * *', 'UTC', TRUE, NOW() + INTERVAL '1 hour', 234),
(4, 'Weekly Report', '0 9 * * 1', 'UTC', TRUE, NOW() + INTERVAL '7 days', 12);

-- Sample audit logs
INSERT INTO audit_logs (user_id, action, resource_type, resource_id, changes) VALUES
(1, 'create', 'workflow', 1, '{"name": "Customer Onboarding"}'),
(1, 'update', 'workflow', 1, '{"status": "active"}'),
(2, 'create', 'workflow', 4, '{"name": "Email Campaign"}'),
(1, 'delete', 'workflow', 6, '{"name": "Old Workflow"}');

-- Create views for common queries
CREATE VIEW workflow_stats AS
SELECT 
    w.id,
    w.name,
    w.status,
    COUNT(e.id) as total_executions,
    COUNT(CASE WHEN e.status = 'completed' THEN 1 END) as successful_executions,
    COUNT(CASE WHEN e.status = 'failed' THEN 1 END) as failed_executions,
    AVG(e.duration_seconds) as avg_duration
FROM workflows w
LEFT JOIN executions e ON w.id = e.workflow_id
GROUP BY w.id, w.name, w.status;

CREATE VIEW recent_executions AS
SELECT 
    e.id,
    e.workflow_id,
    w.name as workflow_name,
    e.status,
    e.trigger_type,
    e.duration_seconds,
    e.created_at
FROM executions e
JOIN workflows w ON e.workflow_id = w.id
ORDER BY e.created_at DESC
LIMIT 100;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO workflow_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO workflow_user;

-- Success message
SELECT 'Database initialized successfully!' as message;