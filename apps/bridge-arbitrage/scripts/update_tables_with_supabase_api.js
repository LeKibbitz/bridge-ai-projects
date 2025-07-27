const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));
const fs = require('fs');
const path = require('path');

const supabaseUrl = 'https://aqokcjsmajnpfkladubp.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzOTg4OTUsImV4cCI6MjA2Njk3NDg5NX0.f2Z4aRkTlUExrpir4fqIpn0TkzpS5B0WPuAHAb26YFM';

async function executeSql(sql) {
    const response = await fetch(`${supabaseUrl}/rest/v1/rpc/execute_sql`, {
        method: 'POST',
        headers: {
            'apikey': supabaseKey,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ sql })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(`Error executing SQL: ${error.message}`);
    }

    return response.json();
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

        console.log('All operations completed successfully!');

    } catch (error) {
        console.error('Error:', error);
        process.exit(1);
    }
}

main();
