const { createClient } = require('@supabase/supabase-js');

// Service Role Key (should be different from anon key)
const supabaseUrl = 'https://aqokcjsmajnpfkladubp.supabase.co';
const serviceRoleKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMTM5ODg5NSwiZXhwIjoyMDY2OTc0ODk1fQ.43k84tq0Qb9a71z7vFwW69V65Gh6n59qX490123456';

const supabase = createClient(supabaseUrl, serviceRoleKey, {
    auth: {
        persistSession: false,
        autoRefreshToken: false
    }
});

async function testServiceRole() {
    try {
        // Test with a simple query
        const { data, error } = await supabase
            .from('rnc_articles')
            .select('*')
            .limit(1);

        if (error) {
            console.error('Error using service role:', error);
            return;
        }

        console.log('Successfully connected with service role!');
        console.log('Sample data:', data);

        // Test with an insert
        const insertData = {
            article_number: 'TEST-123',
            content: 'Test content',
            created_by: 'system',
            updated_by: 'system'
        };

        const { error: insertError } = await supabase
            .from('rnc_articles')
            .insert([insertData]);

        if (insertError) {
            console.error('Error inserting with service role:', insertError);
            return;
        }

        console.log('Successfully inserted test data!');

    } catch (error) {
        console.error('Unexpected error:', error);
    }
}

testServiceRole();
