---
name: hermzner-api
description: "Hermzner API — Terraform outputs, Ansible variables, Hetzner Cloud API integration, deployment hooks"
source: sources/hermzner/
tags: [hermzner, api, deployment, terraform]
---

# Hermzner API

Hermzner exposes its API surface through **Terraform outputs**, **Ansible variables**, **Hetzner Cloud API integration**, and **deployment lifecycle hooks**. No HTTP server — the API is declarative infrastructure-as-code.

## Overview

A deployment blueprint that provisions a hardened Hermes Agent on Hetzner Cloud via `./deploy.sh`. Terraform creates the VPS, Ansible configures it — rootless Podman, Tailscale, UFW lockdown, daily backups.

## API Surface

**Terraform Variable API (`terraform/`):**
| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `hcloud_token` | string | (required) | Hetzner Cloud API token |
| `server_type` | string | `cx23` | VPS plan |
| `location` | string | `nbg1` | Datacenter |
| `ssh_keys` | list | `[]` | Hetzner SSH key names |

**Terraform Outputs:**
| Output | Consumer |
|--------|----------|
| `server_ipv4` | Ansible inventory |
| `tailscale_ip` | Post-deployment access |
| `server_id` | Ansible variables |

**Ansible Variable API (`ansible/group_vars/all.yml`):**
| Variable | Purpose |
|----------|---------|
| `hermes_api_key` | Gateway Bearer token (auto-generated) |
| `hermes_image_ref` | Digest-pinned container image |
| `tailscale_auth_key` | Tailscale node auth key |
| `hermes_mnemosyne_enabled` | Optional memory backend toggle |
| `hermes_dashboard_enabled` | Dashboard enable/disable |
| `backup_retention_days` | Local backup retention period |

**Deployment Hook API (`./deploy.sh`):**
1. `terraform apply` — provisions Hetzner VPS
2. `ansible-playbook` — configures OS, Podman, Tailscale, Hermes
3. `curl /health` — post-deploy gateway health check
4. `ssh -L` — prints tunnel access command

## Authentication

Hetzner Cloud API token (`HCLOUD_TOKEN` env var), Tailscale auth key (`TAILSCALE_AUTH_KEY` env var). Post-deployment access via Tailscale SSH only.

## Usage

```bash
# 1. Set credentials
export HCLOUD_TOKEN="..."
export TAILSCALE_AUTH_KEY="tskey-auth-..."

# 2. Pin image digest
curl -s "https://hub.docker.com/v2/repositories/nousresearch/hermes-agent/tags/main" | jq -r '.images[0].digest'

# 3. Deploy
./deploy.sh

# 4. Access
ssh -L 9119:127.0.0.1:9119 hermes@<tailscale-ip>
```

## Related

- [[domains/api/INDEX|api]]
- [[hermzner]] — Full deployment docs
- [[hermes-agent]] — The agent being deployed
- [[hermes-agent-docker]] — Docker packaging used
- [[tank-os]] — Similar deployment pattern (bootc)
