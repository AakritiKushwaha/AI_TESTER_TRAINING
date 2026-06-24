import React, { useState, useEffect } from 'react';
import './SettingsModal.css';

export default function SettingsModal({ onClose }) {
  const [jiraEmail, setJiraEmail] = useState('');
  const [jiraToken, setJiraToken] = useState('');
  const [jiraBaseUrl, setJiraBaseUrl] = useState('');
  const [groqApiKey, setGroqApiKey] = useState('');

  // Load saved credentials on mount
  useEffect(() => {
    setJiraEmail(localStorage.getItem('jiraEmail') || '');
    setJiraToken(localStorage.getItem('jiraToken') || '');
    setJiraBaseUrl(localStorage.getItem('jiraBaseUrl') || '');
    setGroqApiKey(localStorage.getItem('groqApiKey') || '');
  }, []);

  const handleSave = () => {
    localStorage.setItem('jiraEmail', jiraEmail);
    localStorage.setItem('jiraToken', jiraToken);
    localStorage.setItem('jiraBaseUrl', jiraBaseUrl);
    localStorage.setItem('groqApiKey', groqApiKey);
    onClose();
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <h2>Settings</h2>
        <div className="settings-grid">
          <div className="input-group">
            <label>Jira Email:</label>
            <input type="email" value={jiraEmail} onChange={e => setJiraEmail(e.target.value)} />
          </div>
          <div className="input-group">
            <label>Jira Token:</label>
            <input type="password" value={jiraToken} onChange={e => setJiraToken(e.target.value)} />
          </div>
          <div className="input-group">
            <label>Jira Base URL:</label>
            <input type="text" value={jiraBaseUrl} onChange={e => setJiraBaseUrl(e.target.value)} placeholder="https://your-domain.atlassian.net" />
          </div>
          <div className="input-group">
            <label>Groq API Key:</label>
            <input type="password" value={groqApiKey} onChange={e => setGroqApiKey(e.target.value)} />
          </div>
        </div>
        <div className="modal-actions">
          <button onClick={handleSave}>Save</button>
          <button onClick={onClose}>Cancel</button>
        </div>
      </div>
    </div>
  );
}
