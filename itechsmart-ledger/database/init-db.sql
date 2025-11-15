-- iTechSmart Ledger Database Initialization Script
-- PostgreSQL Database Schema

-- Drop existing tables if they exist
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS api_keys CASCADE;
DROP TABLE IF EXISTS network_configs CASCADE;
DROP TABLE IF EXISTS token_balances CASCADE;
DROP TABLE IF EXISTS tokens CASCADE;
DROP TABLE IF EXISTS blocks CASCADE;
DROP TABLE IF EXISTS contract_interactions CASCADE;
DROP TABLE IF EXISTS smart_contracts CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS wallets CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create Users table
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

-- Create Wallets table
CREATE TABLE wallets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) UNIQUE NOT NULL,
    network VARCHAR(50) NOT NULL,
    wallet_type VARCHAR(50) DEFAULT 'hot',
    balance DECIMAL(20, 8) DEFAULT 0.0,
    encrypted_private_key TEXT,
    public_key TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Transactions table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    from_wallet_id INTEGER REFERENCES wallets(id) ON DELETE SET NULL,
    to_wallet_id INTEGER REFERENCES wallets(id) ON DELETE SET NULL,
    from_address VARCHAR(255),
    to_address VARCHAR(255) NOT NULL,
    network VARCHAR(50) NOT NULL,
    amount DECIMAL(20, 8) NOT NULL,
    fee DECIMAL(20, 8) DEFAULT 0.0,
    gas_price DECIMAL(20, 8),
    gas_limit INTEGER,
    nonce INTEGER,
    transaction_hash VARCHAR(255) UNIQUE,
    block_number INTEGER,
    block_hash VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    confirmations INTEGER DEFAULT 0,
    metadata JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP
);

-- Create Smart Contracts table
CREATE TABLE smart_contracts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    network VARCHAR(50) NOT NULL,
    contract_address VARCHAR(255) UNIQUE,
    abi JSONB,
    bytecode TEXT,
    source_code TEXT,
    compiler_version VARCHAR(50),
    status VARCHAR(50) DEFAULT 'draft',
    deployment_transaction VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deployed_at TIMESTAMP
);

-- Create Contract Interactions table
CREATE TABLE contract_interactions (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES smart_contracts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    function_name VARCHAR(255) NOT NULL,
    parameters JSONB,
    transaction_hash VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    gas_used INTEGER,
    result JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Blocks table
CREATE TABLE blocks (
    id SERIAL PRIMARY KEY,
    network VARCHAR(50) NOT NULL,
    block_number INTEGER NOT NULL,
    block_hash VARCHAR(255) UNIQUE NOT NULL,
    parent_hash VARCHAR(255),
    timestamp TIMESTAMP NOT NULL,
    miner VARCHAR(255),
    difficulty VARCHAR(100),
    total_difficulty VARCHAR(100),
    size INTEGER,
    gas_used INTEGER,
    gas_limit INTEGER,
    transaction_count INTEGER DEFAULT 0,
    extra_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(network, block_number)
);

-- Create Tokens table
CREATE TABLE tokens (
    id SERIAL PRIMARY KEY,
    network VARCHAR(50) NOT NULL,
    contract_address VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    decimals INTEGER DEFAULT 18,
    total_supply VARCHAR(100),
    token_type VARCHAR(50),
    logo_url VARCHAR(500),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Token Balances table
CREATE TABLE token_balances (
    id SERIAL PRIMARY KEY,
    wallet_id INTEGER NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    token_id INTEGER NOT NULL REFERENCES tokens(id) ON DELETE CASCADE,
    balance VARCHAR(100) DEFAULT '0',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(wallet_id, token_id)
);

-- Create Network Configs table
CREATE TABLE network_configs (
    id SERIAL PRIMARY KEY,
    network VARCHAR(50) UNIQUE NOT NULL,
    rpc_url VARCHAR(500) NOT NULL,
    chain_id INTEGER,
    explorer_url VARCHAR(500),
    is_testnet BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    gas_price_multiplier DECIMAL(5, 2) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create API Keys table
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 1000,
    allowed_networks JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP
);

-- Create Audit Logs table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id INTEGER,
    details JSONB,
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Indexes for better query performance
CREATE INDEX idx_wallets_user_id ON wallets(user_id);
CREATE INDEX idx_wallets_address ON wallets(address);
CREATE INDEX idx_wallets_network ON wallets(network);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_from_wallet ON transactions(from_wallet_id);
CREATE INDEX idx_transactions_to_wallet ON transactions(to_wallet_id);
CREATE INDEX idx_transactions_hash ON transactions(transaction_hash);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_network ON transactions(network);
CREATE INDEX idx_transactions_created_at ON transactions(created_at DESC);

CREATE INDEX idx_smart_contracts_user_id ON smart_contracts(user_id);
CREATE INDEX idx_smart_contracts_address ON smart_contracts(contract_address);
CREATE INDEX idx_smart_contracts_network ON smart_contracts(network);
CREATE INDEX idx_smart_contracts_status ON smart_contracts(status);

CREATE INDEX idx_contract_interactions_contract_id ON contract_interactions(contract_id);
CREATE INDEX idx_contract_interactions_user_id ON contract_interactions(user_id);

CREATE INDEX idx_blocks_network ON blocks(network);
CREATE INDEX idx_blocks_number ON blocks(block_number DESC);
CREATE INDEX idx_blocks_hash ON blocks(block_hash);

CREATE INDEX idx_tokens_network ON tokens(network);
CREATE INDEX idx_tokens_address ON tokens(contract_address);

CREATE INDEX idx_token_balances_wallet ON token_balances(wallet_id);
CREATE INDEX idx_token_balances_token ON token_balances(token_id);

CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key ON api_keys(key);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- Insert default admin user (password: admin123)
INSERT INTO users (email, username, hashed_password, full_name, is_admin) VALUES
('admin@itechsmart.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvXqO', 'Admin User', TRUE);

-- Insert default network configurations
INSERT INTO network_configs (network, rpc_url, chain_id, explorer_url, is_testnet) VALUES
('ethereum', 'https://mainnet.infura.io/v3/YOUR_INFURA_KEY', 1, 'https://etherscan.io', FALSE),
('polygon', 'https://polygon-rpc.com', 137, 'https://polygonscan.com', FALSE),
('bitcoin', 'https://bitcoin.example.com', NULL, 'https://blockchain.info', FALSE),
('binance', 'https://bsc-dataseed.binance.org', 56, 'https://bscscan.com', FALSE);

-- Insert sample wallets
INSERT INTO wallets (user_id, name, address, network, wallet_type, balance) VALUES
(1, 'Main Ethereum Wallet', '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb', 'ethereum', 'hot', 12.5),
(1, 'Polygon Trading', '0x8ba1f109551bD432803012645Ac136ddd64DBA72', 'polygon', 'hot', 450.8),
(1, 'Bitcoin Cold Storage', '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 'bitcoin', 'cold', 0.5);

-- Insert sample transactions
INSERT INTO transactions (user_id, from_wallet_id, to_wallet_id, from_address, to_address, network, amount, fee, transaction_hash, block_number, status, confirmations, created_at, confirmed_at) VALUES
(1, 1, NULL, '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb', '0x8ba1f109551bD432803012645Ac136ddd64DBA72', 'ethereum', 1.5, 0.002, '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef', 18500000, 'confirmed', 12, NOW() - INTERVAL '5 hours', NOW() - INTERVAL '4 hours 55 minutes'),
(1, 2, NULL, '0x8ba1f109551bD432803012645Ac136ddd64DBA72', '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb', 'polygon', 0.8, 0.0005, '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890', 50123456, 'confirmed', 25, NOW() - INTERVAL '6 hours', NOW() - INTERVAL '5 hours 57 minutes'),
(1, 3, NULL, '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', '3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy', 'bitcoin', 0.05, 0.0001, 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh', NULL, 'pending', 0, NOW() - INTERVAL '1 hour', NULL);

-- Insert sample smart contracts
INSERT INTO smart_contracts (user_id, name, description, network, contract_address, status, is_verified, created_at, deployed_at) VALUES
(1, 'ERC20 Token Contract', 'Standard ERC20 token implementation', 'ethereum', '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb', 'deployed', TRUE, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days' + INTERVAL '1 hour 30 minutes'),
(1, 'NFT Marketplace', 'Decentralized NFT marketplace contract', 'polygon', '0x8ba1f109551bD432803012645Ac136ddd64DBA72', 'deployed', FALSE, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days' + INTERVAL '1 hour 45 minutes'),
(1, 'Staking Contract', 'Token staking and rewards distribution', 'ethereum', NULL, 'draft', FALSE, NOW() - INTERVAL '1 day', NULL);

-- Insert sample blocks
INSERT INTO blocks (network, block_number, block_hash, parent_hash, timestamp, miner, transaction_count, gas_used, gas_limit) VALUES
('ethereum', 18500000, '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef', '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890', NOW() - INTERVAL '2 minutes', '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb', 156, 12500000, 30000000),
('ethereum', 18499999, '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890', '0x567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234', NOW() - INTERVAL '4 minutes', '0x8ba1f109551bD432803012645Ac136ddd64DBA72', 142, 11800000, 30000000),
('ethereum', 18499998, '0x567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234', '0x234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef12', NOW() - INTERVAL '6 minutes', '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb', 168, 13200000, 30000000);

-- Insert sample tokens
INSERT INTO tokens (network, contract_address, name, symbol, decimals, token_type, is_verified) VALUES
('ethereum', '0xdAC17F958D2ee523a2206206994597C13D831ec7', 'Tether USD', 'USDT', 6, 'ERC20', TRUE),
('ethereum', '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'USD Coin', 'USDC', 6, 'ERC20', TRUE),
('polygon', '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174', 'USD Coin (PoS)', 'USDC', 6, 'ERC20', TRUE);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wallets_updated_at BEFORE UPDATE ON wallets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_network_configs_updated_at BEFORE UPDATE ON network_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ledger_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ledger_user;