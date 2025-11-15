-- iTechSmart Pulse ClickHouse Initialization Script
-- This script creates analytics tables optimized for OLAP queries

-- ============================================================================
-- ANALYTICS EVENTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.events (
    event_id UUID DEFAULT generateUUIDv4(),
    event_type String,
    user_id String,
    session_id String,
    timestamp DateTime DEFAULT now(),
    properties String,
    page_url String,
    referrer String,
    user_agent String,
    ip_address String,
    country String,
    city String,
    device_type String,
    browser String,
    os String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (event_type, user_id, timestamp)
TTL timestamp + INTERVAL 2 YEAR;

-- ============================================================================
-- QUERY METRICS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.query_metrics (
    query_id UUID DEFAULT generateUUIDv4(),
    user_id String,
    query_text String,
    execution_time Float64,
    rows_returned UInt64,
    bytes_scanned UInt64,
    status String,
    error_message String,
    timestamp DateTime DEFAULT now(),
    data_source String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (user_id, timestamp)
TTL timestamp + INTERVAL 1 YEAR;

-- ============================================================================
-- DASHBOARD VIEWS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.dashboard_views (
    view_id UUID DEFAULT generateUUIDv4(),
    dashboard_id String,
    user_id String,
    view_duration UInt32,
    timestamp DateTime DEFAULT now(),
    session_id String,
    device_type String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (dashboard_id, user_id, timestamp)
TTL timestamp + INTERVAL 1 YEAR;

-- ============================================================================
-- REPORT EXECUTIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.report_executions (
    execution_id UUID DEFAULT generateUUIDv4(),
    report_id String,
    user_id String,
    execution_time Float64,
    rows_generated UInt64,
    status String,
    timestamp DateTime DEFAULT now(),
    format String,
    file_size UInt64
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (report_id, timestamp)
TTL timestamp + INTERVAL 2 YEAR;

-- ============================================================================
-- DATA SOURCE METRICS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.data_source_metrics (
    metric_id UUID DEFAULT generateUUIDv4(),
    data_source_id String,
    metric_type String,
    metric_value Float64,
    timestamp DateTime DEFAULT now(),
    tags String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (data_source_id, metric_type, timestamp)
TTL timestamp + INTERVAL 6 MONTH;

-- ============================================================================
-- ALERT TRIGGERS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.alert_triggers (
    trigger_id UUID DEFAULT generateUUIDv4(),
    alert_id String,
    condition_met String,
    threshold_value Float64,
    actual_value Float64,
    timestamp DateTime DEFAULT now(),
    notification_sent UInt8,
    notification_channels String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (alert_id, timestamp)
TTL timestamp + INTERVAL 1 YEAR;

-- ============================================================================
-- USER ACTIVITY TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.user_activity (
    activity_id UUID DEFAULT generateUUIDv4(),
    user_id String,
    action String,
    resource_type String,
    resource_id String,
    timestamp DateTime DEFAULT now(),
    session_id String,
    ip_address String,
    duration UInt32
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (user_id, action, timestamp)
TTL timestamp + INTERVAL 2 YEAR;

-- ============================================================================
-- SYSTEM PERFORMANCE TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.system_performance (
    metric_id UUID DEFAULT generateUUIDv4(),
    service_name String,
    metric_name String,
    metric_value Float64,
    timestamp DateTime DEFAULT now(),
    host String,
    tags String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (service_name, metric_name, timestamp)
TTL timestamp + INTERVAL 3 MONTH;

-- ============================================================================
-- MATERIALIZED VIEWS FOR AGGREGATIONS
-- ============================================================================

-- Daily event counts by type
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.daily_events_mv
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (event_type, date)
AS SELECT
    event_type,
    toDate(timestamp) as date,
    count() as event_count,
    uniq(user_id) as unique_users,
    uniq(session_id) as unique_sessions
FROM analytics.events
GROUP BY event_type, date;

-- Hourly query performance
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.hourly_query_performance_mv
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (data_source, hour)
AS SELECT
    data_source,
    toStartOfHour(timestamp) as hour,
    count() as query_count,
    avg(execution_time) as avg_execution_time,
    quantile(0.95)(execution_time) as p95_execution_time,
    sum(rows_returned) as total_rows,
    sum(bytes_scanned) as total_bytes
FROM analytics.query_metrics
GROUP BY data_source, hour;

-- Daily dashboard popularity
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.daily_dashboard_popularity_mv
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (dashboard_id, date)
AS SELECT
    dashboard_id,
    toDate(timestamp) as date,
    count() as view_count,
    uniq(user_id) as unique_viewers,
    avg(view_duration) as avg_duration
FROM analytics.dashboard_views
GROUP BY dashboard_id, date;

-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

-- Insert sample events
INSERT INTO analytics.events (event_type, user_id, session_id, properties, page_url, device_type, browser, os) VALUES
('page_view', 'user_001', 'session_001', '{"page": "dashboard"}', '/dashboard', 'desktop', 'Chrome', 'Windows'),
('page_view', 'user_002', 'session_002', '{"page": "reports"}', '/reports', 'mobile', 'Safari', 'iOS'),
('query_execute', 'user_001', 'session_001', '{"query_id": "q001"}', '/query-builder', 'desktop', 'Chrome', 'Windows'),
('report_generate', 'user_003', 'session_003', '{"report_id": "r001"}', '/reports', 'desktop', 'Firefox', 'Linux'),
('dashboard_view', 'user_002', 'session_002', '{"dashboard_id": "d001"}', '/dashboard/executive', 'mobile', 'Safari', 'iOS');

-- Insert sample query metrics
INSERT INTO analytics.query_metrics (user_id, query_text, execution_time, rows_returned, bytes_scanned, status, data_source) VALUES
('user_001', 'SELECT * FROM sales_transactions WHERE date >= today() - 7', 0.245, 15000, 524288, 'success', 'production_db'),
('user_002', 'SELECT customer_id, SUM(amount) FROM orders GROUP BY customer_id', 1.532, 5000, 1048576, 'success', 'analytics_warehouse'),
('user_003', 'SELECT * FROM products WHERE category = ''Electronics''', 0.089, 250, 102400, 'success', 'production_db'),
('user_001', 'SELECT COUNT(*) FROM users WHERE created_at >= today()', 0.034, 1, 8192, 'success', 'production_db'),
('user_002', 'SELECT * FROM invalid_table', 0.012, 0, 0, 'error', 'production_db');

-- Insert sample dashboard views
INSERT INTO analytics.dashboard_views (dashboard_id, user_id, view_duration, session_id, device_type) VALUES
('dashboard_001', 'user_001', 300, 'session_001', 'desktop'),
('dashboard_002', 'user_002', 180, 'session_002', 'mobile'),
('dashboard_001', 'user_003', 450, 'session_003', 'desktop'),
('dashboard_003', 'user_001', 120, 'session_001', 'desktop'),
('dashboard_002', 'user_004', 240, 'session_004', 'tablet');

-- Insert sample report executions
INSERT INTO analytics.report_executions (report_id, user_id, execution_time, rows_generated, status, format, file_size) VALUES
('report_001', 'user_001', 2.5, 10000, 'success', 'pdf', 2097152),
('report_002', 'user_002', 1.8, 5000, 'success', 'excel', 1048576),
('report_003', 'user_003', 3.2, 15000, 'success', 'csv', 524288),
('report_001', 'user_004', 2.3, 10000, 'success', 'pdf', 2097152),
('report_004', 'user_002', 0.5, 0, 'error', 'pdf', 0);

-- Insert sample data source metrics
INSERT INTO analytics.data_source_metrics (data_source_id, metric_type, metric_value, tags) VALUES
('ds_001', 'connection_time', 0.045, 'production'),
('ds_001', 'query_count', 150, 'production'),
('ds_002', 'connection_time', 0.089, 'analytics'),
('ds_002', 'query_count', 75, 'analytics'),
('ds_003', 'connection_time', 0.023, 'staging');

-- Insert sample alert triggers
INSERT INTO analytics.alert_triggers (alert_id, condition_met, threshold_value, actual_value, notification_sent, notification_channels) VALUES
('alert_001', 'revenue < threshold', 10000, 8500, 1, 'email,slack'),
('alert_002', 'stock_level < threshold', 100, 45, 1, 'email,sms'),
('alert_003', 'error_rate > threshold', 0.05, 0.08, 1, 'slack,pagerduty');

-- Insert sample user activity
INSERT INTO analytics.user_activity (user_id, action, resource_type, resource_id, session_id, ip_address, duration) VALUES
('user_001', 'create', 'dashboard', 'dashboard_001', 'session_001', '192.168.1.100', 45),
('user_002', 'execute', 'query', 'query_001', 'session_002', '192.168.1.101', 2),
('user_003', 'view', 'report', 'report_001', 'session_003', '192.168.1.102', 120),
('user_001', 'update', 'visualization', 'viz_001', 'session_001', '192.168.1.100', 30),
('user_004', 'delete', 'dataset', 'dataset_001', 'session_004', '192.168.1.103', 5);

-- Insert sample system performance
INSERT INTO analytics.system_performance (service_name, metric_name, metric_value, host, tags) VALUES
('backend', 'cpu_usage', 45.5, 'host-001', 'production'),
('backend', 'memory_usage', 2048, 'host-001', 'production'),
('frontend', 'response_time', 0.125, 'host-002', 'production'),
('database', 'connection_pool', 25, 'host-003', 'production'),
('cache', 'hit_rate', 0.85, 'host-004', 'production');