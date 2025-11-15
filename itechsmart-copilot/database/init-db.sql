-- iTechSmart Copilot Database Initialization Script
-- PostgreSQL Database Schema

-- Drop existing tables if they exist
DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS usage_statistics CASCADE;
DROP TABLE IF EXISTS api_keys CASCADE;
DROP TABLE IF EXISTS code_snippets CASCADE;
DROP TABLE IF EXISTS knowledge_bases CASCADE;
DROP TABLE IF EXISTS document_chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS prompt_templates CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS ai_models CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;

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

-- Create AI Models table
CREATE TABLE ai_models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    model_id VARCHAR(255) NOT NULL,
    description TEXT,
    max_tokens INTEGER DEFAULT 4096,
    temperature DECIMAL(3, 2) DEFAULT 0.7,
    top_p DECIMAL(3, 2) DEFAULT 1.0,
    frequency_penalty DECIMAL(3, 2) DEFAULT 0.0,
    presence_penalty DECIMAL(3, 2) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    cost_per_1k_tokens DECIMAL(10, 6) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    model_id INTEGER NOT NULL REFERENCES ai_models(id) ON DELETE RESTRICT,
    title VARCHAR(500) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    system_prompt TEXT,
    context_window INTEGER DEFAULT 10,
    total_tokens INTEGER DEFAULT 0,
    total_cost DECIMAL(10, 4) DEFAULT 0.0,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    tokens INTEGER DEFAULT 0,
    cost DECIMAL(10, 4) DEFAULT 0.0,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Prompt Templates table
CREATE TABLE prompt_templates (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template TEXT NOT NULL,
    variables JSONB,
    category VARCHAR(100),
    is_public BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(500),
    file_size INTEGER,
    embedding_id VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Document Chunks table
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding_id VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Knowledge Bases table
CREATE TABLE knowledge_bases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    collection_name VARCHAR(255) UNIQUE NOT NULL,
    document_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Code Snippets table
CREATE TABLE code_snippets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,
    code TEXT NOT NULL,
    language VARCHAR(50) NOT NULL,
    description TEXT,
    tags JSONB,
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create API Keys table
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    key_name VARCHAR(255) NOT NULL,
    encrypted_key TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP
);

-- Create Usage Statistics table
CREATE TABLE usage_statistics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date TIMESTAMP NOT NULL,
    provider VARCHAR(50) NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    total_requests INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_cost DECIMAL(10, 4) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Feedback table
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message_id INTEGER REFERENCES messages(id) ON DELETE CASCADE,
    rating INTEGER,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_model_id ON conversations(model_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

CREATE INDEX idx_prompt_templates_user_id ON prompt_templates(user_id);
CREATE INDEX idx_prompt_templates_category ON prompt_templates(category);
CREATE INDEX idx_prompt_templates_is_public ON prompt_templates(is_public);

CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_document_type ON documents(document_type);

CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);

CREATE INDEX idx_knowledge_bases_user_id ON knowledge_bases(user_id);

CREATE INDEX idx_code_snippets_user_id ON code_snippets(user_id);
CREATE INDEX idx_code_snippets_language ON code_snippets(language);
CREATE INDEX idx_code_snippets_is_favorite ON code_snippets(is_favorite);

CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_provider ON api_keys(provider);

CREATE INDEX idx_usage_statistics_user_id ON usage_statistics(user_id);
CREATE INDEX idx_usage_statistics_date ON usage_statistics(date);

CREATE INDEX idx_feedback_user_id ON feedback(user_id);
CREATE INDEX idx_feedback_message_id ON feedback(message_id);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- Insert default admin user (password: admin123)
INSERT INTO users (email, username, hashed_password, full_name, is_admin) VALUES
('admin@itechsmart.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvXqO', 'Admin User', TRUE);

-- Insert default AI models
INSERT INTO ai_models (name, provider, model_id, description, max_tokens, temperature, cost_per_1k_tokens, is_default) VALUES
('GPT-4', 'openai', 'gpt-4', 'Most capable model, best for complex tasks', 8192, 0.7, 0.03, TRUE),
('GPT-3.5 Turbo', 'openai', 'gpt-3.5-turbo', 'Fast and efficient for most tasks', 4096, 0.7, 0.002, FALSE),
('Claude 2', 'anthropic', 'claude-2', 'Excellent for long-form content and analysis', 100000, 0.7, 0.008, FALSE),
('Gemini Pro', 'google', 'gemini-pro', 'Google''s advanced AI model', 32768, 0.7, 0.00025, FALSE);

-- Insert sample conversations
INSERT INTO conversations (user_id, model_id, title, status, total_tokens, total_cost) VALUES
(1, 1, 'Help with React components', 'active', 2500, 0.15),
(1, 2, 'Python data analysis script', 'active', 3200, 0.22),
(1, 1, 'API documentation review', 'archived', 1800, 0.12);

-- Insert sample messages
INSERT INTO messages (conversation_id, role, content, tokens, cost) VALUES
(1, 'user', 'Can you help me create a React component?', 10, 0.0),
(1, 'assistant', 'Of course! I''d be happy to help you create a React component. What kind of component would you like to build?', 25, 0.001),
(2, 'user', 'I need to analyze a CSV file with pandas', 15, 0.0),
(2, 'assistant', 'I can help you with that! Here''s a basic example of how to analyze a CSV file using pandas...', 50, 0.002);

-- Insert sample prompt templates
INSERT INTO prompt_templates (user_id, name, description, template, category, is_public, usage_count) VALUES
(1, 'Code Review', 'Review code for best practices and improvements', 'Please review the following code and provide suggestions for improvements:\n\n{code}', 'Development', TRUE, 45),
(1, 'Bug Fix Assistant', 'Help identify and fix bugs in code', 'I have a bug in my code. Here''s the error: {error}\n\nCode:\n{code}\n\nPlease help me fix it.', 'Development', TRUE, 32),
(1, 'Documentation Writer', 'Generate documentation for code', 'Generate comprehensive documentation for the following code:\n\n{code}', 'Documentation', FALSE, 28);

-- Insert sample documents
INSERT INTO documents (user_id, title, content, document_type, file_size) VALUES
(1, 'API Documentation v2.0', 'This is the API documentation content...', 'pdf', 2048000),
(1, 'User Guide', 'This is the user guide content...', 'docx', 1024000);

-- Insert sample knowledge bases
INSERT INTO knowledge_bases (user_id, name, description, collection_name, document_count) VALUES
(1, 'Technical Documentation', 'API docs, technical specifications, and guides', 'kb_1_tech_docs', 24),
(1, 'Company Policies', 'HR policies, procedures, and guidelines', 'kb_1_policies', 15);

-- Insert sample code snippets
INSERT INTO code_snippets (user_id, title, code, language, description, is_favorite) VALUES
(1, 'React useState Hook', 'const [count, setCount] = useState(0);', 'javascript', 'Basic useState hook example', TRUE),
(1, 'Python List Comprehension', 'squares = [x**2 for x in range(10)]', 'python', 'Create a list of squares', FALSE);

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

CREATE TRIGGER update_ai_models_updated_at BEFORE UPDATE ON ai_models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prompt_templates_updated_at BEFORE UPDATE ON prompt_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_bases_updated_at BEFORE UPDATE ON knowledge_bases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_code_snippets_updated_at BEFORE UPDATE ON code_snippets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();