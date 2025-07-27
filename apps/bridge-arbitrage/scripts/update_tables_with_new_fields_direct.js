const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

// Database connection configuration
const pool = new Pool({
    host: 'db.aqokcjsmajnpfkladubp.supabase.co',
    port: 5432,
    database: 'postgres',
    user: 'postgres',
    password: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzOTg4OTUsImV4cCI6MjA2Njk3NDg5NX0.f2Z4aRkTlUExrpir4fqIpn0TkzpS5B0WPuAHAb26YFM'
});

async function executeSqlFile(filePath) {
    const sql = fs.readFileSync(filePath, 'utf-8');
    
    // Split SQL into individual statements
    const statements = sql.split(';').filter(stmt => stmt.trim());
    
    for (const stmt of statements) {
        const trimmedStmt = stmt.trim();
        if (trimmedStmt) {
            try {
                await pool.query(trimmedStmt);
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
        // 1. Create backup of existing tables
        console.log('Creating backup of existing tables...');
        await executeSqlFile(path.join(__dirname, 'backup_existing_tables.sql'));

        // 2. Run migration to add new fields
        console.log('Running migration to add new fields...');
        await executeSqlFile(path.join(__dirname, 'migrate_to_nullable.sql'));

        // 3. Verify the new structure
        console.log('Verifying new table structure...');
        const { rows: rncColumns } = await pool.query(
            'SELECT column_name FROM information_schema.columns WHERE table_name = $1',
            ['rnc_articles']
        );

        const { rows: codeColumns } = await pool.query(
            'SELECT column_name FROM information_schema.columns WHERE table_name = $1',
            ['code_laws']
        );

        console.log('New fields successfully added to tables!');
        console.log('RNC Articles columns:', rncColumns.map(c => c.column_name));
        console.log('Code Laws columns:', codeColumns.map(c => c.column_name));

    } catch (error) {
        console.error('Error:', error);
        process.exit(1);
    } finally {
        await pool.end();
    }
}

main();
