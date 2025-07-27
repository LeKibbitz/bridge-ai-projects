const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

// Initialize Supabase client with service role
const supabaseUrl = 'https://aqokcjsmajnpfkladubp.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzOTg4OTUsImV4cCI6MjA2Njk3NDg5NX0.f2Z4aRkTlUExrpir4fqIpn0TkzpS5B0WPuAHAb26YFM';
const supabase = createClient(supabaseUrl, supabaseKey);

async function executeSql(sql) {
    try {
        // Use the service role to execute the SQL
        const { data, error } = await supabase.rpc('execute_sql', { sql }, { role: 'service_role' });
        if (error) throw error;
        return data;
    } catch (error) {
        console.error(`Error executing SQL: ${sql}`);
        throw error;
    }
}

async function main() {
    try {
        // 1. Add new fields to rnc_articles
        console.log('Adding new fields to rnc_articles...');
        await executeSql(`
            ALTER TABLE rnc_articles 
            ADD COLUMN IF NOT EXISTS alinea TEXT NULL,
            ADD COLUMN IF NOT EXISTS sub_alinea TEXT NULL,
            ADD COLUMN IF NOT EXISTS sub_sub_alinea TEXT NULL
        `);

        // 2. Add new fields to code_laws
        console.log('Adding new fields to code_laws...');
        await executeSql(`
            ALTER TABLE code_laws 
            ADD COLUMN IF NOT EXISTS alinea TEXT NULL,
            ADD COLUMN IF NOT EXISTS sub_alinea TEXT NULL,
            ADD COLUMN IF NOT EXISTS sub_sub_alinea TEXT NULL
        `);

        // 3. Create indexes
        console.log('Creating indexes...');
        await executeSql(`
            CREATE INDEX IF NOT EXISTS idx_rnc_articles_alinea ON rnc_articles(alinea);
            CREATE INDEX IF NOT EXISTS idx_rnc_articles_sub_alinea ON rnc_articles(sub_alinea);
            CREATE INDEX IF NOT EXISTS idx_rnc_articles_sub_sub_alinea ON rnc_articles(sub_sub_alinea);
            CREATE INDEX IF NOT EXISTS idx_code_laws_alinea ON code_laws(alinea);
            CREATE INDEX IF NOT EXISTS idx_code_laws_sub_alinea ON code_laws(sub_alinea);
            CREATE INDEX IF NOT EXISTS idx_code_laws_sub_sub_alinea ON code_laws(sub_sub_alinea)
        `);

        // 4. Verify the new structure
        console.log('Verifying new table structure...');
        const { data: rncColumns, error: rncError } = await supabase
            .from('information_schema.columns')
            .select('column_name')
            .eq('table_name', 'rnc_articles');

        const { data: codeColumns, error: codeError } = await supabase
            .from('information_schema.columns')
            .select('column_name')
            .eq('table_name', 'code_laws');

        if (rncError || codeError) {
            throw new Error('Error verifying table structure');
        }

        console.log('New fields successfully added to tables!');
        console.log('RNC Articles columns:', rncColumns.map(c => c.column_name));
        console.log('Code Laws columns:', codeColumns.map(c => c.column_name));

    } catch (error) {
        console.error('Error:', error);
        process.exit(1);
    }
}

main();
