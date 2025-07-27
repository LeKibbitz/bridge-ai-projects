-- Create document versions table
CREATE TABLE IF NOT EXISTS document_versions (
  id SERIAL PRIMARY KEY,
  version TEXT UNIQUE NOT NULL,
  document_type TEXT NOT NULL,
  effective_date DATE,
  expiration_date DATE,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create RPI articles table
CREATE TABLE IF NOT EXISTS rpi_articles (
  id SERIAL PRIMARY KEY,
  document_version_id INTEGER REFERENCES document_versions(id),
  main_title TEXT,
  sub_title TEXT,
  section_number TEXT,
  sub_section_number TEXT,
  article_number TEXT,
  sub_article_number TEXT,
  sub_sub_article TEXT,
  content TEXT,
  pdf_path TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_rpi_articles_version ON rpi_articles(document_version_id);
CREATE INDEX idx_rpi_articles_section ON rpi_articles(section_number);
CREATE INDEX idx_rpi_articles_article ON rpi_articles(article_number);

-- Insert initial document version
INSERT INTO document_versions (version, document_type, effective_date, notes)
VALUES ('2021/2022', 'RPI', '2021-11-01', 'Initial RPI document version');
