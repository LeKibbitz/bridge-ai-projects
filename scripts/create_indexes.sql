-- Index sur les clés étrangères et champs importants
CREATE INDEX idx_players_club_code ON players(club_code);
CREATE INDEX idx_players_is_deleted ON players(is_deleted);
CREATE INDEX idx_players_last_paid_season ON players(last_paid_season);
CREATE INDEX idx_players_member_type ON players(member_type);

CREATE INDEX idx_player_roles_licence_number ON player_roles(licence_number);
CREATE INDEX idx_player_roles_role_id ON player_roles(role_id);
CREATE INDEX idx_player_roles_is_deleted ON player_roles(is_deleted);

CREATE INDEX idx_player_functions_licence_number ON player_functions(licence_number);
CREATE INDEX idx_player_functions_function_id ON player_functions(function_id);
CREATE INDEX idx_player_functions_is_deleted ON player_functions(is_deleted);

CREATE INDEX idx_player_agrements_licence_number ON player_agrements(licence_number);
CREATE INDEX idx_player_agrements_agrement_id ON player_agrements(agrement_id);
CREATE INDEX idx_player_agrements_is_deleted ON player_agrements(is_deleted);

CREATE INDEX idx_roles_is_deleted ON roles(is_deleted);
CREATE INDEX idx_functions_is_deleted ON functions(is_deleted);
CREATE INDEX idx_agrements_is_deleted ON agrements(is_deleted); 