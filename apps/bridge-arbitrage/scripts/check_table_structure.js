const { createClient } = require('@supabase/supabase-js');

// Supabase configuration
const SUPABASE_URL = 'https://aqokcjsmajnpfkladubp.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzOTg4OTUsImV4cCI6MjA2Njk3NDg5NX0.f2Z4aRkTlUExrpir4fqIpn0TkzpS5B0WPuAHAb26YFM';

// Create client
const client = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function checkStructure() {
    try {
        // Get table info using Supabase's metadata API
        const { data: rncInfo, error: rncError } = await client
            .from('rnc_articles')
            .select('*')
            .limit(1);

        const { data: codeInfo, error: codeError } = await client
            .from('code_laws')
            .select('*')
            .limit(1);

        // If tables don't exist, create them
        if (!rncInfo || rncInfo.length === 0) {
            console.log('Creating rnc_articles table...');
            await client.rpc('create_rnc_tables');
        }

        if (!codeInfo || codeInfo.length === 0) {
            console.log('Creating code_laws table...');
            await client.rpc('create_code_tables');
        }

        // Get table info again
        const { data: rncInfo2, error: rncError2 } = await client
            .from('rnc_articles')
            .select('*')
            .limit(1);

        const { data: codeInfo2, error: codeError2 } = await client
            .from('code_laws')
            .select('*')
            .limit(1);

        if (rncError2 || codeError2) {
            throw new Error('Failed to get table information');
        }

        console.log('\n✅ Tables created successfully!');
    } catch (error) {
        console.error('Error checking table structure:', error);
        throw error;
    }
}

checkStructure().catch(console.error);
