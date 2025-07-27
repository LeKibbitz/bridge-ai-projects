const fs = require('fs');
const pdf = require('pdf-parse');
const { createClient } = require('../supabaseClient');

// Test data structure
const TEST_DATA = {
  // Sample RNC article structure
  articles: [
    {
      text: "TITRE I\nDISPOSITIONS GÉNÉRALES",
      type: 'title',
      expected: {
        title_number: 1,
        title_name: "DISPOSITIONS GÉNÉRALES"
      }
    },
    {
      text: "Chapitre I\nDU CONTRAT",
      type: 'chapter',
      expected: {
        chapter_number: 1,
        chapter_name: "DU CONTRAT"
      }
    },
    {
      text: "Article 1.1\nLe contrat de bridge est conclu entre deux équipes de deux joueurs chacune.",
      type: 'article',
      expected: {
        article_number: '1.1',
        content: "Le contrat de bridge est conclu entre deux équipes de deux joueurs chacune."
      }
    },
    {
      text: "Article 1.2\nArticle 1.1 est modifié par la Loi 2023-1234 du 15 janvier 2023.",
      type: 'article_with_references',
      expected: {
        article_number: '1.2',
        content: "Article 1.1 est modifié par la Loi 2023-1234 du 15 janvier 2023.",
        references: [
          { type: 'article', number: '1.1', relationship: 'references' },
          { type: 'law', number: '2023-1234', relationship: 'references' }
        ]
      }
    }
  ],
  
  // Test cases for different reference formats
  reference_patterns: [
    "Article 1.1",
    "Article 1.1.1",
    "Loi 2023-1234",
    "Loi 2023-1234 du 15 janvier 2023",
    "Article 1.1 est modifié par la Loi 2023-1234"
  ],
  
  // Test cases for hierarchical structure
  hierarchy: [
    "TITRE I",
    "Chapitre I",
    "Section 1",
    "Article 1.1",
    "Article 1.2",
    "Section 2",
    "Article 1.2.1"
  ]
};

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

// Test functions
const testArticleParsing = async () => {
  console.log('\nTesting Article Parsing...');
  
  for (const test of TEST_DATA.articles) {
    console.log(`\nTesting ${test.type}: ${test.text}`);
    
    // Parse article number
    const articleNumber = parseArticleNumber(test.text);
    if (test.expected.article_number) {
      console.log(`Article number: ${articleNumber}`);
    }
    
    // Parse law number
    const lawNumber = parseLawNumber(test.text);
    if (lawNumber) {
      console.log(`Law number: ${lawNumber}`);
    }
    
    // Extract references
    if (test.type === 'article_with_references') {
      const refs = extractReferences(test.text);
      console.log('References found:');
      console.log('Articles:', refs.articles);
      console.log('Laws:', refs.laws);
    }
  }
};

const testReferencePatterns = () => {
  console.log('\nTesting Reference Patterns...');
  
  for (const pattern of TEST_DATA.reference_patterns) {
    console.log(`\nTesting pattern: ${pattern}`);
    
    // Test article reference
    const articleNumber = parseArticleNumber(pattern);
    if (articleNumber) {
      console.log(`Found article number: ${articleNumber}`);
    }
    
    // Test law reference
    const lawNumber = parseLawNumber(pattern);
    if (lawNumber) {
      console.log(`Found law number: ${lawNumber}`);
    }
  }
};

const testHierarchy = () => {
  console.log('\nTesting Hierarchy...');
  
  const hierarchy = TEST_DATA.hierarchy;
  let currentTitle = null;
  let currentChapter = null;
  let currentSection = null;
  
  for (const item of hierarchy) {
    if (item.startsWith('TITRE')) {
      currentTitle = item;
      console.log(`Title: ${currentTitle}`);
    } else if (item.startsWith('Chapitre')) {
      currentChapter = item;
      console.log(`Chapter: ${currentChapter}`);
    } else if (item.startsWith('Section')) {
      currentSection = item;
      console.log(`Section: ${currentSection}`);
    } else if (item.startsWith('Article')) {
      console.log(`Article: ${item}`);
      console.log(`Hierarchy: ${currentTitle} -> ${currentChapter} -> ${currentSection}`);
    }
  }
};

// Main test function
const runTests = async () => {
  try {
    console.log('Starting RNC Parsing Tests...');
    
    // Test article parsing
    await testArticleParsing();
    
    // Test reference patterns
    testReferencePatterns();
    
    // Test hierarchy
    testHierarchy();
    
    console.log('\nAll tests completed!');
  } catch (error) {
    console.error('Test failed:', error);
  }
};

// Run tests
runTests();
