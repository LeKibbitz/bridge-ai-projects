const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://aqokcjsmajnpfkladubp.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzOTg4OTUsImV4cCI6MjA2Njk3NDg5NX0.f2Z4aRkTlUExrpir4fqIpn0TkzpS5B0WPuAHAb26YFM';

const supabase = createClient(supabaseUrl, supabaseKey, {
    auth: {
        persistSession: false,
        autoRefreshToken: false
    }
});

async function testConnection() {
    try {
        const { data, error } = await supabase
            .from('rnc_articles')
            .select('article_number, article_name')
            .limit(1);

        if (error) throw error;
        console.log('Database connection successful!');
        console.log('Sample data:', data);
    } catch (error) {
        console.error('Database connection error:', error);
    }
}

testConnection();
