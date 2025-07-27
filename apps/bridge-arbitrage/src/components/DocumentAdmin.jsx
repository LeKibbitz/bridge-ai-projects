import React, { useState } from 'react';
import { supabase } from '../supabase';

const DocumentAdmin = ({ documentType, title }) => {
  const [versions, setVersions] = useState([]);
  const [newVersion, setNewVersion] = useState('');
  const [newNotes, setNewNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchVersions = async () => {
    try {
      const { data, error } = await supabase
        .from('document_versions')
        .select('*')
        .eq('document_type', documentType)
        .order('effective_date', { ascending: false });

      if (error) throw error;
      setVersions(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCreateVersion = async () => {
    if (!newVersion) return;

    try {
      setLoading(true);
      const { error } = await supabase
        .from('document_versions')
        .insert({
          version: newVersion,
          document_type: documentType,
          effective_date: new Date(),
          notes: newNotes
        });

      if (error) throw error;
      
      // Reset form
      setNewVersion('');
      setNewNotes('');
      
      // Refresh versions
      await fetchVersions();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteVersion = async (versionId) => {
    try {
      setLoading(true);
      const { error } = await supabase
        .from('document_versions')
        .delete()
        .eq('id', versionId);

      if (error) throw error;
      
      // Refresh versions
      await fetchVersions();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="document-admin">
      <h2>{title}</h2>

      {error && <div className="error">{error}</div>}

      <div className="version-form">
        <h3>Nouvelle version</h3>
        <div className="form-group">
          <label>Numéro de version:</label>
          <input
            type="text"
            value={newVersion}
            onChange={(e) => setNewVersion(e.target.value)}
            placeholder={`Ex: 2021-11`}
          />
        </div>
        <div className="form-group">
          <label>Notes:</label>
          <textarea
            value={newNotes}
            onChange={(e) => setNewNotes(e.target.value)}
            placeholder={`Notes sur cette version...`}
          />
        </div>
        <button
          onClick={handleCreateVersion}
          disabled={loading || !newVersion}
        >
          {loading ? 'En cours...' : 'Créer version'}
        </button>
      </div>

      <div className="versions-list">
        <h3>Versions existantes</h3>
        <table>
          <thead>
            <tr>
              <th>Version</th>
              <th>Date effective</th>
              <th>Notes</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {versions.map((version) => (
              <tr key={version.id}>
                <td>{version.version}</td>
                <td>{new Date(version.effective_date).toLocaleDateString()}</td>
                <td>{version.notes}</td>
                <td>
                  <button
                    onClick={() => handleDeleteVersion(version.id)}
                    disabled={loading}
                  >
                    Supprimer
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DocumentAdmin;
