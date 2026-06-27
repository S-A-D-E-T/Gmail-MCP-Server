"""HTTP API gmail-mcp-serve (legacy email_mcp + MCP proxy to Gmail Node server)."""

from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sadet_obs import log_api, service_logger

from gmail_mcp_serve.compat import email_status, invoke_legacy_tool, send_plain_email

log = service_logger(__name__)


class CallBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    tool: str = ""
    arguments: dict[str, Any] = {}


class SendBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    to: str
    subject: str = ""
    body: str = ""
    smtp: dict[str, Any] | None = None


def build_gmail_app() -> FastAPI:
    app = FastAPI(title="Gmail MCP Serve")

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"ok": True, "service": "gmail-mcp-serve"}

    @app.get("/email/v1/status")
    def status() -> dict[str, Any]:
        return email_status()

    @app.post("/email/v1/send")
    def send_email(payload: SendBody = Body()) -> dict[str, Any]:
        if payload.smtp:
            log.warning("email_send smtp override ignored (Gmail OAuth only)")
        log_api(log, "email_send", to=payload.to, subject_len=len(payload.subject or ""))
        try:
            result = send_plain_email(
                to=payload.to,
                subject=payload.subject,
                body=payload.body,
            )
            log_api(log, "email_send_ok", to=payload.to)
            return result
        except ValueError as exc:
            log.warning("email_send_failed to=%s error=%s", payload.to, exc)
            raise HTTPException(400, str(exc)) from exc
        except RuntimeError as exc:
            log.exception("email_send_error to=%s", payload.to)
            raise HTTPException(503, str(exc)) from exc

    @app.post("/mcp/v1/call")
    def mcp_call(body: CallBody) -> dict[str, Any]:
        tool = (body.tool or "").strip()
        if not tool:
            raise HTTPException(400, "tool is required")
        log.info("mcp_call tool=%s arg_keys=%s", tool, sorted((body.arguments or {}).keys()))
        try:
            result = invoke_legacy_tool(tool, body.arguments)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(503, str(exc)) from exc
        except Exception:
            log.exception("mcp_call failed tool=%s", tool)
            raise
        log.info("mcp_call ok tool=%s", tool)
        return result if isinstance(result, dict) else {"result": result}

    return app
