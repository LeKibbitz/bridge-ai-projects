import React, { useState, useEffect } from 'react';
import { supabase } from '../supabase';
import DocumentAdmin from './DocumentAdmin';
import FileUploader from './FileUploader';

const RncAdmin = () => {
  const [articles, setArticles] = useState([]);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [articleContent, setArticleContent] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchArticles();
  }, []);

  const fetchArticles = async () => {
    try {
      const { data, error } = await supabase
        .from('rnc_articles')
        .select('*')
        .order('title_number', { ascending: true });

      if (error) throw error;
      setArticles(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleArticleEdit = (article) => {
    setSelectedArticle(article);
    setArticleContent(article.content);
    setEditMode(true);
  };

  const handleArticleUpdate = async () => {
    if (!selectedArticle || !articleContent) return;

    try {
      setUploading(true);
      const { error } = await supabase
        .from('rnc_articles')
        .update({ content: articleContent })
        .eq('id', selectedArticle.id);

      if (error) throw error;

      // Refresh articles
      await fetchArticles();
      setEditMode(false);
      setSelectedArticle(null);
      setArticleContent('');
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleFileUpload = async (url) => {
    try {
      setUploading(true);
      // TODO: Implement PDF parsing and article update logic
      console.log('File uploaded:', url);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="rnc-admin">
      <DocumentAdmin
        documentType="RNC"
        title="Gestion des versions RNC"
      />

      <div className="file-upload-section">
        <h3>Uploader un nouveau document</h3>
        <FileUploader onUpload={handleFileUpload} />
      </div>

      <div className="articles-section">
        <h3>Articles</h3>
        <div className="articles-list">
          {articles.map((article) => (
            <div key={article.id} className="article-item">
              <div className="article-header">
                <h4>{article.title}</h4>
                <button
                  onClick={() => handleArticleEdit(article)}
                  disabled={uploading}
                >
                  Éditer
                </button>
              </div>
              <p>{article.content.substring(0, 100)}...</p>
            </div>
          ))}
        </div>
      </div>

      {editMode && (
        <div className="article-editor">
          <h3>Éditer l'article</h3>
          <textarea
            value={articleContent}
            onChange={(e) => setArticleContent(e.target.value)}
            rows={10}
            placeholder="Contenu de l'article..."
          />
          <div className="editor-buttons">
            <button
              onClick={handleArticleUpdate}
              disabled={uploading || !articleContent}
            >
              {uploading ? 'En cours...' : 'Mettre à jour'}
            </button>
            <button
              onClick={() => {
                setEditMode(false);
                setSelectedArticle(null);
                setArticleContent('');
              }}
            >
              Annuler
            </button>
          </div>
        </div>
      )}

      {error && <div className="error">{error}</div>}
    </div>
  );
};

export default RncAdmin;
