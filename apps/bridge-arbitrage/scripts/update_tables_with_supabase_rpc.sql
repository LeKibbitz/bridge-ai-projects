-- Add new fields to rnc_articles
ALTER TABLE rnc_articles 
ADD COLUMN IF NOT EXISTS alinea TEXT NULL,
ADD COLUMN IF NOT EXISTS sub_alinea TEXT NULL,
ADD COLUMN IF NOT EXISTS sub_sub_alinea TEXT NULL;

-- Add new fields to code_laws
ALTER TABLE code_laws 
ADD COLUMN IF NOT EXISTS alinea TEXT NULL,
ADD COLUMN IF NOT EXISTS sub_alinea TEXT NULL,
ADD COLUMN IF NOT EXISTS sub_sub_alinea TEXT NULL;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_rnc_articles_alinea ON rnc_articles(alinea);
CREATE INDEX IF NOT EXISTS idx_rnc_articles_sub_alinea ON rnc_articles(sub_alinea);
CREATE INDEX IF NOT EXISTS idx_rnc_articles_sub_sub_alinea ON rnc_articles(sub_sub_alinea);
CREATE INDEX IF NOT EXISTS idx_code_laws_alinea ON code_laws(alinea);
CREATE INDEX IF NOT EXISTS idx_code_laws_sub_alinea ON code_laws(sub_alinea);
CREATE INDEX IF NOT EXISTS idx_code_laws_sub_sub_alinea ON code_laws(sub_sub_alinea);

-- Verify the changes
SELECT column_name FROM information_schema.columns WHERE table_name = 'rnc_articles';
SELECT column_name FROM information_schema.columns WHERE table_name = 'code_laws';
