const { supabase } = require('../src/supabaseClient');
const pdf = require('pdf-parse');
const fs = require('fs');
const path = require('path');

// Configuration
const PDF_DIR = path.join(__dirname, '../public/Upload/My Code and RNC suggestions');

// Get all PDF files in the directory
const PDF_FILES = fs.readdirSync(PDF_DIR)
    .filter(file => file.toLowerCase().endsWith('.pdf'))
    .sort();

async function parsePDF(filePath) {
    const data = await pdf(fs.readFileSync(filePath));
    return data.text;
}

async function insertRNCArticle(article) {
    try {
        const { error } = await supabase
            .from('rnc_articles')
            .insert([{
                title_number: article.title_number,
                title_name: article.title_name,
                chapter_number: article.chapter_number,
                chapter_name: article.chapter_name,
                section_number: article.section_number,
                section_name: article.section_name,
                article_number: article.article_number,
                article_name: article.article_name,
                content: article.content,
                hypertexte_link: article.hypertexte_link,
                created_by: 'system',
                updated_by: 'system'
            }]);

        if (error) throw error;
    } catch (error) {
        console.error('Error inserting RNC article:', error);
        throw error;
    }
}

async function insertCodeLaw(article) {
    try {
        const { error } = await supabase
            .from('code_laws')
            .insert([{
                title_number: article.title_number,
                title_name: article.title_name,
                chapter_number: article.chapter_number,
                chapter_name: article.chapter_name,
                article_number: article.article_number,
                article_name: article.article_name,
                content: article.content,
                hypertexte_link: article.hypertexte_link,
                created_by: 'system',
                updated_by: 'system'
            }]);

        if (error) throw error;
    } catch (error) {
        console.error('Error inserting Code Law:', error);
        throw error;
    }
}

async function parseDocument(text, isRNC) {
    const articles = [];
    let currentTitle = { number: null, name: null };
    let currentChapter = { number: null, name: null };
    let currentSection = { number: null, name: null };

    const lines = text.split('\n');
    let currentContent = '';
    let currentArticleNumber = null;
    let currentArticleName = null;

    console.log('Starting document parsing...');
    console.log(`Total lines: ${lines.length}`);

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();

        // Update progress
        process.stdout.clearLine();
        process.stdout.cursorTo(0);
        process.stdout.write(`Processing line ${i + 1}/${lines.length}...`);

        // Parse titles
        const titleMatch = line.match(/^TITRE\s+(\d+)\s+(.+)/);
        if (titleMatch) {
            currentTitle.number = titleMatch[1];
            currentTitle.name = titleMatch[2];
            console.log(`Found title: ${currentTitle.number} - ${currentTitle.name}`);
            continue;
        }

        // Parse chapters
        const chapterMatch = line.match(/^Chapitre\s+(\d+)\s*:\s*(.+)/);
        if (chapterMatch) {
            currentChapter.number = chapterMatch[1];
            currentChapter.name = chapterMatch[2];
            console.log(`Found chapter: ${currentChapter.number} - ${currentChapter.name}`);
            continue;
        }

        // Parse sections
        const sectionMatch = line.match(/^Section\s+(\d+)\s*:\s*(.+)/);
        if (sectionMatch) {
            currentSection.number = sectionMatch[1];
            currentSection.name = sectionMatch[2];
            console.log(`Found section: ${currentSection.number} - ${currentSection.name}`);
            continue;
        }

        // Parse articles
        const articleMatch = line.match(/Article\s+(\d+)\s*–\s*(.+)/);
        if (articleMatch) {
            if (currentContent.trim()) {
                // Save previous article
                const article = {
                    title_number: currentTitle.number || null,
                    title_name: currentTitle.name || null,
                    chapter_number: currentChapter.number || null,
                    chapter_name: currentChapter.name || null,
                    section_number: currentSection.number || null,
                    section_name: currentSection.name || null,
                    article_number: currentArticleNumber || null,
                    article_name: currentArticleName || null,
                    content: currentContent.trim() || '',
                    hypertexte_link: isRNC 
                        ? `/rnc/titre-${currentTitle.number || ''}/chapitre-${currentChapter.number || ''}${currentSection.number ? `/section-${currentSection.number}` : ''}/article-${currentArticleNumber || ''}`
                        : `/code/titre-${currentTitle.number || ''}/chapitre-${currentChapter.number || ''}/article-${currentArticleNumber || ''}`
                };
                articles.push(article);
                console.log(`Saved article: ${currentArticleNumber} - ${currentArticleName}`);
            }

            currentArticleNumber = articleMatch[1];
            currentArticleName = articleMatch[2];
            currentContent = '';
        } else {
            currentContent += line + '\n';
        }
    }

    // Save last article
    if (currentContent.trim()) {
        const article = {
            title_number: currentTitle.number || null,
            title_name: currentTitle.name || null,
            chapter_number: currentChapter.number || null,
            chapter_name: currentChapter.name || null,
            section_number: currentSection.number || null,
            section_name: currentSection.name || null,
            article_number: currentArticleNumber || null,
            article_name: currentArticleName || null,
            content: currentContent.trim() || '',
            hypertexte_link: isRNC 
                ? `/rnc/titre-${currentTitle.number || ''}/chapitre-${currentChapter.number || ''}${currentSection.number ? `/section-${currentSection.number}` : ''}/article-${currentArticleNumber || ''}`
                : `/code/titre-${currentTitle.number || ''}/chapitre-${currentChapter.number || ''}/article-${currentArticleNumber || ''}`
        };
        articles.push(article);
        console.log(`Saved last article: ${currentArticleNumber} - ${currentArticleName}`);
    }

    console.log(`\nFinished parsing document. Found ${articles.length} articles`);
    return articles;
}

async function processFile(filePath, isRNC) {
    console.log(`\nProcessing file: ${path.basename(filePath)}`);
    
    try {
        const text = await parsePDF(filePath);
        const articles = await parseDocument(text, isRNC);
        
        console.log(`\nFound ${articles.length} articles`);
        console.log('Starting article insertion...');
        
        for (let i = 0; i < articles.length; i++) {
            const article = articles[i];
            process.stdout.clearLine();
            process.stdout.cursorTo(0);
            process.stdout.write(`Inserting article ${i + 1}/${articles.length} (${article.article_number})...`);

            try {
                if (isRNC) {
                    await insertRNCArticle(article);
                } else {
                    await insertCodeLaw(article);
                }
            } catch (error) {
                console.error(`\nError inserting article ${article.article_number}: ${error.message}`);
                console.error('Article data:', article);
                throw error;
            }
        }

        console.log(`\nCompleted processing ${path.basename(filePath)}`);
    } catch (error) {
        console.error(`\nError processing file ${path.basename(filePath)}: ${error.message}`);
        throw error;
    }
}

async function executeSQL(sql) {
    try {
        // First check if tables exist
        const { data: rncData, error: rncError } = await supabase
            .from('rnc_articles')
            .select('id')
            .limit(1)
            .single();

        const { data: codeData, error: codeError } = await supabase
            .from('code_laws')
            .select('id')
            .limit(1)
            .single();

        // If either table doesn't exist, create them
        if (rncError || codeError) {
            console.log('Creating tables...');
            const statements = sql.split(';').filter(stmt => stmt.trim());
            for (const stmt of statements) {
                console.log('Executing statement:', stmt.trim());
                const { error: createError } = await supabase
                    .from('rnc_articles')
                    .select('*')
                    .limit(1);
                
                if (createError) {
                    console.error('Error creating tables:', createError);
                    throw createError;
                }
            }
        }
    } catch (error) {
        console.error('Error executing SQL:', error);
        throw error;
    }
}

async function main() {
    try {
        console.log('Starting document processing...');
        console.log(`Found ${PDF_FILES.length} PDF files to process`);
        console.log('Files to process:', PDF_FILES);
        
        // Read and execute the setup SQL file
        const sqlPath = path.join(__dirname, 'setup_tables.sql');
        const sql = fs.readFileSync(sqlPath, 'utf8');
        console.log('\nExecuting SQL setup...');
        await executeSQL(sql);
        console.log('SQL setup completed successfully');

        // Process files
        let totalArticles = 0;
        let totalFilesProcessed = 0;
        
        for (const file of PDF_FILES) {
            const filePath = path.join(PDF_DIR, file);
            const isRNC = file.includes('RNC');
            
            console.log('\n\n=== Processing file:', file, '===');
            console.log('Is RNC:', isRNC);
            
            try {
                const articles = await processFile(filePath, isRNC);
                totalFilesProcessed++;
                totalArticles += articles.length;
                console.log(`\nSuccessfully processed ${articles.length} articles from ${file}`);
            } catch (error) {
                console.error(`\nFailed to process file ${file}: ${error.message}`);
                console.error('Error details:', error);
                continue;
            }
        }

        console.log('\n\n=== Processing Summary ===');
        console.log(`Total files processed: ${totalFilesProcessed}/${PDF_FILES.length}`);
        console.log(`Total articles processed: ${totalArticles}`);
        console.log('All documents processed!');
    } catch (error) {
        console.error('\nFatal error during processing:', error);
        process.exit(1);
    }
}

main().catch(console.error);
