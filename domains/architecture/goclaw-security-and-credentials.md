---
name: goclaw-security-and-credentials
description: "GoClaw security and credentials — input guard, SSRF protection, shell/exec controls, credential scrubbing, AES-256-GCM encryption, auth/RBAC, API keys, Secure CLI, remote workstations"
tags: [goclaw, security, credentials, rbac, encryption, architecture]
source: sources/goclaw/
verification_date: 2026-07-12
verified_by: codegraph-verify
---

# GoClaw Security & Credentials
**Source:** `sources/goclaw/`

GoClaw's security model is documented as five defense layers in `docs/09-security.md` (transport → input → tool → output → isolation). This page covers the concrete mechanisms behind those layers: prompt-injection guarding, SSRF protection, shell/exec controls, credential scrubbing, encryption-at-rest, authentication/RBAC, API keys, the credentialed CLI (Secure CLI) system, remote workstation exec, browser cookie sync, and MCP server token gating.

## 1. Input Guard — Prompt Injection Detection

`internal/agent/input_guard.go` ships an `InputGuard` that scans user messages against **6 built-in regex patterns** (`defaultGuardPatterns`, `internal/agent/input_guard.go:52-79`):

| Pattern | Detection Target | Regex (abridged) |
|---|---|---|
| `ignore_instructions` | "ignore all previous instructions" | `ignore\s+(all\s+)?(previous|prior|above|earlier|preceding)\s+(instructions?\|rules?...)\|` |
| `role_override` | "you are now", "pretend you are" | `(you are now\|from now on you are\|pretend you are\|act as if you are\|imagine you are)\s+` |
| `system_tags` | `<system>`, `[SYSTEM]`, `[INST]`, `<<SYS>>` | `</?system>\|\[SYSTEM\]\|\[INST\]\|<<SYS>>\|<\|im_start\|>system` |
| `instruction_injection` | "new instructions:", "override:", "system prompt:" | `(new instructions?:\|override:\|system prompt:\|<\|system\|>)` |
| `null_bytes` | NUL `\x00` obfuscation | raw `\x00` byte |
| `delimiter_escape` | "end of system", "begin user input", `</instructions>` | `(end of system\|begin user input\|</?(instructions?\|rules\|prompt\|context)>)` |

Action is configurable via `gateway.injection_action` (`internal/config/config_channels.go:435`, wired in `internal/config/config_system.go:50`): `"log"` (info log, continue), `"warn"` (warning log, continue — default), `"block"` (reject the message with an error), `"off"` (disable scanning). The guard is detection-oriented (`input_guard.go:8`); matched messages log `security.injection_detected` / `security.injection_blocked`. Messages over `max_message_chars` (default 32K) are truncated, not rejected, and the LLM is notified (`docs/09-security.md:52`).

## 2. SSRF Protection — 3-Layer Validation

`internal/security/ssrf.go` provides SSRF-safe HTTP utilities. **All production outbound webhook HTTP clients must use `NewSafeClient`** (`ssrf.go:1-2`) to prevent admin-configured hooks from probing internal infrastructure. The layered checks (`ssrf.go:162-215`):

1. **Scheme + host validation** — only `http`/`https` accepted; empty host rejected (`ssrf.go:171-180`).
2. **Literal-IP / DNS resolution + blocking** — literal IPs checked directly; hostnames resolved once and the **first resolved IP is pinned** (`ssrf.go:184-214`). Blocked CIDRs (`ssrf.go:42-73`): loopback (`127.0.0.0/8`, `::1/128`), link-local including cloud-metadata (`169.254.0.0/16`, `fe80::/10`), RFC 1918 private (`10/8`, `172.16/12`, `192.168/16`), ULA `fc00::/7`, benchmarking `198.18.0.0/15`, multicast, and unspecified ranges.
3. **Dial-time re-check + DNS-rebinding defense** — `NewSafeClient` (`ssrf.go:239-275`) requires a pinned IP in the request context (`WithPinnedIP`, `ssrf.go:218-220`), re-verifies the pinned IP against the block list at dial time, rewrites the dial address to the pinned IP, and **refuses to follow redirects** (`CheckRedirect` → `http.ErrUseLastResponse`).

**Operator MCP allowlist:** `ValidateAllowingHosts` (`ssrf.go:156-158`) exempts operator-trusted hostnames from the private/loopback block so self-hosted MCP servers on private networks can be registered — wired via `gateway.MCPAllowedHosts` (`cmd/gateway.go:655`). Cloud-metadata/link-local (`169.254.0.0/16`, `fe80::/10`), multicast, and unspecified ranges are **never** exemptable (`ssrf.go:75-104`). This path is intended **only** for owner/admin MCP server config validation, never for agent-influenced fetch paths. `IsBlocked(ip)` (`ssrf.go:122-124`) is the shared predicate for provider-URL validation. See also `docs/09-security.md:70-80` and the MCP stdio validation rules at `docs/09-security.md:80` (bare allowlisted runtime names only; path-bearing commands, shell metacharacters, and remote loader/package-exec modes rejected).

## 3. Shell & Exec Controls

### Shell deny groups
`tools.shellDenyGroups` (`internal/config/config_channels.go:458`) is a global map of deny-group name → denied, with per-agent overrides winning per key. Shell deny **patterns** cover 7 categories of blocked commands at execution time (`docs/09-security.md:56-68`): destructive file ops (`rm -rf`, `del /f`, `rmdir /s`), destructive disk ops (`mkfs`, `dd if=`, `> /dev/sd*`), system commands (`shutdown`, `reboot`, `poweroff`), fork bombs (`:(){ ... };:`), remote code execution (`curl | sh`, `wget -O - | sh`), reverse shells (`/dev/tcp/`, `nc -e`), and eval injection (`eval $()`, `base64 -d | sh`). Per-binary `exec_settings.deny_patterns` and a `deny_verbose` list (blocks verbose/debug output leakage) layer on top.

### Exec approval workflow
`tools.execApproval` (`internal/config/config_channels.go:523-530`, `internal/tools/exec_approval.go`) configures command execution approval:

| Field | Values |
|---|---|
| `security` | `"deny"` (no exec tool), `"allowlist"` (only allowlisted commands), `"full"` (default — all commands, ask mode still applies) |
| `ask` | `"off"` (default, auto-approve), `"on-miss"` (ask only when not allowlisted), `"always"` (ask for every command) |
| `allowlist` | glob patterns for allowed commands |

Approval requests flow through `ExecApprovalManager` (wired as `execApprovalMgr` in `cmd/gateway.go:541`); the approval surface is also exposed as an MCP tool (`internal/mcp/crud_exec_approval.go`) and as WS RPC (`internal/gateway/methods/exec_approval.go`). **Credentialed binaries auto-bypass approval** — an admin configuring credentials for a binary is implicit approval for that binary; the lookup happens before the approval check in `shell.go Execute()` (`docs/19-credentialed-exec.md:214-217`).

### Credentialed exec (Direct Exec Mode)
Four independent defense layers (`docs/09-security.md:94-123`): **no shell** (`exec.CommandContext(binary, args...)`, never `sh -c`), **path verify** (`exec.LookPath()` + config match against spoofed `./gh`), **deny patterns** (per-binary regex on args + verbose flags), and **output scrub** (registered credential values dynamically scrubbed). Agent-level grants are enforced **before any process spawn** via `SecureCLIStore.IsRegisteredBinary` — **fail-closed** on lookup error with a 2-second per-lookup timeout, env scrubbing on escape, wrapper unwrap up to 3 nesting levels (`docs/09-security.md:114-123`).

## 4. Output Security — Credential Scrubbing

`internal/tools/scrub.go` (inspired by zeroclaw's credential scrubbing) compiles **14 `MustCompile` patterns** (`scrub.go:12-38`) that replace secrets in tool output with `[REDACTED]`:

- OpenAI `sk-...`, Anthropic `sk-ant-...`
- GitHub PATs: `ghp_` / `gho_` / `ghu_` / `ghs_` / `ghr_` + 36 alnum
- AWS access keys: `AKIA[A-Z0-9]{16}`
- Generic `key=value`/`key:value` for api key/token/secret/password/bearer/authorization (8+ chars)
- Connection strings: postgres/postgresql/mysql/mongodb/redis/amqp URLs
- Env-var patterns: `*KEY|SECRET|CREDENTIAL|PRIVATE*=` (8+), `DSN|DATABASE_URL|REDIS_URL|MONGO_URI=` (8+), `VIRTUAL_*=` (4+)
- Long hex strings (64+ chars) — likely keys/hashes

Plus runtime-discovered values: `AddCredentialScrubValues` (min 6 chars, dedup, thread-safe) → `[REDACTED]`, and dynamic infra values (`AddDynamicScrubValues`, e.g. server IPs) → `[SERVER_IP]` (`scrub.go:43-114`). A **per-request scrub bag** (`WithScrubBag`/`ScrubCredentialsCtx`, `scrub.go:123-198`) keeps one tenant's credentials out of another tenant's output during concurrent credentialed-exec adapter runs. Web-fetched content is additionally wrapped in `<<<EXTERNAL_UNTRUSTED_CONTENT>>>` tags with a security warning (`docs/09-security.md:132`).

## 5. Encryption at Rest — AES-256-GCM

`internal/crypto/aes.go` implements AES-256-GCM via the standard library. Format: `"aes-gcm:" + base64(12-byte nonce + ciphertext + GCM tag)` (`aes.go:15-46`). `DeriveKey` (`aes.go:107-128`) accepts a 32-byte key as hex (64 chars), base64 (44 chars), or raw 32 bytes. Values without the `aes-gcm:` prefix are returned as-is for backward compatibility (legacy plaintext), logging `crypto.unencrypted_value_read` (`aes.go:58-63`).

**Key:** `GOCLAW_ENCRYPTION_KEY` env var. When missing, the CLI emits a hard warning — e.g. `cmd/bitrix_portal.go:94-96`: `WARNING: GOCLAW_ENCRYPTION_KEY is not set — credentials will be stored UNENCRYPTED`. Encrypted columns (`docs/09-security.md:231-242`):

| Table | Column |
|---|---|
| `llm_providers` | `api_key` |
| `mcp_servers` | `api_key` |
| `custom_tools` | `env` |
| `secure_cli_binaries`, `secure_cli_agent_grants`, `secure_cli_user_credentials`, `secure_cli_agent_credentials` | `encrypted_env` |

Credentialed CLI env entries support a `sensitive` visibility kind inside the encrypted JSON blob: masked in normal API/UI responses, revealed only through the explicit audited grant-reveal flow (`docs/09-security.md:242`).

## 6. Authentication & RBAC

### Gateway token
`GOCLAW_GATEWAY_TOKEN` (or `gateway.token` in config) must be set when the gateway binds a non-loopback address — otherwise startup **fails before the health endpoint reports ready**. `ValidateGatewayAuth` (`internal/config/config_load.go:34-38`) rejects the empty-token config unless `GatewayNoAuthFallbackAllowed` (`config_load.go:22-32`) passes, which is true only for loopback hosts or an explicit `GOCLAW_ALLOW_INSECURE_NO_AUTH=1` opt-in (`config_load.go:18-20`, `40-44`). Token comparison is constant-time (`crypto/subtle.ConstantTimeCompare`).

### Prioritized auth paths (HTTP + WS `connect`)
1. Gateway token (exact, constant-time) → `RoleAdmin`, or `RoleOwner` for configured owner IDs
2. API key (SHA-256 hash lookup) → role derived from scopes
3. Browser pairing (`X-GoClaw-Sender-Id`) → operator role from tenant membership
4. No auth configured + local/dev mode explicitly allowed → full-access dev mode
5. Otherwise → `401` (fail-closed; WS rejects unauthenticated connects, see `internal/gateway/router.go:330-345`)

### RBAC roles (`internal/gateway/router.go` connect handshake, `docs/09-security.md:276-303`)
Hierarchical: Viewer (level 1, read-only) → Operator (level 2, read+write) → Admin (level 3, full control). Owner is a superset of admin. Assignment during `handleConnect` (`router.go:126`): gateway token → `RoleAdmin` (`router.go:148`), owner IDs promoted to `RoleOwner` (`router.go:152-155`); no-token loopback/dev fallback → `RoleOperator` (`router.go:238`); browser pairing → role derived from `tenant_users.role` (`router.go:286-288`). API keys derive role from scopes via `RoleFromScopes` (`internal/permissions/policy.go:156-165`). Method access is gated by `PolicyEngine.CanAccess()` / `CanAccessWithScopes()` (`policy.go:107-153`).

### Tenant scope guards
Writes to **global** tables (no `tenant_id` column) must gate with `http.requireMasterScope` (`internal/http/tenant_auth_helpers.go:71`) wrapping `requireOwner(...)`; writes to **tenant-scoped** tables gate with `http.requireTenantAdmin` (`tenant_auth_helpers.go:22`) + `WHERE tenant_id = $N`. Shared predicate: `store.IsMasterScope(ctx)` (`internal/store/context.go:462`). `RoleAdmin` is **not** a tenant check.

## 7. API Keys (`docs/20-api-keys-auth.md`)

- **Format:** `goclaw_` + 32 hex chars (128-bit entropy); display prefix shows first 8 hex chars. Show-once: raw key returned only at creation (`docs/20-api-keys-auth.md:50-72`).
- **Storage:** SHA-256 hash in `api_keys.key_hash` (UNIQUE, partial index on non-revoked), never the raw key; constant-time comparison on auth (`docs/09-security.md:368-378`).
- **6 scopes** (`internal/permissions/policy.go:41-56`): `operator.admin` (full access, manages keys + SecureCLI), `operator.read`, `operator.write`, `operator.approvals` (exec approvals), `operator.pairing` (browser pairings), `operator.provision`. Highest scope derives the role; admin→RoleAdmin, write/approvals/pairing→RoleOperator, read-only→RoleViewer (`policy.go:156-165`).
- **Tenant binding:** tenant-bound keys (`tenant_id` set) always stay bound to their stored tenant — request headers cannot move them; system-level keys (`tenant_id = NULL`) keep their scope-derived role and may narrow via `X-GoClaw-Tenant-Id` without becoming owner (`docs/20-api-keys-auth.md:170-176`). User-bound keys force the stored `owner_id` and ignore spoofed user headers.
- **Caching:** in-memory 5-minute TTL, negative caching capped at 10,000 entries against token-spraying, pubsub invalidation on create/revoke/update; `last_used_at` updated async (`docs/20-api-keys-auth.md:144-154`).

## 8. Credentialed CLI / Secure CLI (`docs/19-credentialed-exec.md`)

Agents can use external CLIs (`gh`, `gcloud`, `aws`, `kubectl`, `terraform`, `psql`, GWS) with auto-injected, encrypted-at-rest credentials. **5 built-in presets** (`internal/tools/credential_presets.go`) auto-fill env vars, deny patterns, and timeouts — e.g. `gh` (`GH_TOKEN`, denies `auth\s+`, `ssh-key`, `repo\s+delete`, 30s), `gcloud` (`GOOGLE_APPLICATION_CREDENTIALS`, 120s), `aws`, `kubectl` (`KUBECONFIG`, 60s), `terraform` (300s). HTTP API at `/v1/cli-credentials` (+ `/{id}/test` dry-run against deny patterns); `encrypted_env` is never returned by GET handlers. 13 documented edge cases analyzed (`docs/19-credentialed-exec.md:70-86`); shell operators (`; | & < > \` \n \r $( ${`) are rejected outright in Direct Exec Mode.

Adapters (credential injection framework): user guide `docs/git-credential-adapter.md`, implementer guide `docs/credential-adapter-playbook.md`, GWS guide `docs/google-workspace-cli.md`. Every adapter injection emits exactly one `security.system_env_injection` slog line with a pinned field schema (adapter, binary, user_id, credential_source, env_keys names only, argv_prefix_len, host_scope_hash — plaintext hostname deliberately omitted) (`docs/09-security.md:550-578`). Known caveats: git adapter SSH uses `StrictHostKeyChecking=accept-new` (TOFU MITM window — pre-seed `~/.ssh/known_hosts`), and `SIGKILL` can leave 0600 tmpfile credentials (`goclaw-gitkey-*`, `goclaw-pgpass-*`) in `os.TempDir()` (`docs/09-security.md:580-613`).

## 9. Remote Workstations — Allowlisted Exec + Audit (Standard edition)

`internal/workstation/` implements remote exec over SSH backends (`internal/workstation/backends/ssh*.go`). Tools `workstation_exec` and `claude_remote` are registered **Standard edition only** (`cmd/gateway_tools_wiring.go:190-211`, `edition.Current().Name != "standard"` → skipped). Security model (`gateway_tools_wiring.go:196-204`):

- **argv-exec, no `sh -c`** — cmd is the binary name (argv[0]); shell injection impossible on the SSH backend.
- **NFKC normalization** applied to cmd and args before any check (collapses Unicode lookalikes).
- **Default-deny allowlist** — `AllowlistChecker` (`internal/workstation/security/allowlist.go`) rejects any command not matching the workstation's enabled binary patterns; 30s cache TTL with event-driven invalidation. Blocked env keys include `LD_PRELOAD`, `LD_LIBRARY_PATH`, `PATH`, `DYLD_INSERT_LIBRARIES` (checked after normalization).
- **Rate limits** — 30 exec/min per agent+workstation, 300/hr per workstation (`internal/workstation/security/rate_limiter.go`, wired in `gateway_tools_wiring.go:233-244`).
- **Audit** — `WireActivitySink` (`internal/workstation/activity_sink.go`) persists exec audit rows: secrets redacted from `cmd_preview` (sensitive-pattern regexes incl. JWT), raw command never persisted, 30-day retention.

A deny-all sentinel is the default `permCheck` until Phase-6 wiring replaces it (`internal/tools/workstation_exec.go:44-53`, `NewWorkstationExecTool`).

## 10. Browser Cookie Sync (`docs/browser-cookie-sync-threat-model.md`)

Selected cookie sync lets a user copy specific Chrome cookies into a server-side browser session for one agent. `POST /v1/browser/cookies/sync`, `GET /v1/browser/cookies`, `DELETE /v1/browser/cookies` require operator auth; user/tenant come from auth context, never the JSON body. Store key is `(tenant_id, user_id, agent_id, domain, path, name)`; cookie values are **encrypted at rest** and never returned by list responses (metadata only). The cookie store **fails closed when the encryption key is missing** — set `GOCLAW_ENCRYPTION_KEY` before enabling cookie sync. Browser runtime applies cookies only to matching domain/path within the same tenant/user/agent scope; API caps body size, cookie count, and per-cookie value size.

## 11. MCP Server Token Gating (`/api/mcp/`)

The CRUD MCP server (`internal/mcp/crud_server.go:107` `NewCRUDServer`) exposes agents, sessions, skills, cron, config, agent links, API keys, config permissions, Bitrix portals, run timelines, teams, channels, hooks, heartbeat, pairing, exec approval, usage, quota, chat, LLM completion, logs, send, and TTS voices as `goclaw_*` MCP tools backed by the real stores. It is gated by its **own bearer token** `gateway.mcp_server_token` (`internal/config/config_channels.go:429`, env-overridable via `config_secrets.go:181`), independent of the general gateway token so it can be rotated separately. Mounted at `/api/mcp/` behind `mcpServerTokenAuthMiddleware` (`internal/gateway/server.go:281-337`); when the token is unset the route is **not mounted at all** — the surface does not exist on the deployment. Callers may scope a request to a tenant via the `X-GoClaw-Tenant-Id` header (UUID or slug) with no membership check — the token is the full-trust boundary, defaulting to the master tenant (`crud_server.go` package comment).

## 12. Security Logging Convention

All security events use `slog.Warn` with a `security.*` prefix for consistent filtering and alerting (`docs/09-security.md:382-394`): `security.injection_detected`, `security.injection_blocked`, `security.rate_limited`, `security.cors_rejected`, `security.message_truncated`, plus SSRF blocks (`security.hook.ssrf_block`), pairing checks, `security.ws_connect_rejected`, `security.webhook.hmac_replay`, `security.system_env_injection`, and workstation/credentialed-binary events. Filter by grepping `security.` in logs.

## File Reference

| Concern | Path |
|---|---|
| Input guard (6 patterns) | `internal/agent/input_guard.go` |
| SSRF (3-layer) | `internal/security/ssrf.go`, `internal/security/ssrf_redirect.go` |
| Credential scrubbing (14 regexes) | `internal/tools/scrub.go` |
| Shell deny + exec approval | `internal/tools/shell.go`, `internal/tools/exec_approval.go` |
| AES-256-GCM | `internal/crypto/aes.go` |
| Auth/RBAC | `internal/config/config_load.go`, `internal/gateway/router.go`, `internal/permissions/policy.go`, `internal/http/tenant_auth_helpers.go` |
| API keys | `internal/crypto/apikey.go`, `internal/permissions/policy.go`, `docs/20-api-keys-auth.md` |
| Credentialed CLI | `internal/tools/credentialed_exec.go`, `internal/tools/credential_presets.go`, `internal/http/secure_cli.go` |
| Remote workstations | `internal/workstation/`, `cmd/gateway_tools_wiring.go` |
| CRUD MCP token gate | `internal/mcp/crud_server.go`, `internal/gateway/server.go` |
| Security overview | `docs/09-security.md` |

## Cross-References

- [[goclaw-architecture]] — overall GoClaw architecture
- [[goclaw-agents-deep-dive]] — agent loop and pipeline internals
- [[goclaw-n8n-mcp-bridge]] — MCP client/bridge/CRUD surfaces and n8n integration
- [[goclaw]] — GoClaw platform wiki
