---
name: hermes-agent-docker
tags: [cli, hermes-agent, container, deployment, docker, packaging, wiki, hermes-agent-docker]
description: "Wiki entry for Hermes Agent Docker: minimal Docker image for Hermes Agent with configurable version pinning (MIT)"
source: sources/hermes-agent-docker/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# Hermes Agent Docker — Minimal Docker Image Packaging

| Field | Value |
|---|---|
| **Origin** | [NousResearch/hermes-agent-docker](https://github.com/NousResearch/hermes-agent-docker) |
| **License** | MIT |
| **Stack** | Docker, Hermes Agent |
| **Source** | `sources/hermes-agent-docker/` |
| **Wanted** | Minimal, reproducible Docker packaging for Hermes Agent — single-image build with configurable version pinning |

## Overview

A minimal Dockerfile that packages [Hermes Agent](https://github.com/NousResearch/hermes-agent) into a Docker image. It installs Hermes via the official upstream install script at a configurable `HERMES_REF` (branch or tag) and the `@openai/codex` CLI, handles Hermes state persistence through a seed-on-first-start entrypoint, and is designed for straightforward local builds and multi-arch publishing via a GitHub Actions workflow. The image is based on `docker/sandbox-templates:shell` and includes `ffmpeg` for media/codec handling. `mini-swe-agent` is listed in the README's image-contents but has **no explicit install step** in the Dockerfile and no corresponding directory in current hermes-agent `main` — treat that claim as README-stated/unverified.

## Key Features

- **Configurable version pinning** — Build any Hermes version via `--build-arg HERMES_REF` (defaults to `main`; accepts branches or tags like `v2026.3.30`)
- **State persistence with seed-on-first-start** — The `docker-entrypoint.sh` script checks if the mounted `/home/agent/.hermes` directory is empty; if so, it copies prepared defaults from `/usr/local/share/hermes-home/` and writes a `.docker-defaults-seeded` marker file to prevent re-seeding
- **Multi-component image** — Includes Hermes Agent (from upstream install script) and `@openai/codex` CLI (v0.118.0 by default) for AI-powered terminal commands, plus ffmpeg for media handling. `mini-swe-agent` is claimed in README.md:9 for SWE-bench-style tasks, but there is NO explicit install step for it in the Dockerfile and current hermes-agent `main` has no `mini-swe-agent/` directory — the claim is README-stated and unverified
- **Single-stage Dockerfile** — One `FROM` (Dockerfile:1) with multiple `RUN` layers: apt packages + ffmpeg (Dockerfile:10-14), Hermes install from the upstream script (Dockerfile:21-22), npm global `@openai/codex` (Dockerfile:24), npm audit fixes for hermes-agent and whatsapp-bridge (Dockerfile:26-30), skills-list pre-cache (Dockerfile:32), and entrypoint setup + default-state staging (Dockerfile:34-38). The base image switches `USER root` → `USER agent` twice to run privileged and non-privileged steps
- **Entrypoint design** — The `docker-entrypoint.sh` uses a two-phase approach: seeds empty Hermes home from defaults if needed, then `exec "$@"` to pass through to the user's command (Hermes CLI, doctor, or any other command)

## Usage

### Build locally

```bash
# Build latest main
docker build -t hermes-agent-docker:local .

# Build specific tag
docker build --build-arg HERMES_REF=v2026.3.30 -t hermes-agent-docker:v2026.3.30 .
```

### Run Hermes

Mount two paths: your current project into `/home/agent/workspace` and a persistent Hermes home directory into `/home/agent/.hermes`:

```bash
docker run --rm -it \
  -v "$PWD:/home/agent/workspace" \
  -v "$HOME/.hermes:/home/agent/.hermes" \
  hermes-agent-docker:local \
  hermes
```

### Run doctor

```bash
docker run --rm \
  -v "$HOME/.hermes:/home/agent/.hermes" \
  hermes-agent-docker:local \
  hermes doctor
```

### Persistence

Hermes config, sessions, memories, and related state live in `/home/agent/.hermes` inside the container. Mount that path to keep state across runs. On first start with an empty mount, the container seeds defaults from image-prepared Hermes defaults. If you do not mount `/home/agent/.hermes`, Hermes will still start, but its state will be lost when the container exits. Run `hermes setup` inside the container and persist `/home/agent/.hermes`, or place expected config files inside that mounted directory.

### CI/CD workflow (`.github/workflows/docker.yml`)

The repo ships a GitHub Actions workflow that builds and publishes the image to **GHCR** (`ghcr.io/<owner>/hermes-agent-docker`):

- **Triggers** (docker.yml:3-16): push to `main`, tags matching `v*`, pull requests (build-only, no push), and `workflow_dispatch` with a `hermes_ref` input (branch or tag, default `main`) for manual builds of any Hermes ref
- **Platforms** (docker.yml:66): `linux/amd64,linux/arm64` via QEMU + Buildx
- **Tag scheme** (docker.yml:52-57): branch ref, tag ref, commit SHA, `latest` on default branch, and the `hermes_ref` input value on manual dispatch
- **Push gating** (docker.yml:40,67): GHCR login and `push: true` only when the event is not a pull request
- **Build args** (docker.yml:64-65): `HERMES_REF` flows from the dispatch input or defaults to `main`; cache via `type=gha` (docker.yml:70-71)

The `HERMES_REF` build arg enables pinning to specific releases for reproducible deployments, and the seed-on-first-start pattern ensures fresh volumes work without manual initialization steps.

## Related

- [[hermes-agent]] — The agent this Docker image packages
- [[hermes-suite]] — All-in-one Hermes container with gateway + dashboard + webui (alternative packaging)
- [[podman]] — Container runtime (Podman-compatible) for deploying the Hermes Docker image
- [[tank-os]] — bootc-based OS image that can run Hermes containers with systemd-managed Quadlet files
- [[clawpier]] — Desktop GUI that manages Hermes/OpenClaw Docker containers
- [[hermzner]] — Production Hermes deployment blueprint on Hetzner VPS + Podman + Tailscale
- [[buildah]] — Alternative image build approach for Hermes container images
- [[mission-control]] — Dashboard alternative for managing Hermes
- [[openclaw]] — Comparable Docker packaging for competing agent platform
