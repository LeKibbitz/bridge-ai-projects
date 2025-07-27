import React, { useState } from 'react';
import { supabase } from '../supabaseClient';
import { useAuth } from '../context/AuthContext';
import BugReportModal from './BugReportModal';
import './BiddingStyles.css';

// Styles for bidding conventions
const biddingStyles = {
  category1: 'font-normal text-base',
  default: 'font-normal text-base'
};

const ArticleLinker = ({ content, articleType = 'rnc', articleId }) => {
  const { user } = useAuth();
  const [showBugReport, setShowBugReport] = useState(false);
  const [selectedReference, setSelectedReference] = useState(null);

  // Enhanced reference detection patterns
  const referencePatterns = [
    // Article references
    { pattern: /(?:Art\\.|Article|Loi|Law)\\s*(\\d+(?:\\.\\d+)?)\\b/gi, type: 'article' },
    // Section references
    { pattern: /(?:Sect\\.|Section)\\s*(\\d+(?:\\.\\d+)?)\\b/gi, type: 'section' },
    // Chapter references
    { pattern: /(?:Chap\\.|Chapter)\\s*(\\d+(?:\\.\\d+)?)\\b/gi, type: 'chapter' },
    // Title references
    { pattern: /(?:Titre|Title)\\s*(\\d+(?:\\.\\d+)?)\\b/gi, type: 'title' },
    // Part references
    { pattern: /(?:Part\\.|Partie)\\s*(\\d+(?:\\.\\d+)?)\\b/gi, type: 'part' }
  ];

  const articleTypes = {
    rnc: 'rnc_articles',
    code: 'laws',
    rpi: 'rpi_articles'
  };

  const createLink = async (match, number, type) => {
    try {
      // Search for matching article based on type
      const { data: article, error } = await supabase
        .from(articleTypes[articleType])
        .select('id, title, article_number')
        .or(`article_number.eq.${number},title.ilike.%${number}%,section_number.eq.${number},chapter_number.eq.${number},title_number.eq.${number}`)
        .single();

      if (error) throw error;

      // If article found, create a link
      if (article) {
        return `<a href="#/${articleType}/${article.id}" 
          class="article-link"
          data-reference="${match}"
          data-type="${type}"
          data-id="${article.id}"
          title="Cliquez pour voir l'article">
          ${match}
        </a>`;
      }

      // If not found, create a broken link that can be reported
      return `<a href="#" 
          class="article-link broken-link"
          data-reference="${match}"
          data-type="${type}"
          onClick={(e) => {
            e.preventDefault();
            setSelectedReference(match);
            setShowBugReport(true);
          }}
          title="Référence non trouvée - Cliquez pour signaler un problème">
          ${match}
        </a>`;
    } catch (err) {
      console.error('Error creating link:', err);
      return match;
    }
  };

  const processContent = async () => {
    let processedContent = content;
    
    // Handle bidding conventions styling
    processedContent = processedContent.replace(/Autorisé en catégorie 1/g, '<span class="bidding-category-1">Autorisé en catégorie 1</span>');
    processedContent = processedContent.replace(/Autorisées en catégorie 1 et 2 des CI/g, '<span class="bidding-category-1">Autorisées en catégorie 1 et 2 des CI</span>');
    
    // Handle SHA card styling
    processedContent = processedContent.replace(/SHA/g, '<div class="sha-card"><div class="sha-card-header">SHA</div>');
    
    // Handle content styling
    processedContent = processedContent.replace(/Autorisé en catégorie 1/g, '<span style="color: #28a745;">Autorisé en catégorie 1</span>');
    processedContent = processedContent.replace(/Autorisées en catégorie 1 et 2 des CI/g, '<span>Autorisées en catégorie 1 et 2 des CI</span>');
    
    // Add line breaks
    processedContent = processedContent.replace(/Autorisé en catégorie 1/g, '<span style="color: #28a745;">Autorisé en catégorie 1</span><br/>');
    processedContent = processedContent.replace(/Autorisées en catégorie 1 et 2 des CI/g, '<span>Autorisées en catégorie 1 et 2 des CI</span><br/>');
    
    // Close the SHA card div
    processedContent = processedContent.replace(/SHA/g, '</div>');

    // Process all reference patterns
    for (const { pattern, type } of referencePatterns) {
      let match;
      while ((match = pattern.exec(content)) !== null) {
        const link = await createLink(match[0], match[1], type);
        processedContent = processedContent.replace(match[0], link);
      }
    }

    return processedContent;
  };

  // Process content on mount
  const [processedContent, setProcessedContent] = React.useState(content);
  React.useEffect(() => {
    processContent().then(result => setProcessedContent(result));
  }, [content]);

  return (
    <div className="article-content">
      <style>
        {`
          .bidding-category-1 {
            font-family: inherit;
            font-size: 1rem;
            font-weight: normal;
          }
        `}
      </style>
      <div
        dangerouslySetInnerHTML={{ __html: processedContent }}
      />
      {showBugReport && user && (
        <BugReportModal
          isOpen={showBugReport}
          onClose={() => setShowBugReport(false)}
          articleType={articleType}
          articleId={articleId}
          referenceText={selectedReference}
          user={user}
        />
      )}
    </div>
  );
};

export default ArticleLinker;
