# Findings Log

## Research
- GROQ API provides fast LLM inference with `mixtral-8x7b-32768` model; requires `GROQ_API_KEY` env var.
- `python-docx` library enables programmatic DOCX generation with structured sections.
- FastAPI can serve both API routes and static frontend files from a single serverless function on Vercel.
- Vercel Python runtime (via `api/index.py`) supports ASGI apps like FastAPI.

## Discoveries

### Jira Integration
- Jira REST API v3 endpoints: `/rest/agile/1.0/issue/{id}` for issue details.
- When Jira credentials are missing, app gracefully falls back to mock data for any Jira ID (no whitelist).
- CLI args `--email`, `--token`, `--base-url` allow passing credentials dynamically from backend rather than reading `.env` directly.
- `JIRA_API_TOKEN` env var also accepted as fallback in `fetch_jira.py`.

### FastAPI + Vercel Architecture
- Vercel requires a single entry point at `api/index.py`; all traffic rewritten via `vercel.json`.
- Route order matters: API routes must be defined before the catch-all `/{path:path}` static file handler.
- Static files (from `frontend/dist/`) are served by FastAPI using `FileResponse` with proper MIME types.
- `text/javascript` MIME type is automatically correct for `.js` files served via `FileResponse`.

### Frontend
- `crossorigin` attribute on `<script type="module">` tags can cause blank screen in some browsers when serving same-origin; must be stripped post-build via custom Vite plugin.
- React `ErrorBoundary` class component is the only way to catch render errors (cannot use hooks for this).
- `localStorage` is suitable for persisting Jira credentials and theme preference; credentials passed to backend as query params.
- Settings modal validation prevents generation without configured Jira credentials.

### Vite Build
- Custom Vite plugins using `transformIndexHtml` hook can modify the output HTML post-build.
- The `remove-crossorigin` plugin successfully strips `crossorigin` attributes from `<script>` and `<link>` tags.

### Deployment
- Vercel CLI requires `--token` or `VERCEL_TOKEN` env var for non-interactive deploys.
- Environment variables must be explicitly set via `vercel env add` for production.
- Single-command build: `cd frontend && npm install && npm run build` — only frontend needs building; Python deps handled by Vercel.

## Constraints
- Jira credentials must be entered by the user in Settings UI before generation; no auto-discovery possible.
- Vercel serverless functions have a 10-second timeout and 1 GB memory limit; LLM generation may need optimization for larger tickets.
- No real Jira credentials committed to repo; `.env` is in `.gitignore`.
- `__pycache__/` directories must be excluded from version control.
- Python tools communicate with FastAPI via `subprocess.run`; input passed as CLI args, output captured from stdout as JSON.
- The `.docx` download endpoint returns file directly as `StreamingResponse`; preview is rendered as HTML on the frontend.

## Errors Encountered
1. **Blank screen on deploy** — caused by `crossorigin` attribute on `<script type="module" src="...">` in built HTML. Fixed by adding custom Vite plugin `remove-crossorigin` to strip the attribute.
2. **Catch-all route shadowing API routes** — `@app.get("/{path:path}")` was defined before `/fetch-jira/{id}`, causing 404 on API calls. Fixed by moving catch-all to end of route definitions.
3. **Route redefinition error** — `@app.get("/")` for root and catch-all `@app.get("/{path:path}")` conflict; resolved by removing explicit root route and letting catch-all handle `/`.
4. **Post-deploy missing `crossorigin` removal** — initial Vite plugin returned wrong HTML; fixed by correctly using `transformIndexHtml` hook.
5. **`crossorigin` still appearing as `crossorigin`** — regex was case-sensitive; fixed pattern to handle both attribute forms.

---

**How to use**: Append new research, discoveries, constraints, and errors as they occur. This is the project's institutional memory per the BLAST protocol.
