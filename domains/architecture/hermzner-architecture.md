---
name: hermzner-architecture
tags: [hermzner, architecture, terraform, ansible, iac, hetzner, vps, deployment-automation]
description: Hermzner Architecture
---

# Hermzner Architecture

## Overview

Hermzner provisions a hardened Hermes Agent on a Hetzner VPS (cx23, Ubuntu 24.04) using a two-phase pipeline: Terraform creates the infrastructure, then Ansible configures it, orchestrated by `deploy.sh`. The VPS runs rootless Podman as a dedicated `hermes` user with all service ports bound exclusively to `127.0.0.1`. Tailscale provides identity-based access, replacing public SSH as the primary trust boundary.

## Architecture Diagram

```
+-------------------+         +-------------------------------+
|   Deployer Host   |         |     Hetzner VPS (cx23)        |
|                   |         |                               |
|  deploy.sh -----terraform----> hcloud_server.hermes         |
|       |           |         |  (Ubuntu 24.04)               |
|       |           |         |                               |
|       |---ansible---------->|  +-- User: hermes ---------+  |
|       |           |         |  | Podman (rootless)       |  |
|       |           |         |  | Hermes container        |  |
|       |           |         |  |   (127.0.0.1:8642)     |  |
|       |           |         |  |   (127.0.0.1:9119)     |  |
|       |           |         |  | Mnemosyne (optional)    |  |
|       |           |         |  | Tailscale (identity)    |  |
|       |           |         |  | UFW + fail2ban          |  |
|       |           |         |  +-------------------------+  |
|       |           |         |                               |
|   dev machine ----tailscale----> SSH + tunnel access         |
+-------------------+         +-------------------------------+
```

## Two-Phase Pipeline

### Phase 1: Terraform (Infrastructure)

The Terraform configuration in `sources/hermzner/terraform/main.tf` provisions:

| Resource | Details |
|----------|---------|
| `hcloud_ssh_key.deployer` | Deployer SSH public key, named `${var.server_name}-deployer` for state import |
| `hcloud_firewall.provisioning` | Optional firewall (default disabled); inbound SSH (tcp/22) restricted to `deployer_ip` |
| `hcloud_server.hermes` | cx23 (2 vCPU, 4 GB RAM), fsn1 (Falkenstein), ubuntu-24.04, attached SSH key |

Terraform variables:
- `hcloud_token` (sensitive -- never written to disk, passed via `TF_VAR_hcloud_token`)
- `server_type` (default: `cx23`), `location` (default: `fsn1`), `os_type` (default: `ubuntu-24.04`)
- `ssh_public_key`, `server_name` (default: `hermes`)
- `cloud_firewall_enabled` (default: `false`), `deployer_ip` (default: `""`)

Precondition: if firewall is enabled, `deployer_ip` must be non-empty.

### Phase 2: Ansible (Configuration)

Seven roles execute in strict order, driven by `ansible/playbooks/site.yml`:

1. **podman**: Installs Podman from home:lfv apt repo, configures `hermes` user with subuid/subgid, enables linger, writes `containers.conf`
2. **tailscale**: Installs Tailscale, authenticates with pre-auth key, waits for online status
3. **security**: Hardens the host (UFW, SSH config, sysctl, fail2ban, unused services, /dev/shm)
4. **mnemosyne_build**: (optional) Builds custom container image with SQLite-vec memory backend
5. **hermes**: Deploys Hermes Quadlet or Compose file, generates API key, starts runtime
6. **mnemosyne_runtime**: (optional) Installs Mnemosyne plugin inside running container, restarts if config changed
7. **backup**: Deploys backup script, schedules daily cron at 2am

Before any role executes, 8 preflight assertions validate:
- Image pinning (digest required in `hermes_image_ref`)
- CORS origin (not wildcard `*`)
- Runtime backend (must be `quadlet` or `compose`)
- SSH policy (must be `disabled_after_tailscale`, `restricted`, or `open_key_only`)
- Bind mode (must be `localhost`)
- Volume label suffix
- Backup encryption config
- Deployer IP for restricted mode

## Security Architecture

The security model follows 20 principles from `sources/hermzner/COVENANT.md`, implemented at three layers:

### Container Security

The Quadlet unit enforces:

| Setting | Value |
|---------|-------|
| User namespace | `keep-id` (rootless, container runs as UID 1000) |
| Capabilities | `DropCapability=ALL` |
| NoNewPrivileges | `true` |
| Rootfs | `ReadOnly=true` |
| tmpfs mounts | /tmp (512m, noexec), /run (64m, noexec), /.local (64m, noexec) |
| PidsLimit | 512 |
| Memory limit | 2g |
| CPU quota | 200% |
| Ports | `127.0.0.1:8642:8642` (API), `127.0.0.1:9119:9119` (dashboard) |
| Restart | on-failure, 10s delay |

### Network Security

- UFW: default deny incoming, allow outgoing
- SSH policy configurable: `disabled_after_tailscale` (SSH only on tailscale0), `restricted` (only from deployer IP), or `open_key_only`
- No public service ports -- all Hermes service ports bind to `127.0.0.1`
- Tailscale SSH as primary access method
- Optional Hetzner Cloud Firewall as an additional layer

### Host Hardening

| Category | Details |
|----------|---------|
| sysctl | 16 parameters: disable IP forwarding, source routing, redirects; enable rp_filter, tcp_syncookies, kernel.kptr_restrict=2, etc. |
| umask | 077 for hermes user and system-wide |
| fail2ban | SSH ban after 3 failed attempts in 10 min, 1h bantime |
| Disabled services | avahi-daemon, cups, ModemManager, multipathd, udisks2 |
| /dev/shm | noexec, nosuid, nodev |
| unattended-upgrades | Enabled |
| SSH hardening | (optional, default on): PasswordAuthentication no, PermitRootLogin prohibit-password, MaxAuthTries 3, MaxSessions 5 |
| Recovery script | `/root/revert-sshd-hardening.sh` at 0700 |

## Tailscale Integration

Tailscale is the primary access mechanism, installed from the official apt repo. The `tailscale up` command uses `--ssh` to enable Tailscale SSH (WireGuard-level SSH, bypassing sshd_config entirely).

**Access flow:**
1. Ansible connects via public IPv4 (Tailscale not available yet)
2. After `tailscale` role completes, Tailscale is authenticated with a pre-auth key
3. The `security` role verifies Tailscale is online before applying SSH hardening (canary check)
4. UFW allows SSH only on `tailscale0` when `public_ssh_policy: disabled_after_tailscale`

**User access patterns:**
- Primary SSH: `ssh root@<tailscale-ip>` or `ssh hermes@<tailscale-ip>`
- MagicDNS: `<hostname>.tailscale-<netid>.ts.net`
- Tunnels: `ssh -L 9119:127.0.0.1:9119 hermes@<tailscale-ip>` (dashboard)
- Tunnels: `ssh -L 8642:127.0.0.1:8642 hermes@<tailscale-ip>` (API)

## Secret Handling

| Secret | Method |
|--------|--------|
| HCLOUD_TOKEN | `TF_VAR_hcloud_token` env var only -- never on disk |
| TAILSCALE_AUTH_KEY | Passed as Ansible extra_var with `no_log: true` |
| Hermes API key | Generated via `openssl rand -hex 32` (256-bit), stored in `.env` at 0600 |
| Image pinning | `hermes_image_ref` must contain `@sha256:`; override only via `ALLOW_UNPINNED_IMAGE` env var |
| Ansible sensitive tasks | Use `no_log: true` |

## Trust Boundary

The primary trust boundary is Tailscale identity, not SSH. SSH is treated as a transport layer only. Access control is identity-based via Tailscale ACLs. The UFW can be configured to drop all non-Tailscale SSH traffic after provisioning is complete.

## Hermes Service

Deployed via Quadlet (default) or Docker Compose, configurable via `hermes_runtime_backend` in group_vars.

**Quadlet mode** (`hermes.container.j2`):
- Systemd unit at `/home/hermes/.config/containers/systemd/hermes.container`
- Image: pinned digest ref, or `localhost/hermes-mnemosyne:latest` when Mnemosyne is enabled
- Command: `gateway run`
- Key env vars: `API_SERVER_ENABLED=true`, `API_SERVER_HOST=0.0.0.0` (inside container; host mapping restricts to 127.0.0.1), `HERMES_DASHBOARD=1` (optional), `MNEMOSYNE_DATA_DIR=/opt/data/mnemosyne` (optional)
- Env file: `/home/hermes/.hermes/.env` with the generated API key
- Volume: `/home/hermes/.hermes:/opt/data`
- Read-only rootfs with tmpfs mounts

## Mnemosyne Memory Backend (Optional)

Toggled via `hermes_mnemosyne_enabled: true`.

**Build**: A custom container image is built from a Jinja2 Dockerfile that extends the pinned Hermes base image, installs `python3-pip`, enables system-site-packages in the Hermes venv, pip-installs `mnemosyne-memory[all]`, and runs `mnemosyne.install` at build time. Tagged `localhost/hermes-mnemosyne:latest`.

**Runtime**: After the container starts, `mnemosyne.install` runs inside the container to symlink the plugin and update `config.yaml`. The Hermes service restarts only if config.yaml changed (sha256sum before/after comparison). Memory data persists at `/home/hermes/.hermes/mnemosyne/`.

**Post-deploy**: User must select 'mnemosyne' as the active memory provider via `podman exec -it hermes /opt/hermes/.venv/bin/hermes memory setup`.

## Backup Strategy

- **Schedule**: Daily at 02:00 via cron (hermes user)
- **Backup script**: Archives `/home/hermes/.hermes/` (config, API key, skills, sessions, mnemosyne data) to `/home/hermes/backups/hermes-backup-<timestamp>.tar.gz`
- **Encryption**: Optional, via `age` with deployer-provided public key -- `.tar.gz.age` at 0600
- **Retention**: `find ... -mtime +30 -delete` (configurable via `backup_retention_days`)
- **Restore**: Script at `sources/hermzner/scripts/restore.sh` auto-detects Tailscale IP, decrypts if needed, SCPs to server, stops runtime, extracts as hermes user, fixes permissions, restarts, runs verify
- **Gap**: Backups are local-only (on the VPS). No off-site or cloud backup is configured.

## Deploy Flow

The entry point `sources/hermzner/deploy.sh` orchestrates 7 phases:

1. **Prerequisite check**: Validates terraform, ansible-playbook, SSH key, HCLOUD_TOKEN, TAILSCALE_AUTH_KEY; detects deployer public IP for restricted mode
2. **Terraform apply**: Initializes, imports stale SSH key if needed, applies with auto-approve
3. **Inventory generation**: Extracts `server_ipv4` from Terraform output, writes `hosts.yml`
4. **SSH readiness loop**: Removes old host key, keyscans, retries SSH with exponential backoff (5s-60s, max 10 retries)
5. **Ansible site**: Runs `site.yml` with extra vars
6. **Verification**: Queries Tailscale IP, runs `verify.yml` if runtime started, prints Mnemosyne instructions if enabled
7. **Summary**: Prints server IP, Tailscale IP, DNS name, SSH commands, tunnel commands, hardening status

Idempotency is guaranteed -- rerunning `deploy.sh` is safe as Ansible roles are idempotent, secrets are never overwritten, and Terraform state tracks existing resources.

## Post-Deployment Verification

The 11-assertion verification playbook (`verify.yml`) validates:
1. Container is not privileged
2. User namespace is active
3. All capabilities are dropped
4. No-new-privileges is enabled
5. Seccomp is not disabled
6. AppArmor is not disabled
7. All ports are bound to 127.0.0.1
8. Container is not running as root
9. Data directory is 0700
10. .env file is 0600
11. Health endpoint responds

## Related

- [[hermzner-terraform-ansible]] -- Terraform and Ansible configuration reference
- [[hermzner-deployment]] -- deployment guide and operational procedures
- [[hermzner]] -- project overview and wiki
