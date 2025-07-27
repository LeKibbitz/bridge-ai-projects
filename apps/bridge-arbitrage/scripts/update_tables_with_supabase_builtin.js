const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

// Initialize Supabase client
const supabaseUrl = 'https://aqokcjsmajnpfkladubp.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzOTg4OTUsImV4cCI6MjA2Njk3NDg5NX0.f2Z4aRkTlUExrpir4fqIpn0TkzpS5B0WPuAHAb26YFM';
const supabase = createClient(supabaseUrl, supabaseKey);

async function main() {
    try {
        // Read the SQL file
        const sql = fs.readFileSync(path.join(__dirname, 'update_tables_with_supabase_builtin.sql'), 'utf-8');
        
        // Split SQL into individual statements
        const statements = sql.split(';').filter(stmt => stmt.trim());
        
        for (const stmt of statements) {
            const trimmedStmt = stmt.trim();
            if (trimmedStmt) {
                try {
                    // Execute the SQL using service role
                    const { data, error } = await supabase
                        .from('rnc_articles') // Using any table to get a connection
                        .select('*')
                        .limit(1)
                        .then(() => {
                            // Execute the SQL using service role
                            return supabase.rpc('execute_sql', { sql: trimmedStmt }, { role: 'service_role' });
                        });
                    
                    if (error) throw error;
                } catch (error) {
                    console.error(`Error executing statement: ${trimmedStmt}`);
                    throw error;
                }
            }
        }

        console.log('All operations completed successfully!');

    } catch (error) {
        console.error('Error:', error);
        process.exit(1);
    }
}

main();
