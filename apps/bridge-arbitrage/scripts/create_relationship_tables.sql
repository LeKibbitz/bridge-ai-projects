-- Create relationships table
CREATE TABLE IF NOT EXISTS article_relationships (
  id SERIAL PRIMARY KEY,
  source_type VARCHAR(50) NOT NULL,  -- 'rnc' or 'code'
  source_id INTEGER NOT NULL,
  target_type VARCHAR(50) NOT NULL,  -- 'rnc' or 'code'
  target_id INTEGER NOT NULL,
  relationship_type VARCHAR(50) NOT NULL,  -- e.g., 'related', 'example', 'reference'
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_source
    FOREIGN KEY (source_type, source_id)
    REFERENCES (
      SELECT 'rnc' as type, id FROM rnc_articles
      UNION ALL
      SELECT 'code' as type, id FROM laws
    ) (type, id),
  CONSTRAINT fk_target
    FOREIGN KEY (target_type, target_id)
    REFERENCES (
      SELECT 'rnc' as type, id FROM rnc_articles
      UNION ALL
      SELECT 'code' as type, id FROM laws
    ) (type, id)
);

-- Create relationship types table
CREATE TABLE IF NOT EXISTS relationship_types (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert common relationship types
INSERT INTO relationship_types (name, description) VALUES
  ('related', 'Articles liés ou complémentaires'),
  ('example', 'Article utilisé comme exemple'),
  ('reference', 'Article cité ou référencé'),
  ('clarification', 'Article qui clarifie ou explique'),
  ('exception', 'Article qui constitue une exception'),
  ('superseded', 'Article remplacé par'),
  ('amended', 'Article modifié par');

-- Create indexes for better performance
CREATE INDEX idx_relationships_source ON article_relationships(source_type, source_id);
CREATE INDEX idx_relationships_target ON article_relationships(target_type, target_id);
CREATE INDEX idx_relationships_type ON article_relationships(relationship_type);

-- Create view to simplify querying relationships
CREATE VIEW article_relationships_view AS
SELECT
  ar.id,
  ar.source_type,
  ar.source_id,
  CASE ar.source_type
    WHEN 'rnc' THEN (
      SELECT title || ' ' || article_number
      FROM rnc_articles
      WHERE id = ar.source_id
    )
    WHEN 'code' THEN (
      SELECT title || ' ' || article_number
      FROM laws
      WHERE id = ar.source_id
    )
  END as source_title,
  ar.target_type,
  ar.target_id,
  CASE ar.target_type
    WHEN 'rnc' THEN (
      SELECT title || ' ' || article_number
      FROM rnc_articles
      WHERE id = ar.target_id
    )
    WHEN 'code' THEN (
      SELECT title || ' ' || article_number
      FROM laws
      WHERE id = ar.target_id
    )
  END as target_title,
  ar.relationship_type,
  rt.description as relationship_description,
  ar.notes,
  ar.created_at,
  ar.updated_at
FROM article_relationships ar
LEFT JOIN relationship_types rt ON ar.relationship_type = rt.name;
