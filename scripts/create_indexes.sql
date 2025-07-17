-- Index sur les clés étrangères et champs importants

-- Table joueurs
CREATE INDEX idx_joueurs_club_id ON joueurs(club_id);
CREATE INDEX idx_joueurs_is_deleted ON joueurs(is_deleted);
CREATE INDEX idx_joueurs_licence ON joueurs(licence);

-- Table joueur_roles
CREATE INDEX idx_joueur_roles_joueur_id ON joueur_roles(joueur_id);
CREATE INDEX idx_joueur_roles_role_id ON joueur_roles(role_id);
CREATE INDEX idx_joueur_roles_is_deleted ON joueur_roles(is_deleted);

-- Table joueur_functions
CREATE INDEX idx_joueur_functions_joueur_id ON joueur_functions(joueur_id);
CREATE INDEX idx_joueur_functions_function_id ON joueur_functions(function_id);
CREATE INDEX idx_joueur_functions_is_deleted ON joueur_functions(is_deleted);

-- Table joueur_agrements
CREATE INDEX idx_joueur_agrements_joueur_id ON joueur_agrements(joueur_id);
CREATE INDEX idx_joueur_agrements_agrement_id ON joueur_agrements(agrement_id);
CREATE INDEX idx_joueur_agrements_is_deleted ON joueur_agrements(is_deleted);

-- Table roles
CREATE INDEX idx_roles_is_deleted ON roles(is_deleted);

-- Table functions
CREATE INDEX idx_functions_is_deleted ON functions(is_deleted);

-- Table agrements
CREATE INDEX idx_agrements_is_deleted ON agrements(is_deleted);