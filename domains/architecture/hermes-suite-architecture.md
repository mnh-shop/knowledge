---
name: hermes-suite-architecture
tags: [agent-gateway, architecture, container, dashboard, docker, git, hermes-agent, messaging, multi-platform, podman, typescript]
description: "Hermes Suite architecture: all-in-one Hermes container combining gateway, built-in dashboard, and browser-based WebUI"
source: sources/hermes-suite/
---

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
│  PID 1: /opt/supervisor/bin/supervisord                    │
│  Config: supervisord.conf                                   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [program:hermes-gateway]                            │   │
│  │ command: /opt/hermes/.venv/bin/hermes gateway run   │   │
│  │ port: 8642                                          │   │
│  │ priority: 10                                        │   │
│  │ user: hermes · autostart · autorestart              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [program:hermes-dashboard]                          │   │
│  │ command: hermes dashboard --host 0.0.0.0 --port     │   │
│  │          9119 --no-open                             │   │
│  │ port: 9119                                          │   │
│  │ priority: 20 (after gateway) · startsecs: 5         │   │
│  │ user: hermes · autostart · autorestart              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [program:hermes-webui]                              │   │
│  │ command: /opt/hermes-webui/venv/bin/python          │   │
│  │          /opt/hermes-webui/server.py                │   │
│  │ port: 8787                                          │   │
│  │ priority: 30 · startsecs: 5                         │   │
│  │ user: hermes · autostart · autorestart              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Volumes:                                                   │
│  /opt/data    ← ~/.hermes (config, skills, memories)        │
│  /workspace   ← ~/workspace (project files)                 │
│  /etc/localtime (readonly for time sync)                    │
└─────────────────────────────────────────────────────────────┘
```

### Supervisord program map (supervisord.conf)

| Program | Command | Port | Priority | Key settings |
|---|---|---|---|---|
| `hermes-gateway` | `/opt/hermes/.venv/bin/hermes gateway run` | 8642 | 10 | `user=hermes`, autostart, autorestart |
| `hermes-dashboard` | `hermes dashboard --host 0.0.0.0 --port 9119 --no-open` | 9119 | 20 | `user=hermes`, `startsecs=5` |
| `hermes-webui` | `/opt/hermes-webui/venv/bin/python /opt/hermes-webui/server.py` | 8787 | 30 | `user=hermes`, `startsecs=5`, env `HERMES_WEBUI_STATE_DIR=/opt/data/webui` |

All three run as `user=hermes` with `autostart=true` and `autorestart=true`. When supervisord runs as root (Docker path), `user=` drops privileges for children; when supervisord itself runs as hermes (Podman path), `user=hermes` is a harmless no-op (setuid to self). Supervisor socket at `/var/run/supervisor/supervisor.sock`; logs stream to `/dev/stdout` + `/var/log/supervisor/`.

The dashboard program (supervisord.conf:53-57) documents that upstream v2026.7.1 removed unauthenticated public access — `--insecure` is now a no-op, and BasicAuth credentials come from the inherited `HERMES_DASHBOARD_BASIC_AUTH_USERNAME`/`_PASSWORD` env vars set by `start.sh`.

## Build Process

The Dockerfile builds in 7 stages:

1. **Base** — `docker.io/nousresearch/hermes-agent:${AGENT_VERSION}` (Python 3.13, Node.js, npm, Playwright, agent code, built-in dashboard, uv, s6-overlay) — Dockerfile:24
2. **System packages** — sudo, git, curl, nano, net-tools, iputils-ping, iproute2, openssh-client, procps, build-essential; passwordless sudo for `hermes` — Dockerfile:31-45
3. **Playwright** — `npm install` + `npx playwright install --with-deps chromium` for the browser toolset; WhatsApp bridge removed here unless `ENABLE_WHATSAPP_BRIDGE=true` — Dockerfile:54-58
4. **Supervisor** — `uv venv /opt/supervisor` + `uv pip install supervisor` (not in Debian Trixie apt), symlinked to `/usr/local/bin/{supervisord,supervisorctl}` — Dockerfile:64-67
5. **Hermes WebUI** — `git clone --depth 1 --branch ${HERMES_WEBUI_VERSION}` from `nesquena/hermes-webui`, own venv at `/opt/hermes-webui/venv`, agent extras (`all,messaging,anthropic,bedrock,azure-identity,hindsight`) installed alongside for the in-process agent — Dockerfile:83-90
6. **Supervisord config + SSO patch** — copies supervisord.conf/start.sh; sed-patches `auto = _auto_sso_response(request)` → `auto = None` in `hermes_cli/dashboard_auth/middleware.py` (auto-SSO redirects to OAuth start, but BasicAuthProvider is password-only and raises `NotImplementedError`) — Dockerfile:101-111
7. **Env, labels, runtime** — OCI labels with agent/webui versions, `HERMES_HOME`/`HERMES_DATA_DIR=/opt/data`, `PLAYWRIGHT_BROWSERS_PATH`, WebUI env, `EXPOSE 8642 8787 9119`, `ENTRYPOINT ["/opt/hermes-suite/start.sh"]` — Dockerfile:114-152

## Startup Sequence (`start.sh`) — Runtime & Privilege Model

`start.sh` is the entrypoint and handles two divergent startup paths depending on the detected runtime.

### Runtime detection (`is_docker()`, start.sh:23-27)

```bash
is_docker() {
    [ -f /.dockerenv ] && return 0
    grep -qaE '/docker/|docker-|containerd' /proc/1/cgroup 2>/dev/null && return 0
    return 1
}
```

`/.dockerenv` is checked first (created by Docker at runtime, covers cgroup v2 where `/proc/1/cgroup` shows `0::/`); falls back to the cgroup v1 grep. `/run/.containerenv` is deliberately NOT used — Podman can bake a stale copy into image layers at build time.

### Privilege model divergence (start.sh:108-146)

- **Running as root (both runtimes):** remap UID/GID if `HERMES_UID`/`HERMES_GID` set (`usermod`/`groupmod`), then fix `/opt/data` ownership to the hermes UID.
  - **Docker path (is_docker true):** supervisord stays root (fixes `/dev/stdout` permission issue); children drop to hermes via `user=` in supervisord.conf.
  - **Podman path:** drop to hermes immediately via `/command/s6-setuidgid hermes "$0" "$@"` re-exec, then run `setup_hermes` + supervisord as hermes (user= is a no-op).
- The hermes user is UID 10000 inside the image; under rootless Podman this maps to a host subuid (e.g. 109999) per `/etc/subuid`, and rootful Docker/Podman use 10000 directly.

### Config bootstrap (`setup_hermes()`, start.sh:43-90)

1. Source agent venv; create `/opt/data` tree: `cron,sessions,logs,hooks,memories,skills,skins,plans,workspace,home,webui,cache`
2. Copy `.env.example` → `.env` if missing (start.sh:50-53)
3. Copy `cli-config.yaml.example` → `config.yaml` if missing; chown hermes + `chmod 640` (start.sh:56-65)
4. Copy `docker/SOUL.md` → `SOUL.md` if missing (start.sh:68-70)
5. Sync bundled skills via `tools/skills_sync.py` (start.sh:73-75)
6. `setup_dashboard_auth()`: parse `DASHBOARD_CREDENTIAL` (default `admin:admin`) → export `HERMES_DASHBOARD_BASIC_AUTH_USERNAME`/`_PASSWORD` (start.sh:34-40, 77-78)
7. Clean stale `gateway.pid`/`gateway.lock` from previous runs (start.sh:81-86)
8. Ensure `/var/log/supervisor` + `/var/run/supervisor` exist (start.sh:88-90)

Then supervisord launches as PID 1, printing the startup banner with dashboard login.

## Build Helper (`build.sh`) Flags

`build.sh` reads pinned versions + runtime settings from `versions.env` (start.sh of the build side) and accepts CLI overrides:

| Flag | Effect |
|---|---|
| `--agent vX.Y.Z` | Override `AGENT_VERSION` |
| `--webui vX.Y.Z` | Override `WEBUI_VERSION` |
| `--podman` / `--docker` | Force the container runtime |
| `--docker-nolog` | Docker build with supervisord child logs patched to `/dev/null` (sed-patches supervisord.conf before build, restored after via git checkout) — build.sh:106-112, 145-152 |
| `--sudo` / `--no-sudo` | Toggle rootful sudo prefix |
| `--whatsapp` | Set `ENABLE_WHATSAPP_BRIDGE=true` (include WhatsApp bridge) |

Image tag derived as `ascensionoid/hermes-suite:{agent}-{webui}` with `v` prefix stripped (build.sh:100-103).

## `up.sh` — Network Bootstrap & Dashboard Credentials

`up.sh` reads `versions.env`, creates the `agent_net` bridge network if missing, then starts the compose stack:

- **Podman < 4 CNI fix (up.sh:76-87):** after `podman network create --subnet ...`, if the podman major version is < 4, the generated CNI conflist is patched from `"cniVersion": "1.0.0"` → `"0.4.0"` (the firewall plugin doesn't support 1.0.0). This matches the repo's stated Podman v3.4.4 baseline.
- **Dashboard credentials (up.sh:17-36):** `DASHBOARD_CREDENTIAL` is read from `versions.env` (default `admin:admin`). In `auto` mode a random password is generated with `secrets.token_urlsafe(16)` and persisted to `.dashboard_credential` (chmod 600) so it survives restarts. The resolved credential is exported into compose via `DASHBOARD_CREDENTIAL` env (docker-compose.yaml:43) and printed at startup.

## Version Management

Component versions are managed through build args and `versions.env`:

| Component | Source Repository | Version Format | Current Pin |
|---|---|---|---|
| Hermes Agent | `nousresearch/hermes-agent` | Date-based: `v2026.7.7.2` | versions.env:13 |
| Hermes WebUI | `nesquena/hermes-webui` | Semver: `v0.52.76` | versions.env:14 |

Suite tags follow the pattern `{agent_date}-{webui_semver}` (e.g., `2026.7.7.2-0.52.76`). CI (`.github/workflows/build.yml`) parses the compound git tag back into `AGENT_VERSION`/`HERMES_WEBUI_VERSION` build args and pushes multi-arch (`linux/amd64,linux/arm64`) images on `v*` tag pushes.

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

All services share `/opt/data` for config, sessions, skills, and memories. Dashboard login is via BasicAuth (`HERMES_DASHBOARD_BASIC_AUTH_USERNAME`/`_PASSWORD`, from `DASHBOARD_CREDENTIAL`).

## Resource Constraints

Default Docker Compose config sets 4GB memory limit. CPU is unbounded by default.

## Related

- [[hermes-suite]] — Wiki entry
- [[hermes-suite-deployment]] — Deployment guide
- [[hermes-agent]] — Core agent runtime
- [[hermes-agent-docker]] — Simpler single-service Docker packaging
- [[hermes-agent-deployment]] — Agent deployment guide
