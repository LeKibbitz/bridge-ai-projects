const fs = require('fs');
const pdf = require('pdf-parse');
const { supabase } = require('../../src/supabaseClient');

// Read the PDF file
const pdfPath = '../My Code and RNC suggestions/RNC 2025-2026.pdf';

async function parsePDF() {
  try {
    console.log('Reading PDF file...');
    const data = await pdf(fs.readFileSync(pdfPath));
    const text = data.text;
    
    console.log('Processing PDF content...');
    // Split text into sections
    const sections = text.split(/\n\n/);
    
    // Initialize variables for hierarchy
    let currentTitle = null;
    let currentChapter = null;
    let currentSection = null;
    let currentArticle = null;
    let orderInTitle = 0;
    let orderInChapter = 0;
    let titleNumber = null;
    let titleName = null;
    let chapterNumber = null;
    let chapterName = null;
    
    // Process each section
    for (const section of sections) {
      if (!section.trim()) continue;
      
      // Handle Titles
      const titleMatch = section.match(/^TITRE\s+(\d+)\s+(.+)/);
      if (titleMatch) {
        console.log(`Found Title: ${titleMatch[2]}`);
        currentTitle = titleMatch[2];
        orderInTitle++;
        orderInChapter = 0;
        
        titleNumber = titleMatch[1];
        titleName = titleMatch[2];
        
        const { data: titleData, error: titleError } = await supabase
          .from('rnc_article')
          .insert([{
            title_number: titleNumber,
            title_name: titleName,
            is_title: true,
            order_in_title: orderInTitle,
            content: '',
            pdf_path: pdfPath,
            created_by: 'system',
            updated_by: 'system'
          }])
          .select();

        if (titleError) throw titleError;
        console.log(`Inserted Title ${titleNumber}: ${titleName}`);
        currentArticle = titleData[0];
        
      } else if (currentTitle) {
        // Handle Chapters
        const chapterMatch = section.match(/^Chapitre\s+(\d+)\s*:\s*(.+)/);
        if (chapterMatch) {
          console.log(`Found Chapter: ${chapterMatch[2]}`);
          currentChapter = chapterMatch[2];
          orderInChapter++;
              .eq('article_number', refNumber)
              .single())?.data?.id,
            relationship_type: 'references',
            description: `Reference to ${ref}`
          };
          
          await supabase.from('rnc_article_relationships').insert([relationship]);
        }
        
        // Extract law references
        const lawReferences = content.match(/Loi\s+\d+/g) || [];
        for (const lawRef of lawReferences) {
          const lawNumber = lawRef.replace('Loi ', '');
          const lawRelationship = {
            article_id: articleData[0].id,
            law_id: (await supabase
              .from('code_laws')
              .select('id')
              .eq('law_number', lawNumber)
              .single())?.data?.id,
            relationship_type: 'references',
            description: `Reference to ${lawRef}`
          };
          
          await supabase.from('article_law_relationships').insert([lawRelationship]);
        }
      }
    }
    
    console.log('RNC articles parsed and inserted successfully!');
  } catch (error) {
    console.error('Error parsing RNC:', error);
  }
}

parsePDF();
