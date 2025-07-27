const fs = require('fs');
const path = require('path');
const pdfParse = require('pdf-parse');
const { createClient } = require('@supabase/supabase-js');
const config = require('./config');

// Supabase client configuration
const supabase = createClient(
    config.supabase.url,
    config.supabase.key,
    {
        auth: {
            persistSession: false,
            autoRefreshToken: false
        }
    }
);

// Status monitoring object
const status = {
    totalFiles: 0,
    processedFiles: 0,
    totalArticles: 0,
    processedArticles: 0,
    errors: [],
    startTime: new Date(),
    lastUpdate: new Date()
};

// Update status and log progress
function updateStatus(message) {
    status.lastUpdate = new Date();
    console.log(`\n${new Date().toISOString()} - ${message}`);
    console.log(`Progress: ${status.processedFiles}/${status.totalFiles} files, ${status.processedArticles}/${status.totalArticles} articles`);
    console.log(`Errors: ${status.errors.length}`);
}

// Parse a single document
async function parseDocument(filePath, isRNC) {
    try {
        const data = await pdfParse(fs.readFileSync(filePath));
        const text = data.text;
        return parseDocumentText(text, isRNC);
    } catch (error) {
        status.errors.push({
            file: path.basename(filePath),
            error: error.message,
            timestamp: new Date()
        });
        updateStatus(`Error parsing ${path.basename(filePath)}: ${error.message}`);
        throw error;
    }
}

async function parseDocumentText(text, isRNC) {
    const articles = [];
    let currentTitle = { number: null, name: null };
    let currentChapter = { number: null, name: null };
    let currentSection = { number: null, name: null };
    let currentContent = '';
    let currentArticleNumber = null;
    let currentArticleName = null;
    let currentPage = 1;
    let skipPages = isRNC ? 2 : 3;  // RNC skips 2 pages, Code skips 3 pages
    let hasSeenFirstPageMarker = false;

    try {
        const lines = text.split('\n');
        console.log(`\nStarting to parse document...`);
        console.log(`Total lines: ${lines.length}`);
        
        // Handle forewords on first two pages
        if (currentPage === 1) {
            const forewordContent = lines.slice(0, lines.length).join('\n');
            articles.push({
                title_number: isRNC ? '0' : null,
                title_name: 'Préambule',
                chapter_number: null,
                chapter_name: null,
                section_number: null,
                section_name: null,
                article_number: null,
                article_name: null,
                content: forewordContent.trim(),
                hypertexte_link: null
            });
            currentPage = 2;
            skipPages = isRNC ? 1 : 2; // Adjust skipPages since we've already processed page 1
        }

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Track page numbers
            const pageMatch = line.match(/Page\s+(\d+)/);
            if (pageMatch) {
                const pageNumber = parseInt(pageMatch[1]);
                if (pageNumber > currentPage) {
                    currentPage = pageNumber;
                    hasSeenFirstPageMarker = true;
                    console.log(`Found page ${pageNumber}`);
                }
            }

            // Skip lines until we reach the desired page
            if (skipPages > 0 && hasSeenFirstPageMarker) {
                skipPages--;
                continue;
            }

            // Update progress
            if (i % 100 === 0) {
                process.stdout.clearLine();
                process.stdout.cursorTo(0);
                process.stdout.write(`Processing line ${i + 1}/${lines.length}...`);
            }

            // Parse titles
            const titleMatch = line.match(/^titre\s+(\d+)\s+(.+)/i);
            if (titleMatch) {
                if (currentTitle.number !== null) {
                    // Save previous title if it exists
                    articles.push({
                        title_number: currentTitle.number,
                        title_name: currentTitle.name,
                        chapter_number: null,
                        chapter_name: null,
                        section_number: null,
                        section_name: null,
                        article_number: null,
                        article_name: null,
                        content: currentContent.trim() || null,  // Allow null content for titles
                        hypertexte_link: null
                    });
                    currentContent = '';
                }
                // Initialize with title 0 for RNC, or use the matched number for Code
                currentTitle.number = isRNC ? '0' : titleMatch[1];
                currentTitle.name = titleMatch[2];
                currentChapter = { number: null, name: null };
                currentSection = { number: null, name: null };
                console.log(`Found title: ${currentTitle.number} - ${currentTitle.name}`);
                continue;
            }

            // Parse chapters
            const chapterMatch = line.match(/^chapitre\s+(\d+)\s+(.+)/i);
            if (chapterMatch) {
                if (currentChapter.number !== null) {
                    // Save previous chapter if it exists
                    articles.push({
                        title_number: currentTitle.number,
                        title_name: currentTitle.name,
                        chapter_number: currentChapter.number,
                        chapter_name: currentChapter.name,
                        section_number: null,
                        section_name: null,
                        article_number: null,
                        article_name: null,
                        content: currentContent.trim(),
                        hypertexte_link: null
                    });
                    currentContent = '';
                }
                currentChapter.number = chapterMatch[1];
                currentChapter.name = chapterMatch[2];
                currentSection = { number: null, name: null };
                console.log(`Found chapter: ${currentChapter.number} - ${currentChapter.name}`);
                continue;
            }

            // Parse sections
            const sectionMatch = line.match(/^section\s+(\d+)\s+(.+)/i);
            if (sectionMatch) {
                if (currentSection.number !== null) {
                    // Save previous section if it exists
                    articles.push({
                        title_number: currentTitle.number,
                        title_name: currentTitle.name,
                        chapter_number: currentChapter.number,
                        chapter_name: currentChapter.name,
                        section_number: currentSection.number,
                        section_name: currentSection.name,
                        article_number: null,
                        article_name: null,
                        content: currentContent.trim(),
                        hypertexte_link: null
                    });
                    currentContent = '';
                }
                currentSection.number = sectionMatch[1];
                currentSection.name = sectionMatch[2];
                console.log(`Found section: ${currentSection.number} - ${currentSection.name}`);
                continue;
            }

            // Parse articles
            const articleMatch = line.match(/^article\s+(\d+)\s+(.+)/i);
            if (articleMatch) {
                if (currentArticleNumber !== null) {
                    // Save previous article
                    articles.push({
                        title_number: currentTitle.number,
                        title_name: currentTitle.name,
                        chapter_number: currentChapter.number,
                        chapter_name: currentChapter.name,
                        section_number: currentSection.number,
                        section_name: currentSection.name,
                        article_number: currentArticleNumber,
                        article_name: currentArticleName,
                        content: currentContent.trim(),
                        hypertexte_link: `https://www.legifrance.gouv.fr/jorf/article_jo/${currentArticleNumber}`
                    });
                    currentContent = '';
                }
                currentArticleNumber = articleMatch[1];
                currentArticleName = articleMatch[2];
                console.log(`Found article: ${currentArticleNumber} - ${currentArticleName}`);
                continue;
            }

            // Add content lines
            if (currentArticleNumber !== null) {
                currentContent += line + '\n';
            }
        }

        // Save last article
        if (currentArticleNumber !== null) {
            articles.push({
                title_number: currentTitle.number,
                title_name: currentTitle.name,
                chapter_number: currentChapter.number,
                chapter_name: currentChapter.name,
                section_number: currentSection.number,
                section_name: currentSection.name,
                article_number: currentArticleNumber,
                article_name: currentArticleName,
                content: currentContent.trim(),
                hypertexte_link: `https://www.legifrance.gouv.fr/jorf/article_jo/${currentArticleNumber}`
            });
        }

        console.log(`Finished parsing document. Found ${articles.length} articles.`);
        return articles;
    } catch (error) {
        status.errors.push({
            file: path.basename(filePath),
            error: error.message,
            timestamp: new Date()
        });
        updateStatus(`Error parsing ${path.basename(filePath)}: ${error.message}`);
        throw error;
    }
}

// Insert articles into database
async function insertArticles(articles, isRNC) {
    try {
        const tableName = isRNC ? 'rnc_articles' : 'code_laws';
        const insertData = articles.map(article => ({
            ...article,
            created_by: 'system',
            updated_by: 'system'
        }));

        const { error } = await supabase
            .from(tableName)
            .insert(insertData);

        if (error) {
            status.errors.push({
                error: error.message,
                timestamp: new Date()
            });
            updateStatus(`Error inserting articles into ${tableName}: ${error.message}`);
            throw error;
        }

        status.processedArticles += articles.length;
        updateStatus(`Successfully inserted ${articles.length} articles`);
    } catch (error) {
        status.errors.push({
            error: error.message,
            timestamp: new Date()
        });
        updateStatus(`Error processing articles: ${error.message}`);
        throw error;
    }
}

// Main processing function
async function processFiles() {
    try {
        // Process only the specific PDF files
        const UPLOAD_DIR = path.join(__dirname, '../public/Upload');
        const PDF_FILES = [
            'Code International 2017.pdf',
            'RNC 2025-2026.pdf'
        ].filter(file => fs.existsSync(path.join(UPLOAD_DIR, file)));

        status.totalFiles = PDF_FILES.length;
        updateStatus(`Found ${PDF_FILES.length} PDF files to process`);

        // Process each file
        for (const fileName of PDF_FILES) {
            const filePath = path.join(UPLOAD_DIR, fileName);
            const isRNC = fileName.toLowerCase().includes('rnc');

            try {
                // Parse document
                const articles = await parseDocument(filePath, isRNC);
                status.totalArticles += articles.length;

                // Insert articles
                await insertArticles(articles, isRNC);
                status.processedFiles++;
            } catch (error) {
                // Log error but continue processing
                status.errors.push({
                    file: fileName,
                    error: error.message,
                    timestamp: new Date()
                });
                updateStatus(`Error processing file ${fileName}: ${error.message}`);
                continue;
            }
        }

        // Final status
        updateStatus('=== Processing Summary ===');
        updateStatus(`Total files processed: ${status.processedFiles}/${status.totalFiles}`);
        updateStatus(`Total articles processed: ${status.processedArticles}/${status.totalArticles}`);
        updateStatus(`Total errors: ${status.errors.length}`);
        if (status.errors.length > 0) {
            updateStatus('=== Errors ===');
            status.errors.forEach((error, index) => {
                updateStatus(`${index + 1}. ${error.file || 'Unknown file'}: ${error.error}`);
            });
        }
    } catch (error) {
        // Log fatal error but continue processing
        status.errors.push({
            error: `Fatal error during processing: ${error.message}`,
            timestamp: new Date()
        });
        updateStatus(`Fatal error during processing: ${error.message}`);
    }
}

// Start processing
console.log('Starting document processing...');
processFiles().catch(error => {
    console.error('Processing failed:', error);
    process.exit(1);
});
