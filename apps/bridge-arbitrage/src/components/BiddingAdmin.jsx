import React, { useState, useEffect } from 'react';
import { supabase } from '../supabase';
import DocumentAdmin from './DocumentAdmin';
import FileUploader from './FileUploader';

const BiddingAdmin = () => {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [categoryContent, setCategoryContent] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const { data, error } = await supabase
        .from('bidding_categories')
        .select('*')
        .order('number', { ascending: true });

      if (error) throw error;
      setCategories(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCategoryEdit = (category) => {
    setSelectedCategory(category);
    setCategoryContent(category.content);
    setEditMode(true);
  };

  const handleCategoryUpdate = async () => {
    if (!selectedCategory || !categoryContent) return;

    try {
      setUploading(true);
      const { error } = await supabase
        .from('bidding_categories')
        .update({ content: categoryContent })
        .eq('id', selectedCategory.id);

      if (error) throw error;

      // Refresh categories
      await fetchCategories();
      setEditMode(false);
      setSelectedCategory(null);
      setCategoryContent('');
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleFileUpload = async (url) => {
    try {
      setUploading(true);
      // TODO: Implement PDF parsing and category update logic
      console.log('File uploaded:', url);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bidding-admin">
      <DocumentAdmin
        documentType="bidding"
        title="Gestion des versions des Catégories de Paris"
      />

      <div className="file-upload-section">
        <h3>Uploader un nouveau document</h3>
        <FileUploader onUpload={handleFileUpload} />
      </div>

      <div className="categories-section">
        <h3>Catégories</h3>
        <div className="categories-list">
          {categories.map((category) => (
            <div key={category.id} className="category-item">
              <div className="category-header">
                <h4>{category.title}</h4>
                <button
                  onClick={() => handleCategoryEdit(category)}
                  disabled={uploading}
                >
                  Éditer
                </button>
              </div>
              <p>{category.content.substring(0, 100)}...</p>
            </div>
          ))}
        </div>
      </div>

      {editMode && (
        <div className="category-editor">
          <h3>Éditer la catégorie</h3>
          <textarea
            value={categoryContent}
            onChange={(e) => setCategoryContent(e.target.value)}
            rows={10}
            placeholder="Contenu de la catégorie..."
          />
          <div className="editor-buttons">
            <button
              onClick={handleCategoryUpdate}
              disabled={uploading || !categoryContent}
            >
              {uploading ? 'En cours...' : 'Mettre à jour'}
            </button>
            <button
              onClick={() => {
                setEditMode(false);
                setSelectedCategory(null);
                setCategoryContent('');
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

export default BiddingAdmin;
