-- Drop existing tables if they exist
DROP TABLE IF EXISTS rnc_article_relationships;
DROP TABLE IF EXISTS rnc_article_references;
DROP TABLE IF EXISTS rnc_articles;

-- Create main articles table
CREATE TABLE rnc_article (
    id BIGSERIAL PRIMARY KEY,
    title_number INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,
    article_number VARCHAR(10) NOT NULL,
    title_name TEXT NOT NULL,          -- Full title name (e.g., "Titre I - Des règles générales")
    chapter_name TEXT NOT NULL,        -- Full chapter name
    section_number VARCHAR(10),        -- For sections within articles
    section_title TEXT,                -- Title of the section
    alinea_number VARCHAR(5),          -- Can be number (1, 2, 3), letter (a, b, c), letter with parentheses (a), (b)), or roman numeral (i, ii, iii)
    sub_alinea TEXT,                   -- Can be number (1), letter (a), letter with parentheses (a), (b)), or roman numeral (i) with parentheses
    sub_sub_alinea TEXT,               -- Can be number (1), letter (a), letter with parentheses (a), (b)), or roman numeral (i) with parentheses
    content TEXT NOT NULL,
    pdf_path TEXT,                     -- Path to PDF document if available
    hypertexte_link TEXT,              -- Link to related articles/content
    parent_article_id BIGINT REFERENCES rnc_article(id), -- For article relationships
    order_in_chapter INTEGER,
    order_in_title INTEGER,
    is_section BOOLEAN DEFAULT FALSE,
    is_chapter BOOLEAN DEFAULT FALSE,
    is_title BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    version INTEGER DEFAULT 1,
    UNIQUE(article_number),
    CHECK (title_number > 0),
    CHECK (chapter_number > 0)
);

-- Create parsing progress tracking table

CREATE TABLE parsing_progress (
    id BIGSERIAL PRIMARY KEY,
    document_type TEXT CHECK (document_type IN ('code_laws', 'rnc_articles')),
    current_section TEXT,
    current_chapter TEXT,
    current_article TEXT,
    current_alinea TEXT,
    current_sub_alinea TEXT,
    progress_percentage INTEGER,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status TEXT CHECK (status IN ('parsing', 'completed', 'error')),
    error_message TEXT
);

-- Create article relationships table
CREATE TABLE rnc_article_relationships (
    id BIGSERIAL PRIMARY KEY,
    parent_article_id BIGINT REFERENCES rnc_article(id),
    child_article_id BIGINT REFERENCES rnc_article(id),
    relationship_type TEXT CHECK (relationship_type IN (
        'references',
        'follows',
        'is_part_of',
        'explains',
        'amends',
        'replaces'
    )),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(parent_article_id, child_article_id, relationship_type)
);

-- Create article references table
CREATE TABLE rnc_article_references (
    id BIGSERIAL PRIMARY KEY,
    article_id BIGINT REFERENCES rnc_articles(id),
    referenced_article_id BIGINT REFERENCES rnc_article(id),
    reference_text TEXT, -- The actual reference text in the article
    reference_type TEXT CHECK (reference_type IN (
        'article',
        'section',
        'chapter',
        'title',
        'external'
    )),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(article_id, referenced_article_id, reference_text)
);

-- Create code laws table
CREATE TABLE code_laws (
    id SERIAL PRIMARY KEY,
    law_number TEXT UNIQUE NOT NULL,
    law_title TEXT NOT NULL,
    law_text TEXT NOT NULL,
    law_date DATE NOT NULL,
    law_category TEXT NOT NULL,
    section_number VARCHAR(10),
    section_title TEXT,
    alinea_number VARCHAR(5),          -- Can be number (1, 2, 3), letter (a, b, c), letter with parentheses (a), (b)), or roman numeral (i, ii, iii)
    sub_alinea TEXT,                   -- Can be number (1), letter (a), letter with parentheses (a), (b)), or roman numeral (i) with parentheses
    sub_sub_alinea TEXT,               -- Can be number (1), letter (a), letter with parentheses (a), (b)), or roman numeral (i) with parentheses
    hypertexte_link TEXT,
    pdf_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    version INTEGER DEFAULT 1
);

-- Create a separate table to manage parent-child relationships for code laws
CREATE TABLE code_laws_hierarchy (
    id SERIAL PRIMARY KEY,
    child_law_id INTEGER REFERENCES code_laws(id),
    parent_law_id INTEGER REFERENCES code_laws(id),
    hierarchy_level INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(child_law_id, parent_law_id, hierarchy_level)
);

-- Create article-law relationships table
CREATE TABLE article_law_relationships (
    id BIGSERIAL PRIMARY KEY,
    article_id BIGINT REFERENCES rnc_article(id),
    law_id BIGINT REFERENCES code_laws(id),
    relationship_type TEXT CHECK (relationship_type IN (
        'implements',
        'references',
        'amends',
        'announces',
        'complements'
    )),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(article_id, law_id, relationship_type)
);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_code_laws_updated_at
    BEFORE UPDATE ON code_laws
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create article metadata table
CREATE TABLE rnc_article_metadata (
    id BIGSERIAL PRIMARY KEY,
    article_id BIGINT REFERENCES rnc_article(id),
    key TEXT,
    value TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(article_id, key)
);

-- Create indexes for performance
CREATE INDEX idx_article_number ON rnc_article(article_number);
CREATE INDEX idx_title_chapter ON rnc_article(title_number, chapter_number);
CREATE INDEX idx_parent_article ON rnc_article_hierarchy(child_article_id);
CREATE INDEX idx_relationships ON rnc_article_hierarchy(parent_article_id, child_article_id);
CREATE INDEX idx_relationships ON rnc_article_relationships(parent_article_id, child_article_id);
CREATE INDEX idx_references ON rnc_article_references(article_id, referenced_article_id);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_rnc_articles_updated_at
    BEFORE UPDATE ON rnc_articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
