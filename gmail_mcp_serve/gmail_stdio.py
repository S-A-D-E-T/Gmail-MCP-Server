"""Call Gmail MCP (Node) over stdio."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent


def _node_script() -> tuple[str, list[str]]:
    node = os.environ.get("GMAIL_MCP_NODE", "node").strip() or "node"
    script = os.environ.get("GMAIL_MCP_SCRIPT", "/app/node/dist/index.js").strip()
    return node, [script]


def credentials_paths() -> tuple[Path, Path]:
    oauth = Path(
        os.environ.get(
            "GMAIL_OAUTH_PATH",
            str(Path.home() / ".gmail-mcp" / "gcp-oauth.keys.json"),
        )
    )
    creds = Path(
        os.environ.get(
            "GMAIL_CREDENTIALS_PATH",
            str(Path.home() / ".gmail-mcp" / "credentials.json"),
        )
    )
    return oauth, creds


def credentials_configured() -> bool:
    oauth, creds = credentials_paths()
    return oauth.is_file() and creds.is_file()


def _parse_tool_result(result: Any) -> Any:
    if getattr(result, "isError", False):
        text = " ".join(
            block.text
            for block in getattr(result, "content", [])
            if isinstance(block, TextContent)
        )
        raise RuntimeError(text or "gmail mcp tool error")

    chunks: list[str] = []
    for block in getattr(result, "content", []):
        if isinstance(block, TextContent):
            chunks.append(block.text)
    text = "\n".join(chunks).strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"text": text}


async def call_gmail_tool_async(tool: str, arguments: dict[str, Any]) -> Any:
    if not credentials_configured():
        raise RuntimeError(
            "Gmail OAuth is not configured (missing gcp-oauth.keys.json or credentials.json)"
        )
    command, args = _node_script()
    params = StdioServerParameters(command=command, args=args, env=os.environ.copy())
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool, arguments=arguments)
            return _parse_tool_result(result)


def call_gmail_tool(tool: str, arguments: dict[str, Any] | None = None) -> Any:
    return asyncio.run(call_gmail_tool_async(tool, dict(arguments or {})))
