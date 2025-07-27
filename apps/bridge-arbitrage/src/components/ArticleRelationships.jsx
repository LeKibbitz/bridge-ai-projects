import React, { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient';

const ArticleRelationships = ({ articleId, articleType }) => {
  const [relationships, setRelationships] = useState([]);
  const [newRelationship, setNewRelationship] = useState({
    targetType: '',
    targetId: '',
    relationshipType: 'related',
    notes: ''
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRelationships();
  }, [articleId, articleType]);

  const fetchRelationships = async () => {
    try {
      const { data, error } = await supabase
        .from('article_relationships_view')
        .select('*')
        .eq('source_type', articleType)
        .eq('source_id', articleId)
        .order('created_at', { ascending: false });

      if (error) throw error;
      setRelationships(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (term) => {
    if (!term) {
      setSearchResults([]);
      return;
    }

    try {
      // Search in both RNC and Code articles
      const { data: rncResults, error: rncError } = await supabase
        .from('rnc_articles')
        .select('id, title, article_number')
        .or(`title.ilike.%${term}%,article_number.ilike.%${term}%`)
        .limit(10);

      const { data: codeResults, error: codeError } = await supabase
        .from('laws')
        .select('id, title, article_number')
        .or(`title.ilike.%${term}%,article_number.ilike.%${term}%`)
        .limit(10);

      if (rncError || codeError) throw rncError || codeError;

      const results = [
        ...rncResults.map(item => ({
          ...item,
          type: 'rnc'
        })),
        ...codeResults.map(item => ({
          ...item,
          type: 'code'
        }))
      ];

      setSearchResults(results);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleAddRelationship = async () => {
    if (!newRelationship.targetType || !newRelationship.targetId) return;

    try {
      const { error } = await supabase
        .from('article_relationships')
        .insert({
          source_type: articleType,
          source_id: articleId,
          target_type: newRelationship.targetType,
          target_id: newRelationship.targetId,
          relationship_type: newRelationship.relationshipType,
          notes: newRelationship.notes
        });

      if (error) throw error;

      // Reset form
      setNewRelationship({
        targetType: '',
        targetId: '',
        relationshipType: 'related',
        notes: ''
      });
      setSearchTerm('');
      setSearchResults([]);

      // Refresh relationships
      await fetchRelationships();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteRelationship = async (id) => {
    try {
      const { error } = await supabase
        .from('article_relationships')
        .delete()
        .eq('id', id);

      if (error) throw error;
      
      // Refresh relationships
      await fetchRelationships();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="article-relationships">
      <h3>Relations avec d'autres articles</h3>

      {error && <div className="error">{error}</div>}

      <div className="relationship-form">
        <div className="form-group">
          <label>Rechercher un article:</label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              handleSearch(e.target.value);
            }}
            placeholder="Rechercher dans RNC et Code..."
          />
        </div>

        <div className="form-group">
          <label>Type de relation:</label>
          <select
            value={newRelationship.relationshipType}
            onChange={(e) => {
              setNewRelationship(prev => ({
                ...prev,
                relationshipType: e.target.value
              }));
            }}
          >
            <option value="related">Articles liés</option>
            <option value="example">Exemple</option>
            <option value="reference">Référence</option>
            <option value="clarification">Clarification</option>
            <option value="exception">Exception</option>
            <option value="superseded">Remplacé par</option>
            <option value="amended">Modifié par</option>
          </select>
        </div>

        <div className="form-group">
          <label>Notes:</label>
          <textarea
            value={newRelationship.notes}
            onChange={(e) => {
              setNewRelationship(prev => ({
                ...prev,
                notes: e.target.value
              }));
            }}
            placeholder="Notes sur cette relation..."
          />
        </div>

        <button
          onClick={handleAddRelationship}
          disabled={!newRelationship.targetType || !newRelationship.targetId}
        >
          Ajouter la relation
        </button>
      </div>

      {searchResults.length > 0 && (
        <div className="search-results">
          <h4>Résultats de recherche:</h4>
          <ul>
            {searchResults.map((result) => (
              <li
                key={result.id}
                onClick={() => {
                  setNewRelationship(prev => ({
                    ...prev,
                    targetType: result.type,
                    targetId: result.id
                  }));
                }}
                className={
                  newRelationship.targetType === result.type &&
                  newRelationship.targetId === result.id
                    ? 'selected'
                    : ''
                }
              >
                {result.type === 'rnc' ? 'RNC' : 'Code'}: {result.title} {result.article_number}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="relationships-list">
        <h4>Relations existantes:</h4>
        <table>
          <thead>
            <tr>
              <th>Type</th>
              <th>Article lié</th>
              <th>Relation</th>
              <th>Notes</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {relationships.map((relationship) => (
              <tr key={relationship.id}>
                <td>{relationship.target_type === 'rnc' ? 'RNC' : 'Code'}</td>
                <td>{relationship.target_title}</td>
                <td>{relationship.relationship_description}</td>
                <td>{relationship.notes}</td>
                <td>
                  <button
                    onClick={() => handleDeleteRelationship(relationship.id)}
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

export default ArticleRelationships;
