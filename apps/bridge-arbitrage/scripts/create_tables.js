const { supabase } = require('../src/supabaseClient');

async function createTables() {
  try {
    const sql = `-- Drop existing tables if they exist
DROP TABLE IF EXISTS rnc_article_relationships;
DROP TABLE IF EXISTS rnc_article_references;
DROP TABLE IF EXISTS article_law_relationships;
DROP TABLE IF EXISTS rnc_article_metadata;
DROP TABLE IF EXISTS code_laws;
DROP TABLE IF EXISTS rnc_articles;

-- Create main articles table with optimized indexes
CREATE TABLE rnc_articles (
    id BIGSERIAL PRIMARY KEY,
    title_number INTEGER,
    chapter_number INTEGER,
    article_number VARCHAR(10) UNIQUE,
    title_name TEXT,
    chapter_name TEXT,
    section_number VARCHAR(10),
    section_title TEXT,
    content TEXT,
    pdf_path TEXT,
    parent_article_id BIGINT REFERENCES rnc_articles(id),
    order_in_chapter INTEGER,
    order_in_title INTEGER,
    is_section BOOLEAN DEFAULT FALSE,
    is_chapter BOOLEAN DEFAULT FALSE,
    is_title BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create article relationships table with indexes
CREATE TABLE rnc_article_relationships (
    id BIGSERIAL PRIMARY KEY,
    parent_article_id BIGINT REFERENCES rnc_articles(id),
    child_article_id BIGINT REFERENCES rnc_articles(id),
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

-- Create article references table with indexes
CREATE TABLE rnc_article_references (
    id BIGSERIAL PRIMARY KEY,
    article_id BIGINT REFERENCES rnc_articles(id),
    referenced_article_id BIGINT REFERENCES rnc_articles(id),
    reference_text TEXT,
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

-- Create code laws table with optimized indexes
CREATE TABLE code_laws (
    id BIGSERIAL PRIMARY KEY,
    law_number TEXT UNIQUE,
    law_title TEXT,
    law_text TEXT,
    law_date DATE,
    law_category TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create article-law relationships table with indexes
CREATE TABLE article_law_relationships (
    id BIGSERIAL PRIMARY KEY,
    article_id BIGINT REFERENCES rnc_articles(id),
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

-- Create article metadata table with indexes
CREATE TABLE rnc_article_metadata (
    id BIGSERIAL PRIMARY KEY,
    article_id BIGINT REFERENCES rnc_articles(id),
    key TEXT,
    value TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(article_id, key)
);

-- Create indexes for performance
-- RNC Articles indexes
CREATE INDEX idx_article_number ON rnc_articles(article_number);
CREATE INDEX idx_title_chapter ON rnc_articles(title_number, chapter_number);
CREATE INDEX idx_parent_article ON rnc_articles(parent_article_id);
CREATE INDEX idx_article_hierarchy ON rnc_articles(title_number, chapter_number, article_number);
CREATE INDEX idx_article_order ON rnc_articles(order_in_title, order_in_chapter);
CREATE INDEX idx_article_type ON rnc_articles(is_title, is_chapter, is_section);

-- Article Relationships indexes
CREATE INDEX idx_relationships_parent ON rnc_article_relationships(parent_article_id);
CREATE INDEX idx_relationships_child ON rnc_article_relationships(child_article_id);
CREATE INDEX idx_relationships_type ON rnc_article_relationships(relationship_type);

-- Article References indexes
CREATE INDEX idx_references_article ON rnc_article_references(article_id);
CREATE INDEX idx_references_referenced ON rnc_article_references(referenced_article_id);
CREATE INDEX idx_references_type ON rnc_article_references(reference_type);

-- Code Laws indexes
CREATE INDEX idx_law_number ON code_laws(law_number);
CREATE INDEX idx_law_category ON code_laws(law_category);
CREATE INDEX idx_law_date ON code_laws(law_date);

-- Article-Law Relationships indexes
CREATE INDEX idx_article_law_article ON article_law_relationships(article_id);
CREATE INDEX idx_article_law_law ON article_law_relationships(law_id);
CREATE INDEX idx_article_law_type ON article_law_relationships(relationship_type);

-- Create trigger to update updated_at timestamps
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

CREATE TRIGGER update_code_laws_updated_at
    BEFORE UPDATE ON code_laws
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();`;

    const { data, error } = await supabase.rpc('execute_sql', { sql });
    if (error) throw error;
    console.log('Tables created successfully!');
  } catch (error) {
    console.error('Error creating tables:', error);
  }
}

createTables();
