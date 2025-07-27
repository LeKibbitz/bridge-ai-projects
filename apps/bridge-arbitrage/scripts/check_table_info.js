const { createClient } = require('@supabase/supabase-js');

// Supabase configuration
const SUPABASE_URL = 'https://aqokcjsmajnpfkladubp.supabase.co';

// Supabase keys
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzOTg4OTUsImV4cCI6MjA2Njk3NDg5NX0.f2Z4aRkTlUExrpir4fqIpn0TkzpS5B0WPuAHAb26YFM';

// Create client with anon key for table info
const client = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function checkTableInfo() {
    try {
        console.log('Checking table information...');
        
        // First, let's check the structure of rnc_articles
        console.log('\nChecking rnc_articles structure...');
        const { data: rncStructure, error: rncError } = await client
            .from('rnc_articles')
            .select('*')
            .limit(1);

        if (rncError) {
            console.error('Error checking rnc_articles structure:', rncError);
            throw rncError;
        }

        console.log('\nColumns in rnc_articles:');
        console.log(Object.keys(rncStructure[0]));

        // Now check code_laws structure
        console.log('\nChecking code_laws structure...');
        const { data: codeStructure, error: codeError } = await client
            .from('code_laws')
            .select('*')
            .limit(1);

        if (codeError) {
            console.error('Error checking code_laws structure:', codeError);
            throw codeError;
        }

        console.log('\nColumns in code_laws:');
        console.log(Object.keys(codeStructure[0]));

        console.log('\n✅ Table information retrieved successfully!');
    } catch (error) {
        console.error('Error checking table information:', error);
        throw error;
    }
}

checkTableInfo().catch(console.error);
