import React from 'react';
import './JiraInputForm.css';

export default function JiraInputForm({ jiraId, setJiraId, onGenerate, loading, error }) {
  return (
    <section className="jira-input-form-container">
      <div className="jira-input-form">
        <input
          type="text"
          placeholder="Enter Jira Ticket ID..."
          value={jiraId}
          onChange={(e) => setJiraId(e.target.value)}
          disabled={loading}
          className="jira-input"
        />
        <button onClick={onGenerate} disabled={loading || !jiraId} className="generate-btn">
          {loading ? 'Generating...' : 'Generate Strategy'}
        </button>
      </div>
      {error && <div className="error-message">{error}</div>}
    </section>
  );
}
