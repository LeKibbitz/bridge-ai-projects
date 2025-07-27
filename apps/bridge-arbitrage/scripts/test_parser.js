const parseDocuments = require('./parse_documents');
const { parseRNC, parseCodeLaws } = parseDocuments;
const fs = require('fs');
const path = require('path');
const pool = require('../config/database');
const pdfParse = require('pdf-parse');

// Make pdfParse available globally
const globalObject = global || window;
globalObject.pdfParse = pdfParse;

// Initialize database pool
pool.on('error', (err) => {
    console.error('Unexpected error on idle client', err);
    process.exit(-1);
});

async function testParser() {
    try {
        // Test RNC document
        console.log('\nTesting RNC document parsing...');
        const rncFilePath = path.join(__dirname, '../public/Upload/My Code and RNC suggestions/RNC 2025-2026.pdf');
        await parseRNC(rncFilePath);
        
        // Test Code Laws document
        console.log('\nTesting Code Laws document parsing...');
        const codeLawsFilePath = path.join(__dirname, '../public/Upload/My Code and RNC suggestions/Code International 2017.pdf');
        await parseCodeLaws(codeLawsFilePath);
        
        // Verify database content
        console.log('\nVerifying database content...');
        
        // Check RNC titles
        const { rows: titles } = await pool.query('SELECT * FROM rnc_titles ORDER BY title_number');
        console.log(`\nFound ${titles.length} RNC titles:`);
        titles.forEach(title => console.log(`- ${title.title_number}: ${title.title_name}`));
        
        // Check Code Laws articles
        const { rows: codeLaws } = await pool.query('SELECT * FROM code_laws ORDER BY article_number');
        console.log(`\nFound ${codeLaws.length} Code Laws articles:`);
        codeLaws.forEach(article => console.log(`- ${article.article_number}: ${article.article_name}`));
        
    } catch (error) {
        console.error('Error in test:', error);
        process.exit(1);
    } finally {
        // Close database connection
        await pool.end();
    }
}

// Run the test
testParser();
