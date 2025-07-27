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