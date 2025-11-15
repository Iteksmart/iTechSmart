-- iTechSmart Vault - Database Initialization Script
-- PostgreSQL Database Schema with Sample Data

-- Drop existing tables
DROP TABLE IF EXISTS api_keys CASCADE;
DROP TABLE IF EXISTS secret_shares CASCADE;
DROP TABLE IF EXISTS secret_rotations CASCADE;
DROP TABLE IF EXISTS encryption_keys CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS access_grants CASCADE;
DROP TABLE IF EXISTS policies CASCADE;
DROP TABLE IF EXISTS secret_versions CASCADE;
DROP TABLE IF EXISTS secrets CASCADE;
DROP TABLE IF EXISTS vaults CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create ENUM types
CREATE TYPE secret_type AS ENUM ('password', 'api_key', 'token', 'certificate', 'ssh_key', 'database_credential', 'encryption_key', 'generic');
CREATE TYPE secret_status AS ENUM ('active', 'expired', 'revoked', 'archived');
CREATE TYPE policy_effect AS ENUM ('allow', 'deny');
CREATE TYPE audit_action AS ENUM ('create', 'read', 'update', 'delete', 'rotate', 'share', 'revoke');

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vaults table
CREATE TABLE vaults (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_default BOOLEAN DEFAULT FALSE,
    encryption_key_id VARCHAR(255),
    tags JSONB,
    metadata JSONB,
    secret_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Secrets table
CREATE TABLE secrets (
    id SERIAL PRIMARY KEY,
    vault_id INTEGER NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    secret_type secret_type NOT NULL,
    status secret_status DEFAULT 'active',
    encrypted_value BYTEA NOT NULL,
    encryption_algorithm VARCHAR(50) DEFAULT 'AES-256-GCM',
    version INTEGER DEFAULT 1,
    current_version_id INTEGER,
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    tags JSONB,
    metadata JSONB,
    expires_at TIMESTAMP,
    last_rotated_at TIMESTAMP,
    rotation_interval_days INTEGER,
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Secret versions table
CREATE TABLE secret_versions (
    id SERIAL PRIMARY KEY,
    secret_id INTEGER NOT NULL REFERENCES secrets(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    encrypted_value BYTEA NOT NULL,
    encryption_algorithm VARCHAR(50) DEFAULT 'AES-256-GCM',
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    change_description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Policies table
CREATE TABLE policies (
    id SERIAL PRIMARY KEY,
    vault_id INTEGER NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    effect policy_effect NOT NULL,
    actions JSONB NOT NULL,
    resources JSONB NOT NULL,
    conditions JSONB,
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Access grants table
CREATE TABLE access_grants (
    id SERIAL PRIMARY KEY,
    secret_id INTEGER NOT NULL REFERENCES secrets(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    granted_by_id INTEGER NOT NULL REFERENCES users(id),
    permissions JSONB NOT NULL,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action audit_action NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id INTEGER,
    resource_name VARCHAR(255),
    vault_id INTEGER REFERENCES vaults(id) ON DELETE SET NULL,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Encryption keys table
CREATE TABLE encryption_keys (
    id SERIAL PRIMARY KEY,
    key_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    algorithm VARCHAR(50) DEFAULT 'AES-256-GCM',
    encrypted_key BYTEA NOT NULL,
    key_version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    is_master BOOLEAN DEFAULT FALSE,
    rotation_schedule VARCHAR(100),
    last_rotated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Secret rotations table
CREATE TABLE secret_rotations (
    id SERIAL PRIMARY KEY,
    secret_id INTEGER NOT NULL REFERENCES secrets(id) ON DELETE CASCADE,
    old_version INTEGER NOT NULL,
    new_version INTEGER NOT NULL,
    rotation_type VARCHAR(50),
    rotated_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    rotation_reason TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Secret shares table
CREATE TABLE secret_shares (
    id SERIAL PRIMARY KEY,
    secret_id INTEGER NOT NULL REFERENCES secrets(id) ON DELETE CASCADE,
    share_token VARCHAR(255) UNIQUE NOT NULL,
    shared_by_id INTEGER NOT NULL REFERENCES users(id),
    max_access_count INTEGER DEFAULT 1,
    access_count INTEGER DEFAULT 0,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API keys table
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(20) NOT NULL,
    scopes JSONB,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_vaults_owner ON vaults(owner_id);
CREATE INDEX idx_secrets_vault ON secrets(vault_id);
CREATE INDEX idx_secrets_type ON secrets(secret_type);
CREATE INDEX idx_secrets_status ON secrets(status);
CREATE INDEX idx_secrets_created_by ON secrets(created_by_id);
CREATE INDEX idx_secret_versions_secret ON secret_versions(secret_id);
CREATE INDEX idx_policies_vault ON policies(vault_id);
CREATE INDEX idx_access_grants_secret ON access_grants(secret_id);
CREATE INDEX idx_access_grants_user ON access_grants(user_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);
CREATE INDEX idx_secret_rotations_secret ON secret_rotations(secret_id);
CREATE INDEX idx_api_keys_user ON api_keys(user_id);

-- Insert sample data
-- Sample users (password is 'password' hashed with bcrypt)
INSERT INTO users (email, username, hashed_password, full_name, is_admin) VALUES
('admin@itechsmart.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQqK', 'Admin User', TRUE),
('john@itechsmart.com', 'john', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQqK', 'John Doe', FALSE),
('jane@itechsmart.com', 'jane', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQqK', 'Jane Smith', FALSE);

-- Sample vaults
INSERT INTO vaults (name, description, owner_id, is_default, secret_count) VALUES
('Default Vault', 'Default vault for storing secrets', 1, TRUE, 5),
('Production Secrets', 'Production environment secrets', 1, FALSE, 3),
('Development Secrets', 'Development environment secrets', 2, FALSE, 2);

-- Sample secrets (encrypted values are placeholders)
INSERT INTO secrets (vault_id, name, description, secret_type, status, encrypted_value, created_by_id, access_count) VALUES
(1, 'Database Password', 'Production database password', 'password', 'active', E'\\x656e637279707465645f76616c7565', 1, 45),
(1, 'API Key - Stripe', 'Stripe payment API key', 'api_key', 'active', E'\\x656e637279707465645f76616c7565', 1, 23),
(1, 'AWS Access Token', 'AWS S3 access token', 'token', 'active', E'\\x656e637279707465645f76616c7565', 1, 12),
(1, 'SSL Certificate', 'Production SSL certificate', 'certificate', 'active', E'\\x656e637279707465645f76616c7565', 1, 8),
(1, 'SSH Private Key', 'Server SSH private key', 'ssh_key', 'active', E'\\x656e637279707465645f76616c7565', 1, 34),
(2, 'DB Connection String', 'Production database connection', 'database_credential', 'active', E'\\x656e637279707465645f76616c7565', 1, 67),
(2, 'Redis Password', 'Redis cache password', 'password', 'active', E'\\x656e637279707465645f76616c7565', 1, 28),
(2, 'JWT Secret', 'JWT signing secret', 'encryption_key', 'active', E'\\x656e637279707465645f76616c7565', 1, 156),
(3, 'Dev API Key', 'Development API key', 'api_key', 'active', E'\\x656e637279707465645f76616c7565', 2, 89),
(3, 'Test Token', 'Testing authentication token', 'token', 'active', E'\\x656e637279707465645f76616c7565', 2, 45);

-- Sample audit logs
INSERT INTO audit_logs (user_id, action, resource_type, resource_id, resource_name, vault_id, success) VALUES
(1, 'create', 'secret', 1, 'Database Password', 1, TRUE),
(1, 'read', 'secret', 1, 'Database Password', 1, TRUE),
(1, 'create', 'vault', 2, 'Production Secrets', NULL, TRUE),
(2, 'read', 'secret', 9, 'Dev API Key', 3, TRUE),
(1, 'rotate', 'secret', 3, 'AWS Access Token', 1, TRUE);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vault_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vault_user;

SELECT 'Database initialized successfully!' as message;