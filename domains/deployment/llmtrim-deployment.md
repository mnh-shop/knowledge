---
name: llmtrim-deployment
tags: [llmtrim, deployment, proxy, llm]
description: llmtrim — Deployment
source: sources/llmtrim/
---

# llmtrim — Deployment

**Source:** `sources/llmtrim/` · `sources/llmtrim/Dockerfile` · `sources/llmtrim/crates/llmtrim-cli/src/`

## Overview

llmtrim is a local proxy that compresses LLM API requests before they reach the provider, reducing token consumption by a measured average of 31% input tokens and 74% output tokens with no change in answer quality. Written in Rust, it runs as a local HTTPS proxy, MCP server, or CLI tool.

The primary deployment model is a **local user-space daemon** (`llmtrim setup` + `llmtrim serve`), but it is also available as a **Docker image** for server-side deployments. The proxy binds to `0.0.0.0:43117` by default with no external dependencies — no database, no runtime, no model to load.

## Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 64 MB | 128 MB |
| CPU | 1 core | 1 core |
| Runtime | None (static musl binary) | Docker for containerized |
| Disk | 30 MB (binary) | 100 MB (benchmark data) |
| Network | Outbound to LLM provider API | Outbound to LLM provider API |

## Deployment Steps

### 1. Quick Start (User-Space Daemon)

```bash
# Install via Homebrew (macOS/Linux)
brew install fkiene/tap/llmtrim

# Or download binary directly
curl -fsSL https://github.com/fkiene/llmtrim/releases/latest/download/llmtrim-x86_64-musl.tar.gz | tar xz
sudo mv llmtrim /usr/local/bin/

# Setup CA certificate + shell profile
llmtrim setup

# Start the proxy daemon
llmtrim serve
```

The proxy starts on `0.0.0.0:43117`. Configure AI tools to use it via `HTTPS_PROXY=http://127.0.0.1:43117`.

### 2. Docker Compose

```yaml
version: '3.8'
services:
  llmtrim:
    image: ghcr.io/fkiene/llmtrim:latest
    container_name: llmtrim
    restart: unless-stopped
    ports:
      - "43117:43117"
    environment:
      - LLMTRIM_BIND=0.0.0.0
      - LLMTRIM_PORT=43117
      - LLMTRIM_LOG_LEVEL=${LLMTRIM_LOG_LEVEL:-info}
      - LLMTRIM_UPSTREAM_URL=${LLMTRIM_UPSTREAM_URL:-}
      - LLMTRIM_UPSTREAM_API_KEY=${LLMTRIM_UPSTREAM_API_KEY:-}
    volumes:
      - llmtrim_state:/data
    healthcheck:
      test: ["CMD", "llmtrim", "doctor"]
      interval: 60s
      timeout: 10s
      retries: 3

volumes:
  llmtrim_state:
    driver: local
```

### 3. Podman Quadlet

Save as `~/.config/containers/systemd/llmtrim.container`:

```ini
[Container]
Image=ghcr.io/fkiene/llmtrim:latest
ContainerName=llmtrim
PublishPort=43117:43117
Volume=llmtrim-state:/data
Environment=LLMTRIM_BIND=0.0.0.0
Environment=LLMTRIM_PORT=43117
Environment=LLMTRIM_LOG_LEVEL=%%LLMTRIM_LOG_LEVEL%%
Environment=LLMTRIM_UPSTREAM_URL=%%LLMTRIM_UPSTREAM_URL%%
Environment=LLMTRIM_UPSTREAM_API_KEY=%%LLMTRIM_UPSTREAM_API_KEY%%
HealthCmd=llmtrim doctor
HealthInterval=60s
HealthRetries=3
AutoUpdate=registry

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now llmtrim.service
```

### 4. Docker Image Details

The Docker image (`ghcr.io/fkiene/llmtrim`) is built from a **distroless base** (`gcr.io/distroless/cc-debian12:nonroot`) with a static musl binary — no shell, no package manager. Multi-arch support via buildx (`TARGETARCH` → `x86_64-musl` or `aarch64-gnu`).

```dockerfile
FROM gcr.io/distroless/cc-debian12:nonroot
ARG TARGETARCH
COPY binaries/${TARGETARCH}/llmtrim /usr/local/bin/llmtrim
ENV HOME=/data XDG_DATA_HOME=/data XDG_CONFIG_HOME=/data LLMTRIM_BIND=0.0.0.0
VOLUME /data
EXPOSE 43117
ENTRYPOINT ["/usr/local/bin/llmtrim"]
CMD ["serve"]
```

### 5. Integration with Hermes Agent

llmtrim ships a dedicated integration guide (`HERMES.md`). To use with Hermes:

```bash
# Set the proxy in Hermes environment
export HTTPS_PROXY=http://127.0.0.1:43117
export LLMTRIM_UPSTREAM_URL=https://api.anthropic.com  # or any provider
export LLMTRIM_UPSTREAM_API_KEY=sk-ant-...

# Run Hermes — all LLM API calls are compressed transparently
hermes start
```

### 6. Integration with OpenClaw

llmtrim works with any OpenAI-compatible provider. Configure OpenClaw to route through llmtrim:

```json
{
  "providers": {
    "openai": {
      "baseUrl": "http://127.0.0.1:43117/v1",
      "apiKey": "ignored"
    }
  },
  "mcp": {
    "servers": {
      "llmtrim": {
        "command": "llmtrim",
        "args": ["serve", "--mcp"]
      }
    }
  }
}
```

### 7. Compression Pipeline

llmtrim applies a 10-stage compression pipeline internally. No configuration is needed — it auto-detects provider format and optimizes accordingly:

| Stage | Purpose |
|-------|---------|
| 1. Tool output folding | Compress repeated tool call outputs |
| 2. Cache discipline | Optimize prompt-cache markers |
| 3. Lexical retrieval | BM25+ retrieval optimization |
| 4. Skeletonization | Tree-sitter for 14 languages |
| 5. Serialize + hygiene | JSON minification / TOON encoding |
| 6. JSON sampling | Record array downsampling |
| 7. Dedup | Remove duplicate content |
| 8. Output control | Limit output tokens |
| 9. Tool layer | Trim tool definitions |
| 10. Multimodal | Image downscaling |

### 8. CLI Subcommands

| Command | Description |
|---------|-------------|
| `llmtrim setup` | Start proxy, install CA cert, configure shell profile |
| `llmtrim serve` | Run as HTTPS proxy (default daemon mode) |
| `llmtrim status` | Live dashboard of tokens saved and dollars trimmed |
| `llmtrim status --watch` | Interactive real-time dashboard |
| `llmtrim compress < request.json` | Compress a single request body |
| `llmtrim doctor` | End-to-end diagnostic of proxy setup |
| `llmtrim serve --mcp` | Run as MCP server instead of HTTPS proxy |
| `llmtrim monitor` | Track compression savings over time |
| `llmtrim uninstall` | Reverse all setup changes |

## Persistent Storage

| Path | Contents |
|------|----------|
| `/data/` | State directory (CA certs, logs, benchmark data) |

The image runs as non-root (distroless default user). Mount `/data` for persistence.

## Related

- [[llmtrim]] — llmtrim wiki entry (architecture, pipeline, interfaces)
- [[hermes-agent]] — LLM agent that can use llmtrim as a proxy
- [[openclaw]] — AI assistant platform compatible with llmtrim routing
- [[headroom]] — Alternative LLM request optimizer (competitor/complement)
- [[nix-podman-stacks]] — Nix-based infrastructure for deploying llmtrim as a system service
