import { useState } from "react";

const SUGGESTIONS = [
  "Show me login test cases",
  "What negative test cases exist for payment?",
  "List edge cases for checkout",
  "Show all test cases related to wishlist",
  "What are the high-priority test cases for registration?",
];

export default function AskPanel() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleAsk() {
    const q = question.trim();
    if (!q) return;
    setLoading(true);
    setError(null);
    setAnswer(null);
    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      const data = await res.json();
      setAnswer(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      handleAsk();
    }
  }

  function renderAnswer(text) {
    // Replace 【Chunk N】 markers with styled spans
    return text.split(/(【[^】]+】)/g).map((part, i) => {
      if (/^【[^】]+】$/.test(part)) {
        const num = part.replace(/[^0-9]/g, "");
        return (
          <sup key={i} className="citation">
            [{num}]
          </sup>
        );
      }
      return <span key={i}>{part}</span>;
    });
  }

  return (
    <div className="panel ask-panel">
      <h2 className="panel-title">Ask</h2>

      <div className="suggestions-row">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            className="chip"
            onClick={() => setQuestion(s)}
          >
            {s}
          </button>
        ))}
      </div>

      <div className="input-row">
        <textarea
          className="query-input"
          rows={3}
          placeholder="Ask a question about the test cases..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          className="btn ask-btn"
          onClick={handleAsk}
          disabled={loading || !question.trim()}
        >
          {loading ? "Asking..." : "Ask"}
        </button>
      </div>

      {error && <div className="error-box">Error: {error}</div>}

      {answer && (
        <div className="answer-section">
          <div className="answer-header">
            <span className="model-badge">
              {answer.model || "Unknown model"}
            </span>
            {answer.tokens != null && (
              <span className="token-count">
                {answer.tokens} tokens
              </span>
            )}
          </div>

          <div className="answer-text">
            {renderAnswer(answer.answer)}
          </div>

          {answer.chunks && answer.chunks.length > 0 && (
            <div className="chunks-section">
              <h3 className="chunks-title">
                Top Retrieved Chunks ({answer.chunks.length})
              </h3>
              {answer.chunks.map((chunk, i) => (
                <details key={i} className="chunk-card">
                  <summary className="chunk-summary">
                    【Chunk {i + 1}】 — {chunk.source}
                  </summary>
                  <pre className="chunk-text">{chunk.text}</pre>
                </details>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
