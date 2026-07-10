import { useState } from 'react';
import Ajv from 'ajv';

const ajv = new Ajv({ allErrors: true, strict: false });

const defaultSchema = `{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "id": { "type": "integer" },
      "name": { "type": "string" },
      "email": { "type": "string" },
      "gender": { "type": "string" },
      "status": { "type": "string" }
    },
    "required": ["id", "name", "email", "gender", "status"]
  }
}`;

function extractValidationMessage(responseData) {
  try {
    if (!responseData) return null;

    const outputs = responseData.outputs;
    if (!Array.isArray(outputs) || outputs.length === 0) return null;

    const firstOutput = outputs[0];
    const outputsList = firstOutput.outputs;
    if (!Array.isArray(outputsList) || outputsList.length === 0) return null;

    const firstResult = outputsList[0];
    const messages = firstResult.messages;
    if (!Array.isArray(messages) || messages.length === 0) return null;

    const firstMessage = messages[0];
    return firstMessage.message || null;
  } catch {
    return null;
  }
}

function parseValidationMessage(message) {
  if (!message) return null;

  const trimmed = message.trim();

  try {
    const parsed = JSON.parse(trimmed);
    return parsed;
  } catch {
    // Not JSON, return as structured text
    return { text: trimmed };
  }
}

function extractApiUrlFromCurl(curlCommand) {
  const urlMatch = curlCommand.match(/curl\s+['"]*([^\s'"]+)['"]*|--location\s+['"]*([^\s'"]+)['"]*|curl\s+['"]([^'"]+)['"]/i);
  return urlMatch ? (urlMatch[1] || urlMatch[2] || urlMatch[3] || '') : '';
}

function App() {
  const [curlInput, setCurlInput] = useState('curl "https://gorest.co.in/public/v2/users"');
  const [schemaText, setSchemaText] = useState(defaultSchema);
  const [apiKey, setApiKey] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const validateContract = async (event) => {
    event.preventDefault();
    setError('');
    setResult(null);
    setLoading(true);

    try {
      let schema;
      try {
        schema = JSON.parse(schemaText);
      } catch (schemaErr) {
        throw new Error('Expected JSON Schema must be valid JSON.');
      }

      const apiUrl = extractApiUrlFromCurl(curlInput);
      if (!apiUrl) {
        throw new Error('Could not extract API URL from curl command.');
      }

      const langflowPayload = {
        output_type: 'chat',
        input_type: 'chat',
        input_value: `Please perform API Contract validation for following:\ncurl "${apiUrl}"\n\nJSON Schema\n${schemaText}`,
      };

      if (sessionId?.trim()) {
        langflowPayload.session_id = sessionId;
      }

      const langflowUrl = 'http://localhost:7862/api/v1/run/6f5358c8-cab1-4f75-95cf-8940426178b8?stream=false';
      const headers = {
        'Content-Type': 'application/json',
      };

      if (apiKey?.trim()) {
        headers['x-api-key'] = apiKey;
      }

      const langflowResponse = await fetch(langflowUrl, {
        method: 'POST',
        headers,
        body: JSON.stringify(langflowPayload),
      });

      if (!langflowResponse.ok) {
        const errorText = await langflowResponse.text();
        throw new Error(`Langflow request failed with status ${langflowResponse.status}: ${errorText}`);
      }

      const langflowData = await langflowResponse.json();
      const validationMessage = extractValidationMessage(langflowData);

      if (!validationMessage) {
        throw new Error('No validation response from Langflow.');
      }

      const parsedMessage = parseValidationMessage(validationMessage);
      const responseSessionId = langflowData.session_id || sessionId;

      setResult({
        apiUrl,
        validationMessage: parsedMessage,
        rawResponse: validationMessage,
        sessionId: responseSessionId,
      });
    } catch (err) {
      setError(err.message || 'Validation failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="hero-card">
        <div>
          <p className="eyebrow">Lightweight UI</p>
          <h1>API Contract Validator</h1>
          <p className="hero-text">
            Share a request curl or API URL along with your expected JSON schema. We validate the live API response against your contract and provide detailed insights.
          </p>
        </div>
      </header>

      <form className="panel" onSubmit={validateContract}>
        <label className="field">
          <span>Request Curl or API URL</span>
          <input
            type="text"
            value={curlInput}
            onChange={(event) => setCurlInput(event.target.value)}
            placeholder="curl 'https://api.example.com/endpoint' or https://api.example.com/endpoint"
            required
          />
        </label>

        <label className="field">
          <span>Expected JSON Schema</span>
          <textarea
            rows="12"
            value={schemaText}
            onChange={(event) => setSchemaText(event.target.value)}
            spellCheck="false"
            required
          />
        </label>

        <label className="field">
          <span>Langflow API Key (optional)</span>
          <input
            type="password"
            value={apiKey}
            onChange={(event) => setApiKey(event.target.value)}
            placeholder="Enter your Langflow API key if required"
          />
        </label>

        <label className="field">
          <span>Session ID (optional)</span>
          <input
            type="text"
            value={sessionId}
            onChange={(event) => setSessionId(event.target.value)}
            placeholder="Session ID for conversation continuity"
          />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? 'Validating…' : 'Validate Contract'}
        </button>
      </form>

      {error ? <div className="message-box error">{error}</div> : null}

      {result ? (
        <section className="panel result-panel">
          <div className="summary-row">
            <div className="summary-item">
              <strong>API URL</strong>
              <span>{result.apiUrl}</span>
            </div>
            {result.sessionId && (
              <div className="summary-item">
                <strong>Session ID</strong>
                <span>{result.sessionId}</span>
              </div>
            )}
          </div>

          <div className="result-box insight-box">
            <h3>Validation Result</h3>
            {result.validationMessage?.text ? (
              <div>
                {result.validationMessage.text.split('\n').map((line, idx) => (
                  <p key={idx} style={{ marginBottom: '0.5rem', whiteSpace: 'pre-wrap' }}>
                    {line}
                  </p>
                ))}
              </div>
            ) : typeof result.validationMessage === 'object' ? (
              <pre>{JSON.stringify(result.validationMessage, null, 2)}</pre>
            ) : (
              <pre>{result.rawResponse}</pre>
            )}
          </div>
        </section>
      ) : null}
    </div>
  );
}

export default App;
