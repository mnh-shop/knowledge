---
name: tank-os-quadlet
tags: [tank-os, quadlet, bootc, openclaw]
description: Tank OS Quadlet Files
---

# Tank OS Quadlet Files
**Source:** `sources/tank-os/`

The two Quadlet `.container` unit files are installed at `/etc/containers/systemd/users/1000/` on the bootc image. They are placed via the `rootfs/` overlay in `bootc/rootfs/etc/containers/systemd/users/1000/`. These are system-level Quadlet files for user 1000 (`openclaw`), which means systemd user units are generated automatically when the `openclaw` user logs in (and linger ensures they start at boot).

## openclaw.container

**File**: `/etc/containers/systemd/users/1000/openclaw.container`

```ini
[Unit]
Description=OpenClaw Gateway
After=network-online.target
Wants=network-online.target

[Container]
Image=ghcr.io/openclaw/openclaw:latest
Pull=newer
RunInit=true
UserNS=keep-id
User=%U:%G
Volume=%h/.openclaw:/home/node/.openclaw:Z
Environment=HOME=/home/node
Environment=TERM=xterm-256color
Environment=NPM_CONFIG_CACHE=/home/node/.openclaw/.npm
Environment=OPENCLAW_NO_RESPAWN=1
PublishPort=127.0.0.1:18789:18789
PublishPort=127.0.0.1:18790:18790
Exec=node dist/index.js gateway --allow-unconfigured --bind lan --port 18789
ExecStartPre=/usr/libexec/tank-os/bootstrap-openclaw
TimeoutStartSec=300
Restart=on-failure

[Install]
WantedBy=default.target
```

### Key Details

| Parameter | Purpose |
|-----------|---------|
| `RunInit=true` | Run a minimal init (tini) inside the container for proper signal handling and zombie reaping |
| `UserNS=keep-id` | Map the container's UID/GID to the host user's UID/GID (keeps filesystem permissions consistent) |
| `User=%U:%G` | UID and GID from the Quadlet template variable (expands to 1000:1000) |
| `Volume=%h/.openclaw:/home/node/.openclaw:Z` | Persistent data directory; `:Z` relabels for SELinux |
| `PublishPort=127.0.0.1:18789:18789` | Loopback-only binding -- service is NOT exposed to the network |
| `Exec=node dist/index.js gateway ...` | The gateway command with `--allow-unconfigured` (lets it start before secrets are injected) and `--bind lan` (listen on all interfaces inside the container) |
| `ExecStartPre=...` | Bootstrap script that creates directory structure and initial config on first run |
| `TimeoutStartSec=300` | Extended timeout for first-run bootstrap operations (e.g., image pull on cold boot) |

## service-gator.container

**File**: `/etc/containers/systemd/users/1000/service-gator.container`

```ini
[Unit]
Description=Service Gator MCP Proxy
After=network-online.target
Wants=network-online.target

[Container]
Image=ghcr.io/cgwalters/service-gator:latest
Pull=newer
RunInit=true
Volume=%h/.config/service-gator:/etc/service-gator:Z
Volume=%h/.openclaw:/workspaces:Z
Environment=GH_TOKEN_FILE=/run/secrets/gh_token
Environment=GITLAB_TOKEN_FILE=/run/secrets/gitlab_token
Environment=FORGEJO_TOKEN_FILE=/run/secrets/forgejo_token
Environment=JIRA_API_TOKEN_FILE=/run/secrets/jira_api_token
PublishPort=127.0.0.1:8080:8080
Exec=--mcp-server 0.0.0.0:8080 --scope-file /etc/service-gator/scopes.json
ExecStartPre=/usr/libexec/tank-os/bootstrap-service-gator
Restart=on-failure

[Install]
WantedBy=default.target
```

### Key Details

| Parameter | Purpose |
|-----------|---------|
| `Volume=%h/.config/service-gator:/etc/service-gator:Z` | Configuration directory with scopes.json; mounted at `/etc/service-gator` where the binary expects config |
| `Volume=%h/.openclaw:/workspaces:Z` | Agent workspaces mounted so `git_push_local` and similar tools can operate on the host filesystem |
| `Environment=GH_TOKEN_FILE=/run/secrets/gh_token` | Environment vars pointing to mounted secret files (secrets themselves are injected via drop-in) |
| `Exec=--mcp-server 0.0.0.0:8080` | Note: no `-mcp-server` flag type prefix in the actual Exec -- the container's entrypoint processes the args directly |
| No explicit `After` reference to `openclaw` | The two services are independent and can start in any order |

## Secret Drop-In Files

The base Quadlets intentionally have **no** `Secret=` entries. This allows the containers to start before secrets are created. After secrets are injected via `tank-openclaw-secrets`, drop-in files are generated at:

### OpenClaw Drop-In

**File**: `~/.config/containers/systemd/openclaw.container.d/10-secrets.conf`

```ini
[Container]
Secret=anthropic_api_key,type=env,target=ANTHROPIC_API_KEY
Secret=openai_api_key,type=env,target=OPENAI_API_KEY
Secret=gemini_api_key,type=env,target=GEMINI_API_KEY
Secret=google_api_key,type=env,target=GOOGLE_API_KEY
Secret=openrouter_api_key,type=env,target=OPENROUTER_API_KEY
Secret=model_endpoint_api_key,type=env,target=MODEL_ENDPOINT_API_KEY
Secret=telegram_bot_token,type=env,target=TELEGRAM_BOT_TOKEN
```

Each secret is injected as an environment variable into the OpenClaw container.

### Service-Gator Drop-In

**File**: `~/.config/containers/systemd/service-gator.container.d/10-secrets.conf`

```ini
[Container]
Secret=gh_token
Secret=gitlab_token
Secret=forgejo_token
Secret=jira_api_token
```

These secrets are mounted as files (default Podman behavior), matching the `*_FILE` environment variables already declared in the base Quadlet.

## Quadlet Template Variables

Quadlet files in `/etc/containers/systemd/users/<UID>/` support the following automatic template variables:

| Variable | Expands To |
|----------|------------|
| `%U` | The user's UID (1000) |
| `%G` | The user's GID (1000) |
| `%h` | The user's home directory (`/var/home/openclaw`) |

## Important: Drop-In Directory Prerequisites

The `bootstrap-openclaw` and `bootstrap-service-gator` `ExecStartPre` scripts handle creating the drop-in directories:

```
~/.config/containers/systemd/openclaw.container.d/
~/.config/containers/systemd/service-gator.container.d/
```

These are NOT created by the Quadlet itself -- the bootstrap scripts ensure the directory structure exists before `sync-podman-secrets` writes drop-in files.

## Restart Behavior

- `Restart=on-failure`: Container restarts automatically if it exits with a non-zero code
- `service-gator` depends on network (`After=network-online.target`) to ensure MCP endpoints are reachable
- `openclaw` does NOT depend on network -- it can start before connectivity exists and wait for secrets to be injected
- After `sync-podman-secrets` writes drop-in files, a `systemctl --user daemon-reload` is required (performed by the secret sync script)

## Related

- [[tank-os]] -- Wiki overview of the Tank OS project
- [[tank-os-architecture]] -- Architecture context for Quadlet services
- [[tank-os-deployment]] -- Deployment guide for the OS image
