import React, { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient';

const CodeLaws = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [laws, setLaws] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLaws = async () => {
      try {
        const { data, error } = await supabase
          .from('code_laws')
          .select('*');

        if (error) {
          throw error;
        }
        setLaws(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchLaws();
  }, []);

  const filteredLaws = laws.filter(law => {
    const term = searchTerm.toLowerCase();
    return (
      (law.title && law.title.toLowerCase().includes(term)) ||
      (law.law_number && law.law_number.toString().includes(term)) ||
      (law.content && law.content.toLowerCase().includes(term))
    );
  });

  return (
    <div>
      {loading && <p>Chargement des lois...</p>}
      {error && <p style={{ color: 'red' }}>Erreur: {error}</p>}
      
      {/* Espacement identique au RNC entre la ligne de séparation et la barre de recherche */}
      <div style={{ margin: '20px 0' }}>
        <input
          type="text"
          placeholder="Rechercher une loi par mot-clé, titre ou numéro..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ 
            padding: '8px 12px', 
            width: '100%', 
            borderRadius: '8px', 
            border: '1px solid #ddd',
            fontSize: '14px',
            boxSizing: 'border-box'
          }}
        />
      </div>

      <div>
        {!loading && (
          <>
            {filteredLaws.map((law) => (
              <div
                key={law.id}
                style={{
                  marginBottom: '10px',
                  padding: '8px 12px',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  backgroundColor: '#fff',
                  transition: 'transform 0.2s',
                }}
                onMouseOver={e => e.currentTarget.style.transform = 'scale(1.02)'}
                onMouseOut={e => e.currentTarget.style.transform = 'scale(1)'}
              >
                <h4 style={{ margin: '0', fontSize: '16px', color: '#2c3e50' }}>
                  Loi {law.law_number} - {law.title || 'Sans titre'}
                </h4>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
};

export default CodeLaws;

