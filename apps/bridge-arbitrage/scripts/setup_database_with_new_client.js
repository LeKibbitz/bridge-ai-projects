const { createClient } = require('@supabase/supabase-js');
const config = require('./config');

// Service role key for table creation
const serviceRoleKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcwMTM5ODg5NSwiZXhwIjoyMDY2OTc0ODk1fQ.1cXN73yMz74L34v5zF9jM7424v5zF9jM7424v5zF9jM';

// Client for table creation
const supabaseService = createClient(
    config.supabase.url,
    serviceRoleKey,
    {
        auth: {
            persistSession: false,
            autoRefreshToken: false
        }
    }
);

// Client for verification
const supabaseAnon = createClient(
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
        try {
            await supabaseService.rpc('execute_sql', {
                sql: 'DROP TABLE IF EXISTS rnc_articles CASCADE; DROP TABLE IF EXISTS code_laws CASCADE;'
            });
        } catch (error) {
            console.error('Error dropping existing tables:', error);
            throw error;
        }

        // Create RNC articles table
        try {
            await supabaseService.rpc('execute_sql', {
                sql: `
                    CREATE TABLE rnc_articles (
                        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                        title_number TEXT,
                        title_name TEXT,
                        chapter_number TEXT,
                        chapter_name TEXT,
                        section_number TEXT,
                        section_name TEXT,
                        article_number TEXT,
                        article_name TEXT,
                        content TEXT,
                        hypertexte_link TEXT,
                        created_by TEXT NOT NULL DEFAULT 'system',
                        updated_by TEXT NOT NULL DEFAULT 'system',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )`
            });
        } catch (error) {
            console.error('Error creating RNC articles table:', error);
            throw error;
        }

        // Create Code laws table
        try {
            await supabaseService.rpc('execute_sql', {
                sql: `
                    CREATE TABLE code_laws (
                        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                        title_number TEXT,
                        title_name TEXT,
                        chapter_number TEXT,
                        chapter_name TEXT,
                        section_number TEXT,
                        section_name TEXT,
                        article_number TEXT,
                        article_name TEXT,
                        content TEXT,
                        hypertexte_link TEXT,
                        created_by TEXT NOT NULL DEFAULT 'system',
                        updated_by TEXT NOT NULL DEFAULT 'system',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )`
            });
        } catch (error) {
            console.error('Error creating Code laws table:', error);
            throw error;
        }
                    article_name TEXT,
                    content TEXT,
                    hypertexte_link TEXT,
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

        // Close the initial client
        await supabase.auth.signOut();

        // Create a new client instance
        const newSupabase = createClient(
            config.supabase.url,
            config.supabase.key,
            {
                auth: {
                    persistSession: false,
                    autoRefreshToken: false
                }
            }
        );

        // Verify tables were created
        try {
            const { data: rncArticles, error: rncError } = await newSupabase
                .from('rnc_articles')
                .select('id')
                .limit(1);

            const { data: codeArticles, error: codeError } = await supabaseAnon
                .from('code_laws')
                .select('id')
                .limit(1);

            if (rncError) {
                console.error('Error verifying rnc_articles table:', rncError);
            }

            if (codeError) {
                console.error('Error verifying code_laws table:', codeError);
            }
        } catch (error) {
            console.error('Error during table verification:', error);
            throw error;
        }
    } catch (error) {
        console.error('Error setting up database:', error);
        throw error;
    }

        console.log('Database setup completed successfully.');
    } catch (error) {
        console.error('Error setting up database:', error);
    }
}

setupDatabase();
