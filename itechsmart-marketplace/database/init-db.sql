-- iTechSmart Marketplace Database Schema

-- Drop existing tables if they exist
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS app_reports CASCADE;
DROP TABLE IF EXISTS wishlists CASCADE;
DROP TABLE IF EXISTS app_analytics CASCADE;
DROP TABLE IF EXISTS payment_methods CASCADE;
DROP TABLE IF EXISTS purchases CASCADE;
DROP TABLE IF EXISTS review_responses CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS app_versions CASCADE;
DROP TABLE IF EXISTS apps CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS developer_profiles CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create enum types
CREATE TYPE user_role AS ENUM ('user', 'developer', 'admin');
CREATE TYPE app_status AS ENUM ('draft', 'pending_review', 'approved', 'rejected', 'suspended');
CREATE TYPE purchase_status AS ENUM ('pending', 'completed', 'failed', 'refunded');
CREATE TYPE review_status AS ENUM ('pending', 'approved', 'rejected');

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'user' NOT NULL,
    avatar_url VARCHAR(500),
    bio TEXT,
    company VARCHAR(255),
    website VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Developer profiles table
CREATE TABLE developer_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_name VARCHAR(255),
    tax_id VARCHAR(100),
    address TEXT,
    phone VARCHAR(50),
    support_email VARCHAR(255),
    support_url VARCHAR(500),
    total_revenue DECIMAL(12, 2) DEFAULT 0.00,
    total_downloads INTEGER DEFAULT 0,
    average_rating DECIMAL(3, 2) DEFAULT 0.00,
    is_verified BOOLEAN DEFAULT FALSE,
    stripe_account_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    parent_id INTEGER REFERENCES categories(id),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Apps table
CREATE TABLE apps (
    id SERIAL PRIMARY KEY,
    developer_id INTEGER NOT NULL REFERENCES developer_profiles(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    tagline VARCHAR(500),
    description TEXT NOT NULL,
    long_description TEXT,
    icon_url VARCHAR(500),
    banner_url VARCHAR(500),
    screenshots JSONB,
    video_url VARCHAR(500),
    price DECIMAL(10, 2) DEFAULT 0.00,
    is_free BOOLEAN DEFAULT TRUE,
    status app_status DEFAULT 'draft' NOT NULL,
    version VARCHAR(50) DEFAULT '1.0.0',
    size_mb DECIMAL(10, 2),
    min_requirements JSONB,
    features JSONB,
    tags JSONB,
    total_downloads INTEGER DEFAULT 0,
    total_revenue DECIMAL(12, 2) DEFAULT 0.00,
    average_rating DECIMAL(3, 2) DEFAULT 0.00,
    total_reviews INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    featured_order INTEGER,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- App versions table
CREATE TABLE app_versions (
    id SERIAL PRIMARY KEY,
    app_id INTEGER NOT NULL REFERENCES apps(id) ON DELETE CASCADE,
    version VARCHAR(50) NOT NULL,
    release_notes TEXT,
    download_url VARCHAR(500),
    size_mb DECIMAL(10, 2),
    min_requirements JSONB,
    is_current BOOLEAN DEFAULT FALSE,
    downloads INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reviews table
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    app_id INTEGER NOT NULL REFERENCES apps(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT,
    status review_status DEFAULT 'pending' NOT NULL,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(app_id, user_id)
);

-- Review responses table
CREATE TABLE review_responses (
    id SERIAL PRIMARY KEY,
    review_id INTEGER NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    developer_id INTEGER NOT NULL REFERENCES developer_profiles(id) ON DELETE CASCADE,
    response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Purchases table
CREATE TABLE purchases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    app_id INTEGER NOT NULL REFERENCES apps(id) ON DELETE CASCADE,
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    status purchase_status DEFAULT 'pending' NOT NULL,
    payment_method VARCHAR(50),
    stripe_payment_intent_id VARCHAR(255),
    refund_amount DECIMAL(10, 2),
    refund_reason TEXT,
    refunded_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Payment methods table
CREATE TABLE payment_methods (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_payment_method_id VARCHAR(255) UNIQUE NOT NULL,
    type VARCHAR(50),
    last4 VARCHAR(4),
    brand VARCHAR(50),
    exp_month INTEGER,
    exp_year INTEGER,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- App analytics table
CREATE TABLE app_analytics (
    id SERIAL PRIMARY KEY,
    app_id INTEGER NOT NULL REFERENCES apps(id) ON DELETE CASCADE,
    date TIMESTAMP NOT NULL,
    views INTEGER DEFAULT 0,
    downloads INTEGER DEFAULT 0,
    purchases INTEGER DEFAULT 0,
    revenue DECIMAL(10, 2) DEFAULT 0.00,
    unique_visitors INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Wishlists table
CREATE TABLE wishlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    app_id INTEGER NOT NULL REFERENCES apps(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, app_id)
);

-- App reports table
CREATE TABLE app_reports (
    id SERIAL PRIMARY KEY,
    app_id INTEGER NOT NULL REFERENCES apps(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reason VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    admin_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Audit logs table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    details JSONB,
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

CREATE INDEX idx_developer_profiles_user_id ON developer_profiles(user_id);

CREATE INDEX idx_categories_slug ON categories(slug);
CREATE INDEX idx_categories_parent_id ON categories(parent_id);

CREATE INDEX idx_apps_developer_id ON apps(developer_id);
CREATE INDEX idx_apps_category_id ON apps(category_id);
CREATE INDEX idx_apps_slug ON apps(slug);
CREATE INDEX idx_apps_status ON apps(status);
CREATE INDEX idx_apps_is_featured ON apps(is_featured);
CREATE INDEX idx_apps_published_at ON apps(published_at);

CREATE INDEX idx_app_versions_app_id ON app_versions(app_id);
CREATE INDEX idx_app_versions_is_current ON app_versions(is_current);

CREATE INDEX idx_reviews_app_id ON reviews(app_id);
CREATE INDEX idx_reviews_user_id ON reviews(user_id);
CREATE INDEX idx_reviews_status ON reviews(status);

CREATE INDEX idx_review_responses_review_id ON review_responses(review_id);

CREATE INDEX idx_purchases_user_id ON purchases(user_id);
CREATE INDEX idx_purchases_app_id ON purchases(app_id);
CREATE INDEX idx_purchases_transaction_id ON purchases(transaction_id);
CREATE INDEX idx_purchases_status ON purchases(status);

CREATE INDEX idx_payment_methods_user_id ON payment_methods(user_id);

CREATE INDEX idx_app_analytics_app_id ON app_analytics(app_id);
CREATE INDEX idx_app_analytics_date ON app_analytics(date);

CREATE INDEX idx_wishlists_user_id ON wishlists(user_id);
CREATE INDEX idx_wishlists_app_id ON wishlists(app_id);

CREATE INDEX idx_app_reports_app_id ON app_reports(app_id);
CREATE INDEX idx_app_reports_status ON app_reports(status);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Insert sample data

-- Insert categories
INSERT INTO categories (name, slug, description, icon, display_order) VALUES
('Data Integration', 'data-integration', 'Connect and sync data across platforms', '📊', 1),
('Security', 'security', 'Protect your infrastructure and data', '🛡️', 2),
('Analytics', 'analytics', 'Business intelligence and data visualization', '📈', 3),
('API Management', 'api-management', 'Manage and secure your APIs', '🔌', 4),
('Automation', 'automation', 'Automate workflows and processes', '⚙️', 5),
('Communication', 'communication', 'Messaging and notification services', '📢', 6),
('AI & ML', 'ai-ml', 'Artificial intelligence and machine learning', '🤖', 7);

-- Insert admin user
INSERT INTO users (email, username, full_name, hashed_password, role, is_active, is_verified) VALUES
('admin@itechsmart.com', 'admin', 'Admin User', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEkKe2', 'admin', TRUE, TRUE);

-- Insert developer user
INSERT INTO users (email, username, full_name, hashed_password, role, is_active, is_verified) VALUES
('developer@itechsmart.com', 'developer', 'Developer User', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEkKe2', 'developer', TRUE, TRUE);

-- Insert developer profile
INSERT INTO developer_profiles (user_id, company_name, support_email, support_url, is_verified) VALUES
(2, 'iTechSmart Inc.', 'support@itechsmart.com', 'https://support.itechsmart.com', TRUE);

-- Insert sample apps
INSERT INTO apps (developer_id, category_id, name, slug, tagline, description, long_description, icon_url, price, is_free, status, version, size_mb, features, tags, total_downloads, total_revenue, average_rating, total_reviews, is_featured, published_at) VALUES
(1, 1, 'DataFlow Pro', 'dataflow-pro', 'Enterprise Data Integration Platform', 'Connect, transform, and sync data across your entire organization', 'DataFlow Pro is a comprehensive data integration platform designed for enterprise needs. With support for 100+ data sources including databases, cloud services, APIs, and file systems, DataFlow Pro makes it easy to connect all your data sources in one place.', '📊', 99.99, FALSE, 'approved', '2.5.0', 125.5, '["100+ data source connectors", "Real-time data streaming", "Advanced ETL transformations", "Data quality validation"]', '["data", "integration", "etl"]', 15420, 154200.00, 4.8, 342, TRUE, CURRENT_TIMESTAMP),
(1, 2, 'Shield Security', 'shield-security', 'Advanced Security & Compliance', 'Protect your infrastructure with real-time threat detection', 'Shield Security provides comprehensive security monitoring and compliance management for enterprise environments.', '🛡️', 149.99, FALSE, 'approved', '3.2.1', 98.3, '["Real-time threat detection", "Compliance frameworks", "Vulnerability scanning", "Incident management"]', '["security", "compliance"]', 12850, 192750.00, 4.9, 289, TRUE, CURRENT_TIMESTAMP),
(1, 3, 'Pulse Analytics', 'pulse-analytics', 'Business Intelligence & Analytics', 'Transform data into actionable insights', 'Pulse Analytics is a powerful BI platform with advanced visualization and reporting capabilities.', '📈', 79.99, FALSE, 'approved', '1.8.0', 156.2, '["Interactive dashboards", "Custom reports", "Data visualization", "SQL query builder"]', '["analytics", "bi"]', 18920, 151360.00, 4.7, 456, TRUE, CURRENT_TIMESTAMP),
(1, 4, 'Connect API Gateway', 'connect-api', 'API Management Platform', 'Manage, secure, and scale your APIs', 'Connect provides enterprise-grade API management with security, analytics, and developer portal.', '🔌', 0, TRUE, 'approved', '2.0.0', 87.4, '["API gateway", "Rate limiting", "Analytics", "Developer portal"]', '["api", "gateway"]', 25340, 0.00, 4.6, 567, FALSE, CURRENT_TIMESTAMP);

-- Insert sample reviews
INSERT INTO reviews (app_id, user_id, rating, title, comment, status, is_verified_purchase) VALUES
(1, 1, 5, 'Excellent data integration tool!', 'This has transformed how we handle data across our organization. The connectors are robust and the UI is intuitive.', 'approved', TRUE),
(1, 1, 4, 'Great features, minor learning curve', 'Very powerful platform with lots of features. Took a bit to learn but worth it.', 'approved', TRUE),
(2, 1, 5, 'Best security platform', 'Comprehensive security monitoring with excellent threat detection capabilities.', 'approved', TRUE);

-- Create views for common queries
CREATE VIEW app_stats AS
SELECT 
    a.id,
    a.name,
    a.total_downloads,
    a.total_revenue,
    a.average_rating,
    a.total_reviews,
    d.company_name as developer_name,
    c.name as category_name
FROM apps a
JOIN developer_profiles d ON a.developer_id = d.id
JOIN categories c ON a.category_id = c.id;

CREATE VIEW developer_stats AS
SELECT 
    d.id,
    d.company_name,
    d.total_revenue,
    d.total_downloads,
    d.average_rating,
    COUNT(a.id) as total_apps,
    u.email as contact_email
FROM developer_profiles d
JOIN users u ON d.user_id = u.id
LEFT JOIN apps a ON d.id = a.developer_id
GROUP BY d.id, d.company_name, d.total_revenue, d.total_downloads, d.average_rating, u.email;

-- Create trigger to update app rating when review is added/updated
CREATE OR REPLACE FUNCTION update_app_rating()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE apps
    SET 
        average_rating = (
            SELECT COALESCE(AVG(rating), 0)
            FROM reviews
            WHERE app_id = NEW.app_id AND status = 'approved'
        ),
        total_reviews = (
            SELECT COUNT(*)
            FROM reviews
            WHERE app_id = NEW.app_id AND status = 'approved'
        )
    WHERE id = NEW.app_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_app_rating
AFTER INSERT OR UPDATE ON reviews
FOR EACH ROW
EXECUTE FUNCTION update_app_rating();

-- Create trigger to update developer stats
CREATE OR REPLACE FUNCTION update_developer_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE developer_profiles
    SET 
        total_downloads = (
            SELECT COALESCE(SUM(total_downloads), 0)
            FROM apps
            WHERE developer_id = NEW.developer_id
        ),
        total_revenue = (
            SELECT COALESCE(SUM(total_revenue), 0)
            FROM apps
            WHERE developer_id = NEW.developer_id
        ),
        average_rating = (
            SELECT COALESCE(AVG(average_rating), 0)
            FROM apps
            WHERE developer_id = NEW.developer_id AND average_rating > 0
        )
    WHERE id = NEW.developer_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_developer_stats
AFTER INSERT OR UPDATE ON apps
FOR EACH ROW
EXECUTE FUNCTION update_developer_stats();