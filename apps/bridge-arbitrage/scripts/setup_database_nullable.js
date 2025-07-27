const { createClient } = require('@supabase/supabase-js');

// Supabase configuration
const SUPABASE_URL = 'https://aqokcjsmajnpfkladubp.supabase.co';
const SUPABASE_SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMTM5ODg5NSwiZXhwIjoyMDY2OTc0ODk1fQ.15Dp36QxJ86k6xq8jDQ6Qq86k6xq8jDQ6QxJ86k6xq8';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzOTg4OTUsImV4cCI6MjA2Njk3NDg5NX0.f2Z4aRkTlUExrpir4fqIpn0TkzpS5B0WPuAHAb26YFM';

// Create clients
const serviceClient = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);
const anonClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function setupDatabase() {
    try {
        // Drop existing tables
        console.log('Dropping existing tables...');
        await serviceClient.rpc('drop_table', { table_name: 'rnc_articles' });
        await serviceClient.rpc('drop_table', { table_name: 'code_laws' });

        // Create new tables
        console.log('Creating new tables...');
        await serviceClient.rpc('create_table', { 
            table_name: 'rnc_articles',
            sql: `
                CREATE TABLE rnc_articles (
                    id SERIAL PRIMARY KEY,
                    title_number TEXT NULL,
                    title_name TEXT NULL,
                    chapter_number TEXT NULL,
                    chapter_name TEXT NULL,
                    section_number TEXT NULL,
                    section_name TEXT NULL,
                    article_number TEXT NULL,
                    article_name TEXT NULL,
                    content TEXT NULL,
                    hypertexte_link TEXT NULL,
                    created_by TEXT NOT NULL DEFAULT 'system',
                    updated_by TEXT NOT NULL DEFAULT 'system',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unique_article UNIQUE (title_number, chapter_number, section_number, article_number)
                )
            `
        });

        await serviceClient.rpc('create_table', { 
            table_name: 'code_laws',
            sql: `
                CREATE TABLE code_laws (
                    id SERIAL PRIMARY KEY,
                    title_number TEXT NULL,
                    title_name TEXT NULL,
                    chapter_number TEXT NULL,
                    chapter_name TEXT NULL,
                    section_number TEXT NULL,
                    section_name TEXT NULL,
                    article_number TEXT NULL,
                    article_name TEXT NULL,
                    content TEXT NULL,
                    hypertexte_link TEXT NULL,
                    created_by TEXT NOT NULL DEFAULT 'system',
                    updated_by TEXT NOT NULL DEFAULT 'system',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unique_code_law UNIQUE (title_number, chapter_number, section_number, article_number)
                )
            `
        });

        // Create indexes
        console.log('Creating indexes...');
        await serviceClient.rpc('create_index', { 
            table_name: 'rnc_articles',
            index_name: 'idx_rnc_articles_title',
            columns: 'title_number'
        });

        await serviceClient.rpc('create_index', { 
            table_name: 'rnc_articles',
            index_name: 'idx_rnc_articles_chapter',
            columns: 'chapter_number'
        });

        await serviceClient.rpc('create_index', { 
            table_name: 'rnc_articles',
            index_name: 'idx_rnc_articles_section',
            columns: 'section_number'
        });

        await serviceClient.rpc('create_index', { 
            table_name: 'rnc_articles',
            index_name: 'idx_rnc_articles_article',
            columns: 'article_number'
        });

        await serviceClient.rpc('create_index', { 
            table_name: 'code_laws',
            index_name: 'idx_code_laws_title',
            columns: 'title_number'
        });

        await serviceClient.rpc('create_index', { 
            table_name: 'code_laws',
            index_name: 'idx_code_laws_chapter',
            columns: 'chapter_number'
        });

        await serviceClient.rpc('create_index', { 
            table_name: 'code_laws',
            index_name: 'idx_code_laws_section',
            columns: 'section_number'
        });

        await serviceClient.rpc('create_index', { 
            table_name: 'code_laws',
            index_name: 'idx_code_laws_article',
            columns: 'article_number'
        });

        console.log('✅ Database setup completed successfully!');
    } catch (error) {
        console.error('Error setting up database:', error);
        throw error;
    }
}

setupDatabase().catch(console.error);
