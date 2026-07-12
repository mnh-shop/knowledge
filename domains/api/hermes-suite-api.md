---
name: hermes-suite-api
description: "Hermes Suite API — supervisord management, container orchestration, multi-service health endpoints"
source: sources/hermes-suite/
tags: [hermes-suite, api, hermes-agent, docker]
---

# Hermes Suite API

Hermes Suite exposes API surfaces through three integrated services in a single container: **Gateway** (port 8642), **Dashboard** (port 9119), and **WebUI** (port 8787), managed by supervisord.

## Overview

A single-container deployment combining Hermes gateway, built-in dashboard, and browser WebUI. Services are managed via supervisord with XML-RPC control, shell scripts, and Docker Compose lifecycle commands.

## API Surface

**Gateway API (port 8642):**
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness probe |
| `POST` | `/v1/chat/completions` | OpenAI Chat Completions |
| `POST` | `/v1/responses` | OpenAI Responses API |
| `POST` | `/v1/runs` | Long-form run submission |
| `GET` | `/api/sessions` | List agent sessions |

**Dashboard API (port 9119):**
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/auth/providers` | Auth providers list |
| `POST` | `/auth/password-login` | Rate-limited login |
| `GET` | `/api/auth/me` | Current session |

**Supervisord XML-RPC (internal port 9001):**
- `supervisor.startProcess('hermes-gateway')` — start a managed service
- `supervisor.stopProcess('hermes-dashboard')` — stop a managed service
- `supervisor.getAllProcessInfo()` — status of all 3 services
- `supervisor.getState()` — supervisord global state

**Container Lifecycle Scripts:**
| Script | Action |
|--------|--------|
| `./up.sh` | `podman-compose up -d` |
| `./down.sh` | `podman-compose down` |
| `./logs.sh` | `podman logs -f hermes-suite` |
| `./build.sh` | `podman build -t hermes-suite .` |

## Authentication

Gateway requires Bearer token (`API_SERVER_KEY` env var). Dashboard uses password or OAuth login. Supervisord XML-RPC is internal-only (no external exposure).

## Usage

```bash
# Start the suite
./up.sh

# Health check all services
curl http://localhost:8642/health
curl http://localhost:9119/health

# Pin component versions
echo "AGENT_VERSION=v2026.6.19" > versions.env
echo "WEBUI_VERSION=v0.51.625" >> versions.env
./build.sh
```

## Related

- [[domains/api/INDEX|api]]
- [[hermes-suite]] — Full suite documentation
- [[hermes-agent]] — Core gateway runtime
- [[hermes-workspace]] — MCP hub server component
- [[hermes-agent-docker]] — Single-service Docker packaging
