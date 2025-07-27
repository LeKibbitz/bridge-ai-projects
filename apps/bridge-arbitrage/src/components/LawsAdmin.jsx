import React, { useState, useEffect } from 'react';
import { supabase } from '../supabase';
import DocumentAdmin from './DocumentAdmin';
import FileUploader from './FileUploader';

const LawsAdmin = () => {
  const [laws, setLaws] = useState([]);
  const [selectedLaw, setSelectedLaw] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [lawContent, setLawContent] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLaws();
  }, []);

  const fetchLaws = async () => {
    try {
      const { data, error } = await supabase
        .from('laws')
        .select('*')
        .order('number', { ascending: true });

      if (error) throw error;
      setLaws(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleLawEdit = (law) => {
    setSelectedLaw(law);
    setLawContent(law.content);
    setEditMode(true);
  };

  const handleLawUpdate = async () => {
    if (!selectedLaw || !lawContent) return;

    try {
      setUploading(true);
      const { error } = await supabase
        .from('laws')
        .update({ content: lawContent })
        .eq('id', selectedLaw.id);

      if (error) throw error;

      // Refresh laws
      await fetchLaws();
      setEditMode(false);
      setSelectedLaw(null);
      setLawContent('');
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleFileUpload = async (url) => {
    try {
      setUploading(true);
      // TODO: Implement PDF parsing and law update logic
      console.log('File uploaded:', url);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="laws-admin">
      <DocumentAdmin
        documentType="laws"
        title="Gestion du Code International"
      />

      <div className="file-upload-section">
        <h3>Uploader un nouveau document</h3>
        <FileUploader onUpload={handleFileUpload} />
      </div>

      <div className="laws-section">
        <h3>Articles</h3>
        <div className="laws-list">
          {laws.map((law) => (
            <div key={law.id} className="law-item">
              <div className="law-header">
                <h4>{law.title}</h4>
                <button
                  onClick={() => handleLawEdit(law)}
                  disabled={uploading}
                >
                  Éditer
                </button>
              </div>
              <p>{law.content.substring(0, 100)}...</p>
            </div>
          ))}
        </div>
      </div>

      {editMode && (
        <div className="law-editor">
          <h3>Éditer l'article</h3>
          <textarea
            value={lawContent}
            onChange={(e) => setLawContent(e.target.value)}
            rows={10}
            placeholder="Contenu de l'article..."
          />
          <div className="editor-buttons">
            <button
              onClick={handleLawUpdate}
              disabled={uploading || !lawContent}
            >
              {uploading ? 'En cours...' : 'Mettre à jour'}
            </button>
            <button
              onClick={() => {
                setEditMode(false);
                setSelectedLaw(null);
                setLawContent('');
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

export default LawsAdmin;
