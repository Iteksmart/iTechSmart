-- iTechSmart Connect Database Initialization Script
-- This script creates all necessary tables, indexes, and sample data

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- USERS & AUTHENTICATION
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'developer',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- ============================================================================
-- APIS
-- ============================================================================

CREATE TABLE apis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    base_url VARCHAR(500) NOT NULL,
    version VARCHAR(50) DEFAULT 'v1',
    status VARCHAR(50) DEFAULT 'active',
    rate_limit INTEGER DEFAULT 1000,
    timeout INTEGER DEFAULT 30,
    retry_count INTEGER DEFAULT 3,
    owner_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_apis_slug ON apis(slug);
CREATE INDEX idx_apis_status ON apis(status);
CREATE INDEX idx_apis_owner_id ON apis(owner_id);
CREATE INDEX idx_apis_name ON apis USING gin(name gin_trgm_ops);

-- ============================================================================
-- API ENDPOINTS
-- ============================================================================

CREATE TABLE api_endpoints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    api_id UUID REFERENCES apis(id) ON DELETE CASCADE,
    path VARCHAR(500) NOT NULL,
    method VARCHAR(10) NOT NULL,
    description TEXT,
    rate_limit INTEGER,
    timeout INTEGER,
    requires_auth BOOLEAN DEFAULT true,
    request_schema JSONB,
    response_schema JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_endpoints_api_id ON api_endpoints(api_id);
CREATE INDEX idx_api_endpoints_method ON api_endpoints(method);
CREATE INDEX idx_api_endpoints_path ON api_endpoints(path);

-- ============================================================================
-- API VERSIONS
-- ============================================================================

CREATE TABLE api_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    api_id UUID REFERENCES apis(id) ON DELETE CASCADE,
    version VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    is_default BOOLEAN DEFAULT false,
    changelog TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deprecated_at TIMESTAMP
);

CREATE INDEX idx_api_versions_api_id ON api_versions(api_id);
CREATE INDEX idx_api_versions_version ON api_versions(version);

-- ============================================================================
-- API KEYS
-- ============================================================================

CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    scopes JSONB DEFAULT '[]',
    rate_limit INTEGER DEFAULT 1000,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP
);

CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active);

-- ============================================================================
-- REQUEST LOGS
-- ============================================================================

CREATE TABLE request_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    api_id UUID REFERENCES apis(id),
    api_key_id UUID REFERENCES api_keys(id),
    method VARCHAR(10) NOT NULL,
    path VARCHAR(500) NOT NULL,
    query_params JSONB,
    headers JSONB,
    status_code INTEGER NOT NULL,
    response_time_ms FLOAT NOT NULL,
    response_size_bytes INTEGER,
    client_ip VARCHAR(50),
    user_agent TEXT,
    error_message TEXT,
    error_type VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_request_logs_api_id ON request_logs(api_id);
CREATE INDEX idx_request_logs_api_key_id ON request_logs(api_key_id);
CREATE INDEX idx_request_logs_status_code ON request_logs(status_code);
CREATE INDEX idx_request_logs_timestamp ON request_logs(timestamp);

-- ============================================================================
-- RATE LIMITS
-- ============================================================================

CREATE TABLE rate_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    api_id UUID REFERENCES apis(id),
    endpoint_id UUID REFERENCES api_endpoints(id),
    limit INTEGER NOT NULL,
    window_seconds INTEGER NOT NULL DEFAULT 60,
    scope VARCHAR(50) DEFAULT 'global',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rate_limits_api_id ON rate_limits(api_id);
CREATE INDEX idx_rate_limits_endpoint_id ON rate_limits(endpoint_id);

-- ============================================================================
-- WEBHOOKS
-- ============================================================================

CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    events JSONB DEFAULT '[]',
    secret VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    retry_count INTEGER DEFAULT 3,
    retry_delay_seconds INTEGER DEFAULT 60,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_triggered TIMESTAMP
);

CREATE INDEX idx_webhooks_user_id ON webhooks(user_id);
CREATE INDEX idx_webhooks_is_active ON webhooks(is_active);

-- ============================================================================
-- WEBHOOK DELIVERIES
-- ============================================================================

CREATE TABLE webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    webhook_id UUID REFERENCES webhooks(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB,
    status VARCHAR(50) NOT NULL,
    status_code INTEGER,
    response_body TEXT,
    error_message TEXT,
    attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP
);

CREATE INDEX idx_webhook_deliveries_webhook_id ON webhook_deliveries(webhook_id);
CREATE INDEX idx_webhook_deliveries_status ON webhook_deliveries(status);
CREATE INDEX idx_webhook_deliveries_created_at ON webhook_deliveries(created_at);

-- ============================================================================
-- API METRICS
-- ============================================================================

CREATE TABLE api_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    api_id UUID REFERENCES apis(id) ON DELETE CASCADE,
    total_requests INTEGER DEFAULT 0,
    successful_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    avg_response_time_ms FLOAT DEFAULT 0,
    p95_response_time_ms FLOAT DEFAULT 0,
    p99_response_time_ms FLOAT DEFAULT 0,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_metrics_api_id ON api_metrics(api_id);
CREATE INDEX idx_api_metrics_period_start ON api_metrics(period_start);

-- ============================================================================
-- API DOCUMENTATION
-- ============================================================================

CREATE TABLE api_documentation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    api_id UUID REFERENCES apis(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    content_type VARCHAR(50) DEFAULT 'markdown',
    section VARCHAR(100),
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_documentation_api_id ON api_documentation(api_id);
CREATE INDEX idx_api_documentation_section ON api_documentation(section);

-- ============================================================================
-- AUDIT LOGS
-- ============================================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    details JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

-- Insert sample users
INSERT INTO users (email, username, password_hash, full_name, role, is_active, is_verified) VALUES
('admin@itechsmart.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qXqJqQqKa', 'System Administrator', 'admin', true, true),
('developer@itechsmart.com', 'developer', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qXqJqQqKa', 'Lead Developer', 'developer', true, true),
('viewer@itechsmart.com', 'viewer', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qXqJqQqKa', 'API Viewer', 'viewer', true, true);

-- Insert sample APIs
INSERT INTO apis (name, slug, description, base_url, version, status, rate_limit, owner_id) VALUES
('User Authentication API', 'user-auth', 'Secure user authentication and management', 'https://api.example.com/auth', 'v2', 'active', 1000, (SELECT id FROM users WHERE username = 'admin')),
('Payment Processing API', 'payment', 'Process payments and manage transactions', 'https://api.example.com/payment', 'v1', 'active', 500, (SELECT id FROM users WHERE username = 'admin')),
('Data Analytics API', 'analytics', 'Advanced data analytics and reporting', 'https://api.example.com/analytics', 'v3', 'maintenance', 2000, (SELECT id FROM users WHERE username = 'developer')),
('Notification Service API', 'notifications', 'Send notifications via multiple channels', 'https://api.example.com/notify', 'v1', 'active', 1500, (SELECT id FROM users WHERE username = 'developer'));

-- Insert sample API endpoints
INSERT INTO api_endpoints (api_id, path, method, description, requires_auth) VALUES
((SELECT id FROM apis WHERE slug = 'user-auth'), '/login', 'POST', 'Authenticate user and return access token', false),
((SELECT id FROM apis WHERE slug = 'user-auth'), '/register', 'POST', 'Register a new user account', false),
((SELECT id FROM apis WHERE slug = 'user-auth'), '/profile', 'GET', 'Get current user profile', true),
((SELECT id FROM apis WHERE slug = 'user-auth'), '/profile', 'PUT', 'Update user profile', true),
((SELECT id FROM apis WHERE slug = 'payment'), '/charge', 'POST', 'Process a payment charge', true),
((SELECT id FROM apis WHERE slug = 'payment'), '/refund', 'POST', 'Process a refund', true);

-- Insert sample API keys
INSERT INTO api_keys (user_id, name, key_hash, scopes, rate_limit, is_active) VALUES
((SELECT id FROM users WHERE username = 'admin'), 'Production Key', 'hash_prod_key_123', '["read", "write", "admin"]', 2000, true),
((SELECT id FROM users WHERE username = 'developer'), 'Development Key', 'hash_dev_key_456', '["read", "write"]', 1000, true),
((SELECT id FROM users WHERE username = 'viewer'), 'Read-Only Key', 'hash_view_key_789', '["read"]', 500, true);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_apis_updated_at BEFORE UPDATE ON apis FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_api_endpoints_updated_at BEFORE UPDATE ON api_endpoints FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_rate_limits_updated_at BEFORE UPDATE ON rate_limits FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_api_documentation_updated_at BEFORE UPDATE ON api_documentation FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View for API statistics
CREATE OR REPLACE VIEW api_stats AS
SELECT 
    a.id,
    a.name,
    a.slug,
    a.status,
    COUNT(DISTINCT ae.id) as endpoint_count,
    COUNT(DISTINCT rl.id) as request_count,
    AVG(rl.response_time_ms) as avg_response_time
FROM apis a
LEFT JOIN api_endpoints ae ON ae.api_id = a.id
LEFT JOIN request_logs rl ON rl.api_id = a.id
GROUP BY a.id, a.name, a.slug, a.status;

-- View for user activity
CREATE OR REPLACE VIEW user_activity AS
SELECT 
    u.id,
    u.username,
    u.email,
    COUNT(DISTINCT ak.id) as api_key_count,
    COUNT(DISTINCT al.id) as action_count,
    MAX(al.created_at) as last_activity
FROM users u
LEFT JOIN api_keys ak ON ak.user_id = u.id
LEFT JOIN audit_logs al ON al.user_id = u.id
GROUP BY u.id, u.username, u.email;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'iTechSmart Connect Database Initialization Complete!';
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'Tables Created: 13';
    RAISE NOTICE 'Indexes Created: 35+';
    RAISE NOTICE 'Sample Users: 3 (admin, developer, viewer)';
    RAISE NOTICE 'Sample APIs: 4';
    RAISE NOTICE 'Sample Endpoints: 6';
    RAISE NOTICE 'Sample API Keys: 3';
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'Default Login Credentials:';
    RAISE NOTICE 'Admin: admin@itechsmart.com / password';
    RAISE NOTICE 'Developer: developer@itechsmart.com / password';
    RAISE NOTICE 'Viewer: viewer@itechsmart.com / password';
    RAISE NOTICE '=================================================================';
END $$;