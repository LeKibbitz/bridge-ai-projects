
import React, { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient';

const BiddingCategories = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);

  // Données statiques pour les descriptions des catégories
  const categoryDescriptions = {
    "1": "DIVISIONS NATIONALES PAR 4\nDivisions 1, 2, 3, 4",
    "2": "Toutes les divisions Expert/4\nInterclubs divisions 1 & 2\nMoins de 31 ans/4",
    "3": "Toutes les divisions Performance/4\nInterclubs Division 3\nLa coupe de France à partir des finales de zone\nToutes les Divisions Nationales/2\nToutes les divisions Expert/2\nMoins de 31 ans/2",
    "4": "La coupe de France au stade comité\nToutes les divisions Challenge/2 et /4\nToutes les divisions Performance/2\nL'interclubs Division 4\nLe Trophée de France\nLes tournois de régularité, les festivals et voyages-bridge",
    "5": "TOUTES LES DIVISIONS ESPÉRANCE\n(par paire et par quatre)\nInterclubs Division 5\nChampionnat Cadets et Scolaires (par 2 et par 4)",
    "SHA": "Autorisé en catégorie 1\n\nSeules les ouvertures au palier de 1 peuvent avoir des caractéristiques SHA.",
    "CI": "Autorisées en catégorie 1 et 2\n\nSeules les ouvertures de 2♣ à 3♠ inclus, les interventions sur les ouvertures au palier de 1 à la couleur et les enchères faibles au palier de 2 ou de 3 montrant une main bicolore dont une couleur peut n'être que de 3 cartes peuvent être classées CI."
  };

  // Fonction pour obtenir le titre d'affichage avec capitalisation correcte
  const getDisplayTitle = (documentType) => {
    if (documentType === 'SHA') {
      return 'Système Hautement Artificiel (SHA)';
    } else if (documentType === 'CI') {
      return 'Conventions Inhabituelles (CI)';
    } else {
      return `Catégorie ${documentType.replace('CAT', '')}`;
    }
  };

  const getPdfUrl = (documentType) => {
    if (documentType === 'SHA') {
      return '/upload/CATSHA.pdf#toolbar=0&navpanes=0&scrollbar=0';
    } else if (documentType === 'CI') {
      return '/upload/CATCI.pdf#toolbar=0&navpanes=0&scrollbar=0';
    } else {
      return `/upload/CAT${documentType.replace('CAT', '')}.pdf#toolbar=0&navpanes=0&scrollbar=0`;
    }
  };

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const { data, error } = await supabase
          .from('conventions_documents')
          .select('*')
          .order('document_type', { ascending: true });

        if (error) {
          throw error;
        }
        
        setDocuments(data || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, []);

  // Gestion de la touche Escape pour fermer le modal
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        closeModal();
      }
    };

    if (selectedDocument) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [selectedDocument]);

  const openModal = (doc) => {
    setSelectedDocument(doc);
    // Add keyboard event listener for Escape key
    document.addEventListener('keydown', handleKeyDown);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      closeModal();
    }
  };

  const closeModal = () => {
    setSelectedDocument(null);
    // Remove keyboard event listener when modal closes
    document.removeEventListener('keydown', handleKeyDown);
  };

  if (loading) {
    return <p>Chargement des documents...</p>;
  }

  if (error) {
    return <p style={{ color: 'red' }}>Erreur: {error}</p>;
  }

  return (
    <div style={{
      padding: '0',
      maxWidth: '100%',
      margin: '0 auto'
    }}>
      <div style={{ 
        display: 'flex',
        flexDirection: 'column',
        gap: '6px'
      }}>
        {documents.map(doc => (
          <div
            key={doc.id}
            style={{
              border: '1px solid #ddd',
              borderRadius: '8px',
              padding: '6px 12px',
              backgroundColor: 'white',
              display: 'flex',
              justifyContent: 'space-between',
              cursor: 'pointer',
              transition: 'transform 0.2s',
              position: 'relative'
            }}
            onClick={() => openModal(doc)}
            onMouseOver={e => e.currentTarget.style.transform = 'scale(1.02)'}
            onMouseOut={e => e.currentTarget.style.transform = 'scale(1)'}
          >
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column',
              gap: '12px', // Adjusted gap
              width: '100%',
              paddingRight: '20px',
              position: 'relative'
            }}>
              <div className="category-title" style={{ 
                fontSize: '14px',
                fontWeight: 'bold',
                color: '#2c3e50',
                textAlign: 'left',
                lineHeight: '1.2',
                margin: '0',
                padding: '0',
                letterSpacing: doc.document_type === 'SHA' ? '-0.03em' : '-0.02em'
              }}>
                {doc.document_type === 'SHA' ? (
                  <>
                    <span style={{ marginRight: '4px' }}>Système Hautement Artificiel</span>
                    <span style={{ color: '#2c3e50', fontSize: '14px', fontWeight: 'bold' }}>(SHA)</span>
                  </>
                ) : doc.document_type === 'CI' ? (
                  <>
                    <span style={{ marginRight: '4px' }}>Conventions Inhabituelles</span>
                    <span style={{ color: '#2c3e50', fontSize: '14px', fontWeight: 'bold' }}>(CI)</span>
                  </>
                ) : (
                  `Catégorie ${doc.document_type.replace('CAT', '')}`
                )}
              </div>
              <div style={{ 
                fontSize: '14px',
                fontWeight: 'bold',
                color: '#666666',
                textAlign: 'left',
                lineHeight: '1.2',
                margin: '0'
              }}>
                {doc.document_type === 'CI' ? (
                  <>
                    <div style={{ 
                      fontSize: '14px',
                      fontWeight: 'bold',
                      color: '#2e7d32',
                      textAlign: 'left',
                      lineHeight: '1.2',
                      margin: '0'
                    }}>
                      {categoryDescriptions[doc.document_type.replace('CAT', '')].split('\n\n')[0]}
                    </div>
                    <div style={{ 
                      fontSize: '14px',
                      fontWeight: 'bold',
                      color: '#666666',
                      textAlign: 'left',
                      lineHeight: '1.2',
                      margin: '0',
                      marginTop: '4px'
                    }}>
                      {categoryDescriptions[doc.document_type.replace('CAT', '')].split('\n\n')[1]}
                    </div>
                  </>
                ) : doc.document_type === 'SHA' ? (
                  <>
                    <div style={{ 
                      fontSize: '14px',
                      fontWeight: 'bold',
                      color: '#2e7d32',
                      textAlign: 'left',
                      lineHeight: '1.2',
                      margin: '0'
                    }}>
                      {categoryDescriptions[doc.document_type.replace('CAT', '')].split('\n\n')[0]}
                    </div>
                    <div style={{ 
                      fontSize: '14px',
                      fontWeight: 'bold',
                      color: '#666666',
                      textAlign: 'left',
                      lineHeight: '1.2',
                      margin: '0',
                      marginTop: '4px'
                    }}>
                      {categoryDescriptions[doc.document_type.replace('CAT', '')].split('\n\n')[1]}
                    </div>
                  </>
                ) : (
                  <div style={{ 
                    fontSize: '14px',
                    fontWeight: 'bold',
                    color: '#666666',
                    textAlign: 'left',
                    lineHeight: '1.2',
                    margin: '0'
                  }}>
                    {categoryDescriptions[doc.document_type.replace('CAT', '')] || `Compétitions de catégorie ${doc.document_type.replace('CAT', '')}`}
                  </div>
                )}
              </div>
              <span
                style={{
                  position: 'absolute',
                  top: '16px',
                  right: '0',
                  fontSize: '24px',
                  cursor: 'pointer',
                  transition: 'transform 0.2s',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#2563eb'
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.transform = 'scale(1.2)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.transform = 'scale(1)';
                }}
                title="Voir le détail"
              >
                🔍
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Modal PDF */}
      {selectedDocument && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'white',
          zIndex: 9999
        }}>
          {/* Bouton fermer en haut à droite */}
          <button 
            onClick={closeModal}
            style={{
              position: 'absolute',
              top: '10px',
              right: '10px',
              zIndex: 10000,
              background: 'rgba(0, 0, 0, 0.7)',
              color: 'white',
              border: 'none',
              borderRadius: '50%',
              width: '40px',
              height: '40px',
              fontSize: '20px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            ✕
          </button>
          
          {/* PDF */}
          <iframe
            src={getPdfUrl(selectedDocument.document_type)}
            style={{
              width: '100vw',
              height: '100vh',
              border: 'none',
              margin: 0,
              padding: 0
            }}
            title={getDisplayTitle(selectedDocument.document_type)}
            onError={(e) => {
              console.error('Erreur de chargement PDF:', e);
              // Essayer un chemin alternatif pour SHA
              if (selectedDocument.document_type === 'SHA') {
                e.target.src = '/upload/CAT.SHA.pdf';
              } else {
                e.target.src = `/upload/cat${selectedDocument.document_type.replace('CAT', '')}.pdf#toolbar=0&navpanes=0&scrollbar=0`;
              }
            }}
          />
        </div>
      )}
    </div>
  );
};

export default BiddingCategories;
