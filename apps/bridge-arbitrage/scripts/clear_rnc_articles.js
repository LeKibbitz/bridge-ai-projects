const { createClient } = require('@supabase/supabase-js');

// Initialize Supabase client
const supabaseUrl = 'https://aqokcjsmajnpfkladubp.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTM5ODg5NSwiZXhwIjoyMDY2OTc0ODk1fQ.lzWw_o-HtNRCIHAVlq3ucBkHh0ZSRsrHYvE4VwYjafw';

const supabase = createClient(supabaseUrl, supabaseKey, {
    auth: {
        persistSession: false,
        autoRefreshToken: false
    }
});

async function clearArticles() {
    try {
        console.log('Clearing rnc_articles table...');
        
        // Create a new Supabase client with service role
        const serviceRoleSupabase = createClient(supabaseUrl, supabaseKey, {
            auth: {
                persistSession: false,
                autoRefreshToken: false
            }
        });

        // Delete all records from rnc_articles
        const { error } = await serviceRoleSupabase
            .from('rnc_articles')
            .delete()
            .eq('id', 'id'); // Using a trick to delete all records

        if (error) {
            console.error('Error clearing articles:', error);
            throw error;
        }

        console.log('Successfully cleared rnc_articles table');
    } catch (error) {
        console.error('Error in clearArticles:', error);
        throw error;
    }
}

// Run the function
clearArticles();
