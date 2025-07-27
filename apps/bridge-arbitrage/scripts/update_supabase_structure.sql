-- Drop existing tables if they exist
DROP TABLE IF EXISTS rnc_article_relationships;
DROP TABLE IF EXISTS rnc_article_references;
DROP TABLE IF EXISTS rnc_articles;
DROP TABLE IF EXISTS rnc_sections;
DROP TABLE IF EXISTS rnc_chapters;
DROP TABLE IF EXISTS rnc_titles;
DROP TABLE IF EXISTS code_laws;

-- Create titles table
CREATE TABLE rnc_titles (
    id BIGSERIAL PRIMARY KEY,
    title_number INTEGER NOT NULL,
    title_name TEXT NOT NULL,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(title_number)
);

-- Create chapters table
CREATE TABLE rnc_chapters (
    id BIGSERIAL PRIMARY KEY,
    title_number INTEGER NOT NULL,
    title_name TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    chapter_name TEXT NOT NULL,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (title_number) REFERENCES rnc_titles(title_number),
    UNIQUE(title_number, chapter_number)
);

-- Create sections table
CREATE TABLE rnc_sections (
    id BIGSERIAL PRIMARY KEY,
    title_number INTEGER NOT NULL,
    title_name TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    chapter_name TEXT NOT NULL,
    section_number VARCHAR(10) NOT NULL,
    section_name TEXT NOT NULL,
    hypertexte_link TEXT,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (title_number, chapter_number) REFERENCES rnc_chapters(title_number, chapter_number),
    UNIQUE(title_number, chapter_number, section_number)
);

-- Create articles table
CREATE TABLE rnc_articles (
    id BIGSERIAL PRIMARY KEY,
    title_number INTEGER NOT NULL,
    title_name TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    chapter_name TEXT NOT NULL,
    section_number VARCHAR(10),
    section_name TEXT,
    article_number VARCHAR(10) NOT NULL,
    article_name TEXT NOT NULL,
    section_number VARCHAR(10),
    section_name TEXT,
    content TEXT,
    hypertexte_link TEXT,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (title_number, chapter_number) REFERENCES rnc_chapters(title_number, chapter_number),
    UNIQUE(title_number, chapter_number, article_number)
);

-- Create alineas table
CREATE TABLE rnc_alineas (
    id BIGSERIAL PRIMARY KEY,
    title_number INTEGER NOT NULL,
    title_name TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    chapter_name TEXT NOT NULL,
    section_number VARCHAR(10),
    section_name TEXT,
    article_number VARCHAR(10) NOT NULL,
    article_name TEXT NOT NULL,
    alinea_number VARCHAR(5) NOT NULL,
    content TEXT NOT NULL,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (title_number, chapter_number, article_number) REFERENCES rnc_articles(title_number, chapter_number, article_number),
    UNIQUE(title_number, chapter_number, article_number, alinea_number)
);

-- Create sub-alineas table
CREATE TABLE rnc_sub_alineas (
    id BIGSERIAL PRIMARY KEY,
    title_number INTEGER NOT NULL,
    title_name TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    chapter_name TEXT NOT NULL,
    section_number VARCHAR(10),
    section_name TEXT,
    article_number VARCHAR(10) NOT NULL,
    article_name TEXT NOT NULL,
    alinea_number VARCHAR(5) NOT NULL,
    sub_alinea TEXT NOT NULL,
    content TEXT NOT NULL,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (title_number, chapter_number, article_number, alinea_number) REFERENCES rnc_alineas(title_number, chapter_number, article_number, alinea_number),
    UNIQUE(title_number, chapter_number, article_number, alinea_number, sub_alinea)
);

-- Create sub-sub-alineas table
CREATE TABLE rnc_sub_sub_alineas (
    id BIGSERIAL PRIMARY KEY,
    title_number INTEGER NOT NULL,
    title_name TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    chapter_name TEXT NOT NULL,
    section_number VARCHAR(10),
    section_name TEXT,
    article_number VARCHAR(10) NOT NULL,
    article_name TEXT NOT NULL,
    alinea_number VARCHAR(5) NOT NULL,
    sub_alinea TEXT NOT NULL,
    sub_sub_alinea TEXT NOT NULL,
    content TEXT NOT NULL,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (title_number, chapter_number, article_number, alinea_number, sub_alinea) REFERENCES rnc_sub_alineas(title_number, chapter_number, article_number, alinea_number, sub_alinea),
    UNIQUE(title_number, chapter_number, article_number, alinea_number, sub_alinea, sub_sub_alinea)
);

-- Create code laws table
CREATE TABLE code_laws (
    id BIGSERIAL PRIMARY KEY,
    law_number TEXT NOT NULL,
    law_title TEXT NOT NULL,
    law_text TEXT NOT NULL,
    law_date DATE,
    law_category TEXT NOT NULL,
    hypertexte_link TEXT,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(law_number)
);

-- Create article-law relationships table
CREATE TABLE article_law_relationships (
    id BIGSERIAL PRIMARY KEY,
    article_id BIGINT NOT NULL,
    law_id BIGINT NOT NULL,
    relationship_type TEXT CHECK (relationship_type IN (
        'implements',
        'references',
        'amends',
        'announces',
        'complements'
    )),
    description TEXT,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (article_id) REFERENCES rnc_articles(id),
    FOREIGN KEY (law_id) REFERENCES code_laws(id),
    UNIQUE(article_id, law_id, relationship_type)
);

-- Create indexes for performance
CREATE INDEX idx_titles_number ON rnc_titles(title_number);
CREATE INDEX idx_chapters_number ON rnc_chapters(title_number, chapter_number);
CREATE INDEX idx_sections_number ON rnc_sections(title_number, chapter_number, section_number);
CREATE INDEX idx_articles_number ON rnc_articles(title_number, chapter_number, article_number);
CREATE INDEX idx_alineas_number ON rnc_alineas(title_number, chapter_number, article_number, alinea_number);
CREATE INDEX idx_sub_alineas ON rnc_sub_alineas(title_number, chapter_number, article_number, alinea_number, sub_alinea);
CREATE INDEX idx_sub_sub_alineas ON rnc_sub_sub_alineas(title_number, chapter_number, article_number, alinea_number, sub_alinea, sub_sub_alinea);
CREATE INDEX idx_laws_number ON code_laws(law_number);
CREATE INDEX idx_relationships ON article_law_relationships(article_id, law_id);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for all tables
CREATE TRIGGER update_titles_updated_at
    BEFORE UPDATE ON rnc_titles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chapters_updated_at
    BEFORE UPDATE ON rnc_chapters
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sections_updated_at
    BEFORE UPDATE ON rnc_sections
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_articles_updated_at
    BEFORE UPDATE ON rnc_articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alineas_updated_at
    BEFORE UPDATE ON rnc_alineas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sub_alineas_updated_at
    BEFORE UPDATE ON rnc_sub_alineas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sub_sub_alineas_updated_at
    BEFORE UPDATE ON rnc_sub_sub_alineas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_laws_updated_at
    BEFORE UPDATE ON code_laws
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_relationships_updated_at
    BEFORE UPDATE ON article_law_relationships
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
