const { DocumentParser, DOCUMENT_TYPES } = require('./parse_documents.js');

async function main() {
    try {
        const filePath = 'public/Upload/RNC 2025-2026.pdf';
        console.log(`Starting to parse RNC document: ${filePath}`);
        const parser = new DocumentParser(DOCUMENT_TYPES.RNC);
        await parser.parsePDF(filePath);
        console.log('Parsing completed successfully');
    } catch (error) {
        console.error('Error during parsing:', error);
        process.exit(1);
    }
}

main();
