# Hermes Agent Docker — Minimal Docker Image Packaging

| Field | Value |
|---|---|
| **Origin** | [NousResearch/hermes-agent-docker](https://github.com/NousResearch/hermes-agent-docker) |
| **License** | MIT |
| **Stack** | Docker, Hermes Agent |
| **Source** | `sources/hermes-agent-docker/` |
| **Wanted** | Minimal, reproducible Docker packaging for Hermes Agent — single-image build with configurable version pinning |

## What it is

A minimal Dockerfile that packages [Hermes Agent](https://github.com/NousResearch/hermes-agent) into a Docker image. It installs Hermes via the official upstream install script, includes `mini-swe-agent` and `codex` CLI, and handles Hermes state persistence. Designed for straightforward local builds and multi-arch publishing.

## Image Contents

- **Hermes Agent** — installed from upstream script at a configurable `HERMES_REF` (branch or tag)
- **mini-swe-agent** — included for SWE-bench-style tasks
- **Codex CLI** — `@openai/codex` (v0.118.0 by default) for AI-powered terminal commands
- **ffmpeg** — for media/codec handling
- **Entrypoint** — `docker-entrypoint.sh` seeds Hermes home directory from prepared defaults if empty

## Build

```bash
# Build latest main
docker build -t hermes-agent-docker:local .

# Build specific tag
docker build --build-arg HERMES_REF=v2026.3.30 -t hermes-agent-docker:v2026.3.30 .
```

## Run

```bash
# Interactive
docker run --rm -it \
  -v "$PWD:/home/agent/workspace" \
  -v "$HOME/.hermes:/home/agent/.hermes" \
  hermes-agent-docker:local \
  hermes

# Doctor
docker run --rm \
  -v "$HOME/.hermes:/home/agent/.hermes" \
  hermes-agent-docker:local \
  hermes doctor
```

## Persistence

Hermes config, sessions, memories, and state live in `/home/agent/.hermes`. Mount this path to keep state across runs. On first start with an empty mount, the container seeds defaults from image-prepared Hermes defaults.

## Relation to Other Hermes Packaging

| Package | Description |
|---|---|
| [[hermes-agent-docker]] | Minimal single-Dockerfile packaging (this repo) |
| [[hermes-suite]] | All-in-one container with gateway + dashboard + webui |
| [[hermzner]] | Full deployment blueprint: Hetzner VPS + Podman + Tailscale |
| [[hermes-agent]] | Upstream Hermes Agent source |

## Related

- [[hermes-agent]] — The agent this Docker image packages
- [[clawpier]] — Desktop GUI that manages Hermes/OpenClaw Docker containers
- [[hermes-suite]] — All-in-one Hermes container (alternative)
- [[hermzner]] — Production Hermes deployment blueprint
