# syntax=docker/dockerfile:1
FROM node:20-bookworm AS nodebuild

WORKDIR /app/node
COPY package.json package-lock.json tsconfig.json ./
COPY src ./src
RUN npm ci

FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    PIP_NO_CACHE_DIR=1 \
    GMAIL_MCP_SERVE_HOST=0.0.0.0 \
    GMAIL_MCP_SERVE_PORT=8789 \
    GMAIL_MCP_SCRIPT=/app/node/dist/index.js \
    GMAIL_OAUTH_PATH=/root/.gmail-mcp/gcp-oauth.keys.json \
    GMAIL_CREDENTIALS_PATH=/root/.gmail-mcp/credentials.json

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=node:20-bookworm /usr/local/bin/node /usr/local/bin/node
COPY --from=nodebuild /app/node/dist /app/node/dist
COPY --from=nodebuild /app/node/node_modules /app/node/node_modules
COPY --from=nodebuild /app/node/package.json /app/node/package.json

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock README.md ./
COPY gmail_mcp_serve ./gmail_mcp_serve

RUN --mount=type=secret,id=git_token \
    set -eux; \
    git config --global url."https://x-access-token:$(cat /run/secrets/git_token)@github.com/".insteadOf "https://github.com/"; \
    uv sync --frozen --no-dev --no-install-project --no-editable
RUN uv pip install --system --no-deps .

EXPOSE 8789
HEALTHCHECK CMD curl -fsS http://127.0.0.1:8789/health || exit 1
CMD ["gmail-mcp-serve"]
