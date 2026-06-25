---
name: hermes-agent-docker-deployment
tags: [ai-llm, container, container-deployment, deployment, docker, hermes-agent-docker, packaging, podman]
description: Hermes Agent Docker deployment guide for the minimal Docker image packaging
source: sources/hermes-agent-docker/
---

# Hermes Agent Docker — Deployment

| Field | Value |
|---|---|
| **Source** | `sources/hermes-agent-docker/` |
| **Type** | Docker image |

## Build

```bash
# Default (main branch)
docker build -t hermes-agent-docker:local .

# Pinned version
docker build \
  --build-arg HERMES_REF=v2026.3.30 \
  -t hermes-agent-docker:v2026.3.30 .

# Change Codex version
docker build \
  --build-arg HERMES_REF=v2026.3.30 \
  --build-arg CODEX_VERSION=0.120.0 \
  -t hermes-agent-docker:v2026.3.30 .
```

## Run

### Interactive Chat

```bash
docker run --rm -it \
  -v "$PWD:/home/agent/workspace" \
  -v "$HOME/.hermes:/home/agent/.hermes" \
  hermes-agent-docker:local \
  hermes
```

### One-shot Command

```bash
docker run --rm \
  -v "$HOME/.hermes:/home/agent/.hermes" \
  hermes-agent-docker:local \
  hermes doctor
```

### With Gateway Mode

```bash
docker run --rm -d \
  -v "$HOME/.hermes:/home/agent/.hermes" \
  -p 8642:8642 \
  hermes-agent-docker:local \
  gateway
```

## Persistence

Mount `/home/agent/.hermes` to persist config, sessions, memories, and state.
On first start with an empty mount, the container seeds the directory with Hermes defaults from `/usr/local/share/hermes-home/`.

## Podman

The image works with Podman since it uses standard Dockerfile instructions:

```bash
podman build -t hermes-agent-docker:local .
podman run --rm -it \
  -v "$PWD:/home/agent/workspace:Z" \
  -v "$HOME/.hermes:/home/agent/.hermes:Z" \
  hermes-agent-docker:local \
  hermes
```

## Multi-arch

The image builds on both amd64 and arm64. The Dockerfile doesn't specify a specific base arch — it uses `docker/sandbox-templates:shell` which supports multi-arch.

## Related

- [[hermes-agent-docker]] — Wiki entry
- [[hermes-agent]] — The agent runtime this packages
- [[hermes-agent-deployment]] — Full deployment guide
- [[hermes-suite]] — Alternative all-in-one Hermes container
- [[hermes-suite-deployment]] — Suite deployment guide
- [[hermes-suite-architecture]] — Suite architecture
- [[clawpier]] — Desktop GUI alternative
