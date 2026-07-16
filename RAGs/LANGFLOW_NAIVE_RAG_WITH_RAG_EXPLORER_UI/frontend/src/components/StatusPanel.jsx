import { useState, useEffect } from "react";

const MODULES = [
  "Login", "Registration", "Product Search & Listing", "Product Details",
  "Add to Cart", "Wishlist", "Checkout", "Payment",
  "Order Management", "User Profile & Account Settings",
];

function formatTimestamp(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString();
}

export default function StatusPanel() {
  const [pipeline, setPipeline] = useState(null); // null | object
  const [loading, setLoading] = useState(true);

  async function fetchStatus() {
    setLoading(true);
    try {
      const res = await fetch("/api/pipeline-status");
      const data = await res.json();
      setPipeline(data);
    } catch {
      setPipeline({ connected: false, error: "Failed to reach backend." });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <div className="panel status-panel">
      <h2 className="panel-title">Pipeline Status</h2>

      {/* ── Live status card ── */}
      <div className="status-card">
        {loading && !pipeline && (
          <div className="status-row"><span className="status-label">Loading...</span></div>
        )}

        {!loading && pipeline && (
          <>
            <div className="status-row">
              <span className="status-label">Connection</span>
              <span
                className={`status-value ${
                  pipeline.connected ? "connected" : "disconnected"
                }`}
              >
                {pipeline.connected ? "● Connected" : "● Disconnected"}
              </span>
            </div>

            {pipeline.connected && (
              <>
                <div className="status-row">
                  <span className="status-label">Collection</span>
                  <span className="status-value mono">
                    {pipeline.collection_name || "—"}
                  </span>
                </div>
                <div className="status-row">
                  <span className="status-label">Vectors Stored</span>
                  <span className="status-value">
                    {pipeline.total_vectors_stored ?? "—"}
                  </span>
                </div>
                <div className="status-row">
                  <span className="status-label">Embedding Dims</span>
                  <span className="status-value">
                    {pipeline.embedding_dims ?? "—"}
                  </span>
                </div>
                {pipeline.embedding_model && (
                  <div className="status-row">
                    <span className="status-label">Embedding Model</span>
                    <span className="status-value">{pipeline.embedding_model}</span>
                  </div>
                )}
                <div className="status-row">
                  <span className="status-label">Last Checked</span>
                  <span className="status-value">
                    {formatTimestamp(pipeline.last_checked)}
                  </span>
                </div>
              </>
            )}

            {!pipeline.connected && pipeline.error && (
              <div className="status-row">
                <span className="status-label">Error</span>
                <span className="status-value" style={{ color: "var(--error)", fontSize: "0.78rem" }}>
                  {pipeline.error}
                </span>
              </div>
            )}
          </>
        )}
      </div>

      {/* ── Refresh button ── */}
      <button
        className="btn test-btn"
        onClick={fetchStatus}
        disabled={loading}
      >
        {loading ? "Refreshing..." : "Refresh Status"}
      </button>

      {pipeline && !pipeline.connected && (
        <div className="status-indicator error">
          ✗ Cannot reach Chroma DB — check Langflow connection and API key
        </div>
      )}

      <hr className="panel-divider" />

      {/* ── Static dataset reference ── */}
      <div className="status-card dataset-card">
        <div className="status-row">
          <span className="status-label">Source File</span>
          <span className="status-value mono">ecom_test_cases.csv</span>
        </div>
        <div className="status-row">
          <span className="status-label">Test Cases</span>
          <span className="status-value">1,000</span>
        </div>
      </div>

      <details className="modules-details">
        <summary className="modules-summary">Modules ({MODULES.length})</summary>
        <ul className="modules-list">
          {MODULES.map((m) => (
            <li key={m}>{m}</li>
          ))}
        </ul>
      </details>
    </div>
  );
}
