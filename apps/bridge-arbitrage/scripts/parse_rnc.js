const fs = require('fs');
const pdf = require('pdf-parse');
const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://aqokcjsmajnpfkladubp.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzOTg4OTUsImV4cCI6MjA2Njk3NDg5NX0.f2Z4aRkTlUExrpir4fqIpn0TkzpS5B0WPuAHAb26YFM';
const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Read the PDF file
const pdfPath = './public/Upload/RNC 2025-2026.pdf'; // Using real RNC file

// Helper functions
const parseArticleNumber = (text) => {
  const match = text.match(/Article\s+(\d+(?:\.\d+)*)/);
  return match ? match[1] : null;
};

const parseLawNumber = (text) => {
  const match = text.match(/Loi\s+(\d+-\d+)/);
  return match ? match[1] : null;
};

const extractReferences = (content) => {
  const articleRefs = content.match(/Article\s+\d+(?:\.\d+)*/g) || [];
  const lawRefs = content.match(/Loi\s+\d+-\d+/g) || [];
  return {
    articles: articleRefs.map(ref => ({
      number: ref.replace('Article ', ''),
      type: 'article',
      relationship: 'references'
    })),
    laws: lawRefs.map(ref => ({
      number: ref.replace('Loi ', ''),
      type: 'law',
      relationship: 'references'
    }))
  };
};

async function parsePDF() {
  try {
    console.log('Starting PDF parsing...');
    
    // Read and parse the PDF
    // Parse pages 11-13 (PDF pages 10-12) - This should contain actual content
    const data = await pdf(fs.readFileSync(pdfPath), {
      start: 10,  // Page 11
      end: 12     // Page 13
    });
    const text = data.text;
    
    console.log('Raw text extracted from PDF:');
    console.log(text);
    
    // Split text into sections using more precise patterns
    const sections = text.split(/\n\n/).filter(section => 
      // Skip empty sections
      section.trim() && 
      // Include only sections that look like actual content
      (section.match(/^TITRE\s+\d+/) || 
       section.match(/^Chapitre\s+\d+/) || 
       section.match(/^Section\s+\d+/) || 
       section.match(/^Article\s+\d+\.\d+/) || 
       // Include paragraphs that look like article content
       section.trim().length > 50)
    );
    
    console.log(`\nFound ${sections.length} valid sections in PDF`);
    console.log('First few sections:', sections.slice(0, 5));
    
    // Initialize variables for hierarchy
    let currentTitle = null;
    let currentChapter = null;
    let currentSection = null;
    let orderInTitle = 0;
    let orderInChapter = 0;
    
    // Process each section
    for (const section of sections) {
      console.log(`\nProcessing section: ${section}`);
      
      // Handle Titles
      if (section.match(/^Titre\s+\d+/)) {
        console.log('Found Title');
        currentTitle = section;
        orderInTitle++;
        orderInChapter = 0;
        
        const titleNumber = section.match(/\d+/)?.[0];
        console.log(`Title number: ${titleNumber}`);
        
        const article = {
          title_number: titleNumber,
          title_name: section,
          is_title: true,
          order_in_title: orderInTitle,
          content: '',
          pdf_path: pdfPath
        };
        
        console.log('Saving title article...');
        const { data: titleData, error: titleError } = await supabase
          .from('rnc_articles')
          .insert([article])
          .select();

        if (titleError) throw titleError;
        currentArticle = titleData[0];
        console.log('Title saved successfully');
        
      } else if (section.match(/^Chapitre\s+\d+/)) {
        console.log('Found Chapter');
        currentChapter = section;
        orderInChapter++;
        
        const chapterNumber = section.match(/\d+/)?.[0];
        console.log(`Chapter number: ${chapterNumber}`);
        
        const article = {
          title_number: currentTitle?.match(/\d+/)?.[0],
          chapter_number: chapterNumber,
          chapter_name: section,
          is_chapter: true,
          order_in_chapter: orderInChapter,
          order_in_title: orderInTitle,
          content: '',
          pdf_path: pdfPath,
          parent_article_id: currentArticle?.id
        };
        
        console.log('Saving chapter article...');
        const { data: chapterData, error: chapterError } = await supabase
          .from('rnc_articles')
          .insert([article])
          .select();

        if (chapterError) throw chapterError;
        currentArticle = chapterData[0];
        console.log('Chapter saved successfully');
        
      } else if (section.match(/^Section\s+\d+/)) {
        console.log('Found Section');
        currentSection = section;
        
        const article = {
          title_number: currentTitle?.match(/\d+/)?.[0],
          chapter_number: currentChapter?.match(/\d+/)?.[0],
          section_number: section.match(/\d+/)?.[0],
          section_title: section,
          is_section: true,
          order_in_chapter: orderInChapter,
          order_in_title: orderInTitle,
          content: '',
          pdf_path: pdfPath,
          parent_article_id: currentArticle?.id
        };
        
        console.log('Saving section article...');
        const { data: sectionData, error: sectionError } = await supabase
          .from('rnc_articles')
          .insert([article])
          .select();

        if (sectionError) throw sectionError;
        currentArticle = sectionData[0];
        console.log('Section saved successfully');
        
      } else if (section.match(/^Article\s+\d+\.\d+/)) {
        console.log('Found Article');
        const articleNumber = section.match(/Article\s+(\d+\.\d+)/)?.[1];
        const [title, content] = section.split(/\n/);
        
        console.log(`Article number: ${articleNumber}`);
        console.log(`Content: ${content}`);
        
        const article = {
          title_number: currentTitle?.match(/\d+/)?.[0],
          chapter_number: currentChapter?.match(/\d+/)?.[0],
          section_number: currentSection?.match(/\d+/)?.[0],
          article_number: articleNumber,
          title_name: title,
          content: content.trim(),
          pdf_path: pdfPath,
          order_in_chapter: orderInChapter,
          order_in_title: orderInTitle,
          parent_article_id: currentArticle?.id
        };
        
        console.log('Saving article...');
        const { data: articleData, error: articleError } = await supabase
          .from('rnc_articles')
          .insert([article])
          .select();

        if (articleError) throw articleError;
        
        // Verify the article was inserted
        const { data: verifyData } = await supabase
          .from('rnc_articles')
          .select('id, article_number, title_name, content')
          .eq('article_number', article.article_number)
          .single();

        if (verifyData) {
          console.log(`\nVerified article ${article.article_number} saved successfully:`);
          console.log('ID:', verifyData.id);
          console.log('Title:', verifyData.title_name);
          console.log('Content:', verifyData.content.substring(0, 100) + '...');
        } else {
          console.log(`\nWarning: Could not verify article ${article.article_number} in database`);
        }

        if (articleError) throw articleError;
        currentArticle = articleData[0];
        console.log('Article saved successfully');
        
        // Extract references
        const refs = extractReferences(content);
        console.log('Found references:', refs);
        
        // Create article relationships
        for (const ref of refs.articles) {
          console.log(`Processing article reference: ${ref.number}`);
          const relationship = {
            parent_article_id: articleData[0].id,
            child_article_id: (await supabase
              .from('rnc_articles')
              .select('id')
              .eq('article_number', ref.number)
              .single())?.data?.id,
            relationship_type: 'references',
            description: `Reference to Article ${ref.number}`
          };
          
          console.log('Saving article relationship...');
          await supabase.from('rnc_article_relationships').insert([relationship]);
          
          // Verify relationship
          const { data: relVerifyData } = await supabase
            .from('rnc_article_relationships')
            .select('id, parent_article_id, child_article_id, relationship_type')
            .eq('parent_article_id', articleData[0].id)
            .eq('child_article_id', relationship.child_article_id)
            .eq('relationship_type', 'references')
            .single();

          if (relVerifyData) {
            console.log(`\nVerified relationship ${articleNumber} -> ${refNumber} saved successfully`);
          } else {
            console.log(`\nWarning: Could not verify relationship ${articleNumber} -> ${refNumber} in database`);
          }
          
          console.log('Article relationship saved successfully');
        }
        
        // Create law relationships
        for (const ref of refs.laws) {
          console.log(`Processing law reference: ${ref.number}`);
          const lawRelationship = {
            article_id: articleData[0].id,
            law_id: (await supabase
              .from('code_laws')
              .select('id')
              .eq('law_number', ref.number)
              .single())?.data?.id,
            relationship_type: 'references',
            description: `Reference to Loi ${ref.number}`
          };
          
          console.log('Saving law relationship...');
          await supabase.from('article_law_relationships').insert([lawRelationship]);
          
          // Verify law relationship
          const { data: lawRelVerifyData } = await supabase
            .from('article_law_relationships')
            .select('id, article_id, law_id, relationship_type')
            .eq('article_id', articleData[0].id)
            .eq('law_id', lawRelationship.law_id)
            .eq('relationship_type', 'references')
            .single();

          if (lawRelVerifyData) {
            console.log(`\nVerified law relationship ${articleNumber} -> ${ref.number} saved successfully`);
          } else {
            console.log(`\nWarning: Could not verify law relationship ${articleNumber} -> ${ref.number} in database`);
          }
          
          console.log('Law relationship saved successfully');
        }
      }
    }
    
    console.log('\nParsing completed successfully!');
  } catch (error) {
    console.error('Error parsing PDF:', error);
  }
}

// Run the parser
parsePDF();
