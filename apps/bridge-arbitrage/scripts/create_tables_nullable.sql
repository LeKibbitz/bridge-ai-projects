-- Drop existing tables if they exist
DROP TABLE IF EXISTS rnc_articles CASCADE;
DROP TABLE IF EXISTS code_laws CASCADE;

-- Create new tables with nullable fields
CREATE TABLE rnc_articles (
    id SERIAL PRIMARY KEY,
    title_number TEXT NULL,
    title_name TEXT NULL,
    chapter_number TEXT NULL,
    chapter_name TEXT NULL,
    section_number TEXT NULL,
    section_name TEXT NULL,
    article_number TEXT NULL,
    article_name TEXT NULL,
    content TEXT NULL,
    hypertexte_link TEXT NULL,
    created_by TEXT NOT NULL DEFAULT 'system',
    updated_by TEXT NOT NULL DEFAULT 'system',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_article UNIQUE (title_number, chapter_number, section_number, article_number)
);

CREATE TABLE code_laws (
    id SERIAL PRIMARY KEY,
    title_number TEXT NULL,
    title_name TEXT NULL,
    chapter_number TEXT NULL,
    chapter_name TEXT NULL,
    section_number TEXT NULL,
    section_name TEXT NULL,
    article_number TEXT NULL,
    article_name TEXT NULL,
    content TEXT NULL,
    hypertexte_link TEXT NULL,
    created_by TEXT NOT NULL DEFAULT 'system',
    updated_by TEXT NOT NULL DEFAULT 'system',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_code_law UNIQUE (title_number, chapter_number, section_number, article_number)
);

-- Create indexes for better query performance
CREATE INDEX idx_rnc_articles_title ON rnc_articles(title_number);
CREATE INDEX idx_rnc_articles_chapter ON rnc_articles(chapter_number);
CREATE INDEX idx_rnc_articles_section ON rnc_articles(section_number);
CREATE INDEX idx_rnc_articles_article ON rnc_articles(article_number);
CREATE INDEX idx_code_laws_title ON code_laws(title_number);
CREATE INDEX idx_code_laws_chapter ON code_laws(chapter_number);
CREATE INDEX idx_code_laws_section ON code_laws(section_number);
CREATE INDEX idx_code_laws_article ON code_laws(article_number);
