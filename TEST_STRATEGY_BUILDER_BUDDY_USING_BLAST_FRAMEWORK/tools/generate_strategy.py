import os
import json
import httpx
from urllib.parse import urlencode


def main(input_json: str):
    """Call GROQ LLM to generate test strategy.
    Expects input_json with keys:
      - jira_data: dict of issue fields
      - custom_prompt (optional): string to override default prompt
    Returns JSON with 'sections' list where each item has 'title' and 'content'.
    """
    payload = json.loads(input_json)
    jira_data = payload.get('jira_data')
    custom_prompt = payload.get('custom_prompt')

    jira_key = jira_data.get("key", "Unknown") if isinstance(jira_data, dict) else "Unknown"
    fields = jira_data.get("fields", {}) if isinstance(jira_data, dict) else {}
    summary = fields.get("summary", "No Summary")
    description = fields.get("description", "")
    if isinstance(description, dict) or isinstance(description, list):
        description = json.dumps(description)

    default_prompt = f"""You are an expert test-strategy writer. Using the provided Jira issue details ({jira_key}: {summary}), generate a comprehensive test-strategy document.

CRITICAL INSTRUCTION: Do NOT use the raw Issue Key (e.g., '{jira_key}' or 'SCRUM-5') inside the generated document text. You must dynamically use the actual feature name/summary ("{summary}") when referring to the epic or feature set.

You must completely overwrite the boilerplate template sections. Base 100% of the content on the specific functional requirements provided in the user story.

REQUIRED SECTION HIERARCHY (You MUST include these exact sections in this order):
1. Introduction
2. Scope
3. User Stories & Acceptance Criteria (Map out the exact requirements provided in the payload, explicitly mentioning HTTPS, Password Masking, Brute-Force/Captcha rules, and Responsive Design)
4. Focus Areas (Highlight critical testing vectors: Security like SQLi prevention and secure cookies, Session Management like 'Remember Me' logic, and User Experience like error handling clarity and multi-device UI responsiveness)
5. Entry & Exit Criteria (Entry: Secure STAGING deployed with SSL, Test Data with SQLi prepared, Captcha API credentials. Exit: 100% core scenarios executed, zero Blockers/Critical security bugs, successful cross-device verification)
6. Test Types (Dynamically generated to address login flow, responsive testing, and validation errors)
7. Test Objectives
8. Test Approach
9. Test Environment
10. Risks

Ensure Section 6 (Test Types) and Section 10 (Risks) are dynamically generated to address the login flow, responsive testing requirements across Desktop/Tablet/Mobile, and credential validation errors instead of generic frontend/backend component text.

CONTEXT:
Issue Key: {jira_key}
Summary: {summary}
Description / Requirements:
{description}

Return a JSON object with a list of sections, each containing 'title' and 'content'. Your response MUST be valid JSON without any markdown formatting block. Format: {{"sections": [{{"title": "...", "content": "..."}}]}}"""

    prompt = custom_prompt or default_prompt

    # Build request body for GROQ
    body = {
        "model": os.getenv('GROQ_API_MODEL', 'llama-3.3-70b-versatile'),
        "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": json.dumps(jira_data)}],
        "temperature": 0.0,
        "max_tokens": 4000,
    }

    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise RuntimeError('GROQ_API_KEY missing in .env')

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = httpx.post('https://api.groq.com/openai/v1/chat/completions', json=body, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    # The LLM should return JSON in the content field
    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        # If LLM returned plain text, wrap it in a single section
        result = {"sections": [{"title": "Strategy", "content": content}]}
    print(json.dumps(result))

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Input JSON required"}))
        sys.exit(1)
    main(sys.argv[1])
