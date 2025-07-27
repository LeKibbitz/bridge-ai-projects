import React, { useState } from 'react';
import { supabase } from '../supabase';

const FileUploader = ({ onUpload }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    try {
      setUploading(true);
      const { error: uploadError } = await supabase.storage
        .from('documents')
        .upload(file.name, file);

      if (uploadError) throw uploadError;

      // Get the public URL
      const { data: { publicUrl } } = supabase.storage
        .from('documents')
        .getPublicUrl(file.name);

      // Notify parent component
      if (onUpload) {
        onUpload(publicUrl);
      }

      setFile(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="file-uploader">
      <div className="upload-area">
        <input
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={handleFileSelect}
          disabled={uploading}
        />
        {file && (
          <p>{file.name}</p>
        )}
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
        >
          {uploading ? 'En cours...' : 'Uploader'}
        </button>
      </div>
      {error && <div className="error">{error}</div>}
    </div>
  );
};

export default FileUploader;
