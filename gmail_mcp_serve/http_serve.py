"""HTTP serve entry with LGTM observability (sadet_obs)."""

from __future__ import annotations

from sadet_obs import serve

from gmail_mcp_serve.http_app import build_gmail_app


def main() -> None:
    serve(
        build_gmail_app,
        service_name="gmail-mcp-serve",
        host_env="GMAIL_MCP_SERVE_HOST",
        port_env="GMAIL_MCP_SERVE_PORT",
        default_port=8789,
    )


if __name__ == "__main__":
    main()
