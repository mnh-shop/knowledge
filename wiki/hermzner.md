---
name: hermzner
tags: [hermzner, wiki, terraform, ansible, infrastructure-as-code, hetzner, vps, deployment-automation, orchestration, networking, automation, ai-llm, bootc, container, dashboard, desktop-app, docker, git, monitoring, quadlet, security, systemd]
description: "Hermzner — Hardened Hermes on Hetzner"
---

# Hermzner — Hardened Hermes on Hetzner

| Field | Value |
|---|---|
| **Origin** | [LobsterTrap/hermzner](https://github.com/LobsterTrap/hermzner) |
| **License** | Not specified (likely MIT) |
| **Stack** | Terraform + Ansible + Rootless Podman + Tailscale |
| **Source** | `sources/hermzner/` |
| **Wanted** | One-command deploy of hardened Hermes Agent on Hetzner cloud |

## What it is

Hermzner provisions a **hardened Hermes Agent** on Hetzner Cloud with a single `./deploy.sh` command. Terraform creates the VPS, Ansible configures it — rootless Podman, Tailscale for networking, UFW lockdown, daily backups, and optional Mnemosyne memory backend.

It is a **deployment blueprint**, not a service. You clone it, edit `terraform.tfvars` + Ansible vars, and run.

## What Gets Deployed

| Component | Detail |
|---|---|
| **VPS** | Hetzner cx23, Ubuntu 24.04 |
| **Container Runtime** | Rootless Podman (Quadlet default, Compose fallback) |
| **Network** | Tailscale SSH + subnet access (SSH tunnel pattern) |
| **Service** | Hermes Agent (gateway, API, optional dashboard) |
| **Memory** | Mnemosyne (SQLite-vec) — optional, toggle via `hermes_mnemosyne_enabled` |
| **Backups** | Daily local backups to `/home/hermes/backups/`, 30-day retention, optional age encryption |

## Security Controls

- Rootless container, all capabilities dropped, no-new-privileges
- All ports bound to 127.0.0.1 (access via Tailscale SSH tunnel)
- UFW default deny, only `tailscale0` allowed
- Read-only root filesystem, tmpfs for `/tmp` and `/run`
- API key auto-generated, `.env` at `0600` permissions
- **Image digest pinning required** — fail-closed if missing
- Fails2ban + security hardening roles

## Deploy Flow

```bash
# 1. Edit Terraform variables
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# 2. Resolve and pin Hermes image digest
curl -s "https://hub.docker.com/v2/repositories/nousresearch/hermes-agent/tags/main" | jq -r '...'
# 3. Set in Ansible vars: hermes_image_ref: 'docker.io/nousresearch/hermes-agent@sha256:<digest>'
# 4. Deploy
HCLOUD_TOKEN=your_token TAILSCALE_AUTH_KEY=tskey-auth-... ./deploy.sh
```

Ansible connects via the server's **public IPv4** (Tailscale isn't available until the Tailscale role runs).

## Post-Deployment

```bash
# Access dashboard via SSH tunnel
ssh -L 9119:127.0.0.1:9119 hermes@<tailscale-ip>
# Open http://127.0.0.1:9119
```

## Relation to Core Systems

Hermzner is **specifically for [[hermes-agent]]** — it deploys Hermes and nothing else. It does not deploy or configure [[agentfield]], [[n8n]], or [[openclaw]]. It could be extended to deploy a combined stack, but out of the box it's single-service.

## Related

- [Architecture](domains/architecture/hermzner-architecture.md) — Terraform+Vault+Ansible architecture, security controls, Tailscale integration
- [Deployment](domains/deployment/hermzner-deployment.md) — Deploy flow, networking, secrets, monitoring
- [Terraform+Ansible Config](assets/deployment/hermzner-terraform-ansible.md) — Complete reference configs

## Similar Repos

- [[tank-os]] — same deployment pattern, but for OpenClaw (bootc image rather than Terraform + Hetzner)

## Related

- [[hermzner-architecture]] — architecture overview and design decisions
- [[hermzner-deployment]] — deployment guide and operational procedures
- [[hermzner-terraform-ansible]] — Terraform and Ansible configuration reference

## Cross-project

- [[hermes-agent]] -- Deploys Hermes Agent on Hetzner VPS
- [[podman]] -- Rootless Podman as container runtime
- [[tank-os]] -- Similar deployment pattern (bootc vs Terraform)
- [[openclaw]] -- Comparable deployment pattern (bootc-based)
- [[agentfield]] -- Could be extended to deploy
- [[n8n]] -- Could be included in combined stack deployment
- [[gogs]] -- Self-hosted Git service for deployment configs
- [[buildah]] -- Building container images for deployment
- [[clawpier]] -- Desktop alternative to VPS deployment
