---
name: openclaw-plugin-claude-code.integration
description: "Integration companion for openclaw-plugin-claude-code — plugin manifest, npm + multi-arch build/publish pipeline, integration-test matrix, and the Podman/coding-agent decision guide"
source: sources/openclaw-plugin-claude-code/
parent: openclaw-plugin-claude-code
verification_date: 2026-07-12
verified_by: codegraph-verify
tags: [openclaw-plugin-claude-code, openclaw, claude-code, plugin, podman, integration, deployment, testing]
---

# openclaw-plugin-claude-code — Integration Companion

Companion to [[openclaw-plugin-claude-code]]. Covers the operational surface the main wiki only summarizes: what OpenClaw sees in the plugin manifest, how the package and container image get built and published, how the test suites are split, and the README's own guidance on when to use this plugin vs OpenClaw's `coding-agent` skill.

## Plugin Manifest (`openclaw.plugin.json`)

Shipped at the package root and copied into `dist/` during build (`package.json:37`). OpenClaw reads it to introspect the plugin without executing it.

```json
{
  "id": "claude-code",
  "version": "1.1.0",
  "description": "Run Claude Code sessions in isolated Podman containers",
  "main": "claude-code.js",
  "tools": [
    "claude_code_start",
    "claude_code_status",
    "claude_code_output",
    "claude_code_cancel",
    "claude_code_cleanup",
    "claude_code_sessions"
  ],
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "image":        { "type": "string",  "default": "ghcr.io/13rac1/openclaw-claude-code:latest", "description": "Container image for Claude Code sessions" },
      "runtime":      { "type": "string",  "default": "podman", "description": "Container runtime (podman or docker)" },
      "startupTimeout": { "type": "number", "default": 30, "description": "Seconds to wait for container to produce first output" },
      "idleTimeout":  { "type": "number",  "default": 120, "description": "Kill container after this many seconds of no output (hung detection)" },
      "memory":       { "type": "string",  "default": "2g", "description": "Memory limit for containers" },
      "cpus":         { "type": "string",  "default": "1.0", "description": "CPU limit for containers" },
      "sessionsDir":  { "type": "string",  "default": "~/.openclaw/claude-sessions", "description": "Directory for session data" },
      "workspacesDir":{ "type": "string",  "default": "~/.openclaw/workspaces", "description": "Directory for session workspaces" },
      "network":      { "type": "string",  "default": "bridge", "description": "Container network mode (none, bridge, host)" },
      "sessionIdleTimeout": { "type": "number", "default": 3600, "description": "Cleanup idle sessions after this many seconds" },
      "apparmorProfile": { "type": "string", "default": "", "description": "AppArmor profile name for containers (empty = disabled)" },
      "maxOutputSize": { "type": "number", "default": 10485760, "description": "Maximum output size in bytes (0 = unlimited). Default 10MB." }
    }
  },
  "uiHints": {
    "image": { "label": "Container Image" },
    "runtime": { "label": "Container Runtime" },
    "startupTimeout": { "label": "Startup Timeout (seconds)" },
    "idleTimeout": { "label": "Idle Timeout (seconds)" },
    "memory": { "label": "Memory Limit" },
    "cpus": { "label": "CPU Limit" },
    "network": { "label": "Network Mode" },
    "sessionIdleTimeout": { "label": "Session Cleanup Timeout (seconds)" },
    "apparmorProfile": { "label": "AppArmor Profile" },
    "maxOutputSize": { "label": "Max Output Size (bytes)" }
  },
  "requires": { "bins": ["podman"] }
}
```

**Key contract points for integrators:**
- `id: "claude-code"` is the plugin id used in `openclaw.json` under `plugins.entries["claude-code"].config`.
- The `tools` array must stay in sync with the `api.registerTool()` calls in `src/claude-code.ts` (lines 383, 495, 601, 639, 698, 742).
- `configSchema` is `additionalProperties: false` — unknown config keys are rejected by OpenClaw.
- `requires.bins: ["podman"]` lets OpenClaw warn when the runtime binary is missing before the first `claude_code_start`.

**Peer dependency:** `openclaw >= 2025.1.0` (`package.json:51-52`), `engines.node >= 22` (`:67-69`). The npm package ships `dist/` + `openclaw.plugin.json` (`files`, `:32-35`).

## Build & Publish Pipeline

### npm package

```
npm run build     # tsc && esbuild src/claude-code.ts --bundle --platform=node --format=esm
                  #   --outfile=dist/claude-code.js --external:openclaw
                  #   && cp openclaw.plugin.json dist/
npm run check     # lint + format:check + build + test:coverage  (gates prepublishOnly)
```

- The esbuild bundle keeps `openclaw` external — the plugin is loaded inside an OpenClaw process that provides the `PluginApi`.
- `prepublishOnly` runs `npm run check`, so a publish is blocked by lint/format/build/coverage failures.
- Releases are triggered by pushing a `v*` tag; CI publishes to npm **with provenance** and pushes multi-arch images to ghcr.io (README:376-403).

### Container image (`scripts/build-and-push.sh`)

```bash
# Single arch (default builds linux/arm64)
GITHUB_USERNAME=13rac1 ./scripts/build-and-push.sh

# Multi-arch: linux/arm64 + linux/amd64 + combined manifest
GITHUB_USERNAME=13rac1 ./scripts/build-and-push.sh --multi-arch

# Custom tag
GITHUB_USERNAME=13rac1 ./scripts/build-and-push.sh --multi-arch --tag v1.1.0
```

Multi-arch flow (lines 120-150):

1. `podman build --platform linux/arm64` → tag `:latest-arm64`, push
2. `podman build --platform linux/amd64` → tag `:latest-amd64`, push
3. `podman manifest create :latest` + `podman manifest add` both arch tags + `podman manifest push`

Prereqs: `podman` on PATH, `GITHUB_USERNAME` env var, and a ghcr.io login (`echo $PAT | podman login ghcr.io -u $USER --password-stdin`) with `write:packages` scope. Overrides: `IMAGE_NAME` (default `openclaw-claude-code`), `IMAGE_TAG` (default `latest`).

### Image contents (Dockerfile)

`debian:bookworm-slim` base with:
- Go 1.22.5 + TinyGo 0.32.0 (Wasm toolchains)
- Node.js 22 (NodeSource) + `npm i -g @anthropic-ai/claude-code`
- Python 3 + pip + venv
- Dev tools: git, ripgrep, fd-find, jq, curl, sqlite3, strace, build-essential
- Non-root `claude` user (uid 1000), `WORKDIR /workspace`, `ENTRYPOINT ["claude"]`

## Integration-Test Matrix

| Config | Target | Include | Timeout | Requires |
|--------|--------|---------|---------|----------|
| `vitest.config.ts` | Unit | `src/**/*.test.ts` (excludes `*.integration.test.ts`) | default | none (mocked) |
| `vitest.integration.config.ts` | Integration | `src/**/*.integration.test.ts` | 30s | real Podman + image |

Coverage gate (unit): 80% lines/functions/branches/statements via v8 provider; coverage reports published to PRs with `vitest-coverage-report-action`.

| Test file | Suite | Verifies |
|-----------|-------|----------|
| `claude-code.test.ts` | unit | Tool registration, config defaults, auth selection, orphan recovery logic (mocked) |
| `podman-runner.test.ts` | unit | Container command construction, env injection (mocked spawn) |
| `session-manager.test.ts` | unit | Session/job JSON state transitions |
| `notification.test.ts` | unit | Webhook payload + auth header |
| `stream-parser.test.ts` | unit | `stream-json` line parsing, session-id extraction |
| `format.test.ts` | unit | `formatDuration` / `formatBytes` |
| `job-lifecycle.integration.test.ts` | integration | Start → status → output → cancel/cleanup against a real container |
| `podman-runner.integration.test.ts` | integration | `podman run` flags, `--userns=keep-id`, stats, kill |
| `session-manager.integration.test.ts` | integration | Session state persisted across container restarts |

Commands: `npm test` (unit, runs prettier+eslint first), `npm run test:integration` (Podman required), `npm run test:all` (both).

## Decision Guide (README:57-85)

### Why Podman instead of Docker?

The plugin runs AI-generated code with `--dangerously-skip-permissions` — the container **is** the safety net.

- **Podman:** rootless by default. No daemon, no root process, no privilege-escalation path. A container escape lands in an unprivileged user namespace with no capabilities.
- **Docker:** default mode runs a **root daemon** — an escape gives full root on the host. Rootless Docker exists but requires explicit setup, and "most Docker forks of this plugin skip that step."
- `runtime: "docker"` is supported only for users who configured rootless Docker; Podman is strongly recommended.

### Why this plugin instead of the `coding-agent` skill?

The built-in `coding-agent` skill is a prompt teaching agents to delegate via OpenClaw's existing `bash`/`process` tools — lightweight, multi-agent (Codex, Claude Code, Pi), zero setup, but it runs agents **on the host** (or OpenClaw sandbox), with no per-session containment.

| | `coding-agent` skill | this plugin |
|---|---|---|
| Multi-agent (Codex/Pi/Claude Code) | ✅ | ❌ Claude Code only |
| Setup cost | Zero (load skill) | Image + plugin install |
| Containment for `--dangerously-skip-permissions` | Host/sandbox | Rootless Podman, `--cap-drop ALL`, resource limits, tmpfs `/tmp` |
| Session persistence across interactions | ❌ | ✅ session_id resume |
| Structured job management | ❌ | ✅ status/output pagination/activity detection/crash recovery |
| Hard resource limits | ❌ | ✅ memory/cpu/pids |

**Use the skill when:** multi-agent support matters, quick setup > isolation, you're comfortable with OpenClaw's sandbox, or tasks are short-lived.
**Use the plugin when:** real containment is required, sessions must survive across interactions, you need structured job management, or you run untrusted/experimental code.

They compose: skill for quick Codex tasks, plugin for long Claude Code sessions (README:85).

## Related

- [[openclaw-plugin-claude-code]] — Main wiki entry
- [[openclaw-plugin-claude-code.codegraph-verify]] — Source-verified claims
- [[openclaw]] — Agent platform; plugin extension point
- [[openclaw-container]] — OpenClaw container deployment patterns
- [[claw-code]] — Alternative coding-agent tooling (Rust `claw` CLI)
