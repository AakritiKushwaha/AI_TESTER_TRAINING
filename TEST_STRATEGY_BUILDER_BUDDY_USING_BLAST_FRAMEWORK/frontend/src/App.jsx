import { useState } from 'react';
import Header from './components/Header.jsx';
import JiraInputForm from './components/JiraInputForm.jsx';
import StrategyDisplay from './components/StrategyDisplay.jsx';
import DownloadButton from './components/DownloadButton.jsx';
import SettingsModal from './components/SettingsModal.jsx';
import ThemeToggle from './components/ThemeToggle.jsx';
import DocxPreview from './components/DocxPreview.jsx';
import './App.css';

function App() {
  const [jiraId, setJiraId] = useState('');
  const [jiraData, setJiraData] = useState(null);
  const [strategy, setStrategy] = useState(null);
  const [docx, setDocx] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showSettings, setShowSettings] = useState(false);

  const handleGenerate = async () => {
    if (!jiraId) return;
    setLoading(true);
    setError(null);
    setStrategy(null);
    setDocx(null);
    try {
      const email = localStorage.getItem('jiraEmail');
      const token = localStorage.getItem('jiraToken');
      const baseUrl = localStorage.getItem('jiraBaseUrl');
      if (!email || !token || !baseUrl) {
        setError("Please configure your Jira credentials in Settings before generating a strategy.");
        setLoading(false);
        return;
      }
      let jiraUrl = `/fetch-jira/${jiraId}`;
      const params = new URLSearchParams();
      if (email) params.set('email', email);
      if (token) params.set('token', token);
      if (baseUrl) params.set('base_url', baseUrl);
      const qs = params.toString();
      if (qs) jiraUrl += `?${qs}`;
      const jiraRes = await fetch(jiraUrl);
      if (!jiraRes.ok) {
        const errData = await jiraRes.json().catch(() => ({}));
        setError(errData.error || `Error fetching Jira data: ${jiraRes.statusText}`);
        return;
      }
      const fetchedJiraData = await jiraRes.json();
      setJiraData(fetchedJiraData);
      // Generate strategy
      const genRes = await fetch('/generate-strategy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jira_data: fetchedJiraData })
      });
      if (!genRes.ok) {
        const errData = await genRes.json().catch(() => ({}));
        setError(errData.error || `Error generating strategy: ${genRes.statusText}`);
        return;
      }
      const genData = await genRes.json();
      setStrategy(genData);
      // Create DOCX
      const docxRes = await fetch('/create-docx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...genData, jiraId })
      });
      if (!docxRes.ok) {
        const errData = await docxRes.json().catch(() => ({}));
        setError(errData.error || `Error generating document: ${docxRes.statusText}`);
        return;
      }
      const docxData = await docxRes.json();
      setDocx(docxData);
    } catch (e) {
      console.error("Unexpected error:", e);
      setError(e.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header onOpenSettings={() => setShowSettings(true)} />
      {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
      <JiraInputForm jiraId={jiraId} setJiraId={setJiraId} onGenerate={handleGenerate} loading={loading} error={error} />
      {docx && <DownloadButton docx={docx} />}
      {strategy && <StrategyDisplay strategy={strategy} jiraData={jiraData} />}
      {docx && <DocxPreview docx={docx} />}
    </div>
  );
}

export default App;
