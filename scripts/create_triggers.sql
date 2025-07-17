-- Fonction pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers pour updated_at
CREATE TRIGGER trg_set_updated_at_players
BEFORE UPDATE ON players
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_set_updated_at_roles
BEFORE UPDATE ON roles
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_set_updated_at_functions
BEFORE UPDATE ON functions
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_set_updated_at_agrements
BEFORE UPDATE ON agrements
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_set_updated_at_player_roles
BEFORE UPDATE ON player_roles
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_set_updated_at_player_functions
BEFORE UPDATE ON player_functions
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_set_updated_at_player_agrements
BEFORE UPDATE ON player_agrements
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- Fonction pour soft delete en cascade
CREATE OR REPLACE FUNCTION cascade_soft_delete_player()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.is_deleted = TRUE THEN
    UPDATE player_roles SET is_deleted = TRUE WHERE licence_number = NEW.licence_number;
    UPDATE player_functions SET is_deleted = TRUE WHERE licence_number = NEW.licence_number;
    UPDATE player_agrements SET is_deleted = TRUE WHERE licence_number = NEW.licence_number;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cascade_soft_delete_player
AFTER UPDATE OF is_deleted ON players
FOR EACH ROW
EXECUTE FUNCTION cascade_soft_delete_player(); 