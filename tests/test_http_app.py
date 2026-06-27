from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from gmail_mcp_serve.http_app import build_gmail_app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("GMAIL_OAUTH_PATH", "/tmp/gmail-oauth.json")
    monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", "/tmp/gmail-creds.json")
    return TestClient(build_gmail_app())


def test_health(client: TestClient) -> None:
    assert client.get("/health").json()["ok"] is True


def test_status_not_configured(client: TestClient) -> None:
    assert client.get("/email/v1/status").json()["configured"] is False


def test_send_validation(client: TestClient) -> None:
    r = client.post("/email/v1/send", json={"to": "", "subject": "s", "body": "b"})
    assert r.status_code == 400


def test_mcp_email_send_maps_to_gmail(client: TestClient) -> None:
    with patch(
        "gmail_mcp_serve.compat.call_gmail_tool",
        return_value={"id": "msg-1"},
    ) as mocked:
        r = client.post(
            "/mcp/v1/call",
            json={
                "tool": "email_send",
                "arguments": {"to": "a@b.com", "subject": "Hi", "body": "x"},
            },
        )
    assert r.status_code == 200
    mocked.assert_called_once_with(
        "send_email",
        {"to": ["a@b.com"], "subject": "Hi", "body": "x"},
    )
