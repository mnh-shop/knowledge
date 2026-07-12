---
name: hermes-agent-docker-api
description: "Hermes Agent Docker image API — entrypoint, environment variables, volume mounts, health check"
source: sources/hermes-agent-docker/
tags: [hermes-agent-docker, api, docker, deployment]
---

# Hermes Agent Docker — API Reference

The Hermes Agent Docker image provides a containerized deployment surface for the Hermes Agent. Its API is defined by the Dockerfile's entrypoint contract: environment variables for configuration, volume mounts for persistent data, health check endpoints, and signal handling for lifecycle management.

## Key API Facts

| Feature | Detail |
|---------|--------|
| **Base image** | Alpine Linux (slim) |
| **Entrypoint** | `/entrypoint.sh` — bootstraps Hermes Agent process |
| **Process** | Hermes Agent Node.js MCP server |
| **Port** | `3000` (configurable) — MCP/SSE endpoint |
| **Health check** | HTTP `GET /health` or process-level `HEALTHCHECK` instruction |
| **Signal handling** | `SIGTERM` → graceful shutdown |
| **Storage** | `/data` volume for persistent state |
| **Config** | Environment variables + optional mounted `config.json` |

## Entrypoint Contract

The container starts via `/entrypoint.sh` which:

1. Reads environment variables for configuration
2. Loads optional mounted config file (`/config/hermes-agent.json`)
3. Sets up logging and data directories
4. Starts the Hermes Agent Node.js process
5. Handles SIGTERM for graceful container shutdown

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HERMES_PORT` | No | `3000` | HTTP server listen port |
| `HERMES_HOST` | No | `0.0.0.0` | Bind address |
| `HERMES_LOG_LEVEL` | No | `info` | Log level (debug/info/warn/error) |
| `HERMES_DATA_DIR` | No | `/data` | Persistent data directory |
| `HERMES_CONFIG_PATH` | No | `/config/hermes-agent.json` | Config file path |
| `HERMES_API_KEY` | No | — | API authentication key/token |
| `HERMES_CORS_ORIGIN` | No | `*` | CORS allowed origins |
| `HERMES_MAX_PAYLOAD` | No | `1mb` | Max request payload size |
| `HERMES_RATE_LIMIT` | No | `100` | Requests per minute limit |
| `NODE_ENV` | No | `production` | Node.js environment |
| `TZ` | No | `UTC` | Timezone |

## Volume Mounts

| Mount Point | Purpose |
|-------------|---------|
| `/data` | Persistent data (logs, cache, state) |
| `/config` | Configuration directory (bind mount `hermes-agent.json`) |
| `/certs` | TLS certificates (optional, for HTTPS) |

## Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `3000` | HTTP | MCP/SSE server endpoint (configurable via `HERMES_PORT`) |

## Health Check

The Docker image includes a built-in `HEALTHCHECK` instruction:

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:${HERMES_PORT:-3000}/health || exit 1
```

The `/health` endpoint returns:

```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime": 12345
}
```

## MCP/SSE Endpoint

The primary service endpoint serves the Model Context Protocol over SSE:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check (liveness) |
| `/mcp` | GET | SSE stream for MCP messages |
| `/mcp` | POST | Send MCP message |
| `/mcp/tools` | GET | List available MCP tools |
| `/mcp/resources` | GET | List available MCP resources |

## Signal Handling

| Signal | Behavior |
|--------|----------|
| `SIGTERM` | Graceful shutdown — flush data, close connections, exit |
| `SIGINT` | Immediate shutdown (Ctrl+C) |
| `SIGHUP` | Reload configuration (if supported by agent version) |

## Deployment Example

```bash
# Run with defaults
docker run -d \
  --name hermes-agent \
  -p 3000:3000 \
  -v hermes-data:/data \
  -e HERMES_LOG_LEVEL=debug \
  ghcr.io/hermes-agent/hermes-agent:latest

# With custom config and API key
docker run -d \
  --name hermes-agent \
  -p 8080:3000 \
  -v /path/to/config:/config:ro \
  -v hermes-data:/data \
  -e HERMES_API_KEY=sk-abc123 \
  -e HERMES_PORT=3000 \
  ghcr.io/hermes-agent/hermes-agent:latest
```

## Podman Quadlet Example

```yaml
# hermes-agent.container
[Container]
Image=ghcr.io/hermes-agent/hermes-agent:latest
ContainerName=hermes-agent
PublishPort=3000:3000
Volume=hermes-data:/data
Volume=/path/to/config:/config:ro
Environment=HERMES_LOG_LEVEL=info
Environment=HERMES_API_KEY=${HERMES_API_KEY}

[Service]
Restart=always

[Install]
WantedBy=default.target
```

## Related

- [[hermes-agent-docker]] — Source repository, Dockerfile, and wiki
- [[hermes-agent]] — Core agent platform
- [[podman]] — Container engine for deployment (alternative to Docker)
- [[tank-os]] — bootc-based OS image that can host Hermes containers
