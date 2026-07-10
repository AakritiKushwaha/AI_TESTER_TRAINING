# Task Checklist

## Phase 0 – Initialization
- [x] Create `task_plan.md`
- [x] Create `findings.md`
- [x] Create `progress.md`
- [x] Initialize `gemini.md` with project constitution

## Phase 1 – Blueprint (Vision & Logic)
- [x] Finalize JSON schema in `gemini.md`
- [x] Add configurable LLM prompt block
- [x] Ensure behavioral rules and naming convention are defined

## Phase 2 – Link (Connectivity)
- [x] Add `.env.example` with placeholder keys
- [x] Implement `tools/fetch_jira.py` with `--email/--token/--base-url` CLI args + `JIRA_API_TOKEN` env fallback
- [x] Implement `tools/generate_strategy.py`
- [x] Implement `tools/create_docx.py`
- [x] Wire FastAPI endpoints in `backend/main.py`
- [x] Remove mock ID whitelist — accept any Jira ID

## Phase 3 – Architect (3‑Layer Build)
- [x] Scaffold React app with Vite (`npm create vite@latest . --template react`)
- [x] Set up proxy to FastAPI in Vite config
- [x] Create UI components: Header, JiraInputForm, StrategyDisplay, DownloadButton, SettingsModal
- [x] Implement theme toggle with persistence
- [x] Add settings validation — block generation when Jira credentials missing
- [x] Add `try/catch` error handling with user-facing messages in `App.jsx`
- [x] Wire Jira credentials from localStorage as query params to backend

## Phase 4 – Stylize (Refinement & UI)
- [x] Apply premium UI styling (glassmorphism, gradients, Inter font) across components
- [x] Add micro-animations and loading spinners
- [x] Ensure responsive layout for desktop/tablet
- [x] Implement DOCX preview component
- [x] Add `ErrorBoundary.jsx` to catch render errors (blank screen fix)
- [x] Wrap `<App />` in `<ErrorBoundary>` in `main.jsx`
- [x] Strip `crossorigin` attribute from built HTML via custom Vite plugin

## Phase 5 – Trigger (Deployment)
- [x] Create `vercel.json` with rewrite rules and frontend build command
- [x] Create `api/index.py` importing FastAPI `app`
- [x] Create `requirements.txt` for Vercel Python runtime
- [x] Create `.vercelignore`
- [x] Move catch-all route to end of `backend/main.py`
- [x] Add static file serving in FastAPI for single-command deploy
- [x] Set env vars on Vercel project: `GROQ_API_KEY`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_BASE_URL`
- [x] Deploy to Vercel via CLI (`vercel --prod`)
- [x] Verify all endpoints on production:
  - `GET /` — 200 (serves index.html)
  - `GET /assets/*` — 200 (correct JS/CSS MIME types)
  - `GET /fetch-jira/SCRUM-5` — 200
  - `GET /fetch-jira/SCRUM-6` — 200
  - Confirm `crossorigin` removed from built HTML
- [x] Update `.gitignore` to exclude `.env` and `__pycache__/`
- [x] Commit and push to `origin/main` (commit `e2dfa47`, 52 files)

## Not Started / Future
- [ ] Add `architecture/` SOP documents
- [ ] Add real Jira credentials for production use (currently returns mock data)
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Add automated E2E tests (Playwright or Cypress)
- [ ] Add Dockerfile for containerised deployment
- [ ] Document deployment steps in `gemini.md`
