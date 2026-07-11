import { useState, useRef, useCallback, useEffect } from 'react';

const STAGES = [
  { num: 1, label: 'PDF' },
  { num: 2, label: 'Chunk' },
  { num: 3, label: 'Embed' },
  { num: 4, label: 'Store' },
  { num: 5, label: 'Retrieve' },
  { num: 6, label: 'Answer' },
];

function renderAnswer(text) {
  const parts = text.split(/(【Chunk \d+】)/g);
  return parts.map((part, i) => {
    const match = part.match(/【(Chunk \d+)】/);
    if (match) {
      return <sup key={i} className="citation-badge">{match[1]}</sup>;
    }
    return <span key={i}>{part}</span>;
  });
}

function App() {
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState('Ready to ingest.');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [ingested, setIngested] = useState(false);
  const [suggestions, setSuggestions] = useState([
    'What does the login dashboard support?',
    'What are the key features of the PRD?',
    'What browsers are supported?',
    'What are the performance requirements?',
  ]);
  const [stats, setStats] = useState({
    file: '',
    pages: 0,
    chunks: [],
    dims: 0,
    stored: 0,
    sample: [],
  });
  const [expandedChunks, setExpandedChunks] = useState({});
  const [dragOver, setDragOver] = useState(false);
  const [activeStage, setActiveStage] = useState(0);
  const fileInputRef = useRef(null);

  const fetchSuggestions = useCallback(async () => {
    try {
      const res = await fetch('/api/suggestions', { method: 'POST' });
      const data = await res.json();
      if (data.suggestions) setSuggestions(data.suggestions);
    } catch {
      // keep defaults
    }
  }, []);

  useEffect(() => {
    if (ingested) fetchSuggestions();
  }, [ingested, fetchSuggestions]);

  const onIngestDone = useCallback((data) => {
    setStats({
      file: data.file,
      pages: data.pages,
      chunks: data.chunks,
      dims: data.embeddings.dims,
      stored: data.embeddings.total,
      sample: data.embeddings.sample,
    });
    setIngested(true);
    setActiveStage(4);
    setStatus(data.message || 'Index built successfully.');
    setResult(null);
    setExpandedChunks({});
  }, []);

  const ingestPdf = async () => {
    setLoading(true);
    setStatus('Ingesting...');
    setActiveStage(1);
    try {
      const response = await fetch('/api/ingest', { method: 'POST' });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Ingestion failed');
      onIngestDone(data);
    } catch (error) {
      setStatus(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const resetIndex = async () => {
    setLoading(true);
    setStatus('Resetting index...');
    try {
      await fetch('/api/reset', { method: 'POST' });
      setStats({ file: '', pages: 0, chunks: [], dims: 0, stored: 0, sample: [] });
      setIngested(false);
      setResult(null);
      setExpandedChunks({});
      setActiveStage(0);
      setSuggestions([
        'What does the login dashboard support?',
        'What are the key features of the PRD?',
        'What browsers are supported?',
        'What are the performance requirements?',
      ]);
      setStatus('Index reset. Ready to ingest.');
    } catch (error) {
      setStatus(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const uploadFile = useCallback(async (file) => {
    setLoading(true);
    setStatus('Uploading and ingesting...');
    setActiveStage(1);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch('/api/ingest_file', { method: 'POST', body: formData });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Upload failed');
      onIngestDone(data);
    } catch (error) {
      setStatus(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, [onIngestDone]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) uploadFile(file);
  }, [uploadFile]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => setDragOver(false), []);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) uploadFile(file);
  };

  const runQuery = async () => {
    if (!query.trim()) {
      setStatus('Enter a question first.');
      return;
    }
    setLoading(true);
    setActiveStage(5);
    setStatus('Retrieving and generating answer...');
    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Query failed');
      setResult(data);
      setActiveStage(6);
      setStatus('Query completed.');
    } catch (error) {
      setStatus(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const toggleChunk = (idx) => {
    setExpandedChunks((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div className="app-shell">
      {/* Pipeline Stepper */}
      <header className="hero">
        <div>
          <p className="eyebrow">RAG EXPLORER</p>
          <h1>Retrieval-Augmented Generation</h1>
        </div>
      </header>

      <div className="stepper">
        {STAGES.map((s, i) => (
          <span key={s.num} className="stepper-group">
            <span className={`step-badge ${activeStage >= s.num ? 'active' : ''}`}>
              <span className="step-num">{s.num}</span>
              <span className="step-label">{s.label}</span>
            </span>
            {i < STAGES.length - 1 && <span className="step-arrow">→</span>}
          </span>
        ))}
      </div>

      {/* Two-column layout */}
      <div className="columns">
        {/* LEFT COLUMN — Ingestion */}
        <div className="col-left">
          <div className="card">
            <h2>Ingestion</h2>
            <div className="ingest-actions">
              <button className="btn primary" onClick={ingestPdf} disabled={loading}>
                Ingest folder
              </button>
              <button className="btn secondary" onClick={resetIndex} disabled={loading}>
                Reset
              </button>
            </div>
            <p className="source-path">Source: data/</p>

            {/* Drag-and-drop zone */}
            <div
              className={`drop-zone ${dragOver ? 'drag-over' : ''}`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
            >
              <span className="drop-icon">📄</span>
              <p>Drop a PDF, .txt or .md here — or click to browse</p>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt,.md"
                style={{ display: 'none' }}
                onChange={handleFileSelect}
              />
            </div>
          </div>

          {/* Stat cards */}
          {ingested && (
            <>
              <div className="stat-grid">
                <div className="stat-card"><span className="stat-val">{stats.pages}</span><span className="stat-label">Pages</span></div>
                <div className="stat-card"><span className="stat-val">{stats.chunks.length}</span><span className="stat-label">Chunks</span></div>
                <div className="stat-card"><span className="stat-val">{stats.dims}</span><span className="stat-label">Embed dims</span></div>
                <div className="stat-card"><span className="stat-val">{stats.stored}</span><span className="stat-label">Stored</span></div>
              </div>

              {/* Sample embedding */}
              {stats.sample.length > 0 && (
                <div className="card">
                  <h3>Sample embedding (first 8 dims)</h3>
                  <div className="embed-preview">
                    [{stats.sample.map((v, i) => (
                      <span key={i} className="embed-val">{v.toFixed(4)}{i < stats.sample.length - 1 ? ', ' : ''}</span>
                    ))}]
                  </div>
                </div>
              )}

              {/* Chunk preview */}
              <div className="card">
                <h3>Chunk preview</h3>
                <div className="chunk-list">
                  {stats.chunks.map((c) => (
                    <div key={c.index} className="chunk-item">
                      <button className="chunk-toggle" onClick={() => toggleChunk(c.index)}>
                        <span className="chunk-summary">
                          Chunk {c.index} — {c.chars} chars
                        </span>
                        <span className={`chunk-chevron ${expandedChunks[c.index] ? 'open' : ''}`}>▸</span>
                      </button>
                      {expandedChunks[c.index] && (
                        <div className="chunk-text">{c.text}</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>

        {/* RIGHT COLUMN — Ask & Answer */}
        <div className="col-right">
          {/* Suggested questions */}
          <div className="card">
            <h2>Ask a question</h2>
            <div className="suggestions">
              {suggestions.map((s, i) => (
                <button key={i} className="chip" onClick={() => setQuery(s)}>
                  {s}
                </button>
              ))}
            </div>
            <textarea
              rows="4"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="What does the login dashboard support?"
            />
            <div className="actions">
              <button className="btn primary" onClick={runQuery} disabled={loading || !ingested}>
                {loading ? 'Thinking...' : 'Ask'}
              </button>
            </div>
            <p className="status">{status}</p>
          </div>

          {/* Answer */}
          <div className="card results">
            {result ? (
              <>
                <div className="answer-header">
                  <h2>Answer</h2>
                  {result.model && (
                    <span className="model-badge">
                      {result.model} · {result.usage?.total_tokens || 0} tokens
                    </span>
                  )}
                </div>
                <p className="answer">{renderAnswer(result.answer)}</p>
                <div className="sources">
                  <h3>Top retrieved chunks</h3>
                  {result.sources.map((source, index) => (
                    <div key={index} className="source-item">
                      <strong>Chunk {index + 1}</strong>
                      <p>{source}</p>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <p className="muted">No answer yet. Ingest a file and ask a question.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
