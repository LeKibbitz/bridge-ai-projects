const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

// Initialize Supabase client
const supabaseUrl = 'https://aqokcjsmajnpfkladubp.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzOTg4OTUsImV4cCI6MjA2Njk3NDg5NX0.f2Z4aRkTlUExrpir4fqIpn0TkzpS5B0WPuAHAb26YFM';
const supabase = createClient(supabaseUrl, supabaseKey);

async function executeSqlFile(filePath) {
    const sql = fs.readFileSync(filePath, 'utf-8');
    
    // Split SQL into individual statements
    const statements = sql.split(';').filter(stmt => stmt.trim());
    
    for (const stmt of statements) {
        const trimmedStmt = stmt.trim();
        if (trimmedStmt) {
            const { data, error } = await supabase
                .from('rnc_articles') // Using any table to get a connection
                .select('*')
                .limit(1)
                .then(() => {
                    // Execute raw SQL using the service role
                    return supabase.rpc('execute_sql', { sql: trimmedStmt }, { role: 'service_role' });
                });
            
            if (error) throw error;
        }
    }
    
    return { success: true };
}

async function main() {
    try {
        // 1. Create backup of existing tables
        console.log('Creating backup of existing tables...');
        await executeSqlFile(path.join(__dirname, 'backup_existing_tables.sql'));

        // 2. Run migration to add new fields
        console.log('Running migration to add new fields...');
        await executeSqlFile(path.join(__dirname, 'migrate_to_nullable.sql'));

        // 3. Verify the new structure
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
