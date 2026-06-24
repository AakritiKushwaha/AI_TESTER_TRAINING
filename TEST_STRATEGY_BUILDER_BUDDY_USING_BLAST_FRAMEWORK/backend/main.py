from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json

app = FastAPI()

# Allow Vite dev server (default http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def run_tool(script_path: str, *args):
    """Execute a Python tool script and capture JSON output.
    The tool scripts must print a JSON object to stdout.
    """
    cmd = ["python", script_path] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        try:
            err_obj = json.loads(result.stdout)
            if "status" in err_obj:
                raise HTTPException(status_code=err_obj["status"], detail=err_obj.get("error", "Unknown error"))
        except json.JSONDecodeError:
            pass
        raise HTTPException(status_code=500, detail=result.stderr)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON output from tool")

from fastapi.responses import JSONResponse, FileResponse

@app.get("/fetch-jira/{jira_id}")
async def fetch_jira(
    jira_id: str,
    email: str = Query(None),
    token: str = Query(None),
    base_url: str = Query(None),
):
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "fetch_jira.py"))
    args = [jira_id]
    if email:
        args.extend(["--email", email])
    if token:
        args.extend(["--token", token])
    if base_url:
        args.extend(["--base-url", base_url])
    try:
        return run_tool(script_path, *args)
    except HTTPException as exc:
        # Return a JSON error response preserving original error message and status
        return JSONResponse(status_code=exc.status_code, content={"error": exc.detail, "status": exc.status_code})

@app.post("/generate-strategy")
async def generate_strategy(payload: dict):
    # Expect payload with jira_data and optional custom_prompt
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "generate_strategy.py"))
    input_json = json.dumps(payload)
    return run_tool(script_path, input_json)

@app.get("/verify-env")
async def verify_env():
    required = ["JIRA_DOMAIN", "JIRA_EMAIL", "JIRA_API_TOKEN", "GROQ_API_KEY"]
    missing = [var for var in required if not os.getenv(var)]
    status = {"missing": missing, "all_present": len(missing) == 0}
    return status

@app.post("/create-docx")
async def create_docx(payload: dict):
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "create_docx.py"))
    input_json = json.dumps(payload)
    return run_tool(script_path, input_json)

FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

@app.get("/{path:path}")
async def serve_frontend(path: str):
    file_path = os.path.join(FRONTEND_DIST, path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return JSONResponse(status_code=404, content={"error": "Not found"})
