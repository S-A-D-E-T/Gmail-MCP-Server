# gmail-mcp-server

HTTP serve для SADET/jobs_mcp: совместимость с API **email_mcp** (`/email/v1/send`, `email_send` MCP tool) поверх Node [Gmail MCP](src/index.ts).

## Локально

```bash
uv sync --extra dev
uv run gmail-mcp-serve
```

Требуется OAuth: `~/.gmail-mcp/gcp-oauth.keys.json` и `credentials.json` (см. upstream README).

## Docker

```bash
docker build -t gmail-mcp-server:latest .
docker run --rm -p 8789:8789 \
  -v gmail-mcp-credentials:/root/.gmail-mcp \
  gmail-mcp-server:latest
```
