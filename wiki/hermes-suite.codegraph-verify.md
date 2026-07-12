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
  - `supervisord.conf` defines three `[program]` sections: `hermes-gateway` (port 8642, `hermes gateway run`), `hermes-dashboard` (port 9119, `hermes dashboard --host 0.0.0.0 --port 9119`), `hermes-webui` (port 8787, `/opt/hermes-webui/venv/bin/python /opt/hermes-webui/server.py`)
  - All three services run as `user=hermes` with `autostart=true` and `autorestart=true`
  - `supervisord.conf` sets `nodaemon=true`, logfile at `/var/log/supervisor/supervisord.log`
  - `Dockerfile` EXPOSE 8642 8787 9119 (lines 136-137)
  - `README.md` lines 5-11 document the three-service architecture with ports
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Solves Podman v3.4.4 UID/GID sharing issue

- **Wiki says:** Podman v3.4.4 cannot share UID/GID between multiple containers easily, so the suite solves this by running all three services in one container via supervisord.
- **Source evidence:**
  - `Dockerfile` lines 1-6: "Solves Podman v3.4.4 UID/GID sharing limitation between multiple containers by running all three services in a single container under one user."
  - `README.md` lines 18-25: "Podman v3.4.4 cannot share the same UID/GID between multiple containers easily. The standard multi-container setup... requires each container to run as the same user to share the `~/.hermes` volume. This image solves that by running all three services in **one container** via supervisord."
  - `docker-compose.yaml` configures all data under a single `~/.hermes:/opt/data` volume mount
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Automatic runtime detection (Podman vs Docker)

- **Wiki says:** Automatic runtime detection — the same image works on both Podman and Docker CE without separate builds. Detection uses `/proc/1/cgroup` and `/.dockerenv`.
- **Source evidence:**
  - `start.sh` lines 23-27 define `is_docker()`: checks `/.dockerenv` first, then falls back to `grep /docker/ /proc/1/cgroup`
  - `start.sh` lines 90-134: Podman and Docker paths diverge — Docker stays root for supervisord (children run as hermes via `user=`), Podman drops to hermes via `s6-setuidgid`
  - `README.md` line 14: "Now with automatic runtime detection. One image works on both Podman and Docker CE out of the box"
  - `Dockerfile` line 13: "Container runtime detection — the same image works on both Podman and Docker"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Entrypoint bootstraps config from defaults if missing

- **Wiki says:** `start.sh` entrypoint handles UID/GID remapping, directory setup, and config bootstrapping — copies default `.env` and `config.yaml` from Hermes Agent examples if empty.
- **Source evidence:**
  - `start.sh` lines 30-74 define `setup_hermes()`: creates directory tree (`.env`, `config.yaml`, `SOUL.md` from examples), runs `skills_sync.py`, cleans stale PID/lock files
  - `start.sh` lines 37-40: Copies `.env.example` to `.env` if missing
  - `start.sh` lines 43-46: Copies `cli-config.yaml.example` to `config.yaml` if missing
  - `start.sh` lines 55-57: Copies `docker/SOUL.md` to `SOUL.md` if missing
  - `start.sh` line 60-62: Syncs bundled skills via `skills_sync.py`
  - `Dockerfile` line 144: `ENTRYPOINT ["/opt/hermes-suite/start.sh"]`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Pre-built multi-arch images on Docker Hub with pinned version management

- **Wiki says:** Pre-built multi-arch images available on Docker Hub (ascensionoid/hermes-suite). Version pinned via `versions.env` with `AGENT_VERSION` and `WEBUI_VERSION` build args.
- **Source evidence:**
  - `versions.env`: Defines `AGENT_VERSION`, `WEBUI_VERSION`, `CONTAINER_RUNTIME`, `USE_SUDO`, `ENABLE_WHATSAPP_BRIDGE`
  - `Dockerfile` lines 22-24: `ARG AGENT_VERSION=v2026.6.19`, `FROM nousresearch/hermes-agent:${AGENT_VERSION}`
  - `Dockerfile` line 83: `ARG HERMES_WEBUI_VERSION=v0.51.742`, git clone at that tag
  - `build.sh` (confirmed on disk) reads `versions.env` for build args
  - `README.md` lines 63-70: Docker Hub pull command and manual build instructions
  - `README.md` lines 106-111: Version compatibility table tested on amd64 + arm64
  - `Dockerfile` lines 113-118: OCI labels with image source and version metadata
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Workspace and config volumes with host persistence

- **Wiki says:** Config stored in `~/.hermes/` on host (mounted as `/opt/data`), workspace at `~/workspace`. All services share the same data directory.
- **Source evidence:**
  - `docker-compose.yaml` lines 34-38: `~/.hermes:/opt/data:Z`, `~/workspace:/workspace:z`, `/etc/localtime:/etc/localtime:ro`
  - `Dockerfile` lines 121-122: `ENV HERMES_HOME=/opt/data`, `ENV HERMES_DATA_DIR=/opt/data`
  - `start.sh` line 14: `HERMES_HOME="${HERMES_HOME:-/opt/data}"`
  - `start.sh` line 34: Creates directory structure: `cron,sessions,logs,hooks,memories,skills,skins,plans,workspace,home,webui,cache`
  - `README.md` lines 179-191: Documents `~/.hermes/` directory layout with descriptions
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

All 6 key claims from the hermes-suite wiki have been verified against the source code:
- ✅ Three services in one container: Confirmed via `supervisord.conf` with gateway (8642), dashboard (9119), webui (8787)
- ✅ Podman UID/GID workaround: Confirmed in README and design comments
- ✅ Runtime auto-detection: Confirmed via `is_docker()` in `start.sh`
- ✅ Config bootstrapping: Confirmed via `setup_hermes()` with default copies
- ✅ Version pinning: Confirmed via `versions.env` + Docker build args
- ✅ Volume persistence: Confirmed via `docker-compose.yaml` mounts and directory setup

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
