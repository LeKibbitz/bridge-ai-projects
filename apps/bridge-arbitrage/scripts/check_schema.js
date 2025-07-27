const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://aqokcjsmajnpfkladubp.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTM5ODg5NSwiZXhwIjoyMDY2OTc0ODk1fQ.lzWw_o-HtNRCIHAVlq3ucBkHh0ZSRsrHYvE4VwYjafw';

const supabase = createClient(supabaseUrl, supabaseKey, {
    auth: {
        persistSession: false,
        autoRefreshToken: false
    }
});

async function checkSchema() {
    try {
        // Check table schema
        const { data: columns, error } = await supabase
            .rpc('get_table_columns', { table_name: 'rnc_articles' });

        if (error) throw error;

        console.log('rnc_articles columns:', columns);
        
        // Check for indexes
        const { data: indexes, error: indexError } = await supabase
            .rpc('get_table_indexes', { table_name: 'rnc_articles' });

        if (indexError) throw indexError;

        console.log('rnc_articles indexes:', indexes);

    } catch (error) {
        console.error('Error checking schema:', error);
    }
}

checkSchema();
