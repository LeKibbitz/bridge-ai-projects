-- Create backup tables
CREATE TABLE IF NOT EXISTS rnc_articles_backup AS SELECT * FROM rnc_articles;
CREATE TABLE IF NOT EXISTS code_laws_backup AS SELECT * FROM code_laws;

-- Add timestamps to backup tables
ALTER TABLE rnc_articles_backup ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE rnc_articles_backup ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE code_laws_backup ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE code_laws_backup ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- Create triggers for backup tables

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_rnc_articles_backup_updated_at
    BEFORE UPDATE ON rnc_articles_backup
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_code_laws_backup_updated_at
    BEFORE UPDATE ON code_laws_backup
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
