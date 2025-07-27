const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

// Initialize Supabase client with service role
const supabaseUrl = 'https://aqokcjsmajnpfkladubp.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMzE2MjY5MSwiZXhwIjoyMDUxNzQ0NjkxfQ.9844kz8zXG41Y147q75HcN8ZQ3c85475s578141745';
const supabase = createClient(supabaseUrl, supabaseKey);

async function executeSqlFile(filePath) {
    const sql = fs.readFileSync(filePath, 'utf-8');
    
    // Split SQL into individual statements
    const statements = sql.split(';').filter(stmt => stmt.trim());
    
    for (const stmt of statements) {
        const trimmedStmt = stmt.trim();
        if (trimmedStmt) {
            try {
                // Use the service role client
                const { data, error } = await supabase.rpc('execute_sql', { sql: trimmedStmt });
                if (error) throw error;
            } catch (error) {
                console.error(`Error executing statement: ${trimmedStmt}`);
                throw error;
            }
        }
    }
    
    return { success: true };
}

async function main() {
    try {
        // 1. Add new fields to existing tables
        console.log('Adding new fields to existing tables...');
        await executeSqlFile(path.join(__dirname, 'add_fields_to_existing_tables.sql'));

        // 2. Verify the new structure
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
