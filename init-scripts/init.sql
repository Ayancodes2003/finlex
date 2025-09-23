-- Create Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount DECIMAL(15, 2) NOT NULL,
    date TIMESTAMP NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    metadata JSONB
);

-- Create Policies table
CREATE TABLE IF NOT EXISTS policies (
    id UUID PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    jurisdiction VARCHAR(50),
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Violations table
CREATE TABLE IF NOT EXISTS violations (
    id UUID PRIMARY KEY,
    transaction_id UUID REFERENCES transactions(id),
    policy_id UUID REFERENCES policies(id),
    risk_level VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Reports table
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO users (username, email, role) VALUES 
    ('admin', 'admin@finlex.com', 'admin'),
    ('analyst', 'analyst@finlex.com', 'analyst');