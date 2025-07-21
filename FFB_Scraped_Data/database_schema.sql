-- FFB Database Schema
-- Generated on: 2025-07-21 03:45:46
-- Based on analysis of entities: 1 (FFB), 2 (Zone), 18 (Ligue), 38 (Comité), 850 (Club)

-- Entity Types
CREATE TYPE entity_type AS ENUM ('FFB', 'Zone', 'Ligue', 'Comité', 'Club');
-- Status Types
CREATE TYPE entity_status AS ENUM ('Actif', 'Inactif', 'En attente');
-- Member Types
CREATE TYPE member_type AS ENUM ('Payé', 'Non payé', 'En attente');

-- Table: entities
CREATE TABLE entities (
    nom_entite VARCHAR(255) -- Nom de l'entité,
    numero_entite VARCHAR(50) -- Numéro d'entité,
    type_entite VARCHAR(100) -- Type,
    checkbox_1 BOOLEAN -- Checkbox 1,
    checkbox_2 BOOLEAN -- Checkbox 2,
    checkbox_3 BOOLEAN -- Checkbox 3,
    checkbox_4 BOOLEAN -- Checkbox 4,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement,
    entite_subordination VARCHAR(255) -- Entité de subordination,
    entite_regroupement VARCHAR(255) -- Entité de regroupement,
    subordination VARCHAR(255) -- Subordination
);

-- Table: entity_coordinates
CREATE TABLE entity_coordinates (
    email VARCHAR(255) -- E-mail,
    site_internet VARCHAR(255) -- Site internet,
    telephone_principal VARCHAR(50) -- Téléphone principal,
    telephone_secondaire VARCHAR(50) -- Téléphone secondaire,
    email_competitions VARCHAR(255) -- E-mail des Compétitions,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Table: entity_notifications
CREATE TABLE entity_notifications (
    email_principal VARCHAR(255) -- E-mail principal,
    email_secondaire VARCHAR(255) -- E-mail secondaire,
    commentaires TEXT -- Commentaires,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Table: entity_complementary_info
CREATE TABLE entity_complementary_info (
    info_checkbox_1 BOOLEAN -- Info checkbox 1,
    info_checkbox_2 BOOLEAN -- Info checkbox 2,
    info_checkbox_3 BOOLEAN -- Info checkbox 3,
    nombre_tables INTEGER -- Nombre de tables,
    organisme_tutelle VARCHAR(255) -- Organisme de tutelle,
    horaires_ouverture TEXT -- Horaires d'ouverture,
    dates_fermeture TEXT -- Dates de fermeture,
    saisonnier VARCHAR(100) -- Saisonnier,
    plus_club TEXT -- Les plus du club,
    info_texte_1 TEXT -- Info texte 1,
    info_texte_2 TEXT -- Info texte 2,
    info_texte_3 TEXT -- Info texte 3,
    info_texte_4 TEXT -- Info texte 4,
    info_texte_5 TEXT -- Info texte 5,
    info_texte_6 TEXT -- Info texte 6,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement,
    participe_seances_decouverte BOOLEAN -- Participe aux 5 séances Découverte
);

-- Table: entity_photos
CREATE TABLE entity_photos (
    photo_texte TEXT -- Photo texte,
    photo_url VARCHAR(500) -- Photo URL,
    photo_recommendations TEXT -- Photo recommendations,
    photo_consigne TEXT -- Photo consigne,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Table: entity_addresses_jeu
CREATE TABLE entity_addresses_jeu (
    address_line_1 VARCHAR(255) -- Address Line 1,
    address_line_2 VARCHAR(255) -- Address Line 2,
    address_line_3 VARCHAR(255) -- Address Line 3,
    zipcode VARCHAR(50) -- Zipcode,
    city VARCHAR(255) -- City,
    country VARCHAR(255) -- Country,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Table: entity_addresses_courrier
CREATE TABLE entity_addresses_courrier (
    courrier_opg_option VARCHAR(100) -- Courrier OPG option,
    courrier_1 VARCHAR(255) -- Courrier 1,
    courrier_2 VARCHAR(255) -- Courrier 2,
    courrier_3 VARCHAR(255) -- Courrier 3,
    courrier_4 VARCHAR(255) -- Courrier 4,
    courrier_5 VARCHAR(255) -- Courrier 5,
    courrier_6 VARCHAR(255) -- Courrier 6,
    country VARCHAR(255) -- Country,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Table: entity_addresses_facturation
CREATE TABLE entity_addresses_facturation (
    facturation_opg_option VARCHAR(100) -- Facturation OPG option,
    facturation_1 VARCHAR(255) -- Facturation 1,
    facturation_2 VARCHAR(255) -- Facturation 2,
    facturation_3 VARCHAR(255) -- Facturation 3,
    facturation_4 VARCHAR(255) -- Facturation 4,
    facturation_5 VARCHAR(255) -- Facturation 5,
    facturation_6 VARCHAR(255) -- Facturation 6,
    country VARCHAR(255) -- Country,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Table: entity_actors
CREATE TABLE entity_actors (
    nom VARCHAR(255) -- Nom,
    prenom VARCHAR(255) -- Prénom,
    role VARCHAR(255) -- Rôle,
    statut VARCHAR(50) -- Statut,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Table: entity_actors_history
CREATE TABLE entity_actors_history (
    nom VARCHAR(255) -- Nom,
    prenom VARCHAR(255) -- Prénom,
    role VARCHAR(255) -- Rôle,
    statut VARCHAR(50) -- Statut,
    date_fin DATE -- Date de fin,
    page INTEGER -- Page number,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Table: entity_regroupements
CREATE TABLE entity_regroupements (
    entity_id VARCHAR(50) NOT NULL -- FK to entities,
    regroupement_entity_id VARCHAR(50) NOT NULL -- FK to entities,
    regroupement_type VARCHAR(100) NOT NULL -- Type of relationship
);

-- Table: entity_roles
CREATE TABLE entity_roles (
    role_name VARCHAR(255) -- Nom du rôle,
    role_description TEXT -- Description du rôle,
    role_type VARCHAR(100) -- Type de rôle,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Table: billing_rates
CREATE TABLE billing_rates (
    part_ffb DECIMAL(10,2) -- Part FFB,
    part_comite DECIMAL(10,2) -- Part comité,
    total DECIMAL(10,2) -- Total,
    rate_type VARCHAR(100) -- Type de barème,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Table: license_prices
CREATE TABLE license_prices (
    license_type VARCHAR(100) -- Type de licence,
    price DECIMAL(10,2) -- Prix,
    description TEXT -- Description,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Table: ffb_amounts
CREATE TABLE ffb_amounts (
    total DECIMAL(10,2) -- Total,
    amount_type VARCHAR(100) -- Type de montant,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Table: committee_amounts
CREATE TABLE committee_amounts (
    amount_description VARCHAR(255) -- Description,
    amount DECIMAL(10,2) -- Montant,
    due_date DATE -- Date d'échéance,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Table: discovery_sessions
CREATE TABLE discovery_sessions (
    session_name VARCHAR(255) -- Nom de la session,
    session_date DATE -- Date de la session,
    participants INTEGER -- Nombre de participants,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Table: committee_ffb_amounts
CREATE TABLE committee_ffb_amounts (
    titre VARCHAR(255) -- Titre,
    montant DECIMAL(10,2) -- Montant,
    warning TEXT -- Warning,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Table: license_transfers
CREATE TABLE license_transfers (
    transfer_type VARCHAR(100) -- Type de transfert,
    from_entity VARCHAR(50) -- Entité d'origine,
    to_entity VARCHAR(50) -- Entité de destination,
    transfer_date DATE -- Date de transfert,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Table: bridge_schools
CREATE TABLE bridge_schools (
    ecoles_texte TEXT -- Texte des écoles,
    ecoles_logo_url VARCHAR(500) -- URL du logo,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Table: active_teachers
CREATE TABLE active_teachers (
    nom VARCHAR(255) -- Nom,
    prenom VARCHAR(255) -- Prénom,
    agrement VARCHAR(100) -- Agrément,
    validity_date DATE -- Date de validité,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de création,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date de modification,
    created_by VARCHAR(100) -- Créé par,
    updated_by VARCHAR(100) -- Modifié par,
    soft_deleted BOOLEAN DEFAULT FALSE -- Supprimé logiquement
);

-- Indexes
CREATE INDEX idx_entities_type ON entities(type_entite);
CREATE INDEX idx_entities_soft_deleted ON entities(soft_deleted);
CREATE INDEX idx_members_license_number ON members(license_number);
CREATE INDEX idx_members_entity_code ON members(entity_code);
CREATE INDEX idx_members_soft_deleted ON members(soft_deleted);
CREATE INDEX idx_entity_actors_entity_id ON entity_actors(entity_id);
CREATE INDEX idx_entity_actors_statut ON entity_actors(statut);
CREATE INDEX idx_entity_addresses_jeu_entity_id ON entity_addresses_jeu(entity_id);
CREATE INDEX idx_entity_addresses_courrier_entity_id ON entity_addresses_courrier(entity_id);
CREATE INDEX idx_entity_addresses_facturation_entity_id ON entity_addresses_facturation(entity_id);

-- Foreign Key Constraints
ALTER TABLE entity_actors ADD CONSTRAINT fk_entity_actors_entity_id FOREIGN KEY (entity_id) REFERENCES entities(entity_code);
ALTER TABLE entity_coordinates ADD CONSTRAINT fk_entity_coordinates_entity_id FOREIGN KEY (entity_id) REFERENCES entities(entity_code);
ALTER TABLE entity_notifications ADD CONSTRAINT fk_entity_notifications_entity_id FOREIGN KEY (entity_id) REFERENCES entities(entity_code);
ALTER TABLE entity_complementary_info ADD CONSTRAINT fk_entity_complementary_info_entity_id FOREIGN KEY (entity_id) REFERENCES entities(entity_code);
ALTER TABLE entity_photos ADD CONSTRAINT fk_entity_photos_entity_id FOREIGN KEY (entity_id) REFERENCES entities(entity_code);
ALTER TABLE entity_addresses_jeu ADD CONSTRAINT fk_entity_addresses_jeu_entity_id FOREIGN KEY (entity_id) REFERENCES entities(entity_code);
ALTER TABLE entity_addresses_courrier ADD CONSTRAINT fk_entity_addresses_courrier_entity_id FOREIGN KEY (entity_id) REFERENCES entities(entity_code);
ALTER TABLE entity_addresses_facturation ADD CONSTRAINT fk_entity_addresses_facturation_entity_id FOREIGN KEY (entity_id) REFERENCES entities(entity_code);
ALTER TABLE members ADD CONSTRAINT fk_members_entity_code FOREIGN KEY (entity_code) REFERENCES entities(entity_code);

-- Triggers

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_entities_updated_at BEFORE UPDATE ON entities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_entity_coordinates_updated_at BEFORE UPDATE ON entity_coordinates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_entity_notifications_updated_at BEFORE UPDATE ON entity_notifications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_entity_complementary_info_updated_at BEFORE UPDATE ON entity_complementary_info FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_entity_photos_updated_at BEFORE UPDATE ON entity_photos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_entity_addresses_jeu_updated_at BEFORE UPDATE ON entity_addresses_jeu FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_entity_addresses_courrier_updated_at BEFORE UPDATE ON entity_addresses_courrier FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_entity_addresses_facturation_updated_at BEFORE UPDATE ON entity_addresses_facturation FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_entity_actors_updated_at BEFORE UPDATE ON entity_actors FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_entity_actors_history_updated_at BEFORE UPDATE ON entity_actors_history FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_entity_roles_updated_at BEFORE UPDATE ON entity_roles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_billing_rates_updated_at BEFORE UPDATE ON billing_rates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_license_prices_updated_at BEFORE UPDATE ON license_prices FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ffb_amounts_updated_at BEFORE UPDATE ON ffb_amounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_committee_amounts_updated_at BEFORE UPDATE ON committee_amounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_discovery_sessions_updated_at BEFORE UPDATE ON discovery_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_committee_ffb_amounts_updated_at BEFORE UPDATE ON committee_ffb_amounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_license_transfers_updated_at BEFORE UPDATE ON license_transfers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bridge_schools_updated_at BEFORE UPDATE ON bridge_schools FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_active_teachers_updated_at BEFORE UPDATE ON active_teachers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
