-- Create bug reports table
CREATE TABLE IF NOT EXISTS bug_reports (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  article_type VARCHAR(50) NOT NULL,  -- 'rnc', 'code', 'rpi', etc.
  article_id INTEGER,
  reference_text TEXT,
  description TEXT NOT NULL,
  status VARCHAR(20) DEFAULT 'new',
  priority VARCHAR(20) DEFAULT 'normal',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  resolved_at TIMESTAMP WITH TIME ZONE,
  resolution_notes TEXT
);

-- Create bug report attachments table
CREATE TABLE IF NOT EXISTS bug_report_attachments (
  id SERIAL PRIMARY KEY,
  bug_report_id INTEGER REFERENCES bug_reports(id),
  file_path TEXT NOT NULL,
  file_name TEXT NOT NULL,
  file_type VARCHAR(50) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create bug report comments table
CREATE TABLE IF NOT EXISTS bug_report_comments (
  id SERIAL PRIMARY KEY,
  bug_report_id INTEGER REFERENCES bug_reports(id),
  user_id UUID REFERENCES users(id),
  content TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_bug_reports_status ON bug_reports(status);
CREATE INDEX idx_bug_reports_priority ON bug_reports(priority);
CREATE INDEX idx_bug_reports_user ON bug_reports(user_id);
CREATE INDEX idx_bug_reports_article ON bug_reports(article_type, article_id);
CREATE INDEX idx_bug_report_attachments_report ON bug_report_attachments(bug_report_id);
CREATE INDEX idx_bug_report_comments_report ON bug_report_comments(bug_report_id);

-- Create view for easier querying
CREATE VIEW bug_reports_view AS
SELECT
  br.*,
  u.email as reporter_email,
  u.first_name as reporter_first_name,
  u.last_name as reporter_last_name,
  COUNT(DISTINCT brc.id) as comment_count,
  COUNT(DISTINCT bra.id) as attachment_count
FROM bug_reports br
LEFT JOIN users u ON br.user_id = u.id
LEFT JOIN bug_report_comments brc ON br.id = brc.bug_report_id
LEFT JOIN bug_report_attachments bra ON br.id = bra.bug_report_id
GROUP BY br.id, u.id;
