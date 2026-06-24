# Project Constitution (`gemini.md`)

## Data Schema (JSON)
```json
{
  "input": {
    "jiraId": "string"
  },
  "settings": {
    "jiraEmail": "string",
    "jiraToken": "string",
    "jiraBaseUrl": "string",
    "groqApiKey": "string"
  },
  "output": {
    "docxFileName": "string",
    "docxBase64": "string",
    "previewHtml": "string"
  }
}
```

## Configurable LLM Prompt
The prompt sent to the GROQ LLM can be overridden via the Settings modal. Default prompt:
```
You are a test‑strategy writer. Using the provided Jira issue details, generate a comprehensive test‑strategy document following the section structure of the sample document.

```

## Behavioral Rules
- Never expose any credential values in UI or logs.
- Follow the sample document's section hierarchy exactly.
- All generated DOCX must be downloadable via a button.
- Naming convention: `TestStrategy_<JiraID>.docx`.
