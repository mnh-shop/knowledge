---
name: openclaw-security
tags: [acp, agent-gateway, audit, cli, docker, mcp, openclaw, personal-assistant, plugin-sdk, sandbox, security, sqlite, systemd, typescript]
description: OpenClaw Security Model
source: sources/openclaw/
---

# OpenClaw Security Model
**Source:** `sources/openclaw/`

OpenClaw's security model has five pillars: a **security audit subsystem** (`src/security/`), **DM pairing and trust modeling** (`dmPolicy`, allowlists, thread-bindings, dm-access), **sandboxed exec modes** (Docker / SSH / OpenShell), **Gateway authentication and approval management** (`src/gateway/`), and a **secrets-at-rest doctrine** (SQLite only; `~/.openclaw/credentials/` and per-agent `auth-profiles.json`). This document details the implementation, config surface, and operational runbooks.

## Table of Contents

- [Audit Subsystem](#audit-subsystem)
- [DM Pairing and Trust Model](#dm-pairing-and-trust-model)
- [Sandbox Modes](#sandbox-modes)
- [Gateway Auth and Approvals](#gateway-auth-and-approvals)
- [Secrets at Rest](#secrets-at-rest)
- [External Content Sanitization](#external-content-sanitization)
- [Exposure Runbook and Operations](#exposure-runbook-and-operations)
- [Key Source Files](#key-source-files)

---

## Audit Subsystem

The audit subsystem lives in `src/security/` and powers both `openclaw security audit` and the internal Gateway HTTP hardening checks. It is split into **cold** (config/filesystem, no runtime loading) and **deep** (live Gateway probes + plugin-owned collectors) paths.

### Audit Entry Points

- **`src/security/audit.ts`** -- Orchestrates security audit collection and report formatting. Reads `openclaw.json` config snapshot, state dir, Gateway auth config, sandbox config, and agent entries; resolves Gateway auth SecretRefs (without exec when possible).
- **`audit.runtime.ts`** -- Runtime wiring.
- **`audit.nondeep.runtime.ts`** -- Non-deep facade: cheap summary/config findings (`collectAttackSurfaceSummaryFindings`, `collectSmallModelRiskFindings`, `collectExposureMatrixFindings`, `collectGatewayHttpNoAuthFindings`, `collectHooksHardeningFindings`, `collectLikelyMultiUserSetupFindings`, `collectMinimalProfileOverrideFindings`, `collectModelHygieneFindings`, `collectNodeDangerousAllowCommandFindings`, `collectSandboxDangerousConfigFindings`, `collectSandboxDockerNoopFindings`, `collectSecretsInConfigFindings`, `collectSyncedFolderFindings`, ...).
- **`audit.deep.runtime.ts`** -- Deep audit facade for code-safety scans loaded only when requested (`collectInstalledSkillsCodeSafetyFindings`, `collectPluginsCodeSafetyFindings` from `audit-extra.async.js`).
- **`audit-deep-code-safety.ts` / `audit-deep-probe-findings.ts`** -- Deep code-safety and live-probe finding types.

### Audit Modes (CLI)

```bash
openclaw security audit              # cold config/filesystem/read-only path
openclaw security audit --deep       # + best-effort live Gateway probes and plugin collectors
openclaw security audit --deep --fix # apply safe fixes (permissions, tighten defaults)
openclaw security audit --json
openclaw security audit --auth password --password <pw>   # check hooks.token reuse
```

Plain `security audit` stays on the cold path and does not load every installed plugin runtime. `--deep` adds live Gateway probes and plugin-owned security audit collectors. If Gateway password auth is supplied only at startup, pass `--auth password --password <pw>` so the audit can check it against `hooks.token` (`docs/cli/security.md`).

### What the Audit Checks

- **DM/trust model** -- Warns when multiple DM senders share the main session (recommends `session.dmScope="per-channel-peer"` or `per-account-channel-peer`); emits `security.trust_model.multi_user_heuristic` for likely shared-user ingress; warns when small models (<=300B params) run without sandboxing and with web/browser tools enabled.
- **Webhook/hooks** -- Flags `hooks.token` reuse of active Gateway shared-secret auth values, short `hooks.token`, `hooks.path="/"`, unset `hooks.defaultSessionKey`, unrestricted `hooks.allowedAgentIds`, and sessionKey overrides without `hooks.allowedSessionKeyPrefixes`. `openclaw doctor --fix` rotates a persisted reused `hooks.token`.
- **Sandbox/tools** -- Warns when sandbox Docker settings are configured while sandbox mode is off; ineffective/unknown `gateway.nodes.commands.deny` entries; `allow` enabling dangerous node commands; global `tools.profile="minimal"` overridden by agent profiles; write/edit tools disabled while `exec` remains without a constraining sandbox filesystem boundary; open DMs/groups exposing runtime/filesystem tools without sandbox/workspace guards; permissive plugin tool policy.

### Dangerous Config Flags and Tools

- **`dangerous-tools.ts`** -- Centralizes tool-risk constants so Gateway HTTP restrictions and security audits don't drift. `DEFAULT_GATEWAY_HTTP_TOOL_DENY` denies high-risk tools over Gateway HTTP `POST /tools/invoke` by default: `exec`, `spawn`, `shell`, `fs_write`, `fs_delete`, `fs_move`, `apply_patch`, `terminal`, `sessions_spawn`, `sessions_send` (session orchestration/control-plane/interactive flows that don't make sense over a non-interactive HTTP surface).
- **`dangerous-config-flags.ts` / `dangerous-config-flags-core.ts` / `core-dangerous-config-flags.ts`** -- Core dangerous config flag metadata for audits (e.g. `DANGEROUS_SANDBOX_DOCKER_BOOLEAN_KEYS`), plus plugin config contract metadata for detecting insecure flag values.
- **`audit-gateway-tools-http.ts` / `audit-gateway-http-auth.ts`** -- HTTP tool surface and auth-selection checks.

### Filesystem Policy

- **`exec-filesystem-policy.ts`** -- Resolves filesystem policy for exec and sandbox tool use: lists agent entries, resolves configured tool policies and sandbox config, and applies allow/deny policy matching. `MUTATING_FS_TOOLS = ["write", "edit", "apply_patch"]`; `RUNTIME_TOOLS = ["exec", "process"]`. Defines the scope where exec-like tools remain available while mutating filesystem tools are disabled.
- **`audit-fs.ts`, `scan-paths.ts`, `safe-regex.ts`, `config-regex.ts`, `context-visibility.ts`, `windows-acl.ts`** -- Filesystem/scanning/path, regex-safety, context-visibility, and Windows ACL audit helpers.
- **`install-policy.ts` / `installed-plugin-dirs.ts`** -- Plugin install policy and installed plugin directory resolution.
- **`secret-mask.ts` / `secret-equal.ts`** -- Redaction and safe comparison of secrets in output.
- **`fix.ts`** -- Safe "fix" application for audit findings (permissions, tightened defaults).

---

## DM Pairing and Trust Model

OpenClaw's default trust model is **personal-assistant** (one operator), not hostile multi-tenant isolation. DM ingress is controlled by a per-channel `dmPolicy` and `allowFrom` allowlists.

### dmPolicy

Every chat channel defines `dmPolicy` with enum `["pairing", "allowlist", "open", "disabled"]` (default `"pairing"`; `channels.discord.dmPolicy`, etc. in `src/config/bundled-channel-config-metadata.generated.ts`):

| Policy | Meaning |
|--------|---------|
| `pairing` | Inbound DMs require a secure pairing handshake (approve inbound requests via `openclaw pairing`) |
| `allowlist` | Only senders in `allowFrom` (or the channel's `allowFrom` list) can DM |
| `open` | Any sender can DM (requires `channels.<id>.allowFrom=["*"]`; flagged by the audit's multi-user heuristics) |
| `disabled` | DMs disabled |

- **`src/security/dm-policy-shared.ts`** -- Shares DM-policy normalization for channel audits; derives a stable main-DM owner from a single-entry allowlist (wildcards/multi-owner lists stay unpinned so callers keep route-specific sessions); resolves effective allow-from lists via `src/channels/message-access/effective-allow-from.js` and `store-allow-from.js`; evaluates group access.
- **`src/channels/allowlists/resolve-utils.ts`** -- Channel allowlist resolution helpers: dedupes `allowFrom` entries and canonicalizes user lookups into stable id additions.
- **`src/channels/plugins/dm-access.ts`, `src/channels/direct-dm-access.ts`, `src/channels/direct-dm-guard-policy.ts`** -- DM access plumbing and guard policy.
- **Thread bindings** -- `src/channels/thread-bindings-policy.ts`, `src/channels/thread-binding-id.ts`, `src/channels/plugins/thread-binding-api.ts` plus `src/shared/thread-binding-lifecycle.ts` and `src/plugin-sdk/thread-bindings-*.ts` scope sessions to threads and enforce idle/max-age caps.
- **`src/security/audit-channel-dm-policy.test.ts`, `audit-channel-readonly-*.test.ts`** -- Audit coverage for DM policy and channel read-only resolution.

The audit's `security.trust_model.multi_user_heuristic` fires when config suggests likely shared-user ingress (open DM/group policy, configured group targets, wildcard sender rules). For intentional shared-user setups the runbook says: sandbox all sessions, keep filesystem access workspace-scoped, and keep personal/private identities or credentials off that runtime.

---

## Sandbox Modes

Exec sandboxing is off by default; when enabled, the default backend is Docker. Three backends exist:

| Backend | Source | Notes |
|---------|--------|-------|
| **Docker** | `src/agents/sandbox/docker-backend.ts` (`id: "docker"`) | Default when `agents.defaults.sandbox` is enabled. Container isolation; does not require the Gateway itself to run in Docker (`docs/install/docker.md:11`). |
| **SSH** | `src/agents/sandbox/ssh-backend.ts` (`id: "ssh"`) | Remote shell execution over SSH with `SandboxSshConfig`/`SshSandboxSession` |
| **OpenShell** | `@openclaw/openshell-sandbox` plugin | Sandbox backend for the NVIDIA OpenShell CLI with mirrored local workspaces and SSH command execution (`docs/plugins/reference/openshell.md`); manage via `openclaw sandbox` |

- **`src/plugin-sdk/sandbox.ts`** -- Public SDK subpath exporting sandbox backend types, SSH execution, and temp workspace helpers (`CreateSandboxBackendParams`, `RemoteShellSandboxHandle`, `RunSshSandboxCommandParams`, `SandboxBackendManager`, `SandboxSshConfig`, ...).
- **`src/agents/sandbox/`** -- Backend implementation directory: `backend.ts`, `docker-backend.ts`, `ssh-backend.ts`, `registry.ts`, `config.ts`, `manage.ts`, `prune.ts`, `fs-bridge*.ts`, `workspace*.ts`, `sanitize-env-vars.ts`, `tool-policy.ts`, `validate-sandbox-security.ts`, and browser/novnc bridges.
- **`src/plugin-sdk/agent-harness.ts`** -- Agent harness runtime that consumes the sandbox backends for tool execution.
- **`src/commands/sandbox.ts`** -- `openclaw sandbox` sub-CLI ("Manage sandbox containers (Docker-based agent isolation)").

The audit flags sandbox misconfigurations: Docker settings configured while sandbox mode is off (`collectSandboxDockerNoopFindings`), dangerous Docker config keys (`DANGEROUS_SANDBOX_DOCKER_BOOLEAN_KEYS`), and exec-without-sandbox-filesystem-boundary exposure.

---

## Gateway Auth and Approvals

Gateway ingress auth and exec approval management live in `src/gateway/`:

- **`src/gateway/auth.ts`** -- Gateway authentication surface (bearer token / password / auth-mode policy). See `auth-mode-policy.ts`, `auth-resolve.ts`, `auth-token-resolution.ts`, `auth-rate-limit.ts`, `auth-surface-resolution.ts`, `auth-config-utils.ts`, `auth-install-policy.ts`.
- **`src/gateway/device-auth.ts`** -- Device pairing/auth tokens for CLI/UI access (backed by `src/infra/device-auth-store.ts`; shared helpers in `src/shared/device-auth.ts`). Exposed via `openclaw devices`.
- **`src/gateway/exec-approval-manager.ts`** -- Manages exec approval requests (the `exec.approval.requested`/`exec.approval.resolved` event flow consumed by the MCP channel bridge and ACP `permission-relay.ts`). Config surface: `execApprovals` (enabled, approvers, agentFilter, sessionFilter, target `dm|channel|both`, cleanupAfterResolve).
- **`src/gateway/credentials.ts` / `credentials-secret-inputs.ts`** -- Gateway credential resolution from secrets.
- **`src/security/audit-gateway-*.ts`** -- Audit checks for gateway auth selection, HTTP auth, exposure, tools, and config.

Approval policy is also surfaced on the CLI: `openclaw approvals` (manage approval policy and pending requests), `openclaw exec-approvals` (alias), and `openclaw exec-policy` (show/synchronize requested exec policy with host approvals).

---

## Secrets at Rest

OpenClaw's storage doctrine is **SQLite only** for runtime state ("Storage default: SQLite only. Do not add JSON/JSONL/TXT/sidecar files for OpenClaw-owned runtime state" — `AGENTS.md`). Secrets specifically live in two locations:

| Secret Store | Path | Contents |
|--------------|------|----------|
| Legacy channel/provider credentials | `~/.openclaw/credentials/` | Channel/provider creds (API keys, bot tokens); auto-resolved by Gateway URL/auth when not explicitly provided; legacy — SecretRef-managed values preferred |
| Model auth profiles | `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` | Per-agent model provider auth profiles (api_key and static token profiles are portable and copied on `agents add`; OAuth refresh-token profiles are not copied unless a provider opts in with `copyToAgents: true`) |

- Container deployments mount the auth-profile secrets dir into the container: `docker-compose.yml` maps `${OPENCLAW_AUTH_PROFILE_SECRET_DIR:-${HOME}/.openclaw-auth-profile-secrets}` to `/home/node/.config/openclaw` (lines 44, 123).
- The audit checks for secrets in config (`collectSecretsInConfigFindings`) and flags literal sensitive header/env values in saved MCP definitions (`openclaw mcp doctor`).
- `openclaw secrets` provides secrets runtime controls; `openclaw security audit` and `openclaw doctor` verify secret handling and rotate reused secrets (e.g. `hooks.token` duplicating `gateway.auth.token`).
- `src/security/secret-mask.ts` and `secret-equal.ts` keep secrets out of logs and provide safe comparison; `audit-config-basics.test.ts` covers config hygiene.

### SecretRef Doctrine

Gateway auth secrets are managed as SecretRefs: `gateway.auth.token` can reference env/file/exec sources, and `openclaw onboard --install-daemon` validates but does **not** persist a resolved plaintext token in supervisor service environment metadata (install fails closed if the ref is unresolved — `docs/cli/onboard.md:272`). On SecretRef failure, Gateway startup marks the exact owning capability/account/route as configured-unavailable and emits a typed redacted diagnostic; doctor/status list every degraded owner.

---

## External Content Sanitization

Untrusted external content (emails, webhooks, web tools) is wrapped with source tags and random boundary tokens before reaching the LLM:

- **`src/security/external-content.ts`** -- "Wraps external content with source tags and random boundary tokens" (`randomBytes`); safety utilities for handling untrusted external content from emails, webhooks, and web tools before passing to LLM agents.
- **`src/security/external-content-source.ts`** -- Normalizes source identifiers: `HookExternalContentSource = "gmail" | "webhook"`; resolves a hook session key into its external content source (unknown `hook:*` sessions are treated as webhooks so legacy/custom hooks stay wrapped).
- **`src/security/context-visibility.ts`** -- Context visibility controls for shared-user/group setups.

---

## Exposure Runbook and Operations

- **Security docs:** `docs/security/` — `CONTRIBUTING-THREAT-MODEL.md`, `THREAT-MODEL-ATLAS.md`, `formal-verification.md`, `incident-response.md`, `network-proxy.md`. The incident-response runbook classifies severity (Critical = package/repo compromise or unauthenticated trust-boundary bypass; High = verified trust-boundary bypass or exposure of OpenClaw-owned sensitive credentials) and coordinates disclosure with CVE issuance when appropriate.
- **Gateway security docs:** `docs/gateway/authentication.md`, `docs/gateway/trusted-proxy-auth.md`, and a `docs/gateway/security` section.
- **Operational commands:**
  - `openclaw security audit` / `--deep` / `--fix` / `--json` — audit + safe fixes
  - `openclaw doctor` / `openclaw doctor --fix` — health checks, config migration, secret rotation
  - `openclaw approvals` / `exec-approvals` / `exec-policy` — approval policy management
  - `openclaw pairing` — secure DM pairing (approve inbound requests)
  - `openclaw devices` — device pairing and auth tokens
  - `openclaw secrets` — secrets runtime controls
  - `openclaw sandbox` — sandbox container management

---

## Key Source Files

| File | Purpose |
|------|---------|
| `src/security/audit.ts` | Security audit orchestration and report formatting |
| `src/security/audit.nondeep.runtime.ts` | Cold-path summary/config findings facade |
| `src/security/audit.deep.runtime.ts` | Deep code-safety findings facade (lazy-loaded) |
| `src/security/dangerous-tools.ts` | `DEFAULT_GATEWAY_HTTP_TOOL_DENY` — shared tool-risk constants |
| `src/security/dangerous-config-flags*.ts` | Dangerous config flag metadata (core + plugin contracts) |
| `src/security/exec-filesystem-policy.ts` | Exec/sandbox filesystem policy resolution |
| `src/security/dm-policy-shared.ts` | Shared DM policy normalization for audits |
| `src/security/external-content.ts` / `external-content-source.ts` | External content wrapping + source resolution |
| `src/security/secret-mask.ts` / `secret-equal.ts` | Secret redaction and safe comparison |
| `src/channels/allowlists/resolve-utils.ts` | Channel allowlist resolution helpers |
| `src/agents/sandbox/` | Docker/SSH/OpenShell sandbox backends |
| `src/plugin-sdk/sandbox.ts` | Public sandbox backend SDK subpath |
| `src/gateway/auth.ts`, `device-auth.ts` | Gateway auth + device pairing |
| `src/gateway/exec-approval-manager.ts` | Exec approval flow management |
| `src/gateway/credentials.ts` | Gateway credential resolution |
| `src/cli/security-cli.ts` (registered via `src/cli/program/subcli-descriptors.ts`) | `openclaw security` sub-CLI |

## Related

- [[domains/architecture/openclaw-architecture.md]] -- Gateway architecture and agent system
- [[domains/cli/openclaw-cli.md]] -- CLI surface (`openclaw security`, `doctor`, `approvals`, `sandbox`)
- [[domains/mcp/openclaw-mcp-implementation.md]] -- MCP surfaces (HTTP tool deny policy)
- [[domains/acp/openclaw-acp-implementation.md]] -- ACP approval classifier and environment sanitization
- [[domains/api/openclaw-api.md]] -- Gateway API reference (auth)
- [[assets/deployment/openclaw-quadlet.md]] -- Quadlet deployment patterns
