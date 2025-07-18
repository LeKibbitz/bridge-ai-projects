-- Création de la table des clubs (entités)
CREATE TABLE IF NOT EXISTS entites (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    adresse TEXT,
    code_postal VARCHAR(10),
    ville VARCHAR(255),
    telephone VARCHAR(20),
    email VARCHAR(255),
    region VARCHAR(100) NOT NULL,
    departement VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(id)
);

-- Création de la table des rôles
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(nom)
);

-- Création de la table de jointure entre joueurs et rôles
CREATE TABLE IF NOT EXISTS licensee_roles (
    licensee_id INTEGER REFERENCES licensees(id),
    role_id INTEGER REFERENCES roles(id),
    PRIMARY KEY(licensee_id, role_id)
);

-- Création de la table des joueurs (licenciés)
CREATE TABLE IF NOT EXISTS licensees (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    prenom VARCHAR(255) NOT NULL,
    numero_licence VARCHAR(50) NOT NULL,
    date_naissance DATE,
    email VARCHAR(255),
    telephone VARCHAR(20),
    adresse TEXT,
    code_postal VARCHAR(10),
    ville VARCHAR(255),
    besoin_special BOOLEAN DEFAULT FALSE,
    club_id INTEGER REFERENCES entites(id),
    statut VARCHAR(50) NOT NULL,  -- licencié, sympathisant, bénévole, etc.
    saison VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(id),
    UNIQUE(numero_licence)
);

-- Index pour optimiser les requêtes
CREATE INDEX idx_licensees_nom_prenom ON licensees(nom, prenom);
CREATE INDEX idx_entites_nom ON entites(nom);
CREATE INDEX idx_licensees_statut ON licensees(statut);
CREATE INDEX idx_licensees_saison ON licensees(saison);
CREATE INDEX idx_licensees_club_id ON licensees(club_id); 