import React, { useState } from 'react';
import { supabase } from '../supabaseClient';
import { useAuth } from '../context/AuthContext';

const BugReportModal = ({ isOpen, onClose, articleType, articleId, referenceText, user }) => {
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('normal');
  const [attachment, setAttachment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const priorities = [
    { value: 'critical', label: 'Critique' },
    { value: 'high', label: 'Haute' },
    { value: 'normal', label: 'Normale' },
    { value: 'low', label: 'Basse' }
  ];

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (file) {
      setAttachment(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!description.trim()) {
      setError('Veuillez décrire le problème.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Create bug report
      const { data: bugReport, error: createError } = await supabase
        .from('bug_reports')
        .insert([
          {
            user_id: user.id,
            article_type: articleType,
            article_id: articleId,
            reference_text: referenceText,
            description,
            priority
          }
        ])
        .select()
        .single();

      if (createError) throw createError;

      // Upload attachment if present
      if (attachment) {
        const { error: uploadError } = await supabase.storage
          .from('bug_attachments')
          .upload(`bug_reports/${bugReport.id}/${attachment.name}`, attachment);

        if (uploadError) throw uploadError;

        // Create attachment record
        await supabase
          .from('bug_report_attachments')
          .insert([
            {
              bug_report_id: bugReport.id,
              file_path: `bug_reports/${bugReport.id}/${attachment.name}`,
              file_name: attachment.name,
              file_type: attachment.type
            }
          ]);
      }

      setSuccess(true);
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="bug-report-modal">
      <div className="modal-content">
        <h2>Signaler un problème</h2>
        
        {error && <div className="error">{error}</div>}
        {success && (
          <div className="success">
            <p>Merci pour votre retour ! Votre rapport a été soumis avec succès.</p>
          </div>
        )}

        {!success && (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Description du problème:</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Décrivez le problème que vous avez rencontré..."
                required
              />
            </div>

            <div className="form-group">
              <label>Priorité:</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                required
              >
                {priorities.map((p) => (
                  <option key={p.value} value={p.value}>{p.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Joindre un fichier (optionnel):</label>
              <input
                type="file"
                onChange={handleFileUpload}
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.gif"
              />
            </div>

            <div className="form-actions">
              <button
                type="button"
                onClick={onClose}
                className="secondary"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={loading}
              >
                {loading ? 'En cours...' : 'Envoyer le rapport'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default BugReportModal;
