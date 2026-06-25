# Hermes Suite Architecture — All-in-One Hermes Container

| Field | Value |
|---|---|
| **Origin** | [sunnysktsang/hermes-suite](https://github.com/sunnysktsang/hermes-suite) |
| **Source** | `sources/hermes-suite/` |
| **Stack** | Docker/Podman, Python, Supervisor, Hermes Agent, Hermes WebUI |
| **Runtime** | Any container host with Docker or Podman (amd64 + arm64) |

## Overview

Hermes Suite packages three related Hermes services into a single container managed by supervisord. It exists to solve UID/GID sharing issues in Podman v3.4.4 where multiple containers cannot share the same user namespace. By running all services in one container, they naturally share filesystem, user, and process namespace.

## Container Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  PID 1: /opt/supervisor/venv/bin/supervisord               │
│  Config: supervisord.conf                                   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [program:hermes-gateway]                            │   │
│  │ command: hermes gateway run                         │   │
│  │ port: 8642                                          │   │
│  │ priority: 10                                        │   │
│  │ autorestart: true                                   │   │
│  │ depends: -                                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [program:hermes-dashboard]                          │   │
│  │ command: hermes dashboard --host 0.0.0.0            │   │
│  │ port: 9119                                          │   │
│  │ priority: 20 (starts after gateway)                 │   │
│  │ autorestart: true                                   │   │
│  │ depends: hermes-gateway (via readiness)             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [program:hermes-webui]                              │   │
│  │ command: python server.py (in venv)                 │   │
│  │ port: 8787                                          │   │
│  │ priority: 20 (starts after gateway)                 │   │
│  │ autorestart: true                                   │   │
│  │ depends: hermes-gateway (via readiness)             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Volumes:                                                   │
│  /opt/data    ← ~/.hermes (config, skills, memories)        │
│  /workspace   ← ~/workspace (project files)                 │
│  /etc/localtime (readonly for time sync)                    │
└─────────────────────────────────────────────────────────────┘
```

## Build Process

The Dockerfile builds in stages:

1. **Base** — `nousresearch/hermes-agent:latest` (contains Python 3.13, Node.js, npm, Playwright, agent code, built-in dashboard)
2. **System packages** — sudo, git, nano, curl, net-tools, procps
3. **Playwright** — installs Chromium browser for browser toolset
4. **Supervisor** — pip install supervisord into dedicated venv at `/opt/supervisor`
5. **Hermes WebUI** — clones from GitHub, creates venv at `/opt/hermes-webui/venv`, installs agent Python deps alongside
6. **WhatsApp bridge** (optional) — installs when `ENABLE_WHATSAPP_BRIDGE=true`

## Startup Sequence (`start.sh`)

1. Accept or detect container runtime (auto/podman/docker)
2. Remap UID 10000 to host subuid for rootless Podman compatibility
3. Create directory structure under `/opt/data`
4. Bootstrap config: copy default `.env` and `config.yaml` from hermes-agent examples if not present
5. Copy WebUI config if absent
6. Launch supervisord as PID 1

## Version Management

Component versions are managed through build args and `versions.env`:

| Component | Source Repository | Version Format |
|---|---|---|
| Hermes Agent | `nousresearch/hermes-agent` | Date-based: `v2026.6.19` |
| Hermes WebUI | `nesquena/hermes-webui` | Semver: `v0.51.625` |

Suite tags follow the pattern `{agent_date}-{webui_semver}` (e.g., `2026.6.19-0.51.625`).

## Network Architecture

```
Host                           Container
┌─────────────────┐          ┌──────────────────────────────┐
│  localhost:8642  │◄────────┤► hermes-gateway (port 8642)  │
│  localhost:8787  │◄────────┤► hermes-webui  (port 8787)   │
│  localhost:9119  │◄────────┤► hermes-dash   (port 9119)   │
└─────────────────┘          └──────────────────────────────┘
    agent_net (10.99.0.0/24) bridge
```

## Data Flow

```
User browser (WebUI at :8787)
        │ HTTP / WebSocket
        ▼
┌──────────────┐
│ Hermes WebUI │ ── HTTP API ──► ┌────────────────┐
│ (Flask app)  │                 │ Hermes Gateway │ ◄── CLI, Telegram, cron
└──────────────┘                 │ (port 8642)    │
        │                        └───────┬────────┘
        │                                │
        ▼                                ▼
┌──────────────┐                ┌────────────────┐
│  Dashboard   │                │  LLM Providers  │
│  (port 9119) │                │  (OpenAI, etc.) │
└──────────────┘                └────────────────┘
```

All services share `/opt/data` for config, sessions, skills, and memories.

## Resource Constraints

Default Docker Compose config sets 4GB memory limit. CPU is unbounded by default.

## Related

- [[hermes-suite]] — Wiki entry
- [Deployment: hermes-suite](domains/deployment/hermes-suite-deployment.md)
- [[hermes-agent]] — Core agent runtime
- [[hermes-agent-docker]] — Simpler single-service Docker packaging
