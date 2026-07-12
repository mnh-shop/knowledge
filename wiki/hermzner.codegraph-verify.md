---
title: hermzner.codegraph-verify
date: 2026-07-12
tags: [hermzner, codegraph-verify, hermes-agent, hetzner]
related: [[hermzner]], [[hermes-agent]], [[hermes-agent-docker]], [[tank-os]]
source: sources/hermzner/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# hermzner — CodeGraph Verification

## Claim-1: Full infrastructure-as-code provisioning pipeline (Terraform → Ansible → deploy.sh)

The project uses Terraform to provision a Hetzner CX23 VPS (Ubuntu 24.04) and Ansible to configure it, orchestrated by `deploy.sh`. Terraform handles VPS creation (`hcloud_server`), SSH key injection, and optional cloud firewall. Ansible runs 7 roles via `site.yml`: podman, tailscale, security, mnemosyne_build, hermes, mnemosyne_runtime, backup. The deploy script runs Terraform, waits for SSH readiness, then runs Ansible.

**Source evidence:** `README.md` lines 32-34 ("deploy.sh runs Terraform (provisions VPS) then Ansible (configures it). Ansible connects via the server's public IPv4."). Lines 53-61 (deployment architecture table: VPS = Hetzner cx23, Ubuntu 24.04). `terraform/main.tf` lines 1-50 (Terraform configuration: hcloud provider, SSH key resource, firewall, server resource with lifecycle precondition). `ansible/roles/` directory with 7 roles confirmed.

## Claim-2: 20 security principles implemented across all roles with fail-closed verification

Every role implements principles from `COVENANT.md`. Security controls include: rootless containers (all capabilities dropped, no-new-privileges), ports bound to 127.0.0.1 (Tailscale SSH tunnel only), UFW default deny (only tailscale0 allowed), read-only root filesystem with tmpfs for /tmp and /run, API key auto-generated at 0600 permissions, image digest pinning required (fail-closed). A verify.yml playbook runs 11 security invariant checks post-deployment.

**Source evidence:** `README.md` lines 62-71 (Security Controls: "Rootless container, all capabilities dropped, no-new-privileges", "All ports bound to 127.0.0.1", "UFW default deny, only tailscale0 allowed", "Read-only root filesystem", "API key auto-generated, .env at 0600", "Image digest pinning required"). `AGENTS.md` lines 39-51 (Security Verification: 11 checks including container not privileged, user namespace active, all capabilities dropped, no-new-privileges, ports bound to 127.0.0.1, health endpoint). `AGENTS.md` lines 18-20 ("This project implements all 20 principles from COVENANT.md").

## Claim-3: Rootless Podman with Quadlet (default) and Compose (fallback) runtime

The container runtime uses rootless Podman with Quadlet as the default backend and Compose as fallback. Quadlet provides cleaner systemd lifecycle integration. The dedicated `hermes` user has subuid/subgid configured. Runtime backend is configurable via `hermes_runtime_backend` variable with preflight assertion that it must be `quadlet` or `compose`.

**Source evidence:** `README.md` line 56 (table: "Container Runtime: Rootless Podman (Quadlet default, Compose fallback)"). `AGENTS.md` lines 12-14 (Key Architecture Decisions: "Quadlet gives cleaner systemd lifecycle; Compose for environments without systemd user sessions"). Lines 28-29 (Preflight Assertions: `hermes_runtime_backend` is `quadlet` or `compose`). `ansible/roles/podman/` role configures rootless Podman with subuid/subgid and linger.

## Claim-4: Tailscale networking with zero public port exposure

All service ports are bound to 127.0.0.1 and accessed exclusively through Tailscale SSH tunnel. Tailscale is installed via apt, configured with a pre-auth key, SSH enabled, and the Tailscale IP is registered. Ansible connects via public IPv4 initially (before Tailscale exists), then all subsequent access goes through Tailscale. Dashboard is accessed via SSH tunnel on port 9119.

**Source evidence:** `README.md` lines 64-65 ("All ports bound to 127.0.0.1 (access via Tailscale SSH tunnel)"). Lines 76-80 (dashboard access: `ssh -L 9119:127.0.0.1:9119 hermes@<tailscale-ip>`). `README.md` line 57 (table: "Network: Tailscale SSH + subnet access"). `AGENTS.md` lines 12-16 (Key Architecture Decisions: "No public port exposure; ports bound to 127.0.0.1", "Ansible runs before Tailscale exists — connects via Hetzner-assigned IPv4"). `ansible/roles/tailscale/` role handles installation and auth key configuration.

## Claim-5: Mnemosyne SQLite-vec memory backend (optional, dual-role deployment)

Mnemosyne provides persistent memory via SQLite-vec for Hermes Agent. When enabled via `hermes_mnemosyne_enabled: true`, two dedicated Ansible roles activate: `mnemosyne_build` (builds a custom container image extending pinned Hermes base with `mnemosyne-memory[all]`) and `mnemosyne_runtime` (runs `mnemosyne.install` inside container post-deploy, restarts service if changes made). Memory data at `/home/hermes/.hermes/mnemosyne/` included in daily backups.

**Source evidence:** `README.md` lines 58-59 (table: "Mnemosyne Memory: SQLite-vec memory backend (optional)"), lines 83-124 (entire Mnemosyne Memory Backend section with enable toggle, build role, runtime role, post-deploy setup, manual setup). `ansible/roles/mnemosyne_build/` and `ansible/roles/mnemosyne_runtime/` directories confirmed. `AGENTS.md` lines 25-26 (Key Architecture Decisions: "Memory backend: Mnemosyne (opt-in via hermes_mnemosyne_enabled)", "SQLite-vec memory, custom Docker image built from pinned base").

## Claim-6: Daily encrypted backups with age and 30-day retention

Daily backups run via cron at 2am as the `hermes` user. Archives `/home/hermes/.hermes/` (data + auto-generated .env) to `/home/hermes/backups/` with 30-day retention. Mnemosyne memory data included automatically. Optional age encryption via `backup_encryption_enabled: true` and `backup_age_recipient` (deployer's age public key). Restore script auto-detects Tailscale IP from Terraform state.

**Source evidence:** `README.md` lines 126-151 (Backup & Restore section: "Daily backups run via cron at 2am", "30-day retention", backup file formats `.tar.gz` and `.tar.gz.age`, restore script with age private key support). `AGENTS.md` lines 19-20 (Key Architecture Decisions: "age (opt-in) — backup_encryption_enabled + backup_age_recipient"). `ansible/roles/backup/` directory confirmed. `scripts/restore.sh` confirmed in directory listing.

## Claim-7: Preflight assertions and local security scanning

The `site.yml` playbook runs fail-closed preflight assertions before any role executes: `hermes_image_ref` must be digest-pinned, `api_server_cors_origins` must not be `"*"`, runtime backend must be `quadlet` or `compose`, SSH policy must be one of three allowed values, bind mode must be `localhost`, age recipient must be set if encryption enabled. `scripts/repo_check.sh` scans for secret leakage, dangerous container flags, image pinning enforcement, and syntax errors locally.

**Source evidence:** `AGENTS.md` lines 28-35 (Preflight Assertions: "Before any role executes, site.yml validates" with 7 assertion rules). `README.md` lines 165-179 (repo_check.sh: "scans for secret leakage, dangerous container flags (--privileged, host networking), image pinning and port binding enforcement, shell/YAML/Ansible syntax errors, optional Terraform validation"). `README.md` line 179 ("Output is written to hermzner-local-check-report.txt").
