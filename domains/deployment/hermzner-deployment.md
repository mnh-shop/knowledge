---
name: hermzner-deployment
tags: [hermzner, hetzner, deployment, terraform]
description: Hermzner Deployment Guide
---

# Hermzner Deployment Guide

This guide covers deploying a hardened Hermes Agent on a Hetzner VPS using the Hermzner provisioning pipeline.

## Prerequisites

- **Terraform** (1.5+)
- **Ansible** (core 2.15+)
- **Hetzner Cloud account** with API token (read+write)
- **Tailscale account** with pre-auth key (reusable, non-ephemeral)
- **SSH key pair** (default: `~/.ssh/id_ed25519`)
- **Internet access** from deployer host (for ifconfig.me to detect deployer IP)

### Environment Variables

```bash
export HCLOUD_TOKEN="<your-hetzner-api-token>"
export TAILSCALE_AUTH_KEY="tskey-auth-<...>"
```

These are read by `deploy.sh` and forwarded to Terraform/Ansible securely. Never write them to `.tfvars` files or version control.

## Quick Start

### 1. Clone and Configure

```bash
cd sources/hermzner

# Copy and customize Terraform variables
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit terraform.tfvars: set ssh_public_key, customize server_name if desired
```

The example tfvars file shows the expected variable pattern. Note that `hcloud_token` is NOT set here -- it is provided via the `TF_VAR_hcloud_token` environment variable.

### 2. Deploy

```bash
./deploy.sh
```

This single command runs the full 7-phase pipeline:

- Validates prerequisites
- Provisions the Hetzner server via Terraform
- Generates Ansible inventory
- Waits for SSH readiness
- Runs all 7 Ansible roles
- Runs post-deployment verification
- Prints connection summary

### 3. Connect

After deployment, `deploy.sh` prints connection details, including:

```
=== Connection Summary ===
Server IP:      123.123.123.123
Tailscale IP:   100.x.x.x
Tailscale DNS:  hermes.tailscale-xxxxx.ts.net

SSH (public):           ssh root@123.123.123.123
SSH (tailscale root):   ssh root@100.x.x.x
SSH (tailscale user):   ssh hermes@100.x.x.x

SSH Tunnel (dashboard): ssh -L 9119:127.0.0.1:9119 hermes@100.x.x.x
SSH Tunnel (API):       ssh -L 8642:127.0.0.1:8642 hermes@100.x.x.x

Open http://127.0.0.1:9119 in your browser.
```

## Variable Configuration

### Terraform Variables

Variables are in `terraform/variables.tf`. Set values in `terraform/terraform.tfvars`:

```hcl
server_type      = "cx23"          # Hetzner server type (default: cx23)
location         = "fsn1"          # Datacenter location (default: fsn1)
os_type          = "ubuntu-24.04"  # OS image (default: ubuntu-24.04)
server_name      = "hermes"        # Server name in Hetzner
ssh_public_key   = "ssh-ed25519 AAAA..."  # Your public key
```

### Ansible Variables

Group variables in `ansible/inventory/group_vars/all.yml`:

```yaml
# Image
hermes_image_ref: ghcr.io/hermes-agent/hermes-agent:latest@sha256:<digest>
hermes_dashboard_enabled: true

# Runtime
hermes_runtime_backend: quadlet          # quadlet or compose
hermes_start_runtime: true               # auto-start after deploy

# Mnemosyne memory backend
hermes_mnemosyne_enabled: false          # set true to enable

# Network
public_ssh_policy: disabled_after_tailscale  # disabled_after_tailscale, restricted, or open_key_only

# Hardening
sshd_hardening_enabled: true             # apply sshd hardening

# Backup
backup_encryption_enabled: false
backup_age_recipient: ""                 # age public key if encryption enabled
backup_retention_days: 30

# CORS
hermes_cors_origins:                     # list of allowed origins (no wildcards)
  - "http://localhost:9119"
  - "http://127.0.0.1:9119"
```

## Deploy Script Details

`deploy.sh` at `sources/hermzner/deploy.sh` accepts optional overrides:

```bash
# Override SSH key
PRIVATE_SSH_KEY=~/.ssh/id_rsa ./deploy.sh

# Allow unpinned image (skip digest validation)
ALLOW_UNPINNED_IMAGE=true ./deploy.sh

# Override deployer IP for restricted SSH mode
# (normally auto-detected via ifconfig.me)
DEPLOYER_IP=203.0.113.1 ./deploy.sh
```

### Phase Details

**Phase 1 -- Prerequisite check**: Validates all required tools and environment variables. Detects deployer public IP via `ifconfig.me` (with `icanhazip.com` fallback).

**Phase 2 -- Terraform apply**: Runs `terraform init -upgrade` and `terraform apply -auto-approve`. Attempts to import a stale SSH key if a prior deploy's key still exists in the Hetzner API (handles the case where a server was manually destroyed but the SSH key resource was not cleaned up).

**Phase 3 -- Inventory generation**: Writes `ansible/inventory/hosts.yml` with the server's public IP, targeting `root@<public-ip>` with the deployer SSH key.

**Phase 4 -- SSH readiness loop**: Removes old host key from `known_hosts`, keyscans, then attempts SSH connection with exponential backoff: 5s, 10s, 20s, 40s, 60s (max 10 retries). Host key verification is always enabled via `known_hosts`.

**Phase 5 -- Ansible site**: Executes `ansible/playbooks/site.yml` with extra vars passed on the command line (tailscale_auth_key, allow_unpinned_image, deployer_ip). The TAILSCALE_AUTH_KEY is handled with `no_log: true`.

**Phase 6 -- Verification**: Queries Tailscale IP and DNS name from the server. If `hermes_start_runtime: true`, runs `verify.yml` (11 assertions). If Mnemosyne is enabled, prints manual post-deploy instructions.

**Phase 7 -- Summary**: Prints all connection information in a formatted summary.

## Smoke Test

After deployment, verify the service is working:

```bash
# Check health endpoint via API tunnel
ssh -L 8642:127.0.0.1:8642 hermes@<tailscale-ip> -N &
curl http://127.0.0.1:8642/health
# Expected: {"status":"ok"} or similar

# Check dashboard via tunnel
ssh -L 9119:127.0.0.1:9119 hermes@<tailscale-ip> -N &
open http://127.0.0.1:9119

# Run the verification playbook directly
cd sources/hermzner/ansible
ansible-playbook -i inventory/hosts.yml playbooks/verify.yml
```

## Post-Deployment: Mnemosyne Setup

If Mnemosyne is enabled, a manual step is required after deployment:

```bash
SSH into the server via Tailscale:
ssh hermes@<tailscale-ip>

# Select the memory provider
podman exec -it hermes /opt/hermes/.venv/bin/hermes memory setup
# Choose 'mnemosyne' from the provider list

# Verify the setup
podman exec -it hermes /opt/hermes/.venv/bin/hermes memory status
```

## Managing the Service

```bash
# SSH via Tailscale
ssh hermes@<tailscale-ip>

# Check service status (Quadlet)
systemctl --user status hermes

# View logs
journalctl --user -u hermes -f

# Restart
systemctl --user restart hermes

# Podman commands
podman ps
podman logs hermes
```

## Redeployment

Re-running `deploy.sh` is safe and idempotent:

- Terraform detects existing resources and does nothing
- Ansible roles are idempotent (the API key check prevents overwrite)
- The SSH key import step only fires if the key is orphaned

To force a full redeploy (destroy and recreate):

```bash
cd sources/hermzner/terraform
terraform destroy -auto-approve
cd ..
./deploy.sh
```

## Backup and Restore

### Backups

Backups run automatically daily at 02:00 via cron (hermes user). To trigger manually:

```bash
ssh hermes@<tailscale-ip>
~/hermes-backup.sh
```

Backup archives are at `/home/hermes/backups/`. When encryption is enabled, files end in `.tar.gz.age`.

### Restore

Use the restore script from your deployer host:

```bash
sources/hermzner/scripts/restore.sh \
  --backup-file /path/to/hermes-backup-<timestamp>.tar.gz[.age] \
  [--age-key /path/to/age-key.txt] \
  [--tailscale-ip 100.x.x.x]
```

The script auto-detects the Tailscale IP from Terraform output if not provided.

## Troubleshooting

### SSH Not Connecting After Deployment

If the security role applied SSH hardening and you're locked out:

```bash
# Use Tailscale SSH (bypasses sshd_config entirely)
ssh -o ProxyCommand='tailscale ssh' root@<tailscale-ip>
# Or from another machine on the tailnet
ssh root@<tailscale-ip>
```

### Container Not Starting

```bash
ssh hermes@<tailscale-ip>
journalctl --user -u hermes -n 50 --no-pager
podman inspect hermes | jq '.[0].State.Status'
podman logs hermes
```

### Verification Assertion Failures

Run the verification playbook directly with verbose output:

```bash
cd sources/hermzner/ansible
ansible-playbook -i inventory/hosts.yml playbooks/verify.yml -v
```

Each of the 11 assertions prints a clear pass/fail message.

### Terraform State Issues

If Terraform state is out of sync with the Hetzner API:

```bash
cd sources/hermzner/terraform
terraform refresh
terraform plan
```

## Related

- [[hermzner-architecture]] -- architecture overview and design decisions
- [[hermzner-terraform-ansible]] -- Terraform and Ansible configuration reference
- [[hermzner]] -- project overview and wiki
