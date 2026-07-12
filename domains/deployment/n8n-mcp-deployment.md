---
name: n8n-mcp-deployment
tags: [n8n-mcp, deployment, n8n, mcp]
description: n8n-mcp — Deployment
source: sources/n8n-mcp/
---

# n8n-mcp — Deployment

**Source:** `sources/n8n-mcp/` · `sources/n8n-mcp/Dockerfile` · `sources/n8n-mcp/docker-compose.yml`

## Overview

n8n-mcp is a Model Context Protocol (MCP) server that provides AI assistants with comprehensive access to n8n's 1,845+ node ecosystem (816 core + 1,029 community). It exposes node documentation, parameter schemas, workflow validation, and n8n API management tools through MCP.

Supports multiple deployment modes:
- **stdio** — Direct integration with Claude Desktop, Claude Code, VS Code
- **HTTP** — Remote MCP server with SSE transport (production)
- **Docker** — Containerized deployment via Docker Compose
- **Railway** — One-click cloud deploy
- **Single-session HTTP** — Session-persistent HTTP for multi-tenant setups

## Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 256 MB | 512 MB |
| CPU | 1 core | 2 cores |
| Storage | 500 MB (DB + deps) | 2 GB (templates + logs) |
| Runtime | Node.js 22+ | Docker/Podman for containerized |
| Database | SQLite (bundled) | SQLite (auto-managed) |
| n8n instance | Optional (for management tools) | n8n v2+ with API key |

## Deployment Steps

### 1. Quick Start (stdio — Local MCP Client)

```bash
# Clone and install
git clone https://github.com/czlonkowski/n8n-mcp.git
cd n8n-mcp
npm install

# Build and set up node database
npm run build
npm run rebuild

# Start in stdio mode (for Claude Desktop, VS Code, etc.)
npm start
```

The server exposes MCP tools over stdio. Configure your MCP client to point to this process.

### 2. HTTP Mode (Production)

```bash
# Start HTTP server
npm run start:http

# Default: http://127.0.0.1:3000
# Requires AUTH_TOKEN environment variable
```

### 3. Docker Compose (Standalone)

```yaml
version: '3.8'
services:
  n8n-mcp:
    image: ghcr.io/czlonkowski/n8n-mcp:latest
    container_name: n8n-mcp
    restart: unless-stopped
    environment:
      # Mode configuration
      MCP_MODE: ${MCP_MODE:-http}
      AUTH_TOKEN: ${AUTH_TOKEN:?AUTH_TOKEN is required for HTTP mode}

      # Application settings
      NODE_ENV: ${NODE_ENV:-production}
      LOG_LEVEL: ${LOG_LEVEL:-info}
      PORT: ${PORT:-3000}

      # Database
      NODE_DB_PATH: ${NODE_DB_PATH:-/app/data/nodes.db}
      REBUILD_ON_START: ${REBUILD_ON_START:-false}

      # Optional: n8n API configuration (enables 16 management tools)
      # N8N_API_URL: ${N8N_API_URL}
      # N8N_API_KEY: ${N8N_API_KEY}
      # N8N_API_TIMEOUT: ${N8N_API_TIMEOUT:-30000}
      # N8N_API_MAX_RETRIES: ${N8N_API_MAX_RETRIES:-3}

      # Telemetry: opt-out
      N8N_MCP_TELEMETRY_DISABLED: ${N8N_MCP_TELEMETRY_DISABLED:-false}
    volumes:
      - n8n-mcp-data:/app/data
    ports:
      - "${PORT:-3000}:${PORT:-3000}"
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
    healthcheck:
      test: ["CMD", "sh", "-c", "curl -f http://127.0.0.1:$${PORT:-3000}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  n8n-mcp-data:
    driver: local
```

### 4. Docker Compose (with n8n Instance)

For full workflow management tools (create, read, update, delete, execute workflows):

```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "${N8N_PORT:-5678}:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_BASIC_AUTH_USER:-admin}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_BASIC_AUTH_PASSWORD}
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY:?required}
    volumes:
      - n8n_data:/home/node/.n8n
    healthcheck:
      test: ["CMD", "sh", "-c", "wget --quiet --spider --tries=1 --timeout=10 http://localhost:5678/healthz || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  n8n-mcp:
    image: ghcr.io/czlonkowski/n8n-mcp:latest
    container_name: n8n-mcp
    restart: unless-stopped
    ports:
      - "${MCP_PORT:-3000}:${MCP_PORT:-3000}"
    environment:
      - NODE_ENV=production
      - N8N_MODE=true
      - MCP_MODE=http
      - PORT=${MCP_PORT:-3000}
      - N8N_API_URL=http://n8n:5678
      - N8N_API_KEY=${N8N_API_KEY:-}
      - AUTH_TOKEN=${MCP_AUTH_TOKEN:?required}
      - LOG_LEVEL=${LOG_LEVEL:-info}
    volumes:
      - mcp_data:/app/data
    depends_on:
      n8n:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "sh", "-c", "curl -f http://127.0.0.1:$${MCP_PORT:-3000}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  n8n_data:
  mcp_data:
```

### 5. Podman Quadlet

Save as `~/.config/containers/systemd/n8n-mcp.container`:

```ini
[Container]
Image=ghcr.io/czlonkowski/n8n-mcp:latest
ContainerName=n8n-mcp
PublishPort=3000:3000
Volume=n8n-mcp-data:/app/data
Environment=MCP_MODE=http
Environment=AUTH_TOKEN=%%AUTH_TOKEN%%
Environment=NODE_ENV=production
Environment=LOG_LEVEL=%%LOG_LEVEL%%
Environment=PORT=3000
Environment=N8N_MCP_TELEMETRY_DISABLED=%%N8N_MCP_TELEMETRY_DISABLED%%
HealthCmd=sh -c 'curl -f http://127.0.0.1:3000/health'
HealthInterval=30s
HealthRetries=3
AutoUpdate=registry

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now n8n-mcp.service
```

### 6. Image Details

The Docker image uses a multi-stage build:

1. **Builder stage** (`node:22-alpine`): TypeScript compilation only
2. **Runtime stage** (`node:22-alpine`): Minimal dependencies (`curl`, `su-exec`) + compiled dist + pre-built SQLite database

Key characteristics:
- **Pre-bundled database**: `data/nodes.db` ships inside the image with all 1,845+ nodes indexed
- **Seed copy**: `.db-seed/nodes.db` exists for restoring when volume mounts mask the bundled DB
- **Non-root user**: Unpredictable UID/GID per build for security
- **Telemetry opt-out**: Set `N8N_MCP_TELEMETRY_DISABLED=true`

### 7. Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_MODE` | `http` | Server mode (`http` or `stdio`) |
| `AUTH_TOKEN` | — | **Required** for HTTP mode |
| `PORT` | `3000` | HTTP server port |
| `NODE_ENV` | `production` | Node environment |
| `LOG_LEVEL` | `info` | Logging verbosity |
| `NODE_DB_PATH` | `/app/data/nodes.db` | SQLite database path |
| `REBUILD_ON_START` | `false` | Rebuild node DB from n8n packages on start |
| `N8N_API_URL` | — | n8n instance URL (enables management tools) |
| `N8N_API_KEY` | — | n8n API key for management tools |
| `N8N_API_TIMEOUT` | `30000` | n8n API request timeout |
| `N8N_API_MAX_RETRIES` | `3` | n8n API retry count |
| `N8N_MCP_TELEMETRY_DISABLED` | `false` | Opt out of anonymous telemetry |

### 8. MCP Tools Available

Once deployed, the server exposes these tool categories:

| Category | Tools |
|----------|-------|
| **Discovery** | `n8n_list_available_tools`, `n8n_search_nodes`, `n8n_get_node_essentials`, `n8n_get_node_info`, `n8n_get_node_documentation`, `n8n_search_node_properties`, `n8n_list_ai_tools` |
| **Configuration** | `n8n_validate_node_operation`, `n8n_validate_node_minimal`, `n8n_generate_workflow`, `n8n_generate_workflow_doc` |
| **Validation** | `n8n_validate_workflow`, `n8n_update_partial_workflow` |
| **Management** | `n8n_create_workflow`, `n8n_read_workflow`, `n8n_update_workflow`, `n8n_delete_workflow`, `n8n_activate_workflow`, `n8n_deactivate_workflow`, `n8n_list_workflows`, `n8n_execute_workflow`, `n8n_get_execution`, `n8n_audit_instance`, `n8n_diagnostic`, `n8n_health_check` |

Management tools require `N8N_API_URL` and `N8N_API_KEY` to be configured.

## Persistent Storage

| Path | Contents |
|------|----------|
| `/app/data/nodes.db` | SQLite node database (FTS5 full-text search) |
| `/app/data/skills/` | Skills data for Claude integration |
| `/app/data/templates/` | Workflow template cache (2,352+ templates) |

## Related

- [[n8n-mcp]] — n8n-mcp wiki entry (architecture, tools, features)
- [[n8n]] — Overall n8n platform documentation
- [[mcp]] — Model Context Protocol specification
- [[n8n-workflows]] — Workflow catalog and template collection
- [[n8n-nodes]] — n8n node reference
- [[domains/api/INDEX|api]] — HTTP API integration patterns
