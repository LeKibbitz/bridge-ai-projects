import React from 'react';

function LawDetail({ law, onBack, allLaws, onNavigateToLaw }) {
  const currentIndex = allLaws.findIndex(l => l.id === law.id);
  const previousLaw = currentIndex > 0 ? allLaws[currentIndex - 1] : null;
  const nextLaw = currentIndex < allLaws.length - 1 ? allLaws[currentIndex + 1] : null;

  return (
    <div>
      {/* Bouton retour et navigation */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px', flexWrap: 'wrap', gap: '10px' }}>
        <button onClick={onBack} className="back-button">
          ← Retour à la liste
        </button>
        
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {previousLaw && (
            <button
              onClick={() => onNavigateToLaw(previousLaw)}
              style={{
                padding: '8px 16px',
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = '#5a6268';
                e.target.style.transform = 'translateY(-1px)';
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = '#6c757d';
                e.target.style.transform = 'translateY(0)';
              }}
            >
              ← Loi {previousLaw.law_number}
            </button>
          )}
          {nextLaw && (
            <button
              onClick={() => onNavigateToLaw(nextLaw)}
              style={{
                padding: '8px 16px',
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = '#5a6268';
                e.target.style.transform = 'translateY(-1px)';
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = '#6c757d';
                e.target.style.transform = 'translateY(0)';
              }}
            >
              Loi {nextLaw.law_number} →
            </button>
          )}
        </div>
      </div>

      {/* Contenu de la loi */}
      <div style={{ 
        backgroundColor: 'white', 
        padding: '30px', 
        borderRadius: '12px', 
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        border: '1px solid #e1e8ed'
      }}>
        <h1 style={{ 
          color: '#2c3e50', 
          marginBottom: '20px',
          fontSize: '2rem',
          fontWeight: '300',
          lineHeight: '1.3'
        }}>
          Loi {law.law_number} - {law.title}
        </h1>
        
        <div style={{ 
          display: 'flex', 
          gap: '20px', 
          marginBottom: '25px',
          padding: '15px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          flexWrap: 'wrap'
        }}>
          <p style={{ margin: 0, color: '#666' }}>
            <strong>Page:</strong> {law.page}
          </p>
          {law.section && (
            <p style={{ margin: 0, color: '#666' }}>
              <strong>Section:</strong> {law.section}
            </p>
          )}
          {law.subsection && (
            <p style={{ margin: 0, color: '#666' }}>
              <strong>Sous-section:</strong> {law.subsection}
            </p>
          )}
        </div>
        
        <div style={{ 
          marginBottom: '30px', 
          whiteSpace: 'pre-wrap', 
          lineHeight: '1.8',
          fontSize: '16px',
          color: '#333'
        }}>
          {law.content}
        </div>
        
        {law.keywords && (
          <div style={{ 
            marginTop: '30px', 
            padding: '20px', 
            backgroundColor: '#f8f9fa', 
            borderRadius: '8px',
            border: '1px solid #e1e8ed'
          }}>
            <h4 style={{ marginBottom: '15px', color: '#2c3e50' }}>Mots-clés:</h4>
            <div>
              {law.keywords.split(',').map((keyword, index) => (
                <span key={index} className="keyword-tag" style={{ marginRight: '8px', marginBottom: '8px' }}>
                  {keyword.trim()}
                </span>
              ))}
            </div>
          </div>
        )}

        {law.law_references && (
          <div style={{ 
            marginTop: '30px', 
            padding: '20px', 
            backgroundColor: '#e8f5e8', 
            borderRadius: '8px',
            border: '1px solid #c8e6c9'
          }}>
            <h4 style={{ marginBottom: '15px', color: '#2e7d32' }}>Références:</h4>
            <p style={{ margin: 0, color: '#2e7d32', lineHeight: '1.6' }}>
              {law.law_references}
            </p>
          </div>
        )}

        {/* Navigation entre les lois */}
        {(previousLaw || nextLaw) && (
          <div style={{ 
            marginTop: '30px', 
            padding: '20px', 
            backgroundColor: '#e3f2fd', 
            borderRadius: '8px',
            border: '1px solid #bbdefb'
          }}>
            <h4 style={{ marginBottom: '15px', color: '#1976d2' }}>Navigation:</h4>
            <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
              {previousLaw && (
                <button
                  onClick={() => onNavigateToLaw(previousLaw)}
                  style={{
                    padding: '10px 16px',
                    backgroundColor: '#2196f3',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    transition: 'all 0.2s ease',
                    flex: '1',
                    minWidth: '200px'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = '#1976d2';
                    e.target.style.transform = 'translateY(-1px)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = '#2196f3';
                    e.target.style.transform = 'translateY(0)';
                  }}
                >
                  ← Loi {previousLaw.law_number}: {previousLaw.title}
                </button>
              )}
              {nextLaw && (
                <button
                  onClick={() => onNavigateToLaw(nextLaw)}
                  style={{
                    padding: '10px 16px',
                    backgroundColor: '#2196f3',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    transition: 'all 0.2s ease',
                    flex: '1',
                    minWidth: '200px'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = '#1976d2';
                    e.target.style.transform = 'translateY(-1px)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = '#2196f3';
                    e.target.style.transform = 'translateY(0)';
                  }}
                >
                  Loi {nextLaw.law_number}: {nextLaw.title} →
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default LawDetail;
