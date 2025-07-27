const { PDFDocument } = require('pdf-lib');
const fs = require('fs').promises;
const path = require('path');
const supabase = require('./supabase'); // Assuming you have a supabase client setup

const PDF_PATH = path.join(__dirname, '../public/Upload/RPI Nov 2021.pdf');
const VERSION = '2021-11';

async function parseRPI() {
  try {
    // Read the PDF
    const pdfBytes = await fs.readFile(PDF_PATH);
    const pdfDoc = await PDFDocument.load(pdfBytes);
    const pages = pdfDoc.getPageCount();

    // Define patterns and hierarchy levels
    const patterns = {
      mainTitle: /^[A-Z]+$/i,
      subTitle: /^(PATTON SUISSE|ARBITRAGE)$/i,
      section: /^(\d+\.)$/i,
      subSection: /^(\d+\.\d+)$/i,
      article: /^(\d+\.)$/i,
      subArticle: /^(\d+\.\d+)$/i,
      subSubArticle: /^[a-z]\)$/i,
      organization: /^CONSEILS D'ORGANISATION$/i
    };

    // Current hierarchy state
    let currentMainTitle = null;
    let currentSubTitle = null;
    let currentSection = null;
    let currentSubSection = null;
    let currentArticle = null;
    let currentSubArticle = null;
    let currentSubSubArticle = null;
    
    // Content storage
    let currentContent = '';
    let articles = [];

    // First, get or create the document version
    const { data: version, error: versionError } = await supabase
      .from('document_versions')
      .select('id')
      .eq('version', VERSION)
      .single();

    if (versionError) {
      console.error('Error fetching document version:', versionError);
      return;
    }

    // If version doesn't exist, create it
    if (!version) {
      const { data: newVersion, error: createError } = await supabase
        .from('document_versions')
        .insert({
          version: VERSION,
          document_type: 'RPI',
          effective_date: new Date('2021-11-01'),
          notes: 'Initial RPI document version'
        })
        .select()
        .single();

      if (createError) {
        console.error('Error creating document version:', createError);
        return;
      }
      version = newVersion;
    }

    // Process each page
    for (let i = 0; i < pages; i++) {
      const page = pdfDoc.getPage(i);
      const text = await page.getText();
      
      // Process text content
      const lines = text.split('\n').map(line => line.trim());

      for (const line of lines) {
        // Skip page numbers and empty lines
        if (!line || line.match(/\d+$/)) continue;

        // Detect main title (all caps)
        if (patterns.mainTitle.test(line)) {
          if (currentContent) {
            await saveCurrentArticle(version.id);
          }
          currentMainTitle = line;
          currentSubTitle = null;
          currentSection = null;
          currentSubSection = null;
          currentArticle = null;
          currentSubArticle = null;
          currentSubSubArticle = null;
          continue;
        }

        // Detect sub-title (like PATTON SUISSE, ARBITRAGE)
        if (patterns.subTitle.test(line)) {
          if (currentContent) {
            await saveCurrentArticle(version.id);
          }
          currentSubTitle = line;
          currentSection = null;
          currentSubSection = null;
          currentArticle = null;
          currentSubArticle = null;
          currentSubSubArticle = null;
          continue;
        }

        // Special case for CONSEILS D'ORGANISATION
        if (patterns.organization.test(line)) {
          if (currentContent) {
            await saveCurrentArticle(version.id);
          }
          currentSubTitle = line;
          continue;
        }

        // Detect section (with dot)
        if (patterns.section.test(line)) {
          if (currentContent) {
            await saveCurrentArticle(version.id);
          }
          currentSection = line;
          currentSubSection = null;
          currentArticle = null;
          currentSubArticle = null;
          currentSubSubArticle = null;
          continue;
        }

        // Detect sub-section (without dot)
        if (patterns.subSection.test(line)) {
          if (currentContent) {
            await saveCurrentArticle(version.id);
          }
          currentSubSection = line;
          currentArticle = null;
          currentSubArticle = null;
          currentSubSubArticle = null;
          continue;
        }

        // Detect article (with dot)
        if (patterns.article.test(line)) {
          if (currentContent) {
            await saveCurrentArticle(version.id);
          }
          currentArticle = line;
          currentSubArticle = null;
          currentSubSubArticle = null;
          continue;
        }

        // Detect sub-article (without dot)
        if (patterns.subArticle.test(line)) {
          if (currentContent) {
            await saveCurrentArticle(version.id);
          }
          currentSubArticle = line;
          currentSubSubArticle = null;
          continue;
        }

        // Detect sub-sub-article (like a), b))
        if (patterns.subSubArticle.test(line)) {
          if (currentContent) {
            await saveCurrentArticle(version.id);
          }
          currentSubSubArticle = line;
          continue;
        }

        // Add content to current article
        if (currentContent !== null) {
          currentContent += '\n' + line;
        }
      }
    }

    // Save the last article if any
    if (currentContent) {
      await saveCurrentArticle(version.id);
    }

    console.log(`Parsed articles have been saved to database`);

  } catch (error) {
    console.error('Error parsing RPI:', error);
  }
}

async function saveCurrentArticle(versionId) {
  if (!currentContent) return;

  const article = {
    document_version_id: versionId,
    main_title: currentMainTitle,
    sub_title: currentSubTitle,
    section_number: currentSection,
    sub_section_number: currentSubSection,
    article_number: currentArticle,
    sub_article_number: currentSubArticle,
    sub_sub_article: currentSubSubArticle,
    content: currentContent.trim()
  };

  const { error } = await supabase
    .from('rpi_articles')
    .insert(article);

  if (error) {
    console.error('Error saving article:', error);
  }

  currentContent = '';
}

parseRPI();

// Remove these lines since we already declared PDF_PATH at the top of the file

async function parseRPI() {
  try {
    // Read the PDF
    const pdfBytes = await fs.readFile(PDF_PATH);
    const pdfDoc = await PDFDocument.load(pdfBytes);
    const pages = pdfDoc.getPageCount();

    // Define patterns for different levels
    const patterns = {
      mainSection: /^(PATTON SUISSE|ARBITRAGE)/i,
      subSection: /^(ORGANISATION|FORFAIT|DÉROULEMENT|INCOMPATIBILITÉ|REGLEMENT)/i,
      article: /^(UN SEUL|DEUX|MATCHS|MOUVEMENT|CONSEILS|PROGRAMMES|COMMISSION)/i
    };

    let currentMainSection = null;
    let currentSubSection = null;
    let currentArticle = null;
    let articles = [];

    // Process each page
    for (let i = 0; i < pages; i++) {
      const page = pdfDoc.getPage(i);
      const text = await page.getText();
      
      // Process text content
      const lines = text.split('\n').map(line => line.trim());

      for (const line of lines) {
        // Skip page numbers and empty lines
        if (!line || line.match(/\d+$/)) continue;

        // Detect main section
        if (patterns.mainSection.test(line)) {
          currentMainSection = line;
          currentSubSection = null;
          currentArticle = null;
          continue;
        }

        // Detect sub-section
        if (patterns.subSection.test(line)) {
          currentSubSection = line;
          currentArticle = null;
          continue;
        }

        // Detect article
        if (patterns.article.test(line)) {
          currentArticle = line;
          
          // Store the article with proper hierarchy
          articles.push({
            main_section: currentMainSection,
            sub_section: currentSubSection,
            article_title: currentArticle,
            content: ''
          });
          continue;
        }

        // Add content to current article
        if (currentArticle) {
          const lastArticle = articles[articles.length - 1];
          lastArticle.content += '\n' + line;
        }
      }
    }

    // Remove these lines since we already declared these variables earlier

    // Process each page
    for (let i = 0; i < pages; i++) {
      const page = pdfDoc.getPage(i);
      const text = await page.getText();
      
      // Process text content
      const lines = text.split('\n').map(line => line.trim());
      
      for (const line of lines) {
        // Detect title (e.g., "TITRE I")
        const titleMatch = line.match(/TITRE\s+(\d+)/i);
        if (titleMatch) {
          currentTitle = titleMatch[1];
          currentChapter = null;
          currentArticle = null;
          continue;
        }

        // Detect chapter (e.g., "CHAPITRE I")
        const chapterMatch = line.match(/CHAPITRE\s+(\d+)/i);
        if (chapterMatch) {
          currentChapter = chapterMatch[1];
          currentArticle = null;
          continue;
        }

        // Detect article (e.g., "ARTICLE 1")
        const articleMatch = line.match(/ARTICLE\s+(\d+)/i);
        if (articleMatch) {
          currentArticle = articleMatch[1];
          
          // Store the article
          articles.push({
            title_number: currentTitle,
            chapter_number: currentChapter,
            article_number: currentArticle,
            title: line,
            content: ''
          });
          continue;
        }

        // Add content to current article
        if (currentArticle) {
          const lastArticle = articles[articles.length - 1];
          lastArticle.content += '\n' + line;
        }
      }
    }

    // Save the parsed data
    const organizedData = {
      main_sections: articles.reduce((acc, article) => {
        const mainSection = article.main_section;
        if (!acc[mainSection]) {
          acc[mainSection] = [];
        }
        acc[mainSection].push(article);
        return acc;
      }, {})
    };

    await fs.writeFile(OUTPUT_PATH, JSON.stringify(organizedData, null, 2));

    console.log(`Parsed ${articles.length} articles from RPI`);

  } catch (error) {
    console.error('Error parsing RPI:', error);
  }
}

parseRPI();
