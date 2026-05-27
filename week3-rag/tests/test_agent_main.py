from fastapi.testclient import TestClient
from unittest.mock import patch
from agent_main import app
import httpx
from anthropic import RateLimitError, APIConnectionError, AuthenticationError


client = TestClient(app)


def test_happy_path():
    with patch("agent_main.run_agent") as mock_run:
        mock_run.return_value = "Fake answer"
        response = client.post(
            "/agent-chat",
            json={"message": "hello", "session_id": "test-session"},
        )
    assert response.status_code == 200
    assert response.json()["answer"] == "Fake answer"
    assert response.json()["session_id"] == "test-session"


def _fake_response(status: int) -> httpx.Response:
    """Minimal httpx.Response so Anthropic error classes can be instantiated."""
    return httpx.Response(
        status_code=status,
        request=httpx.Request("POST", "http://test"),
    )


def test_rate_limit_returns_429():
    err = RateLimitError("rate limited", response=_fake_response(429), body=None)
    with patch("agent_main.run_agent") as mock_run:
        mock_run.side_effect = err
        response = client.post(
            "/agent-chat",
            json={"message": "hello", "session_id": "test-session"},
        )
    assert response.status_code == 429


def test_connection_error_returns_503():
    err = APIConnectionError(
        message="connection failed",
        request=httpx.Request("POST", "http://test"),
    )
    with patch("agent_main.run_agent") as mock_run:
        mock_run.side_effect = err
        response = client.post(
            "/agent-chat",
            json={"message": "hello", "session_id": "test-session"},
        )
    assert response.status_code == 503


def test_auth_error_returns_500():
    err = AuthenticationError("auth failed", response=_fake_response(401), body=None)
    with patch("agent_main.run_agent") as mock_run:
        mock_run.side_effect = err
        response = client.post(
            "/agent-chat",
            json={"message": "hello", "session_id": "test-session"},
        )
    assert response.status_code == 500


def test_generic_exception_returns_500():
    with patch("agent_main.run_agent") as mock_run:
        mock_run.side_effect = Exception("kaboom")
        response = client.post(
            "/agent-chat",
            json={"message": "hello", "session_id": "test-session"},
        )
    assert response.status_code == 500