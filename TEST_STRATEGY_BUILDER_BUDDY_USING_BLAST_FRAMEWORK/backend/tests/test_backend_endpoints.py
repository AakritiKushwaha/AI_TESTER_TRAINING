import os
import json
import sys
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Ensure environment variables are set for the test run
os.environ.setdefault('JIRA_DOMAIN', 'example.atlassian.net')
os.environ.setdefault('JIRA_EMAIL', 'test@example.com')
os.environ.setdefault('JIRA_API_TOKEN', 'dummy_token')
os.environ.setdefault('GROQ_API_KEY', 'dummy_groq_key')

# Import the FastAPI app after setting env vars
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

client = TestClient(app)

def test_fetch_jira_success():
    jira_id = "TEST-123"
    response = client.get(f"/fetch-jira/{jira_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == jira_id
    assert "summary" in data
    assert "description" in data

def test_generate_strategy_success():
    # Mock the httpx.post call used in generate_strategy.py
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": json.dumps({"sections": [{"title": "Intro", "content": "Test strategy"}]})}}]
    }
    mock_response.raise_for_status.return_value = None
    with patch('httpx.post', return_value=mock_response):
        payload = {
            "jira_data": {
                "id": "TEST-123",
                "summary": "Sample summary",
                "description": "Sample description",
                "components": []
            }
        }
        response = client.post("/generate-strategy", json=payload)
        assert response.status_code == 200
        result = response.json()
        assert "sections" in result
        assert isinstance(result["sections"], list)
        assert result["sections"][0]["title"] == "Intro"
