const { createClient } = require('@supabase/supabase-js');
const config = require('./config');

const supabase = createClient(
    config.supabase.url,
    config.supabase.key,
    {
        auth: {
            persistSession: false,
            autoRefreshToken: false
        }
    }
);

async function setupDatabase() {
    try {
        // Drop existing tables if they exist
        await supabase.rpc('execute_sql', {
            sql: 'DROP TABLE IF EXISTS rnc_articles CASCADE; DROP TABLE IF EXISTS code_laws CASCADE;'
        });

        // Create RNC articles table
        await supabase.rpc('execute_sql', {
            sql: `
                CREATE TABLE rnc_articles (
                    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                    title_number TEXT NOT NULL,
                    title_name TEXT NOT NULL,
                    chapter_number TEXT,
                    chapter_name TEXT,
                    section_number TEXT,
                    section_name TEXT,
                    article_number TEXT NOT NULL,
                    article_name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    hypertexte_link TEXT NOT NULL,
                    created_by TEXT NOT NULL DEFAULT 'system',
                    updated_by TEXT NOT NULL DEFAULT 'system',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )`
        });

        // Create Code laws table
        await supabase.rpc('execute_sql', {
            sql: `
                CREATE TABLE code_laws (
                    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                    title_number TEXT NOT NULL,
                    title_name TEXT NOT NULL,
                    chapter_number TEXT,
                    chapter_name TEXT,
                    section_number TEXT,
                    section_name TEXT,
                    article_number TEXT NOT NULL,
                    article_name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    hypertexte_link TEXT NOT NULL,
                    created_by TEXT NOT NULL DEFAULT 'system',
                    updated_by TEXT NOT NULL DEFAULT 'system',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )`
        });

        // Create indexes
        await supabase.rpc('execute_sql', {
            sql: `
                CREATE INDEX idx_rnc_articles_title ON rnc_articles(title_number);
                CREATE INDEX idx_rnc_articles_chapter ON rnc_articles(chapter_number);
                CREATE INDEX idx_rnc_articles_section ON rnc_articles(section_number);
                CREATE INDEX idx_rnc_articles_article ON rnc_articles(article_number);
                CREATE INDEX idx_code_laws_title ON code_laws(title_number);
                CREATE INDEX idx_code_laws_chapter ON code_laws(chapter_number);
                CREATE INDEX idx_code_laws_article ON code_laws(article_number)`
        });

        // Create trigger function
        await supabase.rpc('execute_sql', {
            sql: `
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql'`
        });

        // Create triggers
        await supabase.rpc('execute_sql', {
            sql: `
                CREATE TRIGGER update_rnc_articles_updated_at
                    BEFORE UPDATE ON rnc_articles
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();

                CREATE TRIGGER update_code_laws_updated_at
                    BEFORE UPDATE ON code_laws
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();`
        });

        // Wait for schema cache to update
        console.log('Waiting for schema cache to update...');
        await new Promise(resolve => setTimeout(resolve, 5000));

        // Verify tables exist
        const { data: rncArticles, error: rncError } = await supabase
            .from('rnc_articles')
            .select('id')
            .limit(1);

        const { data: codeLaws, error: codeError } = await supabase
            .from('code_laws')
            .select('id')
            .limit(1);

        if (rncError) {
            console.error('Error verifying rnc_articles table:', rncError);
        }

        if (codeError) {
            console.error('Error verifying code_laws table:', codeError);
        }

        console.log('Database setup completed successfully.');
    } catch (error) {
        console.error('Error setting up database:', error);
    }
}

setupDatabase();
