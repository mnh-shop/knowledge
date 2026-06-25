---
name: tank-os-architecture
tags: [architecture, bootc, cli, container, container-os, fedora, git, image-based, immutable-os, mcp, messaging, podman, quadlet, systemd, tank-os]
description: Tank OS Architecture
---

# Tank OS Architecture

## Overview

Tank OS is a Fedora bootc image that packages the entire operating system plus an OpenClaw rootless Podman workload into a single bootable, updateable OCI container image. The image is published at `quay.io/sallyom/tank-os:latest` for both amd64 and arm64 architectures.

## Architecture Principles

- **Immutable OS image**: The entire deployment is a single OCI artifact, versioned and signed.
- **Transactional updates**: bootc provides A/B update semantics -- new deployments are staged, activated on reboot, and automatically rolled back if the new image fails.
- **Rootless by default**: All workloads run as user `openclaw` (UID/GID 1000) via rootless Podman.
- **Secret injection at boot**: Secrets are injected via rootless Podman secrets with Quadlet drop-in generation on first boot, not baked into the image.
- **Loopback-only networking**: All service ports bind exclusively to `127.0.0.1`, accessed via SSH tunnel.

## Image Build

The Containerfile at `sources/tank-os/bootc/Containerfile` (63 lines) defines the build:

1. **Base**: `quay.io/fedora/fedora-bootc:latest` (overridable via build ARG)
2. **Packages installed**: `cloud-init`, `openssh-server`, `podman`, `python3`, `qemu-guest-agent`, `shadow-utils`, `sudo`, `vim-enhanced`
3. **User creation**: `openclaw` user at UID/GID 1000, added to `wheel` group, with subordinate UID/GID mapping `100000:65536` configured in `/etc/subuid` and `/etc/subgid`
4. **Linger**: `/var/lib/systemd/linger/openclaw` enables systemd user services for `openclaw`
5. **Rootfs overlay**: `COPY rootfs/ /` installs Quadlet files, bootstrap scripts, sudoers configuration, and the release file into their final paths
6. **Service enablement**: `sshd.service` and all 5 `cloud-init` services are enabled

There is no `CMD` or `ENTRYPOINT` in the Containerfile -- bootc images use systemd as PID 1 by default.

## Quadlet Services

Two Quadlet files are installed at `/etc/containers/systemd/users/1000/` (the system-level Quadlet directory for user 1000), putting them under systemd user unit control for the `openclaw` user. Both are rootless Podman containers that start automatically on boot.

### openclaw.container

The primary OpenClaw gateway service:

| Field | Value |
|-------|-------|
| Image | `ghcr.io/openclaw/openclaw:latest` |
| Pull | `newer` |
| RunInit | `true` |
| UserNS | `keep-id` |
| Volumes | `%h/.openclaw:/home/node/.openclaw:Z` |
| Ports | `127.0.0.1:18789:18789`, `127.0.0.1:18790:18790` |
| Command | `node dist/index.js gateway --allow-unconfigured --bind lan --port 18789` |
| ExecStartPre | `/usr/libexec/tank-os/bootstrap-openclaw` |
| Restart | `on-failure` |
| TimeoutStartSec | `300` |

### service-gator.container

The MCP proxy service providing scoped access to external services:

| Field | Value |
|-------|-------|
| Image | `ghcr.io/cgwalters/service-gator:latest` |
| Pull | `newer` |
| RunInit | `true` |
| Volumes | `%h/.config/service-gator:/etc/service-gator:Z`, `%h/.openclaw:/workspaces:Z` |
| Ports | `127.0.0.1:8080:8080` |
| Command | `--mcp-server 0.0.0.0:8080 --scope-file /etc/service-gator/scopes.json` |
| After | `network-online.target` |
| ExecStartPre | `/usr/libexec/tank-os/bootstrap-service-gator` |
| Restart | `on-failure` |

The base Quadlet intentionally has no secret references so the container can start before credentials exist. Secrets are added dynamically via drop-in files in `~/.config/containers/systemd/<name>.container.d/10-secrets.conf`.

### Service-Gator Details

service-gator is an MCP proxy server that gives sandboxed agents scoped access to external services (GitHub, GitLab, Forgejo/Gitea, JIRA). It listens on `127.0.0.1:8080` and receives API tokens via Podman secrets mounted as files (`GH_TOKEN_FILE`, `GITLAB_TOKEN_FILE`, `FORGEJO_TOKEN_FILE`, `JIRA_API_TOKEN_FILE`). Per-repo and per-project scoped permissions are read from `~/.config/service-gator/scopes.json`, which is watched and reloadable without restart.

## Secret Management

Secrets are managed through a two-layer pipeline:

### 1. `tank-openclaw-secrets` (CLI wrapper)

Located at `/usr/local/bin/tank-openclaw-secrets`. A CLI wrapper that re-execs as the `openclaw` user via `sudo`, then delegates to `sync-podman-secrets`.

### 2. `sync-podman-secrets` (Bash + embedded Python, 230 lines)

The engine performs three tasks:

1. **Quadlet drop-in generation**: Checks `podman secret inspect` for each known secret name, then writes Quadlet drop-in files:
   - `~/.config/containers/systemd/openclaw.container.d/10-secrets.conf` with `Secret=name,type=env,target=ENV_VAR` lines for each OpenClaw secret
   - `~/.config/containers/systemd/service-gator.container.d/10-secrets.conf` with `Secret=name` lines for each service-gator secret

2. **OpenClaw config rewriting**: An inline Python script (66 lines) rewrites `~/.openclaw/openclaw.json`:
   - Sets `secrets.providers.default` source to `"env"`
   - Adds `models.providers` entries with `SecretRefs` for Google and OpenRouter (Anthropic/OpenAI use built-in env auth)
   - Sets `agents.defaults.models` allowlist with primary model preference: `OPENROUTER > OPENAI > ANTHROPIC > GEMINI > GOOGLE`
   - Configures `channels.telegram.botToken` if the `telegram_bot_token` secret exists

3. **Daemon reload**: Runs `systemctl --user daemon-reload` for the openclaw user

### Known Secrets

**OpenClaw**: `anthropic_api_key`, `openai_api_key`, `gemini_api_key`, `google_api_key`, `openrouter_api_key`, `model_endpoint_api_key`, `telegram_bot_token`

**Service-Gator**: `gh_token`, `gitlab_token`, `forgejo_token`, `jira_api_token`

### Bootstrap Scripts

Two bootstrap scripts run as `ExecStartPre` hooks to create initial directory structure and empty JSON configs on first boot:
- `bootstrap-openclaw`: Prepares `~/.openclaw/` directory structure
- `bootstrap-service-gator`: Prepares `~/.config/service-gator/` directory and default scopes

## Build System

The Makefile at `sources/tank-os/Makefile` (145 lines) provides:

- **`make build`**: `podman build --platform $(PLATFORM) -t $(IMAGE_URI):latest -f bootc/Containerfile bootc`
- **`make push`**: Pushes to registry (requires `IMAGE_REGISTRY` + `IMAGE_NAMESPACE`)
- **`make build-qcow2`**: Runs `bootc-image-builder` in a privileged container to produce a QCOW2 disk image
- **`make build-iso`**: Same but produces an anaconda-iso installer
- **`make lint`**: Runs `bootc container lint` on the image
- **`make verify`**: `cosign verify` with `COSIGN_PUBLIC_KEY`

Variables: `IMAGE_REGISTRY` and `IMAGE_NAMESPACE` have no defaults and must be set explicitly. Architecture auto-detected from `uname -m` (x86_64 -> amd64, aarch64 -> arm64).

### CI/CD (GitHub Actions)

- PR validation builds both architectures
- Semantic release creates version tags on main merges
- Full release builds per-arch images by digest, creates multi-arch manifest (latest, VERSION, SHA tags)
- Optional cosign signing, CycloneDX SBOM generation, build provenance + SBOM attestations, Trivy vulnerability scanning

## Update and Rollback

Transactional updates via the bootc mechanism:

- **First-time switch**: `sudo bootc switch --apply quay.io/sallyom/tank-os:latest` (from locally-built image to registry ref)
- **Upgrade**: `sudo bootc upgrade --apply`
- **Rollback**: `sudo bootc rollback`

bootc provides A/B deployment semantics: the new deployment is staged, activated on reboot, and automatically rolled back if the new image fails to boot.

## macOS Development Workflow

A complete workflow is documented in `sources/tank-os/docs/provisioning.md`:

1. **Build**: `make build ARCH=arm64` to build the bootc image locally
2. **QCOW2**: Build via Podman Desktop BootC extension or `make build-qcow2` (requires rootful Podman machine)
3. **Resize**: `qemu-img resize disk.qcow2 20G`
4. **Launch QEMU**: `qemu-system-aarch64 -machine virt,highmem=on -accel hvf -cpu host -smp 4 -m 4096` with `edk2-aarch64-code.fd` from Homebrew
5. **Find SSH port**: Use `gvproxy` process from Podman Desktop/macadam, or use port 2222 for QEMU hostfwd
6. **SSH tunnel**: `ssh -N -L 18789:127.0.0.1:18789 -L 18790:127.0.0.1:18790 openclaw@localhost -p <port>`
7. **Browse**: `http://127.0.0.1:18789`

Cloud-init config for local dev at `sources/tank-os/examples/cloud-init/openclaw-user-data.yaml`: creates `openclaw` user with `wheel` group, passwordless sudo, locked password, and `ssh_authorized_keys`. The `bootc-config.toml` example provides equivalent build-time user customization for `bootc-image-builder`.

## Generalizable bootc Pattern

The architecture generalizes cleanly to any service that needs to be deployed as an appliance-like VM:

1. Start from `fedora-bootc`
2. Install the target service as a rootless Quadlet under `/etc/containers/systemd/users/<UID>/`
3. Use the same linger + cloud-init + SSH key provisioning pattern
4. Replicate the secret management pipeline (Quadlet drop-in generation + config rewriting)
5. Replicate the CLI shim pattern for `sudo` delegation

A hypothetical `hermes-bootc` would differ only in base image tag, packages installed, Quadlet image/ports/volumes/command, bootstrap script logic, secret names, and config file locations. The entire OS+workload-as-OCI-image pattern, transactional updates via bootc, and the Podman secret injection pipeline are the reusable architectural assets.

## Related

- [[tank-os]] -- Wiki overview of the Tank OS project
- [[tank-os-quadlet]] -- Detailed Quadlet file reference
- [[tank-os-deployment]] -- Deployment guide
