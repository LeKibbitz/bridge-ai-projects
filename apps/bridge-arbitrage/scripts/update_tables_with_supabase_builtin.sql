-- Add new fields to rnc_articles
SELECT * FROM public.alter_table_add_column('rnc_articles', 'alinea', 'TEXT', 'NULL');
SELECT * FROM public.alter_table_add_column('rnc_articles', 'sub_alinea', 'TEXT', 'NULL');
SELECT * FROM public.alter_table_add_column('rnc_articles', 'sub_sub_alinea', 'TEXT', 'NULL');

-- Add new fields to code_laws
SELECT * FROM public.alter_table_add_column('code_laws', 'alinea', 'TEXT', 'NULL');
SELECT * FROM public.alter_table_add_column('code_laws', 'sub_alinea', 'TEXT', 'NULL');
SELECT * FROM public.alter_table_add_column('code_laws', 'sub_sub_alinea', 'TEXT', 'NULL');

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_rnc_articles_alinea ON rnc_articles(alinea);
CREATE INDEX IF NOT EXISTS idx_rnc_articles_sub_alinea ON rnc_articles(sub_alinea);
CREATE INDEX IF NOT EXISTS idx_rnc_articles_sub_sub_alinea ON rnc_articles(sub_sub_alinea);
CREATE INDEX IF NOT EXISTS idx_code_laws_alinea ON code_laws(alinea);
CREATE INDEX IF NOT EXISTS idx_code_laws_sub_alinea ON code_laws(sub_alinea);
CREATE INDEX IF NOT EXISTS idx_code_laws_sub_sub_alinea ON code_laws(sub_sub_alinea);
