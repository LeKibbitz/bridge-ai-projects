import React, { useState, useEffect } from 'react';
import { supabase } from '../supabase';
import RpiAdmin from './RpiAdmin';
import RncAdmin from './RncAdmin';
import BiddingAdmin from './BiddingAdmin';
import LawsAdmin from './LawsAdmin';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('rpi');
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      // Fetch all document versions
      const { data: versions, error: versionsError } = await supabase
        .from('document_versions')
        .select('*')
        .order('created_at', { ascending: false });

      if (versionsError) throw versionsError;
      
      // Group documents by type
      const grouped = versions.reduce((acc, version) => {
        if (!acc[version.document_type]) {
          acc[version.document_type] = [];
        }
        acc[version.document_type].push(version);
        return acc;
      }, {});

      setDocuments(grouped);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentTypeChange = (type) => {
    setActiveTab(type);
  };

  const renderAdminPanel = () => {
    switch (activeTab) {
      case 'rpi':
        return <RpiAdmin />;
      case 'rnc':
        return <RncAdmin />;
      case 'bidding':
        return <BiddingAdmin />;
      case 'laws':
        return <LawsAdmin />;
      default:
        return <RpiAdmin />;
    }
  };

  if (loading) {
    return <div className="loading">Chargement...</div>;
  }

  return (
    <div className="admin-dashboard">
      <h1>Administration des Documents</h1>

      {error && <div className="error">{error}</div>}

      <div className="document-types">
        <button
          className={activeTab === 'rpi' ? 'active' : ''}
          onClick={() => handleDocumentTypeChange('rpi')}
        >
          RPI
        </button>
        <button
          className={activeTab === 'rnc' ? 'active' : ''}
          onClick={() => handleDocumentTypeChange('rnc')}
        >
          RNC
        </button>
        <button
          className={activeTab === 'bidding' ? 'active' : ''}
          onClick={() => handleDocumentTypeChange('bidding')}
        >
          Catégories de Paris
        </button>
        <button
          className={activeTab === 'laws' ? 'active' : ''}
          onClick={() => handleDocumentTypeChange('laws')}
        >
          Code International
        </button>
      </div>

      <div className="admin-content">
        {renderAdminPanel()}
      </div>
    </div>
  );
};

export default AdminDashboard;
