.PHONY: help sync sync-prod test mcp serve docker-build docker-run

.DEFAULT_GOAL := help

UV ?= uv
IMAGE ?= email-mcp:latest
SERVE_PORT ?= 8789

help: ## Показать цели
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

sync: ## Установить зависимости (dev)
	$(UV) sync --extra dev

sync-prod: ## Зависимости для Docker (без dev)
	$(UV) sync --frozen --no-dev

test: sync ## Запустить pytest
	$(UV) run pytest

mcp: ## MCP stdio (Cursor / Claude Desktop)
	$(UV) run email-mcp

serve: ## HTTP MCP API (:$(SERVE_PORT))
	$(UV) run email-mcp-serve

docker-build: ## Собрать Docker-образ
	docker build -t $(IMAGE) .

docker-run: ## Запустить контейнер (HTTP serve)
	docker run --rm -p $(SERVE_PORT):$(SERVE_PORT) $(IMAGE)
