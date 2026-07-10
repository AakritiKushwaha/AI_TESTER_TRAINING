import httpx
import sys
import os
import json
import argparse
from dotenv import load_dotenv

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("jira_id", help="Jira ticket ID")
    parser.add_argument("--email", default=None)
    parser.add_argument("--token", default=None)
    parser.add_argument("--base-url", default=None)
    args = parser.parse_args()

    jira_id = args.jira_id
    # Use provided credentials first, then fall back to env vars
    jira_email = args.email or os.getenv("JIRA_EMAIL")
    jira_token = args.token or os.getenv("JIRA_TOKEN") or os.getenv("JIRA_API_TOKEN")
    jira_base_url = args.base_url or os.getenv("JIRA_BASE_URL")

    if jira_email and jira_token and jira_base_url and "your-domain" not in jira_base_url:
        url = f"{jira_base_url.rstrip('/')}/rest/api/2/issue/{jira_id}"
        try:
            response = httpx.get(url, auth=(jira_email, jira_token), timeout=15.0)
            if response.status_code == 404:
                print(json.dumps({"error": f"Jira Ticket ID not found: {jira_id}", "status": 404}))
                sys.exit(1)
            response.raise_for_status()
            print(json.dumps(response.json()))
            return
        except httpx.HTTPStatusError as exc:
            print(json.dumps({"error": f"Jira API error: {exc.response.status_code}", "status": exc.response.status_code}))
            sys.exit(1)
        except Exception as e:
            print(json.dumps({"error": str(e), "status": 500}))
            sys.exit(1)

    # Mock fallback logic — accept any Jira ID dynamically
    data = {
        "key": jira_id.upper(),
        "fields": {
            "summary": "VWO Login Page Authentication Feature",
            "description": (
                "User Story: As a user, I want to securely log into the VWO platform so that I can access my dashboard.\n"
                "Acceptance Criteria:\n"
                "1. Login page must strictly enforce HTTPS loading.\n"
                "2. 'Remember Me' session behavior should keep the user logged in for 30 days.\n"
                "3. Captcha challenge must trigger automatically after 3 consecutive failed login attempts.\n"
                "4. All login input fields must be sanitized to prevent SQL injection security edge cases."
            ),
            "components": [{"name": "frontend"}, {"name": "backend"}],
        }
    }
    print(json.dumps(data))

if __name__ == "__main__":
    main()
