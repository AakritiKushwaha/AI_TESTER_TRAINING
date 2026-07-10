# Test Strategy Builder Buddy

An AI-powered web application that generates professional test strategy documents from Jira tickets using GROQ LLM. Built with React + Vite frontend and FastAPI backend, deployed as a single Vercel serverless function.

## Features

- **Jira Integration** — Fetch issue details from any Jira Cloud instance via ticket ID (SCRUM-123, PROJ-42, etc.)
- **AI Strategy Generation** — Uses GROQ LLM (`mixtral-8x7b-32768`) to generate 10-section test strategy documents
- **DOCX Export** — Download the generated strategy as a formatted `.docx` file
- **Live Preview** — Preview the generated strategy in-browser before downloading
- **Dark/Light Theme** — Persistent theme toggle with glassmorphism UI
- **Settings Panel** — Configure Jira credentials (email, API token, base URL) with validation
- **Error Boundary** — Graceful error handling with reload fallback instead of blank screen

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite 8, CSS3 (glassmorphism) |
| Backend | FastAPI (Python 3.12), subprocess-based tool runner |
| LLM | GROQ API (`mixtral-8x7b-32768`) |
| Deployment | Vercel (single serverless function) |
| Auth | Jira Cloud API (Basic Auth via email + API token) |

## Architecture

```
frontend/          # Vite + React SPA
  src/
    components/    # UI components (Header, JiraInputForm, StrategyDisplay, etc.)
    App.jsx        # Main app with state management
    main.jsx       # Entry point (wraps App in ErrorBoundary)
api/index.py       # Vercel entry point — imports FastAPI app
backend/main.py    # FastAPI app — API routes + static file serving
tools/
  fetch_jira.py         # Jira issue fetcher (CLI + env fallback)
  generate_strategy.py  # GROQ LLM strategy generator
  create_docx.py        # DOCX document builder
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.12+
- UV or pip
- A GROQ API key ([get one here](https://console.groq.com))
- A Jira Cloud instance + API token ([generate token](https://id.atlassian.com/manage-profile/security/api-tokens))

### Local Development

1. **Clone and install frontend deps**
   ```bash
   cd frontend
   npm install
   ```

2. **Create `.env`** in the project root
   ```env
   GROQ_API_KEY=gsk_your_key_here
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your_jira_api_token
   JIRA_BASE_URL=https://your-domain.atlassian.net
   ```

3. **Start the backend**
   ```bash
   cd backend
   pip install -r ../requirements.txt
   uvicorn main:app --reload --port 8000
   ```

4. **Start the frontend** (in a separate terminal)
   ```bash
   cd frontend
   npm run dev
   ```

   The Vite dev server proxies `/fetch-jira`, `/generate-strategy`, and `/create-docx` to `http://localhost:8000`.

5. Open `http://localhost:5173` in your browser.

### Deploy to Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Set environment variables:
   ```bash
   vercel env add GROQ_API_KEY
   vercel env add JIRA_EMAIL
   vercel env add JIRA_API_TOKEN
   vercel env add JIRA_BASE_URL
   ```
3. Deploy:
   ```bash
   vercel --prod
   ```

The app is served from a single Python serverless function at `/api/index.py`. All routes are rewritten to this function via `vercel.json`.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/fetch-jira/{id}` | Fetch Jira issue (optional `?email`, `?token`, `?base_url` query params) |
| POST | `/generate-strategy` | Generate test strategy from issue data |
| POST | `/create-docx` | Generate downloadable `.docx` file |
| GET | `/*` | Serve frontend static assets |

## BLAST Framework

This project follows the **B.L.A.S.T.** protocol:
- **B**lueprint — Requirements and data schema defined upfront
- **L**ink — Jira and GROQ integrations verified early
- **A**rchitect — 3-layer architecture (SOPs, Navigation, Tools)
- **S**tylize — Premium UI, error boundaries, responsive design
- **T**rigger — Deployed to Vercel, environment-configured

See `B.L.A.S.T.md` for the full protocol specification.

## Project Files

- `task.md` — Task checklist by phase
- `progress.md` — Chronological progress log
- `findings.md` — Research, discoveries, constraints, and errors
- `B.L.A.S.T.md` — Framework protocol definition
- `gemini.md` — Project constitution and data schemas
