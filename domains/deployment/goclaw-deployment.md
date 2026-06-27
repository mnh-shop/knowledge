---
name: goclaw-deployment
description: "GoClaw deployment — Go binary deployment, container images, Quadlet patterns, environment configuration"
tags: [deployment, goclaw, golang]
source: sources/goclaw/
---

# GoClaw Deployment

## Overview

GoClaw is a Go-based desktop application (Wails) with a CLI gateway server, web UI, and Docker-based sandboxing for code execution. This document covers its deployment characteristics.

## Project Structure

- **Entry point**: `main.go` at repository root
- **CLI gateway**: `cmd/gateway.go` — primary server entry point (`runGateway` at line 79)
- **Desktop app**: `ui/desktop/app.go` — Wails desktop wrapper (`NewApp`, `startGateway`)
- **Web UI**: `ui/web/` — React/TypeScript frontend
- **Sandbox**: `internal/sandbox/docker.go` — Docker-based sandbox for code execution
- **Package helper**: `cmd/pkg-helper/main.go` — Alpine Linux apk package management

## Build and Release

- **Makefile** (5.1 KB) — build targets for development and release
- **go.mod** (10.9 KB) — Go module definition
- **GitHub Actions**: CI and release workflows in `.github/workflows/`
  - `ci.yaml` (3.7 KB) — continuous integration checks
  - `release.yaml` (10.2 KB) — release pipeline, including GitHub Releases
- **CI scripts**: `scripts/ci/semantic-beta-version.mjs` (6.4 KB) — semantic versioning for release tags

## Container Images

### Dockerfile (7.3 KB)

A multi-stage Docker build for the CLI gateway. Located at the repository root. Builds the Go binary and produces a minimal container image for running the gateway server.

### Docker Compose (2.9 KB)

`docker-compose.yml` at the repository root provides a local development / single-host deployment setup for the gateway and its dependencies.

## Docker Sandbox

GoClaw uses Docker as a sandbox for secure code execution. Implemented in `internal/sandbox/docker.go`:

- `DockerManager` (line 230) — manages a pool of Docker sandbox instances
- `NewDockerManager` (line 239) — creates the manager, called from `cmd/gateway_setup.go:36`
- `DockerSandbox` (line 31) — individual sandbox container
- Key behaviors:
  - Container caching with key-based reuse (`dockerCacheKey` at line 290)
  - Automatic pruning of stale containers (`startPruning` at line 371)
  - `Exec` (line 153) — run commands inside the sandbox
  - `Destroy` (line 216) — tear down sandbox
- Runtime dependency: Docker daemon must be available

## Configuration

### Config File Loading (`internal/config/config_load.go`)

Config is loaded from disk via `Load()` (line 127) with a `Default()` config (line 76). Environment variable overrides are applied via `applyEnvOverrides()` (line 149).

### Config Struct (`internal/config/config.go:45`)

Core configuration fields (identified from codegraph symbol analysis):

| Field / Section | Description |
|---|---|
| `SandboxConfig` (line 345) | Docker sandbox settings |
| `SkillsConfig` (line 133) | Skills/plugin configuration |
| `AgentsConfig` (line 234) | Agent definitions |
| `AgentDefaults` (line 240) | Default agent parameters |
| `SubagentsConfig` (line 539) | Sub-agent settings |
| `ClampSkillMaxUploadSizeMB` (line 161) | Upload size limit |

### Key Methods

- `ReplaceFrom` (line 569) — merge config from another source
- `Clone` (line 589) — deep copy configuration
- `ShellDenyGroupsSnapshot` (line 606) — shell access controls
- `ToSandboxConfig` (line 370) — extract sandbox-specific config
- `ValidateGatewayAuth` (config_load.go:34) — gateway auth validation
- `ApplyEnvOverrides` (config_load.go:521) — apply env overrides to loaded config
- `ResolvedDataDir` (config_load.go:429) — resolved data directory path
- `WorkspacePath` (config_load.go:445) — workspace directory path
- `ExpandHome` (config_load.go:526) — expand ~ in paths

### Config References from Channels

Channel-specific configs are defined in `internal/config/config_channels.go`:
- `ACPConfig` (line 300) — ACP channel configuration
- `TtsConfig` (line 564) — Text-to-speech configuration
- `HasAnyProvider` (line 365) — provider detection

## Environment Variables

Loaded from `.env.example` (926 bytes) at the repository root. Specific env vars identified from code analysis:

- Gateway auth env vars (`ValidateGatewayAuth`, `GatewayNoAuthFallbackAllowed`)
- Data directory and workspace path overrides
- Sandbox mode selection (`ModeNonMain`, `ModeAll` in `internal/sandbox/sandbox.go:110`)
- TTS provider credentials (ElevenLabs, Edge, MiniMax, OpenAI, Gemini)
- MCP OAuth configuration
- Channel-specific tokens (Discord, Telegram, Bitrix24)

## Deployment Modes

1. **Desktop App** (macOS/Linux/Windows)
   - Uses `ui/desktop/app.go` — Wails-based desktop wrapper
   - Starts embedded gateway via `RunGateway` (from `cmd/gateway_export.go:5`)
   - Local data directory managed by `GetDataDir` (ui/desktop/app.go:264)

2. **CLI Gateway Server**
   - Standalone binary deployment
   - Runs the gateway service with HTTP/webhook listeners
   - Docker sandbox for code execution
   - Configured via config file and environment variables

3. **Docker Container**
   - Multi-stage Dockerfile for minimal image
   - Docker Compose for local/orchestrated deployment

## Runtime Dependencies

- Go runtime (built as static binary, no runtime dependency)
- Docker daemon (for sandbox execution)
- Data directory for agent state, skills, memory
- Network access to LLM provider APIs

## CI/CD Pipeline

### CI Workflow (`.github/workflows/ci.yaml`)
Runs on pushes and pull requests. Likely includes:
- Go build and test
- Linting/static analysis
- Web UI build

### Release Workflow (`.github/workflows/release.yaml`)
Larger workflow (10.2 KB) that handles:
- GitHub Release creation
- Version tagging via `scripts/ci/semantic-beta-version.mjs`
- Multi-platform binary builds
- Container image build and push (via Dockerfile)

## Notes

- No systemd units, Quadlet files, or Nix expressions found in the repository
- No GoReleaser configuration found
- Docker sandbox requires the Docker socket to be accessible at runtime
- The `.dockerignore` file controls build context for the Dockerfile

## Related

- [[deployment]]
- [[goclaw]]
- [[podman]]
