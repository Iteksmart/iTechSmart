-- iTechSmart Shield Database Initialization Script

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Threats table
CREATE TABLE IF NOT EXISTS threats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    source VARCHAR(255) NOT NULL,
    target VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'mitigated', 'investigating')),
    indicators JSONB DEFAULT '[]',
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Vulnerabilities table
CREATE TABLE IF NOT EXISTS vulnerabilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cve_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    cvss_score DECIMAL(3,1) NOT NULL CHECK (cvss_score >= 0 AND cvss_score <= 10),
    affected_systems JSONB DEFAULT '[]',
    status VARCHAR(50) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved')),
    patch_available BOOLEAN DEFAULT FALSE,
    remediation TEXT,
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Compliance frameworks table
CREATE TABLE IF NOT EXISTS compliance_frameworks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    total_controls INTEGER NOT NULL DEFAULT 0,
    passed_controls INTEGER NOT NULL DEFAULT 0,
    failed_controls INTEGER NOT NULL DEFAULT 0,
    compliance_score DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    status VARCHAR(50) NOT NULL DEFAULT 'non_compliant' CHECK (status IN ('compliant', 'non_compliant', 'partial')),
    last_assessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Compliance controls table
CREATE TABLE IF NOT EXISTS compliance_controls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    framework_id UUID REFERENCES compliance_frameworks(id) ON DELETE CASCADE,
    control_id VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'not_tested' CHECK (status IN ('passed', 'failed', 'not_tested')),
    evidence JSONB DEFAULT '[]',
    last_tested TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(framework_id, control_id)
);

-- Incidents table
CREATE TABLE IF NOT EXISTS incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    status VARCHAR(50) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'contained', 'resolved', 'closed')),
    category VARCHAR(100) NOT NULL,
    affected_systems JSONB DEFAULT '[]',
    assigned_to VARCHAR(255),
    reported_by VARCHAR(255) NOT NULL,
    resolution_time INTEGER, -- in minutes
    timeline JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Security events table
CREATE TABLE IF NOT EXISTS security_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info')),
    source VARCHAR(255) NOT NULL,
    destination VARCHAR(255),
    description TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255),
    details JSONB DEFAULT '{}',
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_threats_severity ON threats(severity);
CREATE INDEX idx_threats_status ON threats(status);
CREATE INDEX idx_threats_detected_at ON threats(detected_at DESC);

CREATE INDEX idx_vulnerabilities_severity ON vulnerabilities(severity);
CREATE INDEX idx_vulnerabilities_status ON vulnerabilities(status);
CREATE INDEX idx_vulnerabilities_cve_id ON vulnerabilities(cve_id);

CREATE INDEX idx_incidents_severity ON incidents(severity);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_created_at ON incidents(created_at DESC);

CREATE INDEX idx_security_events_type ON security_events(event_type);
CREATE INDEX idx_security_events_severity ON security_events(severity);
CREATE INDEX idx_security_events_timestamp ON security_events(timestamp DESC);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_threats_updated_at BEFORE UPDATE ON threats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vulnerabilities_updated_at BEFORE UPDATE ON vulnerabilities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_compliance_frameworks_updated_at BEFORE UPDATE ON compliance_frameworks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_compliance_controls_updated_at BEFORE UPDATE ON compliance_controls
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_incidents_updated_at BEFORE UPDATE ON incidents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for demonstration

-- Sample threats
INSERT INTO threats (type, severity, source, target, description, status, indicators) VALUES
('Malware', 'critical', '192.168.1.100', '10.0.0.50', 'Ransomware detected attempting to encrypt files', 'active', '["trojan.exe", "C2: malicious-domain.com"]'),
('DDoS', 'high', '203.0.113.0/24', 'web-server-01', 'Distributed denial of service attack detected', 'investigating', '["SYN flood", "10000 req/sec"]'),
('Phishing', 'medium', 'external-email', 'user@company.com', 'Phishing email with malicious attachment detected', 'mitigated', '["invoice.pdf.exe", "sender: fake@bank.com"]');

-- Sample vulnerabilities
INSERT INTO vulnerabilities (cve_id, title, description, severity, cvss_score, affected_systems, status, patch_available, remediation) VALUES
('CVE-2024-0001', 'Critical Remote Code Execution in Web Server', 'A critical vulnerability allows remote attackers to execute arbitrary code', 'critical', 9.8, '["web-server-01", "web-server-02"]', 'open', true, 'Apply security patch version 2.1.5 immediately'),
('CVE-2024-0002', 'SQL Injection in Database API', 'SQL injection vulnerability in API endpoint allows data exfiltration', 'high', 8.2, '["api-server-01"]', 'in_progress', true, 'Update to version 3.0.1 and implement input validation'),
('CVE-2023-9999', 'Cross-Site Scripting in Admin Panel', 'XSS vulnerability in admin panel could lead to session hijacking', 'medium', 6.5, '["admin-portal"]', 'resolved', true, 'Patch applied successfully');

-- Sample compliance frameworks
INSERT INTO compliance_frameworks (name, description, total_controls, passed_controls, failed_controls, compliance_score, status) VALUES
('SOC2', 'Service Organization Control 2 - Trust Services Criteria', 150, 135, 15, 90.0, 'partial'),
('ISO27001', 'Information Security Management System Standard', 114, 100, 14, 87.7, 'partial'),
('GDPR', 'General Data Protection Regulation', 99, 95, 4, 95.9, 'compliant'),
('HIPAA', 'Health Insurance Portability and Accountability Act', 164, 140, 24, 85.4, 'partial');

-- Sample compliance controls
INSERT INTO compliance_controls (framework_id, control_id, title, description, status, evidence) VALUES
((SELECT id FROM compliance_frameworks WHERE name = 'SOC2'), 'CC6.1', 'Logical and Physical Access Controls', 'The entity implements logical access security software, infrastructure, and architectures', 'passed', '["MFA enabled", "Access logs reviewed"]'),
((SELECT id FROM compliance_frameworks WHERE name = 'SOC2'), 'CC7.2', 'System Monitoring', 'The entity monitors system components and the operation of those components', 'passed', '["24/7 monitoring active", "Alert system configured"]'),
((SELECT id FROM compliance_frameworks WHERE name = 'ISO27001'), 'A.9.2.1', 'User Registration and De-registration', 'A formal user registration and de-registration process', 'failed', '["Manual process needs automation"]');

-- Sample incidents
INSERT INTO incidents (title, description, severity, status, category, affected_systems, assigned_to, reported_by, timeline) VALUES
('Data Breach Attempt', 'Unauthorized access attempt to customer database detected and blocked', 'critical', 'investigating', 'Data Security', '["db-server-01", "api-gateway"]', 'security-team@company.com', 'monitoring-system', '[{"timestamp": "2024-01-15T10:30:00Z", "action": "Incident detected", "user": "system"}, {"timestamp": "2024-01-15T10:35:00Z", "action": "Security team notified", "user": "system"}]'),
('Malware Infection', 'Malware detected on employee workstation, isolated from network', 'high', 'contained', 'Malware', '["workstation-042"]', 'it-support@company.com', 'antivirus-system', '[{"timestamp": "2024-01-14T14:20:00Z", "action": "Malware detected", "user": "system"}, {"timestamp": "2024-01-14T14:25:00Z", "action": "System quarantined", "user": "admin"}]'),
('Policy Violation', 'Employee attempted to access restricted resources', 'low', 'resolved', 'Policy', '["vpn-gateway"]', 'hr@company.com', 'dlp-system', '[{"timestamp": "2024-01-13T09:15:00Z", "action": "Violation detected", "user": "system"}, {"timestamp": "2024-01-13T16:00:00Z", "action": "Employee counseled", "user": "hr-manager"}, {"timestamp": "2024-01-13T16:30:00Z", "action": "Incident closed", "user": "hr-manager"}]');

-- Sample security events
INSERT INTO security_events (event_type, severity, source, destination, description, metadata) VALUES
('Login Attempt', 'info', '192.168.1.50', 'auth-server', 'Successful user login', '{"user": "john.doe", "method": "MFA"}'),
('Failed Login', 'medium', '203.0.113.45', 'auth-server', 'Multiple failed login attempts detected', '{"attempts": 5, "user": "admin"}'),
('File Access', 'info', '10.0.0.25', 'file-server', 'User accessed sensitive file', '{"file": "/data/confidential/report.pdf", "user": "jane.smith"}'),
('Network Scan', 'high', '198.51.100.10', 'firewall', 'Port scanning activity detected', '{"ports": "1-65535", "protocol": "TCP"}');

-- Sample audit logs
INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details, ip_address) VALUES
('admin@company.com', 'CREATE', 'threat', (SELECT id FROM threats WHERE type = 'Malware'), '{"severity": "critical"}', '10.0.0.1'),
('security@company.com', 'UPDATE', 'incident', (SELECT id FROM incidents WHERE title = 'Data Breach Attempt'), '{"status": "investigating"}', '10.0.0.2'),
('analyst@company.com', 'VIEW', 'vulnerability', (SELECT id FROM vulnerabilities WHERE cve_id = 'CVE-2024-0001'), '{"action": "viewed details"}', '10.0.0.3');

-- Create views for common queries
CREATE OR REPLACE VIEW active_threats_summary AS
SELECT 
    severity,
    COUNT(*) as count,
    MAX(detected_at) as latest_detection
FROM threats
WHERE status = 'active'
GROUP BY severity;

CREATE OR REPLACE VIEW open_vulnerabilities_summary AS
SELECT 
    severity,
    COUNT(*) as count,
    AVG(cvss_score) as avg_cvss_score
FROM vulnerabilities
WHERE status = 'open'
GROUP BY severity;

CREATE OR REPLACE VIEW compliance_overview AS
SELECT 
    name,
    compliance_score,
    status,
    (passed_controls::float / NULLIF(total_controls, 0) * 100) as pass_rate
FROM compliance_frameworks
ORDER BY compliance_score DESC;

-- Grant permissions (adjust as needed for your security requirements)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO shield_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO shield_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO shield_user;