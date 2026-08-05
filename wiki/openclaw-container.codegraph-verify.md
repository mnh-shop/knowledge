---
name: openclaw-container-codegraph-verify
tags: [openclaw-container, codegraph-verify, openclaw, docker, podman, container]
description: "Codegraph Verification: openclaw-container"
source: sources/openclaw-container/
---

# Codegraph Verification: openclaw-container

**Date:** 2026-07-12

## Claim 1: OpenClaw Gateway container built on `node:22-bookworm-slim` with CLI tools
- **Wiki says:** "OpenClaw Gateway Container — Node.js 22 on Debian, includes CLI tools (gh, gcloud, yq, Jira CLI, trash-cli) and openclaw 2026.2.23, EXPOSE 18789, `CMD ["openclaw","gateway","--bind","lan"]`."
- **Source evidence:**
  - `openclaw.Containerfile:1` — `FROM node:22-bookworm-slim`
  - `openclaw.Containerfile:20-26` — GitHub CLI install via apt (`gh`)
  - `openclaw.Containerfile:29-33` — Google Cloud SDK install (`gcloud`)
  - `openclaw.Containerfile:36-41` — yq install (architecture-aware, `yq_linux_arm64` or `yq_linux_amd64`)
  - `openclaw.Containerfile:44-53` — Jira CLI install (`ankitpokhrel/jira-cli`)
  - `openclaw.Containerfile:56` — `npm install -g trash-cli`
  - `openclaw.Containerfile:59` — `npm install -g openclaw@2026.2.23`
  - `openclaw.Containerfile:88` — `EXPOSE 18789`
  - `openclaw.Containerfile:92` — `CMD ["openclaw", "gateway", "--bind", "lan"]`
  - `openclaw.Containerfile:82-83` — `ENV OPENCLAW_CONFIG_PATH=/app/openclaw-data/openclaw.json`, `ENV OPENCLAW_STATE_DIR=/app/openclaw-data`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Whisper service container for audio transcription with whisper.cpp
- **Wiki says:** "Whisper Service — Python 3.11 + whisper.cpp, HTTP API on port 8080, gunicorn (2 workers, 120s timeout), endpoints `/health`, `/v1/audio/transcriptions`, `/transcribe`, internal services only."
- **Source evidence:**
  - `whisper.Containerfile:1` — `FROM python:3.11-slim`
  - `whisper.Containerfile:4-7` — Installs `ffmpeg` and `wget`
  - `whisper.Containerfile:11-25` — Builds `whisper.cpp` from source: clone, `make`, copy `whisper-cli` binary + `.so` libs
  - `whisper.Containerfile:28` — `pip install --no-cache-dir flask gunicorn`
  - `whisper.Containerfile:39` — `CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "whisper-api:app"]`
  - `whisper-api.py:17-18` — `GET /health`
  - `whisper-api.py:85-86` — OpenAI-compatible `POST /v1/audio/transcriptions`
  - `whisper-api.py:99-100` — legacy `POST /transcribe`
  - `start-containers.sh:27` — whisper-service attached to `internal-services` only (no internet)
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Volume strategy as actually implemented — 1 rw base + 3 ro overlays, optional credentials, SSH keys NOT mounted, whisper model mount
- **Wiki says:** "Single `rw` base mount (`~/.openclaw:/app/openclaw-data:rw,z`) + three `ro` overlays (openclaw.json, credentials, exec-approvals.json); NO per-subdirectory mounts; optional credential mounts (gcloud/gh rw, gitconfig/.jira/jira/notion/todoist ro); SSH keys NOT mounted; whisper model `~/.local/share/whisper-cpp:/app/models:ro` on whisper-service only."
- **Source evidence:**
  - `start-containers.sh:54-62` — `VOLUME_ARGS` = exactly 1 rw base + 3 ro overlays (no per-subdir mounts)
  - `start-containers.sh:9-10,30` — `WHISPER_MODEL_DIR="$HOME/.local/share/whisper-cpp"` mounted `-v "$WHISPER_MODEL_DIR:/app/models:ro"`
  - `start-containers.sh:18-21` — fails fast if `ggml-small.bin` missing from the model dir
  - `start-containers.sh:68-119` — optional credential mounts (gcloud/gh `:rw` for token refresh; `.gitconfig`, `.jira`, `jira`, `notion`, `todoist` `:ro`)
  - `start-containers.sh:121-124` — comment: "SSH keys NOT mounted — Firewall blocks port 22"
  - `README.md:231-251` — the per-directory table (workspace, logs, agents, cron, memories, subagents, telegram, scripts, settings, devices, delivery-queue, media, identity/) is the stale pre-simplification design, NOT the running script
- **Verdict:** ✅ CORRECT (wiki mounts section rewritten to match the script; stale per-subdir list removed)
- **Fix needed:** Applied to wiki (removed "Other RW Mounts" list; added whisper model mount + SSH-keys-not-mounted note).

## Claim 4: Port mapping 127.0.0.1:18789:18789, gateway binds to 0.0.0.0, dual-homed
- **Wiki says:** "Gateway binds to `0.0.0.0` inside container (via `--bind lan`) for host access. Port forwarding: `127.0.0.1:18789:18789` (localhost only). Network attach: `openclaw-external` + `internal-services`."
- **Source evidence:**
  - `openclaw.Containerfile:88` — `EXPOSE 18789`
  - `openclaw.Containerfile:92` — `CMD ["openclaw", "gateway", "--bind", "lan"]` — binds all interfaces
  - `start-containers.sh:132` — `-p 127.0.0.1:18789:18789` — localhost-only on host
  - `start-containers.sh:130` — `--network openclaw-external`; `start-containers.sh:143` — `podman network connect internal-services openclaw-gateway`
  - `start-containers.sh:152` — post-start verification `curl http://localhost:18789/health`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Two repo-owned networks; `google-vertex` is pre-existing LiteLLM infrastructure
- **Wiki says:** "Repo-owned networks: `openclaw-external` (10.92.0.0/24) and `internal-services` (10.93.0.0/24), created by `setup-networks.sh`. `google-vertex` (10.89.0.0/24) is LiteLLM's pre-existing network — referenced but NOT created or managed by this repo."
- **Source evidence:**
  - `setup-networks.sh:11-14` — creates `openclaw-external` with `--subnet=10.92.0.0/24 --gateway=10.92.0.1`
  - `setup-networks.sh:18-21` — creates `internal-services` with `--subnet=10.93.0.0/24 --gateway=10.93.0.1`
  - `setup-networks.sh:24-26` — summary lists only these two zones
  - `README.md:18` — `google-vertex` described as "Litellm's existing network"; `README.md:10` — litellm-proxy "already deployed"
  - `CLAUDE.md` (Networks section) — documents `google-vertex` as a separate existing network, not something this repo provisions
  - `start-containers.sh:36-41,143` — this repo only joins containers to `internal-services`
- **Verdict:** ✅ CORRECT (wiki previously presented 3 repo networks; now fixed to 2 owned + 1 pre-existing)
- **Fix needed:** Applied to wiki (Network Architecture section rewritten).

## Claim 6: Firewall chains and systemd persistence
- **Wiki says:** "`setup-firewall-policies.sh` builds `PODMAN_ZONE_OPENCLAW` (allow DNS/HTTPS to Telegram, Google, Red Hat, Brave, GitHub; log+drop rest) and `PODMAN_ZONE_INTERNAL_SVC` (intra-subnet only, no internet). `install-persistent-firewall.sh` installs a systemd oneshot in the VM that restores `iptables-save`d rules on boot."
- **Source evidence:**
  - `setup-firewall-policies.sh:65` — `OPENCLAW_CHAIN="${CHAIN_PREFIX}_OPENCLAW"`; `:72-73` — DNS allow; `:79-101` — HTTPS allow to Telegram/Google/RedHat/Brave/GitHub; `:104-105` — LOG `openclaw-blocked:` + DROP
  - `setup-firewall-policies.sh:114` — `INTERNAL_CHAIN="${CHAIN_PREFIX}_INTERNAL_SVC"`; `:121` — allow 10.93.0.0/24; `:127-128` — LOG `internal-svc-blocked:` + DROP
  - `install-persistent-firewall.sh:45-47` — `iptables-save > /etc/podman-firewall-rules.v4`
  - `install-persistent-firewall.sh:21-42` — restore script `/etc/podman-firewall-rules-restore.sh`
  - `install-persistent-firewall.sh:51-66` — `podman-firewall.service` (oneshot, `Before=network.target podman.service`, `WantedBy=multi-user.target`)
  - `install-persistent-firewall.sh:70-72,90-91` — enable/start; re-run to re-save rules
  - `install-persistent-firewall.sh:15-17` — also re-applies pre-existing LiteLLM policies
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: SELinux-compatible volume mounts with `:z` flag
- **Wiki says:** "All mounts use `:z` flag for SELinux compatibility — without `:z`: files appear as `nobody:nogroup` with `nfs_t` context → permission denied; with `:z`: `container_file_t` context → accessible."
- **Source evidence:**
  - `start-containers.sh:56` — `-v "$OPENCLAW_DATA_DIR:/app/openclaw-data:rw,z"`
  - `start-containers.sh:59-61` — all 3 RO overlays use `:ro,z`
  - `start-containers.sh:30` — whisper model mount `:ro`
  - `openclaw.Containerfile:66-70` — security note: rootless podman isolates at VM level
  - `CLAUDE.md` — "**Critical**: All mounts use `:z` flag for SELinux relabeling. Without `:z`: Files appear as `nobody:nogroup` with `nfs_t` context → permission denied. With `:z`: Files get `container_file_t` context → accessible" and "Don't remove `:z` flags from volume mounts (causes SELinux permission issues)"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: `MIGRATION-GUIDE.md` does not exist — stale reference; CLAUDE.md is a real source
- **Wiki says:** "`MIGRATION-GUIDE.md` does NOT exist in this repo — it is a stale reference in `README.md:64,97,212,270`; references removed from the wiki and redirected to the new `openclaw-container.migration` companion. `CLAUDE.md` is an actual repo file (AI-assistant context)."
- **Source evidence:**
  - Repo file listing: no `MIGRATION-GUIDE.md` anywhere under `sources/openclaw-container/` (only README.md, CLAUDE.md, Containerfiles, scripts, whisper-api.py, whisper-wrapper.sh, .gitignore)
  - `README.md:64` — file-structure block lists `MIGRATION-GUIDE.md` (does not exist)
  - `README.md:97,212` — "See MIGRATION-GUIDE.md for details/troubleshooting" (dead links); `README.md:270` — "Next Step: Follow `MIGRATION-GUIDE.md`"
  - `CLAUDE.md` — present, documents architecture, volume/SELinux conventions, troubleshooting, "What NOT to Do"
- **Verdict:** ✅ CORRECT (wiki corrected — MIGRATION-GUIDE.md removed from Main Scripts, references fixed, CLAUDE.md added to sources)
- **Fix needed:** Applied to wiki + new companion doc `wiki/openclaw-container.migration.md` created.

## Summary

The OpenClaw Container wiki is accurate regarding:
- **Container base image:** ✅ Correct (node:22-bookworm-slim with gh, gcloud, yq, jira, trash-cli, openclaw 2026.2.23)
- **Whisper service:** ✅ Correct (Python 3.11, whisper.cpp, Flask, gunicorn on 8080)
- **Volume mounts:** ✅ Corrected (1 RW base + 3 RO overlays; per-subdir list removed; whisper model + SSH-keys-not-mounted added)
- **Port mapping:** ✅ Correct (127.0.0.1:18789:18789, `--bind lan`, dual-homed)
- **Networks:** ✅ Corrected (2 repo-owned + google-vertex pre-existing LiteLLM network)
- **Firewall:** ✅ Correct (OPENCLAW_CHAIN + INTERNAL_CHAIN; systemd persistence)
- **SELinux compatibility:** ✅ Correct (`:z` flags confirmed on all mounts)
- **Stale refs:** ✅ Corrected (MIGRATION-GUIDE.md does not exist; CLAUDE.md added as source)

## Related

- [[openclaw-container]] -- Main wiki entry
- [[openclaw-container.migration]] -- Operations/troubleshooting companion
- [[openclaw]] -- Parent project
- [[podman]] -- Container runtime
- [[tank-os]] -- bootc image deployment

## Cross-project

- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[alphaclaw.codegraph-verify]] -- Similar codegraph verification for AlphaClaw
- [[clawpier.codegraph-verify]] -- Similar codegraph verification for ClawPier
