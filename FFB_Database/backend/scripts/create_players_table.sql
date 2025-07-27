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