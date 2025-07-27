-- Backup existing data
CREATE TABLE IF NOT EXISTS rnc_articles_backup AS SELECT * FROM rnc_articles;
CREATE TABLE IF NOT EXISTS code_laws_backup AS SELECT * FROM code_laws;

-- Drop existing tables
DROP TABLE IF EXISTS rnc_articles CASCADE;
DROP TABLE IF EXISTS code_laws CASCADE;

-- Create temporary tables
CREATE TABLE temp_rnc_articles (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title_number TEXT NULL,
  title_name TEXT NULL,
  chapter_number TEXT NULL,
  chapter_name TEXT NULL,
  section_number TEXT NULL,
  section_name TEXT NULL,
  article_number TEXT NULL,
  article_name TEXT NULL,
  alinea TEXT NULL,
  sub_alinea TEXT NULL,
  sub_sub_alinea TEXT NULL,
  content TEXT NULL,
  hypertexte_link TEXT NULL,
  created_by TEXT NULL,
  updated_by TEXT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT unique_article UNIQUE (
    title_number,
    article_number
  )
) TABLESPACE pg_default;

CREATE TABLE temp_code_laws (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title_number TEXT NULL,
  title_name TEXT NULL,
  chapter_number TEXT NULL,
  chapter_name TEXT NULL,
  article_number TEXT NULL,
  article_name TEXT NULL,
  alinea TEXT NULL,
  sub_alinea TEXT NULL,
  sub_sub_alinea TEXT NULL,
  content TEXT NULL,
  hypertexte_link TEXT NULL,
  created_by TEXT NULL,
  updated_by TEXT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT unique_code_law UNIQUE (
    title_number,
    article_number
  )
) TABLESPACE pg_default;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_temp_code_laws_title ON temp_code_laws USING btree (title_number) TABLESPACE pg_default;
CREATE INDEX IF NOT EXISTS idx_temp_code_laws_article ON temp_code_laws USING btree (article_number) TABLESPACE pg_default;
CREATE INDEX IF NOT EXISTS idx_temp_rnc_articles_title ON temp_rnc_articles USING btree (title_number) TABLESPACE pg_default;
CREATE INDEX IF NOT EXISTS idx_temp_rnc_articles_article ON temp_rnc_articles USING btree (article_number) TABLESPACE pg_default;

-- Create triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_temp_code_laws_updated_at
    BEFORE UPDATE ON temp_code_laws
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_temp_rnc_articles_updated_at
    BEFORE UPDATE ON temp_rnc_articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert backed up data back into the tables
INSERT INTO temp_code_laws 
SELECT uuid_generate_v4() as id, * 
FROM code_laws_backup;

INSERT INTO temp_rnc_articles 
SELECT uuid_generate_v4() as id, * 
FROM rnc_articles_backup;

    EXECUTE FUNCTION update_updated_at_column();

-- Insert backed up data back into the tables
INSERT INTO temp_code_laws SELECT * FROM code_laws_backup;
INSERT INTO temp_rnc_articles SELECT * FROM rnc_articles_backup;

-- Rename tables
ALTER TABLE temp_rnc_articles RENAME TO rnc_articles;
ALTER TABLE temp_code_laws RENAME TO code_laws;

-- Drop backup tables
DROP TABLE IF EXISTS rnc_articles_backup;
DROP TABLE IF EXISTS code_laws_backup;
