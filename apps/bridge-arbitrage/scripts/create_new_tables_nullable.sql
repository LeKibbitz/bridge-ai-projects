-- Drop existing tables if they exist
DROP TABLE IF EXISTS rnc_articles CASCADE;
DROP TABLE IF EXISTS code_laws CASCADE;

-- Create new tables with updated structure
CREATE TABLE rnc_articles (
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

CREATE TABLE code_laws (
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

-- Create indexes for better query performance
CREATE INDEX idx_rnc_articles_title ON rnc_articles(title_number);
CREATE INDEX idx_rnc_articles_chapter ON rnc_articles(chapter_number);
CREATE INDEX idx_rnc_articles_section ON rnc_articles(section_number);
CREATE INDEX idx_rnc_articles_article ON rnc_articles(article_number);
CREATE INDEX idx_code_laws_title ON code_laws(title_number);
CREATE INDEX idx_code_laws_chapter ON code_laws(chapter_number);
CREATE INDEX idx_code_laws_article ON code_laws(article_number);

-- Create triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_rnc_articles_updated_at
    BEFORE UPDATE ON rnc_articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_code_laws_updated_at
    BEFORE UPDATE ON code_laws
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
