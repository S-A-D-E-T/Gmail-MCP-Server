"""Legacy email_mcp tool and REST compatibility."""

from __future__ import annotations

from typing import Any

from gmail_mcp_serve.gmail_stdio import call_gmail_tool, credentials_configured


def map_legacy_tool(tool: str, arguments: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if tool == "email_send":
        to = str(arguments.get("to") or "").strip()
        if not to:
            raise ValueError("to is required")
        return "send_email", {
            "to": [to],
            "subject": str(arguments.get("subject") or ""),
            "body": str(arguments.get("body") or ""),
        }
    return tool, arguments


def invoke_legacy_tool(tool: str, arguments: dict[str, Any] | None = None) -> Any:
    mapped_tool, mapped_args = map_legacy_tool(tool, dict(arguments or {}))
    return call_gmail_tool(mapped_tool, mapped_args)


def email_status() -> dict[str, Any]:
    from gmail_mcp_serve.gmail_stdio import credentials_paths

    oauth, creds = credentials_paths()
    configured = credentials_configured()
    return {
        "configured": configured,
        "provider": "gmail",
        "oauth_path": str(oauth),
        "credentials_path": str(creds),
    }


def send_plain_email(*, to: str, subject: str, body: str) -> dict[str, Any]:
    to = (to or "").strip()
    if not to:
        raise ValueError("to is required")
    result = call_gmail_tool(
        "send_email",
        {"to": [to], "subject": subject or "", "body": body or ""},
    )
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(str(result.get("message") or result.get("error")))
    return {"status": "sent", "to": to, "result": result}
