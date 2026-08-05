---
name: openclaw-container-migration
description: "OpenClaw container operations and troubleshooting companion: migration config, volume mounts, SELinux, firewall persistence, deferred features"
source: sources/openclaw-container/
verification_date: 2026-07-12
verified_by: codegraph-verify
tags: [openclaw-container, openclaw, podman, container, firewall, selinux, systemd, troubleshooting, deployment]
status: active
---

# OpenClaw Container — Operations & Troubleshooting Companion

Companion to [[openclaw-container]]. Covers the migration config changes, the volume strategy as **actually implemented**, SELinux behavior, firewall persistence mechanics, deferred Phase-2 features, and troubleshooting quick checks.

> **Note on `MIGRATION-GUIDE.md`:** the upstream `README.md` references a `MIGRATION-GUIDE.md` (`README.md:64,97,212,270`) that does **not** exist in the repository. This page is the replacement for those stale references.

## Migration Config Changes

Before first start, edit `~/.openclaw/openclaw.json` (same as `README.md:126-158`):

**Change 1 — LiteLLM URL:**
```json
"models": {
  "providers": {
    "litellm": {
      "baseUrl": "http://litellm-proxy:4000",  // was: http://localhost:4000
      ...
    }
  }
}
```

**Change 2 — Whisper tool to HTTP:**
```json
"tools": {
  "media": {
    "audio": {
      "enabled": true,
      "models": [
        {
          "type": "http",                                    // was: "cli"
          "url": "http://whisper-service:8080/transcribe",  // new
          "method": "POST"
        }
      ]
    }
  }
}
```

Config must use **container paths** (`/app/openclaw-data/...`), never host paths.

## Volume Strategy (as Actually Implemented)

`start-containers.sh:54-62` mounts exactly **one rw base + three ro overlays** — there are no per-subdirectory mounts:

```bash
-v ~/.openclaw:/app/openclaw-data:rw,z                                        # base RW
-v ~/.openclaw/openclaw.json:/app/openclaw-data/openclaw.json:ro,z            # RO overlay
-v ~/.openclaw/credentials:/app/openclaw-data/credentials:ro,z                 # RO overlay
-v ~/.openclaw/exec-approvals.json:/app/openclaw-data/exec-approvals.json:ro,z # RO overlay
```

- The base `rw` mount makes every `~/.openclaw/` subdirectory (workspace, logs, agents, cron, memories, subagents, telegram, scripts, settings, devices, delivery-queue, media, ...) writable automatically. New subdirectories appear in the container without editing the script.
- The three `ro` overlays protect `openclaw.json`, `credentials/`, and `exec-approvals.json` from in-container modification.
- The per-directory mount table in `README.md:231-251` (workspace, logs, agents, cron, memories, subagents, telegram, scripts, settings, devices, delivery-queue, media, identity/) is the **stale pre-simplification design** — do not use it to debug mounts.
- **SSH keys are NOT mounted** (`start-containers.sh:121-124`). The firewall blocks port 22; `gh`/`git` use HTTPS/OAuth instead. Do not mount them.
- **Optional credential mounts** (`start-containers.sh:68-119`, conditional on the host path existing):
  - `~/.config/gcloud:/root/.config/gcloud:rw` — Google OAuth token refresh
  - `~/.config/gh:/root/.config/gh:rw` — GitHub OAuth refresh
  - `~/.gitconfig:/root/.gitconfig:ro`, `~/.config/.jira:/root/.config/.jira:ro`, `~/.config/jira:/root/.config/jira:ro`, `~/.config/notion:/root/.config/notion:ro`, `~/.config/todoist:/root/.config/todoist:ro` — static configs

### Whisper Model Mount

`start-containers.sh:10,30` mounts the whisper.cpp models **read-only into whisper-service only**:

```bash
WHISPER_MODEL_DIR="$HOME/.local/share/whisper-cpp"
-v "$WHISPER_MODEL_DIR:/app/models:ro"
```

- The script fails fast if `$WHISPER_MODEL_DIR/ggml-small.bin` is missing (`start-containers.sh:18-21`) — this is the most common cause of a whisper-service that starts and immediately exits.
- The gateway container never sees the models; it calls the HTTP API.

## SELinux Notes

All mounts use the `:z` flag for SELinux relabeling (Podman VM is Fedora CoreOS):

- **Without `:z`:** files appear as `nobody:nogroup` with `nfs_t` context → `Permission denied`
- **With `:z`:** files get `container_file_t` context → accessible

Rules of thumb (from `CLAUDE.md`):
- **Don't** remove `:z` flags from volume mounts — causes SELinux permission issues.
- Verify inside the container: `podman exec openclaw-gateway ls -laZ /app/openclaw-data/`
- On permission errors, first check the mount labels, then ownership (container runs as root, files appear UID 0).

## Firewall Persistence

### Chains applied (`setup-firewall-policies.sh`)

Run inside the Podman VM (`podman machine ssh podman-machine-default < setup-firewall-policies.sh`):

- **`PODMAN_ZONE_OPENCLAW`** (`:65-109`) — for the `openclaw-external` subnet (10.92.0.0/24):
  - Allow DNS (UDP/TCP 53) + established/related
  - Allow HTTPS (443) to Telegram (`149.154.160.0/20`, `91.108.4.0/22`), Google, Red Hat/Jira, Brave, GitHub CIDR ranges
  - LOG `openclaw-blocked:` + DROP everything else
- **`PODMAN_ZONE_INTERNAL_SVC`** (`:114-132`) — for the `internal-services` subnet (10.93.0.0/24):
  - Allow only intra-subnet (10.93.0.0/24) + established
  - LOG `internal-svc-blocked:` + DROP — no internet from this network

### systemd persistence (`install-persistent-firewall.sh`)

Makes the rules survive Podman VM reboots:

1. Applies the current policies (`:11-12`) plus the pre-existing LiteLLM policies (`:15-17`).
2. Saves live rules: `iptables-save > /etc/podman-firewall-rules.v4` (`:45-47`).
3. Installs `/etc/podman-firewall-rules-restore.sh`, a boot-time restore script (`:21-42`).
4. Creates `podman-firewall.service` — `Type=oneshot`, `Before=network.target podman.service`, `WantedBy=multi-user.target`, runs `iptables-restore < /etc/podman-firewall-rules.v4` (`:51-66`).
5. Enables + starts the service (`:70-72`).

**To update rules after a change:** edit `setup-firewall-policies.sh`, then **re-run `install-persistent-firewall.sh`** to re-save the new rules (`:90-91`). Just re-applying policies without re-saving loses them on reboot.

**Verify persistence:**
```bash
podman machine ssh 'sudo systemctl status podman-firewall.service'
podman machine ssh 'sudo cat /etc/podman-firewall-rules.v4'
```

## Deferred Features (Phase 2)

Per `README.md:178-188`, two features are intentionally deferred:

### Browser Tool
- Currently **disabled** in the container.
- Requires a Chrome/Chromium install (~500MB) inside the gateway image.
- Will be added in a future phase only if needed.

### Google OAuth Re-auth
- The current setup reuses existing tokens from `~/.openclaw/identity/` — reachable through the base `~/.openclaw` rw mount if present.
- Refresh tokens should auto-renew via the rw `~/.config/gcloud` mount (`/root/.config/gcloud:rw`).
- If a full re-auth becomes necessary, it is deferred to Phase 2. Symptom to watch for: the container's `gcloud` CLI starts returning auth errors while the host's still works.
- If OAuth token refresh fails: verify the mount is rw (`podman inspect openclaw-gateway | jq '.[].Mounts[] | select(.Destination | contains("gh"))'`) and that the container can write (`podman exec openclaw-gateway touch /root/.config/gh/test`).

## Troubleshooting Quick Checks

From `README.md:210-227` — the definitive order of operations:

```bash
# 1. Container won't start
podman logs openclaw-gateway          # or whisper-service

# 2. Can't reach other containers
podman network inspect internal-services

# 3. Port not accessible from host
lsof -i :18789
podman port openclaw-gateway          # expect 127.0.0.1:18789

# 4. Firewall blocking too much
podman machine ssh "sudo iptables -L PODMAN_ZONE_OPENCLAW -n -v"
```

### Per-component triage

**Gateway unreachable:**
1. Check bind mode — must be `--bind lan` (0.0.0.0 inside the container); loopback binding makes it unreachable from the host.
2. Check port forwarding: `podman port openclaw-gateway`.
3. Check logs: `podman logs openclaw-gateway`.

**Whisper not working:**
1. `podman ps | grep whisper` — is it up?
2. `podman exec openclaw-gateway curl http://whisper-service:8080/health`
3. `podman exec openclaw-gateway which whisper` — is the wrapper installed?
4. `podman logs whisper-service` — model missing (`ggml-small.bin`) is the usual startup failure.

**Permission denied / SELinux:**
1. Confirm every mount carries `:z` (`podman inspect openclaw-gateway | jq '.[].Mounts'`).
2. Check context inside container: `podman exec openclaw-gateway ls -laZ /app/openclaw-data/` — expect `container_file_t`.
3. Re-apply `:z` if missing — do not remove the flags.

**Network issues:**
1. `podman network ls` — do `openclaw-external` and `internal-services` exist?
2. `podman network inspect internal-services` — are whisper-service, openclaw-gateway, and litellm-proxy attached?
3. `podman machine ssh "sudo journalctl -k --since '10 minutes ago' | grep openclaw-blocked"` — blocked outbound traffic.

**Firewall blocking too much:** inspect chain counters, then adjust `setup-firewall-policies.sh` and **re-run `install-persistent-firewall.sh`** (see above).

## Network Topology Recap

- **Repo-owned:** `openclaw-external` (10.92.0.0/24), `internal-services` (10.93.0.0/24) — created by `setup-networks.sh:11-21`.
- **Pre-existing:** `google-vertex` (10.89.0.0/24) belongs to the already-deployed LiteLLM proxy (`README.md:18`); this repo never creates or manages it. OpenClaw reaches LiteLLM over `internal-services`.
- Gateway is dual-homed (`openclaw-external` + `internal-services`); whisper-service is internal-only.

## Related

- [[openclaw-container]] — Main wiki entry
- [[openclaw-container.codegraph-verify]] — Evidence-backed verification
- [[openclaw]] — Parent project
- [[podman]] — Container runtime platform
