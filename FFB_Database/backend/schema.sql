-- Table des clubs
CREATE TABLE clubs (
    club_code VARCHAR(16) PRIMARY KEY,
    club_name VARCHAR(128) NOT NULL,
    committee VARCHAR(128) NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Table des joueurs
CREATE TABLE players (
    licence_number VARCHAR(16) PRIMARY KEY,
    member_type VARCHAR(32) NOT NULL, -- 'Membre' ou 'Sympathisant'
    last_name VARCHAR(64) NOT NULL,
    first_name VARCHAR(64) NOT NULL,
    birthdate DATE NOT NULL,
    category VARCHAR(32),
    club_code VARCHAR(16) REFERENCES clubs(club_code),
    IV VARCHAR(8),
    IC VARCHAR(8),
    last_paid_season VARCHAR(16),
    alert VARCHAR(128),
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Table des rôles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(64),
    updated_by VARCHAR(64),
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Table des fonctions
CREATE TABLE functions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(64),
    updated_by VARCHAR(64),
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Table des agréments
CREATE TABLE agrements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(64),
    updated_by VARCHAR(64),
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Table de jonction joueurs <-> rôles
CREATE TABLE player_roles (
    id SERIAL PRIMARY KEY,
    licence_number VARCHAR(16) REFERENCES players(licence_number),
    role_id INTEGER REFERENCES roles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(64),
    updated_by VARCHAR(64),
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Table de jonction joueurs <-> fonctions
CREATE TABLE player_functions (
    id SERIAL PRIMARY KEY,
    licence_number VARCHAR(16) REFERENCES players(licence_number),
    function_id INTEGER REFERENCES functions(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(64),
    updated_by VARCHAR(64),
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Table de jonction joueurs <-> agréments
CREATE TABLE player_agrements (
    id SERIAL PRIMARY KEY,
    licence_number VARCHAR(16) REFERENCES players(licence_number),
    agrement_id INTEGER REFERENCES agrements(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(64),
    updated_by VARCHAR(64),
    is_deleted BOOLEAN DEFAULT FALSE
); 