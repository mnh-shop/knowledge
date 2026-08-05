---
name: hermes-suite-codegraph-verify
tags: [hermes-suite, codegraph-verify, hermes-agent, docker]
description: "Codegraph Verification: hermes-suite — validating wiki claims against indexed source code"
source: sources/hermes-suite/
---

# Codegraph Verification: hermes-suite

**Date:** 2026-07-12

## Claim 1: Three Hermes services in one container managed by supervisord

- **Wiki says:** Hermes Suite packages three services (hermes-gateway on 8642, hermes-dashboard on 9119, hermes-webui on 8787) into a single Docker/Podman container managed by supervisord.
- **Source evidence:**
  - `supervisord.conf` defines three `[program]` sections: `hermes-gateway` (lines 36-47, `hermes gateway run`, priority 10), `hermes-dashboard` (lines 59-71, `hermes dashboard --host 0.0.0.0 --port 9119 --no-open`, priority 20), `hermes-webui` (lines 77-89, `/opt/hermes-webui/venv/bin/python /opt/hermes-webui/server.py`, priority 30)
  - All three services run as `user=hermes` with `autostart=true` and `autorestart=true`; supervisord sets `nodaemon=true` (line 15) and manages via `/var/run/supervisor/supervisor.sock`
  - `Dockerfile` line 144: `EXPOSE 8642 8787 9119`
  - `README.md` lines 6-10 document the three-service architecture with ports
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Solves Podman v3.4.4 UID/GID sharing issue

- **Wiki says:** Podman v3.4.4 cannot share UID/GID between multiple containers easily, so the suite solves this by running all three services in one container via supervisord.
- **Source evidence:**
  - `Dockerfile` lines 5-6: "Solves Podman v3.4.4 UID/GID sharing limitation between multiple containers by running all three services in a single container under one user."
  - `README.md` lines 20-25: "Podman v3.4.4 cannot share the same UID/GID between multiple containers easily... This image solves that by running all three services in **one container** via supervisord."
  - `docker-compose.yaml` (lines 32-38) configures all data under a single `~/.hermes:/opt/data` volume mount
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Automatic runtime detection (Podman vs Docker)

- **Wiki says:** Automatic runtime detection — the same image works on both Podman and Docker CE without separate builds. Detection uses `/.dockerenv` and `/proc/1/cgroup`.
- **Source evidence:**
  - `start.sh` lines 23-27 define `is_docker()`: checks `/.dockerenv` first (covers cgroup v2), then falls back to `grep -qaE '/docker/|docker-|containerd' /proc/1/cgroup`; a stale `/run/.containerenv` baked by Podman builds is deliberately ignored
  - `start.sh` lines 128-146: Podman and Docker paths diverge — Docker stays root for supervisord (children run as hermes via `user=`), Podman drops to hermes via `/command/s6-setuidgid hermes` re-exec
  - `README.md` line 14: "Now with automatic runtime detection. One image works on both Podman and Docker CE out of the box"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Entrypoint bootstraps config from defaults if missing

- **Wiki says:** `start.sh` entrypoint handles UID/GID remapping, directory setup, and config bootstrapping — copies default `.env` and `config.yaml` from Hermes Agent examples if empty.
- **Source evidence:**
  - `start.sh` lines 43-90 define `setup_hermes()`: creates the `/opt/data` directory tree (line 47), runs `skills_sync.py` (lines 73-75), cleans stale `gateway.pid`/`gateway.lock` (lines 81-86), ensures `/var/log/supervisor` + `/var/run/supervisor` exist (lines 88-90)
  - `start.sh` lines 50-53: Copies `.env.example` to `.env` if missing
  - `start.sh` lines 56-59: Copies `cli-config.yaml.example` to `config.yaml` if missing (chown hermes + `chmod 640` at lines 62-65)
  - `start.sh` lines 68-70: Copies `docker/SOUL.md` to `SOUL.md` if missing
  - `Dockerfile` line 152: `ENTRYPOINT ["/opt/hermes-suite/start.sh"]`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Dashboard authentication since hermes-agent v2026.7.1 (DASHBOARD_CREDENTIAL + SSO patch)

- **Wiki says:** Since agent v2026.7.1 the dashboard requires authentication; `DASHBOARD_CREDENTIAL` (default `admin:admin`) configures the login, and a Dockerfile patch disables the broken auto-SSO redirect.
- **Source evidence:**
  - `versions.env` lines 47-56: `DASHBOARD_CREDENTIAL` setting (default `admin:admin`, options `auto` / `user:password`)
  - `start.sh` lines 30-40 `setup_dashboard_auth()`: parses the credential and exports `HERMES_DASHBOARD_BASIC_AUTH_USERNAME`/`_PASSWORD`; called from `setup_hermes` (lines 77-78)
  - `up.sh` lines 17-36: `auto` mode generates a random password via `secrets.token_urlsafe(16)` persisted to `.dashboard_credential` (chmod 600)
  - `supervisord.conf` lines 53-57: documents that v2026.7.1 removed unauthenticated dashboard access and `--insecure` is now a no-op
  - `Dockerfile` line 111: sed-patches `auto = _auto_sso_response(request)` → `auto = None` in `/opt/hermes/hermes_cli/dashboard_auth/middleware.py` (BasicAuthProvider has no OAuth start flow)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Version pinning via versions.env + pre-built multi-arch Docker Hub images

- **Wiki says:** Versions are pinned in `versions.env` (`AGENT_VERSION`, `WEBUI_VERSION`) and pre-built multi-arch images are on Docker Hub (ascensionoid/hermes-suite).
- **Source evidence:**
  - `versions.env` lines 13-14: `AGENT_VERSION=v2026.7.7.2`, `WEBUI_VERSION=v0.52.76`
  - `Dockerfile` lines 22-24: `ARG AGENT_VERSION=v2026.7.7.2` + `FROM docker.io/nousresearch/hermes-agent:${AGENT_VERSION}`; line 83: `ARG HERMES_WEBUI_VERSION=v0.52.76` (git clone at pinned tag, lines 84-90); lines 117-119 re-declare both ARGs for the OCI labels (lines 121-126)
  - `build.sh` lines 29-35: reads versions from `versions.env`; CLI overrides `--agent`/`--webui` (lines 38-59); image tag derived at lines 100-103
  - `.github/workflows/build.yml`: tag-triggered (`v*`), parses the compound tag into agent/webui versions (lines 23-41), builds `linux/amd64,linux/arm64` (line 59) and pushes to `docker.io/ascensionoid/hermes-suite` + `latest`
  - `README.md` line 69: `podman pull ascensionoid/hermes-suite:2026.7.7.2-0.52.76`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Workspace and config volumes with host persistence

- **Wiki says:** Config stored in `~/.hermes/` on host (mounted as `/opt/data`), workspace at `~/workspace`. All services share the same data directory.
- **Source evidence:**
  - `docker-compose.yaml` lines 34-38: `~/.hermes:/opt/data:Z`, `~/workspace:/workspace:z`, `/etc/localtime:/etc/localtime:ro`
  - `Dockerfile` lines 129-130: `ENV HERMES_HOME=/opt/data`, `ENV HERMES_DATA_DIR=/opt/data`; line 139: `HERMES_WEBUI_STATE_DIR=/opt/data/webui`
  - `start.sh` line 14: `HERMES_HOME="${HERMES_HOME:-/opt/data}"`; line 47: creates `cron,sessions,logs,hooks,memories,skills,skins,plans,workspace,home,webui,cache`
  - `README.md` lines 215-223: documents `~/.hermes/` directory layout
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: WhatsApp bridge is opt-in at build time (excluded by default for security)

- **Wiki says:** The WhatsApp bridge is not included by default; enable with `ENABLE_WHATSAPP_BRIDGE=true` or `--whatsapp`, and must restrict `WHATSAPP_ALLOWED_USERS`.
- **Source evidence:**
  - `Dockerfile` lines 54-58: `if [ "$ENABLE_WHATSAPP_BRIDGE" != "true" ]; then rm -rf /opt/hermes/scripts/whatsapp-bridge; fi`
  - `build.sh` lines 54-55: `--whatsapp` flag sets `ENABLE_WHATSAPP_BRIDGE=true`; passed as build arg at lines 128-141
  - `versions.env` lines 37-44: `ENABLE_WHATSAPP_BRIDGE=false` default with security rationale and link to upstream issue #15108
  - `README.md` lines 286-307: security warning ("anyone who messages your number gets full agent access") and `WHATSAPP_ALLOWED_USERS` requirement
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 8 key claims from the hermes-suite wiki have been verified against the source code:
- ✅ Three services in one container: Confirmed via `supervisord.conf` with gateway (8642), dashboard (9119), webui (8787)
- ✅ Podman UID/GID workaround: Confirmed in README and Dockerfile design comments
- ✅ Runtime auto-detection: Confirmed via `is_docker()` in `start.sh`
- ✅ Config bootstrapping: Confirmed via `setup_hermes()` with default copies
- ✅ Dashboard auth (v2026.7.1+): Confirmed via `DASHBOARD_CREDENTIAL`, `setup_dashboard_auth()`, and the SSO middleware patch
- ✅ Version pinning: Confirmed via `versions.env` + Docker build args + CI tag parsing
- ✅ Volume persistence: Confirmed via `docker-compose.yaml` mounts and directory setup
- ✅ WhatsApp bridge opt-in: Confirmed via Dockerfile removal + `--whatsapp` build flag

## Related

- [[hermes-suite]] -- Main wiki entry
- [[hermes-agent]] -- Core agent runtime this suite packages
- [[hermes-agent-docker]] -- Simpler Docker packaging (single service)
- [[hermes-workspace]] -- Hermes development workspace

## Cross-project

- [[hermes-agent.codegraph-verify]] -- Similar codegraph verification for the base agent
- [[clawpier]] -- Desktop GUI alternative for managing Hermes containers
- [[hermzner]] -- Production deployment blueprint for Hermes on Hetzner
- [[openclaw]] -- Comparable all-in-one agent suite
