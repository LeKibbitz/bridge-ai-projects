const { supabase } = require('../src/supabaseClient');

async function checkTables() {
    try {
        // First, let's check if we can access the rnc_articles table
        const { data: articles, error: articlesError } = await supabase
            .from('rnc_articles')
            .select('*')
            .limit(1);

        if (articlesError) throw articlesError;

        console.log('\nDatabase structure check:');
        
        // Check table structure by trying to insert a test record
        const { error: insertError } = await supabase
            .from('rnc_articles')
            .insert([{
                title_number: '1',
                chapter_number: '1',
                article_number: '1',
                article_name: 'Test Article',
                content: 'Test content',
                created_by: 'test',
                updated_by: 'test'
            }]);

        if (insertError) {
            console.log('Insert test failed:', insertError.message);
        } else {
            console.log('Successfully inserted test record');
        }

        // Clean up the test record
        const { error: deleteError } = await supabase
            .from('rnc_articles')
            .delete()
            .eq('article_number', '1');

        if (deleteError) {
            console.log('Cleanup failed:', deleteError.message);
        } else {
            console.log('Successfully cleaned up test record');
        }

    } catch (error) {
        console.error('Error checking database structure:', error);
    }
}

checkTables();
