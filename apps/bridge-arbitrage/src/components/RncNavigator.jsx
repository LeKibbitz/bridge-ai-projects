import React, { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient';
import './RncNavigator.css';
import ArticleLinker from './ArticleLinker';
import './ArticleLinker.css';
import './BugReportModal.css';

// Constants for keyboard shortcuts
const SHORTCUTS = {
  FOCUS_SEARCH: 'f',
  PREV_ARTICLE: 'ArrowLeft',
  NEXT_ARTICLE: 'ArrowRight',
  CLOSE_MODAL: 'Escape',
  SCROLL_UP: 'PageUp',
  SCROLL_DOWN: 'PageDown',
  FIRST_ARTICLE: 'Home',
  LAST_ARTICLE: 'End',
  OPEN_PDF: 'p'
};

// Helper function to parse article references
const parseReferences = (text) => {
  const referenceRegex = /(?:Art\.\s*|Article\s*|Loi\s*|Law\s*)\d+(?:\.\d+)?/g;
  const matches = text.match(referenceRegex) || [];
  return matches.map(match => match.trim());
};

// Helper function to get article hierarchy
const getArticleHierarchy = (article) => {
  const parts = [];
  
  if (article.title_number) parts.push(`TITRE ${article.title_number}`);
  if (article.chapter_number) parts.push(`Chapitre ${article.chapter_number}`);
  if (article.article_number) parts.push(`Article ${article.article_number}`);
  
  return parts;
};

const RncNavigator = () => {
  const [articles, setArticles] = useState([]);
  const [currentArticle, setCurrentArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [breadcrumbs, setBreadcrumbs] = useState([]);
  const [focusedArticle, setFocusedArticle] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredArticles, setFilteredArticles] = useState([]);
  const [pdfViewerOpen, setPdfViewerOpen] = useState(false);
  const [currentPdfPath, setCurrentPdfPath] = useState('');

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Prevent default behavior for modifier keys
      if (event.ctrlKey || event.metaKey) {
        if (event.key.toLowerCase() === SHORTCUTS.FOCUS_SEARCH) {
          event.preventDefault();
          const searchInput = document.querySelector('.search-container input');
          if (searchInput) {
            searchInput.focus();
          }
        } else if (event.key.toLowerCase() === SHORTCUTS.OPEN_PDF && currentArticle?.pdf_path) {
          event.preventDefault();
          openPdfViewer(currentArticle.pdf_path);
        }
        return;
      }

      // Handle regular keyboard shortcuts
      if (event.key === SHORTCUTS.CLOSE_MODAL) {
        if (currentArticle) {
          closeArticle();
        } else {
          setSearchTerm('');
        }
      }
      
      if (currentArticle) {
        if (event.key === SHORTCUTS.PREV_ARTICLE) {
          const prev = filteredArticles.find(a => 
            a.id < currentArticle.id && 
            getArticleHierarchy(a).join('.') === getArticleHierarchy(currentArticle).join('.')
          );
          if (prev) openArticle(prev);
        }
        if (event.key === SHORTCUTS.NEXT_ARTICLE) {
          const next = filteredArticles.find(a => 
            a.id > currentArticle.id && 
            getArticleHierarchy(a).join('.') === getArticleHierarchy(currentArticle).join('.')
          );
          if (next) openArticle(next);
        }
      }

      // Handle scrolling shortcuts
      if (event.key === SHORTCUTS.SCROLL_UP) {
        window.scrollBy(0, -window.innerHeight);
      }
      if (event.key === SHORTCUTS.SCROLL_DOWN) {
        window.scrollBy(0, window.innerHeight);
      }

      // Handle navigation to first/last article
      if (event.key === SHORTCUTS.FIRST_ARTICLE) {
        const first = filteredArticles[0];
        if (first) openArticle(first);
      }
      if (event.key === SHORTCUTS.LAST_ARTICLE) {
        const last = filteredArticles[filteredArticles.length - 1];
        if (last) openArticle(last);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentArticle, filteredArticles]);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const { data, error } = await supabase
          .from('rnc_articles')
          .select('*')
          .order('title_number', { ascending: true })
          .order('chapter_number', { ascending: true })
          .order('article_number', { ascending: true });

        if (error) {
          throw error;
        }
        
        if (!data || data.length === 0) {
          throw new Error('Aucun article trouvé dans la base de données');
        }

        setArticles(data);
        setFilteredArticles(data);
      } catch (err) {
        setError(err.message || 'Une erreur est survenue lors du chargement des articles');
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  const openArticle = async (article) => {
    setCurrentArticle(article);
    const hierarchy = await getArticleHierarchy(article);
    setBreadcrumbs(hierarchy);
    setFocusedArticle(article);
  };

  const closeArticle = () => {
    setCurrentArticle(null);
    setBreadcrumbs([]);
    setFocusedArticle(null);
    setPdfViewerOpen(false);
  };

  const openPdfViewer = (pdfPath) => {
    setCurrentPdfPath(pdfPath);
    setPdfViewerOpen(true);
  };

  const closePdfViewer = () => {
    setPdfViewerOpen(false);
    setCurrentPdfPath('');
  };

  const handleReferenceClick = (reference) => {
    const article = articles.find(a => 
      parseReferences(a.title).includes(reference) || 
      parseReferences(a.content).includes(reference)
    );
    if (article) {
      openArticle(article);
    }
  };

  const formatContent = (content) => {
    if (!content) return '';
    
    const references = parseReferences(content);
    let formatted = content;
    
    references.forEach(ref => {
      const escapedRef = ref.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      formatted = formatted.replace(
        new RegExp(escapedRef, 'g'),
        `<span class="reference" onclick="handleReferenceClick('${ref}')">${ref}</span>`
      );
    });
    
    return formatted;
  };

  return (
    <div className="rnc-navigator" role="application" tabIndex="0">
      {loading && (
        <div className="loading-container">
          <div className="loading-spinner">
            <div></div>
            <div></div>
            <div></div>
            <div></div>
          </div>
          <p>Chargement en cours...</p>
        </div>
      )}

      <div className="search-container">
        <input
          type="text"
          placeholder="Rechercher dans les articles..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            const term = e.target.value.toLowerCase();
            setFilteredArticles(
              articles.filter(article => 
                article.title?.toLowerCase().includes(term) ||
                article.content?.toLowerCase().includes(term) ||
                article.article_number?.toLowerCase().includes(term)
              )
            );
          }}
        />
      </div>

      <div className="articles-list">
        {filteredArticles.map((article) => (
          <div
            key={article.id}
            className={`article-item ${article.id === currentArticle?.id ? 'active' : ''}`}
            onClick={() => openArticle(article)}
            role="listitem"
            aria-label={`Article ${article.article_number} - ${article.title}`}
            aria-expanded={currentArticle?.id === article.id ? 'true' : 'false'}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                openArticle(article);
              }
            }}
            tabIndex={focusedArticle === article.id ? 0 : -1}
            ref={(el) => {
              if (el && focusedArticle === article.id) {
                el.focus();
              }
            }}
          >
            <div className="article-hierarchy">
              {article.pdf_path && (
                <span className="pdf-icon" title="PDF disponible">
                  📄
                </span>
              )}
              {getArticleHierarchy(article).map((part, index) => (
                <span key={index} className="hierarchy-part">
                  {part}
                  {index < getArticleHierarchy(article).length - 1 && ' > '}
                </span>
              ))}
            </div>
            <div className="article-header">
              <h2 className="article-title">
                {article.title}
              </h2>
              <div className="article-navigation">
                <button
                  className="nav-button"
                  onClick={() => {
                    const prev = articles.find(a => 
                      a.id < currentArticle.id && 
                      getArticleHierarchy(a).join('.') === getArticleHierarchy(currentArticle).join('.')
                    );
                    if (prev) openArticle(prev);
                  }}
                >
                  ← Article précédent
                </button>
                <button
                  className="nav-button"
                  onClick={() => {
                    const next = articles.find(a => 
                      a.id > currentArticle.id && 
                      getArticleHierarchy(a).join('.') === getArticleHierarchy(currentArticle).join('.')
                    );
                    if (next) openArticle(next);
                  }}
                >
                  Article suivant →
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Article Content */}
      {currentArticle && (
        <div className="article-content">
          <ArticleLinker 
            content={currentArticle.content} 
            articleType="rnc" 
            articleId={currentArticle.id} 
          />
        </div>
      )}

      {/* PDF Viewer */}
      {pdfViewerOpen && (
        <div className="pdf-viewer">
          <div className="pdf-overlay" onClick={closePdfViewer} />
          <div className="pdf-container">
            <button 
              className="close-pdf" 
              onClick={closePdfViewer}
              aria-label="Fermer le PDF"
            >
              ×
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default RncNavigator;
