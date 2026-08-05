---
name: openclaw-plugin-claude-code-codegraph-verify
tags: [openclaw-plugin-claude-code, codegraph-verify, openclaw, claude-code]
description: "Codegraph Verification: openclaw-plugin-claude-code — validating wiki claims against indexed source code"
source: sources/openclaw-plugin-claude-code/
---

# Codegraph Verification: openclaw-plugin-claude-code

**Date:** 2026-07-12

## Claim 1: Six OpenClaw tools registered via plugin API

- **Wiki says:** The plugin registers 6 tools: `claude_code_start`, `claude_code_status`, `claude_code_output`, `claude_code_cancel`, `claude_code_cleanup`, and `claude_code_sessions`.
- **Source evidence:**
  - `src/claude-code.ts` line 383: `api.registerTool({name: "claude_code_start", ...})`
  - `src/claude-code.ts` line 495: `api.registerTool({name: "claude_code_status", ...})`
  - `src/claude-code.ts` line 601: `api.registerTool({name: "claude_code_output", ...})`
  - `src/claude-code.ts` line 639: `api.registerTool({name: "claude_code_cancel", ...})`
  - `src/claude-code.ts` line 698: `api.registerTool({name: "claude_code_cleanup", ...})`
  - `src/claude-code.ts` line 742: `api.registerTool({name: "claude_code_sessions", ...})`
  - All tools are registered via the standard `PluginApi.registerTool()` interface with typed `Type.Object` parameter schemas
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 2: Rootless Podman containers with capability dropping, resource limits, and tmpfs

- **Wiki says:** Runs Claude Code in rootless Podman containers with `--cap-drop ALL`, configurable memory/CPU/PID limits, `/tmp` as tmpfs, and optional AppArmor profiles.
- **Source evidence:**
  - `src/podman-runner.ts` lines 288-399 (`startDetached()`): `podman run` with `--userns=keep-id:uid=1000,gid=1000`, `--cap-drop ALL`, `--memory`, `--cpus`, `--pids-limit 100`, `--tmpfs /tmp:rw,nosuid,size=512m`
  - `src/podman-runner.ts` lines 319-321: Optional `--security-opt apparmor=...` when `apparmorProfile` is set
  - `src/podman-runner.ts` lines 7-13: `PodmanConfig` interface defines `runtime`, `memory`, `cpus`, `network`, `apparmorProfile` fields
  - `src/claude-code.ts` lines 44-58: Default config `runtime: "podman"`, `memory: "2g"`, `cpus: "1.0"`, `network: "bridge"`
  - README.md lines 60-64: Documents why Podman is recommended over Docker for security
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3: Session persistence with session ID capture and multi-turn resume

- **Wiki says:** Claude Code session IDs captured and reused for multi-turn workflows. Session manager maintains per-session state, job history, and workspace directories.
- **Source evidence:**
  - `src/claude-code.ts` lines 260, 350-354: Captures `detectedClaudeSessionId` from stream output, persists via `sessionManager.updateSession()`
  - `src/claude-code.ts` lines 302-305: Resume flag: `--resume '${params.resumeSessionId}'` when resuming
  - `src/claude-code.ts` lines 416-417: `sessionManager.getOrCreateSession(sessionKey)` on start
  - `src/session-manager.ts` (exported class): Manages session state, job records, output files
  - README.md lines 89-95: "Session Persistence: Sessions maintain state across multiple interactions"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 3b: Plugin manifest, license, peer dependency, and distribution metadata

- **Wiki says:** `openclaw.plugin.json` ships `id: claude-code`, the 6 tool names, a JSON-Schema `configSchema` for every option, `uiHints` labels, and `requires: { bins: ["podman"] }`; the package is Apache-2.0, requires `openclaw >= 2025.1.0`, and Node.js >= 22.
- **Source evidence:**
  - `openclaw.plugin.json` lines 2-6: `"id": "claude-code"`, `"version": "1.1.0"`, `"main": "claude-code.js"`, and the explicit `tools` array of all 6 registered tool names
  - `openclaw.plugin.json` lines 7-72: `configSchema` covering `image`, `runtime`, `startupTimeout`, `idleTimeout`, `memory`, `cpus`, `sessionsDir`, `workspacesDir`, `network`, `sessionIdleTimeout`, `apparmorProfile`, `maxOutputSize` — each with type, default, and description
  - `openclaw.plugin.json` lines 73-84: `uiHints` label map per config field; lines 85-87: `"requires": { "bins": ["podman"] }`
  - `package.json` line 6: `"license": "Apache-2.0"` (LICENSE file present at repo root); lines 51-53: `"peerDependencies": { "openclaw": ">=2025.1.0" }`; lines 67-69: `"engines": { "node": ">=22.0.0" }`
  - `package.json` lines 32-35: `files: ["dist", "openclaw.plugin.json"]` — manifest ships in the npm package; build script (line 37) copies it into `dist/`
  - README.md lines 97-101 (Requirements): "OpenClaw >= 2025.1.0", "Podman (recommended) or Docker", "Node.js >= 22"
- **Verdict:** ✅ CORRECT (new claim — manifest/license/peer dep previously missing from wiki)
- **Fix needed:** None

## Claim 4: Real-time streaming output capture and pagination

- **Wiki says:** Output captured via `stream-json` format as it's generated. Supports pagination while running with byte offsets and size limits.
- **Source evidence:**
  - `src/claude-code.ts` lines 239-284 (`watchJobCompletion`): Streams container logs in real-time via `podmanRunner.streamContainerLogs()`, parses `stream-json` events, appends text output to file
  - `src/podman-runner.ts` lines 551-567 (`streamContainerLogs()`): Uses `podman logs -f` to follow logs in real-time
  - `src/claude-code.ts` lines 600-636 (`claude_code_output` tool): Supports `offset` and `limit` parameters for paginated reads
  - `src/stream-parser.ts` (confirmed on disk): `parseStreamLine()`, `extractTextFromStream()`, `parseSessionId()` functions
  - README.md line 90: "Real-time Streaming: Output is captured as it's generated using Claude Code's stream-json format"
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 5: Dual authentication — OAuth/Claude Max and API key

- **Wiki says:** Supports OAuth/Claude Max credentials (via mounted `~/.claude`) or API key. OAuth takes precedence when both are available.
- **Source evidence:**
  - `src/claude-code.ts` lines 116-142 (`getAuth()`): Checks `~/.claude/.credentials.json` first. If found, `hasCredsFile=true` and API key is not read. Falls back to `process.env.ANTHROPIC_API_KEY`.
  - `src/podman-runner.ts` lines 332-336: Mounts `hostClaudeDir:/home/claude/.claude:rw` for credential persistence
  - `src/podman-runner.ts` lines 338-340: Passes `ANTHROPIC_API_KEY` as environment variable when API key is used
  - `README.md` lines 257-264: Documents both auth methods: "If both are available, OAuth takes precedence."
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 6: Webhook notifications for job completion events

- **Wiki says:** Jobs push completion events (status, elapsed time, exit code, error type) via POST to configured webhook URL — no polling required.
- **Source evidence:**
  - `src/claude-code.ts` lines 214-236 (`sendCompletionNotification()`): Posts job completion event to `config.notifyWebhookUrl` with `hooksToken` auth
  - `src/claude-code.ts` lines 363-372: Completion notification sent with `jobId`, `sessionKey`, `status`, `elapsedSeconds`, `outputSize`, `exitCode`, `errorType`
  - `src/claude-code.ts` lines 673-686: Cancellation notification also sent
  - `src/notification.ts` (confirmed on disk): `notifyJobCompletion()` function and `JobCompletionEvent` interface
  - `README.md` lines 195-211: Documents webhook payload schema with TypeScript interface
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 7: Orphan container recovery on plugin startup

- **Wiki says:** Plugin recovers orphaned containers on startup, reconciling running containers with persisted job state.
- **Source evidence:**
  - `src/claude-code.ts` lines 799-852 (`recoverOrphanedJobs()`): Lists containers by prefix, matches against active jobs, cleans up orphans, recovers completed jobs
  - `src/claude-code.ts` line 796: Recovery triggered at plugin startup: `void recoverOrphanedJobs(sessionManager, podmanRunner)`
  - `src/podman-runner.ts` lines 494-544 (`listContainersByPrefix()`): Lists containers matching name prefix via `podman ps -a --filter name=^claude-`
- **Verdict:** ✅ CORRECT
- **Fix needed:** None

## Claim 8: Split test suite and multi-arch build/publish pipeline

- **Wiki says:** Vitest unit + integration configs; 9 test files total (6 unit, 3 integration); integration tests require a real Podman runtime with 30s timeouts. `scripts/build-and-push.sh` builds/pushes to ghcr.io; `--multi-arch` builds linux/arm64 + linux/amd64 and combines them into a multi-arch manifest.
- **Source evidence:**
  - `vitest.config.ts` lines 5-7: `include: ["src/**/*.test.ts"]`, `exclude: ["src/**/*.integration.test.ts"]`; lines 17-21: 80% coverage thresholds (lines/functions/branches/statements)
  - `vitest.integration.config.ts` lines 5-7: `include: ["src/**/*.integration.test.ts"]`, `testTimeout: 30000` for container operations
  - Test files on disk: unit = `claude-code.test.ts`, `podman-runner.test.ts`, `session-manager.test.ts`, `notification.test.ts`, `stream-parser.test.ts`, `format.test.ts`; integration = `job-lifecycle.integration.test.ts`, `podman-runner.integration.test.ts`, `session-manager.integration.test.ts`
  - `package.json` lines 43-46: `test` (unit), `test:integration`, `test:all` = unit + integration; line 49: `prepublishOnly` gates releases on `npm run check` (lint + format + build + coverage)
  - CHANGELOG.md lines 25-26: "Replace Codecov with `vitest-coverage-report-action`"
  - `scripts/build-and-push.sh` lines 120-150: `--multi-arch` branch — `podman build --platform linux/arm64` and `linux/amd64`, pushes both arch tags, then `podman manifest create/add/push` for the combined `:latest` manifest
  - `scripts/build-and-push.sh` lines 48-64: usage/`--tag`/env overrides (`GITHUB_USERNAME`, `IMAGE_NAME`, `IMAGE_TAG`); lines 104-110: fails fast without `GITHUB_USERNAME`; lines 159-165: single-arch build tags a local alias too
  - README.md lines 366-374: documents single-arch `podman build` and `GITHUB_USERNAME=13rac1 ./scripts/build-and-push.sh --multi-arch`; lines 400-403: release workflow "Build and push multi-arch container images to ghcr.io" on version tags
- **Verdict:** ✅ CORRECT (new claim — test suite and pipeline previously unmentioned in wiki)
- **Fix needed:** None

## Summary

All 8 key claims from the openclaw-plugin-claude-code wiki have been verified against the source code:
- ✅ 6 OpenClaw tools: All registered via `api.registerTool()` in `src/claude-code.ts`
- ✅ Rootless Podman containment: `--cap-drop ALL`, resource limits, tmpfs confirmed in `startDetached()`
- ✅ Session persistence: Session ID capture and resume confirmed
- ✅ Plugin manifest + distribution: `openclaw.plugin.json` (id/tools/configSchema/uiHints/requires), Apache-2.0, `openclaw >= 2025.1.0`, Node >= 22
- ✅ Real-time streaming: `podman logs -f` + `stream-json` parsing confirmed
- ✅ Dual auth: OAuth-first fallback to API key confirmed in `getAuth()`
- ✅ Webhook notifications: Completion events pushed via POST confirmed
- ✅ Orphan recovery: `recoverOrphanedJobs()` on startup confirmed
- ✅ Test suite + pipeline: split unit/integration vitest configs, 9 test files, 30s integration timeouts, `scripts/build-and-push.sh --multi-arch` manifest flow

## Related

- [[openclaw-plugin-claude-code]] -- Main wiki entry
- [[openclaw-plugin-claude-code.integration]] -- Companion: manifest, build/publish, integration-test matrix, decision guide
- [[openclaw]] -- Core agent platform this plugin extends
- [[openclaw-container]] -- Container deployment for OpenClaw
- [[claw-code]] -- Related coding agent tooling

## Cross-project

- [[openclaw.codegraph-verify]] -- Similar codegraph verification for OpenClaw
- [[podman]] -- Container runtime for plugin isolation
- [[buildah]] -- Image builder for the Claude Code container image
- [[hermes-agent]] -- Alternative agent platform that could use this plugin pattern
