const { createClient } = require('@supabase/supabase-js');

// Supabase configuration
const SUPABASE_URL = 'https://aqokcjsmajnpfkladubp.supabase.co';
const SUPABASE_SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMTM5ODg5NSwiZXhwIjoyMDY2OTc0ODk1fQ.15Dp36QxJ86k6xq8jDQ6Qq86k6xq8jDQ6QxJ86k6xq8';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzOTg4OTUsImV4cCI6MjA2Njk3NDg5NX0.f2Z4aRkTlUExrpir4fqIpn0TkzpS5B0WPuAHAb26YFM';

// Create clients
const serviceClient = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);
const anonClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function createTables() {
    try {
        // Drop existing tables if they exist
        const dropRnc = await serviceClient.rpc('drop_rnc_tables');
        const dropCode = await serviceClient.rpc('drop_code_tables');

        // Create tables
        const createRnc = await serviceClient.rpc('create_rnc_tables');
        const createCode = await serviceClient.rpc('create_code_tables');

        console.log('Tables created successfully!');
        
        // Verify tables exist
        const { data: rncData, error: rncError } = await anonClient
            .from('rnc_articles')
            .select('article_number')
            .limit(1);
        
        const { data: codeData, error: codeError } = await anonClient
            .from('code_laws')
            .select('article_number')
            .limit(1);

        if (rncError || codeError) {
            console.error('Error verifying tables:', rncError || codeError);
            throw rncError || codeError;
        }

        console.log('✅ Database setup completed successfully!');
    } catch (error) {
        console.error('Error creating tables:', error);
        throw error;
    }
}

createTables().catch(console.error);
