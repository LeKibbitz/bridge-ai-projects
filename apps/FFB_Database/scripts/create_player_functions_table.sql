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