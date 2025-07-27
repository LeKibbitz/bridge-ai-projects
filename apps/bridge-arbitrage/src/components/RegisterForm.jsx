import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { supabase } from '../supabaseClient';

const RegisterForm = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    bridgeLicenseNumber: '',
    federation: 'FBS',
    language: 'fr'
  });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const { signUp } = useAuth();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    try {
      const user = await signUp(
        formData.email,
        formData.password,
        {
          first_name: formData.firstName,
          last_name: formData.lastName,
          bridge_license_number: formData.bridgeLicenseNumber,
          federation_id: formData.federation,
          language_preference: formData.language
        }
      );

      if (user) {
        setSuccess(true);
        setError(null);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="register-form">
      {success ? (
        <div className="success">
          <h2>Inscription réussie !</h2>
          <p>Un email de confirmation a été envoyé à votre adresse.</p>
          <p>Vérifiez votre boîte de réception et suivez les instructions pour activer votre compte.</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit}>
          <h2>Inscription</h2>
          
          {error && <div className="error">{error}</div>}

          <div className="form-group">
            <label>Email:</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Mot de passe:</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Confirmer le mot de passe:</label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Nom:</label>
            <input
              type="text"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Prénom:</label>
            <input
              type="text"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Numéro de licence bridge:</label>
            <input
              type="text"
              name="bridgeLicenseNumber"
              value={formData.bridgeLicenseNumber}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Fédération:</label>
            <select
              name="federation"
              value={formData.federation}
              onChange={handleChange}
              required
            >
              <option value="FBS">Fédération Suisse de Bridge</option>
              <option value="FRA">Fédération Française de Bridge</option>
              <option value="WBF">World Bridge Federation</option>
            </select>
          </div>

          <div className="form-group">
            <label>Langue préférée:</label>
            <select
              name="language"
              value={formData.language}
              onChange={handleChange}
              required
            >
              <option value="fr">Français</option>
              <option value="en">Anglais</option>
            </select>
          </div>

          <button type="submit">S'inscrire</button>
        </form>
      )}
    </div>
  );
};

export default RegisterForm;
