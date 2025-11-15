-- iTechSmart Notify - Database Initialization Script
-- PostgreSQL Database Schema with Sample Data

-- Drop existing tables
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS webhooks CASCADE;
DROP TABLE IF EXISTS subscribers CASCADE;
DROP TABLE IF EXISTS schedules CASCADE;
DROP TABLE IF EXISTS delivery_logs CASCADE;
DROP TABLE IF EXISTS channels CASCADE;
DROP TABLE IF EXISTS templates CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create ENUM types
CREATE TYPE notification_status AS ENUM ('pending', 'queued', 'sending', 'sent', 'delivered', 'failed', 'cancelled');
CREATE TYPE notification_priority AS ENUM ('low', 'normal', 'high', 'urgent');
CREATE TYPE channel_type AS ENUM ('email', 'sms', 'push', 'slack', 'webhook', 'in_app');
CREATE TYPE template_type AS ENUM ('email', 'sms', 'push', 'slack');

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone_number VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    channel_type channel_type NOT NULL,
    status notification_status DEFAULT 'pending',
    priority notification_priority DEFAULT 'normal',
    recipient VARCHAR(255) NOT NULL,
    recipient_name VARCHAR(255),
    subject VARCHAR(500),
    body TEXT NOT NULL,
    html_body TEXT,
    template_id INTEGER,
    template_variables JSONB,
    scheduled_at TIMESTAMP,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    metadata JSONB,
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Templates table
CREATE TABLE templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_type template_type NOT NULL,
    subject VARCHAR(500),
    body TEXT NOT NULL,
    html_body TEXT,
    variables JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    category VARCHAR(100),
    tags JSONB,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Channels table
CREATE TABLE channels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    channel_type channel_type NOT NULL,
    description TEXT,
    configuration JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    rate_limit_per_minute INTEGER,
    rate_limit_per_hour INTEGER,
    rate_limit_per_day INTEGER,
    total_sent INTEGER DEFAULT 0,
    total_delivered INTEGER DEFAULT 0,
    total_failed INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    owner_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Delivery logs table
CREATE TABLE delivery_logs (
    id SERIAL PRIMARY KEY,
    notification_id INTEGER NOT NULL REFERENCES notifications(id) ON DELETE CASCADE,
    attempt_number INTEGER NOT NULL,
    status notification_status NOT NULL,
    response_code VARCHAR(50),
    response_message TEXT,
    response_data JSONB,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    error_message TEXT,
    error_code VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schedules table
CREATE TABLE schedules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cron_expression VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'UTC',
    channel_type channel_type NOT NULL,
    template_id INTEGER REFERENCES templates(id),
    recipients JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    next_run_at TIMESTAMP,
    last_run_at TIMESTAMP,
    run_count INTEGER DEFAULT 0,
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subscribers table
CREATE TABLE subscribers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    phone_number VARCHAR(20),
    device_token VARCHAR(500),
    preferences JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    tags JSONB,
    total_notifications_received INTEGER DEFAULT 0,
    last_notification_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Webhooks table
CREATE TABLE webhooks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    events JSONB NOT NULL,
    secret VARCHAR(255),
    headers JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    total_calls INTEGER DEFAULT 0,
    last_called_at TIMESTAMP,
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id INTEGER,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_channel ON notifications(channel_type);
CREATE INDEX idx_notifications_created ON notifications(created_at DESC);
CREATE INDEX idx_templates_type ON templates(template_type);
CREATE INDEX idx_templates_created_by ON templates(created_by_id);
CREATE INDEX idx_channels_type ON channels(channel_type);
CREATE INDEX idx_channels_owner ON channels(owner_id);
CREATE INDEX idx_delivery_logs_notification ON delivery_logs(notification_id);
CREATE INDEX idx_delivery_logs_created ON delivery_logs(created_at DESC);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);

-- Insert sample data
INSERT INTO users (email, username, hashed_password, full_name, is_admin) VALUES
('admin@itechsmart.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQqK', 'Admin User', TRUE),
('john@itechsmart.com', 'john', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQqK', 'John Doe', FALSE);

-- Sample templates
INSERT INTO templates (name, description, template_type, subject, body, variables, created_by_id) VALUES
('Welcome Email', 'Welcome email for new users', 'email', 'Welcome to {{company_name}}!', 'Hello {{user_name}}, Welcome to our platform!', '["user_name", "company_name"]', 1),
('Password Reset', 'Password reset notification', 'email', 'Reset Your Password', 'Click here to reset: {{reset_link}}', '["reset_link"]', 1),
('Order Confirmation', 'Order confirmation SMS', 'sms', NULL, 'Your order #{{order_id}} has been confirmed!', '["order_id"]', 1);

-- Sample channels
INSERT INTO channels (name, channel_type, description, configuration, owner_id) VALUES
('Default Email', 'email', 'Default email channel', '{"smtp_host": "smtp.example.com", "smtp_port": 587}', 1),
('SMS Provider', 'sms', 'SMS delivery channel', '{"provider": "twilio", "account_sid": "xxx"}', 1);

-- Sample notifications
INSERT INTO notifications (user_id, channel_type, status, recipient, subject, body, priority) VALUES
(1, 'email', 'sent', 'user@example.com', 'Welcome!', 'Welcome to our platform', 'normal'),
(1, 'sms', 'delivered', '+1234567890', NULL, 'Your code is 123456', 'high'),
(1, 'email', 'failed', 'invalid@example.com', 'Test', 'Test message', 'low');

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO notify_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO notify_user;

SELECT 'Database initialized successfully!' as message;