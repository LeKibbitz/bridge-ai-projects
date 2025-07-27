-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255),
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  bridge_license_number VARCHAR(50) UNIQUE,
  federation_id VARCHAR(50), -- Reference to bridge federation
  language_preference VARCHAR(20) DEFAULT 'en',
  is_admin BOOLEAN DEFAULT FALSE,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create federations table
CREATE TABLE IF NOT EXISTS federations (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  country VARCHAR(100) NOT NULL,
  language VARCHAR(50) NOT NULL,
  script VARCHAR(50), -- e.g., 'latin', 'cyrillic', 'hanzi'
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create user roles table
CREATE TABLE IF NOT EXISTS user_roles (
  user_id UUID REFERENCES users(id),
  role VARCHAR(50) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, role)
);

-- Create user session table
CREATE TABLE IF NOT EXISTS user_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  token VARCHAR(255) UNIQUE NOT NULL,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_license ON users(bridge_license_number);
CREATE INDEX idx_users_federation ON users(federation_id);
CREATE INDEX idx_sessions_token ON user_sessions(token);
CREATE INDEX idx_sessions_user ON user_sessions(user_id);

-- Insert initial federation data
INSERT INTO federations (id, name, country, language, script)
VALUES
  ('FBS', 'Fédération Suisse de Bridge', 'Switzerland', 'fr', 'latin'),
  ('WBF', 'World Bridge Federation', 'International', 'en', 'latin'),
  ('FRA', 'Fédération Française de Bridge', 'France', 'fr', 'latin'),
  ('USA', 'American Contract Bridge League', 'USA', 'en', 'latin');
