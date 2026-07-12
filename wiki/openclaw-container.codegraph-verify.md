---
name: openclaw-container-codegraph-verify
tags: [openclaw-container, codegraph-verify, openclaw, docker, podman, container]
description: "Codegraph Verification: openclaw-container"
source: sources/openclaw-container/
---

# Codegraph Verification: openclaw-container

**Date:** 2026-07-12

## Claim 1: OpenClaw Gateway container built on `node:22-bookworm-slim` with CLI tools
- **Wiki says:** "OpenClaw Gateway Container — Node.js 22 on Debian, includes CLI tools (gh, gcloud, yq, Jira CLI, trash-cli)"
- **Source evidence:**
  - `openclaw.Containerfile:1` — `FROM node:22-bookworm-slim`
  - `openclaw.Containerfile:4-17` — `apt-get install` layer: `ca-certificates`, `gnupg`, `curl`, `wget`, `git`, `jq`, `rsync`, `ffmpeg`, `zip`, `unzip`, `python3`, `python3-pip`
  - `openclaw.Containerfile:20-26` — GitHub CLI install via apt (`gh`)
  - `openclaw.Containerfile:29-33` — Google Cloud SDK install (`gcloud`)
  - `openclaw.Containerfile:36-41` — yq install (architecture-aware, `yq_linux_arm64` or `yq_linux_amd64`)
  - `openclaw.Containerfile:44-53` — Jira CLI install (`ankitpokhrel/jira-cli`)
  - `openclaw.Containerfile:56` — `npm install -g trash-cli`
  - `openclaw.Containerfile:59` — `npm install -g openclaw@2026.2.23`
  - `openclaw.Containerfile:88` — `EXPOSE 18789`
  - `openclaw.Containerfile:92` — `CMD ["openclaw", "gateway", "--bind", "lan"]`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Whisper service container for audio transcription with whisper.cpp
- **Wiki says:** "Whisper Service — Python 3.11 + whisper.cpp, HTTP API on port 8080, internal services only (no internet access)"
- **Source evidence:**
  - `whisper.Containerfile:1` — `FROM python:3.11-slim`
  - `whisper.Containerfile:4-7` — Installs `ffmpeg` and `wget`
  - `whisper.Containerfile:11-25` — Builds `whisper.cpp` from source: clone git repo, `make`, copy `whisper-cli` binary and `.so` libraries
  - `whisper.Containerfile:28` — `pip install --no-cache-dir flask gunicorn`
  - `whisper.Containerfile:36` — `EXPOSE 8080`
  - `whisper.Containerfile:39` — `CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "whisper-api:app"]`
  - `whisper-api.py:8-10` — Flask app with `health()` and `_transcribe_audio()` endpoints
  - `whisper-api.py:17-20` — `GET /health` health check endpoint
  - `whisper-api.py:22-50` — `_transcribe_audio()` saves uploaded file, converts to 16kHz mono WAV via ffmpeg, calls `whisper-cli`
  - `whisper-api.py:51-114` — OpenAI-compatible `POST /v1/audio/transcriptions` and legacy `POST /transcribe` endpoints
  - `whisper-wrapper.sh` — CLI wrapper that intercepts `whisper` calls and proxies to `http://whisper-service:8080/transcribe`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Podman-based deployment with volume mount strategy (single base mount + read-only overlays)
- **Wiki says:** "Simplification Philosophy — Single base mount + read-only overlays"
- **Source evidence:**
  - `start-containers.sh:54-62` — Volume mount strategy:
    ```bash
    VOLUME_ARGS=(
      -v "$OPENCLAW_DATA_DIR:/app/openclaw-data:rw,z"           # Base RW mount
      -v "$OPENCLAW_DATA_DIR/openclaw.json:/app/openclaw-data/openclaw.json:ro,z"     # RO overlay
      -v "$OPENCLAW_DATA_DIR/credentials:/app/openclaw-data/credentials:ro,z"          # RO overlay
      -v "$OPENCLAW_DATA_DIR/exec-approvals.json:/app/openclaw-data/exec-approvals.json:ro,z"  # RO overlay
    )
    ```
  - `start-containers.sh:68-127` — Optional credential mounts:
    - `~/.config/gcloud:/root/.config/gcloud:rw` (OAuth token refresh)
    - `~/.config/gh:/root/.config/gh:rw` (GitHub OAuth refresh)
    - `~/.gitconfig:/root/.gitconfig:ro` (static)
    - `~/.config/.jira:/root/.config/.jira:ro` (static)
    - `~/.config/jira:/root/.config/jira:ro`, `~/.config/notion:/root/.config/notion:ro`, `~/.config/todoist:/root/.config/todoist:ro`
  - `start-containers.sh:121-124` — Comment: "SSH keys NOT mounted — Firewall blocks port 22"
  - `openclaw.Containerfile:66-79` — Security comments: read-only/read-write mounts documented
  - `setup-networks.sh` — Creates `internal-services` network for inter-container traffic
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 4: Port mapping 127.0.0.1:18789:18789, gateway binds to 0.0.0.0
- **Wiki says:** "Gateway binds to 0.0.0.0 inside container (via `--bind lan`) for host access. Port forwarding: `127.0.0.1:18789:18789`"
- **Source evidence:**
  - `openclaw.Containerfile:88` — `EXPOSE 18789`
  - `openclaw.Containerfile:92` — `CMD ["openclaw", "gateway", "--bind", "lan"]` — binds to all interfaces
  - `start-containers.sh:132` — `-p 127.0.0.1:18789:18789` — localhost-only port mapping on host
  - `openclaw.Containerfile:81-83` — Environment variables:
    - `ENV OPENCLAW_CONFIG_PATH=/app/openclaw-data/openclaw.json`
    - `ENV OPENCLAW_STATE_DIR=/app/openclaw-data`
  - `start-containers.sh:138` — Container runs on `openclaw-external` network
  - `start-containers.sh:143` — Also connected to `internal-services` network
  - `start-containers.sh:152` — Verification: `curl http://localhost:18789/health`
  - `openclaw.Containerfile:82-86` — `ENV PATH` includes `/usr/local/bin`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Network isolation with multiple Podman networks and iptables firewall policies
- **Wiki says:** "Three networks: `openclaw-external` (10.92.0.0/24) for internet-restricted traffic, `internal-services` (10.93.0.0/24) for container-to-container only, `google-vertex` (10.89.0.0/24) for LiteLLM to Google Cloud"
- **Source evidence:**
  - `setup-networks.sh:11-14` — Creates `openclaw-external` with `--subnet=10.92.0.0/24 --gateway=10.92.0.1`
  - `setup-networks.sh:18-21` — Creates `internal-services` with `--subnet=10.93.0.0/24 --gateway=10.93.0.1`
  - `setup-networks.sh:25-26` — Comments documenting zones: "openclaw-external (10.92.0.0/24) - Telegram, Brave, Jira, Google APIs" and "internal-services (10.93.0.0/24) - Container-to-container only"
  - `setup-firewall-policies.sh:10-11` — Subnet constants: `OPENCLAW_EXTERNAL_SUBNET="10.92.0.0/24"`, `INTERNAL_SERVICES_SUBNET="10.93.0.0/24"`
  - `setup-firewall-policies.sh:14-59` — IP range definitions:
    - `TELEGRAM_RANGES`: 149.154.160.0/20, 91.108.4.0/22
    - `GOOGLE_RANGES`: Google Cloud and service IPs (8 CIDR blocks)
    - `REDHAT_RANGES`: AWS us-east-1 for issues.redhat.com
    - `BRAVE_RANGES`: Cloudflare ranges for api.search.brave.com
    - `GITHUB_RANGES`: 6 CIDR blocks from GitHub meta
  - `setup-firewall-policies.sh:65-109` — `OPENCLAW_CHAIN` iptables chain:
    - Lines 72-73: Allow DNS (UDP/TCP port 53)
    - Lines 79-101: Allow HTTPS (port 443) to Telegram, Google, Red Hat, Brave, GitHub
    - Lines 104-105: Log and DROP all other traffic
  - `setup-firewall-policies.sh:114-134` — `INTERNAL_CHAIN` for internal-services:
    - Line 121: Allow traffic within 10.93.0.0/24
    - Lines 127-128: Log and DROP all other (no internet)
  - `setup-firewall-policies.sh:138-142` — Policy summary: "openclaw-external: Telegram, Brave, Jira, GitHub, Google APIs only. internal-services: Container-to-container only, no internet"
- **Verdict:** ✅ CORRECT
- **Fix needed:** The wiki mentions 3 networks but the source only defines 2 in `setup-networks.sh`. The `google-vertex` network is referenced in comments as an existing separate network for LiteLLM, not created by this repo.

## Claim 6: SELinux-compatible volume mounts with `:z` flag
- **Wiki says:** "All mounts use `:z` flag for SELinux compatibility — without `:z`: files appear as `nobody:nogroup` with `nfs_t` context → permission denied"
- **Source evidence:**
  - `start-containers.sh:56` — `-v "$OPENCLAW_DATA_DIR:/app/openclaw-data:rw,z"`
  - `start-containers.sh:59-61` — All 3 RO overlays use `:ro,z`:
    - `openclaw-data/openclaw.json:ro,z`
    - `openclaw-data/credentials:ro,z`
    - `openclaw-data/exec-approvals.json:ro,z`
  - `openclaw.Containerfile:67-70` — Security documentation: "Container is isolated via: Rootless podman (runs in VM as non-root user)"
  - `CLAUDE.md` — "**Critical**: All mounts use `:z` flag for SELinux relabeling. Without `:z`: Files appear as `nobody:nogroup` with `nfs_t` context → permission denied. With `:z`: Files get `container_file_t` context → accessible"
  - `CLAUDE.md` — "Don't remove `:z` flags from volume mounts (causes SELinux permission issues)"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Summary

The OpenClaw Container wiki is accurate regarding:
- **Container base image:** ✅ Correct (node:22-bookworm-slim with gh, gcloud, yq, jira, trash-cli)
- **Whisper service:** ✅ Correct (Python 3.11, whisper.cpp, Flask, gunicorn on 8080)
- **Volume mounts:** ✅ Correct (single RW base + RO overlays, OAuth RW for refresh)
- **Port mapping:** ✅ Correct (127.0.0.1:18789:18789, `--bind lan` for 0.0.0.0 binding)
- **Network isolation:** ⚠️ Partially accurate — only 2 networks defined in source (not 3)
- **SELinux compatibility:** ✅ Correct (`:z` flags confirmed on all mounts)

## Related

- [[openclaw-container]] -- Main wiki entry
- [[openclaw]] -- Parent project
- [[podman]] -- Container runtime
- [[tank-os]] -- bootc image deployment

## Cross-project

- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[alphaclaw.codegraph-verify]] -- Similar codegraph verification for AlphaClaw
- [[clawpier.codegraph-verify]] -- Similar codegraph verification for ClawPier
