-- iTechSmart Pulse Database Initialization Script
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
    role VARCHAR(50) DEFAULT 'viewer',
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
-- DATA SOURCES
-- ============================================================================

CREATE TABLE data_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    connection_string TEXT,
    config JSONB,
    status VARCHAR(50) DEFAULT 'active',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_tested TIMESTAMP,
    test_status VARCHAR(50)
);

CREATE INDEX idx_data_sources_type ON data_sources(type);
CREATE INDEX idx_data_sources_status ON data_sources(status);
CREATE INDEX idx_data_sources_created_by ON data_sources(created_by);

-- ============================================================================
-- DATASETS
-- ============================================================================

CREATE TABLE datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    source_id UUID REFERENCES data_sources(id),
    query TEXT,
    schema JSONB,
    row_count BIGINT DEFAULT 0,
    size_bytes BIGINT DEFAULT 0,
    refresh_schedule VARCHAR(100),
    last_refreshed TIMESTAMP,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_datasets_source_id ON datasets(source_id);
CREATE INDEX idx_datasets_created_by ON datasets(created_by);
CREATE INDEX idx_datasets_name ON datasets USING gin(name gin_trgm_ops);

-- ============================================================================
-- REPORTS
-- ============================================================================

CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,
    config JSONB,
    dataset_id UUID REFERENCES datasets(id),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_run TIMESTAMP,
    is_public BOOLEAN DEFAULT false,
    tags TEXT[]
);

CREATE INDEX idx_reports_type ON reports(type);
CREATE INDEX idx_reports_dataset_id ON reports(dataset_id);
CREATE INDEX idx_reports_created_by ON reports(created_by);
CREATE INDEX idx_reports_tags ON reports USING gin(tags);

-- ============================================================================
-- DASHBOARDS
-- ============================================================================

CREATE TABLE dashboards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    layout JSONB,
    config JSONB,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_public BOOLEAN DEFAULT false,
    tags TEXT[]
);

CREATE INDEX idx_dashboards_created_by ON dashboards(created_by);
CREATE INDEX idx_dashboards_tags ON dashboards USING gin(tags);

-- ============================================================================
-- VISUALIZATIONS
-- ============================================================================

CREATE TABLE visualizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    config JSONB,
    query TEXT,
    dataset_id UUID REFERENCES datasets(id),
    dashboard_id UUID REFERENCES dashboards(id),
    position JSONB,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_visualizations_type ON visualizations(type);
CREATE INDEX idx_visualizations_dataset_id ON visualizations(dataset_id);
CREATE INDEX idx_visualizations_dashboard_id ON visualizations(dashboard_id);
CREATE INDEX idx_visualizations_created_by ON visualizations(created_by);

-- ============================================================================
-- QUERIES
-- ============================================================================

CREATE TABLE queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sql_query TEXT NOT NULL,
    data_source_id UUID REFERENCES data_sources(id),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_executed TIMESTAMP,
    execution_count INTEGER DEFAULT 0,
    avg_execution_time FLOAT,
    is_saved BOOLEAN DEFAULT true
);

CREATE INDEX idx_queries_data_source_id ON queries(data_source_id);
CREATE INDEX idx_queries_created_by ON queries(created_by);
CREATE INDEX idx_queries_name ON queries USING gin(name gin_trgm_ops);

-- ============================================================================
-- QUERY HISTORY
-- ============================================================================

CREATE TABLE query_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_id UUID REFERENCES queries(id),
    user_id UUID REFERENCES users(id),
    sql_query TEXT NOT NULL,
    execution_time FLOAT,
    row_count INTEGER,
    status VARCHAR(50),
    error_message TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_query_history_query_id ON query_history(query_id);
CREATE INDEX idx_query_history_user_id ON query_history(user_id);
CREATE INDEX idx_query_history_executed_at ON query_history(executed_at);

-- ============================================================================
-- ALERTS
-- ============================================================================

CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    condition JSONB NOT NULL,
    query_id UUID REFERENCES queries(id),
    notification_channels JSONB,
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_triggered TIMESTAMP,
    trigger_count INTEGER DEFAULT 0
);

CREATE INDEX idx_alerts_query_id ON alerts(query_id);
CREATE INDEX idx_alerts_created_by ON alerts(created_by);
CREATE INDEX idx_alerts_is_active ON alerts(is_active);

-- ============================================================================
-- ALERT HISTORY
-- ============================================================================

CREATE TABLE alert_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_id UUID REFERENCES alerts(id),
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    condition_met JSONB,
    notification_sent BOOLEAN DEFAULT false,
    notification_status JSONB
);

CREATE INDEX idx_alert_history_alert_id ON alert_history(alert_id);
CREATE INDEX idx_alert_history_triggered_at ON alert_history(triggered_at);

-- ============================================================================
-- SCHEDULED JOBS
-- ============================================================================

CREATE TABLE scheduled_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    schedule VARCHAR(100) NOT NULL,
    config JSONB,
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_run TIMESTAMP,
    next_run TIMESTAMP,
    run_count INTEGER DEFAULT 0
);

CREATE INDEX idx_scheduled_jobs_type ON scheduled_jobs(type);
CREATE INDEX idx_scheduled_jobs_is_active ON scheduled_jobs(is_active);
CREATE INDEX idx_scheduled_jobs_next_run ON scheduled_jobs(next_run);

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
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- ============================================================================
-- API KEYS
-- ============================================================================

CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    permissions JSONB,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP
);

CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active);

-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

-- Insert sample users
INSERT INTO users (email, username, password_hash, full_name, role, is_active, is_verified) VALUES
('admin@itechsmart.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qXqJqQqKa', 'System Administrator', 'admin', true, true),
('analyst@itechsmart.com', 'analyst', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qXqJqQqKa', 'Data Analyst', 'analyst', true, true),
('viewer@itechsmart.com', 'viewer', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qXqJqQqKa', 'Report Viewer', 'viewer', true, true);

-- Insert sample data sources
INSERT INTO data_sources (name, type, connection_string, config, status, created_by) VALUES
('Production Database', 'postgresql', 'postgresql://user:pass@localhost:5432/prod', '{"ssl": true, "pool_size": 10}', 'active', (SELECT id FROM users WHERE username = 'admin')),
('Analytics Warehouse', 'clickhouse', 'clickhouse://localhost:9000/analytics', '{"compression": true}', 'active', (SELECT id FROM users WHERE username = 'admin')),
('Sales CRM', 'mysql', 'mysql://user:pass@localhost:3306/crm', '{"charset": "utf8mb4"}', 'active', (SELECT id FROM users WHERE username = 'admin')),
('Marketing Data', 'mongodb', 'mongodb://localhost:27017/marketing', '{"auth_source": "admin"}', 'active', (SELECT id FROM users WHERE username = 'admin')),
('Customer Data Lake', 's3', 's3://customer-data-lake', '{"region": "us-east-1"}', 'active', (SELECT id FROM users WHERE username = 'admin'));

-- Insert sample datasets
INSERT INTO datasets (name, description, source_id, query, schema, row_count, size_bytes, refresh_schedule, created_by) VALUES
('Sales Transactions', 'Daily sales transaction data', (SELECT id FROM data_sources WHERE name = 'Production Database'), 'SELECT * FROM sales_transactions WHERE date >= CURRENT_DATE - INTERVAL ''30 days''', '{"columns": [{"name": "id", "type": "integer"}, {"name": "amount", "type": "decimal"}, {"name": "date", "type": "date"}]}', 125000, 5242880, 'daily', (SELECT id FROM users WHERE username = 'admin')),
('Customer Analytics', 'Customer behavior and demographics', (SELECT id FROM data_sources WHERE name = 'Analytics Warehouse'), 'SELECT * FROM customer_analytics', '{"columns": [{"name": "customer_id", "type": "string"}, {"name": "lifetime_value", "type": "decimal"}, {"name": "segment", "type": "string"}]}', 50000, 2097152, 'hourly', (SELECT id FROM users WHERE username = 'analyst')),
('Product Performance', 'Product sales and inventory metrics', (SELECT id FROM data_sources WHERE name = 'Production Database'), 'SELECT * FROM product_metrics', '{"columns": [{"name": "product_id", "type": "string"}, {"name": "units_sold", "type": "integer"}, {"name": "revenue", "type": "decimal"}]}', 10000, 524288, 'daily', (SELECT id FROM users WHERE username = 'analyst'));

-- Insert sample dashboards
INSERT INTO dashboards (name, description, layout, config, created_by, is_public, tags) VALUES
('Executive Dashboard', 'High-level business metrics for executives', '{"widgets": [{"id": "w1", "x": 0, "y": 0, "w": 6, "h": 4}, {"id": "w2", "x": 6, "y": 0, "w": 6, "h": 4}]}', '{"refresh_interval": 300, "theme": "light"}', (SELECT id FROM users WHERE username = 'admin'), true, ARRAY['executive', 'overview']),
('Sales Analytics', 'Detailed sales performance analysis', '{"widgets": [{"id": "w1", "x": 0, "y": 0, "w": 12, "h": 6}]}', '{"refresh_interval": 600, "theme": "light"}', (SELECT id FROM users WHERE username = 'analyst'), true, ARRAY['sales', 'analytics']),
('Customer Insights', 'Customer behavior and segmentation', '{"widgets": [{"id": "w1", "x": 0, "y": 0, "w": 8, "h": 5}, {"id": "w2", "x": 8, "y": 0, "w": 4, "h": 5}]}', '{"refresh_interval": 900, "theme": "dark"}', (SELECT id FROM users WHERE username = 'analyst'), false, ARRAY['customer', 'insights']);

-- Insert sample reports
INSERT INTO reports (name, description, type, config, dataset_id, created_by, is_public, tags) VALUES
('Monthly Sales Report', 'Comprehensive monthly sales analysis', 'tabular', '{"format": "pdf", "schedule": "monthly"}', (SELECT id FROM datasets WHERE name = 'Sales Transactions'), (SELECT id FROM users WHERE username = 'admin'), true, ARRAY['sales', 'monthly']),
('Customer Segmentation', 'Customer segments by behavior and value', 'analytical', '{"format": "excel", "schedule": "weekly"}', (SELECT id FROM datasets WHERE name = 'Customer Analytics'), (SELECT id FROM users WHERE username = 'analyst'), true, ARRAY['customer', 'segmentation']),
('Product Performance Summary', 'Top and bottom performing products', 'summary', '{"format": "pdf", "schedule": "weekly"}', (SELECT id FROM datasets WHERE name = 'Product Performance'), (SELECT id FROM users WHERE username = 'analyst'), false, ARRAY['product', 'performance']);

-- Insert sample visualizations
INSERT INTO visualizations (name, type, config, query, dataset_id, dashboard_id, position, created_by) VALUES
('Revenue Trend', 'line', '{"x_axis": "date", "y_axis": "revenue", "color": "#3b82f6"}', 'SELECT date, SUM(amount) as revenue FROM sales_transactions GROUP BY date ORDER BY date', (SELECT id FROM datasets WHERE name = 'Sales Transactions'), (SELECT id FROM dashboards WHERE name = 'Executive Dashboard'), '{"x": 0, "y": 0, "w": 6, "h": 4}', (SELECT id FROM users WHERE username = 'admin')),
('Customer Segments', 'pie', '{"label": "segment", "value": "count", "colors": ["#3b82f6", "#10b981", "#f59e0b"]}', 'SELECT segment, COUNT(*) as count FROM customer_analytics GROUP BY segment', (SELECT id FROM datasets WHERE name = 'Customer Analytics'), (SELECT id FROM dashboards WHERE name = 'Customer Insights'), '{"x": 0, "y": 0, "w": 4, "h": 4}', (SELECT id FROM users WHERE username = 'analyst')),
('Top Products', 'bar', '{"x_axis": "product_name", "y_axis": "units_sold", "color": "#10b981"}', 'SELECT product_name, units_sold FROM product_metrics ORDER BY units_sold DESC LIMIT 10', (SELECT id FROM datasets WHERE name = 'Product Performance'), (SELECT id FROM dashboards WHERE name = 'Sales Analytics'), '{"x": 0, "y": 0, "w": 12, "h": 6}', (SELECT id FROM users WHERE username = 'analyst'));

-- Insert sample queries
INSERT INTO queries (name, description, sql_query, data_source_id, created_by, execution_count, avg_execution_time, is_saved) VALUES
('Daily Revenue', 'Calculate total revenue for today', 'SELECT SUM(amount) as total_revenue FROM sales_transactions WHERE date = CURRENT_DATE', (SELECT id FROM data_sources WHERE name = 'Production Database'), (SELECT id FROM users WHERE username = 'admin'), 150, 0.25, true),
('Active Customers', 'Count of active customers in last 30 days', 'SELECT COUNT(DISTINCT customer_id) as active_customers FROM customer_analytics WHERE last_activity >= CURRENT_DATE - INTERVAL ''30 days''', (SELECT id FROM data_sources WHERE name = 'Analytics Warehouse'), (SELECT id FROM users WHERE username = 'analyst'), 75, 0.50, true),
('Low Stock Products', 'Products with inventory below threshold', 'SELECT product_id, product_name, stock_level FROM product_metrics WHERE stock_level < 100 ORDER BY stock_level ASC', (SELECT id FROM data_sources WHERE name = 'Production Database'), (SELECT id FROM users WHERE username = 'analyst'), 50, 0.15, true);

-- Insert sample alerts
INSERT INTO alerts (name, description, condition, query_id, notification_channels, is_active, created_by, trigger_count) VALUES
('Low Revenue Alert', 'Alert when daily revenue drops below threshold', '{"operator": "less_than", "threshold": 10000, "field": "total_revenue"}', (SELECT id FROM queries WHERE name = 'Daily Revenue'), '{"email": ["admin@itechsmart.com"], "slack": ["#alerts"]}', true, (SELECT id FROM users WHERE username = 'admin'), 5),
('Low Stock Alert', 'Alert when products are running low on stock', '{"operator": "less_than", "threshold": 50, "field": "stock_level"}', (SELECT id FROM queries WHERE name = 'Low Stock Products'), '{"email": ["inventory@itechsmart.com"], "sms": ["+1234567890"]}', true, (SELECT id FROM users WHERE username = 'analyst'), 12);

-- Insert sample scheduled jobs
INSERT INTO scheduled_jobs (name, type, schedule, config, is_active, created_by, run_count) VALUES
('Daily Sales Report', 'report_generation', '0 8 * * *', '{"report_id": "monthly-sales", "format": "pdf", "recipients": ["admin@itechsmart.com"]}', true, (SELECT id FROM users WHERE username = 'admin'), 30),
('Hourly Data Refresh', 'data_refresh', '0 * * * *', '{"dataset_ids": ["customer-analytics"], "mode": "incremental"}', true, (SELECT id FROM users WHERE username = 'admin'), 720),
('Weekly Backup', 'backup', '0 2 * * 0', '{"type": "full", "retention_days": 30, "destination": "s3://backups"}', true, (SELECT id FROM users WHERE username = 'admin'), 4);

-- Insert sample audit logs
INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details, ip_address) VALUES
((SELECT id FROM users WHERE username = 'admin'), 'create', 'dashboard', (SELECT id FROM dashboards WHERE name = 'Executive Dashboard'), '{"name": "Executive Dashboard"}', '192.168.1.100'),
((SELECT id FROM users WHERE username = 'analyst'), 'execute', 'query', (SELECT id FROM queries WHERE name = 'Daily Revenue'), '{"execution_time": 0.25}', '192.168.1.101'),
((SELECT id FROM users WHERE username = 'admin'), 'update', 'data_source', (SELECT id FROM data_sources WHERE name = 'Production Database'), '{"field": "config", "old_value": "{}", "new_value": "{}"}', '192.168.1.100');

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

-- Apply updated_at trigger to all relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_data_sources_updated_at BEFORE UPDATE ON data_sources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_datasets_updated_at BEFORE UPDATE ON datasets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON reports FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_dashboards_updated_at BEFORE UPDATE ON dashboards FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_visualizations_updated_at BEFORE UPDATE ON visualizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_queries_updated_at BEFORE UPDATE ON queries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE ON alerts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_scheduled_jobs_updated_at BEFORE UPDATE ON scheduled_jobs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View for dashboard statistics
CREATE OR REPLACE VIEW dashboard_stats AS
SELECT 
    d.id,
    d.name,
    d.created_by,
    u.full_name as creator_name,
    COUNT(DISTINCT v.id) as visualization_count,
    d.created_at,
    d.updated_at
FROM dashboards d
LEFT JOIN visualizations v ON v.dashboard_id = d.id
LEFT JOIN users u ON u.id = d.created_by
GROUP BY d.id, d.name, d.created_by, u.full_name, d.created_at, d.updated_at;

-- View for query performance
CREATE OR REPLACE VIEW query_performance AS
SELECT 
    q.id,
    q.name,
    q.execution_count,
    q.avg_execution_time,
    COUNT(qh.id) as history_count,
    MAX(qh.executed_at) as last_executed,
    AVG(qh.execution_time) as actual_avg_time
FROM queries q
LEFT JOIN query_history qh ON qh.query_id = q.id
GROUP BY q.id, q.name, q.execution_count, q.avg_execution_time;

-- View for user activity
CREATE OR REPLACE VIEW user_activity AS
SELECT 
    u.id,
    u.username,
    u.full_name,
    COUNT(DISTINCT al.id) as action_count,
    MAX(al.created_at) as last_activity,
    COUNT(DISTINCT CASE WHEN al.action = 'login' THEN al.id END) as login_count
FROM users u
LEFT JOIN audit_logs al ON al.user_id = u.id
GROUP BY u.id, u.username, u.full_name;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'iTechSmart Pulse Database Initialization Complete!';
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'Tables Created: 15';
    RAISE NOTICE 'Indexes Created: 40+';
    RAISE NOTICE 'Sample Users: 3 (admin, analyst, viewer)';
    RAISE NOTICE 'Sample Data Sources: 5';
    RAISE NOTICE 'Sample Datasets: 3';
    RAISE NOTICE 'Sample Dashboards: 3';
    RAISE NOTICE 'Sample Reports: 3';
    RAISE NOTICE 'Sample Visualizations: 3';
    RAISE NOTICE 'Sample Queries: 3';
    RAISE NOTICE 'Sample Alerts: 2';
    RAISE NOTICE 'Sample Scheduled Jobs: 3';
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'Default Login Credentials:';
    RAISE NOTICE 'Admin: admin@itechsmart.com / password';
    RAISE NOTICE 'Analyst: analyst@itechsmart.com / password';
    RAISE NOTICE 'Viewer: viewer@itechsmart.com / password';
    RAISE NOTICE '=================================================================';
END $$;